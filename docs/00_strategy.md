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

## Data Black Holes — Survival Strategy

> **Mindset shift (read this first):** This project ships a **framework and pipeline**, not **ground-truth data**.
> The most decision-relevant numbers in advanced reactors and sCO₂ thermal hydraulics — commercial compressor maps, real-plant corrosion rates, Heatric's actual PCHE etching geometry — are commercial secrets or national-lab restricted. Waiting to collect "complete" data before shipping guarantees the project never ships.
> Industrial users typically have the data; what they lack is a system-level framework that can ingest it. Build the framework with documented placeholders, expose clean ingestion interfaces, and the data will follow from the institutions that hold it.

> **Citation discipline:** Every external number cited or transcribed in this repo follows [`docs/citation_protocol.md`](citation_protocol.md). The bibliographic single-source-of-truth is [`docs/references.bib`](references.bib); per-source extract notes live under [`docs/data_extracts/`](data_extracts/).

Four predictable "data black holes" will be hit during execution. Each has a known escape strategy.

### Black Hole 1 — sCO₂ compressor / turbine performance maps (Phase 3)

- **Where it bites:** Modelica turbomachinery components require multidimensional flow-pressure-efficiency-speed maps; complete maps from Barber-Nichols, Dresser-Rand, etc. are not public.
- **Escape — non-dimensional scaling + BYOD (Bring Your Own Data) interface:**
  1. Default map: use Sandia SNL public single-point or coarse curves as a placeholder.
  2. Engineering layer: implement a generic centrifugal scaling law (flow coefficient vs. head coefficient) so the placeholder is at least dimensionally credible across operating points.
  3. Document loudly: *"Default map is concept-validation only. Component exposes a standard CSV/table input — industrial users plug in their proprietary map."* The win is the ingestion interface, not the default numbers.
- **Public sources currently indexed** (per [`docs/references.bib`](references.bib) and `docs/data_extracts/`):
  `Wright2010_SAND2010_0171` (design point + Table 5.1 main-compressor wheel geometry; first 7 rows of `SNL_compressor_data.csv`),
  `Wright2011_SAND2010_8840` (LWR-temperature condensing-cycle study, Table 2-1 14 modelled state points + Table 4-1 measured rows; first-pass extracted 2026-05-22).
  These are the seed for the BYOD default map; treat each as documented placeholder, not ground truth. (A previously-listed `Conboy2014_SAND2014_2098` candidate was retired 2026-05-22 — source-identity error, see `docs/data_extracts/conboy2014_sand2014-2098.md`.)

### Black Hole 2 — Real PCHE micro-channel geometry & high-fidelity heat-transfer data (Phase 2)

- **Where it bites:** Optimal airfoil-fin pitch and angle of attack are vendor-confidential; experimental Nu data at 700 °C / 20 MPa is sparse and contradictory across papers.
- **Escape — academic stand-ins + the pipeline IS the contribution:**
  1. Drop the vendor-comparison goal. Adopt explicitly idealized geometries from highly-cited PCHE papers (e.g., Ngo et al., Kim et al.) and document the source.
  2. Ship the **end-to-end automated pipeline**: geometry generation → mesh → CFD run → Nu correlation extraction. Even with academic geometries, an open, reproducible pipeline is the durable contribution. Users with confidential geometry can swap inputs and re-run.
- **PCHE references status** (per [`docs/data_extracts/_acquisition_log.md`](data_extracts/_acquisition_log.md)):
  `Kim2014_NED_PCHE`, `Ngo2007_ETFS_PCHE` — both Elsevier-paywalled; landing pages reachable but full text is not. Work continues from author webpage abstracts and prior secondary citations until institutional access is arranged.
  Real engineering-scale chiller geometry (`Wright2010_SAND2010_0171`, Table 3.2: tube OD 38.1 mm / wall 2.4 mm / coil 19.15 m) is on hand for a future `case04_chiller` benchmark.

### Black Hole 3 — Mixture properties at extreme conditions (Phase 1)

- **Where it bites:** For sCO₂ + He or sCO₂ + H₂O at high pressure or near the phase envelope, CoolProp's Span-Wagner / HEOS backend may fail to converge or raise exceptions. There is no experimental dataset to patch the EOS with.
- **Escape — turn the failure boundary into a deliverable:**
  1. Do not treat convergence failures as code defects to suppress. Instead, sweep T-P space and produce a **failure-envelope contour plot** marking where current open property libraries succeed vs. crash.
  2. Publish the map with the call-out: *"Inside this region the current open property stack is unusable — experimental thermodynamics groups, please fill in."* Mapping the boundary of human knowledge is itself a high-value contribution.

### Black Hole 4 — Tritium permeation material constants (Phase 3, § 3.5)

- **Where it bites:** Reported tritium permeability for Inconel 617 (Φ₀, Eₐ) varies by 10×–100× across papers because surface oxide layers dominate the result. There is no single defensible value.
- **Escape — parameterize the uncertainty, do not hide it:**
  1. Never hard-code Φ₀ / Eₐ as a single constant. Expose `Worst_Case` (no oxide barrier, literature maximum) and `Best_Case` (intact oxide, literature minimum) presets, plus a free `Custom` channel.
  2. Reframe the deliverable: the model does not predict an absolute tritium release number (no one can). It bounds the answer for safety analysts: *"under the worst documented case, accumulation is X; under the best, Y."* Bracketing is the honest output.

### Standard handling protocol when data is missing

Apply this loop every time a black hole is hit, in any phase:

1. **Mock it** — replace the missing value with a constant or linear fit so the program runs end-to-end. Never let a data gap block the rest of the stack.
2. **Flag it** — emit a visible runtime log line, e.g. `[WARNING] Placeholder data in use — see docs/known_gaps.md#<anchor>`.
3. **Document it** — record the gap, the placeholder used, and the upstream literature in a single living chapter (Jupyter Book: *Known Data Gaps & Open Questions*).
4. **Publish it** — release the project *with* the documented gaps. A transparent gap is an invitation to collaborators who hold the closed data; a hidden gap is a credibility loss waiting to happen.

### What "success" actually means here

If success is defined as *"reproduce a commercial sCO₂ reactor's full performance numbers"*, the data wall guarantees failure.
The achievable definition of success: **a robust, modular, well-engineered (CI, tests, standardized interfaces) digital infrastructure** that institutions with closed data can run on their own inputs. As long as the skeleton — physics equations, conservation laws, solver logic, software architecture — is correct, the flesh (high-quality experimental data) arrives later, contributed by the labs and groups that own it.

> Cross-references: turbomachinery BYOD interface — § 3.x components; PCHE pipeline — § 2.6; failure-envelope sweeps — § 1.6 / Phase 1 CI; tritium parameter presets — § 3.5.

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
| Key reference data inaccessible (compressor maps, vendor PCHE geometry, mixture EOS at extremes, tritium constants) | High | See *Data Black Holes — Survival Strategy*: ship framework + BYOD interfaces, publish documented placeholders and failure envelopes rather than blocking on data |
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
- Open-source license (Apache-2.0 for code + CC BY-SA 4.0 for docs — aligned with the OpenLithoHub project family; MIT / BSD are also JOSS-acceptable alternatives)
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
