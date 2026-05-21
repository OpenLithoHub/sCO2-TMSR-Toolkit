"""Validate CFD summary outputs against published experimental data.

Reference: docs/02_phase2_cfd_rom.md § 2.2

Loads the experimental benchmark CSVs from `validation/experimental_data/`
and compares the closest CFD operating point in `cases/case0X_*/run_*/summary.csv`.

Until either dataset (CFD summaries or SNL/STEP transcribed values) is
populated, the script exits 0 with an informational message — same policy
as `src/tools/validate_against_sandia.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def nearest_cfd(df_cfd: pd.DataFrame, T: float, P: float) -> pd.Series | None:
    if df_cfd.empty:
        return None
    d = (
        ((df_cfd["T_in_K"] - T) / max(T, 1)) ** 2
        + ((df_cfd["P_in_Pa"] - P) / max(P, 1)) ** 2
    )
    return df_cfd.iloc[int(np.argmin(d.to_numpy()))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfd-root", type=Path, default=Path("cases"))
    ap.add_argument(
        "--exp",
        type=Path,
        default=Path("validation/experimental_data/SNL_compressor_data.csv"),
    )
    ap.add_argument("--tol-pct", type=float, default=10.0)
    args = ap.parse_args()

    cfd_rows = []
    for s in args.cfd_root.glob("case*/run_*/summary.csv"):
        cfd_rows.append(pd.read_csv(s))
    df_cfd = pd.concat(cfd_rows, ignore_index=True) if cfd_rows else pd.DataFrame()

    df_exp = pd.read_csv(args.exp, comment="#")
    df_exp = df_exp.dropna(subset=["rho_inlet_measured"])

    if df_cfd.empty or df_exp.empty:
        print(
            f"validate_against_exp: cfd rows={len(df_cfd)}, exp rows={len(df_exp)} "
            "— skipping (need both)"
        )
        return 0

    failures: list[str] = []
    for _, exp in df_exp.iterrows():
        match = nearest_cfd(df_cfd, exp.T_inlet_K, exp.P_inlet_Pa)
        if match is None:
            continue
        # If the CFD summary recorded inlet density, compare.
        if "rho_in_kg_m3" not in match:
            continue
        err_pct = (
            100
            * abs(match["rho_in_kg_m3"] - exp.rho_inlet_measured)
            / exp.rho_inlet_measured
        )
        status = "OK " if err_pct < args.tol_pct else "FAIL"
        print(
            f"  [{status}] T_exp={exp.T_inlet_K:.1f} K  err={err_pct:.2f}%"
        )
        if err_pct >= args.tol_pct:
            failures.append(f"row at T={exp.T_inlet_K} K: {err_pct:.2f}%")

    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
