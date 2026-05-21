"""Smoke test for the end-to-end ROM training pipeline.

Reference: docs/02_phase2_cfd_rom.md § 2.6.

This test exercises the *pipeline plumbing* on a tiny synthetic dataset:
    extract_from_cfd --synthetic → train_rom → ONNX file on disk

It does NOT validate ROM accuracy — the docs are explicit that any ROM
trained on synthetic data must not be published. The point here is to
catch breakage in argument plumbing, scaler save/load, ONNX export, and
file IO when somebody refactors any of those pieces.

Required optional dependencies: torch, scikit-learn. Skips otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

torch = pytest.importorskip("torch", reason="PyTorch not installed (rom optional)")
sklearn = pytest.importorskip("sklearn", reason="scikit-learn not installed")
# `onnx` is also optional (requirements-rom.txt). Tests that exercise the
# torch.onnx export path call `pytest.importorskip("onnx")` individually so
# the column-shape and CSV round-trip tests still run without it.


def test_synthetic_dataset_has_required_columns():
    from rom.dataset.extract_from_cfd import synthetic_dataset

    df = synthetic_dataset(n=50, seed=0)
    required = {"T_in_K", "P_in_Pa", "mass_flow_kg_s", "geometry_id",
                "Nu_avg", "dp_total_Pa"}
    assert required.issubset(df.columns)
    assert (df["Nu_avg"] >= 1.0).all()
    assert (df["dp_total_Pa"] >= 1.0).all()


def test_synthetic_to_csv(tmp_path):
    """The dataset script must round-trip through CSV without losing rows."""
    from rom.dataset.extract_from_cfd import synthetic_dataset
    import pandas as pd

    out = tmp_path / "synth.csv"
    df = synthetic_dataset(n=80)
    df.to_csv(out, index=False)
    re_read = pd.read_csv(out)
    assert len(re_read) == 80
    assert set(re_read.columns) == set(df.columns)


def test_end_to_end_train_export(tmp_path):
    """Train on synthetic data and confirm ONNX + scalers land on disk."""
    pytest.importorskip("onnx", reason="onnx not installed (rom optional)")
    from rom.dataset.extract_from_cfd import synthetic_dataset
    from rom.train_rom import train

    csv_path = tmp_path / "training_set.csv"
    out_dir = tmp_path / "exported"
    df = synthetic_dataset(n=120, seed=42)
    df.to_csv(csv_path, index=False)

    metrics = train(csv_path, out_dir, epochs=200, lr=1e-3, seed=0)
    assert "mape_Nu_pct" in metrics
    assert "mape_dp_pct" in metrics
    assert (out_dir / "pche_rom.onnx").exists()
    assert (out_dir / "scalers.npz").exists()


def test_onnx_runtime_inference_round_trip(tmp_path):
    """A freshly-exported ONNX must be loadable by onnxruntime."""
    pytest.importorskip("onnx", reason="onnx not installed (rom optional)")
    ort = pytest.importorskip("onnxruntime", reason="onnxruntime not installed")

    from rom.dataset.extract_from_cfd import synthetic_dataset
    from rom.train_rom import train
    import numpy as np

    csv_path = tmp_path / "training_set.csv"
    out_dir = tmp_path / "exported"
    synthetic_dataset(n=80).to_csv(csv_path, index=False)
    train(csv_path, out_dir, epochs=100, seed=0)

    sess = ort.InferenceSession(str(out_dir / "pche_rom.onnx"))
    scalers = np.load(out_dir / "scalers.npz")
    x = np.array([[400.0, 15e6, 0.2, 1]], dtype=np.float32)
    xn = (x - scalers["x_mean"]) / scalers["x_scale"]
    y_pred = sess.run(None, {"features": xn.astype(np.float32)})[0]
    assert y_pred.shape == (1, 2)
    y = y_pred * scalers["y_scale"] + scalers["y_mean"]
    assert np.isfinite(y).all()
