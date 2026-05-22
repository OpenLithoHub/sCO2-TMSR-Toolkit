# Tritium Permeability of Incoloy 800H and Inconel 617 (INL/EXT-11-23265)

> **BibTeX key:** `Humrickhouse2012_INL_EXT_11_23265`
> **Source:** Humrickhouse, Pawelko, Shimada, Winston, *Idaho National
> Laboratory*, INL/EXT-11-23265 Revision 1, July 2012,
> [https://www.osti.gov/biblio/1056010](https://www.osti.gov/biblio/1056010).
> **Read-through date:** 2026-05-22 (single-pass; first 47 pages
> + Appendix B).

## What this document is

A bookmark of every fact, table, figure, or pointer in the source that
has been (or might be) used by this toolkit. New uses append; old
entries are not deleted even if superseded.

## § 1 / Table 1 — Literature Arrhenius constants for hydrogen permeation in Inconel 617 [Confidence A]

- **Source location:** Table 1, p.13 (full PDF page numbering, body
  page "13").
- **Content:** Three independent literature values for Inconel 617
  hydrogen permeability in the diffusion-limited regime
  (`K = K0 · exp(-Q/RT)`), units of K0 are `cm^3 H2 (STP) / (cm · s · atm^0.5)`.
  The footnote on p.13 ("To convert to mol/(m · s · Pa^0.5),
  divide by 7.66e4") fixes the conversion factor.
  - Ref [11] — Mori et al. 1974: K0 = 5.39e-1, Q = 21.3 kcal/mol,
    T = 650-950 °C, P = 0.001-0.01 atm.
  - Ref [7]  — Roehrig 1975:    K0 = 2.28e-1, Q = 18.9 kcal/mol,
    T = 600-1050 °C, P = 1-10 atm.
  - Ref [5]  — Masui 1979:      K0 = 1.39e-1, Q = 19.8 kcal/mol,
    T = 750-950 °C, P < 40 atm.
- **Conversion to SI** (mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵, kJ/mol):
  - Ref [11]: K0 = 7.04e-6, Q = 89.1 kJ/mol.
  - Ref [7]:  K0 = 2.98e-6, Q = 79.1 kJ/mol.
  - Ref [5]:  K0 = 1.81e-6, Q = 82.8 kJ/mol.
- **Used in this repo by:**
  `modelica/AdvancedReactor_sCO2_Library/Components/HeatExchangers/TritiumPermeationLayer.mo`
  (`Phi_0_worst`, `E_a_worst`),
  `docs/known_gaps.md#tritium-constants`.
- **Used as:** Worst-Case (no oxide) Arrhenius envelope upper bound.
  Modelica defaults take ref [11] as the most conservative single-source
  value (highest K0 of the three, largest at the upper end of the
  fit-temperature range): K0 = 7.04e-6, Eₐ = 89.1 kJ/mol.

## § 4 / Conclusions — Surface-oxide reduction factor [Confidence A]

- **Source location:** § 4 conclusions, p.43 (PDF body page 43); also
  cross-referenced § 5 p.44 paragraph 1.
- **Content:** "The result was a permeability value that was
  approximately two orders of magnitude lower than previously measured
  for hydrogen". The text attributes the gap to surface oxide
  (Cr₂O₃) on the Inconel 617 sample acting as a permeation barrier.
- **Used in this repo by:**
  `Components/HeatExchangers/TritiumPermeationLayer.mo` (`Phi_0_best`,
  inner-comment justification for the 100× reduction from `Phi_0_worst`).
- **Used as:** quantitative anchor for the Worst→Best envelope ratio.
  Best case ≈ Worst K0 ÷ 100 (oxide reduces magnitude, leaves Eₐ broadly
  unchanged); the model uses K0_best = 7.04e-8 mol·m⁻¹·s⁻¹·Pa⁻⁰·⁵,
  Eₐ_best = 89.1 kJ/mol on the same Arrhenius slope.
- **Verbatim quote (for traceability):** "The result was a permeability
  value that was approximately two orders of magnitude lower than
  previously measured for hydrogen ... Some tests noted in the
  literature indicate that surface oxidation of high Ni alloys can
  reduce the permeability by 2 to 3 orders of magnitude, consistent with
  the current test observations." — § 4, p.36 / § 5, p.44.

## § 4.1 — Sieverts' + Fick's permeation model [Confidence A]

- **Source location:** Equations (1)–(6), pp.30–31.
- **Content:** Confirms the same mathematical form used in
  `TritiumPermeationLayer.mo`:
  `J = (K/x)·(sqrt(P_T2,1) − sqrt(P_T2,2))` and
  `K = K0·exp(−Q/RT)`. Discusses the diffusion-limited vs. surface-
  limited transition (dimensionless number W, Eq. (41)–(42)), confirming
  that for the model as written we are in the diffusion-limited regime
  whenever (Kd · x · sqrt(P)) / (Ks · D) >> 1.
- **Used in this repo by:** the model docstring of
  `TritiumPermeationLayer.mo` (validation strategy).
- **Used as:** confirmation that the Sieverts + Fick form is
  appropriate for the operating regime targeted by this toolkit
  (sCO₂ secondary loop, P_T2 typically << 1 Pa per § 1.6 of
  the project plan).

## Appendix B — Inconel 617 raw test data [Confidence A]

- **Source location:** Tables B-1, B-2, p.51.
- **Content:** Nine FY-11 permeation test points (TS17_1–TS17_9) for
  Inconel 617 at 700/800/900 °C peak, with primary T₂ pressure
  0.32–0.67 Pa and secondary T₂ pressure 3.6e-4–3.6e-2 Pa. Sample
  thickness 0.0254 cm, length 15.24 cm, He pressure 1.05e5 Pa both
  loops.
- **Used in this repo by:** not directly transcribed yet. Indexed
  here as a future source for either (a) a tritium component-level
  CSV benchmark file once one exists, or (b) regression-test inputs
  for `TritiumPermeationLayer.mo`.
- **Used as:** N/A yet — pointer.
