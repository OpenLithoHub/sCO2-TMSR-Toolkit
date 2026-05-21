# AdvancedReactor_sCO2_Library — User Guide

> **Reference:** docs/03_phase3_modelica.md § 3.2 (architecture) and § 3.8 (CI/docs).

## What is this library?

A modular OpenModelica library for simulating supercritical-CO₂ Brayton power
cycles coupled to advanced nuclear reactors (TMSR — thorium molten-salt reactor;
HTGR — high-temperature gas-cooled reactor).

The library provides equation-based components that compose into full plant
models suitable for design-point analysis, load-following studies, and
transient response (including the v1.4 extension for TMSR-LF1 online-refueling
reactivity perturbations).

## Quick start

### 1. Load the library

```modelica
// In OMShell:
loadFile("modelica/AdvancedReactor_sCO2_Library/package.mo");
```

The Modelica package name uses underscores (`AdvancedReactor_sCO2_Library`)
because Modelica identifiers cannot contain hyphens. The repository / project
name remains `AdvancedReactor-sCO2-Library` for human-readable use.

### 2. Run the validation suite

```modelica
simulate(AdvancedReactor_sCO2_Library.Tests.ValidationTests, stopTime = 1);
```

This compiles every published component as a smoke test. The CI workflow
(docs/03 § 3.8) runs the same check inside an OpenModelica Docker image:

```bash
docker run --rm -v $PWD:/lib openmodelica/openmodelica:v1.22.0-minimal \
    omc /lib/Tests/ValidationTests.mo
```

### 3. Run an example

```modelica
simulate(AdvancedReactor_sCO2_Library.Examples.LoadFollowing,
         stopTime = 3600, tolerance = 1e-5);
plot({plant.cycle.efficiency, plant.reactor.power_fraction});
```

## Examples (`Examples/`)

| Example                   | Scenario                                           | StopTime |
| ------------------------- | -------------------------------------------------- | -------- |
| `DesignPointAnalysis`     | Steady-state nominal-load efficiency check         | 1 s      |
| `LoadFollowing`           | 100 % → 50 % → 100 % power ramp; cycle response    | 3 600 s  |
| `StartupSequence`         | Cold-start sequence (placeholder, future work)     | 7 200 s  |

## ROM bridge (`ExternalROM/`)

`Components/HeatExchangers/PCHE.mo` exposes a `useROM` Boolean. When `true`,
Phase 2's CFD-driven ROM is loaded as an FMU from the `ExternalROM/` directory.

Build the FMU with:

```bash
cd rom/exported
pythonfmu build -f wrap_as_fmu.py
mv PCHE_ROM_FMU.fmu ../../modelica/AdvancedReactor_sCO2_Library/ExternalROM/
```

Then in OMShell:

```modelica
parameter Boolean useROM = true;
```

## Limitations & disclaimers

- **`PCHE.mo` ASME check** — order-of-magnitude sanity check only, not
  engineering certification (see § 3.6).
- **`TritiumPermeationLayer.mo`** — steady-state Sieverts + Arrhenius;
  surface kinetics, transient wall storage, and TPB coatings are not modeled.
- **`OnlineFuellingTransient.mo`** — point-kinetics with default U-235 thermal
  precursor data; replace with Th-U values before quantitative claims.
- **`Media/sCO2.mo`** — placeholder `BaseProperties`; full CoolProp-backed
  Medium coupling lands in the Phase 3 month-12 milestone.

## File layout

```
AdvancedReactor_sCO2_Library/
├── package.mo
├── Media/sCO2.mo
├── Components/
│   ├── HeatExchangers/         (IntermediateHeatExchanger, PCHE, TritiumPermeationLayer)
│   ├── Turbomachinery/         (Compressor, ReCompressor, Turbine)
│   ├── Reactor/                (MoltenSaltReactor, ReactorPowerControl, OnlineFuellingTransient)
│   └── Valves/                 (ThrottleValve, BypassValve)
├── Cycles/                     (SimpleRecuperation, RecompressionCycle, TMSR_sCO2_Full)
├── Examples/                   (DesignPointAnalysis, LoadFollowing, StartupSequence)
├── Tests/                      (ValidationTests)
├── ExternalROM/                (PCHE_ROM_FMU.fmu — drop-zone, see ROM bridge)
└── docs/                       (this file + ComponentReference.md)
```

## See also

- [`ComponentReference.md`](ComponentReference.md) — per-component parameter/equation reference.
- `docs/03_phase3_modelica.md` (project docs, repo root) — phase 3 plan and rationale.
- `docs/02_phase2_cfd_rom.md` — ROM training pipeline that produces the PCHE FMU.
