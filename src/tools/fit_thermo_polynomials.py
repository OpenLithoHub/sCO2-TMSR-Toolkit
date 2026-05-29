"""Fit sCO2 thermophysical properties to OpenFOAM polynomial coefficients.

Reference: docs/02_phase2_cfd_rom.md § 2.3 (Method A) +
           docs/known_gaps.md#pche-geometry.

OpenFOAM's icoPolynomial + hPolynomial accept T-only polynomials, so this
fitter produces fixed-pressure fits — appropriate for case04_chiller where
the gas-side pressure is essentially constant at 7.7 MPa (Wright2010
SAND2010-0171 § 3) over the meshed flow domain.

For a full T-P-coupled lookup the project must move to a custom OpenFOAM
thermo class (Method B in the docs). That requires an OpenFOAM build
environment and is tracked under docs/known_gaps.md#pche-geometry.

Output is two `<name>` blocks suitable for pasting into a
`thermophysicalProperties` mixture { thermodynamics / transport / ... }
block, plus a JSON sidecar holding the raw coefficients for tests.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class PolynomialFit:
    """Coefficients ascending in T-power: c0 + c1*T + c2*T^2 + ..."""

    coeffs: tuple[float, ...]
    T_min: float
    T_max: float
    rms_error: float
    rel_max_error: float

    def evaluate(self, T: float | np.ndarray) -> float | np.ndarray:
        T = np.asarray(T)
        return sum(c * T**i for i, c in enumerate(self.coeffs))


def fit_polynomial(
    T: np.ndarray,
    y: np.ndarray,
    order: int = 7,
) -> PolynomialFit:
    """Fit y(T) to an `order`-degree polynomial; return ascending coefficients.

    OpenFOAM's polynomial thermo expects coefficients in ascending order
    (c0 first), but numpy.polyfit returns descending. We flip after fitting.
    """
    if T.shape != y.shape:
        raise ValueError(f"T and y must share shape; got {T.shape} vs {y.shape}.")
    if T.size < order + 1:
        raise ValueError(f"Need at least order+1 = {order + 1} samples; got {T.size}.")
    coeffs_desc = np.polyfit(T, y, deg=order)
    coeffs_asc = tuple(float(c) for c in coeffs_desc[::-1])

    fit_y = sum(c * T**i for i, c in enumerate(coeffs_asc))
    rms = float(np.sqrt(np.mean((fit_y - y) ** 2)))
    rel_max = float(np.max(np.abs(fit_y - y) / np.abs(y)))

    return PolynomialFit(
        coeffs=coeffs_asc,
        T_min=float(T.min()),
        T_max=float(T.max()),
        rms_error=rms,
        rel_max_error=rel_max,
    )


def fit_sco2_chiller_thermo(
    T_min: float = 320.0,
    T_max: float = 360.0,
    n_T: int = 200,
    P_fixed: float = 7.7e6,
    order: int = 7,
    fluid: str = "CO2",
) -> dict[str, PolynomialFit]:
    """Fit rho(T), Cp(T), mu(T), k(T) at fixed P for the chiller gas side.

    Default window 320–360 K stays *above* the pseudo-critical Cp spike at
    7.7 MPa (peak around 305–310 K, where Cp jumps from ~4 to ~13 kJ/kg·K
    over 5 K — un-fittable by a degree-7 polynomial). Wright2010 § 3 puts
    the gas-side **inlet** at ≈ 323 K and **outlet** at ≈ 305 K, so the
    chiller's outlet half crosses the spike: this fit covers the inlet
    half well (rel-max errors < 2e-4) but is invalid for T < 320 K. A
    full chiller simulation needs the Method-B custom thermo class —
    tracked under docs/known_gaps.md#pche-geometry.
    """
    import CoolProp.CoolProp as CP  # local import keeps numpy-only callers light

    T = np.linspace(T_min, T_max, n_T)
    rho = np.array([CP.PropsSI("D", "T", t, "P", P_fixed, fluid) for t in T])
    cp = np.array([CP.PropsSI("C", "T", t, "P", P_fixed, fluid) for t in T])
    mu = np.array([CP.PropsSI("V", "T", t, "P", P_fixed, fluid) for t in T])
    k = np.array([CP.PropsSI("L", "T", t, "P", P_fixed, fluid) for t in T])

    return {
        "rho": fit_polynomial(T, rho, order=order),
        "Cp": fit_polynomial(T, cp, order=order),
        "mu": fit_polynomial(T, mu, order=order),
        "k": fit_polynomial(T, k, order=order),
    }


def render_openfoam_block(fits: dict[str, PolynomialFit], P_fixed: float) -> str:
    """Render a `thermophysicalProperties` mixture block using polynomial fits.

    OpenFOAM's polynomial syntax: `Cp ( c0 c1 c2 c3 c4 c5 c6 c7 );` — exactly
    8 coefficients, ascending in T-power. Order < 7 must be padded with zeros.
    """

    def coeffs_padded(fit: PolynomialFit, n: int = 8) -> str:
        out = list(fit.coeffs) + [0.0] * (n - len(fit.coeffs))
        return " ".join(f"{c:.6e}" for c in out[:n])

    rho = fits["rho"]
    cp = fits["Cp"]
    mu = fits["mu"]
    k = fits["k"]

    return f"""// sCO2 polynomial fit — fixed-P approximation at P = {P_fixed:.3e} Pa.
