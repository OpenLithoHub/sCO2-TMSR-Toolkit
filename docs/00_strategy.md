# Strategy, Milestones & Sustainability

> **Core strategy:** Bypass knowledge fortresses → fill ecosystem vacuums → establish de-facto standards
> **Target horizon:** 24 months (v1.4 increments add approximately 2–4 months to the overall timeline)
> **Intended audience:** Developers with a working knowledge of Python or C++, willing to fill gaps in engineering thermophysics

---

## Sober Corrections

The strategic judgment behind this project is sound, but the tone can be over-optimistic.
Acknowledge these realities upfront:

| Optimistic framing | Ground truth |
|-------------------|--------------|
| "Become the globally most-recognized ID in this niche within 1–2 years" | More realistic: become *one of* the recognized contributors in this sub-field |
| "De-facto standard" | Requires adoption and citation by research institutions — it is not automatic after shipping |
| "All materials scientists will thank you" | The data problem is a genuine bottleneck; the warning in the docs is real — take it seriously |
| "A smooth, obstacle-free path" | Every phase involves tedious debugging, literature reading, and waiting for PR merges |

**Realistic expectation:** This path is viable, but requires sustained effort. It cannot be replicated by simply following the map.

---

## Version History

### v1.4 (current)

Increments over v1.3:

| # | Addition | Problem solved |
|---|----------|---------------|
| 1 | **§ 2.6.3a** — Physics-informed loss extension (optional) | Adds an energy-balance penalty term to the CFD-ROM surrogate; honestly framed as "physics-informed loss", not full PINN |
| 2 | **§ 1.6 / CI update** — STEP project data integration | DOE Phase 1 (500 °C simple cycle) public data as an additional benchmark alongside Sandia SNL; Phase 2 (715 °C RCBC) noted as upcoming |
| 3 | **§ 3.7** — TMSR-LF1 online-refueling transient module | Optional advanced extension based on confirmed milestones: criticality Oct 2023, full power Jun 2024, first online thorium addition Oct 2024, Th-U conversion confirmed Nov 2025 |
| 4 | **Dependency baseline** — CoolProp ≥ 7.1, FMI 3.0 upgrade path | Reflects current ecosystem; FMI 3.0 honest note: mature in Dymola / pythonfmu3, still limited in OpenModelica — keep FMI 2.0 as default |
| 5 | **§ 0.3** — AI-assisted coding guidance | Practical tooling advice for high-value use cases (OpenFOAM dict generation, Modelica equation counting, doc translation) |

> **Important:** All v1.4 increments build on a completed v1.3 mainline. Do not attempt v1.4 additions before the corresponding phase is stable.

### v1.3

| # | Addition | Problem solved |
|---|----------|---------------|
| 1 | **§ 2.6** — CFD-driven ROM / Surrogate Model training pipeline | Gnielinski correlations do not apply to PCHE non-circular channels; train a lightweight neural network on Phase 2 CFD data as a high-fidelity proxy for Phase 3 Modelica |
| 2 | **§ 3.6** — ASME BPVC simplified compliance check | Gives PCHE and other pressure-bearing components a minimum-wall-thickness engineering constraint, making the library credible to industrial users |
| 3 | **Living-documentation system** — Jupyter Book + Binder integration | Streamlit handles "try it"; Jupyter Book handles "readable derivation + one-click reproduction" — complementary |
| 4 | **Academic credit & sustainability** — JOSS, GitHub Sponsors, NumFOCUS, PSF Grant | Turns 24 months of sustained effort into formally indexed academic output and defensible funding/credit |

### v1.2

1. **§ 1.8** — Streamlit web application wrapping local scripts
2. **§ 2.5** — Large-file version control (Git LFS / DVC) and cloud compute strategy
3. **§ 3.5** — Optional "differentiating extension": tritium permeation and mass transport model
4. **Software engineering infrastructure** — GitHub Actions CI/CD automated testing

### v1.1
Technical path expanded into Phase 1 (properties) → Phase 2 (CFD) → Phase 3 (system simulation).

### v1.0
Core strategic framing: bypass knowledge fortresses → fill ecosystem vacuums → establish de-facto standards.

---

## Milestone Timeline

