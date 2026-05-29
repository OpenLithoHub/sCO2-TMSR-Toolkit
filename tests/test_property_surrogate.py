"""Tests for PropertySurrogate (CoolProp neural surrogate)."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from property_surrogate import PropertySurrogate


def _make_synthetic_data(n: int = 50) -> dict[str, np.ndarray]:
    """Generate synthetic thermophysical data (no CoolProp dependency)."""
    rng = np.random.default_rng(42)
    T = rng.uniform(350, 900, n)
    P = rng.uniform(7.5e6, 30e6, n)
    # Simple synthetic relationships (not physically accurate, just for testing)
    density = 100.0 + 0.5 * P / 1e6 - 0.1 * T
    viscosity = 1e-5 + 1e-8 * P / 1e6 - 1e-9 * T
    conductivity = 0.05 + 1e-5 * P / 1e6 - 2e-6 * T
    specific_heat = 1000.0 + 0.5 * T - 1e-5 * P
    return {
        "T": T,
        "P": P,
        "density": density,
        "viscosity": np.abs(viscosity),
        "conductivity": np.abs(conductivity),
        "specific_heat": np.abs(specific_heat),
    }


class TestPropertySurrogateInit:
    def test_default_init(self):
        surr = PropertySurrogate()
        assert surr._device == torch.device("cpu")
        assert surr._hidden_dim == 64
        assert not surr._trained

    def test_custom_hidden_dim(self):
        surr = PropertySurrogate(hidden_dim=32)
        # Verify networks have correct hidden dim by checking parameter shapes
        params = list(surr._density_net.parameters())
        assert params[0].shape[0] == 32

    def test_device_kwarg(self):
        surr = PropertySurrogate(device="cpu")
        assert surr._device == torch.device("cpu")


class TestPropertySurrogateTrain:
    def test_train_reduces_loss(self):
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(80)
        losses = surr.train(data, epochs=30, lr=1e-3, verbose=False)
        # Training should reduce loss over time
        assert len(losses["density"]) == 30
        assert losses["density"][-1] < losses["density"][0]

    def test_train_sets_trained_flag(self):
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(30)
        surr.train(data, epochs=5, verbose=False)
        assert surr._trained

    def test_loss_weights(self):
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(40)
        losses = surr.train(
            data,
            epochs=10,
            loss_weights={"density": 10.0, "viscosity": 0.1},
            verbose=False,
        )
        assert len(losses["density"]) == 10


class TestPropertySurrogatePredict:
    def test_predict_all_after_training(self):
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(60)
        surr.train(data, epochs=20, verbose=False)

        result = surr.predict_all(500.0, 20e6)
        assert "density" in result
        assert "viscosity" in result
        assert "conductivity" in result
        assert "specific_heat" in result
        for key, val in result.items():
            assert isinstance(val, np.ndarray)
            assert np.isfinite(val).all(), f"{key} has non-finite values"

    def test_predict_scalar_methods(self):
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(60)
        surr.train(data, epochs=20, verbose=False)

        rho = surr.predict_density(500.0, 20e6)
        assert isinstance(rho, float)
        assert np.isfinite(rho)

        mu = surr.predict_viscosity(500.0, 20e6)
        assert mu > 0, "viscosity should be positive (PositiveOutputMLP)"

        k = surr.predict_conductivity(500.0, 20e6)
        assert k > 0, "conductivity should be positive (PositiveOutputMLP)"

        cp = surr.predict_specific_heat(500.0, 20e6)
        assert cp > 0, "specific_heat should be positive (PositiveOutputMLP)"

    def test_predict_before_training_raises(self):
        surr = PropertySurrogate()
        with pytest.raises(RuntimeError, match="not trained"):
            surr.predict_all(500.0, 20e6)

    def test_predict_array_input(self):
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(60)
        surr.train(data, epochs=20, verbose=False)

        T_arr = np.array([400.0, 500.0, 600.0])
        P_arr = np.array([10e6, 15e6, 20e6])
        result = surr.predict_all(T_arr, P_arr)
        assert result["density"].shape == (3,)


class TestPropertySurrogateState:
    def test_state_dict_roundtrip(self, tmp_path):
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(40)
        surr.train(data, epochs=10, verbose=False)

        state = surr.state_dict()
        assert "density_net" in state
        assert "stats" in state
        assert "trained" in state

        surr2 = PropertySurrogate(hidden_dim=32)
        surr2.load_state_dict(state)
        assert surr2._trained

        # Predictions should match
        x = surr.predict_all(500.0, 20e6)
        y = surr2.predict_all(500.0, 20e6)
        for key in x:
            np.testing.assert_allclose(x[key], y[key], rtol=1e-5)


class TestPhysicsConstraints:
    def test_viscosity_always_positive(self):
        """PositiveOutputMLP guarantees positive viscosity."""
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(60)
        surr.train(data, epochs=20, verbose=False)

        # Test at extreme conditions
        T_extreme = np.linspace(300, 1000, 20)
        P_extreme = np.linspace(5e6, 40e6, 20)
        result = surr.predict_all(T_extreme, P_extreme)
        assert (result["viscosity"] > 0).all()
        assert (result["conductivity"] > 0).all()
        assert (result["specific_heat"] > 0).all()

    def test_density_monotone_in_pressure(self):
        """MonotoneMLP should produce non-decreasing density with pressure."""
        surr = PropertySurrogate(hidden_dim=32)
        data = _make_synthetic_data(100)
        surr.train(data, epochs=50, verbose=False)

        T_fixed = np.full(20, 500.0)
        P_range = np.linspace(8e6, 28e6, 20)
        result = surr.predict_all(T_fixed, P_range)
        diffs = np.diff(result["density"])
        # Allow small numerical tolerance
        assert (diffs >= -0.1).all(), (
            f"Density not monotone in pressure: min diff = {diffs.min():.4f}"
        )
