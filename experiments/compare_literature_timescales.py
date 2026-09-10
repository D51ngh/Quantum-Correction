"""Compare independent-noise simulations with reported literature timescales.

An IID Bernoulli stream has no physical memory. It can validate an error rate,
but it cannot reproduce T1, T2, leakage lifetime, drift, or 1/f correlation.
"""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class LiteratureRecord:
    mechanism: str
    reported_value: float | None
    reported_unit: str
    timescale_type: str
    model: str
    source: str
    citation: str
    cycle_us: float | None = None


LITERATURE = (
    LiteratureRecord("T1 relaxation", 68.0, "us", "T1 decay constant", "exponential", "Google Willow Nature 2025", "Google Quantum AI et al., Nature 638 (2025), DOI: 10.1038/s41586-024-08449-y"),
    LiteratureRecord("T2 CPMG dephasing", 89.0, "us", "T2,CPMG coherence decay", "exponential", "Google Willow Nature 2025", "Google Quantum AI et al., Nature 638 (2025), DOI: 10.1038/s41586-024-08449-y"),
    LiteratureRecord("Single-qubit gate error", None, "n.a.", "no memory time reported", "iid", "Li et al. npj QI 2023", "Zhiyuan Li et al., npj Quantum Information 9, 111 (2023), DOI: 10.1038/s41534-023-00781-x"),
    LiteratureRecord("Two-qubit gate error", None, "n.a.", "no memory time reported", "iid", "Google Nature 2023 / crosstalk PRX Quantum 2022", "Google Quantum AI et al., Nature 614 (2023), DOI: 10.1038/s41586-022-05434-1; Sundaresan et al., PRX Quantum 3, 020301 (2022), DOI: 10.1103/PRXQuantum.3.020301"),
    LiteratureRecord("Measurement/readout", 6.18, "us", "T01 relaxation during readout", "exponential", "Chen et al. arXiv:2208.05879", "Liangyu Chen et al., arXiv:2208.05879 (2022)"),
    LiteratureRecord("Reset", 45.0, "ns", "resonator decay time 1/kappa", "exponential", "Google Nature Communications 2021", "Google Quantum AI et al., Nature Communications 12, 697 (2021), DOI: 10.1038/s41467-021-21982-y"),
    LiteratureRecord("Leakage", 4.4, "cycles", "injected leakage decay constant", "exponential", "Google Nature Physics 2024", "Google Quantum AI et al., Nature Physics 20, 875-881 (2024), DOI: 10.1038/s41567-023-02226-w", cycle_us=1.0),
    LiteratureRecord("Crosstalk", None, "n.a.", "no measured memory time reported", "correlated", "Sundaresan et al. PRX Quantum 2022", "Sundaresan et al., PRX Quantum 3, 020301 (2022), DOI: 10.1103/PRXQuantum.3.020301"),
    LiteratureRecord("1/f noise", None, "n.a.", "no unique finite correlation time", "one_over_f", "Bylander 2011 / Yan 2012", "Bylander et al., Nature Physics 7, 565-570 (2011), DOI: 10.1038/nphys1994; Yan et al., arXiv:1201.5665"),
    LiteratureRecord("Calibration drift", None, "n.a.", "no universal physical tau reported", "drift", "Klimov 2018 / arXiv:2602.11912", "Klimov et al., PRL 121, 090502 (2018), DOI: 10.1103/PhysRevLett.121.090502; arXiv:2602.11912"),
    LiteratureRecord("High-energy correlated events", None, "n.a.", "burst duration not reported", "bursty", "arXiv:2505.15919 / Google Nature 2025", "Mitigating cosmic ray-like correlated events, arXiv:2505.15919; Google Quantum AI et al., Nature 638 (2025), DOI: 10.1038/s41586-024-08449-y"),
)


def simulate_iid_errors(probability: float, samples: int, rng: np.random.Generator) -> np.ndarray:
    return (rng.random(samples) < probability).astype(float)