```
Month
│
├─  0  ── Environment setup; begin literature review (Phase 0)
│
├─  1  ── Publish first CoolProp visualization tool (Gist or small repo)
│         Configure GitHub Actions; README shows green passing badge
│
├─  2  ── File first CoolProp Issue (discovered bug or gap)
│
├─  3  ── First CoolProp PR (merge is not required; the process has value)
│         ★ Streamlit web app live at a public URL (§ 1.8)
│         ★ Jupyter Book framework up; first notebook published (v1.3)
│         Begin scaffolding the PCHE-Benchmark repo
│
├─  5  ── Case01 (straight channel) converged; result vs. literature plot uploaded
│         Benchmark data managed via Git LFS / Zenodo (§ 2.5)
│         ★ Zenodo configured; v0.1.0 released → first DOI obtained (v1.3)
│
├─  6  ── Begin accumulating Phase 2 CFD case data (feed ROM training, § 2.6)
│         ★ GitHub Sponsors enabled (v1.3)
│
├─  7  ── Case02 (zigzag channel) complete; repo has first Stars
│         ★ Milestone 1: post a technical report on ResearchGate or arXiv
│
├─  8  ── Begin learning Modelica; PCHE and turbomachinery base components done
│         ★ ROM training pipeline validated; validation-set MAPE report published (§ 2.6, v1.3)
│         ★ Prepare JOSS submission materials (v1.3)
│
├─ 12  ── Simple recuperation cycle complete; reproduces Dostal 2004 efficiency figures
│         ★ JOSS paper enters peer review (v1.3)
│         ★ Milestone 2: contact a university nuclear-engineering group for collaborative validation
│
├─ 14  ── PCHE.mo gains ASME simplified compliance check (§ 3.6, v1.3)
│         ROM-FMU integrated into Modelica library; comparison benchmark published (v1.3)
│         ★ (v1.4) TMSR-LF1 online-refueling transient module: first draft (§ 3.7)
│
├─ 16  ── Recompression cycle complete; TMSR simplified thermal-hydraulic model added
│         (If capacity allows) Start § 3.5 tritium permeation extension
│
├─ 18  ── FMU exported; v1.0 released
│         ★ Milestone 3: submit library for inclusion in OpenModelica official community
│         ★ Apply for NumFOCUS / PSF / NLnet funding (v1.3)
│
└─ 24  ── Iterate on community feedback; aim for first external citation
```

---

## Risk Register

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| CoolProp PR not merged long-term | Medium | Publish as independent PyPI package — still valuable |
| OpenFOAM case results deviate significantly from literature | High | The deviation itself is a finding; document it, discuss publicly |
| OpenFOAM data bursts the repository | High | Strictly apply § 2.5 `.gitignore` + LFS + Zenodo strategy |
| Insufficient local compute stalls progress | High | Use AWS Spot / university HPC / national supercomputer (§ 2.5.2) |
| ROM training sample too small → poor generalization | High (v1.3) | Enforce § 2.6.2 data-size guidelines; do not publish ROM until samples are sufficient; declare accuracy boundaries |
| ASME check misread as "certification" | Medium (v1.3) | Repeat "simplified indicative check only" in docs and code comments |
| JOSS submission rejected | Medium (v1.3) | JOSS rejection rate is low; main risk is long review cycle — keep CI green and docs complete |
| Open-source funding application fails | High (v1.3) | Treat as project-positioning exercise; do not make funding a prerequisite for the mainline |
| Modelica library unused | Medium | Contact potential users early (months 3–4); lower adoption barrier with FMU export |
| Tritium permeation model has inaccurate physical parameters | High | Always state data sources and applicable range; do not overstate precision |
| Insufficient domain knowledge leads to code errors | High | Every component must have literature references; actively invite domain-expert review |
| Cannot sustain 24-month commitment | High | Complete Phase 1 first, then reassess — do not plan 24 months before starting |

---

## Non-Technical Work

### Documentation Standards

Every component must include:
- Equation sources and literature references
- Applicable range (e.g., "Gnielinski valid for Re > 3000")
- Known limitations (e.g., "not applicable to two-phase flow")
- Validation status: *unvalidated* / *compared against literature* / *compared against experimental data*
- (v1.3+) If using ROM or ASME-checked components: training data range / compliance-check disclaimer

### Community Participation

