"""Tests for postProcessing CFD-summary scripts."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def plot_module():
    return _load("pp_plot_nu", REPO_ROOT / "postProcessing" / "plot_Nu_vs_Re.py")


@pytest.fixture
def validate_module():
    return _load(
        "pp_validate", REPO_ROOT / "postProcessing" / "validate_against_exp.py"
    )


def test_gnielinski_classical_value(plot_module):
    """Spot-check Gnielinski at Re=10^4, Pr=0.85.

    Hand calculation:
        f = (0.79*ln(1e4) - 1.64)^-2 ≈ 0.03088
        Nu ≈ (f/8)*(Re-1000)*Pr / (1 + 12.7*sqrt(f/8)*(Pr^(2/3)-1))
            ≈ 28-32 for Pr=0.85
    Loose tolerance — keep it as a regression guard, not an accuracy claim.
    """
    import numpy as np

    Nu = plot_module.gnielinski(np.array([1e4]))
    assert 20.0 < float(Nu[0]) < 40.0


def test_collect_summaries_empty(plot_module, tmp_path):
    """No CFD summary files → empty DataFrame, no exception."""
    df = plot_module.collect_summaries(tmp_path)
    assert df.empty


def test_collect_summaries_round_trip(plot_module, tmp_path):
    """Plant a fake summary.csv and confirm it gets picked up with the geometry tag."""
    case_dir = tmp_path / "case02_zigzag" / "run_001"
    case_dir.mkdir(parents=True)
    pd.DataFrame(
        {"Re": [5000.0], "Nu_avg": [25.0], "T_in_K": [350.0], "P_in_Pa": [15e6]}
    ).to_csv(case_dir / "summary.csv", index=False)

    df = plot_module.collect_summaries(tmp_path)
    assert len(df) == 1
    assert df.iloc[0]["geometry"] == "zigzag"
    assert df.iloc[0]["Re"] == 5000.0


def test_validate_skips_when_either_side_empty(
    validate_module, tmp_path, monkeypatch, capsys
):
    """validate_against_exp must exit-style return 0 when one side is empty."""
    fake_exp = tmp_path / "exp.csv"
    fake_exp.write_text(
        "T_inlet_K,P_inlet_Pa,rho_inlet_measured,source_ref\n"
        "350,15000000,750,placeholder\n"
    )
    fake_root = tmp_path / "cfd"
    fake_root.mkdir()

    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_against_exp", "--cfd-root", str(fake_root), "--exp", str(fake_exp)],
    )
    rc = validate_module.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "skipping" in out


def test_nearest_cfd_picks_closest(validate_module):
    cfd = pd.DataFrame(
        {
            "T_in_K": [305.0, 400.0, 500.0],
            "P_in_Pa": [8e6, 15e6, 20e6],
        }
    )
    nearest = validate_module.nearest_cfd(cfd, T=399.0, P=15.1e6)
    assert nearest is not None
    assert nearest["T_in_K"] == 400.0
