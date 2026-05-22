"""Tests for tools/compressor_map_to_modelica.py.

Confirms that the BYOD compressor-map CSV → Modelica .txt converter:
- accepts the shipping placeholder CSV (validation/compressor_maps/...)
- emits the `#1` magic header + `double <name>(rows, cols)` shape line
- preserves row order and column count
- rejects non-monotonic φ rows (a real source of opaque
  Modelica.Blocks.Tables errors at simulation start)
- rejects CSVs missing required columns
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from tools.compressor_map_to_modelica import (  # noqa: E402
    parse_csv,
    render_modelica_txt,
    main,
)


SHIPPING_CSV = REPO_ROOT / "validation" / "compressor_maps" / "sandia_main_compressor.csv"
SHIPPING_TURBINE_CSV = REPO_ROOT / "validation" / "turbine_maps" / "sandia_main_turbine.csv"


def test_shipping_csv_parses_to_nine_rows():
    rows = parse_csv(SHIPPING_CSV)
    assert len(rows) == 9
    assert rows[0].phi == 0.010
    assert rows[-1].phi == 0.040


def test_shipping_csv_emits_modelica_txt_header():
    rows = parse_csv(SHIPPING_CSV)
    txt = render_modelica_txt(rows, table_name="compressor_map")
    lines = txt.splitlines()
    assert lines[0] == "#1"
    assert lines[1] == "double compressor_map(9, 3)"
    # 9 data rows after the two-line header.
    assert len(lines) == 2 + 9


def test_phi_must_be_strictly_increasing(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "phi,psi,eta\n"
        "0.020,0.78,0.84\n"
        "0.020,0.78,0.85\n"   # duplicate phi
    )
    with pytest.raises(ValueError, match="strictly increasing"):
        parse_csv(bad)


def test_missing_columns_rejected(tmp_path):
    bad = tmp_path / "missing.csv"
    bad.write_text("phi,psi\n0.02,0.78\n")
    with pytest.raises(ValueError, match="missing required columns"):
        parse_csv(bad)


def test_main_writes_default_txt_next_to_csv(tmp_path):
    csv = tmp_path / "tiny.csv"
    csv.write_text("phi,psi,eta\n0.01,0.6,0.5\n0.02,0.8,0.85\n")
    rc = main([str(csv)])
    assert rc == 0
    out = csv.with_suffix(".txt")
    assert out.exists()
    body = out.read_text().splitlines()
    assert body[0] == "#1"
    assert body[1] == "double compressor_map(2, 3)"


def test_main_respects_custom_output_and_table_name(tmp_path):
    csv = tmp_path / "tiny.csv"
    csv.write_text("phi,psi,eta\n0.01,0.6,0.5\n0.02,0.8,0.85\n")
    out = tmp_path / "elsewhere.txt"
    rc = main([str(csv), "-o", str(out), "--table-name", "rc_map"])
    assert rc == 0
    body = out.read_text()
    assert body.startswith("#1\ndouble rc_map(2, 3)\n")


def test_shipping_csv_round_trips_through_main(tmp_path):
    """Regenerate the shipping .txt into a tmp dir and confirm it matches the
    in-tree copy byte-for-byte. Guards against future format drift."""
    out = tmp_path / "regen.txt"
    rc = main([str(SHIPPING_CSV), "-o", str(out)])
    assert rc == 0
    expected = (REPO_ROOT / "validation" / "compressor_maps"
                / "sandia_main_compressor.txt").read_text()
    assert out.read_text() == expected


def test_turbine_csv_parses_to_nine_rows():
    """Same converter handles the BYOD turbine map (Gap 1 symmetric extension)."""
    rows = parse_csv(SHIPPING_TURBINE_CSV)
    assert len(rows) == 9
    assert rows[0].phi == 0.012
    assert rows[-1].phi == 0.040


def test_turbine_csv_round_trips_with_table_name(tmp_path):
    """Turbine CSV round-trips byte-for-byte with --table-name turbine_map."""
    out = tmp_path / "regen.txt"
    rc = main([str(SHIPPING_TURBINE_CSV), "-o", str(out), "--table-name", "turbine_map"])
    assert rc == 0
    expected = (REPO_ROOT / "validation" / "turbine_maps"
                / "sandia_main_turbine.txt").read_text()
    assert out.read_text() == expected
