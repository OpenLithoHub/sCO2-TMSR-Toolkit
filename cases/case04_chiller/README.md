# Case 04 — Engineering-Scale Gas Chiller (Wright2010 Table 3.2)

> **Reference:** docs/02_phase2_cfd_rom.md § 2.5 (large-file strategy) +
> docs/known_gaps.md#pche-geometry +
> docs/data_extracts/wright2010_sand2010-0171.md "Table 3.2 (p.30) — gas chiller PCHE-like geometry".
>
> **Why this case matters:** case01–03 use idealized *micro-channel* PCHE
> geometries from highly-cited academic papers (Ngo, Kim) — sub-millimetre
> hydraulic diameters typical of diffusion-bonded plate exchangers. The
> SNL 10 MWe test-loop gas chiller is a different beast: a 19.15 m helical
> tube-and-shell coil at engineering scale (Confidence A). Adding it as a
> fourth benchmark gives the ROM training set a coarse-channel anchor
> point and lets the pipeline accept a real-engineering geometry alongside
> the academic placeholders.

## Geometry (Wright2010 SAND2010-0171 Table 3.2, p.30)

| Quantity | Value | Note |
|---|---|---|
| Tube outer diameter | 38.1 mm | from Table 3.2 |
| Tube wall thickness | 2.4 mm | from Table 3.2 |
| Tube inner diameter | 33.3 mm | derived: OD − 2·wall |
| Single-coil length | 19.15 m | from Table 3.2 |
| Coil pitch | 101.6 mm | from Table 3.2 |
| Gas-side HT area | 4.00 m² | from Table 3.2 |
| Liquid-side HT area | 4.58 m² | from Table 3.2 |
| Gas hydraulic diameter | 3.33 mm | from Table 3.2 |
| Liquid hydraulic diameter | 14.4 mm | from Table 3.2 |

## Differences from case01–03

| Aspect | case01 (straight micro) | case02 (zigzag) | case03 (airfoil) | **case04 (chiller)** |
|---|---|---|---|---|
| Geometry source | academic (idealized) | academic (idealized) | academic (idealized) | **Sandia 10 MWe loop, real engineering** |
| Hydraulic diameter | ~2 mm | ~2 mm | ~2 mm | **3.33 mm gas / 14.4 mm liquid** |
| Length | 50 mm | wavelength × N | wavelength × N | **19.15 m (single coil)** |
| Geometry kind | Cartesian | Cartesian + zigzag STL | Airfoil cascade STL | **Helical coil + shell** |
| Confidence of geometry | C (placeholder) | C (placeholder) | C (placeholder) | **A (Wright2010 Table 3.2)** |

## Status

✅ **Multi-region (chtMultiRegionFoam) pipeline scaffolded.** Built on the
production-grade helical-coil mesh: STL generator
(`src/tools/cad/helical_coil.py`) emits `helical_tube.stl` + `chiller_shell.stl`
from the Wright2010 Table 3.2 defaults; `system/surfaceFeatureExtractDict`
extracts feature edges (tube end caps + shell rims) into `.eMesh` files;
`system/blockMeshDict` is the background Cartesian mesh enclosing both STLs
and exposes `liquid_inlet` / `liquid_outlet` / `background_sides` patches;
`system/snappyHexMeshDict` cuts the tube and shell walls at production
levels (3 4)/(2 3), references the feature edges, grows surface layers on
the tube wall (5 layers, expansion 1.2), **and tags the tube interior as
the `gas_zone` cellZone with the tube/shell interface as the `tube_wall`
faceZone** (refinementSurfaces.tube_wall.{cellZone, faceZone, cellZoneInside};
`locationsInMesh` lists the per-region insidePoints).

`Allrun` now runs the full multi-region chain: STL → surfaceFeatureExtract
→ blockMesh → snappyHexMesh → **splitMeshRegions -cellZones -overwrite** →
per-region checkMesh → **chtMultiRegionFoam**. Per-region directories are
populated:

