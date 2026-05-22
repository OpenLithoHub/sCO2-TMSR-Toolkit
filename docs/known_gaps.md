# Known Data Gaps & Open Questions

> **Mindset:** this project ships a framework and pipeline, **not ground-truth data**.
> Every numeric placeholder below is intentional. Replace with verified values from
> the cited public source before claiming "validated against experimental data".
>
> Reference: [`docs/00_strategy.md` § Data Black Holes — Survival Strategy](00_strategy.md#data-black-holes--survival-strategy)
>
> Standard handling protocol when a data gap is hit:
> 1. **Mock it** — replace the missing value with a constant or linear fit so the program runs end-to-end.
> 2. **Flag it** — emit a runtime log line such as `[WARNING] Placeholder data in use — see docs/known_gaps.md#<anchor>`.
> 3. **Document it** — record the gap, the placeholder used, and the upstream literature here.
> 4. **Publish it** — release the project *with* the documented gaps; transparent gaps invite collaborators.

---

## Gap 1 — sCO₂ compressor / turbine performance maps  <a id="compressor-maps"></a>

**Phase:** 3 (Modelica turbomachinery)
**Status:** placeholder.
**Where it bites:** Modelica turbomachinery components require multidimensional flow-pressure-efficiency-speed maps. Complete maps from Barber-Nichols, Dresser-Rand, Hanwha PSM are commercial secrets.
**Current placeholder:** `Components/Turbomachinery/{Compressor,ReCompressor,Turbine}.mo` exposes a generic centrifugal scaling law and a CSV input parameter. The default coefficients are based on Sandia SNL public single-point data and are **concept-validation only**.
**Escape strategy:** BYOD (Bring Your Own Data) interface. Industrial users plug in their proprietary map via CSV.
**Upstream (already on disk, transcription pending):**
  - `Wright2010_SAND2010_0171` — Table 5.1 main-compressor wheel geometry (used as `Compressor.mo` defaults; see `docs/data_extracts/wright2010_sand2010-0171.md`).
  - `Wright2011_SAND2010_8840` — LWR-temperature condensing-cycle modelling (first-pass extracted 2026-05-22; Table 2-1 14 modelled state points and Table 4-1 measured rows pending transcription).
  - `Conboy2014_SAND2014_2098` — operating-point sweep (extract stub created; transcription pending).
  - `Vrancik1968_NASA_TN_D4849` — primary windage formula (read-through pending; once transcribed, lifts windage cite from C → A confidence).
**Upstream (blocked / future):** STEP Phase 2 RCBC reports (not yet public).

---

## Gap 2 — Real PCHE micro-channel geometry & high-fidelity heat-transfer data  <a id="pche-geometry"></a>

**Phase:** 2 (OpenFOAM benchmark cases, ROM training).
**Status:** placeholder.
**Where it bites:** Optimal airfoil-fin pitch and angle of attack are vendor-confidential (Heatric, Vacuum Process Engineering). Experimental Nu data at 700 °C / 20 MPa is sparse and contradictory.
**Current placeholder:** `cases/case0{1,2,3}_*/system/blockMeshDict` use idealized geometries from highly-cited public papers (Ngo et al., Kim et al.). Vendor comparison is explicitly out of scope.
**Escape strategy:** ship the end-to-end automated pipeline (geometry generation → mesh → CFD run → Nu correlation extraction). The pipeline is the contribution; users with confidential geometry can swap inputs and re-run.
**Upstream (blocked):** `Kim2014_NED_PCHE` and `Ngo2007_ETFS_PCHE` — both Elsevier paywalled (per `docs/data_extracts/_acquisition_log.md`); landing pages reachable, full text not. Geometry references continue from author-webpage abstracts and prior secondary citations until institutional access is arranged.
**Upstream (on disk, alternate):** `Wright2010_SAND2010_0171` Table 3.2 — engineering-scale gas-chiller coil geometry (tube OD 38.1 mm / wall 2.4 mm / coil 19.15 m). Reserved for a future `case04_chiller` benchmark beside the academic-paper geometries.

---

## Gap 3 — Mixture properties at extreme conditions  <a id="mixture-eos"></a>

**Phase:** 1 (CoolProp validation).
**Status:** first-pass failure-envelope sweep produced; broader-coverage second pass pending.
**Where it bites:** For sCO₂ + He or sCO₂ + H₂O at high pressure or near the phase envelope, CoolProp's HEOS backend may fail to converge or raise exceptions.
**Current placeholder:** `src/sco2_mixture_validation.py` returns `None` and prints a physical warning when the two-phase region is encountered. First-pass envelope artifacts under `validation/failure_envelopes/`: `co2_he_3pct.{png,csv}` (CO₂ + 3 mol% He, ~54 % of T-P window unsupported) and `co2_h2o_1pct.{png,csv}` (CO₂ + 1 mol% H₂O, ~0.1 % failure). Coverage at additional impurity fractions (e.g. He @ 1 %/5 %, H₂O @ 0.5 %/2 %) and a CoolProp-version-bump regeneration workflow are still pending.
**Escape strategy:** sweep T-P space and publish a contour plot marking where current open property libraries succeed vs. crash. The boundary itself is a high-value contribution. Reproduction CLI is documented in `validation/failure_envelopes/README.md`.
**Upstream (blocked):** `SpanWagner1996_CO2_EOS` — AIP/Cloudflare WAF 403 (per `docs/data_extracts/_acquisition_log.md`). Substitute with NIST Standard Reference Data (SRD 23 / REFPROP documentation) which tabulates the same reference values without paywall, and the in-repo `coolprop_self_consistency.csv` for regression detection.

---

## Gap 4 — Tritium permeation material constants  <a id="tritium-constants"></a>

**Phase:** 3 (`Components/HeatExchangers/TritiumPermeationLayer.mo`).
**Status:** Best/Worst/Custom preset wrapper implemented (2026-05-22); literature-bracketed defaults indicative only — second-pass verification of upper/lower envelope values pending.
**Where it bites:** Reported tritium permeability for Inconel 617 (Φ₀, Eₐ) varies by 10×–100× across papers because surface oxide layers dominate the result.
**Current placeholder:** the Modelica component selects between three presets via `parameter Integer preset` (1=Worst_Case no-oxide upper bound, 2=Best_Case intact-oxide lower bound, 3=Custom). Worst defaults Φ₀=2e-6 / Eₐ=42 kJ/mol, Best defaults Φ₀=2e-8 / Eₐ=55 kJ/mol; both are **indicative envelope values** anchored to Causey SAND2008-1141 + Forcey 1988 narrative ranges — not single-source-traceable yet. Custom channel exposes `Phi_0_user` / `E_a_user` and requires the caller to cite their source.
**Escape strategy:** the model bounds the answer rather than predicting an absolute number. Output is *"under the worst documented case, accumulation is X; under the best, Y"*.
**Upstream:** Causey et al., *Tritium Barriers and Permeation*, SAND2008-1141; Forcey et al., *J. Nucl. Mater.* (1988) — Inconel series data.

---

## Gap 5 — SNL / BYU pilot benchmark CSV rows  <a id="snl-step-rows"></a>

**Phase:** 1 (CI benchmark).
**Status:** SNL populated single-pass; BYU pilot populated single-pass (10 state pairs cross-verified against CoolProp enthalpy at ≤ 0.03 % error); STEP Phase 1 final remains unreleased.
**Where it bites:** the test infrastructure exists (`tests/test_sco2_properties.py`, `src/tools/validate_against_sandia.py`); `validation/experimental_data/SNL_compressor_data.csv` now carries 9 rows — 8 transcribed from [`Wright2010_SAND2010_0171`] (2 with measured density actively gating CoolProp regression at ±5 %, plus 6 (T, P, η) reference rows; see `docs/data_extracts/wright2010_sand2010-0171.md`) and 1 *modelled* condensing-cycle pair from [`Wright2011_SAND2010_8840`] Table 2-1 Stn 1→2 (`_modelled` tag, ρ left blank so the density gate is skipped); `BYU_pilot_data.csv` carries 6 component-pair rows transcribed from [`Held2025_BYU_pilot`] Table 2 (1.26 MWth simple recuperated cycle, San Rafael Energy Research Center, DOE FE award DE-FE0031928); ρ left blank because the source paper does not tabulate density.
**Current placeholder:** BYU CSV does not gate the density check (paper tabulates P / T / mdot / h, not ρ); validator skips. Cross-source confidence comes from the secondary check that CoolProp's `H('T', T, 'P', P, CO2)` agrees with the paper's tabulated h at ≤ 0.03 % across all 10 state points — single-pass transcription verified end-to-end. STEP Phase 1 final report (Southwest Research Institute, 10 MWe demonstration) remains unreleased; do not treat the BYU pilot data as a STEP substitute.
**Escape strategy:** continue transcribing additional public reports per `docs/citation_protocol.md`. Add a dedicated enthalpy-based validator (`validate_enthalpy.py` or a `--check h` flag on the existing tool) so the BYU rows actively gate CI, not just record state. Wait for DOE STEP Phase 1 final and add as a *new* CSV (`STEP_phase1_data.csv` revived) when it appears — do not back-fill BYU pilot rows under that filename.
**Upstream:** `Wright2010_SAND2010_0171` (transcribed); `Wright2011_SAND2010_8840`, `Conboy2014_SAND2014_2098` (on disk, additional rows pending); `Held2025_BYU_pilot` (transcribed: Table 2 state points; Table 1 / Table 3 design points indexed in extract doc but not yet rowed). All four entries indexed in `docs/data_extracts/_acquisition_log.md`.

---

## Gap 6 — TMSR-LF1 online-refueling transient data  <a id="tmsr-lf1"></a>

**Phase:** 3 (`Components/Reactor/OnlineFuellingTransient.mo`, optional v1.4 extension).
**Status:** model skeleton uses point-kinetics with literature-bracketed parameters.
**Where it bites:** quantitative validation requires SINAP-internal transient data not available publicly.
**Current placeholder:** point-kinetics model uses `beta_eff = 0.003` (Th-U typical), `Lambda = 1e-4 s` (literature estimate). Reactivity-insertion magnitudes per refueling batch (`±5 pcm`) are estimates pending SINAP publication.
**Escape strategy:** clearly mark the model as "simplified; not validated against experimental TMSR-LF1 data". Track SINAP/CNNC 2025–2026 publications for parameter updates.
**Upstream:** SINAP public announcements (2023–2025); future TMSR-LF1 operational papers.

---

## How to update this file

When you add a placeholder anywhere in the repo:

1. Append a new section here with an anchor matching the warning emitted at runtime.
2. Reference the section from any code comment near the placeholder, e.g.
   `# WARNING: placeholder — see docs/known_gaps.md#compressor-maps`.
3. When the placeholder is replaced with verified data, change the **Status** line
   to "verified" and cite the source. **Never delete the section** — the gap
   history is itself documentation.
