"""Tests for the recompression cycle T-s helper."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

CP = pytest.importorskip("CoolProp.CoolProp", reason="CoolProp not installed")

from sco2_cycle import (  # noqa: E402
    CycleParams,
    build_states,
    cycle_summary_table,
    plot_ts_diagram,
    saturation_dome,
)


def test_default_cycle_has_six_states():
    states = build_states()
    assert len(states) == 6
    assert [s.label for s in states] == ["1", "2", "3", "4", "5", "6"]


def test_pressures_alternate_low_high():
    """States 1, 5, 6 are low-pressure; 2, 3, 4 are high-pressure."""
    states = build_states()
    by_label = {s.label: s for s in states}
    P_low = CycleParams().P_low_Pa
    P_high = CycleParams().P_high_Pa
    for label in ("1", "5", "6"):
        assert by_label[label].P_Pa == P_low
    for label in ("2", "3", "4"):
        assert by_label[label].P_Pa == P_high


def test_entropy_rises_through_turbine():
    """State 5 (turbine outlet) must have higher entropy than state 4 (inlet) on a real expansion.

    With our purely isothermal-input idealisation this only holds because we
    ALSO drop pressure 25 MPa → 8 MPa. CoolProp's S(T, P) at lower P is
    higher → assertion holds. If somebody refactors to keep P fixed, this
    fails loudly — that is the purpose of the check.
    """
    states = build_states()
    s4 = next(s for s in states if s.label == "4")
    s5 = next(s for s in states if s.label == "5")
    assert s5.s_J_kgK > s4.s_J_kgK


def test_saturation_dome_sorted_by_entropy():
    """Liquid branch entropy must lie below vapour branch entropy at every T."""
    T, s_liq, s_vap = saturation_dome(n=20)
    assert (s_liq < s_vap).all()
    assert T[0] < T[-1]


def test_summary_table_round_trip():
    states = build_states()
    rows = cycle_summary_table(states)
    assert len(rows) == 6
    assert {"Point", "T (°C)", "P (MPa)", "s (J/kg·K)"} == set(rows[0].keys())


def test_plot_returns_figure():
    fig = plot_ts_diagram(output_path=None)
    assert fig is not None
    ax = fig.axes[0]
    assert "entropy" in ax.get_xlabel().lower()
