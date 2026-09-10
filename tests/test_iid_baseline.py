import pytest

from experiments.baseline_mwpm import run_baseline
from src.circuits.surface_code import create_surface_code
from src.noise.iid_noise import get_iid_noise


def test_iid_noise_rejects_invalid_probability():
    with pytest.raises(ValueError):
        get_iid_noise(-0.1)
    with pytest.raises(ValueError):
        get_iid_noise(1.1)


def test_surface_code_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        create_surface_code(4, 4)
    with pytest.raises(ValueError):
        create_surface_code(3, 0)


def test_zero_noise_has_no_logical_failures():
    result = run_baseline(distances=(3,), error_rates=(0.0,), shots=100)
    assert result[0]["logical_failures"] == 0


def test_baseline_sweeps_requested_points():
    result = run_baseline(distances=(3, 5), error_rates=(0.001, 0.003), shots=10)
    assert len(result) == 4
    assert all(0.0 <= row["logical_error_rate"] <= 1.0 for row in result)
