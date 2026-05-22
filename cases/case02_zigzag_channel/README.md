# Case 02 — Zigzag Channel

> **Reference:** docs/02_phase2_cfd_rom.md § 2.2 + Phase 2 milestone month 7.
>
> **Why this case matters:** zigzag channels are the *production* PCHE
> geometry — the Gnielinski correlation does not apply, and CFD becomes
> the credible source for Nu / Δp predictions. Re-using the case01 baseline,
> we override only the geometry and the inlet conditions sweep.

## Differences from case01

| Aspect | case01 (straight) | case02 (zigzag) |
|--------|------------------|-----------------|
| Geometry | Straight 50 mm channel | Periodic zigzag with 80° bend angle, 7 mm pitch |
| Mesh | Hex blocks | snappyHexMesh on STL of one zigzag wavelength |
| Hardware (RANS) | 8-core / 16 GB | 16-core / 32 GB |
| Wall-time | ~2 h | ~8 h |

## Mesh source

Generate `constant/triSurface/zigzag_channel.stl` with the bundled geometry
script:

```bash
python -m src.tools.cad.zigzag                  # writes to this case's triSurface/
```

The script emits ASCII STL of the four channel walls (top, bottom, ±z sides)
swept along a triangular-wave centreline. See `src/tools/cad/zigzag.py` for
parameter knobs (length, period, amplitude, channel cross-section).

## Run

```bash
./Allrun
```

`Allrun` is symlink-compatible with case01 — it just calls
`blockMesh` → `snappyHexMesh` → `checkMesh` → `buoyantPimpleFoam` once the
STL is in place.

## Status

🚧 **Skeleton — STL is regenerable but coarse, initial fields are case01-derived.** The bundled `zigzag.py`
emits a plumbing-quality STL good for smoke-testing the snappy + buoyantPimpleFoam
chain. Production runs should regenerate from the upstream PCHE geometry source
(or pull a vetted STL from Zenodo per `docs/02 § 2.5.1`).

The `0/` initial-field set was carried over from case01 with patch names
remapped to case02's blockMesh + snappy patches (`inlet`, `outlet`, `sides`,
`zigzag_wall`). Internal field values (308.15 K, 8 MPa, 1 m/s) are
placeholders for the smoke test; real Re-sweep runs override them per
`Allrun` parameter overrides.
