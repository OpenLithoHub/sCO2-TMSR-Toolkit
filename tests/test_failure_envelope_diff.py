"""Tests for validation/failure_envelopes/diff_status_codes.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DIFF_PY = REPO_ROOT / "validation" / "failure_envelopes" / "diff_status_codes.py"

spec = importlib.util.spec_from_file_location("diff_status_codes", DIFF_PY)
diff_status_codes = importlib.util.module_from_spec(spec)
sys.modules["diff_status_codes"] = diff_status_codes
spec.loader.exec_module(diff_status_codes)


def _grid_csv(tmp_path: Path, name: str, rows: list[tuple[float, float, int]]) -> Path:
    csv = tmp_path / name
    df = pd.DataFrame(rows, columns=["T_K", "P_Pa", "status_code"])
    df["status_label"] = df["status_code"].map(diff_status_codes.STATUS_LABELS)
    df.to_csv(csv, index=False)
    return csv


def test_diff_no_flips_returns_empty(tmp_path):
    a = _grid_csv(tmp_path, "a.csv", [(300.0, 8e6, 0), (310.0, 8e6, 0)])
    b = _grid_csv(tmp_path, "b.csv", [(300.0, 8e6, 0), (310.0, 8e6, 0)])
    flipped = diff_status_codes.diff(
        diff_status_codes._load_csv(a),
        diff_status_codes._load_csv(b),
    )
    assert flipped.empty


def test_diff_detects_flip(tmp_path):
    a = _grid_csv(tmp_path, "a.csv", [(300.0, 8e6, 0), (310.0, 8e6, 0)])
    b = _grid_csv(tmp_path, "b.csv", [(300.0, 8e6, 0), (310.0, 8e6, 3)])
    flipped = diff_status_codes.diff(
        diff_status_codes._load_csv(a),
        diff_status_codes._load_csv(b),
    )
    assert len(flipped) == 1
    row = flipped.iloc[0]
    assert row["T_K"] == 310.0
    assert row["from"] == "OK"
    assert row["to"] == "solver failed"


def test_diff_misaligned_grid_raises(tmp_path):
    a = _grid_csv(tmp_path, "a.csv", [(300.0, 8e6, 0), (310.0, 8e6, 0)])
    b = _grid_csv(tmp_path, "b.csv", [(300.0, 8e6, 0)])
    with pytest.raises(ValueError, match="grids differ"):
        diff_status_codes.diff(
            diff_status_codes._load_csv(a),
            diff_status_codes._load_csv(b),
        )


def test_main_exit_codes(tmp_path):
    a = _grid_csv(tmp_path, "a.csv", [(300.0, 8e6, 0), (310.0, 8e6, 0)])
    b_same = _grid_csv(tmp_path, "b_same.csv", [(300.0, 8e6, 0), (310.0, 8e6, 0)])
    b_flip = _grid_csv(tmp_path, "b_flip.csv", [(300.0, 8e6, 0), (310.0, 8e6, 3)])
    b_misalign = _grid_csv(tmp_path, "b_mis.csv", [(300.0, 8e6, 0)])

    assert diff_status_codes.main([str(b_same), "--old", str(a)]) == 0
    assert diff_status_codes.main([str(b_flip), "--old", str(a)]) == 1
    assert diff_status_codes.main([str(b_misalign), "--old", str(a)]) == 2


def test_main_rejects_both_sources(tmp_path):
    csv = _grid_csv(tmp_path, "x.csv", [(300.0, 8e6, 0)])
    with pytest.raises(SystemExit):
        diff_status_codes.main([str(csv), "--old", str(csv), "--git-ref", "HEAD"])


def test_main_rejects_neither_source(tmp_path):
    csv = _grid_csv(tmp_path, "x.csv", [(300.0, 8e6, 0)])
    with pytest.raises(SystemExit):
        diff_status_codes.main([str(csv)])
