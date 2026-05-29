"""Tests for src/tools/validate_against_sandia.py.

Covers the multi-check ``--check rho,h`` extension plus the existing
single-check behaviour. Each test runs against a tmp_path CSV so we
don't couple to in-flight transcription of the shipping benchmark
CSVs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from tools.validate_against_sandia import (  # noqa: E402
    _parse_checks,
    main,
    validate,
)


# Reference state CoolProp can evaluate without surprises:
# CO2 at 350 K / 8 MPa is well clear of the pseudo-critical line.
_REF_T = 350.0
_REF_P = 8_000_000.0


def _csv_with(tmp_path: Path, rows: list[str], header_extra: str = "") -> Path:
    header = (
        "T_inlet_K,P_inlet_Pa,T_outlet_K,P_outlet_Pa,"
        "rho_inlet_measured,h_inlet_measured_J_kg,"
        "efficiency_measured,source_ref" + header_extra
    )
    csv = tmp_path / "bench.csv"
    csv.write_text("\n".join([header, *rows]) + "\n")
    return csv


def _coolprop_ref(key: str) -> float:
    import CoolProp.CoolProp as CP

    return float(CP.PropsSI(key, "T", _REF_T, "P", _REF_P, "CO2"))


def test_parse_checks_single():
    assert _parse_checks("rho") == ["rho"]


def test_parse_checks_comma_separated():
    assert _parse_checks("rho,h") == ["rho", "h"]


def test_parse_checks_strips_whitespace():
    assert _parse_checks(" rho , h ") == ["rho", "h"]


def test_parse_checks_rejects_unknown():
    with pytest.raises(SystemExit, match="unknown"):
        _parse_checks("rho,bogus")


def test_parse_checks_rejects_empty():
    with pytest.raises(SystemExit, match="at least one"):
        _parse_checks(",")


def test_validate_rho_pass(tmp_path):
    rho = _coolprop_ref("D")
    csv = _csv_with(
        tmp_path,
        [f"{_REF_T},{_REF_P},,,{rho},,,row_a"],
    )
    assert validate(csv, tolerance_pct=0.5, check="rho") == 0


def test_validate_h_pass(tmp_path):
    h = _coolprop_ref("H")
    csv = _csv_with(
        tmp_path,
        [f"{_REF_T},{_REF_P},,,,{h},,row_a"],
    )
    assert validate(csv, tolerance_pct=0.5, check="h") == 0


def test_validate_rho_fail_outside_tolerance(tmp_path):
    rho = _coolprop_ref("D")
    bogus = rho * 1.5
    csv = _csv_with(
        tmp_path,
        [f"{_REF_T},{_REF_P},,,{bogus},,,row_a"],
    )
    assert validate(csv, tolerance_pct=1.0, check="rho") == 1


def test_validate_skips_empty_check_column(tmp_path):
    """Row populates ρ but not h. --check h must skip cleanly."""
    rho = _coolprop_ref("D")
    csv = _csv_with(
        tmp_path,
        [f"{_REF_T},{_REF_P},,,{rho},,,row_a"],
    )
    assert validate(csv, tolerance_pct=1.0, check="h") == 0


def test_validate_skips_csv_without_column(tmp_path):
    """CSV predating the h column — validator must skip with rc=0."""
    header = (
        "T_inlet_K,P_inlet_Pa,T_outlet_K,P_outlet_Pa,"
        "rho_inlet_measured,efficiency_measured,source_ref"
    )
    rho = _coolprop_ref("D")
    csv = tmp_path / "legacy.csv"
    csv.write_text(f"{header}\n{_REF_T},{_REF_P},,,{rho},,row_a\n")
    assert validate(csv, tolerance_pct=1.0, check="h") == 0


def test_main_combined_check_passes(tmp_path):
    rho = _coolprop_ref("D")
    h = _coolprop_ref("H")
    csv = _csv_with(
        tmp_path,
        [f"{_REF_T},{_REF_P},,,{rho},{h},,row_a"],
    )
    rc = main(["--data", str(csv), "--tolerance", "0.5", "--check", "rho,h"])
    assert rc == 0


def test_main_combined_check_fails_if_any_fails(tmp_path):
    rho = _coolprop_ref("D")
    bad_h = _coolprop_ref("H") * 2.0
    csv = _csv_with(
        tmp_path,
        [f"{_REF_T},{_REF_P},,,{rho},{bad_h},,row_a"],
    )
    rc = main(["--data", str(csv), "--tolerance", "0.5", "--check", "rho,h"])
    assert rc == 1


def test_main_unknown_check_exits():
    with pytest.raises(SystemExit):
        main(["--check", "bogus"])
