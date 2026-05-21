# Case 01 — Straight Channel (PCHE Baseline)

> **Reference:** docs/02_phase2_cfd_rom.md § 2.4
>
> **Goal:** Establish a converged baseline for sCO₂ flow through a single
> straight semi-circular PCHE channel. Validates against published correlations
> (Gnielinski + smooth-tube friction factor) before moving to zigzag / airfoil
> geometries where these correlations break down.

## Geometry

- Equivalent diameter: 2 mm (semi-circular cross-section approximated as rectangular)
- Length: 50 mm
- Reynolds-number range targeted: 1 000 – 30 000

## Run

```bash
./Allrun
# or step-by-step:
blockMesh
checkMesh
buoyantPimpleFoam   # or rhoPimpleFoam if buoyancy is unimportant
```

## Post-processing

```bash
postProcess -func 'wallHeatFlux' -latestTime
python3 ../../postProcessing/plot_Nu_vs_Re.py
```

## Status

🚧 **Skeleton.** dict files contain placeholder values matching the dimensions
in docs § 2.4 but have not been used to produce a converged solution yet.
Once a real run lands, append a "Convergence record" section with mesh stats,
residuals, and Nu / dp comparison vs. literature.

## Reproducibility

| Hardware | Wall-time estimate |
|----------|--------------------|
| 8-core CPU / 16 GB RAM | ~2 hours |

Time-step output directories are excluded by the repo `.gitignore`.
Benchmark fields (`*.vtu`) belong on Zenodo, not in the git tree.
