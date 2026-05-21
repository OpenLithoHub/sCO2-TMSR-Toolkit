<p align="center">
  <img src="docs/assets/logo.png" alt="sCO₂-TMSR-Toolkit" width="240" />
</p>

# sCO₂-TMSR-Toolkit

> ⭐ **If you find this project useful, please star the repo!** It helps the community discover it.

**Open-source full-stack toolkit for supercritical CO₂ Brayton cycles coupled to advanced nuclear reactors (TMSR / HTGR).**

[![Tests](https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit/actions/workflows/python-tests.yml/badge.svg)](https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
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
│   └── AdvancedReactor-sCO2-Library/
│       ├── package.mo
│       ├── Components/
│       ├── Cycles/
│       └── Tests/
│
├── validation/                  # Experimental benchmark data
│   └── experimental_data/
│       ├── SNL_compressor_data.csv
│       └── data_sources.md
│
├── tests/                       # Automated tests
│   └── test_sco2_properties.py
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
| Phase 0 — knowledge preparation | Weeks 0–6 | 🔲 |
| Phase 1 — sCO₂ property tools | Months 1–3 | 🔲 |
| Phase 2 — PCHE CFD benchmarks + ROM | Months 4–8 | 🔲 |
| Phase 3 — OpenModelica library | Months 8–18 | 🔲 |

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

MIT License. See [LICENSE](LICENSE) for details.

Data in `validation/experimental_data/` is sourced from published literature and public DOE reports.
See `validation/experimental_data/data_sources.md` for provenance and copyright information.

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
Experimental validation data sourced from Sandia National Laboratories public OSTI reports
and the DOE STEP demonstration project public releases.
