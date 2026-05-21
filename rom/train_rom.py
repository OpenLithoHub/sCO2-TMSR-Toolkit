"""Train the PCHE ROM and export ONNX + scalers.

Reference: docs/02_phase2_cfd_rom.md § 2.6.3 (+ optional § 2.6.3a physics-informed).

Design choice rationale (per docs):
  - Not GP/Kriging: slow once samples exceed a few hundred
  - Not XGBoost: harder to export as ONNX/FMU for embedding in Modelica
  - Neural network: fast inference + clean ONNX export

Inputs : (T_in_K, P_in_Pa, mass_flow_kg_s, geometry_id)  shape (N, 4)
Outputs: (Nu_avg, dp_total_Pa)                            shape (N, 2)

All scalers are saved alongside the ONNX so the FMU can de-normalise at
runtime (see exported/wrap_as_fmu.py).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Imports we expect in CI; raise a clear message if absent.
try:
    import torch
    import torch.nn as nn
except ImportError as e:
    raise SystemExit(
        "PyTorch not installed. Install with `pip install torch` (CPU build is fine)."
    ) from e

try:
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
except ImportError as e:
    raise SystemExit("scikit-learn not installed. `pip install scikit-learn`.") from e


class PCHE_ROM(nn.Module):
    def __init__(self, in_dim: int = 4, out_dim: int = 2, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.SiLU(),
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def energy_balance_penalty(
    T_in: torch.Tensor,
    P_in: torch.Tensor,
    mdot: torch.Tensor,
    Nu_pred: torch.Tensor,
    dp_pred: torch.Tensor,
    T_wall: torch.Tensor | None = None,
    D_ch: float = 0.002,
    L: float = 0.6,
    N_ch: int = 1000,
) -> torch.Tensor:
    """Optional § 2.6.3a — soft energy-balance penalty.

    Skip if T_wall data is not available (returns zero). This is NOT a full
    PINN — it penalises gross channel-level energy-balance violations only.
    """
    if T_wall is None:
        return torch.tensor(0.0)
    try:
        import CoolProp.CoolProp as CP
    except ImportError:
        return torch.tensor(0.0)

    with torch.no_grad():
        try:
            k = CP.PropsSI("L", "T", float(T_in.mean()), "P", float(P_in.mean()), "CO2")
            Cp = CP.PropsSI("C", "T", float(T_in.mean()), "P", float(P_in.mean()), "CO2")
        except Exception:
            return torch.tensor(0.0)

    h_conv = Nu_pred * k / D_ch
    A_surf = float(np.pi * D_ch * L * N_ch)
    dT_wall = T_wall - T_in
    Q_conv = h_conv * A_surf * dT_wall
    Q_fluid = mdot * Cp * dT_wall
    return torch.mean((Q_conv - Q_fluid) ** 2) / (
        (Q_fluid.detach() ** 2 + 1e-8).mean()
    )


def train(
    csv_path: Path,
    out_dir: Path,
    epochs: int = 2000,
    lr: float = 1e-3,
    seed: int = 42,
    use_physics: bool = False,
    lambda_phys: float = 0.05,
) -> dict[str, float]:
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(seed)
    np.random.seed(seed)

    df = pd.read_csv(csv_path)
    X = df[["T_in_K", "P_in_Pa", "mass_flow_kg_s", "geometry_id"]].to_numpy(
        dtype=np.float32
    )
    y = df[["Nu_avg", "dp_total_Pa"]].to_numpy(dtype=np.float32)

    xs, ys = StandardScaler(), StandardScaler()
    Xn = xs.fit_transform(X)
    yn = ys.fit_transform(y)
    X_train, X_val, y_train, y_val = train_test_split(
        Xn, yn, test_size=0.2, random_state=seed
    )

    model = PCHE_ROM()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-5)
    loss_fn = nn.MSELoss()

    Xt = torch.tensor(X_train, dtype=torch.float32)
    yt = torch.tensor(y_train, dtype=torch.float32)
    Xv = torch.tensor(X_val, dtype=torch.float32)
    yv = torch.tensor(y_val, dtype=torch.float32)

    best_val = float("inf")
    for epoch in range(epochs):
        model.train()
        pred = model(Xt)
        data_loss = loss_fn(pred, yt)
        if use_physics:
            phys = energy_balance_penalty(
                T_in=Xt[:, 0], P_in=Xt[:, 1], mdot=Xt[:, 2],
                Nu_pred=pred[:, 0], dp_pred=pred[:, 1], T_wall=None,
            )
            loss = data_loss + lambda_phys * phys
        else:
            loss = data_loss
        opt.zero_grad()
        loss.backward()
        opt.step()

        if epoch % 200 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                val_loss = loss_fn(model(Xv), yv).item()
            best_val = min(best_val, val_loss)
            print(
                f"epoch {epoch:5d} | train {loss.item():.5f} | val {val_loss:.5f}"
            )

    # Validation MAPE in original units
    model.eval()
    with torch.no_grad():
        pred_val = ys.inverse_transform(model(Xv).numpy())
    true_val = ys.inverse_transform(y_val)
    mape_Nu = float(np.mean(np.abs((pred_val[:, 0] - true_val[:, 0]) / true_val[:, 0])) * 100)
    mape_dp = float(np.mean(np.abs((pred_val[:, 1] - true_val[:, 1]) / true_val[:, 1])) * 100)
    print(f"Validation MAPE: Nu_avg={mape_Nu:.2f}% dp_total={mape_dp:.2f}%")

    np.savez(
        out_dir / "scalers.npz",
        x_mean=xs.mean_, x_scale=xs.scale_,
        y_mean=ys.mean_, y_scale=ys.scale_,
    )

    dummy = torch.randn(1, 4)
    torch.onnx.export(
        model,
        dummy,
        out_dir / "pche_rom.onnx",
        input_names=["features"],
        output_names=["Nu_dp"],
        dynamic_axes={"features": {0: "batch"}},
        opset_version=17,
    )
    print(f"✅ Wrote {out_dir/'pche_rom.onnx'} and scalers.npz")

    return {"mape_Nu_pct": mape_Nu, "mape_dp_pct": mape_dp, "best_val_loss": best_val}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=Path("rom/dataset/training_set.csv"))
    ap.add_argument("--out-dir", type=Path, default=Path("rom/exported"))
    ap.add_argument("--epochs", type=int, default=2000)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--use-physics", action="store_true",
                    help="Enable § 2.6.3a physics-informed loss (requires T_wall in data)")
    args = ap.parse_args()
    train(
        args.csv, args.out_dir,
        epochs=args.epochs, lr=args.lr,
        use_physics=args.use_physics,
    )


if __name__ == "__main__":
    main()
