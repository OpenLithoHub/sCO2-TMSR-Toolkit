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

✅ **Helical-coil pipeline at production-grade refinement.** STL generator
(`src/tools/cad/helical_coil.py`) emits `helical_tube.stl` + `chiller_shell.stl`
from the Wright2010 Table 3.2 defaults; `system/surfaceFeatureExtractDict`
extracts feature edges (tube end caps + shell rims) into `.eMesh` files;
`system/blockMeshDict` is the background Cartesian mesh enclosing both STLs
and exposes `liquid_inlet` / `liquid_outlet` / `background_sides` patches
(named for the shell-side flow domain — see "What still needs doing" for
the gas-side multi-region split); `system/snappyHexMeshDict` cuts the tube
and shell walls at production levels (3 4)/(2 3), references the feature
edges, and grows surface layers on the tube wall (5 layers, expansion 1.2).
`Allrun` runs the full chain (STL → surfaceFeatureExtract → blockMesh →
snappyHexMesh → checkMesh → buoyantPimpleFoam).

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
- [ ] Multi-region split (chtMultiRegionFoam): mesh the tube interior as a
      separate `gas` region and the shell annulus as `liquid`, with a
      `tube_wall` faceZone coupling them via solid heat conduction. Today
      `tube_wall` is exposed as a single wall patch and the gas-side flow
      domain is not yet meshed. The post-processing for convective heat
      transfer extraction blocks on this split.
      *Scaffold present:* `constant/regionProperties` declares the target
      `(gas liquid)` fluid-region topology. **Not consumed by the live
      Allrun yet** — the pipeline still calls `buoyantPimpleFoam` on the
      single-region shell-side mesh. Promoting to chtMultiRegionFoam needs:
      (a) `system/snappyHexMeshDict` to tag the tube interior as a cellZone
      (add a `refinementRegions { tube_wall { mode inside; } }` block);
      (b) an `Allrun` step running `splitMeshRegions -cellZones -overwrite`
      after snappyHexMesh; (c) per-region `system/{gas,liquid}/fvSchemes`,
      `fvSolution`, and `0/{gas,liquid}/` field initial conditions; (d)
      switch the solver call to `chtMultiRegionFoam`. Each step needs an
      OpenFOAM environment to validate.
- [ ] Calibrate `coil_radius` against the Wright2010 single-coil length
      (19.15 m). Default R=200 mm gives ~18.9 m arc; sweep R or N to
      match exactly if needed (see CLI `--coil-radius` / `--turns`).

## Geometry reference

See `docs/data_extracts/wright2010_sand2010-0171.md`, "Table 3.2 (p.30)
— gas chiller PCHE-like geometry" — which in turn cites
[`Wright2010_SAND2010_0171`, Table 3.2, p.30] verbatim.
