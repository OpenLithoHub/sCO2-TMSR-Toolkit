"""sCO2 mixture failure-envelope sweep — Data Black Hole 3 deliverable.

Reference: docs/00_strategy.md § Data Black Holes — Survival Strategy
           docs/known_gaps.md#mixture-eos
           docs/01_phase1_properties.md § 1.3

Sweep T-P space for a CO2 + impurity mixture and record where the open
property stack succeeds vs. fails. The output contour map is itself the
deliverable: it tells experimental thermodynamics groups *where the open
ecosystem is unusable*. Mapping the boundary of human knowledge is the
contribution — not pretending we have the data behind it.

Status codes (encoded as integers in the output grid so contour plots work):
    0 = OK              — solver converged in a well-defined single phase
    1 = TWO_PHASE       — operating point inside the phase envelope (avoid)
    2 = NEAR_CRITICAL   — within ±2 K / ±0.2 MPa of the mixture critical point
    3 = SOLVER_FAILED   — CoolProp raised; data gap / unsupported region

Run:
    python -m src.sco2_failure_envelope --x-he 0.03 --grid 60 \
        --out validation/failure_envelopes/co2_he_3pct.png
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import CoolProp.CoolProp as CP
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OK = 0
TWO_PHASE = 1
NEAR_CRITICAL = 2
SOLVER_FAILED = 3

STATUS_LABELS = {
    OK: "OK",
    TWO_PHASE: "two-phase",
    NEAR_CRITICAL: "near-critical",
    SOLVER_FAILED: "solver failed",
}


def _mixture_string(impurity: str, x_imp: float) -> str:
    return f"HEOS::CO2[{1 - x_imp:.4f}]&{impurity}[{x_imp:.4f}]"


def _on_or_near_saturation(T: float, P: float, dP_band: float = 0.05e6) -> bool:
    """Return True if (T, P) is within ``dP_band`` of pure CO2 saturation.

    PhaseSI('T', T, 'P', P) on a subcritical (T, P) always returns a single
    phase (gas or liquid). Genuine two-phase coexistence only resolves when
    pressure is queried with quality Q. So we instead bracket: T must be
    subcritical, P must be within ``dP_band`` of the saturation pressure
    P_sat(T). Anything inside that band is operationally inside the
    two-phase region for an engineering controller dealing with measurement
    uncertainty.
    """
    Tc = CP.PropsSI("Tcrit", "CO2")
    if T >= Tc:
        return False
    try:
        P_sat = CP.PropsSI("P", "T", T, "Q", 0.5, "CO2")
    except Exception:
        return False
    return abs(P - P_sat) < dP_band


def classify_point(
    T: float,
    P: float,
    impurity: str,
    x_imp: float,
    near_crit_dT: float = 2.0,
    near_crit_dP: float = 0.2e6,
    sat_band_Pa: float = 0.05e6,
) -> int:
    """Probe a single (T, P) and return its status code.

    Order of checks matters: we look for the *most actionable* failure mode
    first so the colour map highlights the worst issue when several apply.
        SOLVER_FAILED > TWO_PHASE > NEAR_CRITICAL > OK
    """
    Tc = CP.PropsSI("Tcrit", "CO2")
    Pc = CP.PropsSI("Pcrit", "CO2")
    near_crit = abs(T - Tc) < near_crit_dT and abs(P - Pc) < near_crit_dP

    # Saturation band — check before any property call so the contour map
    # always shows the two-phase strip even when the underlying call would
    # have succeeded with one of the two phases.
    if _on_or_near_saturation(T, P, sat_band_Pa):
        return TWO_PHASE

    if x_imp <= 0.0:
        try:
            CP.PropsSI("D", "T", T, "P", P, "CO2")
        except Exception:
            return SOLVER_FAILED
        return NEAR_CRITICAL if near_crit else OK

    mix = _mixture_string(impurity, x_imp)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            CP.PropsSI("D", "T", T, "P", P, mix)
    except Exception:
        return SOLVER_FAILED
    return NEAR_CRITICAL if near_crit else OK


def sweep(
    impurity: str = "Helium",
    x_imp: float = 0.03,
    T_range: tuple[float, float] = (290.0, 800.0),
    P_range: tuple[float, float] = (5e6, 25e6),
    n_T: int = 60,
    n_P: int = 60,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sweep T-P; return (T_axis, P_axis, status_grid).

    status_grid[i, j] gives the integer status at (T_axis[j], P_axis[i]) —
    matching the convention used by matplotlib's contourf with X=T, Y=P.
    """
    T_axis = np.linspace(*T_range, n_T)
    P_axis = np.linspace(*P_range, n_P)
    grid = np.zeros((n_P, n_T), dtype=int)
    for i, P in enumerate(P_axis):
        for j, T in enumerate(T_axis):
            grid[i, j] = classify_point(T, P, impurity, x_imp)
    return T_axis, P_axis, grid


