<p align="center">
  <img src="docs/assets/logo.png" alt="sCO₂-TMSR-Toolkit" width="240" />
</p>

# sCO₂-TMSR-Toolkit

> ⭐ **If you find this project useful, please star the repo!** It helps the community discover it.

**Open-source full-stack toolkit for supercritical CO₂ Brayton cycles coupled to advanced nuclear reactors (TMSR / HTGR).**

> **Status:** Phase 1 (property tools) complete with tests. Phase 2–3 (CFD runs, Modelica compile-checks) are scaffolded but pending external compute / installation. **This toolkit is not validated for reactor safety analysis.**

[![Tests](https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit/actions/workflows/python-tests.yml/badge.svg)](https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit/actions/workflows/python-tests.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Docs: CC BY-SA 4.0](https://img.shields.io/badge/Docs-CC%20BY--SA%204.0-lightgrey.svg)](LICENSE-DOCS)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![CoolProp](https://img.shields.io/badge/CoolProp-%E2%89%A57.1-orange)](https://github.com/CoolProp/CoolProp)
[![OpenFOAM](https://img.shields.io/badge/OpenFOAM-11-blue)](https://openfoam.org/)
[![OpenModelica](https://img.shields.io/badge/OpenModelica-1.22%2B-green)](https://openmodelica.org/)

---

## What Is This?

sCO₂-TMSR-Toolkit provides an integrated open-source workflow for researchers and engineers building simulation capabilities for advanced nuclear reactor power cycles. It bridges three engineering layers:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        sCO₂-TMSR-Toolkit                                 │
├────────────────┬────────────────────┬────────────────────────────────────┤
│  Layer 1       │  Layer 2           │  Layer 3                           │
│  Properties    │  CFD Benchmarks    │  System Simulation                 │
│                │                    │                                    │
│  CoolProp≥7.1  │  OpenFOAM PCHE     │  OpenModelica component library    │
│  Mixture       │  cases (straight,  │  PCHE / turbomachinery / reactor   │
│  validation    │  zigzag, airfoil)  │  FMU export for co-simulation      │
│  LUT export    │  CFD-ROM surrogate │  ASME compliance check             │
│  Streamlit app │  STEP data CI      │  Tritium permeation (optional)     │
│                │                    │  Online-refueling transient (opt.) │
└────────────────┴────────────────────┴────────────────────────────────────┘
```

**Why this matters:**
- No open-source library currently integrates sCO₂ property diagnostics, PCHE CFD benchmarking, and a Modelica system-simulation library in a single coherent workflow
- PCHE channels operate in regimes where classical Gnielinski correlations have documented significant deviations — the CFD-trained ROM in this toolkit addresses that gap
- TMSR-LF1 (SINAP, 2 MWth) achieved world-first online thorium addition in Oct 2024 — creating a new class of transient disturbances not previously modeled in open tools

---

## Quick Start

```bash
# Install Python dependencies (CoolProp >= 7.1 required)
pip install "CoolProp>=7.1" numpy scipy matplotlib pandas streamlit pytest

# Run the property diagnostic tool
python src/sco2_property_explorer.py

# Launch the interactive Streamlit app
streamlit run app/streamlit_app.py

# Generate a sCO2 look-up table for OpenFOAM
python src/tools/export_lut.py

# Run the test suite
pytest tests/ -v
```

---

## Repository Structure

```
sCO2-TMSR-Toolkit/
├── README.md                    # this file
├── LICENSE
├── pyproject.toml
├── requirements.txt
│
├── src/                         # Phase 1: property tools
│   ├── sco2_property_explorer.py
│   ├── sco2_mixture_validation.py
│   └── tools/
│       └── export_lut.py
│
├── app/                         # Streamlit web application
│   └── streamlit_app.py
│
├── cases/                       # Phase 2: OpenFOAM CFD benchmark cases
│   ├── case01_straight_channel/
│   ├── case02_zigzag_channel/
│   └── case03_airfoil_channel/
│
├── rom/                         # Phase 2: CFD-trained ROM surrogate
│   ├── dataset/
│   ├── train_rom.py
│   └── exported/
│
├── modelica/                    # Phase 3: OpenModelica component library
│   └── AdvancedReactor_sCO2_Library/
│       ├── package.mo
│       ├── Media/                  # sCO2 medium (placeholder, full Medium coupling pending)
│       ├── Components/             # HeatExchangers / Turbomachinery / Reactor / Valves
│       ├── Cycles/                 # SimpleRecuperation / RecompressionCycle / TMSR_sCO2_Full
│       ├── Examples/               # DesignPointAnalysis / LoadFollowing / StartupSequence
│       ├── Tests/                  # ValidationTests (compile smoke test)
│       ├── ExternalROM/            # FMU drop-zone for Phase 2 ROM
│       └── docs/                   # UserGuide.md + ComponentReference.md
│
├── validation/                  # Experimental benchmark data
│   └── experimental_data/
│       ├── SNL_compressor_data.csv         # Wright2010 + Wright2011 SNL rows (gates --check rho)
│       ├── BYU_pilot_data.csv              # Held2025 BYU/Echogen pilot Table 2 (gates --check h)
│       ├── coolprop_self_consistency.csv   # auto-generated self-regression rows
│       ├── Kim2016_PCHE.csv                # PCHE benchmark seed
│       └── data_sources.md
│   └── failure_envelopes/                  # CoolProp HEOS mixture failure maps (Gap 3)
│       ├── co2_he_{1,3,5}pct.{png,csv}
│       ├── co2_h2o_{0p5,1,2}pct.{png,csv}
│       └── regenerate_all.sh
│
├── tests/                       # Automated tests (~100 cases)
│   ├── test_sco2_properties.py
│   ├── test_cycle.py
│   ├── test_failure_envelope.py
│   ├── test_modelica_structure.py
│   ├── test_postprocessing.py
│   ├── test_rom_pipeline.py
│   ├── test_warnings.py
│   └── test_zigzag_cad.py
│
├── book/                        # Jupyter Book living documentation
│
├── .github/
│   └── workflows/
│       ├── python-tests.yml
│       └── build-book.yml
│
└── docs/                        # Engineering documentation (this toolkit's execution manual)
    ├── README.md                # docs navigation
    ├── 00_strategy.md           # strategy, milestones, risks, sustainability
    ├── 01_phase1_properties.md  # Phase 0 + Phase 1 implementation guide
    ├── 02_phase2_cfd_rom.md     # Phase 2 implementation guide
    └── 03_phase3_modelica.md    # Phase 3 implementation guide
```

---

## Documentation

The `docs/` directory contains the full engineering implementation manual, split by phase:

| Document | Scope |
|----------|-------|
| [docs/00_strategy.md](docs/00_strategy.md) | Strategy, version history, milestone timeline (24 months), risk register, community, academic credit |
| [docs/01_phase1_properties.md](docs/01_phase1_properties.md) | Knowledge prep, CoolProp contributions, mixture validation, LUT export, Streamlit app, CI/CD |
| [docs/02_phase2_cfd_rom.md](docs/02_phase2_cfd_rom.md) | PCHE OpenFOAM benchmark cases, large-file strategy, CFD-ROM training, physics-informed loss extension, STEP data integration |
| [docs/03_phase3_modelica.md](docs/03_phase3_modelica.md) | OpenModelica library, FMU export (FMI 2.0 default / FMI 3.0 upgrade path), tritium permeation, ASME check, online-refueling transient module, Jupyter Book |

---

## Roadmap (v1.4)

| Phase | Timeline | Status |
|-------|----------|--------|
| Phase 0 — knowledge preparation | Weeks 0–6 | ✅ scaffolding ready |
| Phase 1 — sCO₂ property tools | Months 1–3 | ✅ tools + tests + Streamlit + Jupyter Book |
| Phase 2 — PCHE CFD benchmarks + ROM | Months 4–8 | 🟡 scaffolded (cases/, rom/, postProcessing/, Git LFS); CFD runs blocked on compute |
| Phase 3 — OpenModelica library | Months 8–18 | 🟡 library skeleton complete (PCHE + ASME, tritium, point-kinetics, cycles, examples, docs); compile-check blocked on OpenModelica install |

### Component status — `modelica/AdvancedReactor_sCO2_Library/`

| Component | Status | Notes |
|-----------|--------|-------|
| `Media/sCO2.mo` | placeholder `BaseProperties` | full CoolProp coupling at month-12 milestone |
| `Components/HeatExchangers/IntermediateHeatExchanger.mo` | ✅ NTU-effectiveness | design-point Cp values |
| `Components/HeatExchangers/PCHE.mo` | ✅ NTU + ROM switch + ASME warning | § 3.3 + § 3.6 |
| `Components/HeatExchangers/TritiumPermeationLayer.mo` | ✅ Sieverts + Arrhenius (steady) | § 3.5 |
| `Components/Turbomachinery/Compressor.mo` | ✅ isentropic-efficiency + BYOD CSV interface | scalar defaults are engineering-typical (η=0.85, ṁ=100 kg/s, PR=2.5), not source-anchored — see docs/known_gaps.md#compressor-maps |
| `Components/Turbomachinery/ReCompressor.mo` | ✅ extends Compressor (η=0.83) | inherits BYOD interface |
| `Components/Turbomachinery/Turbine.mo` | ✅ isentropic-efficiency + symmetric BYOD CSV interface | scalar default η=0.90 |
| `Components/Turbomachinery/LabyrinthSeal.mo` | ✅ Egli leakage correlation | defaults from Wright2010 §5.5 / Table 5.3 |
| `Components/Reactor/MoltenSaltReactor.mo` | ✅ lumped thermal-hydraulic | |
| `Components/Reactor/ReactorPowerControl.mo` | ✅ PI controller | |
| `Components/Reactor/OnlineFuellingTransient.mo` | ✅ point-kinetics, 6-group | § 3.7; default β_i / λ_i are U-235 thermal — replace with Th-U |
| `Components/Valves/{ThrottleValve, BypassValve}.mo` | ✅ isenthalpic | |
| `Cycles/{SimpleRecuperation, RecompressionCycle, TMSR_sCO2_Full}.mo` | ✅ skeleton | |
| `Examples/{DesignPointAnalysis, LoadFollowing, StartupSequence}.mo` | ✅ skeleton | |
| `Tests/ValidationTests.mo` | ✅ instantiates every published component | OpenModelica compile blocked locally |
| `ExternalROM/PCHE_ROM_FMU.fmu` | 🚫 not built | requires CFD dataset + `pythonfmu build` |

### External / blocked items

These items are part of the 24-month plan but cannot be completed in a single
implementation pass — they require external compute, hardware, or third-party
service accounts:

- **Zenodo DOI** — manual deposit per release (`docs/00 § Sustainability`)
- **JOSS submission** — after the v1.0 milestone with quantitative validation
- **OSTI Sandia / BYU pilot benchmark data** — Wright2010 + Wright2011 transcribed
  into `SNL_compressor_data.csv` (gates `--check rho`); Held2025 BYU/Echogen
  pilot transcribed into `BYU_pilot_data.csv` with enthalpy actively gating
  CI (`--check h`). DOE STEP Phase 1 final report still unreleased; see
  `docs/known_gaps.md#snl-step-rows`.
- **Streamlit Cloud deployment** — push `app/streamlit_app.py` after a project
  is created on share.streamlit.io
- **OpenFOAM CFD runs** for `cases/case01..03` — needs an OpenFOAM 11 environment
- **OpenModelica compile-check** — runs in CI (Docker image), not in this dev env

### Test status

```
tests/ — 101 passed, 1 skipped (STEP Phase 1 CSV not yet released)
```

Full milestone timeline with month-by-month checkpoints: [docs/00_strategy.md](docs/00_strategy.md#milestone-timeline)

---

## Contributing

We welcome contributions at any layer. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

Key contribution paths:
- **Property layer:** mixture validation scripts, CoolProp issue reproduction cases
- **CFD layer:** new PCHE geometry benchmark cases, mesh quality improvements
- **Modelica layer:** new components, additional validation test cases
- **Documentation:** notebook improvements, translation corrections

When filing an issue, include: CoolProp version, Python version, and a minimal reproducible example.

---

## License

- **Software / source code:** [Apache License 2.0](LICENSE)
- **Documentation (`docs/`, `book/`, README content):** [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE-DOCS)
- **Attribution notices:** see [NOTICE](NOTICE)

This dual-license layout matches the OpenLithoHub project family.

Data in `validation/experimental_data/` is referenced from published literature
and public DOE / national-laboratory reports. See
[validation/experimental_data/data_sources.md](validation/experimental_data/data_sources.md)
for provenance and citation information.

---

## Citation

If this toolkit contributes to your research, please cite the Zenodo archive:

```bibtex
@software{sco2_tmsr_toolkit,
  title  = {sCO2-TMSR-Toolkit: Open-source toolkit for supercritical CO₂ cycles and advanced reactors},
  author = {[Contributors]},
  year   = {2025},
  url    = {https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit},
  doi    = {10.5281/zenodo.xxxxxxx}
}
```

---

## Acknowledgements

This toolkit builds on the CoolProp, OpenFOAM, and OpenModelica open-source communities.
Experimental validation data sourced from Sandia National Laboratories public OSTI
reports (Wright et al. 2010 SAND2010-0171, Wright et al. 2011 SAND2010-8840), the
BYU/Echogen 1.26 MWth pilot at the San Rafael Energy Research Center (Held et al.
2025, DOE FE award DE-FE0031928), and the DOE STEP demonstration project public
releases.
