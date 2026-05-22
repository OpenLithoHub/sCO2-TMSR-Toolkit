"""Tests for tools/cad/helical_coil.py — STL generator for case04_chiller."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from tools.cad.helical_coil import (  # noqa: E402
    HelicalCoilParams,
    build_shell_stl,
    build_tube_stl,
    helix_centreline,
    implied_arc_length_mm,
    main,
    parallel_transport_frames,
    _vcross,
    _vdot,
)


def test_centreline_endpoints_match_helix_formula():
    """First point at θ=0 sits at (R, 0, 0); last point at θ=N has z = N·pitch."""
    p = HelicalCoilParams(coil_radius=200.0, coil_pitch=101.6, n_turns=15.0,
                          n_segments_per_turn=32)
    pts = helix_centreline(p)
    assert pts[0] == pytest.approx((200.0, 0.0, 0.0), abs=1e-9)
    x_end, y_end, z_end = pts[-1]
    # After integer N turns we're back at angle 0 in the (x, y) plane.
    assert x_end == pytest.approx(200.0, abs=1e-9)
    assert y_end == pytest.approx(0.0, abs=1e-9)
    assert z_end == pytest.approx(15.0 * 101.6, abs=1e-9)


def test_implied_arc_length_close_to_wright2010_table32():
    """Default knobs (R=200, pitch=101.6, N=15) should land within 5 % of 19.15 m."""
    p = HelicalCoilParams()
    arc_mm = implied_arc_length_mm(p)
    assert arc_mm == pytest.approx(15.0 * math.sqrt((2 * math.pi * 200.0) ** 2
                                                    + 101.6 ** 2), rel=1e-12)
    arc_m = arc_mm / 1000.0
    assert abs(arc_m - 19.15) / 19.15 < 0.05


def test_parallel_transport_frame_is_orthonormal():
    """Each (T, N, B) triple must be orthonormal at every sample."""
    p = HelicalCoilParams(n_turns=2.0, n_segments_per_turn=24)
    frames = parallel_transport_frames(helix_centreline(p))
    for t, n, b in frames:
        assert _vdot(t, t) == pytest.approx(1.0, abs=1e-9)
        assert _vdot(n, n) == pytest.approx(1.0, abs=1e-9)
        assert _vdot(b, b) == pytest.approx(1.0, abs=1e-9)
        assert _vdot(t, n) == pytest.approx(0.0, abs=1e-9)
        assert _vdot(t, b) == pytest.approx(0.0, abs=1e-9)
        assert _vdot(n, b) == pytest.approx(0.0, abs=1e-9)
        # Right-handed: T × N == B.
        cx = _vcross(t, n)
        for a, c in zip(cx, b):
            assert a == pytest.approx(c, abs=1e-9)


def test_tube_stl_is_well_formed_ascii():
    """STL must open/close with solid/endsolid and balance facet/endfacet."""
    p = HelicalCoilParams(n_turns=2.0, n_segments_per_turn=16, n_circumferential=12)
    stl = build_tube_stl(p, name="helical_tube")
    assert stl.startswith("solid helical_tube\n")
    assert stl.rstrip().endswith("endsolid helical_tube")
    assert stl.count("facet normal") == stl.count("endfacet")
    assert stl.count("outer loop") == stl.count("endloop")
    # 2 turns × 16 segs/turn = 32 spans, 12 circ facets/span × 2 tris/facet.
    assert stl.count("facet normal") == 32 * 12 * 2


def test_shell_stl_is_well_formed_ascii():
    p = HelicalCoilParams(n_turns=1.0, n_segments_per_turn=8, n_circumferential=16)
    stl = build_shell_stl(p, name="chiller_shell")
    assert stl.startswith("solid chiller_shell\n")
    assert stl.rstrip().endswith("endsolid chiller_shell")
    assert stl.count("facet normal") == stl.count("endfacet")
    # n_circ is clamped to >=32 for the shell; 32 segments × 2 tris each.
    assert stl.count("facet normal") == 32 * 2


def test_main_writes_both_stls(tmp_path):
    """CLI must emit both helical_tube.stl and chiller_shell.stl, non-empty."""
    rc = main([
        "--out-dir", str(tmp_path),
        "--turns", "1",
        "--seg-per-turn", "16",
        "--n-circ", "12",
    ])
    assert rc == 0
    tube = tmp_path / "helical_tube.stl"
    shell = tmp_path / "chiller_shell.stl"
    assert tube.exists() and tube.stat().st_size > 0
    assert shell.exists() and shell.stat().st_size > 0
    assert "facet normal" in tube.read_text()
    assert "facet normal" in shell.read_text()


def test_tube_id_property_matches_wright2010():
    """tube_id = tube_od - 2·wall = 38.1 - 4.8 = 33.3 mm (Wright2010 Table 3.2)."""
    p = HelicalCoilParams()
    assert p.tube_id == pytest.approx(33.3, abs=1e-9)
