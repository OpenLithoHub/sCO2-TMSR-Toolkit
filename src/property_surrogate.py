"""CoolProp neural surrogate for sCO2 thermophysical properties.

Provides a PyTorch-based surrogate model that replaces slow CoolProp PropsSI
calls with fast neural-network forward passes, achieving 100x+ speedup.

Architecture mirrors DiffCFD's SCO2Surrogate: 4 independent MLP networks,
one per property (density, viscosity, conductivity, specific heat). Each
network takes (T_normalized, P_normalized) as input and outputs the property
value. Physical constraints are enforced by architecture design:
  - Positive outputs via softplus for viscosity, conductivity, cp
  - Monotone density via positive-weight final layer

Training data is generated from CoolProp PropsSI calls over the
user-specified (T, P) operating range, then normalized internally.

Typical usage::

    >>> from property_surrogate import PropertySurrogate
    >>> surr = PropertySurrogate(hidden_dim=64)
    >>> data = surr.generate_coolprop_data(
    ...     T_range=(350.0, 900.0), P_range=(7.5e6, 30e6), n=200
    ... )
    >>> surr.train(data, epochs=200, lr=1e-3)
    >>> rho = surr.predict_density(500.0, 20e6)  # scalar or arrays

Reference: DiffCFD diffcfd/props/sco2.py — SCO2Surrogate class.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from torch import Tensor


__all__ = ["PropertySurrogate"]


# ---------------------------------------------------------------------------
# Constrained MLP building blocks (inlined from diff-surrogate)
# ---------------------------------------------------------------------------


class _MonotoneLinear(nn.Module):
    """Linear layer with non-negative weights via softplus parameterization."""

    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.raw_weight = nn.Parameter(torch.empty(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.register_parameter("bias", None)
        nn.init.kaiming_uniform_(self.raw_weight, nonlinearity="relu")
        self.raw_weight.data.abs_()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = torch.nn.functional.softplus(self.raw_weight)
        out = x @ w.T
        if self.bias is not None:
            out = out + self.bias
        return out


class _MonotoneMLP(nn.Module):
    """MLP with approximate monotonicity via positive-weight linear layers."""

    def __init__(self, in_features: int, hidden: int = 64, n_layers: int = 3):
        super().__init__()
        layers = [_MonotoneLinear(in_features, hidden), nn.ReLU()]
        for _ in range(n_layers - 2):
            layers.extend([_MonotoneLinear(hidden, hidden), nn.ReLU()])
        layers.append(_MonotoneLinear(hidden, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class _PositiveOutputMLP(nn.Module):
    """MLP that guarantees positive output via softplus activation."""

    def __init__(self, in_features: int, hidden: int = 64, n_layers: int = 3):
        super().__init__()
        layers = [nn.Linear(in_features, hidden), nn.ReLU()]
        for _ in range(n_layers - 2):
            layers.extend([nn.Linear(hidden, hidden), nn.ReLU()])
        layers.append(nn.Linear(hidden, 1))
        self.net = nn.Sequential(*layers)
        self.positive = nn.Softplus()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.positive(self.net(x))

# ---------------------------------------------------------------------------
# CO2 critical-point constants (for normalization reference)
# ---------------------------------------------------------------------------
TC = 304.13  # K
PC = 7.377e6  # Pa (7.377 MPa)


# ---------------------------------------------------------------------------
# PropertySurrogate — main class
# ---------------------------------------------------------------------------


class PropertySurrogate:
    """Neural surrogate for CO2 thermophysical properties from CoolProp data.

    Trains 4 independent MLPs (density, viscosity, conductivity, specific_heat)
    on CoolProp PropsSI data over a user-specified (T, P) operating range.
    Once trained, forward passes provide 100x+ speedup over CoolProp API calls.

    Parameters
    ----------
    hidden_dim : int
        Hidden layer width for each property MLP.
    device : str or torch.device
        Compute device for tensors and networks.
    """

    def __init__(self, hidden_dim: int = 64, device: str = "cpu") -> None:
        self._device = torch.device(device)
        self._hidden_dim = hidden_dim
        self._trained = False

        # Normalization statistics — populated during training data generation
        self._T_mean = TC
        self._T_std = 0.2 * TC
        self._P_mean = PC
        self._P_std = 0.5 * PC

        # Property output statistics for denormalization
        self._stats: dict[str, dict[str, float]] = {}

        in_dim = 2  # (T_normalized, P_normalized)

        # 4 independent MLPs, one per property (output dim is always 1)
        self._density_net = _MonotoneMLP(in_dim, hidden=hidden_dim).to(self._device)
        self._viscosity_net = _PositiveOutputMLP(in_dim, hidden=hidden_dim).to(
            self._device
        )
        self._conductivity_net = _PositiveOutputMLP(in_dim, hidden=hidden_dim).to(
            self._device
        )
        self._cp_net = _PositiveOutputMLP(in_dim, hidden=hidden_dim).to(self._device)

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize_input(self, T: Tensor, P: Tensor) -> Tensor:
        """Normalize (T, P) to zero-mean, unit-scale around operating range."""
        T_n = (T - self._T_mean) / self._T_std
        P_n = (P - self._P_mean) / self._P_std
        return torch.stack([T_n, P_n], dim=-1)

    def _set_stats(self, name: str, values: np.ndarray) -> None:
        """Store mean/std for denormalizing a property output."""
        self._stats[name] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)) + 1e-8,
        }

    def _denormalize_output(self, name: str, raw: Tensor) -> Tensor:
        """Convert normalized network output back to physical units."""
        s = self._stats[name]
        return raw * s["std"] + s["mean"]

    # ------------------------------------------------------------------
    # Forward methods (individual properties)
    # ------------------------------------------------------------------

    def forward_density(self, T: Tensor, P: Tensor) -> Tensor:
        """Predict density rho [kg/m^3]."""
        x = self._normalize_input(T, P)
        raw = self._density_net(x).squeeze(-1)
        return self._denormalize_output("density", raw)

    def forward_viscosity(self, T: Tensor, P: Tensor) -> Tensor:
        """Predict dynamic viscosity mu [Pa*s]."""
        x = self._normalize_input(T, P)
        raw = self._viscosity_net(x).squeeze(-1)
        return self._denormalize_output("viscosity", raw)

    def forward_conductivity(self, T: Tensor, P: Tensor) -> Tensor:
        """Predict thermal conductivity k [W/(m*K)]."""
        x = self._normalize_input(T, P)
        raw = self._conductivity_net(x).squeeze(-1)
        return self._denormalize_output("conductivity", raw)

    def forward_specific_heat(self, T: Tensor, P: Tensor) -> Tensor:
        """Predict isobaric specific heat cp [J/(kg*K)]."""
        x = self._normalize_input(T, P)
        raw = self._cp_net(x).squeeze(-1)
        return self._denormalize_output("specific_heat", raw)

    # ------------------------------------------------------------------
    # Convenience: predict all properties at once
    # ------------------------------------------------------------------

    def predict_all(
        self, T: float | np.ndarray, P: float | np.ndarray
    ) -> dict[str, np.ndarray]:
        """Predict all 4 properties at given (T, P) point(s).

        Parameters
        ----------
        T : float or ndarray
            Temperature in K.
        P : float or ndarray
            Pressure in Pa.

        Returns
        -------
        dict with keys 'density', 'viscosity', 'conductivity', 'specific_heat',
        each mapping to a numpy array.
        """
        if not self._trained:
            raise RuntimeError("Surrogate not trained yet. Call train() first.")

        T_t = torch.as_tensor(T, dtype=torch.float32, device=self._device)
        P_t = torch.as_tensor(P, dtype=torch.float32, device=self._device)

        with torch.no_grad():
            rho = self.forward_density(T_t, P_t)
            mu = self.forward_viscosity(T_t, P_t)
            k = self.forward_conductivity(T_t, P_t)
            cp = self.forward_specific_heat(T_t, P_t)

        return {
            "density": rho.cpu().numpy(),
            "viscosity": mu.cpu().numpy(),
            "conductivity": k.cpu().numpy(),
            "specific_heat": cp.cpu().numpy(),
        }

    def predict_density(self, T: float, P: float) -> float:
        """Quick scalar prediction for density [kg/m^3]."""
        return float(self.predict_all(T, P)["density"])

    def predict_viscosity(self, T: float, P: float) -> float:
        """Quick scalar prediction for viscosity [Pa*s]."""
        return float(self.predict_all(T, P)["viscosity"])

    def predict_conductivity(self, T: float, P: float) -> float:
        """Quick scalar prediction for conductivity [W/(m*K)]."""
        return float(self.predict_all(T, P)["conductivity"])

    def predict_specific_heat(self, T: float, P: float) -> float:
        """Quick scalar prediction for specific heat [J/(kg*K)]."""
        return float(self.predict_all(T, P)["specific_heat"])

    # ------------------------------------------------------------------
    # Data generation
    # ------------------------------------------------------------------

    @staticmethod
    def generate_coolprop_data(
        T_range: tuple[float, float] = (350.0, 900.0),
        P_range: tuple[float, float] = (7.5e6, 30e6),
        n: int = 200,
        fluid: str = "CO2",
    ) -> dict[str, np.ndarray]:
        """Generate training data using CoolProp PropsSI calls.

        Creates a Latin-hypercube-style grid over (T, P) and evaluates all 4
        properties. Points where CoolProp fails (e.g. two-phase region) are
        filtered out automatically.

        Parameters
        ----------
        T_range : (T_min, T_max) in Kelvin.
        P_range : (P_min, P_max) in Pa.
        n : int
            Grid resolution per dimension; total points = n*n (minus failures).
        fluid : str
            CoolProp fluid name.

        Returns
        -------
        dict with keys 'T', 'P', 'density', 'viscosity', 'conductivity',
        'specific_heat', each a 1-D numpy array of the same length.
        """
        import CoolProp.CoolProp as CP

        T_arr = np.linspace(T_range[0], T_range[1], n)
        P_arr = np.linspace(P_range[0], P_range[1], n)
        T_grid, P_grid = np.meshgrid(T_arr, P_arr)

        T_flat = T_grid.flatten()
        P_flat = P_grid.flatten()
        N = len(T_flat)

        rho = np.full(N, np.nan)
        mu = np.full(N, np.nan)
        k = np.full(N, np.nan)
        cp = np.full(N, np.nan)

        for i in range(N):
            try:
                rho[i] = CP.PropsSI("D", "T", T_flat[i], "P", P_flat[i], fluid)
                mu[i] = CP.PropsSI("V", "T", T_flat[i], "P", P_flat[i], fluid)
                k[i] = CP.PropsSI("L", "T", T_flat[i], "P", P_flat[i], fluid)
                cp[i] = CP.PropsSI("C", "T", T_flat[i], "P", P_flat[i], fluid)
            except Exception:
                pass  # skip two-phase or out-of-range points

        # Filter out any NaN entries (failed CoolProp evaluations)
        valid = ~(np.isnan(rho) | np.isnan(mu) | np.isnan(k) | np.isnan(cp))
        print(
            f"CoolProp data: {valid.sum()}/{N} points valid "
            f"({(~valid).sum()} failed, likely two-phase)"
        )

        return {
            "T": T_flat[valid],
            "P": P_flat[valid],
            "density": rho[valid],
            "viscosity": mu[valid],
            "conductivity": k[valid],
            "specific_heat": cp[valid],
        }

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(
        self,
        data: dict[str, np.ndarray],
        epochs: int = 200,
        lr: float = 1e-3,
        batch_size: int | None = None,
        loss_weights: dict[str, float] | None = None,
        verbose: bool = True,
    ) -> dict[str, list[float]]:
        """Train all 4 property networks on CoolProp data.

        Parameters
        ----------
        data : dict
            Output of ``generate_coolprop_data``. Must contain keys
            'T', 'P', 'density', 'viscosity', 'conductivity', 'specific_heat'.
        epochs : int
            Number of training epochs.
        lr : float
            Adam learning rate.
        batch_size : int or None
            Mini-batch size. Defaults to min(1024, n_samples).
        loss_weights : dict or None
            Per-property loss weights. Keys should be property names
            ('density', 'viscosity', 'conductivity', 'specific_heat').
            Defaults to equal weights if None.
        verbose : bool
            Print training progress every 50 epochs.

        Returns
        -------
        dict mapping property names to per-epoch loss lists.
        """
        # Convert to tensors
        T = torch.as_tensor(data["T"], dtype=torch.float32, device=self._device)
        P = torch.as_tensor(data["P"], dtype=torch.float32, device=self._device)

        # Set normalization statistics from data
        T_np = np.asarray(data["T"])
        P_np = np.asarray(data["P"])
        self._T_mean = float(T_np.mean())
        self._T_std = float(T_np.std()) + 1e-8
        self._P_mean = float(P_np.mean())
        self._P_std = float(P_np.std()) + 1e-8

        # Prepare normalized targets
        properties = {
            "density": data["density"],
            "viscosity": data["viscosity"],
            "conductivity": data["conductivity"],
            "specific_heat": data["specific_heat"],
        }

        targets = {}
        for name, raw_vals in properties.items():
            vals = np.asarray(raw_vals)
            self._set_stats(name, vals)
            normalized = (vals - self._stats[name]["mean"]) / self._stats[name]["std"]
            targets[name] = torch.as_tensor(
                normalized, dtype=torch.float32, device=self._device
            )

        n_samples = T.shape[0]
        if batch_size is None:
            batch_size = min(1024, n_samples)

        # Networks and optimizers
        networks = {
            "density": self._density_net,
            "viscosity": self._viscosity_net,
            "conductivity": self._conductivity_net,
            "specific_heat": self._cp_net,
        }

        all_params = []
        for net in networks.values():
            all_params.extend(net.parameters())
        optimizer = torch.optim.Adam(all_params, lr=lr)

        # Training loop
        loss_history: dict[str, list[float]] = {k: [] for k in networks}
        w = loss_weights or {}

        for epoch in range(epochs):
            perm = torch.randperm(n_samples, device=self._device)
            epoch_losses = {k: torch.zeros((), device=self._device) for k in networks}
            n_batches = 0

            for start in range(0, n_samples, batch_size):
                idx = perm[start : start + batch_size]
                T_batch = T[idx]
                P_batch = P[idx]
                x = self._normalize_input(T_batch, P_batch)

                batch_losses = {}
                for name, net in networks.items():
                    pred = net(x).squeeze(-1)
                    loss = nn.functional.mse_loss(pred, targets[name][idx])
                    batch_losses[name] = w.get(name, 1.0) * loss

                total_loss = sum(batch_losses.values())
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()

                for name in networks:
                    epoch_losses[name] = epoch_losses[name] + batch_losses[name].detach()
                n_batches += 1

            for name in networks:
                loss_history[name].append((epoch_losses[name] / max(1, n_batches)).item())

            if verbose and (epoch % 50 == 0 or epoch == epochs - 1):
                parts = "  ".join(
                    f"{name}={loss_history[name][-1]:.4e}" for name in networks
                )
                print(f"Epoch {epoch:4d}/{epochs}:  {parts}")

        self._trained = True
        return loss_history

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def state_dict(self) -> dict:
        """Return full model state for saving."""
        return {
            "density_net": self._density_net.state_dict(),
            "viscosity_net": self._viscosity_net.state_dict(),
            "conductivity_net": self._conductivity_net.state_dict(),
            "cp_net": self._cp_net.state_dict(),
            "stats": self._stats,
            "T_mean": self._T_mean,
            "T_std": self._T_std,
            "P_mean": self._P_mean,
            "P_std": self._P_std,
            "hidden_dim": self._hidden_dim,
            "trained": self._trained,
        }

    def load_state_dict(self, state: dict) -> None:
        """Restore model from saved state."""
        self._density_net.load_state_dict(state["density_net"])
        self._viscosity_net.load_state_dict(state["viscosity_net"])
        self._conductivity_net.load_state_dict(state["conductivity_net"])
        self._cp_net.load_state_dict(state["cp_net"])
        self._stats = state["stats"]
        self._T_mean = state["T_mean"]
        self._T_std = state["T_std"]
        self._P_mean = state["P_mean"]
        self._P_std = state["P_std"]
        self._trained = state["trained"]


# ---------------------------------------------------------------------------
# CLI: quick smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== CoolProp Neural Surrogate Smoke Test ===\n")

    surr = PropertySurrogate(hidden_dim=64)

    # Generate training data (small grid for quick test)
    print("Generating CoolProp training data (50x50 grid)...")
    data = surr.generate_coolprop_data(
        T_range=(350.0, 900.0),
        P_range=(7.5e6, 30e6),
        n=50,
    )
    print(f"  Data points: {len(data['T'])}")
    print(f"  T range: [{data['T'].min():.1f}, {data['T'].max():.1f}] K")
    print(
        f"  P range: [{data['P'].min() / 1e6:.2f}, {data['P'].max() / 1e6:.2f}] MPa\n"
    )

    # Train
    print("Training surrogate (200 epochs)...")
    losses = surr.train(data, epochs=200, lr=1e-3)

    # Evaluate at a few test points
    print("\n--- Predictions vs CoolProp ---")
    import CoolProp.CoolProp as CP

    test_points = [
        (500.0, 20e6),  # typical compressor outlet
        (700.0, 15e6),  # turbine inlet
        (350.0, 25e6),  # near pseudo-critical
    ]

    for T_test, P_test in test_points:
        pred = surr.predict_all(T_test, P_test)
        try:
            rho_cp = CP.PropsSI("D", "T", T_test, "P", P_test, "CO2")
            mu_cp = CP.PropsSI("V", "T", T_test, "P", P_test, "CO2")
            k_cp = CP.PropsSI("L", "T", T_test, "P", P_test, "CO2")
            cp_cp = CP.PropsSI("C", "T", T_test, "P", P_test, "CO2")

            def rel_err(a, b):
                return abs(a - b) / (abs(b) + 1e-10) * 100

            print(f"\nT={T_test:.0f} K, P={P_test / 1e6:.1f} MPa:")
            print(
                f"  density:     surrogate={pred['density']:.2f}  CoolProp={rho_cp:.2f}  "
                f"err={rel_err(pred['density'], rho_cp):.1f}%"
            )
            print(
                f"  viscosity:   surrogate={pred['viscosity']:.2e}  CoolProp={mu_cp:.2e}  "
                f"err={rel_err(pred['viscosity'], mu_cp):.1f}%"
            )
            print(
                f"  conductivity: surrogate={pred['conductivity']:.4f}  CoolProp={k_cp:.4f}  "
                f"err={rel_err(pred['conductivity'], k_cp):.1f}%"
            )
            print(
                f"  specific_heat: surrogate={pred['specific_heat']:.1f}  CoolProp={cp_cp:.1f}  "
                f"err={rel_err(pred['specific_heat'], cp_cp):.1f}%"
            )
        except Exception as e:
            print(
                f"\nT={T_test:.0f} K, P={P_test / 1e6:.1f} MPa: CoolProp failed ({e})"
            )
            print(
                f"  surrogate: rho={pred['density']:.2f}  mu={pred['viscosity']:.2e}  "
                f"k={pred['conductivity']:.4f}  cp={pred['specific_heat']:.1f}"
            )

    print("\nDone.")
