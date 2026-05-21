# Contributing to sCO2-TMSR-Toolkit

Thank you for considering a contribution. This project is part of the
[OpenLithoHub](https://github.com/OpenLithoHub) family and follows its
licensing model: **Apache-2.0 for code** + **CC BY-SA 4.0 for documentation**.

By submitting a contribution, you agree that:

- Your code contributions are licensed under the Apache License 2.0.
- Your documentation contributions are licensed under CC BY-SA 4.0.
- You have the right to submit the work under those licenses.

For non-trivial contributions we may ask for an Individual or Corporate CLA;
see the OpenLithoHub family templates if/when this becomes applicable.

---

## Workflow

```
1. Open an Issue first (Feature Request / Discussion)
   - Describe the engineering context (e.g., "PCHE inlet validation")
   - Describe the specific problem
   - Describe the artifact you plan to write
   - Ask: "Does this direction look valuable? Known pitfalls?"

2. Wait for response (3–14 days typical)

3. Fork → feature branch → PR
   - Reference the Issue: "Closes #N" in the PR description
   - Keep PRs focused; one logical change per PR
```

---

## Local development

```bash
# Clone
git clone https://github.com/OpenLithoHub/sCO2-TMSR-Toolkit.git
cd sCO2-TMSR-Toolkit

# Install dev dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Run the test suite
pytest tests/ -v

# Run the property explorer (writes sco2_cp_pseudocritical.png)
python src/sco2_property_explorer.py

# Generate a small LUT for OpenFOAM
python src/tools/export_lut.py --n-T 20 --n-P 10

# Launch the Streamlit app
streamlit run app/streamlit_app.py
```

---

## Coding conventions

- **Documentation per component:**
  - Equation sources and literature references (cite — do not hand-wave)
  - Applicable range (e.g., "Gnielinski valid for Re > 3000")
  - Known limitations (e.g., "not applicable to two-phase flow")
  - Validation status: *unvalidated* / *compared against literature* / *compared against experimental data*
- **Tests:** every new function in `src/` should have at least one test in `tests/`.
- **Python:** standard `pep8`-ish via PEP 8; prefer type hints in new code.
- **Modelica:** every component must have an `annotation(Documentation(...))` block
  describing scope, references, and limitations.

---

## Data and copyright

```
✅ Permitted:
  - NIST WebBook public data
  - Tabulated data from published papers (cite source)
  - IAEA nuclear database (free access agreement)

❌ Not permitted:
  - Full REFPROP source code (commercial)
  - Unpublished experimental data from national labs
  - Raw research-group data without authorization

Grey area (handle carefully):
  - Data points digitized from paper figures
    → Note "digitized from ref [x]; contact us if this raises concerns"
```

When adding to `validation/experimental_data/`, also update
`validation/experimental_data/data_sources.md` with provenance.

---

## Issue triage SLO

- **Any Issue** → first response within 48 hours (critical for trust).
- **Tag** issues by phase: `phase-1-properties`, `phase-2-cfd-rom`,
  `phase-3-modelica`, `docs`, `infra`.

---

## Commit message style

```
<area>: <imperative summary>

Optional body explaining the *why*. Reference issues with "Closes #N".
```

Examples:
```
properties: add pseudo-critical line search with explicit T range
ci: pin CoolProp ≥ 7.1 in matrix
docs: clarify ROM accuracy boundary for two-phase region
```
