"""Convert a BYOD compressor map CSV into Modelica.Blocks.Tables .txt format.

Modelica's `Modelica.Blocks.Tables.CombiTable1Dv` reads "table on file" via a
plain-text matrix file with this layout::

    #1
    double <table_name>(<n_rows>, <n_cols>)
    <row 1 col 1> <row 1 col 2> ... <row 1 col n_cols>
    <row 2 col 1> <row 2 col 2> ... <row 2 col n_cols>
    ...

The leading `#1` is a magic header that Modelica's table reader requires.
`<table_name>` must match the `tableName` parameter on the table block —
`Compressor.mo` exposes this as `mapTableName` (default `compressor_map`).

Input CSV (validation/compressor_maps/*.csv) is expected to carry three
columns named `phi, psi, eta`. Comments (`#`-prefixed lines) and blank lines
are ignored. The output preserves row order.

Usage::

    python -m tools.compressor_map_to_modelica \\
        validation/compressor_maps/sandia_main_compressor.csv \\
        -o validation/compressor_maps/sandia_main_compressor.txt

Reference: docs/00_strategy.md § Black Hole 1, docs/03_phase3_modelica.md § 3.2.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = ("phi", "psi", "eta")


@dataclass(frozen=True)
class MapRow:
    phi: float
    psi: float
    eta: float


def parse_csv(path: Path) -> list[MapRow]:
    """Parse a `phi, psi, eta` CSV, skipping `#` comments and blank lines."""
    rows: list[MapRow] = []
    with path.open() as fh:
        cleaned = (line for line in fh if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(cleaned)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                f"{path}: CSV missing required columns {missing}; "
                f"got {reader.fieldnames!r}. Expected {REQUIRED_COLUMNS}."
            )
        for raw in reader:
            rows.append(MapRow(
                phi=float(raw["phi"]),
                psi=float(raw["psi"]),
                eta=float(raw["eta"]),
            ))
    if not rows:
        raise ValueError(f"{path}: parsed zero data rows.")

    # Modelica table-on-file requires the key column (phi) to be strictly
    # increasing. Surface that requirement here rather than at simulation
    # start where the error message is opaque.
    for prev, curr in zip(rows, rows[1:]):
        if curr.phi <= prev.phi:
            raise ValueError(
                f"{path}: phi column must be strictly increasing "
                f"(saw {prev.phi} then {curr.phi}). "
                "Sort the CSV by phi before converting."
            )
    return rows


def render_modelica_txt(rows: list[MapRow], table_name: str) -> str:
    """Emit the Modelica.Blocks.Tables `#1` text format."""
    n_rows = len(rows)
    n_cols = 3
    lines = [
        "#1",
        f"double {table_name}({n_rows}, {n_cols})",
    ]
    for r in rows:
        lines.append(f"  {r.phi:.6f} {r.psi:.6f} {r.eta:.6f}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("csv", type=Path, help="Input CSV with phi, psi, eta columns")
    p.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output .txt path (defaults to <csv stem>.txt next to the CSV)",
    )
    p.add_argument(
        "--table-name",
        default="compressor_map",
        help="Modelica table identifier (matches `mapTableName` parameter on the .mo block)",
    )
    args = p.parse_args(argv)

    if not args.csv.exists():
        print(f"error: {args.csv} not found", file=sys.stderr)
        return 2
    rows = parse_csv(args.csv)

    out = args.output or args.csv.with_suffix(".txt")
    out.write_text(render_modelica_txt(rows, args.table_name))
    print(f"Wrote {out} ({len(rows)} rows, table_name={args.table_name!r}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
