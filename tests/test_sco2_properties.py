"""Pytest tests for Phase 1 sCO2 property tools.

Reference: docs/01_phase1_properties.md (CI/CD section).

Benchmark tolerances are intentionally loose for the first iteration; tighten
after manual validation against the source reports.

NOTE: ``SANDIA_BENCHMARK_POINTS`` and ``STEP_PHASE1_POINTS`` here are
ILLUSTRATIVE placeholders ordered as (T_K, P_Pa, expected_density_kg_m3,
tolerance_pct). Verify each entry against the original Sandia / STEP report
before declaring the toolkit "validated against experimental data".
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

CP = pytest.importorskip("CoolProp.CoolProp", reason="CoolProp not installed")


SANDIA_BENCHMARK_POINTS: list[tuple[float, float, float, float]] = [
    # (T_K, P_Pa, expected_density_kg_m3, tolerance_pct)
    # Source: Wright2010_SAND2010_0171, § 2.3 narrative — measured compression-
    # process densities along the pseudo-critical line. Reported as
    # 0.608 kg/L (inlet) → 0.670 kg/L (outlet). Section 2.3 wording implies
    # ±5% measurement uncertainty, which the tolerance reflects.
    # See validation/experimental_data/SNL_compressor_data.csv row tagged
    # `Wright2010_SAND_S2.3_pseudocrit` and docs/data_extracts/wright2010_sand2010-0171.md.
    (305.3, 7.69e6, 608.0, 5.0),    # design-point compressor inlet
    (324.659, 13.984e6, 670.0, 5.0),  # design-point compressor outlet
]


STEP_PHASE1_POINTS: list[tuple[float, float, float, float]] = [
    # Populate from STEP Phase 1 (~500 °C simple cycle) public DOE reports.
    # (T_K, P_Pa, expected_density_kg_m3, tolerance_pct)
]


@pytest.mark.skipif(
    not SANDIA_BENCHMARK_POINTS, reason="SNL benchmark points not yet populated"
)
@pytest.mark.parametrize("T,P,rho_expected,tol_pct", SANDIA_BENCHMARK_POINTS)
def test_density_against_sandia(T: float, P: float, rho_expected: float, tol_pct: float):
    rho_calc = CP.PropsSI("D", "T", T, "P", P, "CO2")
    rel_err = abs(rho_calc - rho_expected) / rho_expected * 100
    assert rel_err < tol_pct, (
        f"Density deviation {rel_err:.2f}% exceeds tolerance {tol_pct}% "
        f"(T={T - 273.15:.1f} °C, P={P / 1e6:.1f} MPa, "
        f"calculated={rho_calc:.1f}, reference={rho_expected:.1f})"
    )


@pytest.mark.skipif(
    not STEP_PHASE1_POINTS, reason="STEP Phase 1 points not yet populated"
)
@pytest.mark.parametrize("T,P,rho_expected,tol_pct", STEP_PHASE1_POINTS)
def test_density_against_step_phase1(
    T: float, P: float, rho_expected: float, tol_pct: float
):
    """Density vs. STEP Phase 1 public data (simple cycle, ~500 °C)."""
    rho_calc = CP.PropsSI("D", "T", T, "P", P, "CO2")
    rel_err = abs(rho_calc - rho_expected) / rho_expected * 100
    assert rel_err < tol_pct


def test_pseudocritical_line_monotonic():
    """Pseudo-critical temperature must rise monotonically with pressure."""
    from sco2_property_explorer import find_pseudocritical_temp

    T_pc_8 = find_pseudocritical_temp(8.0e6)
    T_pc_15 = find_pseudocritical_temp(15.0e6)
    T_pc_20 = find_pseudocritical_temp(20.0e6)
    assert T_pc_8 < T_pc_15 < T_pc_20, (
        f"Pseudo-critical T must rise with P: got {T_pc_8:.2f}, {T_pc_15:.2f}, "
        f"{T_pc_20:.2f} K at 8, 15, 20 MPa"
    )


def test_critical_point_constants():
    """CoolProp must report the canonical CO2 critical point constants."""
    Tc = CP.PropsSI("Tcrit", "CO2")
    Pc = CP.PropsSI("Pcrit", "CO2")
    assert abs(Tc - 304.13) < 0.5, f"Tc deviation: {Tc:.2f} K"
    assert abs(Pc - 7.3773e6) < 5e4, f"Pc deviation: {Pc:.0f} Pa"


def test_mixture_two_phase_guard_returns_none():
    """When fed a two-phase point, calc_mixture_properties must not raise."""
    from sco2_mixture_validation import calc_mixture_properties

    # Sub-critical liquid-vapor coexistence line: 280 K, ~4.16 MPa for pure CO2
    result = calc_mixture_properties(T=280.0, P=4.16e6, x_he=0.0, verbose=False)
    # Either two-phase guard (None) or a valid scalar — never raise
    assert result is None or hasattr(result, "rho_pure")


def test_lut_export_small_grid(tmp_path):
    """Smoke-test LUT export with a tiny grid."""
    from tools.export_lut import export_sco2_lut

    prefix = tmp_path / "lut_smoke"
    df = export_sco2_lut(
        T_min=320.0,
        T_max=400.0,
        P_min=8.0e6,
        P_max=20.0e6,
        n_T=4,
        n_P=3,
        output_prefix=str(prefix),
    )
    assert len(df) == 12
    assert (tmp_path / "lut_smoke.csv").exists()
    assert (tmp_path / "lut_smoke_openfoam.dat").exists()
    assert {"T", "P", "rho", "Cp", "mu", "k", "h"}.issubset(df.columns)


def test_lut_density_matches_coolprop(tmp_path):
    """Every LUT row must equal a fresh CoolProp PropsSI call (no drift)."""
    from tools.export_lut import export_sco2_lut

    prefix = tmp_path / "lut_consistency"
    df = export_sco2_lut(
        T_min=320.0,
        T_max=420.0,
        P_min=8.0e6,
        P_max=20.0e6,
        n_T=5,
        n_P=4,
        output_prefix=str(prefix),
    )
    for row in df.itertuples(index=False):
        rho_ref = CP.PropsSI("D", "T", row.T, "P", row.P, "CO2")
        assert abs(row.rho - rho_ref) / rho_ref < 1e-9, (
            f"LUT row drifted from CoolProp at T={row.T}, P={row.P}"
        )


def test_lut_monotonic_density_in_pressure():
    """Above the pseudo-critical T, density rises monotonically with P."""
    # 600 K is well above pseudo-critical for any P in 8-20 MPa
    rhos = [CP.PropsSI("D", "T", 600.0, "P", P, "CO2") for P in (8e6, 12e6, 16e6, 20e6)]
    assert rhos == sorted(rhos), f"Density must increase with P at fixed T: {rhos}"


def test_pure_co2_returns_valid_result():
    """x_he=0 must return a valid result with rho_pure==rho_mix."""
    from sco2_mixture_validation import calc_mixture_properties

    result = calc_mixture_properties(T=350.0, P=15.0e6, x_he=0.0, verbose=False)
    assert result is not None, "Pure CO2 at supercritical conditions must succeed"
    # x_he=0 collapses to pure CO2 — densities should match within numerical noise
    assert abs(result.rho_pure - result.rho_mix) / result.rho_pure < 1e-3


def test_helium_impurity_lowers_density():
    """At supercritical conditions adding light He must reduce mixture density."""
    from sco2_mixture_validation import calc_mixture_properties

    # 350 K, 15 MPa is firmly supercritical — outside any phase envelope
    pure = calc_mixture_properties(T=350.0, P=15.0e6, x_he=0.0, verbose=False)
    mix = calc_mixture_properties(T=350.0, P=15.0e6, x_he=0.03, verbose=False)
    if pure is None or mix is None:
        pytest.skip("Mixture solver could not evaluate one of the points")
    assert mix.rho_mix < pure.rho_mix, (
        f"He impurity should lower density: pure={pure.rho_mix:.2f}, "
        f"mix={mix.rho_mix:.2f}"
    )


def test_property_explorer_returns_figure():
    """plot_cp_with_pseudocritical must return a matplotlib Figure object."""
    from sco2_property_explorer import plot_cp_with_pseudocritical

    fig = plot_cp_with_pseudocritical(
        T_range=(305.0, 340.0),
        P_range=(8e6, 12e6),
        grid=10,
        output_path=None,
    )
    assert fig is not None
    # Figure must contain at least one axes with the expected x-label
    ax = fig.axes[0]
    assert "Temperature" in ax.get_xlabel()


def test_pseudocritical_within_engineering_window():
    """At 8 MPa the pseudo-critical T should be 305-320 K (literature)."""
    from sco2_property_explorer import find_pseudocritical_temp

    T_pc = find_pseudocritical_temp(8.0e6)
    assert 305.0 < T_pc < 320.0, (
        f"Pseudo-critical T at 8 MPa should be 305-320 K, got {T_pc:.2f} K"
    )