def lag1_autocorrelation(values: np.ndarray) -> float:
    centered = values - values.mean()
    denominator = np.dot(centered, centered)
    if denominator == 0:
        return 0.0
    return float(np.dot(centered[:-1], centered[1:]) / denominator)


def iid_memory_check(probability: float, samples: int, seed: int) -> dict:
    errors = simulate_iid_errors(probability, samples, np.random.default_rng(seed))
    return {
        "iid_probability": probability,
        "iid_lag1_autocorrelation": lag1_autocorrelation(errors),
        "iid_memory_result": "approximately memoryless",
    }


def exponential_decay_check(tau: float, dt: float, seed: int) -> float:
    """Fit a controlled synthetic exponential; this is not hardware validation."""
    rng = np.random.default_rng(seed)
    time = np.arange(101) * dt
    ideal = np.exp(-time / tau)
    measured = np.clip(ideal + rng.normal(0.0, 0.003, len(time)), 1e-4, None)
    slope, _ = np.polyfit(time, np.log(measured), 1)
    return float(-1.0 / slope)


def to_us(value: float, unit: str, cycle_us: float | None) -> float:
    if unit == "us":
        return value
    if unit == "ns":
        return value / 1000.0
    if unit == "cycles":
        return value * (cycle_us or 1.0)
    raise ValueError(f"Cannot convert {unit!r} to microseconds")


def run_check(probability: float, samples: int, seed: int):
    iid = iid_memory_check(probability, samples, seed)
    rows = []
    for index, record in enumerate(LITERATURE):
        row = {
            "mechanism": record.mechanism,
            "reported_timescale": record.reported_value if record.reported_value is not None else "not reported",
            "reported_unit": record.reported_unit,
            "timescale_type": record.timescale_type,
            "source": record.source,
            "citation": record.citation,
            "iid_probability": iid["iid_probability"],
            "iid_lag1_autocorrelation": iid["iid_lag1_autocorrelation"],
            "iid_estimated_memory": "no finite memory",
            "literature_comparison": "not comparable: IID has no memory",
            "analysis_check_value": "not run",
            "analysis_check_unit": "n.a.",
            "evidence_note": "IID rate check only; not hardware validation",
        }
        if record.model == "exponential" and record.reported_value is not None:
            tau_us = to_us(record.reported_value, record.reported_unit, record.cycle_us)
            row["analysis_check_value"] = round(exponential_decay_check(tau_us, tau_us / 100.0, seed + index), 6)
            row["analysis_check_unit"] = "us"
            row["literature_comparison"] = "controlled exponential-fit check; not hardware validation"
            row["evidence_note"] = "The literature value was used as a synthetic model parameter to test the fitter; this is not hardware validation."
        elif record.model == "one_over_f":
            row["literature_comparison"] = "not comparable: 1/f has no unique finite tau without cutoffs"
        elif record.model in {"correlated", "drift", "bursty"}:
            row["literature_comparison"] = "not comparable: independent stream omits the reported correlation mechanism"
        rows.append(row)
    return rows


def save_csv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probability", type=float, default=0.001)
    parser.add_argument("--samples", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--output", type=Path, default=Path("results/literature_timescale_check.csv"))
    args = parser.parse_args()
    if not 0 <= args.probability <= 1:
        raise ValueError("--probability must be between 0 and 1")
    if args.samples < 2:
        raise ValueError("--samples must be at least 2")
    rows = run_check(args.probability, args.samples, args.seed)
    save_csv(rows, args.output)
    print(f"IID probability: {args.probability}")
    print(f"IID lag-1 autocorrelation: {rows[0]['iid_lag1_autocorrelation']:.6g}")
    print("Result: the independent-noise stream is approximately memoryless.")
    for row in rows:
        print(f"{row['mechanism']}: {row['literature_comparison']}")
    print(f"Saved report to {args.output}")


if __name__ == "__main__":
    main()
