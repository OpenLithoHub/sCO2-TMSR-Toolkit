## Summary

One sentence: what does this PR change?

## Motivation

Why is this change needed? Link to an Issue if one exists ("Closes #NN").

## Changes

- [ ] Code changes (list files)
- [ ] Test changes (added / updated)
- [ ] Documentation changes (`docs/`, `README.md`, `book/`)

## Validation

How did you verify the change is correct?

- [ ] `pytest tests/ -v` passes locally
- [ ] If touching property calculations: compared against CoolProp reference values
- [ ] If touching CFD: documented mesh quality, residuals, and y+ where applicable
- [ ] If touching Modelica: ran `omc` (or noted which OpenModelica version)
- [ ] Updated relevant `docs/0X_*.md` section if behaviour or scope changed

## Author checklist

- [ ] PR title is clear and English-language (CoolProp / OpenModelica are international projects)
- [ ] Added myself to NOTICE if this is my first contribution
- [ ] No experimental data added without source citation in `validation/experimental_data/data_sources.md`
- [ ] No file >50 MB committed directly (use Git LFS or Zenodo per `docs/02 § 2.5.1`)
