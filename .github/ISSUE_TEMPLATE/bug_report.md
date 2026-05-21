---
name: Bug report
about: Report a problem in the toolkit code, tests, or documentation
title: "[BUG] "
labels: bug
assignees: ''
---

## Environment

- CoolProp version (`python -c "import CoolProp; print(CoolProp.__version__)"`):
- Python version:
- OS:
- Toolkit commit / release tag:

## What did you try?

A minimal reproducible example — preferably 10–20 lines of Python.

```python
import CoolProp.CoolProp as CP
# ...
```

## What did you expect?

E.g. "density at 305.4 K, 7.69 MPa to be within 5 % of the SNL 2010 Wright report value of 632 kg/m³".

## What happened?

Actual output, error, or plot. Attach figures if relevant.

## Have you read the docs?

- [ ] Checked `docs/01_phase1_properties.md` for the relevant section
- [ ] Searched existing issues
- [ ] If this is a CoolProp accuracy issue, also checked the CoolProp upstream issue tracker
