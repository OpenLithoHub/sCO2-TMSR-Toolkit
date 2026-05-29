"""sCO2 recompression cycle — T-s diagram and idealised state points.

Reference: docs/01_phase1_properties.md § 1.8 (Streamlit) +
           book/03_ts_diagram.md (Jupyter Book version).

This module gives the Streamlit app and the test suite a single source of
truth for the recompression cycle state points and saturation dome. It is
intentionally pedagogical — no solver, just CoolProp ``PropsSI`` calls at
user-specified (T, P).
"""

from __future__ import annotations

from dataclasses import dataclass

import CoolProp.CoolProp as CP
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


@dataclass(frozen=True)
class CycleState:
    label: str
    T_K: float
    P_Pa: float
    s_J_kgK: float


@dataclass(frozen=True)
class CycleParams:
    """User-tunable cycle conditions. All temperatures in K, pressures in Pa."""

    P_low_Pa: float = 8.0e6
    P_high_Pa: float = 25.0e6
    T_compressor_in_K: float = 308.15  # ~35 °C
    T_compressor_out_K: float = 343.15  # ~70 °C
    T_after_lowT_recup_K: float = 423.15  # ~150 °C
    T_turbine_in_K: float = 823.15  # ~550 °C
    T_turbine_out_K: float = 703.15  # ~430 °C
    T_after_highT_recup_K: float = 473.15  # ~200 °C


def build_states(params: CycleParams = CycleParams()) -> list[CycleState]:
    """Return the six idealised state points in cycle traversal order."""
    spec = [
        ("1", params.T_compressor_in_K, params.P_low_Pa),
        ("2", params.T_compressor_out_K, params.P_high_Pa),
        ("3", params.T_after_lowT_recup_K, params.P_high_Pa),
        ("4", params.T_turbine_in_K, params.P_high_Pa),
        ("5", params.T_turbine_out_K, params.P_low_Pa),
        ("6", params.T_after_highT_recup_K, params.P_low_Pa),
    ]
    states = []
    for label, T, P in spec:
        s = CP.PropsSI("S", "T", T, "P", P, "CO2")
        states.append(CycleState(label=label, T_K=T, P_Pa=P, s_J_kgK=s))
    return states


def saturation_dome(
    T_min_K: float = 220.0, T_max_K: float = None, n: int = 50
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (T, s_liquid, s_vapor) along the sub-critical saturation dome.

    The vapour branch ends at the critical temperature; we cap T_max one
    decimal below T_crit to dodge solver-edge instability.
    """
    if T_max_K is None:
        T_max_K = CP.PropsSI("Tcrit", "CO2") - 0.1
    T_arr = np.linspace(T_min_K, T_max_K, n)
    s_liq = np.array([CP.PropsSI("S", "T", t, "Q", 0, "CO2") for t in T_arr])
    s_vap = np.array([CP.PropsSI("S", "T", t, "Q", 1, "CO2") for t in T_arr])
    return T_arr, s_liq, s_vap


def plot_ts_diagram(
    states: list[CycleState] | None = None,
    params: CycleParams = CycleParams(),
    output_path: str | None = "sco2_recompression_ts.png",
):
    """Plot a T-s diagram showing the saturation dome and the cycle path."""
    if states is None:
        states = build_states(params)

    T_dome, s_liq, s_vap = saturation_dome()

    fig, ax = plt.subplots(figsize=(10, 6.5))
    s_dome = np.concatenate([s_liq, s_vap[::-1]])
    T_close = np.concatenate([T_dome, T_dome[::-1]])
    ax.plot(s_dome, T_close, color="lightgrey", lw=1.5, label="CO₂ saturation dome")

    s_arr = [s.s_J_kgK for s in states] + [states[0].s_J_kgK]
    T_arr = [s.T_K for s in states] + [states[0].T_K]
    ax.plot(
        s_arr,
        T_arr,
        "o-",
        color="navy",
        markersize=7,
        lw=2,
        label="Idealised recompression path",
    )

    for s in states:
        ax.annotate(
            f"{s.label}\n({s.T_K - 273.15:.0f}°C, {s.P_Pa / 1e6:.0f} MPa)",
            (s.s_J_kgK, s.T_K),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=9,
        )

    Tc = CP.PropsSI("Tcrit", "CO2")
    ax.axhline(Tc, color="red", linestyle=":", alpha=0.4, label=f"T_crit = {Tc:.1f} K")

    ax.set_xlabel("Specific entropy (J/kg·K)")
    ax.set_ylabel("Temperature (K)")
    ax.set_title(
        "sCO₂ Recompression Cycle — T-s Diagram\n"
        "Illustrative state points (no solver — see Phase 3 Modelica for converged results)"
    )
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150)
    return fig


def cycle_summary_table(states: list[CycleState]) -> list[dict[str, float | str]]:
    """Tabular form of the state points — used by the Streamlit metric grid."""
    return [
        {
            "Point": s.label,
            "T (°C)": round(s.T_K - 273.15, 1),
            "P (MPa)": round(s.P_Pa / 1e6, 2),
            "s (J/kg·K)": round(s.s_J_kgK, 1),
        }
        for s in states
    ]


if __name__ == "__main__":
    states = build_states()
    fig = plot_ts_diagram(states)
    print("Saved: sco2_recompression_ts.png")
    for row in cycle_summary_table(states):
        print(row)
