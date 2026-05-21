"""Generate a zigzag PCHE channel STL for case02_zigzag_channel.

Reference: docs/02_phase2_cfd_rom.md § 2.5.2 + cases/case02_zigzag_channel/README.md.

Why this exists
---------------
The case02 OpenFOAM setup expects `constant/triSurface/zigzag_channel.stl`
to be cut out of a background hex mesh by snappyHexMesh. We deliberately
keep the geometry generation in plain Python (no FreeCAD / CadQuery / Salome)
so the CI can regenerate the STL on a vanilla machine.

The output is an ASCII STL of the *channel walls*, not the fluid volume —
snappyHexMesh treats the surface as the wall patch (`zigzag_wall`).

Geometry
--------
A single PCHE micro-channel that follows a triangular-wave centreline:

    period (mm) ───────►
        ╱╲    ╱╲    ╱╲
       ╱  ╲  ╱  ╲  ╱  ╲
      ╱    ╲╱    ╲╱    ╲   ← centreline (this script discretises it)
              channel half-height = h/2

We sweep a rectangular cross-section (width=channel_width, height=channel_height)
along this centreline and emit two planar walls (top + bottom) plus two
sidewalls. End caps are omitted so snappyHexMesh's inlet/outlet patches see
through-flow.

This is a coarse model — good enough for plumbing / smoke tests. Production
runs should regenerate from the upstream PCHE geometry source.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ZigzagParams:
    """All units mm; matches blockMeshDict scale=0.001 convention."""

    length: float = 14.0          # one full wavelength (set blockMesh accordingly)
    period: float = 7.0           # one zigzag tooth = one half-wavelength
    amplitude: float = 1.0        # peak-to-mean offset of centreline (mm)
    channel_width: float = 1.5    # spanwise (z) extent
    channel_height: float = 1.5   # wall-normal (y) extent
    n_segments_per_period: int = 24  # discretisation of the triangular wave


def centreline(params: ZigzagParams) -> list[tuple[float, float]]:
    """Return (x, y) points along the triangular centreline.

    y oscillates as a triangular wave of amplitude `amplitude` and period
    `period`. We discretise so each half-period gets ~half of
    n_segments_per_period samples; the corners are sharp by design (matches
    the triangular wave; snappyHexMesh's resolveFeatureAngle will round them
    inside the cell-cut step).
    """
    pts: list[tuple[float, float]] = []
    n_periods = max(1, int(round(params.length / params.period)))
    n_total = n_periods * params.n_segments_per_period
    for i in range(n_total + 1):
        t = i / n_total                              # 0..1 along channel
        x = t * params.length
        # triangular wave on [0, period]
        phase = (x / params.period) % 1.0
        y = params.amplitude * (1.0 - 4.0 * abs(phase - 0.5))
        pts.append((x, y))
    return pts


def _tri(p1, p2, p3, normal=(0.0, 0.0, 1.0)) -> str:
    """One ASCII-STL facet block."""
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


def _norm3(a, b, c) -> tuple[float, float, float]:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    m = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / m, ny / m, nz / m


def build_stl(params: ZigzagParams, name: str = "zigzag_wall") -> str:
    """Return an ASCII STL string for the four channel walls."""
    cl = centreline(params)
    h = params.channel_height / 2.0
    w = params.channel_width / 2.0

    facets: list[str] = []

    # For each centreline segment build a hex prism slab (width × height) and
    # emit its 4 lateral faces (2 triangles each = 8 facets per segment).
    for (x0, yc0), (x1, yc1) in zip(cl, cl[1:]):
        # 8 vertices of the segment slab
        # bottom face (y = yc - h), top face (y = yc + h); span ±w in z
        v = {
            "BL0": (x0, yc0 - h, -w), "BR0": (x0, yc0 - h,  w),
            "TL0": (x0, yc0 + h, -w), "TR0": (x0, yc0 + h,  w),
            "BL1": (x1, yc1 - h, -w), "BR1": (x1, yc1 - h,  w),
            "TL1": (x1, yc1 + h, -w), "TR1": (x1, yc1 + h,  w),
        }

        # bottom wall (y = yc - h)
        for a, b, c in [("BL0","BR0","BR1"), ("BL0","BR1","BL1")]:
            facets.append(_tri(v[a], v[b], v[c], _norm3(v[a], v[b], v[c])))
        # top wall
        for a, b, c in [("TL0","TR1","TR0"), ("TL0","TL1","TR1")]:
            facets.append(_tri(v[a], v[b], v[c], _norm3(v[a], v[b], v[c])))
        # -z side (left)
        for a, b, c in [("BL0","TL1","TL0"), ("BL0","BL1","TL1")]:
            facets.append(_tri(v[a], v[b], v[c], _norm3(v[a], v[b], v[c])))
        # +z side (right)
        for a, b, c in [("BR0","TR0","TR1"), ("BR0","TR1","BR1")]:
            facets.append(_tri(v[a], v[b], v[c], _norm3(v[a], v[b], v[c])))

    body = "".join(facets)
    return f"solid {name}\n{body}endsolid {name}\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--out",
        type=Path,
        default=Path("cases/case02_zigzag_channel/constant/triSurface/zigzag_channel.stl"),
        help="Output STL path (relative paths resolve against CWD).",
    )
    p.add_argument("--length", type=float, default=14.0, help="Channel length (mm)")
    p.add_argument("--period", type=float, default=7.0, help="Zigzag period (mm)")
    p.add_argument("--amplitude", type=float, default=1.0, help="Zigzag amplitude (mm)")
    p.add_argument("--width", type=float, default=1.5, help="Channel width / spanwise (mm)")
    p.add_argument("--height", type=float, default=1.5, help="Channel height / wall-normal (mm)")
    p.add_argument("--segments", type=int, default=24, help="Segments per period")
    args = p.parse_args(argv)

    params = ZigzagParams(
        length=args.length,
        period=args.period,
        amplitude=args.amplitude,
        channel_width=args.width,
        channel_height=args.height,
        n_segments_per_period=args.segments,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build_stl(params))
    print(f"Wrote {args.out} (length={params.length} mm, period={params.period} mm)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
