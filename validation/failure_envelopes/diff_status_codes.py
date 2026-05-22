"""Diff status_code columns between two failure-envelope CSV snapshots.

Reference: docs/known_gaps.md#mixture-eos (Gap 3)
           validation/failure_envelopes/README.md "Reproduction"

After a CoolProp version bump, ``regenerate_all.sh`` rewrites every
envelope CSV in place. This tool compares the new artifact against a
prior snapshot and reports cells whose ``status_code`` flipped.

Two input modes:

* Two explicit CSVs — ``--old prior.csv --new current.csv``
* Git-anchored — ``--git-ref HEAD validation/failure_envelopes/co2_he_3pct.csv``
  reads the file as it stood at ``HEAD`` (or any rev) and diffs against
  the working-tree copy.

Exit status:
    0  no flips
    1  one or more cells flipped status_code
    2  inputs are non-comparable (different (T,P) grid)

The flip table lines up cleanly with the headline finding in
``README.md`` so the reviewer can see exactly which cells migrated
across status codes after the EOS update.
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path

import pandas as pd

STATUS_LABELS = {
    0: "OK",
    1: "two-phase",
    2: "near-critical",
    3: "solver failed",
}


def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _load_from_git(rev: str, path: Path) -> pd.DataFrame:
    """Read ``path`` as of git rev ``rev`` without touching the working tree."""
    result = subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"git show {rev}:{path} failed: {result.stderr.strip()}"
        )
    return pd.read_csv(io.StringIO(result.stdout))


def _key(df: pd.DataFrame) -> pd.DataFrame:
    return df[["T_K", "P_Pa"]].round({"T_K": 6, "P_Pa": 0})


def diff(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of cells whose status_code flipped.

    Raises if the (T, P) grids do not align — an envelope regenerated
    with a different ``--grid`` or ``--T-max`` is not comparable cell
    by cell, and silently masking that would hide the real change.
    """
    old_key = _key(old)
    new_key = _key(new)
    if not old_key.equals(new_key):
        raise ValueError(
            f"(T, P) grids differ: old={len(old)} rows, new={len(new)} rows. "
            "Regenerate both snapshots with the same --grid / --T-max."
        )

    merged = old.merge(
        new,
        on=["T_K", "P_Pa"],
        suffixes=("_old", "_new"),
    )
    flipped = merged[merged["status_code_old"] != merged["status_code_new"]].copy()
    flipped["from"] = flipped["status_code_old"].map(STATUS_LABELS)
    flipped["to"] = flipped["status_code_new"].map(STATUS_LABELS)
    return flipped[["T_K", "P_Pa", "status_code_old", "status_code_new", "from", "to"]]


def _summarise(flipped: pd.DataFrame) -> str:
    if flipped.empty:
        return "no status_code flips"
    counts = (
        flipped.groupby(["from", "to"]).size().reset_index(name="cells")
        .sort_values("cells", ascending=False)
    )
    lines = [f"{len(flipped)} cell(s) flipped:"]
    for _, row in counts.iterrows():
        lines.append(f"  {row['from']} -> {row['to']}: {row['cells']} cell(s)")
    return "\n".join(lines)


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Diff two failure-envelope CSV snapshots by status_code."
    )
    p.add_argument(
        "csv",
        type=Path,
        help="Working-tree (or 'new') CSV path.",
    )
    p.add_argument(
        "--old",
        type=Path,
        help="Prior CSV path (use this OR --git-ref, not both).",
    )
    p.add_argument(
        "--git-ref",
        help=(
            "Git rev (e.g. HEAD, HEAD~1, a tag) to read the CSV from. "
            "Diffs that snapshot against the working-tree copy."
        ),
    )
    p.add_argument(
        "--max-rows",
        type=int,
        default=20,
        help="Maximum flipped rows to print individually (default 20).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    if (args.old is None) == (args.git_ref is None):
        raise SystemExit("Specify exactly one of --old or --git-ref.")

    new_df = _load_csv(args.csv)
    old_df = (
        _load_from_git(args.git_ref, args.csv) if args.git_ref else _load_csv(args.old)
    )

    try:
        flipped = diff(old_df, new_df)
    except ValueError as exc:
        print(f"[diff_status_codes] {exc}", file=sys.stderr)
        return 2

    print(_summarise(flipped))
    if not flipped.empty:
        print()
        print(
            flipped.head(args.max_rows).to_string(
                index=False,
                columns=["T_K", "P_Pa", "from", "to"],
                float_format=lambda v: f"{v:.2f}",
            )
        )
        if len(flipped) > args.max_rows:
            print(f"... ({len(flipped) - args.max_rows} more)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
