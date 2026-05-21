"""
sCO2 property explorer — pseudo-critical line diagnostic visualization.

Reference: docs/01_phase1_properties.md § 1.2

The pseudo-critical line is the locus of (T, P) points where Cp peaks at fixed P
above the critical pressure (P > 7.38 MPa). Engineering sCO2 cycles operate at
15-25 MPa and must be designed around this line — not around the critical point itself.
"""

from __future__ import annotations

import numpy as np

import CoolProp.CoolProp as CP
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def find_pseudocritical_temp(
    P: float,
    fluid: str = "CO2",
    T_search_range: tuple[float, float] = (305.0, 800.0),
    n_search: int = 500,
) -> float:
    """Return the temperature (K) of the local Cp maximum at pressure P (Pa).

    Above the critical pressure, CO2 has no phase transition but Cp still peaks
    at a specific temperature. The locus of these peaks is the pseudo-critical line.
    """
    T_arr = np.linspace(*T_search_range, n_search)
    Cp_arr = np.full(n_search, np.nan)
    for i, T in enumerate(T_arr):
        try:
            Cp_arr[i] = CP.PropsSI("C", "T", T, "P", P, fluid)
        except Exception:
            pass
    if np.all(np.isnan(Cp_arr)):
        raise RuntimeError(f"All Cp evaluations failed at P={P:.3e} Pa for {fluid}")
    return float(T_arr[np.nanargmax(Cp_arr)])


def plot_cp_with_pseudocritical(
    fluid: str = "CO2",
    T_range: tuple[float, float] = (300.0, 400.0),
    P_range: tuple[float, float] = (7e6, 25e6),
    grid: int = 200,
    output_path: str | None = "sco2_cp_pseudocritical.png",
):
    """Plot a Cp contour map overlaid with the pseudo-critical line.

    T_range extends to ~127 °C because at high pressures (20+ MPa) the
    pseudo-critical temperature rises significantly above 31 °C.
    """
    T_arr = np.linspace(*T_range, grid)
    P_arr = np.linspace(*P_range, grid)
    T_grid, P_grid = np.meshgrid(T_arr, P_arr)

    Cp_grid = np.full_like(T_grid, np.nan)
    for i in range(grid):
        for j in range(grid):
            try:
                Cp_grid[i, j] = CP.PropsSI(
                    "C", "T", T_grid[i, j], "P", P_grid[i, j], fluid
                )
            except Exception:
                pass

    P_line = np.linspace(*P_range, 80)
    T_pc = [
        find_pseudocritical_temp(P, fluid, (T_range[0], T_range[1])) for P in P_line
    ]

    fig, ax = plt.subplots(figsize=(11, 7))
    c = ax.contourf(
        T_grid - 273.15, P_grid / 1e6, Cp_grid / 1000, levels=50, cmap="inferno"
    )
    plt.colorbar(c, ax=ax, label="Cp (kJ/kg·K)")
    ax.axvline(
        31.1,
        color="cyan",
        linestyle="--",
        alpha=0.5,
        label="Critical T 31.1 °C (only at 7.38 MPa)",
    )
    ax.axhline(
        7.38, color="lime", linestyle="--", alpha=0.5, label="Critical P 7.38 MPa"
    )
    ax.plot(
        np.array(T_pc) - 273.15,
        P_line / 1e6,
        color="white",
        linewidth=2.5,
        label="Pseudo-critical line (engineering design reference)",
    )

    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Pressure (MPa)")
    ax.set_title(
        f"{fluid} Specific Heat Cp + Pseudo-Critical Line\n"
        "Engineering cycles (15–25 MPa) track the white line, not the critical point"
    )
    ax.legend(loc="upper right", fontsize=9)
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150)
    return fig


if __name__ == "__main__":
    fig = plot_cp_with_pseudocritical()
    print("Saved: sco2_cp_pseudocritical.png")
