"""Plot Nusselt number vs Reynolds number from converged OpenFOAM cases.

Reference: docs/02_phase2_cfd_rom.md § 2.2 / 2.4

Reads the per-case `summary.csv` (one row per converged steady-state run)
under cases/case0X_*/run_*/ and produces a Nu–Re scatter overlay against
classical correlations.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def gnielinski(Re: np.ndarray, Pr: float = 0.85) -> np.ndarray:
    """Gnielinski correlation — smooth circular tube, Re > 3000.

    Returned for *reference only*; for PCHE zigzag/airfoil channels the
    correlation is documented to deviate significantly. The whole point of
    the project's CFD-trained ROM is to replace it.
    """
    f = (0.79 * np.log(Re) - 1.64) ** -2
    Nu = (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * np.sqrt(f / 8) * (Pr ** (2/3) - 1))
    return Nu


def collect_summaries(cases_root: Path) -> pd.DataFrame:
    rows = []
    for summary in cases_root.glob("case*/run_*/summary.csv"):
        df = pd.read_csv(summary)
        df["geometry"] = summary.parents[1].name.split("_")[1]
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases-root", type=Path, default=Path("cases"))
    ap.add_argument("--out", type=Path, default=Path("postProcessing/nu_vs_re.png"))
    args = ap.parse_args()

    df = collect_summaries(args.cases_root)
    if df.empty:
        print("No converged summary.csv files found — nothing to plot.")
        return

    fig, ax = plt.subplots(figsize=(8, 5.5))
    for geom, sub in df.groupby("geometry"):
        ax.scatter(sub["Re"], sub["Nu_avg"], s=30, label=f"CFD: {geom}")

    Re_ref = np.logspace(np.log10(3e3), np.log10(3e4), 50)
    ax.plot(
        Re_ref,
        gnielinski(Re_ref),
        "--",
        color="grey",
        label="Gnielinski (smooth tube; reference only)",
    )

    ax.set_xscale("log")
    ax.set_xlabel("Reynolds number")
    ax.set_ylabel("Average Nusselt number")
    ax.set_title("PCHE Nu vs Re — CFD vs Gnielinski")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
