"""Tests for the mixture failure-envelope sweep."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

CP = pytest.importorskip("CoolProp.CoolProp", reason="CoolProp not installed")

from sco2_failure_envelope import (  # noqa: E402
    NEAR_CRITICAL,
    OK,
    SOLVER_FAILED,
    TWO_PHASE,
    classify_point,
    sweep,
)


def test_supercritical_pure_co2_is_ok():
    """350 K, 15 MPa is firmly supercritical — must classify as OK."""
    assert classify_point(350.0, 15e6, "Helium", 0.0) == OK


def test_saturation_band_marks_two_phase():
    """At 280 K, P_sat ≈ 4.16 MPa — points inside the saturation band classify as two-phase."""
    assert classify_point(280.0, 4.16e6, "Helium", 0.0) == TWO_PHASE


def test_near_critical_classification():
    """Within ±2 K / ±0.2 MPa of CO₂ critical point classifies as near-critical."""
    Tc = CP.PropsSI("Tcrit", "CO2")
    Pc = CP.PropsSI("Pcrit", "CO2")
    assert classify_point(Tc, Pc, "Helium", 0.0) == NEAR_CRITICAL


def test_sweep_returns_expected_shape():
    """Sweep grid must match requested resolution and contain only valid codes."""
    T_axis, P_axis, grid = sweep(
        impurity="Helium", x_imp=0.0, n_T=8, n_P=6,
        T_range=(290.0, 700.0), P_range=(8e6, 25e6),
    )
    assert T_axis.shape == (8,)
    assert P_axis.shape == (6,)
    assert grid.shape == (6, 8)
    valid = {OK, TWO_PHASE, NEAR_CRITICAL, SOLVER_FAILED}
    assert set(grid.flatten().tolist()).issubset(valid)


def test_helium_mixture_has_failures():
    """CO₂+He at 3% must hit at least some HEOS failures in the engineering window.

    If CoolProp is ever fixed enough that this assertion flips to OK
    everywhere, that is excellent news worth writing up — update the
    test (and this docstring) instead of suppressing it.
    """
    _, _, grid = sweep(
        impurity="Helium", x_imp=0.03, n_T=10, n_P=10,
        T_range=(290.0, 700.0), P_range=(8e6, 25e6),
    )
    failures = (grid == SOLVER_FAILED).sum()
    assert failures > 0, (
        "Helium HEOS used to fail at high pressure — expected at least one "
        "failure. If this passes by accident the upstream EOS may have "
        "improved; update the test."
    )


def test_water_mixture_mostly_ok():
    """CO₂+H₂O HEOS is documented as much more robust than CO₂+He."""
    _, _, grid = sweep(
        impurity="Water", x_imp=0.01, n_T=10, n_P=10,
        T_range=(310.0, 600.0), P_range=(8e6, 20e6),
    )
    n = grid.size
    ok_frac = (grid == OK).sum() / n
    assert ok_frac > 0.8, f"CO₂-H₂O HEOS expected to converge mostly; got {ok_frac:.2%}"
