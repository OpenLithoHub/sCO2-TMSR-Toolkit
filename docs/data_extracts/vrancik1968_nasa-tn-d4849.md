# Vrancik 1968 — Prediction of Windage Power Loss in Alternators

> **BibTeX key:** `Vrancik1968_NASA_TN_D4849`
> **Source:** J. E. Vrancik, NASA-TN-D-4849, NASA Lewis Research
> Center, October 1968.
> URL: https://ntrs.nasa.gov/citations/19680027690
> **Read-through date:** _pending_
> **Reviewer:** _pending_

## What this document is

A per-section index of formulas and constants from Vrancik's
windage-loss prediction. The Wright2010 SAND report cites this work
indirectly for the `Pwr = π·C_d(Re)·ρ·r⁴·ω³·L_r` rotor-windage
formula (see `docs/data_extracts/wright2010_sand2010-0171.md`,
"§5.4 Vrancik windage formula").

This document is now a **direct** primary reference rather than an
indirect one — confidence grade upgrades from C to A once the
read-through is complete.

The PDF is **not** committed. Local copy:
`~/Downloads/Vrancik1968_NASA_TN_D4849.pdf` (749 KB, downloaded
2026-05-21 from NTRS direct).

## § Stub — read-through pending

Candidate uses:

- verbatim windage formula and discharge-coefficient correlation
  (currently referenced indirectly via Wright2010 §5.4)
- comparison of laminar / turbulent regimes that bound the
  applicability of the formula in our ROM physical-constraint module
- reference experimental data points for smooth cylindrical rotors
  vs. slotted alternators (7% max variance reported in abstract)

## § Pending follow-ups

- [ ] Read-through pass 1; transcribe the windage formula exactly.
- [ ] Compare against the form used by Wright2010 §5.4 — flag any
      transcription drift in that downstream citation.
- [ ] Update `docs/data_extracts/wright2010_sand2010-0171.md`
      "Vrancik windage formula" entry to point both to Wright2010
      §5.4 (where the formula is *applied*) and to this primary
      source (where it is *defined*). Confidence grade A.
- [ ] Implement as ROM soft-physical-constraint candidate per
      Wright2010 follow-up "Vrancik windage as ROM soft constraint".
