"""Tests for tools/fit_thermo_polynomials.py — sCO2 → OpenFOAM polynomial dict.

Covers: round-trip fit accuracy on a known polynomial, fit-error bounds on
shipping coefficients, OpenFOAM dict header/format invariants, JSON sidecar
shape, and CLI smoke. Heavy CoolProp-driven fits are guarded by an
importorskip so the suite still runs in lean envs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from tools.fit_thermo_polynomials import (  # noqa: E402
    PolynomialFit,
    fit_polynomial,
    main,
    render_openfoam_block,
    render_thermophysical_properties_file,
)


def test_fit_polynomial_recovers_known_function():
    """Fitting a degree-3 polynomial reproduces the function within rms tolerance.

    We verify *values*, not raw coefficients: the Vandermonde system on
    T ∈ [300, 360] is ill-conditioned at high powers, so individual
    coefficients drift even when y(T) is recovered to machine precision.
    """
    T = np.linspace(300.0, 360.0, 200)
    true = (1.0, -2.0, 3.0, -0.5)
    y = sum(c * T**i for i, c in enumerate(true))

    fit = fit_polynomial(T, y, order=3)

    assert len(fit.coeffs) == 4
    assert np.allclose(fit.evaluate(T), y, rtol=1e-8, atol=1e-6)
    assert fit.rms_error < 1e-6
    assert fit.T_min == pytest.approx(300.0)
    assert fit.T_max == pytest.approx(360.0)


def test_fit_polynomial_evaluate_matches_polyval():
    """PolynomialFit.evaluate matches numpy polyval on the descending coeffs."""
    T = np.linspace(320.0, 360.0, 50)
    y = 1.5 + 2.0 * T - 1e-3 * T**2
    fit = fit_polynomial(T, y, order=2)

    eval_at = np.array([320.0, 340.0, 360.0])
    expected = 1.5 + 2.0 * eval_at - 1e-3 * eval_at**2
    assert np.allclose(fit.evaluate(eval_at), expected, rtol=1e-8)


def test_fit_polynomial_rejects_too_few_samples():
    T = np.array([300.0, 310.0, 320.0])
    with pytest.raises(ValueError, match="Need at least"):
        fit_polynomial(T, T**2, order=7)


def test_fit_polynomial_rejects_shape_mismatch():
    with pytest.raises(ValueError, match="must share shape"):
        fit_polynomial(np.linspace(300, 360, 50), np.linspace(300, 360, 40), order=3)


def _stub_fits() -> dict[str, PolynomialFit]:
    """Cheap synthetic fits for format-only tests (no CoolProp needed)."""
    T = np.linspace(320.0, 360.0, 50)
    return {
        "rho": fit_polynomial(T, 200.0 + 0.1 * T, order=7),
        "Cp": fit_polynomial(T, 1500.0 + 0.5 * T, order=7),
        "mu": fit_polynomial(T, 2e-5 + 1e-8 * T, order=7),
        "k": fit_polynomial(T, 0.04 + 1e-4 * T, order=7),
    }


def test_render_openfoam_block_has_eight_padded_coefficients():
    """OpenFOAM polyN<8> requires exactly 8 numbers — order < 7 must zero-pad."""
    T = np.linspace(320.0, 360.0, 20)
    fits = {
        "rho": fit_polynomial(T, 200.0 + 0.1 * T, order=2),
        "Cp": fit_polynomial(T, 1500.0 + 0.5 * T, order=2),
        "mu": fit_polynomial(T, 2e-5 + 1e-8 * T, order=2),
        "k": fit_polynomial(T, 0.04 + 1e-4 * T, order=2),
    }
    block = render_openfoam_block(fits, P_fixed=7.7e6)
    for tag in ("rhoCoeffs<8>", "CpCoeffs<8>", "muCoeffs<8>", "kappaCoeffs<8>"):
        line = next(l for l in block.splitlines() if tag in l)
        nums = line.split("(")[1].split(")")[0].split()
        assert len(nums) == 8, f"{tag} expected 8 coeffs, got {len(nums)}: {line}"


def test_render_thermophysical_properties_file_is_well_formed():
    text = render_thermophysical_properties_file(_stub_fits(), P_fixed=7.7e6)
    assert "FoamFile" in text
    assert text.count("{") == text.count("}")
    assert "thermoType" in text
    assert "icoPolynomial" in text
    assert "hPolynomial" in text
    assert "polynomial" in text
    assert "object      thermophysicalProperties;" in text
    assert "molWeight   44.01" in text


def test_shipping_coefficients_meet_quality_bounds():
    """The committed sco2_thermo_coeffs.json must satisfy the documented bounds.

    320–360 K at 7.7 MPa is well above the pseudo-critical Cp peak; we
    expect rel-max errors < 1e-3 across all four properties. If a CoolProp
    bump moves any of these out of band the maintainer should diff
    against the prior commit and document the change.
    """
    coeffs_path = (
        REPO_ROOT
        / "cases"
        / "case04_chiller"
        / "constant"
        / "gas"
        / "sco2_thermo_coeffs.json"
    )
    if not coeffs_path.exists():
        pytest.skip("sco2_thermo_coeffs.json not committed yet")
    data = json.loads(coeffs_path.read_text())
    for name in ("rho", "Cp", "mu", "k"):
        assert name in data, f"missing {name} in coeffs JSON"
        rec = data[name]
        assert len(rec["coeffs"]) == 8, f"{name}: OpenFOAM polyN<8> needs 8 coeffs"
        assert rec["T_min"] == pytest.approx(320.0)
        assert rec["T_max"] == pytest.approx(360.0)
        assert rec["rel_max_error"] < 1e-3, (
            f"{name} rel-max {rec['rel_max_error']:.3e} exceeds 1e-3 — "
            "regenerate via `python -m tools.fit_thermo_polynomials` and "
            "investigate before bumping the bound."
        )


def test_cli_smoke(tmp_path):
    """Driving main() end-to-end emits a parseable dict and JSON sidecar."""
    pytest.importorskip("CoolProp")
    out = tmp_path / "thermophysicalProperties"
    js = tmp_path / "coeffs.json"
    rc = main(
        [
            "--T-min",
            "320",
            "--T-max",
            "360",
            "--n-T",
            "60",
            "--output",
            str(out),
            "--coeffs-json",
            str(js),
        ]
    )
    assert rc == 0
    text = out.read_text()
    assert "FoamFile" in text and "icoPolynomial" in text
    parsed = json.loads(js.read_text())
    assert set(parsed) == {"rho", "Cp", "mu", "k"}
