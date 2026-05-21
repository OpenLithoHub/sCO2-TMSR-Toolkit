"""
sCO2 mixture property validation — CO2 + He two-phase guard.

Reference: docs/01_phase1_properties.md § 1.3

Adding an impurity converts the CO2 critical point into a phase envelope
(dew point + bubble point). At certain T/P the mixture can enter a two-phase
region, causing solver crashes. This module emits a physical warning instead
of a code exception when the two-phase region is encountered.
"""

from __future__ import annotations

from dataclasses import dataclass

import CoolProp.CoolProp as CP
from CoolProp.CoolProp import PhaseSI, PropsSI

from sco2_warnings import warn_placeholder

PHASE_NAMES = {
    "liquid": "liquid",
    "gas": "gas",
    "supercritical": "supercritical",
    "supercritical_liquid": "supercritical_liquid",
    "supercritical_gas": "supercritical_gas",
    "twophase": "TWO-PHASE ⚠",
    "unknown": "unknown",
}


@dataclass
class MixtureResult:
    rho_pure: float
    rho_mix: float
    cp_pure: float
    cp_mix: float
    phase: str

    @property
    def rho_delta_pct(self) -> float:
        return 100.0 * (self.rho_mix - self.rho_pure) / self.rho_pure

    @property
    def cp_delta_pct(self) -> float:
        return 100.0 * (self.cp_mix - self.cp_pure) / self.cp_pure


def check_phase(T: float, P: float, fluid: str = "CO2") -> str:
    """Return CoolProp phase string, or 'unknown' on failure."""
    try:
        return PhaseSI("T", T, "P", P, fluid)
    except Exception:
        return "unknown"


def calc_mixture_properties(
    T: float, P: float, x_he: float, verbose: bool = True
) -> MixtureResult | None:
    """Compute CO2-He mixture properties.

    Parameters
    ----------
    T : temperature (K)
    P : pressure (Pa)
    x_he : He mole fraction (0-1)

    Returns
    -------
    MixtureResult or None — None when the operating point is in the two-phase
    region or the mixture solver fails. Two-phase regions must be avoided in
    engineering designs.
    """
    phase = check_phase(T, P)
    if phase == "twophase":
        if verbose:
            print(
                f"⚠  Physical warning: T={T - 273.15:.1f} °C, P={P / 1e6:.2f} MPa "
                "is in the two-phase region!"
            )
            print(
                "   Impurity-induced phase-envelope shift may cause "
                "liquid-gas coexistence here."
            )
            print("   Engineering design must avoid this operating window entirely.")
        return None

    rho_pure = PropsSI("D", "T", T, "P", P, "CO2")
    cp_pure = PropsSI("C", "T", T, "P", P, "CO2")

    try:
        mixture = f"HEOS::CO2[{1 - x_he:.4f}]&Helium[{x_he:.4f}]"
        rho_mix = PropsSI("D", "T", T, "P", P, mixture)
        cp_mix = PropsSI("C", "T", T, "P", P, mixture)
    except Exception as e:
        warn_placeholder(
            "mixture-eos",
            f"CO2-He HEOS solver failed at T={T:.1f} K, P={P / 1e6:.2f} MPa, "
            f"x_he={x_he:.4f}: {e}",
        )
        if verbose:
            print(f"⚠  Mixture calculation failed (log this as an Issue!): {e}")
        return None

    result = MixtureResult(
        rho_pure=rho_pure,
        rho_mix=rho_mix,
        cp_pure=cp_pure,
        cp_mix=cp_mix,
        phase=phase,
    )

    if verbose:
        phase_label = PHASE_NAMES.get(phase, phase)
        print(
            f"T={T - 273.15:.1f} °C | P={P / 1e6:.2f} MPa | "
            f"x_He={x_he * 100:.2f}% | Phase: {phase_label}"
        )
        print(
            f"  Density: pure CO₂={rho_pure:.2f} → mixture={rho_mix:.2f} kg/m³  "
            f"(Δ={result.rho_delta_pct:+.2f}%)"
        )
        print(
            f"  Cp:      pure CO₂={cp_pure:.0f} → mixture={cp_mix:.0f} J/kg·K  "
            f"(Δ={result.cp_delta_pct:+.2f}%)"
        )
    return result


if __name__ == "__main__":
    # Engineering test points: near pseudo-critical operating window
    print(f"CoolProp version: {CP.__version__}\n")
    for x in (0.0, 0.005, 0.01, 0.03):
        calc_mixture_properties(T=308.15, P=8.0e6, x_he=x)
        print()