def plot_envelope(
    T_axis: np.ndarray,
    P_axis: np.ndarray,
    grid: np.ndarray,
    impurity: str,
    x_imp: float,
    out_path: Path,
) -> None:
    """Render the failure envelope as a discrete contour plot."""
    fig, ax = plt.subplots(figsize=(10, 6.5))
    cmap = matplotlib.colors.ListedColormap(
        ["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]
    )
    boundaries = [-0.5, 0.5, 1.5, 2.5, 3.5]
    norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N)
    im = ax.pcolormesh(
        T_axis - 273.15,
        P_axis / 1e6,
        grid,
        cmap=cmap,
        norm=norm,
        shading="auto",
    )
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    cbar.ax.set_yticklabels([STATUS_LABELS[i] for i in (0, 1, 2, 3)])
    cbar.set_label("Solver status")

    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (MPa)")
    ax.set_title(
        f"sCO2 + {impurity} ({x_imp * 100:.1f} mol%) failure envelope\n"
        "Red regions = open EOS unusable. See docs/known_gaps.md#mixture-eos"
    )
    ax.grid(alpha=0.2, color="white", linewidth=0.5)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    print(f"Wrote {out_path}")


def write_grid_csv(
    T_axis: np.ndarray,
    P_axis: np.ndarray,
    grid: np.ndarray,
    out_path: Path,
) -> None:
    rows: list[dict[str, float | int | str]] = []
    for i, P in enumerate(P_axis):
        for j, T in enumerate(T_axis):
            rows.append(
                {
                    "T_K": float(T),
                    "P_Pa": float(P),
                    "status_code": int(grid[i, j]),
                    "status_label": STATUS_LABELS[int(grid[i, j])],
                }
            )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", maxsplit=1)[0])
    ap.add_argument("--impurity", default="Helium", choices=["Helium", "Water"])
    ap.add_argument("--x-imp", type=float, default=0.03,
                    help="Impurity mole fraction (0-0.1 typical)")
    ap.add_argument("--T-min", type=float, default=290.0)
    ap.add_argument("--T-max", type=float, default=800.0)
    ap.add_argument("--P-min", type=float, default=5e6)
    ap.add_argument("--P-max", type=float, default=25e6)
    ap.add_argument("--grid", type=int, default=60)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("validation/failure_envelopes/co2_he_envelope.png"),
    )
    ap.add_argument("--csv", type=Path, default=None)
    args = ap.parse_args()

    T_axis, P_axis, grid = sweep(
        impurity=args.impurity,
        x_imp=args.x_imp,
        T_range=(args.T_min, args.T_max),
        P_range=(args.P_min, args.P_max),
        n_T=args.grid,
        n_P=args.grid,
    )
    plot_envelope(T_axis, P_axis, grid, args.impurity, args.x_imp, args.out)

    csv_path = args.csv or args.out.with_suffix(".csv")
    write_grid_csv(T_axis, P_axis, grid, csv_path)

    n_total = grid.size
    counts = {
        STATUS_LABELS[s]: int((grid == s).sum())
        for s in (OK, TWO_PHASE, NEAR_CRITICAL, SOLVER_FAILED)
    }
    print("\nSummary (cells):")
    for k, v in counts.items():
        print(f"  {k:>14s}: {v:5d} ({100 * v / n_total:5.1f}%)")


if __name__ == "__main__":
    main()
