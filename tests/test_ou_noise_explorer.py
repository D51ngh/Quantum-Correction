import numpy as np

from dashboard.ou_noise_explorer import autocorrelation, memory_fraction, simulate_ou


def test_ou_output_shapes_and_probability_bounds():
    level, probability, errors = simulate_ou(50, 1.0, 10.0, -4.0, 0.8, 0.02, 7)
    assert level.shape == probability.shape == errors.shape == (50,)
    assert np.all((probability >= 0) & (probability <= 0.02))
    assert errors.dtype == bool


def test_zero_fluctuation_stays_at_mean():
    level, _, _ = simulate_ou(20, 1.0, 10.0, 0.5, 0.0, 0.2, 1)
    assert np.allclose(level, 0.5)


def test_memory_fraction_has_expected_values():
    assert np.isclose(memory_fraction(10, 1.0, 10.0), 1 - np.exp(-1))
    assert memory_fraction(30, 1.0, 10.0) > memory_fraction(10, 1.0, 10.0)


def test_autocorrelation_lag_zero_is_one():
    values = np.sin(np.linspace(0, 10, 100))
    assert np.isclose(autocorrelation(values, 5)[0], 1.0)
