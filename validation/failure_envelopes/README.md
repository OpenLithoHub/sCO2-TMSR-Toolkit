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
| `co2_he_1pct.png` / `.csv` | CO₂ + Helium @ 1 mol% | T 290-800 K, P 5-25 MPa, 50×50 grid |
| `co2_he_3pct.png` / `.csv` | CO₂ + Helium @ 3 mol% | T 290-800 K, P 5-25 MPa, 50×50 grid |
| `co2_he_5pct.png` / `.csv` | CO₂ + Helium @ 5 mol% | T 290-800 K, P 5-25 MPa, 50×50 grid |
| `co2_h2o_0p5pct.png` / `.csv` | CO₂ + Water @ 0.5 mol% | T 290-700 K, P 5-25 MPa, 40×40 grid |
| `co2_h2o_1pct.png` / `.csv` | CO₂ + Water @ 1 mol% | T 290-700 K, P 5-25 MPa, 40×40 grid |
| `co2_h2o_2pct.png` / `.csv` | CO₂ + Water @ 2 mol% | T 290-700 K, P 5-25 MPa, 40×40 grid |

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

To regenerate **every** envelope in one shot (e.g. after a CoolProp
version bump), use the wrapper script — it pins grid sizes and T/P
ranges so the artifacts here are reproducible across machines:

```bash
bash validation/failure_envelopes/regenerate_all.sh
```

After regeneration, diff the resulting CSVs against the previous
commit. A status-cell delta indicates the new CoolProp release
shifted the failure boundary; that delta is itself worth reporting.

Use `diff_status_codes.py` for a structured cell-by-cell comparison:

```bash
# Diff working tree against the committed snapshot
python validation/failure_envelopes/diff_status_codes.py \
    validation/failure_envelopes/co2_he_3pct.csv --git-ref HEAD

# Or compare two arbitrary snapshots
python validation/failure_envelopes/diff_status_codes.py \
    new.csv --old prior.csv
```

Exits 0 if no cells flipped, 1 if any flipped (with a summary table),
2 if the two grids have incompatible (T, P) shape (e.g. one was
regenerated with a different `--grid`).

## Headline finding (current snapshot, CoolProp 7.2.0)

CO₂ + Helium failure rate scales sharply with He content; the open
mixture stack collapses well before nuclear-relevant impurity levels:

| Mixture | OK cells | Solver-failed cells | Failure % |
|---------|----------|---------------------|-----------|
| CO₂ + 1 mol% He | 1500 | 1000 | **40.0 %** |
| CO₂ + 3 mol% He | 1140 | 1342 | **53.7 %** |
| CO₂ + 5 mol% He |  944 | 1556 | **62.2 %** |

CO₂ + H₂O is effectively production-grade across the cycle window at
all three impurity levels probed:

| Mixture | OK cells | Solver-failed cells | Failure % |
|---------|----------|---------------------|-----------|
| CO₂ + 0.5 mol% H₂O | 1599 | 1 | **0.06 %** |
| CO₂ + 1 mol% H₂O   | 1599 | 1 | **0.06 %** |
| CO₂ + 2 mol% H₂O   | 1594 | 6 | **0.38 %** |

Cell counts come straight from the `status_code` column of each
companion CSV. Update this table whenever the artifacts are regenerated.

> If you have measurement-grade mixture data inside the red regions of
> these maps — particularly for CO₂-He at high pressure — please open an
> issue on this repo. Filling the failure envelope is exactly the kind of
> contribution this project is built to receive.
