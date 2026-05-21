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
**Upstream:** Sandia SNL test reports (Wright et al. 2010–2016), STEP Phase 1 reports (when fully released).

---

## Gap 2 — Real PCHE micro-channel geometry & high-fidelity heat-transfer data  <a id="pche-geometry"></a>

**Phase:** 2 (OpenFOAM benchmark cases, ROM training).
**Status:** placeholder.
**Where it bites:** Optimal airfoil-fin pitch and angle of attack are vendor-confidential (Heatric, Vacuum Process Engineering). Experimental Nu data at 700 °C / 20 MPa is sparse and contradictory.
**Current placeholder:** `cases/case0{1,2,3}_*/system/blockMeshDict` use idealized geometries from highly-cited public papers (Ngo et al., Kim et al.). Vendor comparison is explicitly out of scope.
**Escape strategy:** ship the end-to-end automated pipeline (geometry generation → mesh → CFD run → Nu correlation extraction). The pipeline is the contribution; users with confidential geometry can swap inputs and re-run.
**Upstream:** Kim et al. *Nuclear Engineering and Design* 270 (2014) 73–81; Ngo et al. *Experimental Thermal and Fluid Science* 32 (2007) 560–570.

---

## Gap 3 — Mixture properties at extreme conditions  <a id="mixture-eos"></a>

**Phase:** 1 (CoolProp validation).
**Status:** failure-envelope sweep planned; not yet executed.
**Where it bites:** For sCO₂ + He or sCO₂ + H₂O at high pressure or near the phase envelope, CoolProp's HEOS backend may fail to converge or raise exceptions.
**Current placeholder:** `src/sco2_mixture_validation.py` returns `None` and prints a physical warning when the two-phase region is encountered. Failure-envelope contour plots have not yet been produced.
**Escape strategy:** sweep T-P space and publish a contour plot marking where current open property libraries succeed vs. crash. The boundary itself is a high-value contribution.
**Upstream:** Span & Wagner (1996); REFPROP NIST mixture model documentation.

---

## Gap 4 — Tritium permeation material constants  <a id="tritium-constants"></a>

**Phase:** 3 (`Components/Reactor/TritiumPermeationLayer.mo`).
**Status:** parameterized, not hard-coded.
**Where it bites:** Reported tritium permeability for Inconel 617 (Φ₀, Eₐ) varies by 10×–100× across papers because surface oxide layers dominate the result.
**Current placeholder:** the Modelica component exposes `Worst_Case` (no oxide barrier, literature maximum), `Best_Case` (intact oxide, literature minimum), and `Custom` parameter sets. **Defaults are indicative only.**
**Escape strategy:** the model bounds the answer rather than predicting an absolute number. Output is *"under the worst documented case, accumulation is X; under the best, Y"*.
**Upstream:** Causey et al., *Tritium Barriers and Permeation*, SAND2008-1141; Forcey et al., *J. Nucl. Mater.* (1988) — Inconel series data.

---

## Gap 5 — SNL / STEP benchmark CSV rows  <a id="snl-step-rows"></a>

**Phase:** 1 (CI benchmark).
**Status:** placeholder rows commented out in CSV; pytest skips assertions.
**Where it bites:** the test infrastructure exists (`tests/test_sco2_properties.py`, `src/tools/validate_against_sandia.py`) but the CSVs `validation/experimental_data/{SNL_compressor_data,STEP_phase1_data}.csv` ship empty (header-only).
**Current placeholder:** illustrative rows are present as comments only. `validate_against_sandia.py` exits 0 when no measured rows are found.
**Escape strategy:** transcribe rows directly from public Sandia OSTI reports and DOE STEP Phase 1 reports. Verify each row against the cited table before uncommenting.
**Upstream:** OSTI search `supercritical CO2 test loop Sandia`; DOE STEP Phase 1 final report.

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
