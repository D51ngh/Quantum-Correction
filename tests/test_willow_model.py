import math

from src.noise.willow_model import WillowParameters


def test_willow_reference_values_and_timescales():
    params = WillowParameters()
    assert math.isclose(params.relaxation_probability_per_cycle(), 1 - math.exp(-1.1 / 68.0))
    assert math.isclose(params.leakage_survival(4.4), math.exp(-1.0))


def test_leakage_stream_is_reproducible():
    params = WillowParameters()
    first = params.leakage_persistence_stream(20, 0.2, seed=7)
    second = params.leakage_persistence_stream(20, 0.2, seed=7)
    assert (first == second).all()