```
Weekly:
  Read new Issues in OpenMC, CoolProp (understand the frontier — no need to answer)

Monthly:
  Post progress updates on sCO₂-related paper author mailing lists / ResearchGate

Quarterly:
  Post a progress thread on GitHub Discussions or the Modelica forum
  Review whether Jupyter Book content needs updating (v1.3+)

Key thresholds:
  50+ Stars  → proactively contact one related research group
  100+ Stars → consider applying for open-source funding (v1.3+)
  Any Issue  → respond within 48 hours (critical for building trust)
```

### Data & Copyright

```
✅ Permitted:
  - NIST WebBook public data
  - Tabulated data from published papers (cite source)
  - IAEA nuclear database (free access agreement)

❌ Not permitted:
  - Full REFPROP source code (commercial)
  - Unpublished experimental data from national labs
  - Raw research-group data without authorization

Grey area (handle carefully):
  - Data points digitized from paper figures
    → Recommended: note "digitized from ref [x]; contact us if this raises concerns"
```

---

## Academic Credit & Sustainability

### Step 1 — Zenodo Permanent Archive & DOI (near-zero cost; mandatory)

1. Register at [zenodo.org](https://zenodo.org) → link GitHub account
2. Enable archiving for the repository in Zenodo's GitHub settings
3. Create a GitHub Release (e.g., `v0.1.0`) → Zenodo auto-archives and assigns a DOI
4. Add the DOI badge to the README

**Why it matters:** Any paper can formally cite a specific version of your software. Required prerequisite for JOSS submission.

### Step 2 — JOSS Submission (target: month 8–12)

[JOSS](https://joss.theoj.org) reviews *software quality* (tests, docs, API design), not scientific novelty.
Acceptance yields a peer-reviewed paper with a DOI indexed by Crossref and Google Scholar.

**Readiness checklist:**
- Open-source license (MIT / BSD / Apache 2.0)
- Visible version control on GitHub
- Automated tests covering core functionality (CI passing badge)
- Complete `README.md` and install / usage guide
- Clear "Statement of Need" explaining what gap the software fills
- Work equivalent to ≥ 3 months of research development (met at end of Phase 1)

**Recommended `paper.md` title:**
```
sCO2-TMSR-Toolkit: An Open Toolkit for Supercritical CO₂ Property
Diagnostics, PCHE CFD Benchmarking, and Advanced-Reactor System Simulation
```

### Step 3 — GitHub Sponsors (enable at ~month 6)

Configure `.github/FUNDING.yml`:
```yaml
github: [your-username]
ko_fi: your-username
open_collective: sco2-tmsr-toolkit
```

**Realistic expectation:** Revenue will be minimal. Value lies in signaling long-term maintainer commitment and enabling institutional supporters to contribute formally.

### Step 4 — Open-Source Funding (target: month 12–18)

Applicable after: 100+ Stars, at least one external project citing yours, JOSS paper published.

| Fund | Fit | Difficulty |
|------|-----|-----------|
| NumFOCUS Affiliate | Scientific Python ecosystem | Medium |
| PSF Grants | Small development tasks | Medium |
| NLnet Foundation | Open digital public goods (EU focus) | Medium–High |
| Sovereign Tech Fund | Critical open infrastructure | High |

**Grant proposal skeleton (universal):**
```
1. Project Background      — what problem you solve and why it matters
2. Existing Gap            — specific deficiencies of current tools
3. Concrete Deliverables   — what you ship in 3–6 months
4. Timeline & Milestones   — per-month or per-quarter checkpoints
5. Budget Justification    — cloud compute, literature, conference travel
6. Sustainability Plan     — how the project continues after funding ends
7. Community Evidence      — Stars, forks, testimonials from users
```

**Sober expectation:** Most applications fail — that is normal. The application process itself forces clarity on project positioning; that value persists regardless of outcome.

---

*Document version: v1.4 | Recommended review cadence: every 3 months*

*Core references: CoolProp GitHub, OpenMC docs, Dostal 2004 MIT thesis, OpenModelica user manual, Sandia SNL sCO₂ test reports (OSTI public), ASME BPVC Section VIII Div.1, JOSS submission guide, Zenodo docs, STEP project DOE reports, TMSR-LF1 SINAP announcements (2023–2025)*
