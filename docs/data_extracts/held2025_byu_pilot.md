# Held et al. 2025 — Extended Duration Operation of a Pilot-Scale Supercritical CO₂ Test Loop

> **BibTeX key:** `Held2025_BYU_pilot`
> **Source:** T. J. Held, K. Sedlacko, B. Bowan, V. Avadhanula,
> J. D. Miller, A. Fry, B. Schoof, S. Montgomery (Echogen Power Systems
> + Brigham Young University + San Rafael Energy Research Center),
> *Extended Duration Operation of a Pilot-Scale Supercritical CO₂
> Test Loop*, Proceedings of the ASME Turbo Expo 2025, GT2025-152150,
> Memphis, TN, June 2025.
> URL: https://www.osti.gov/biblio/2575689 (DOE OSTI)
> **Read-through date:** 2026-05-22 (first pass — pp. 1–10, all tables)
> **Reviewer:** AI-transcribed, single-pass

> **Source-identity correction (2026-05-22):** earlier this repo logged
> this paper under `Allison2025_STEP_extended` and used it as a
> substitute citation for the (still-unreleased) DOE STEP Phase 1
> final report. That mapping is wrong: the paper describes the
> **BYU/Echogen 1.26 MWth pilot-scale sCO₂ test loop at the San Rafael
> Energy Research Center**, funded under DOE FE award `DE-FE0031928`.
> This is a *different* DOE-funded sCO₂ pilot from STEP (which is the
> Southwest Research Institute–led 10 MWe demonstration). Both are
> referenced as "DOE pilot-scale sCO₂ test loops" but they are not
> the same loop, scale, or programme. The data below is **not** a
> stand-in for STEP — it is a self-standing benchmark in its own
> right, complementing Sandia (Wright/Conboy) and STEP (when STEP
> publishes).

## What this document is

A per-section index of operating-point data and design parameters in
the GT2025-152150 paper that this toolkit uses (or might use) for
CoolProp regression and cycle-level Modelica validation.

The PDF is **not** committed. Local copy:
`~/Downloads/STEP_2025_extended_duration.pdf` (15 246 152 bytes,
downloaded 2026-05-22 via OSTI direct + local proxy + multi-segment
resume). The filename retains the original misnamed download
(`STEP_2025_*`) — not renamed on disk to preserve the acquisition
log audit trail; future fetches should save under the corrected key.

---

## § 1.1 — Test-loop overall topology  [Confidence A]

- **Source location:** [Held2025_BYU_pilot, §1, p.2; Figure 3, p.3]
- **Content:** simple recuperated sCO₂ system. Loop ordering at the
  primary side: pump → recuperator (cold side, 2→3) → fired heater
  PHX (3→4) → throttle valve (4→5) → recuperator (hot side, 5→6) →
  cooler/condenser CHX (6→1) → pump. State numbering matches Table 2
  below; primed states `2'`, `3'`, `4'`, `5'` denote the *downstream*
  boundary of each connecting pipe (versus unprimed = upstream).
  Loop has no work-extraction turbine — the throttle valve produces
  the pressure differential a turbine would.
- **Used in this repo by:** *not yet*. Strong candidate for a
  `Cycles/SimpleRecuperated_BYU.mo` Modelica example once Phase 3
  cycle-level work begins.

## § 1.2 — Table 1 — Fired heater design point  [Confidence A]

- **Source location:** [Held2025_BYU_pilot, Table 1, p.2]
- **Content:**

  | Parameter | Value |
  |-----------|-------|
  | Inlet temperature | 415 °C |
  | Inlet pressure | 20.38 MPa |
  | Pressure drop | 0.4 MPa |
  | Outlet temperature | 600 °C |
  | CO₂ flow rate | 5.5 kg/s |
  | Thermal input (CO₂) | 1.26 MW |
  | Thermal duty (fired) | 1.58 MW (assuming 80 % burner efficiency) |

- **Used as:** PHX bounding conditions for any future cycle model
  using this loop as its physical reference.

## § 1.3 — Table 2 — Full 11-state-point cycle design point  [Confidence A]

