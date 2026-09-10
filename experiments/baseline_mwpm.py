import argparse
import csv
from pathlib import Path

import numpy as np

from src.circuits.surface_code import create_surface_code
from src.decoders.mwpm import create_mwpm_decoder


DEFAULT_DISTANCES = (3, 5, 7)
DEFAULT_ERROR_RATES = (0.0001, 0.0003, 0.001, 0.003, 0.01)


def run_point(distance, error_rate, shots):
    circuit = create_surface_code(distance, distance, error_rate)
    decoder = create_mwpm_decoder(circuit)
    sampler = circuit.compile_detector_sampler()
    detectors, observables = sampler.sample(
        shots=shots, separate_observables=True
    )
    predictions = decoder.decode_batch(detectors)
    return int(np.any(predictions != observables, axis=1).sum())


def run_baseline(distances=DEFAULT_DISTANCES, error_rates=DEFAULT_ERROR_RATES, shots=10_000):
    if shots < 1:
        raise ValueError("shots must be positive")
    results = []
    for distance in distances:
        for error_rate in error_rates:
            failures = run_point(distance, error_rate, shots)
            row = {
                "distance": distance,
                "error_rate": error_rate,
                "rounds": distance,
                "shots": shots,
                "logical_failures": failures,
                "logical_error_rate": failures / shots,
            }
            results.append(row)
            print(f"d={distance}, p={error_rate:g}, logical_error_rate={failures / shots:.6g}")
    return results


def save_csv(results, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(results[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def save_plot(results, path):
    import matplotlib.pyplot as plt

    path.parent.mkdir(parents=True, exist_ok=True)
    for distance in sorted({row["distance"] for row in results}):
        rows = [row for row in results if row["distance"] == distance]
        plt.loglog(
            [row["error_rate"] for row in rows],
            [max(row["logical_error_rate"], 0.5 / row["shots"]) for row in rows],
            marker="o", label=f"d={distance}",
        )
    plt.xlabel("Physical error probability p")
    plt.ylabel("Logical error rate")
    plt.title("IID-noise surface-code baseline with MWPM")
    plt.grid(True, which="both", linestyle=":", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=int, default=10_000)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    results = run_baseline(shots=args.shots)
    save_csv(results, args.output_dir / "iid_baseline.csv")
    save_plot(results, args.output_dir / "iid_baseline.png")
    print(f"Saved results to {args.output_dir / 'iid_baseline.csv'}")
    print(f"Saved plot to {args.output_dir / 'iid_baseline.png'}")


if __name__ == "__main__":
    main()
