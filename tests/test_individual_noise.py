from experiments.individual_noise_baseline import run_experiment


def test_individual_noise_experiment_has_four_models():
    rows = run_experiment(distances=(3,), error_rates=(0.001,), shots=10)
    assert {row["noise_model"] for row in rows} == {
        "gate_only", "measurement_only", "reset_only", "combined"
    }