- **Source location:** [Held2025_BYU_pilot, Table 2, p.4]
- **Content:** complete state-point table for the BYU pilot
  recuperated cycle. Columns are P (MPa), T (°C), ṁ (kg/s),
  h (kJ/kg). Unprimed states are the upstream boundary of each
  connecting pipe, primed states are the downstream boundary.
  Wi / Wo are the cooling-water inlet / outlet states.

  | State | P (MPa) | T (°C) | ṁ (kg/s) | h (kJ/kg) |
  |-------|---------|--------|----------|-----------|
  | 1   |  6.78 |  20.5 |  5.50 |  252.5 |
  | 2   | 20.68 |  38.7 |  5.50 |  273.3 |
  | 2'  | 20.58 |  38.6 |  5.50 |  273.3 |
  | 3   | 20.38 | 415.1 |  5.50 |  868.5 |
  | 3'  | 20.28 | 415.0 |  5.50 |  868.5 |
  | 4   | 19.88 | 600.0 |  5.50 | 1097.5 |
  | 4'  | 19.58 | 600.0 |  5.50 | 1097.5 |
  | 5   |  7.18 | 593.1 |  5.50 | 1097.5 |
  | 5'  |  7.08 | 593.0 |  5.50 | 1097.5 |
  | 6   |  6.88 |  80.0 |  5.50 |  502.3 |
  | Wi  |  0.10 |  20.0 | 32.9 |   84.0 |
  | Wo  |  0.10 |  30.0 | 32.9 |  125.8 |

- **Used in this repo by:**
  `validation/experimental_data/BYU_pilot_data.csv` — selected pairs
  transcribed as `Held2025_BYU_T2_*` rows for CoolProp enthalpy /
  density regression at each pipe-end state.
- **Used as:** measured-grade benchmark for CoolProp's enthalpy and
  density calls across the full cycle window (20–600 °C, 7–21 MPa).

## § 1.4 — Table 3 — Recuperator + CHX design points  [Confidence A]

- **Source location:** [Held2025_BYU_pilot, Table 3, p.6]
- **Content:**

  | Side | RHX (recuperator) | CHX (cooler/condenser) |
  |------|-------------------|------------------------|
  | Hot inlet  | CO₂ 593 °C / 7.08 MPa  | CO₂ 45.7 °C / 6.27 MPa |
  | Hot outlet | CO₂ 80.0 °C            | CO₂ 20.0 °C            |
  | Hot ΔP     | 0.20 MPa               | 0.07 MPa               |
  | Hot ṁ      | 5.50 kg/s              | 5.50 kg/s              |
  | Cold inlet  | CO₂ 38.6 °C / 20.58 MPa | Water 12.8 °C / 0.48 MPa |
  | Cold outlet | CO₂ 415.1 °C           | Water 22.7 °C          |
  | Cold ΔP     | 0.20 MPa               | 0.22 MPa               |
  | Cold ṁ      | 5.50 kg/s              | 32.1 kg/s              |
  | Thermal duty | 3.27 MW               | 2.37 MW                |
  | Conductance UA | 27.8 kW/K          | 186.7 kW/K             |

- **Used as:** sizing reference for a future Modelica recuperator /
  cooler component validated against measured UA.

## § 2 — Operations / continuous-run statistics  [Confidence A]

- **Source location:** [Held2025_BYU_pilot, §2, p.4]
- **Content:** initial firing April 2023. First long-duration run
  June 19–22 2023 (80 hours continuous). Second run October 18–22
  2024 (115 hours continuous). Combined extended-duration testing
  exceeded 200 hours continuous operation across natural-gas / coal
  / coal+gas firing modes. Instrumentation: Class A PT100 RTDs
  ±0.15 + 0.002·T °C, Rosemount 3051 pressure transmitters
  ±0.065 % of span, Emerson Micro Motion Coriolis flowmeters
  ±0.05 % of reading.
- **Used as:** uncertainty bound when applying the Table 2 state
  points as CoolProp benchmarks.

## § 2.2 — Pump performance  [Confidence A]

- **Source location:** [Held2025_BYU_pilot, §2.2, p.5; Figure 5]
- **Content:** quintuplex plunger pump (NOV 350Q-5M, alternative to
  centrifugal because flow rate is too small for a centrifugal
  compressor at this scale); 3.5 kg/s design flow. Pump inlet
  pressure setpoint 9.25 MPa to avoid CO₂ vapor formation /
  cavitation. Density ratio across pump only 1.08 → near-incompressible.
  Measured isentropic efficiency 0.8–0.9 (RMS uncertainty ~±0.09);
  volumetric efficiency 0.85–0.88 declining to 0.806 at high pressure
  ratio (uncertainty ±0.006 + unknown belt-slip contribution).
- **Used as:** order-of-magnitude check for any "low-flow positive-
  displacement compressor" component the Modelica library might add.

---

## § Pending follow-ups

- [ ] Add a `Cycles/SimpleRecuperated_BYU.mo` Modelica example
      (Phase 3) when cycle-level scaffolding lands. Use Table 2 as
      reference state points.
- [ ] If/when DOE STEP Phase 1 final report is released, file it
      under a *new* BibTeX key and acquisition-log row. Do **not**
      back-fill it into this entry — STEP and BYU pilot are separate
      programmes.
