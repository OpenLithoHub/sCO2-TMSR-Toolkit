# sCO₂-TMSR-Toolkit — Living Documentation

This Jupyter Book is the *researcher-facing* companion to the toolkit.
Where the [Streamlit app](https://share.streamlit.io) lets an engineer
click through a property field in 30 seconds, this book lays out the
**physics, equations, code, and validation** behind every component
in a form you can read, re-run, or fork.

## How to use this book

| Reading mode | What you get |
|--------------|--------------|
| **Read online** | All notebooks pre-rendered with figures and equations |
| **Run in Binder** | Click the rocket icon → live Python kernel in your browser |
| **Open in Colab** | Run on Google's free GPU-backed runtime |
| **Run locally** | `git clone` the repo → `jupyter-book build book/` |

## Notebook structure convention

Every notebook follows the same four-section pattern, taken from
`docs/03_phase3_modelica.md` § 3.8:

1. **Problem** — what physical or engineering question motivates the work
2. **Equations** — the mathematical model, with literature references
3. **Code** — runnable cells using `CoolProp ≥ 7.1`
4. **Conclusion** — engineering implication or validation status

## Citing this work

Every notebook can be cited individually via the project Zenodo DOI
(see [README.md § Citation](https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit#citation)).

## Coverage

| Chapter | Phase mapping | Status |
|---------|---------------|--------|
| 01 — Pseudo-critical line | docs/01_phase1 § 1.2 | Skeleton |
| 02 — Mixture effects | docs/01_phase1 § 1.3 | Skeleton |
| 03 — T-s diagram | docs/01_phase1 + docs/03_phase3 cycles | Skeleton |
| 04 — SNL validation | docs/01_phase1 § 1.6 | Awaits SNL CSV transcription |

> **Note:** This book is part of the **v1.3+** living documentation system.
> Content will expand as Phase 1 → Phase 3 deliverables ship.
