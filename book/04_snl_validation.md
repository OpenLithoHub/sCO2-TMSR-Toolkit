---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# 4. Validation Against SNL Public Data

## 4.1 Problem statement

A property library is only as credible as the experimental data it has
been compared against. Sandia National Laboratories (SNL) operated the
world's first sCO₂ test loop (~10 MWe) and published compressor inlet/
outlet measurements in OSTI public reports (Wright et al., 2010–2016).

The DOE STEP Phase 1 demonstration project (10 MWe class, Southwest
Research Institute) is positioned as a future second public source;
its final report is not yet released as of 2026. STEP Phase 2 (RCBC,
~715 °C) data is *not* yet public.

A separate, smaller pilot programme — the BYU/Echogen 1.26 MWth loop
at the San Rafael Energy Research Center, DOE FE award DE-FE0031928 —
is now indexed in this repo (`BYU_pilot_data.csv`, source
`Held2025_BYU_pilot`) and exercises CoolProp enthalpy across a wider
T window (20–600 °C) than the SNL data alone covers.

This notebook is the public-facing place where the project's
"compared-against-experiment" evidence lives.

## 4.2 Status

> **Current status:** the SNL CSV in
> `validation/experimental_data/SNL_compressor_data.csv` ships with 9
> single-pass transcribed rows (8 from Wright2010 SAND2010-0171 + 1
> modelled pair from Wright2011 SAND2010-8840). The BYU pilot CSV
> (`BYU_pilot_data.csv`) ships with 6 component-pair rows from
> Held2025 Table 2; CoolProp enthalpy agrees with the paper's
> tabulated h to ≤ 0.03 % at all 10 state points (cross-check
> documented in `docs/data_extracts/held2025_byu_pilot.md`).
> No STEP Phase 1 / Phase 2 rows are present — the final report is
> not yet released.

This is the same caution policy applied in `tests/test_sco2_properties.py`
(see the `pytest.mark.skipif` guards) and `src/tools/validate_against_sandia.py`.

## 4.3 Loading the placeholder dataset

```{code-cell} ipython3
import sys
from pathlib import Path
import pandas as pd

repo_root = Path("..").resolve()
csv_path = repo_root / "validation/experimental_data/SNL_compressor_data.csv"

df = pd.read_csv(csv_path, comment="#")
print(f"Loaded {len(df)} rows from {csv_path.name}")
print(df.head())
```

## 4.4 Calling CoolProp at each row

```{code-cell} ipython3
import CoolProp.CoolProp as CP

verified = df.dropna(subset=["rho_inlet_measured"])
if len(verified) == 0:
    print("No verified rows yet — see data_sources.md transcription rules.")
else:
    rows = []
    for _, r in verified.iterrows():
        rho_calc = CP.PropsSI("D", "T", r.T_inlet_K, "P", r.P_inlet_Pa, "CO2")
        err_pct  = 100.0 * (rho_calc - r.rho_inlet_measured) / r.rho_inlet_measured
        rows.append({
            "T_K":     r.T_inlet_K,
            "P_MPa":   r.P_inlet_Pa / 1e6,
            "ref":     r.rho_inlet_measured,
            "CoolProp": rho_calc,
            "err_pct": err_pct,
        })
    print(pd.DataFrame(rows).to_string(index=False))
```

## 4.5 Acceptance criterion

CI gates two checks side by side:

* `--check rho` against `SNL_compressor_data.csv` — fails if any verified
  row exceeds **5 % relative density error**. Tighten the tolerance only
  after the per-row uncertainty in the source report is documented.
* `--check h` against `BYU_pilot_data.csv` — fails if any row exceeds
  **1 % relative enthalpy error**. The Held2025 paper rounds h to
  0.1 kJ/kg, so 1 % is conservative; current CoolProp 7.2.0 sits at
  ≤ 0.012 % across all six rows.

## 4.6 Once data is verified

When `SNL_compressor_data.csv` or `BYU_pilot_data.csv` gains additional
rows (or a future `STEP_phase1_data.csv` is created when the DOE STEP
Phase 1 final report is released):

1. Move the row from comment-only placeholder lines to active CSV rows
2. Append a citation block in
   `validation/experimental_data/data_sources.md`
3. Re-run this notebook locally — the CI step
   `python -m src.tools.validate_against_sandia` (with the appropriate
   `--check rho|h` and `--data` flags) will start asserting on the new
   rows. The validator gracefully skips legacy CSVs whose schema
   predates the requested column.

## 4.7 References

- Wright, S. A. et al. (2010, 2011), Sandia Laboratory technical reports
  on the sCO₂ test loop — OSTI public collection
- Held, T. J. et al. (2025), *Extended Duration Operation of a Pilot-Scale
  sCO₂ Test Loop* — ASME GT2025-152150, BYU/Echogen 1.26 MWth pilot at
  the San Rafael Energy Research Center (DOE FE award DE-FE0031928)
- DOE STEP Demonstration Project — Phase 1 final report not yet released
- See `book/references.bib` for the canonical citation keys
