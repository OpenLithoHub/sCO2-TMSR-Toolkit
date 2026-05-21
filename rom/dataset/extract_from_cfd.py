"""Extract (T_in, P_in, mdot, geom) -> (Nu_avg, dp_total) from CFD output.

Reference: docs/02_phase2_cfd_rom.md § 2.6.2

This script walks `cases/case0X_*/run_*` directories of converged
OpenFOAM steady-state results and produces `rom/dataset/training_set.csv`.

Until real CFD runs land, the parser fields are filled with NaN and the
script reports zero rows — that is the expected state. See `--synthetic`
flag to generate a small in-memory dataset for end-to-end pipeline tests.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


GEOM_MAP = {"straight": 0, "zigzag": 1, "airfoil": 2}


@dataclass
class Sample:
    T_in_K: float
    P_in_Pa: float
    mass_flow_kg_s: float
    geometry_id: int
    Nu_avg: float
    dp_total_Pa: float


def parse_case(case_dir: Path) -> Sample | None:
    """Parse a single converged steady-state run directory.

    Returns None if the directory is not yet a finished run. Real
    OpenFOAM parsing is left as a future TODO; this skeleton expects
    `summary.csv` (a single-row CSV with the columns below) produced by
    a per-case post-processing pass.
    """
    summary = case_dir / "summary.csv"
    if not summary.exists():
        return None

    row = pd.read_csv(summary).iloc[0]
    geom_token = case_dir.parent.name.split("_")[1]   # e.g. "straight"
    return Sample(
        T_in_K=float(row["T_in_K"]),
        P_in_Pa=float(row["P_in_Pa"]),
        mass_flow_kg_s=float(row["mass_flow_kg_s"]),
        geometry_id=GEOM_MAP[geom_token],
        Nu_avg=float(row["Nu_avg"]),
        dp_total_Pa=float(row["dp_total_Pa"]),
    )


def collect_all(cases_root: Path) -> pd.DataFrame:
    rows: list[Sample] = []
    skipped: list[Path] = []
    for case in sorted(cases_root.glob("case*/run_*")):
        s = parse_case(case)
        if s is None:
            skipped.append(case)
        else:
            rows.append(s)

    df = pd.DataFrame([s.__dict__ for s in rows])
    print(f"Extracted {len(rows)} samples; skipped {len(skipped)}")
    return df


def synthetic_dataset(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """Synthetic samples — physically plausible but not validated.

    Use only for end-to-end pipeline smoke tests. Do NOT publish a ROM
    trained on this.
    """
    rng = np.random.default_rng(seed)
    T_in = rng.uniform(305.0, 823.0, n)
    P_in = rng.uniform(7.5e6, 25e6, n)
    mdot = rng.uniform(0.05, 0.5, n)
    geom = rng.integers(0, 3, n)

    # Loosely physical surrogates: Nu ~ 0.023 Re^0.8 Pr^0.4 (Dittus-Boelter ballpark)
    # Re ~ 4*mdot / (pi * D * mu); fold constants into a coefficient
    Nu_avg = 0.023 * (mdot * 1e4) ** 0.8 + 5.0 * geom + rng.normal(0, 2, n)
    dp_total = 5e3 * (mdot ** 1.8) + 200.0 * geom + rng.normal(0, 50, n)

    return pd.DataFrame({
        "T_in_K": T_in,
        "P_in_Pa": P_in,
        "mass_flow_kg_s": mdot,
        "geometry_id": geom,
        "Nu_avg": np.maximum(Nu_avg, 1.0),
        "dp_total_Pa": np.maximum(dp_total, 1.0),
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases-root", type=Path, default=Path("cases"))
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("rom/dataset/training_set.csv"),
    )
    ap.add_argument(
        "--synthetic",
        type=int,
        default=0,
        help="If >0, skip CFD parsing and emit N synthetic samples for pipeline tests.",
    )
    args = ap.parse_args()

    if args.synthetic > 0:
        df = synthetic_dataset(args.synthetic)
        print(f"⚠  Synthetic dataset: {len(df)} samples — for pipeline test only.")
    else:
        df = collect_all(args.cases_root)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
