from experiments.compare_literature_timescales import run_check


def test_iid_check_has_no_memory():
    rows = run_check(probability=0.1, samples=10_000, seed=7)
    assert len(rows) == 11
    assert abs(rows[0]["iid_lag1_autocorrelation"]) < 0.05
    assert all(row["iid_estimated_memory"] == "no finite memory" for row in rows)


def test_exponential_fit_is_controlled_only():
    rows = run_check(probability=0.001, samples=1_000, seed=7)
    t1 = next(row for row in rows if row["mechanism"] == "T1 relaxation")
    leakage = next(row for row in rows if row["mechanism"] == "Leakage")
    assert abs(t1["analysis_check_value"] - 68.0) < 5.0
    assert abs(leakage["analysis_check_value"] - 4.4) < 0.5
    assert "not hardware validation" in t1["evidence_note"]
