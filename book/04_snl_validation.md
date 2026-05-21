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

The DOE STEP Phase 1 demonstration project added a second public source
(simple cycle, ~500 °C); STEP Phase 2 (RCBC, ~715 °C) data is *not* yet
public as of 2026.

This notebook is the public-facing place where the project's
"compared-against-experiment" evidence lives.

## 4.2 Status

> **Current status:** the SNL/STEP CSVs in
> `validation/experimental_data/` are placeholders. Until each row is
> transcribed from the original OSTI / DOE report and checked against the
> source by a named reviewer, **this notebook only exercises the
> pipeline**, not the validation claim.

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

CI fails if any verified row exceeds **5 % relative density error**.
Tighten the tolerance only after the per-row uncertainty in the source
report is documented.

## 4.6 Once data is verified

When `SNL_compressor_data.csv` (and / or `STEP_phase1_data.csv`) is
populated:

1. Move the row from comment-only placeholder lines to active CSV rows
2. Append a citation block in
   `validation/experimental_data/data_sources.md`
3. Re-run this notebook locally — the CI step
   `python src/tools/validate_against_sandia.py` will start asserting

## 4.7 References

- Wright, S. A. et al. (2010 et seq.), Sandia Laboratory technical reports
  on the sCO₂ test loop — OSTI public collection
- DOE STEP Demonstration Project — Phase 1 reports (Southwest Research Institute)
- See `book/references.bib` for the canonical citation keys