// Fit window: {rho.T_min:.1f} K – {rho.T_max:.1f} K.
// rms / rel-max errors:
//   rho: rms={rho.rms_error:.3e}, rel-max={rho.rel_max_error:.3e}
//   Cp:  rms={cp.rms_error:.3e}, rel-max={cp.rel_max_error:.3e}
//   mu:  rms={mu.rms_error:.3e}, rel-max={mu.rel_max_error:.3e}
//   k:   rms={k.rms_error:.3e}, rel-max={k.rel_max_error:.3e}

mixture
{{
    specie
    {{
        molWeight   44.01;          // g/mol — CO2
    }}
    equationOfState
    {{
        rhoCoeffs<8>    ( {coeffs_padded(rho)} );
    }}
    thermodynamics
    {{
        Hf              0;
        Sf              0;
        CpCoeffs<8>     ( {coeffs_padded(cp)} );
    }}
    transport
    {{
        muCoeffs<8>     ( {coeffs_padded(mu)} );
        kappaCoeffs<8>  ( {coeffs_padded(k)} );
    }}
}}
"""


def render_thermophysical_properties_file(
    fits: dict[str, PolynomialFit],
    P_fixed: float,
) -> str:
    """Wrap the mixture block in a complete `thermophysicalProperties` dict."""
    block = render_openfoam_block(fits, P_fixed)
    header = """/*--------------------------------*- C++ -*----------------------------------*\\
| sCO2 polynomial-fit thermophysicalProperties for case04_chiller gas        |
| region. Generated by `python -m tools.fit_thermo_polynomials`.              |
|                                                                             |
| Method-A path per docs/02_phase2_cfd_rom.md § 2.3: fixed-P polynomial fit  |
| (Wright2010 chiller gas-side P ≈ 7.7 MPa is approximately uniform across   |
| the meshed flow domain; see Wright2010 SAND2010-0171 § 3).                 |
|                                                                             |
| Limits — see docs/known_gaps.md#pche-geometry:                             |
|   - Fit is T-only; pressure variation away from P_fixed is NOT captured.   |
|   - Polynomial degree 7 cannot resolve the pseudo-critical Cp peak; the    |
|     default fit window 320–360 K stays above the sharpest spike (which    |
|     sits near 305–310 K at 7.7 MPa). Wright2010 chiller outlet ≈ 305 K    |
|     is BELOW the fit floor — outlet-side cells need Method B.             |
|   - For T-P-coupled lookup, move to Method B (custom sCO2Thermo class).    |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant/gas";
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       polynomial;
    thermo          hPolynomial;
    equationOfState icoPolynomial;
    specie          specie;
    energy          sensibleEnthalpy;
}

"""
    footer = "\n// ************************************************************************* //\n"
    return header + block + footer


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Fit sCO2 thermophysical properties to OpenFOAM polynomials.",
    )
    p.add_argument("--T-min", type=float, default=320.0, help="Lower fit bound (K)")
    p.add_argument("--T-max", type=float, default=360.0, help="Upper fit bound (K)")
    p.add_argument("--n-T", type=int, default=200, help="Number of fit samples")
    p.add_argument(
        "--P-fixed",
        type=float,
        default=7.7e6,
        help="Pressure at which the polynomial is evaluated (Pa)",
    )
    p.add_argument(
        "--order", type=int, default=7, help="Polynomial degree (max 7 for OpenFOAM)"
    )
    p.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to write the OpenFOAM thermophysicalProperties dict",
    )
    p.add_argument(
        "--coeffs-json",
        type=Path,
        default=None,
        help="Optional JSON sidecar with raw coefficients + error metrics",
    )
    args = p.parse_args(argv)

    if args.order > 7:
        print(f"warning: order {args.order} > 7 will exceed OpenFOAM polyN<8> bounds")

    fits = fit_sco2_chiller_thermo(
        T_min=args.T_min,
        T_max=args.T_max,
        n_T=args.n_T,
        P_fixed=args.P_fixed,
        order=args.order,
    )
    args.output.write_text(render_thermophysical_properties_file(fits, args.P_fixed))
    print(f"Wrote {args.output}")

    if args.coeffs_json:
        args.coeffs_json.write_text(
            json.dumps(
                {
                    name: {
                        "coeffs": list(fit.coeffs),
                        "T_min": fit.T_min,
                        "T_max": fit.T_max,
                        "rms_error": fit.rms_error,
                        "rel_max_error": fit.rel_max_error,
                    }
                    for name, fit in fits.items()
                },
                indent=2,
            )
        )
        print(f"Wrote {args.coeffs_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
