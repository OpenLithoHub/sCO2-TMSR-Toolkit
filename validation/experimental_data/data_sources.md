# Experimental Data Sources

This directory will hold tabulated experimental benchmark data referenced from
public sources. **Each row in every CSV must be traceable to a public,
citable report.** When adding data, append a section here with:

- Source (paper title, lab report number, DOI/URL)
- Original data form (table number / figure number)
- Whether values were transcribed from a table or digitized from a plot
- Date accessed

---

## Sandia National Laboratories (SNL) sCO2 test loop

**Status:** *not yet populated.* Placeholders for SNL benchmark points exist in
`tests/test_sco2_properties.py` and must be replaced with verified values from
the original Wright et al. reports before declaring "validated against
experimental data".

- Search OSTI: `supercritical CO2 test loop Sandia`
- Key series: Wright, Conboy, Pickard et al. (2010–2016)

Add a CSV here named `SNL_compressor_data.csv` with columns:
`T_inlet_K, P_inlet_Pa, T_outlet_K, P_outlet_Pa, efficiency_measured, source_ref`

---

## DOE STEP demonstration project

**Status:** *not yet populated.*

- **Phase 1 (simple cycle, ~500 °C):** public reports released — usable.
- **Phase 2 (RCBC, ~715 °C):** in progress as of 2025; data not yet public.
  Do not cite "715 °C RCBC operating data" as available.

Add `STEP_phase1_data.csv` with columns aligned to the SNL CSV when ready.

---

## What is *not* permitted here

- Full REFPROP source code (commercial)
- Unpublished experimental data from national labs
- Raw research-group data without explicit authorization

For digitized data points (extracted from published plots), add a clear note:
"digitized from ref [x]; contact us if this raises concerns".
