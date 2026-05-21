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

Place a `constant/triSurface/zigzag_channel.stl` produced from the geometry
script under `tools/cad/zigzag.py` (script not yet written — Phase 2 month 5
deliverable). Until that exists, this case directory is a placeholder.

## Run

```bash
./Allrun
```

`Allrun` is symlink-compatible with case01 — it just calls
`blockMesh` → `snappyHexMesh` → `checkMesh` → `buoyantPimpleFoam` once the
STL is in place.

## Status

🚧 **Skeleton — STL geometry not committed.** STL will be hosted on Zenodo
per `docs/02 § 2.5.1` (LFS quota strategy); the case directory will pull it
via a download script.
