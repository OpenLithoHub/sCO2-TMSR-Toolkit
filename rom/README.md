# PCHE CFD-Driven Reduced-Order Model (ROM)

> **Reference:** docs/02_phase2_cfd_rom.md § 2.6
>
> **Purpose:** Replace the Gnielinski correlation in the Phase 3 Modelica
> library with a fast surrogate trained on Phase 2 OpenFOAM CFD results.
> The surrogate is exported as ONNX + a FMI 2.0 FMU so the same model can
> be embedded into OpenModelica, Dymola, or any FMI-compliant simulator.

## Pipeline

```
cases/case0X_*/  (CFD outputs)
        │
        ▼  rom/dataset/extract_from_cfd.py
training_set.csv
        │
        ▼  rom/train_rom.py
pche_rom.onnx + scalers.npz
        │
        ▼  rom/exported/wrap_as_fmu.py
PCHE_ROM_FMU.fmu  →  modelica/AdvancedReactor_sCO2_Library/ExternalROM/
```

## Status

🚧 **Skeletons in place.** Real CFD training data is not yet committed
(see Phase 2 milestone month 6 — at least 200 converged samples required
before publishing a ROM). Until then, the scripts run end-to-end on
synthetic data so the pipeline can be exercised without OpenFOAM.

## Coverage declaration (mandatory before publishing)

| Dimension | Training-data coverage | Out-of-range behaviour |
|-----------|------------------------|------------------------|
| `T_in` (K) | 305–823 (planned) | hard clamp + warning |
| `P_in` (Pa) | 7.5e6–25e6 (planned) | hard clamp + warning |
| `mass_flow` (kg/s) | 0.05–0.5 (planned) | hard clamp + warning |
| Geometry | straight, zigzag, airfoil | discrete — cannot interpolate |

> **Honest boundary:** ROM accuracy is bounded by training-data coverage.
> A ROM is not a universal replacement — it packages "the operating space
> already computed by CFD" into a fast callable.
