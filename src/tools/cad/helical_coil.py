"""Generate a helical-coil STL for case04_chiller.

Reference: docs/02_phase2_cfd_rom.md § 2.5 +
docs/data_extracts/wright2010_sand2010-0171.md "Table 3.2 (p.30) — gas chiller PCHE-like geometry" +
cases/case04_chiller/README.md.

Why this exists
---------------
case04_chiller models the SNL 10 MWe test-loop gas chiller, which is a
helical-coil tube-and-shell heat exchanger (not a micro-channel PCHE).
Wright2010 Table 3.2 gives the engineering-scale geometry (Confidence A):

    tube OD          = 38.1 mm
    tube wall        =  2.4 mm   ⇒ tube ID = 33.3 mm
    single-coil len  = 19.15 m
    coil pitch       = 101.6 mm

Coil radius is not tabulated explicitly, so it is exposed as a CLI knob.
Defaults (R = 200 mm, N = 15 turns) imply an arc length of ~18.9 m, close
to the Table 3.2 value; the script prints the implied arc length so the
user can match Wright2010 by tweaking R or N.

Outputs
-------
Two ASCII STLs, written under cases/case04_chiller/constant/triSurface/:

    helical_tube.stl    → gas-side flow path: outer surface of the inner
                          tube (tube OD 38.1 mm). snappyHexMesh sees this
                          as the gas/liquid interface wall.
    chiller_shell.stl   → shell-side outer wall: a coaxial cylinder
                          enclosing the helix; its radius is set so the
                          shell annulus around the tube has the
                          Wright2010 Table 3.2 liquid-side hydraulic
                          diameter (14.4 mm) at first order.

Both STLs are produced in plain Python — no FreeCAD / CadQuery / Salome
— so CI on a vanilla machine can regenerate them.

Geometry note
-------------
Each centreline point is wrapped with a circle in the plane perpendicular
to the tangent. We use a *parallel-transport* Frenet frame (rotation
minimising frame, RMF) to avoid the cumulative twist that the naive
binormal frame would introduce on a helix; pure-helix geometry actually
admits an exact closed-form normal/binormal pair, but the parallel
transport is general and matches what snappyHexMesh expects on the
inlet/outlet end caps.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HelicalCoilParams:
    """All units mm; matches blockMeshDict scale=0.001 convention."""

    tube_od: float = 38.1          # outer tube diameter (Wright2010 Table 3.2)
    tube_wall: float = 2.4         # tube wall thickness (Wright2010 Table 3.2)
    coil_radius: float = 200.0     # helix radius R (centreline) — not in Table 3.2
    coil_pitch: float = 101.6      # axial advance per turn (Wright2010 Table 3.2)
    n_turns: float = 15.0          # turns; default chosen so arc length ≈ 19.15 m
    n_segments_per_turn: int = 64  # centreline samples per turn
    n_circumferential: int = 24    # facets around the tube cross-section
    shell_clearance: float = 14.4  # shell-annulus clearance (mm) — Wright2010
                                   #   Table 3.2 liquid-side D_h = 14.4 mm

    @property
    def tube_id(self) -> float:
        return self.tube_od - 2.0 * self.tube_wall


# --------------------------------------------------------------------------
# Helix sampling + parallel-transport frame
# --------------------------------------------------------------------------


def helix_centreline(p: HelicalCoilParams) -> list[tuple[float, float, float]]:
    """Return (x, y, z) points on the helix centreline, mm.

        x(θ) = R · cos(2πθ)
        y(θ) = R · sin(2πθ)
        z(θ) = pitch · θ           θ ∈ [0, n_turns]
    """
    n_total = max(2, int(round(p.n_turns * p.n_segments_per_turn)))
    pts: list[tuple[float, float, float]] = []
    for i in range(n_total + 1):
        theta = p.n_turns * i / n_total
        ang = 2.0 * math.pi * theta
        pts.append((
            p.coil_radius * math.cos(ang),
            p.coil_radius * math.sin(ang),
            p.coil_pitch * theta,
        ))
    return pts


def _vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vadd(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vscale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _vcross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _vnorm(a):
    m = math.sqrt(_vdot(a, a)) or 1.0
    return _vscale(a, 1.0 / m)


def parallel_transport_frames(
    points: list[tuple[float, float, float]],
) -> list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]]:
    """Build a rotation-minimising frame (T, N, B) along a polyline.

    Returns one (tangent, normal, binormal) triple per point. For a helix
    this avoids the binormal flip the naive Frenet frame would produce when
    curvature is constant.
    """
    n = len(points)
    if n < 2:
        raise ValueError("Need at least 2 points to build frames")

    tangents: list[tuple[float, float, float]] = []
    for i in range(n):
        if i == 0:
            t = _vnorm(_vsub(points[1], points[0]))
        elif i == n - 1:
            t = _vnorm(_vsub(points[-1], points[-2]))
        else:
            t = _vnorm(_vsub(points[i + 1], points[i - 1]))
        tangents.append(t)

    # Initial reference normal — pick any vector not parallel to T0.
    t0 = tangents[0]
    if abs(t0[2]) < 0.9:
        ref = (0.0, 0.0, 1.0)
    else:
        ref = (1.0, 0.0, 0.0)
    n0 = _vnorm(_vcross(_vcross(t0, ref), t0))
    b0 = _vnorm(_vcross(t0, n0))

    frames: list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]] = [
        (t0, n0, b0),
    ]

    for i in range(1, n):
        t_prev, n_prev, _b_prev = frames[-1]
        t_curr = tangents[i]

        # Rotation axis = T_prev × T_curr; angle from their dot product.
        axis = _vcross(t_prev, t_curr)
        sin_phi = math.sqrt(_vdot(axis, axis))
        cos_phi = max(-1.0, min(1.0, _vdot(t_prev, t_curr)))
        if sin_phi < 1e-12:
            n_curr = n_prev
        else:
            axis = _vscale(axis, 1.0 / sin_phi)
            # Rodrigues' rotation of n_prev around `axis` by angle phi.
            phi = math.atan2(sin_phi, cos_phi)
            cph, sph = math.cos(phi), math.sin(phi)
            n_curr = _vadd(
                _vadd(_vscale(n_prev, cph), _vscale(_vcross(axis, n_prev), sph)),
                _vscale(axis, _vdot(axis, n_prev) * (1.0 - cph)),
            )
            n_curr = _vnorm(n_curr)
        b_curr = _vnorm(_vcross(t_curr, n_curr))
        frames.append((t_curr, n_curr, b_curr))

    return frames


# --------------------------------------------------------------------------
# Tube surface — a swept circle along the helix
# --------------------------------------------------------------------------


def tube_ring(
    centre: tuple[float, float, float],
    normal: tuple[float, float, float],
    binormal: tuple[float, float, float],
    radius: float,
    n_circ: int,
) -> list[tuple[float, float, float]]:
    """Return n_circ points on the circle of given radius lying in the plane
    spanned by (normal, binormal) at `centre`."""
    pts: list[tuple[float, float, float]] = []
    for k in range(n_circ):
        ang = 2.0 * math.pi * k / n_circ
        c, s = math.cos(ang), math.sin(ang)
        offset = _vadd(_vscale(normal, radius * c), _vscale(binormal, radius * s))
        pts.append(_vadd(centre, offset))
    return pts


def _tri(p1, p2, p3, normal=None) -> str:
    """One ASCII-STL facet block."""
    if normal is None:
        normal = _vnorm(_vcross(_vsub(p2, p1), _vsub(p3, p1)))
    nx, ny, nz = normal
    return (
        f"  facet normal {nx:.6e} {ny:.6e} {nz:.6e}\n"
        f"    outer loop\n"
        f"      vertex {p1[0]:.6e} {p1[1]:.6e} {p1[2]:.6e}\n"
        f"      vertex {p2[0]:.6e} {p2[1]:.6e} {p2[2]:.6e}\n"
        f"      vertex {p3[0]:.6e} {p3[1]:.6e} {p3[2]:.6e}\n"
        f"    endloop\n"
        f"  endfacet\n"
    )


def build_tube_stl(p: HelicalCoilParams, name: str = "helical_tube") -> str:
    """Return an ASCII STL string for the tube outer surface.

    The tube is the outer wall of the inner pipe — radius = tube_od / 2.
    End caps are NOT emitted (snappyHexMesh sees inlet/outlet patches via
    blockMesh background mesh).
    """
    cl = helix_centreline(p)
    frames = parallel_transport_frames(cl)
    radius = p.tube_od / 2.0
    n_circ = p.n_circumferential

    rings = [
        tube_ring(c, n, b, radius, n_circ)
        for c, (_, n, b) in zip(cl, frames)
    ]

    facets: list[str] = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n_circ):
            kn = (k + 1) % n_circ
            a, b, c, d = r0[k], r0[kn], r1[kn], r1[k]
            facets.append(_tri(a, b, c))
            facets.append(_tri(a, c, d))

    body = "".join(facets)
    return f"solid {name}\n{body}endsolid {name}\n"


# --------------------------------------------------------------------------
# Shell — coaxial outer cylinder enclosing the helix
# --------------------------------------------------------------------------


def build_shell_stl(p: HelicalCoilParams, name: str = "chiller_shell") -> str:
    """Return an ASCII STL of the shell-side outer cylinder.

    The shell is a straight cylinder coaxial with the helix axis (z), with
    radius = coil_radius + tube_od / 2 + shell_clearance. The Wright2010
    Table 3.2 shell-annulus geometry is multi-pass with baffles; this
    placeholder is the single-pass enclosure good enough for snappyHexMesh
    to anchor the outer wall patch.
    """
    cl = helix_centreline(p)
    z_min = min(z for _, _, z in cl) - 0.5 * p.coil_pitch
    z_max = max(z for _, _, z in cl) + 0.5 * p.coil_pitch
    R_shell = p.coil_radius + p.tube_od / 2.0 + p.shell_clearance
    n_circ = max(p.n_circumferential, 32)

    facets: list[str] = []
    for k in range(n_circ):
        a0 = 2.0 * math.pi * k / n_circ
        a1 = 2.0 * math.pi * (k + 1) / n_circ
        p00 = (R_shell * math.cos(a0), R_shell * math.sin(a0), z_min)
        p01 = (R_shell * math.cos(a1), R_shell * math.sin(a1), z_min)
        p10 = (R_shell * math.cos(a0), R_shell * math.sin(a0), z_max)
        p11 = (R_shell * math.cos(a1), R_shell * math.sin(a1), z_max)
        facets.append(_tri(p00, p01, p11))
        facets.append(_tri(p00, p11, p10))

    body = "".join(facets)
    return f"solid {name}\n{body}endsolid {name}\n"


# --------------------------------------------------------------------------
# Diagnostics
# --------------------------------------------------------------------------


def implied_arc_length_mm(p: HelicalCoilParams) -> float:
    """Closed-form helix arc length: N · sqrt((2πR)² + pitch²) (mm)."""
    return p.n_turns * math.sqrt(
        (2.0 * math.pi * p.coil_radius) ** 2 + p.coil_pitch ** 2
    )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("cases/case04_chiller/constant/triSurface"),
        help="Directory to write the two STL files into.",
    )
    p.add_argument("--tube-od", type=float, default=38.1, help="Tube outer diameter (mm)")
    p.add_argument("--tube-wall", type=float, default=2.4, help="Tube wall thickness (mm)")
    p.add_argument("--coil-radius", type=float, default=200.0, help="Helix centreline radius (mm)")
    p.add_argument("--coil-pitch", type=float, default=101.6, help="Axial advance per turn (mm)")
    p.add_argument("--turns", type=float, default=15.0, help="Number of helix turns")
    p.add_argument("--seg-per-turn", type=int, default=64, help="Centreline samples per turn")
    p.add_argument("--n-circ", type=int, default=24, help="Facets around the tube cross-section")
    p.add_argument("--shell-clearance", type=float, default=14.4, help="Shell-annulus clearance (mm)")
    args = p.parse_args(argv)

    params = HelicalCoilParams(
        tube_od=args.tube_od,
        tube_wall=args.tube_wall,
        coil_radius=args.coil_radius,
        coil_pitch=args.coil_pitch,
        n_turns=args.turns,
        n_segments_per_turn=args.seg_per_turn,
        n_circumferential=args.n_circ,
        shell_clearance=args.shell_clearance,
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    tube_path = args.out_dir / "helical_tube.stl"
    shell_path = args.out_dir / "chiller_shell.stl"
    tube_path.write_text(build_tube_stl(params))
    shell_path.write_text(build_shell_stl(params))

    arc_m = implied_arc_length_mm(params) / 1000.0
    print(
        f"Wrote {tube_path} ({params.n_turns} turns, "
        f"R={params.coil_radius} mm, pitch={params.coil_pitch} mm, "
        f"tube OD={params.tube_od} mm, ID={params.tube_id:.2f} mm)"
    )
    print(f"Wrote {shell_path}")
    print(
        f"Implied helix arc length: {arc_m:.3f} m "
        f"(Wright2010 Table 3.2 reports 19.15 m for the SNL gas chiller)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
