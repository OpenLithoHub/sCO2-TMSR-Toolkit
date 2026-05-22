"""Validate CoolProp sCO2 properties against SNL / BYU benchmark CSVs.

Reference: docs/01_phase1_properties.md § 1.6 + CI/CD section.
           docs/known_gaps.md#snl-step-rows (Gap 5).

This script powers the "SNL benchmark" CI step. It loads a public-source
benchmark CSV, calls CoolProp at each row's inlet (T, P), and reports the
relative error against a reported quantity. CI fails if any row exceeds the
configured tolerance.

Two checks are supported via ``--check``:

* ``rho`` (default) — validates density against ``rho_inlet_measured``. Used
  by SNL Wright2010 rows and the self-consistency CSV. Rows with a blank
  ``rho_inlet_measured`` are skipped (they remain in the CSV for downstream
  state logging).
* ``h`` — validates enthalpy against ``h_inlet_measured_J_kg``. Used by the
  Held2025 BYU pilot rows where the source paper tabulates h but not ρ. CSVs
  whose schema predates this column (SNL_compressor_data.csv,
  coolprop_self_consistency.csv) are skipped with a notice rather than
  erroring, so the same validator step can run across every benchmark file.

``--check`` also accepts a comma-separated list (e.g. ``--check rho,h``).
Each check is run sequentially against the same CSV; the script exits
non-zero if *any* check fails. CSVs lacking a check's column are skipped
(not failed), so a single CI invocation can fan out across mixed-schema
benchmark files.

The shipping CSVs are still partial — see validation/experimental_data/
data_sources.md for the transcription rules.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import CoolProp.CoolProp as CP
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sco2_warnings import warn_placeholder  # noqa: E402


# --- Per-check configuration ----------------------------------------------

_CHECK_SPECS = {
    "rho": {
        "column": "rho_inlet_measured",
        "coolprop_key": "D",
        "label": "density",
        "unit": "kg/m^3",
    },
    "h": {
        "column": "h_inlet_measured_J_kg",
        "coolprop_key": "H",
        "label": "enthalpy",
        "unit": "J/kg",
    },
}


def _load_benchmark(path: Path, column: str, check: str) -> pd.DataFrame | None:
    df = pd.read_csv(path, comment="#")
    if column not in df.columns:
        # Schema predates this check — return None so the caller can decide
        # whether to skip (CI parity) or error (single-CSV invocation).
        print(
            f"[validate_against_sandia] {path}: no '{column}' column "
            f"(schema predates --check {check}) — skipping."
        )
        return None
    return df


def validate(
    path: Path, tolerance_pct: float, fluid: str = "CO2", check: str = "rho"
) -> int:
    spec = _CHECK_SPECS[check]
    df = _load_benchmark(path, spec["column"], check)
    if df is None:
        return 0

    measured = df.dropna(subset=[spec["column"]])
    if measured.empty:
        warn_placeholder(
            "snl-step-rows",
            f"{path.name} contains no verified {spec['label']} rows — CI is "
            "exercising the validation pipeline but skipping all assertions",
        )
        print(
            f"[validate_against_sandia] {path}: no verified {spec['label']} "
            "rows — skipping."
        )
        return 0

    failures: list[tuple[int, float]] = []
    print(
        f"[validate_against_sandia] {path}: {len(measured)} verified "
        f"{spec['label']} rows"
    )
    print(f"  Check: {spec['label']} ({spec['unit']})")
    print(f"  Tolerance: {tolerance_pct:.2f}%")
    for idx, row in measured.iterrows():
        calc = CP.PropsSI(
            spec["coolprop_key"],
            "T",
            row["T_inlet_K"],
            "P",
            row["P_inlet_Pa"],
            fluid,
        )
        ref = float(row[spec["column"]])
        rel_err_pct = 100.0 * abs(calc - ref) / abs(ref)
        status = "OK " if rel_err_pct < tolerance_pct else "FAIL"
        print(
            f"  [{status}] T={row['T_inlet_K']:.2f} K  "
            f"P={row['P_inlet_Pa']:.3e} Pa | "
            f"ref={ref:.4g}  CoolProp={calc:.4g}  err={rel_err_pct:.3f}%"
        )
        if rel_err_pct >= tolerance_pct:
            failures.append((int(idx), rel_err_pct))

    if failures:
        print(f"\n{len(failures)} row(s) exceeded tolerance:")
        for idx, err in failures:
            print(f"  row {idx}: {err:.3f}%")
        return 1
    print("All rows within tolerance.")
    return 0


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Benchmark CoolProp vs SNL/BYU CSV.")
    p.add_argument(
        "--data",
        type=Path,
        default=Path("validation/experimental_data/SNL_compressor_data.csv"),
        help="Benchmark CSV path",
    )
    p.add_argument(
        "--tolerance",
        type=float,
        default=5.0,
        help="Maximum allowed relative error (%%)",
    )
    p.add_argument(
        "--check",
        default="rho",
        help=(
            "Quantity to validate. Single value (rho|h) or comma-separated "
            "list (e.g. rho,h). Default: rho."
        ),
    )
    p.add_argument("--fluid", type=str, default="CO2")
    return p


def _parse_checks(spec: str) -> list[str]:
    checks = [c.strip() for c in spec.split(",") if c.strip()]
    if not checks:
        raise SystemExit("--check must name at least one quantity")
    unknown = [c for c in checks if c not in _CHECK_SPECS]
    if unknown:
        raise SystemExit(
            f"--check: unknown quantity {unknown!r}. "
            f"Valid: {sorted(_CHECK_SPECS)}"
        )
    return checks


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    checks = _parse_checks(args.check)
    rc = 0
    for check in checks:
        rc |= validate(args.data, args.tolerance, args.fluid, check)
    return rc


if __name__ == "__main__":
    sys.exit(main())
