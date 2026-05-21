# Mixture Failure Envelopes

> **What is this?** Maps of where the open property stack (CoolProp's HEOS
> backend) succeeds or fails for sCO₂ + impurity mixtures, as a function of
> T and P. See [`docs/00_strategy.md` § Data Black Holes](../../docs/00_strategy.md#data-black-holes--survival-strategy)
> and [`docs/known_gaps.md#mixture-eos`](../../docs/known_gaps.md#mixture-eos).
>
> **What is this *not*?** Validated mixture property data. Every red cell
> below means *the open EOS could not converge* — it does not say what the
> true property at that point would be.

## Generated artifacts

| File | Mixture | Coverage |
|------|---------|----------|
| `co2_he_3pct.png` / `.csv` | CO₂ + Helium @ 3 mol% | T 290-800 K, P 5-25 MPa, 50×50 grid |
| `co2_h2o_1pct.png` / `.csv` | CO₂ + Water @ 1 mol% | T 290-700 K, P 5-25 MPa, 40×40 grid |

## Status legend (encoded as `status_code` in CSV)

| Code | Label | Engineering meaning |
|------|-------|---------------------|
| 0 | OK | HEOS converged; density/Cp callable |
| 1 | two-phase | Inside the pure-CO₂ saturation band — avoid in cycle design |
| 2 | near-critical | Within ±2 K / ±0.2 MPa of the CO₂ critical point — Cp diverges |
| 3 | solver failed | HEOS raised an exception — unsupported region for this stack |

## Reproduction

```bash
python -m src.sco2_failure_envelope \
    --impurity Helium --x-imp 0.03 --grid 50 \
    --out validation/failure_envelopes/co2_he_3pct.png
```

The CSV companion is written automatically next to the PNG. Both are
checked into the repo so reviewers can see the result without re-running
CoolProp; regenerate them after every CoolProp version bump.

## Headline finding (current snapshot, CoolProp 7.2.0)

- **CO₂ + 3 mol% Helium:** ~54% of the engineering T-P window cannot be
  evaluated. The open mixture stack is *not usable* for serious cycle
  studies of helium-tagged sCO₂ today.
- **CO₂ + 1 mol% Water:** ~0.1% failure. CoolProp's CO₂-H₂O HEOS is
  effectively production-grade across the cycle window.

> If you have measurement-grade mixture data inside the red regions of
> these maps — particularly for CO₂-He at high pressure — please open an
> issue on this repo. Filling the failure envelope is exactly the kind of
> contribution this project is built to receive.
