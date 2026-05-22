#!/usr/bin/env bash
# Regenerate every failure-envelope artifact in this directory.
#
# Run after a CoolProp version bump (or any time the EOS backend
# changes). Diff the resulting CSVs against the previous commit:
# any non-trivial status_code delta is itself a finding worth
# reporting in docs/known_gaps.md#mixture-eos.
#
# Run from the repository root:
#     bash validation/failure_envelopes/regenerate_all.sh

set -euo pipefail

OUT_DIR="validation/failure_envelopes"
PY="${PYTHON:-python3}"

# Helium sweeps — full nuclear-cycle T window.
$PY -m src.sco2_failure_envelope --impurity Helium --x-imp 0.01 \
    --grid 50 --out "${OUT_DIR}/co2_he_1pct.png"
$PY -m src.sco2_failure_envelope --impurity Helium --x-imp 0.03 \
    --grid 50 --out "${OUT_DIR}/co2_he_3pct.png"
$PY -m src.sco2_failure_envelope --impurity Helium --x-imp 0.05 \
    --grid 50 --out "${OUT_DIR}/co2_he_5pct.png"

# Water sweeps — capped at 700 K because CoolProp HEOS for CO2-H2O
# tightens at higher T and the 800 K cells add no information.
$PY -m src.sco2_failure_envelope --impurity Water --x-imp 0.005 \
    --T-max 700 --grid 40 --out "${OUT_DIR}/co2_h2o_0p5pct.png"
$PY -m src.sco2_failure_envelope --impurity Water --x-imp 0.01 \
    --T-max 700 --grid 40 --out "${OUT_DIR}/co2_h2o_1pct.png"
$PY -m src.sco2_failure_envelope --impurity Water --x-imp 0.02 \
    --T-max 700 --grid 40 --out "${OUT_DIR}/co2_h2o_2pct.png"

echo
echo "All envelopes regenerated. Update the headline-finding table in"
echo "${OUT_DIR}/README.md if any failure percentages shifted."
