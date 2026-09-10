"""Measure each currently implemented IID noise component separately."""

import argparse
import csv
from pathlib import Path

import numpy as np

from src.circuits.surface_code import create_surface_code
from src.decoders.mwpm import create_mwpm_decoder


COMPONENTS = {
    "gate_only": ("after_clifford_depolarization",),
    "measurement_only": ("before_measure_flip_probability",),
    "reset_only": ("after_reset_flip_probability",),
    "combined": None,
}
DISTANCES = (3, 5, 7)
ERROR_RATES = (0.0001, 0.0003, 0.001, 0.003, 0.01)


def run_point(distance, error_rate, shots, noise_components):
    circuit = create_surface_code(
        distance=distance,
        rounds=distance,
        error_rate=error_rate,
        noise_components=noise_components,
    )
    decoder = create_mwpm_decoder(circuit)
    detectors, observables = circuit.compile_detector_sampler().sample(
        shots=shots, separate_observables=True
    )
    predictions = decoder.decode_batch(detectors)
    failures = int(np.any(predictions != observables, axis=1).sum())
    return failures, failures / shots


def run_experiment(distances=DISTANCES, error_rates=ERROR_RATES, shots=10_000):
    if shots < 1:
        raise ValueError("shots must be positive")
    rows = []
    for label, components in COMPONENTS.items():
        for distance in distances:
            for error_rate in error_rates:
                failures, logical_error_rate = run_point(
                    distance, error_rate, shots, components
                )
                row = {
                    "noise_model": label,
                    "distance": distance,
                    "rounds": distance,
                    "error_rate": error_rate,
                    "shots": shots,
                    "logical_failures": failures,
                    "logical_error_rate": logical_error_rate,
                }
                rows.append(row)
                print(
                    f"{label:17s} d={distance}, p={error_rate:g}, "
                    f"logical_error_rate={logical_error_rate:.6g}"
                )
    return rows


def save_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=10_000)
    parser.add_argument("--output", type=Path, default=Path("results/individual_noise_baseline.csv"))
    args = parser.parse_args()
    rows = run_experiment(shots=args.shots)
    save_csv(rows, args.output)
    print(f"Saved results to {args.output}")


if __name__ == "__main__":
    main()
