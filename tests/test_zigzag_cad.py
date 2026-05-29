"""Tests for tools/cad/zigzag.py — STL generator for case02."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from tools.cad.zigzag import ZigzagParams, build_stl, centreline, main


def test_centreline_apex_amplitude_matches_param():
    """At phase 0.5 the triangular wave reaches +amplitude exactly."""
    params = ZigzagParams(
        length=14.0, period=7.0, amplitude=1.0, n_segments_per_period=12
    )
    pts = centreline(params)
    ys = [y for _, y in pts]
    assert max(ys) == pytest.approx(params.amplitude, abs=1e-9)
    assert min(ys) == pytest.approx(-params.amplitude, abs=1e-9)


def test_build_stl_is_well_formed_ascii():
    """STL must start with `solid`, end with `endsolid`, and have facet/endfacet pairs."""
    params = ZigzagParams(length=14.0, period=7.0, n_segments_per_period=8)
    stl = build_stl(params, name="zigzag_wall")
    assert stl.startswith("solid zigzag_wall\n")
    assert stl.rstrip().endswith("endsolid zigzag_wall")
    assert stl.count("facet normal") == stl.count("endfacet")
    assert stl.count("outer loop") == stl.count("endloop")
    # 8 facets per segment × 16 segments (2 periods × 8 segs/period)
    assert stl.count("facet normal") == 8 * 16


def test_main_writes_file_to_disk(tmp_path):
    """The CLI entrypoint must emit a non-empty STL at the requested path."""
    out = tmp_path / "zz.stl"
    rc = main(
        [
            "--out",
            str(out),
            "--length",
            "14",
            "--period",
            "7",
            "--amplitude",
            "1",
            "--segments",
            "8",
        ]
    )
    assert rc == 0
    assert out.exists() and out.stat().st_size > 0
    text = out.read_text()
    assert "facet normal" in text
