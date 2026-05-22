# Vrancik 1968 — Prediction of Windage Power Loss in Alternators

> **BibTeX key:** `Vrancik1968_NASA_TN_D4849`
> **Source:** J. E. Vrancik, NASA-TN-D-4849, NASA Lewis Research
> Center, October 1968.
> URL: https://ntrs.nasa.gov/citations/19680027690
> **Read-through date:** 2026-05-22 (single-pass).

## What this document is

A per-section index of formulas and constants from Vrancik's
windage-loss prediction. The Wright2010 SAND report cites this work
indirectly for the `Pwr = π·C_d(Re)·ρ·r⁴·ω³·L_r` rotor-windage
formula (see `docs/data_extracts/wright2010_sand2010-0171.md`,
"§5.4 Vrancik windage formula").

This document is now a **direct** primary reference. The formula is
exactly as Wright2010 transcribed it; confidence grade upgrades from
**C → A** (read off Eq. 5 verbatim, with Eq. 6 closing the C_d(Re)
dependence).

The PDF is **not** committed. Local copy:
`~/Downloads/Vrancik1968_NASA_TN_D4849.pdf` (749 KB, 21 pages,
downloaded 2026-05-21 from NTRS direct).

## § Cylindrical-rotor windage formula — Eq. (5) [Confidence A]

- **Source location:** Eq. (5), p.5 (PDF body page numbering).
- **Verbatim form:**
  `W = π · C_d · ρ · R⁴ · ω³ · L`
  where `W` is windage power loss (watts), `C_d` is the skin-friction
  coefficient, `ρ` is fluid density, `R` is rotor radius, `ω` is angular
  velocity (rad/s), `L` is cylinder length. Symbols defined in the
  SYMBOLS list, p.2 (kinematic viscosity ν = µ/ρ; Re = R·ω·R/ν =
  R²·ω/ν).
- **Used in this repo by:**
  `docs/02_phase2_cfd_rom.md` § "ROM physical constraints",
  `docs/03_phase3_modelica.md` Compressor.mo windage-loss row.
- **Used as:** **direct primary reference** for the windage power
  formula. Confidence A.

## § Skin-friction coefficient — Eq. (6) [Confidence A]

- **Source location:** Eq. (6), p.6.
- **Verbatim form:**
  `1 / √C_d = B + 1.768 · ln(Re · √C_d)`,
  with experimental B = 2.04 (ref. [2]).
- **Notes:**
  - Implicit in `C_d`; iterate or invert numerically to get C_d(Re).
  - Derivation assumes turbulent flow in the air gap, modelled as
    parallel-plate flow; the laminar-flow form of Eq. (5) uses
    `C_d = 2/Re` (eq. between Eqs. 4 and 5, p.5).
- **Used in this repo by:** intended downstream — when a windage
  ROM constraint is implemented, both the laminar (`C_d = 2/Re`)
  and turbulent (Eq. 6) regimes will be available.
- **Used as:** primary closure formula for `C_d(Re)`. Confidence A.

## § Experimental verification — 7 % maximum error [Confidence A]

- **Source location:** § "Experimental verification of equations (5)
  and (6)", p.6, paragraph 1.
- **Content:** Verbatim: "The maximum difference between the
  experimental and calculated loss is 7 percent. This represents very
  good correlation in windage loss testing."
- **Test conditions:** smooth cylindrical rotor, slotted alternator
  stator, ambient air, Re ≈ 5000 at 12 000 rpm.
- **Used in this repo by:** intended downstream — sets the empirical
  uncertainty bound for windage as a ROM soft-physical constraint
  (constraint tolerance 7 % of predicted W).
- **Used as:** quantitative anchor for ROM tolerance band on windage
  loss. Confidence A.

## § Salient-pole correction factor K [Confidence A]

- **Source location:** symbols list p.2 (`K = salient-pole correction
  factor`); applied later in the report for shrouded homopolar
  inductor alternators.
- **Used in this repo by:** none yet.
- **Used as:** indexed for future use if turbomachinery components
  with non-cylindrical rotor geometry are added.

## § Pending follow-ups (downstream)

- [x] Read-through pass 1 (2026-05-22).
- [x] Transcribe windage formula (Eq. 5) and turbulent C_d closure
  (Eq. 6) verbatim.
- [ ] Update `docs/data_extracts/wright2010_sand2010-0171.md`
  "Vrancik windage formula" entry to point both to Wright2010 §5.4
  (where the formula is *applied*) and to this primary source (where
  it is *defined*). Confidence grade A.
- [ ] Implement as ROM soft-physical-constraint candidate per
  `docs/02_phase2_cfd_rom.md` follow-up.
