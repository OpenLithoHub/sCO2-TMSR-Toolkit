"""Structural sanity tests for the Modelica library.

These do NOT compile Modelica (that requires OpenModelica's `omc` and runs in
CI per `docs/03_phase3_modelica.md` § 3.8). They catch the most common
refactor breakage on every developer's local machine in <1 second:

- Every `.mo` file declares a `within` clause (or is a top-level package).
- Every `model X ... end X;` and `package X ... end X;` block is balanced
  by name.
- The aggregate `Tests/ValidationTests.mo` references every component
  documented in `docs/03_phase3_modelica.md § 3.2` so a newly-added
  component is not silently skipped by CI.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELICA_ROOT = REPO_ROOT / "modelica" / "AdvancedReactor_sCO2_Library"

# Top-level package file is the only one allowed to use `within ;`.
TOP_LEVEL_PACKAGE = MODELICA_ROOT / "package.mo"

# Components listed in docs/03_phase3_modelica.md § 3.2 that ValidationTests
# must instantiate. Add to this list when a new component is documented.
EXPECTED_VALIDATED_COMPONENTS = (
    "Components.Valves.ThrottleValve",
    "Components.Valves.BypassValve",
    "Components.Turbomachinery.Compressor",
    "Components.Turbomachinery.ReCompressor",
    "Components.Turbomachinery.Turbine",
    "Components.Turbomachinery.LabyrinthSeal",
    "Components.HeatExchangers.IntermediateHeatExchanger",
    "Components.HeatExchangers.PCHE",
    "Components.HeatExchangers.TritiumPermeationLayer",
    "Components.Reactor.MoltenSaltReactor",
    "Components.Reactor.OnlineFuellingTransient",
)


def all_mo_files() -> list[Path]:
    return sorted(MODELICA_ROOT.rglob("*.mo"))


@pytest.mark.parametrize("mo_path", all_mo_files(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_within_clause_present(mo_path: Path):
    """Every Modelica file must start with a `within` clause."""
    text = mo_path.read_text()
    first_nonblank = next(
        (line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("//")),
        "",
    )
    assert first_nonblank.startswith("within "), (
        f"{mo_path.relative_to(REPO_ROOT)}: first non-blank line must start "
        f"with 'within' (got {first_nonblank!r})"
    )


@pytest.mark.parametrize("mo_path", all_mo_files(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_block_names_balanced(mo_path: Path):
    """The opening `model X` / `package X` must match the closing `end X;`.

    Strips strings and line comments so an `end Foo;` inside an HTML annotation
    does not confuse the matcher.
    """
    text = mo_path.read_text()
    # Strip line comments and string literals before matching.
    stripped = re.sub(r"//[^\n]*", "", text)
    stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', stripped, flags=re.DOTALL)

    open_match = re.search(
        r"^\s*(model|package|record|function|connector|block|class)\s+(\w+)",
        stripped,
        re.MULTILINE,
    )
    assert open_match, f"{mo_path.relative_to(REPO_ROOT)}: no top-level Modelica block found"
    block_kind, block_name = open_match.group(1), open_match.group(2)

    end_pattern = re.compile(rf"\bend\s+{re.escape(block_name)}\s*;\s*$", re.MULTILINE)
    assert end_pattern.search(stripped), (
        f"{mo_path.relative_to(REPO_ROOT)}: opens '{block_kind} {block_name}' "
        f"but is not closed by 'end {block_name};'"
    )


def test_validation_tests_references_every_documented_component():
    """Tests/ValidationTests.mo must instantiate every § 3.2 component.

    If you add a new component under Components/, add it to ValidationTests
    and to EXPECTED_VALIDATED_COMPONENTS above. Otherwise CI will not catch
    a syntax error in the new file.
    """
    vt_text = (MODELICA_ROOT / "Tests" / "ValidationTests.mo").read_text()
    missing = [c for c in EXPECTED_VALIDATED_COMPONENTS if c not in vt_text]
    assert not missing, (
        "ValidationTests.mo does not reference: " + ", ".join(missing)
    )