```
0/{gas,liquid}/{T,p,p_rgh,U,k,omega,nut,alphat}
constant/{gas,liquid}/{thermophysicalProperties,turbulenceProperties,g}
system/controlDict                      # global time controls + functions
system/{gas,liquid}/{fvSchemes,fvSolution}
constant/regionProperties               # `fluid (gas liquid)` topology
```

Boundary conditions on `tube_wall_gas` / `tube_wall_liquid` use
`compressible::turbulentTemperatureCoupledBaffleMixed` (regionCoupling), so
heat is transferred across the tube wall by region-to-region thermal
matching rather than by meshing the wall as a thin solid.

**Validation status:** dictionary-only — none of the steps above have been
exercised in an OpenFOAM environment. The next checkpoint is to run
`Allrun` on a workstation with OpenFOAM ≥ v2012 / OpenFOAM 11 and
confirm that splitMeshRegions yields two non-empty regions and
chtMultiRegionFoam reaches the first time step. Smoke-test refinement
fallback via `CASE04_SMOKE_TEST=1` is wired in `Allrun`.

The intent of staging this case is to:

1. Reserve the case slot so geometry parameters live in version control
   beside their primary source (Wright2010 Table 3.2, Confidence A).
2. Give the ROM training pipeline (rom/dataset/extract_from_cfd.py) an
   engineering-scale anchor row alongside the academic micro channels.
3. Make the gap between *academic placeholder* and *engineering-scale
   real geometry* visible — which is exactly the framing of
   docs/00_strategy.md § Black Hole 2.

## What still needs doing

- [x] Helical-coil CAD generator (analogous to `src/tools/cad/zigzag.py`)
      emitting the gas-tube outer surface and shell inner surface,
      parameterised by tube ID, coil pitch, and number of turns. See
      `src/tools/cad/helical_coil.py` (tests in
      `tests/test_helical_coil_cad.py`).
- [x] Switch `system/` over to `snappyHexMesh` on the generated STL.
- [x] Production-grade refinement: tube_wall (3 4) with 5 surface layers,
      shell_wall (2 3) with 2 surface layers, feature-edge file via
      `surfaceFeatureExtract` so the tube/shell intersection edges are
      captured. See `system/snappyHexMeshDict` +
      `system/surfaceFeatureExtractDict`.
- [x] Rename background patches to reflect that the meshed domain is
      shell-side (liquid) only until the tube interior becomes a separate
      region: `liquid_inlet` / `liquid_outlet` / `background_sides`.
- [x] Multi-region split (chtMultiRegionFoam): the tube interior is now
      meshed as the `gas` region (cellZone tagged in
      `system/snappyHexMeshDict` refinementSurfaces.tube_wall.cellZone =
      `gas_zone`, cellZoneInside `inside`) and the shell annulus as
      `liquid`. The tube/shell interface is exposed as a `tube_wall`
      faceZone and split into `tube_wall_gas` / `tube_wall_liquid`
      regionCoupling patches by `splitMeshRegions -cellZones`. Boundary
      conditions on those patches use
      `compressible::turbulentTemperatureCoupledBaffleMixed`. The pipeline
      now calls `chtMultiRegionFoam`. Per-region directories
      (`0/{gas,liquid}/`, `constant/{gas,liquid}/`,
      `system/{gas,liquid}/`) are populated with k-ω SST schemes
      mirroring case01. **Not yet validated in an OpenFOAM environment**
      — dictionaries are written from the OpenFOAM tutorial template
      (heatTransfer/chtMultiRegionFoam/multiRegionHeater) but the only
      check so far is that the dict files parse on this machine. First
      OpenFOAM run is the next deliverable.
- [ ] Calibrate `coil_radius` against the Wright2010 single-coil length
      (19.15 m). Default R=200 mm gives ~18.9 m arc; sweep R or N to
      match exactly if needed (see CLI `--coil-radius` / `--turns`).

## Geometry reference

See `docs/data_extracts/wright2010_sand2010-0171.md`, "Table 3.2 (p.30)
— gas chiller PCHE-like geometry" — which in turn cites
[`Wright2010_SAND2010_0171`, Table 3.2, p.30] verbatim.
