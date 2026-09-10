"""Check the current experiment against directly reported Willow timescales."""

from __future__ import annotations

import argparse

from src.noise.willow_model import WillowParameters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=20)
    parser.add_argument("--injection-probability", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()

    willow = WillowParameters()
    print("Willow reference parameters")
    print(f"  T1 = {willow.t1_us:.1f} us (directly measured)")
    print(f"  T2,CPMG = {willow.t2_cpmg_us:.1f} us (directly measured)")
    print(f"  QEC cycle = {willow.qec_cycle_us:.1f} us (directly measured)")
    print(f"  leakage lifetime = {willow.leakage_decay_cycles:.1f} cycles (fitted)")
    print(
        "  relaxation probability per cycle = "
        f"{willow.relaxation_probability_per_cycle():.6f} (derived from T1)"
    )
    print(
        "  CPMG coherence survival per cycle = "
        f"{willow.coherence_survival_per_cycle():.6f} (derived from T2)"
    )
    print("\nLeakage survival from the reported 4.4-cycle lifetime:")
    for rounds in (1, 3, 4, 5, 10, args.rounds):
        print(f"  after {rounds:>2} rounds: {willow.leakage_survival(rounds):.4f}")
    states = willow.leakage_persistence_stream(
        args.rounds, args.injection_probability, args.seed
    )
    print("\nExample leakage-state stream (injection probability is user-supplied):")
    print("  " + " ".join(map(str, states.tolist())))
    print("\nReported Willow bulk detection-event probabilities:")
    for distance, probability in willow.p_det_by_distance:
        print(f"  d={distance}: p_det={probability:.3f} (directly measured)")
    print(f"\nSource: {willow.source}")


if __name__ == "__main__":
    main()
