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
**Status:** placeholder; wheel-geometry block + Vrancik windage closure source-anchored in `Compressor.mo` (2026-05-22). Off-design BYOD map (φ → ψ, η) wired through `Modelica.Blocks.Tables.CombiTable1Dv` (2026-05-22) with in-line Sandia-placeholder default + CSV-to-Modelica converter (`src/tools/compressor_map_to_modelica.py`).
**Where it bites:** Modelica turbomachinery components require multidimensional flow-pressure-efficiency-speed maps. Complete maps from Barber-Nichols, Dresser-Rand, Hanwha PSM are commercial secrets.
**Current placeholder:** `Components/Turbomachinery/{Compressor,ReCompressor,Turbine}.mo` exposes scalar isentropic-efficiency defaults plus a symmetric BYOD interface. `Compressor.mo` now drives `eta_isen` from a `CombiTable1Dv` keyed on flow coefficient `φ = ṁ/(ρ·ω·r_tip³)`; the in-line default table mirrors `validation/compressor_maps/sandia_main_compressor.csv` (Wright2010 design point + generic centrifugal surge-to-choke shape, Confidence C). When `useExternalMap=true`, the table is loaded from `mapFileName` (a `#1`-headed Modelica table .txt produced by `tools/compressor_map_to_modelica.py`). The scalar `eta_isen_design = 0.85` / `mdot_design = 100 kg/s` / `PR_design = 2.5` placeholders remain in the parameter block for tooling that does not exercise the table — they are explicitly tagged "not source-anchored". Turbine retains scalar-only defaults (off-design map TODO). **Wheel geometry block (r_tip, b₂, β₂b, Z_r, blade thickness, r_s1, r_h1, β₁bt, α₂, tip clearance, ω_design) in `Compressor.mo` is Confidence-A from Wright2010 SAND2010-0171 Table 5.1 (transcribed 2026-05-22 verbatim from p.54).** **Rotor-windage equation (Vrancik 1968 Eq. 5 with Re-dependent C_d closure, Confidence A) is wired into `Compressor.mo` as opt-in via `enable_windage`; defaults `C_d=0.03` (mid-range of Vrancik's Re=10⁴–10⁸ band) and laminar `C_d=2/Re` fallback exposed.** ReCompressor inherits both blocks + the BYOD table; Turbine retains scalar defaults only (windage is rotor-loss specific to compressor/alternator side per Wright2010 §5.4).
**Escape strategy:** BYOD (Bring Your Own Data) interface. Industrial users plug in their proprietary map via CSV → `tools/compressor_map_to_modelica.py` → .txt → `mapFileName`.
**Upstream (consumed by `.mo` defaults):**
  - `Wright2010_SAND2010_0171` Table 5.1 — main-compressor wheel geometry (r_tip 18.7 mm, b₂ 1.71 mm, β₂b −50°, Z_r=12, tip clearance 0.254 mm, etc.). Now wired as `Compressor.mo` named parameters (2026-05-22). See `docs/data_extracts/wright2010_sand2010-0171.md` "Table 5.1 main-compressor wheel".
  - `Wright2011_SAND2010_8840` — LWR-temperature condensing-cycle modelling (extracted 2026-05-22; Table 2-1 8 rho-gating + 5 excluded modelled rows and Table 4-1 2 measured pairs transcribed into `SNL_compressor_data.csv`). Not yet consumed by `.mo` component defaults.
  - ~~`Conboy2014_SAND2014_2098`~~ — **retired 2026-05-22**: source-identity error (PDF at OSTI 1177045 is SAND2014-3136 wind-turbine report by Resor et al., not the Conboy/Wright/Pasch sCO₂ paper). See `docs/data_extracts/conboy2014_sand2014-2098.md`.
  - `Vrancik1968_NASA_TN_D4849` — windage formula `P_windage = π·C_d(Re)·ρ·r⁴·ω³·L_r` (Eq. 5–6, 7 % experimental error). Read-through complete 2026-05-22. Equation now implemented in `Compressor.mo` as opt-in branch (`enable_windage`); ReCompressor inherits via `extends`.
**Upstream (blocked / future):** STEP Phase 2 RCBC reports (not yet public).

---

## Gap 2 — Real PCHE micro-channel geometry & high-fidelity heat-transfer data  <a id="pche-geometry"></a>

**Phase:** 2 (OpenFOAM benchmark cases, ROM training).
**Status:** placeholder; `case04_chiller` engineering-scale helical-coil pipeline at production-grade refinement (CAD generator + surfaceFeatureExtract + snappyHexMesh (3 4)/(2 3) + surface layers); multi-region gas/liquid split deferred.
**Where it bites:** Optimal airfoil-fin pitch and angle of attack are vendor-confidential (Heatric, Vacuum Process Engineering). Experimental Nu data at 700 °C / 20 MPa is sparse and contradictory.
**Current placeholder:** `cases/case0{1,2,3}_*/system/blockMeshDict` use idealized geometries from highly-cited public papers (Ngo et al., Kim et al.). Vendor comparison is explicitly out of scope. `cases/case04_chiller/` carries the SNL 10 MWe gas-chiller geometry from Wright2010 SAND2010-0171 Table 3.2 (Confidence A: tube ID 33.3 mm, single-coil length 19.15 m). The helical-coil CAD generator `src/tools/cad/helical_coil.py` (added 2026-05-22, tested in `tests/test_helical_coil_cad.py`) emits `helical_tube.stl` + `chiller_shell.stl` from those defaults; `system/surfaceFeatureExtractDict` extracts tube end-cap + shell-rim feature edges into `.eMesh` files; `system/snappyHexMeshDict` cuts both walls at production refinement (tube_wall (3 4) with 5 surface layers, shell_wall (2 3) with 2 surface layers) referencing those features. Background patches renamed `liquid_inlet` / `liquid_outlet` / `background_sides` to reflect that the meshed domain is shell-side only — multi-region split (chtMultiRegionFoam: gas inside the tube + liquid in the shell annulus, coupled at the `tube_wall` faceZone) and gas-side patch exposure are explicitly deferred. See `cases/case04_chiller/README.md` "What still needs doing" for the open multi-region item.
**Escape strategy:** ship the end-to-end automated pipeline (geometry generation → mesh → CFD run → Nu correlation extraction). The pipeline is the contribution; users with confidential geometry can swap inputs and re-run.
**Upstream (blocked):** `Kim2014_NED_PCHE` and `Ngo2007_ETFS_PCHE` — both Elsevier paywalled (per `docs/data_extracts/_acquisition_log.md`); landing pages reachable, full text not. Geometry references continue from author-webpage abstracts and prior secondary citations until institutional access is arranged.
**Upstream (on disk, alternate):** `Wright2010_SAND2010_0171` Table 3.2 — engineering-scale gas-chiller coil geometry (tube OD 38.1 mm / wall 2.4 mm / coil 19.15 m). Now consumed by `cases/case04_chiller/` end-to-end (helical-coil STL via `src/tools/cad/helical_coil.py` + surfaceFeatureExtract + snappyHexMesh at production refinement). Multi-region gas/liquid split (chtMultiRegionFoam) is the next deliverable.

---

## Gap 3 — Mixture properties at extreme conditions  <a id="mixture-eos"></a>

**Phase:** 1 (CoolProp validation).
**Status:** broader-coverage second pass complete (six envelopes shipped: He @ 1/3/5 mol%, H₂O @ 0.5/1/2 mol%); CoolProp-version-bump regeneration workflow shipped as `validation/failure_envelopes/regenerate_all.sh`.
**Where it bites:** For sCO₂ + He or sCO₂ + H₂O at high pressure or near the phase envelope, CoolProp's HEOS backend may fail to converge or raise exceptions.
**Current placeholder:** `src/sco2_mixture_validation.py` returns `None` and prints a physical warning when the two-phase region is encountered. Envelope artifacts under `validation/failure_envelopes/`: `co2_he_{1,3,5}pct.{png,csv}` and `co2_h2o_{0p5,1,2}pct.{png,csv}`. Headline-finding table in the directory README — at CoolProp 7.2.0, He @ 1 % already loses 40 % of the cycle window; He @ 5 % loses 62 %. H₂O failure rate stays ≤ 0.4 % across the three probed levels. After every CoolProp version bump, run `bash validation/failure_envelopes/regenerate_all.sh` and diff CSV `status_code` columns against the prior commit; any non-trivial delta is a finding worth reporting here.
**Escape strategy:** sweep T-P space and publish a contour plot marking where current open property libraries succeed vs. crash. The boundary itself is a high-value contribution. Reproduction CLI is documented in `validation/failure_envelopes/README.md`.
**Upstream (blocked):** `SpanWagner1996_CO2_EOS` — AIP/Cloudflare WAF 403 (per `docs/data_extracts/_acquisition_log.md`). Substitute with NIST Standard Reference Data (SRD 23 / REFPROP documentation) which tabulates the same reference values without paywall, and the in-repo `coolprop_self_consistency.csv` for regression detection.

---

## Gap 4 — Tritium permeation material constants  <a id="tritium-constants"></a>

**Phase:** 3 (`Components/HeatExchangers/TritiumPermeationLayer.mo`).
**Status:** Best/Worst/Custom preset wrapper implemented (2026-05-22); upper/lower envelope re-anchored to a single primary source (Humrickhouse2012 INL/EXT-11-23265, OSTI 1056010, single-pass extracted 2026-05-22).
**Where it bites:** Reported tritium permeability for Inconel 617 (Φ₀, Eₐ) varies by 10×–100× across papers because surface oxide layers dominate the result.
**Current placeholder:** the Modelica component selects between three presets via `parameter Integer preset` (1=Worst_Case no-oxide upper bound, 2=Best_Case intact-oxide lower bound, 3=Custom). Worst defaults Φ₀=7.04e-6 mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵ / Eₐ=89.1 kJ/mol — taken from [`Humrickhouse2012_INL_EXT_11_23265`] Table 1, p.13, ref [11] (Mori 1974), the highest-K₀ of three independent literature values for Inconel 617 hydrogen permeability (table-footnote unit conversion: ÷7.66e4 from cm³(STP)/(cm·s·atm⁰·⁵) → SI). Best defaults Φ₀=7.04e-8 / Eₐ=89.1 kJ/mol — same Arrhenius slope, K₀ reduced by ×100 per the same report's § 4 conclusions ("approximately two orders of magnitude lower than previously measured for hydrogen … attributed to Cr₂O₃ surface oxide", p.43). Custom channel exposes `Phi_0_user` / `E_a_user` and requires the caller to cite their source.
**Escape strategy:** the model bounds the answer rather than predicting an absolute number. Output is *"under the worst documented case, accumulation is X; under the best, Y"*.
**Upstream:** [`Humrickhouse2012_INL_EXT_11_23265`] (transcribed; Table 1 + § 4 conclusions); [`Calderoni2010_INL_EXT_10_19387`] (companion FY-10 hydrogen-only report, indexed for cross-check). Causey *Tritium Barriers and Permeation* SAND2008-1141 not publicly indexed by OSTI search API; superseded as the primary anchor.

---

## Gap 5 — SNL / BYU pilot benchmark CSV rows  <a id="snl-step-rows"></a>

**Phase:** 1 (CI benchmark).
**Status:** SNL populated single-pass; BYU pilot populated single-pass and **actively gating CI** via the new `--check h` enthalpy validator (six state-point rows, all ≤ 0.012 % error against CoolProp 7.2.0, 1 % tolerance); STEP Phase 1 final remains unreleased. Validator extended 2026-05-22 to accept comma-separated `--check rho,h`; CI now runs both checks against both SNL and BYU CSVs in a single invocation. BYU CSV gained one Table 3 row (CHX hot-inlet 45.7 °C / 6.27 MPa — the only non-duplicate Table 3 state vs. Table 2).
**Where it bites:** the test infrastructure exists (`tests/test_sco2_properties.py`, `src/tools/validate_against_sandia.py`); `validation/experimental_data/SNL_compressor_data.csv` now carries 23 rows — 8 transcribed from [`Wright2010_SAND2010_0171`] (2 with measured density actively gating CoolProp regression at ±5 %, plus 6 (T, P, η) reference rows; see `docs/data_extracts/wright2010_sand2010-0171.md`), 1 *modelled* condensing-cycle compressor pair from [`Wright2011_SAND2010_8840`] Table 2-1 Stn 1→2 (`_modelled` tag, ρ blank), 8 additional Table 2-1 modelled stations with paper ρ actively gating CoolProp at <1 % error, 5 Table 2-1 *excluded* (T, P)-only rows (paper rho is a copy-paste artifact — see extract doc § 2.2), and 2 measured Table 4-1 pairs (compressor 1→2, throttle 3→4); `BYU_pilot_data.csv` carries 7 rows transcribed from [`Held2025_BYU_pilot`]: 6 component-pair rows from Table 2 (1.26 MWth simple recuperated cycle, San Rafael Energy Research Center, DOE FE award DE-FE0031928), each carrying `h_inlet_measured_J_kg` from Table 2 column h, plus 1 row from Table 3 capturing the CHX hot-inlet (45.7 °C / 6.27 MPa) — the only Table 3 state not duplicated by Table 2. ρ left blank because the source paper does not tabulate density.
**Current placeholder:** BYU CSV does not gate the density check (paper tabulates P / T / mdot / h, not ρ); validator's ρ branch skips on the same CSV that the h branch validates. Cross-source confidence comes from the dedicated enthalpy validator (`validate_against_sandia.py --check h`, or as part of `--check rho,h`) — extended 2026-05-22 to accept comma-separated quantity lists, so a single CI invocation runs both ρ and h against the same CSV; checks whose column is missing or blank skip cleanly rather than failing. CoolProp's `H('T', T, 'P', P, CO2)` agrees with the BYU paper's tabulated h at ≤ 0.012 % across all 6 component-pair inlet states, well inside the 1 % tolerance. STEP Phase 1 final report (Southwest Research Institute, 10 MWe demonstration) remains unreleased; do not treat the BYU pilot data as a STEP substitute.
**Escape strategy:** continue transcribing additional public reports per `docs/citation_protocol.md`. ρ + h gating now active via `--check rho,h`; the validator gracefully no-ops on legacy schemas (SNL CSV pre-h, self-consistency CSV) so the same CI step covers every benchmark file. Wait for DOE STEP Phase 1 final and add as a *new* CSV (`STEP_phase1_data.csv` revived) when it appears — do not back-fill BYU pilot rows under that filename.
**Upstream:** `Wright2010_SAND2010_0171` (transcribed); `Wright2011_SAND2010_8840` (Table 2-1 + Table 4-1 transcribed 2026-05-22); `Held2025_BYU_pilot` (transcribed: Table 2 state points with enthalpy column actively gating CI; Table 3 CHX hot-inlet rowed 2026-05-22; Table 1 fired-heater inlet intentionally not rowed because it duplicates Table 2 state 3). All three entries indexed in `docs/data_extracts/_acquisition_log.md`. (`Conboy2014_SAND2014_2098` retired 2026-05-22 due to source-identity error — see Gap 1.)

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
