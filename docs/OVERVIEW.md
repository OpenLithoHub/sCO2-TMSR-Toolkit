# sCO₂-TMSR-Toolkit — Documentation

> **Project goal:** A full-stack open-source toolkit for supercritical CO₂ Brayton cycles coupled to advanced nuclear reactors (TMSR / HTGR).
> Covers three engineering layers: thermophysical properties → CFD benchmarking → system-level Modelica simulation.

---

## Document Map

| File | Scope | Read when… |
|------|-------|------------|
| [00_strategy.md](00_strategy.md) | Strategy, version history, milestone timeline, risks, community, academic credit | First visit; deciding whether to contribute |
| [01_phase1_properties.md](01_phase1_properties.md) | Phase 0 (prep) + Phase 1: sCO₂ property tools, CoolProp contributions, Streamlit app, CI/CD | Working on months 1–3 |
| [02_phase2_cfd_rom.md](02_phase2_cfd_rom.md) | Phase 2: PCHE OpenFOAM benchmark cases, large-file strategy, CFD-ROM surrogate, STEP data | Working on months 4–8 |
| [03_phase3_modelica.md](03_phase3_modelica.md) | Phase 3: OpenModelica component library, FMU export, tritium permeation, ASME check, online-refueling transient module, Jupyter Book | Working on months 8–18 |

---

## Quick Navigation

- **First visit** → read the "Sober corrections" and milestone timeline in [00_strategy.md](00_strategy.md)
- **Want to start coding now** → jump to "Minimum viable starting point" in [01_phase1_properties.md](01_phase1_properties.md)
- **Looking for code structure** → every phase document contains a complete repo directory tree and runnable code snippets

---

## Current Version: v1.4

Built on v1.3. New in v1.4:

1. **Physics-informed loss extension** (optional) — energy-balance penalty term for the CFD-ROM surrogate (§ 2.6.3a)
2. **STEP project data integration** — DOE Phase 1 (500 °C simple cycle) public data as an additional validation source (§ 1.6, CI)
3. **TMSR-LF1 online-refueling transient module** — based on confirmed 2023–2025 milestones; optional advanced extension (§ 3.7)
4. **Dependency baseline update** — CoolProp ≥ 7.1; FMI 3.0 explained as an optional upgrade path (§ 2.6.4, § 3.4)
5. **AI-assisted coding guidance** — practical tooling advice added to Phase 0 (§ 0.3)

> Full version history: [00_strategy.md § Version History](00_strategy.md#version-history)
