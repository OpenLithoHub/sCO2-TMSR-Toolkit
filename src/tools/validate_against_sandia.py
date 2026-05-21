"""Validate CoolProp sCO2 properties against SNL / STEP benchmark CSVs.

Reference: docs/01_phase1_properties.md § 1.6 + CI/CD section.

This script powers the "SNL benchmark" CI step. It loads the public-source
benchmark CSV, calls CoolProp at each row's (T, P), and reports the relative
density error. CI fails if any row exceeds the configured tolerance.

The shipping CSVs are placeholders — see validation/experimental_data/
data_sources.md for the transcription rules. When the CSV has no measured
data rows the script prints a notice and exits 0 so CI does not break before
the data is verified.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import CoolProp.CoolProp as CP
import pandas as pd

# Make the src/ package importable regardless of how the script is launched.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sco2_warnings import warn_placeholder  # noqa: E402


def _load_benchmark(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    if "rho_inlet_measured" not in df.columns:
        raise ValueError(
            f"{path} missing rho_inlet_measured column — check schema"
        )
    return df


def validate(path: Path, tolerance_pct: float, fluid: str = "CO2") -> int:
    df = _load_benchmark(path)
    measured = df.dropna(subset=["rho_inlet_measured"])
    if measured.empty:
        warn_placeholder(
            "snl-step-rows",
            f"{path.name} contains no verified rows — CI is exercising the "
            "validation pipeline but skipping all assertions",
        )
        print(f"[validate_against_sandia] {path}: no verified rows — skipping.")
        return 0

    failures: list[tuple[int, float]] = []
    print(f"[validate_against_sandia] {path}: {len(measured)} verified rows")
    print(f"  Tolerance: {tolerance_pct:.2f}%")
    for idx, row in measured.iterrows():
        rho_calc = CP.PropsSI(
            "D", "T", row["T_inlet_K"], "P", row["P_inlet_Pa"], fluid
        )
        rho_ref = float(row["rho_inlet_measured"])
        rel_err_pct = 100.0 * abs(rho_calc - rho_ref) / rho_ref
        status = "OK " if rel_err_pct < tolerance_pct else "FAIL"
        print(
            f"  [{status}] T={row['T_inlet_K']:.2f} K  P={row['P_inlet_Pa']:.3e} Pa "
            f"| ref={rho_ref:.2f}  CoolProp={rho_calc:.2f}  err={rel_err_pct:.2f}%"
        )
        if rel_err_pct >= tolerance_pct:
            failures.append((int(idx), rel_err_pct))

    if failures:
        print(f"\n{len(failures)} row(s) exceeded tolerance:")
        for idx, err in failures:
            print(f"  row {idx}: {err:.2f}%")
        return 1
    print("All rows within tolerance.")
    return 0


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Benchmark CoolProp vs SNL/STEP CSV.")
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
        help="Maximum allowed relative density error (%%)",
    )
    p.add_argument("--fluid", type=str, default="CO2")
    return p


if __name__ == "__main__":
    args = _build_argparser().parse_args()
    rc = validate(args.data, args.tolerance, args.fluid)
    sys.exit(rc)
