# Testing criteria and correctness checklist

This document explains how to decide whether the Quantum-Correction project is
working correctly. A successful run means the code is functioning as intended;
it does not by itself prove that the simplified IID model represents a real
hardware device.

## 1. Install and environment check

From the repository root:

```bash
python -m pip install -r requirements.txt
```

The required libraries are Stim, PyMatching, NumPy, Matplotlib, pandas,
pytest, and Streamlit. The command should finish without dependency errors.

## 2. Automated test suite

Run:

```bash
PYTHONPATH=. pytest -q
```

Expected result:

```text
12 passed
```

The tests check:

- Invalid probabilities are rejected.
- Invalid code distances and round counts are rejected.
- One or separate IID noise channels can be selected.
- A surface-code circuit is created.
- The circuit and MWPM decoder have matching detector counts.
- Zero physical noise produces zero logical failures.
- The baseline sweep returns valid rates.
- Willow timescale calculations follow their formulas.
- Persistent leakage sampling is reproducible with a fixed seed.

## 3. Circuit and decoder smoke test

Run:

```bash
PYTHONPATH=. python -c "from src.circuits.surface_code import create_surface_code; from src.decoders.mwpm import create_mwpm_decoder; c=create_surface_code(3,3,0.001); d=create_mwpm_decoder(c); print(c.num_detectors, d.num_detectors)"
```

The two printed detector counts must be equal and greater than zero. This
checks that the circuit can be passed to the decoder.

## 4. Main baseline experiment

For a quick check:

```bash
python -m experiments.baseline_mwpm --shots 100
```

For useful statistics:

```bash
python -m experiments.baseline_mwpm
```

The program must finish and create:

```text
output/results/iid_baseline.csv
output/results/iid_baseline.png
```

The CSV must contain 15 rows: three distances times five physical error
probabilities. Every logical-error rate must be between 0 and 1, and every
failure count must be between 0 and the shot count.

The exact numbers change from run to run because the simulation is Monte Carlo.
Do not require every run to produce identical rates.

## 5. Physical sanity checks

These are expected trends, not strict mathematical assertions for small shot
counts:

- At `p=0`, the logical-error rate must be exactly zero.
- Increasing `p` should generally increase the logical-error rate.
- At low or moderate noise, increasing distance should generally reduce the
  logical-error rate.
- At high noise, larger distance may stop helping because the circuit is
  outside its useful operating regime.
- A zero measured rate means no failure was observed; it does not prove the
  true rate is exactly zero.

## 6. Individual-noise experiment

Run:

```bash
python -m experiments.individual_noise_baseline --shots 1000
```

The output must contain four models:

```text
gate_only
measurement_only
reset_only
combined
```

The CSV is written to:

```text
output/results/individual_noise_baseline.csv
```

This experiment compares the current phenomenological Stim channels. It is not
an experimental separation of hardware mechanisms.

## 7. Interactive dashboard test

Run:

```bash
streamlit run dashboard/noise_dashboard.py
```

The page should open in a browser. Choose the distance, rounds, shots, and
three noise probabilities, then click:

```text
▶ Play: run circuit
```

The page must display logical failures, logical-error rate, detector-event
rate, graphs, and a written explanation. The distance-sweep button must also
produce results for `d=3`, `d=5`, and `d=7`.

The dashboard is correct when its displayed result has the same definitions as
the baseline: logical failures are decoded predictions that disagree with
Stim's logical observables, divided by the number of shots.

## 8. Literature and Willow checks

Run:

```bash
python -m experiments.compare_literature_timescales --samples 1000
python -m experiments.willow_reference_check
```

The IID checker should report approximately memoryless behavior. The Willow
check should report the reference values `T1=68 us`, `T2,CPMG=89 us`, QEC cycle
`1.1 us`, and leakage lifetime `4.4 cycles`.

These scripts validate analysis and reference formulas. They do not claim that
the current IID circuit reproduces Willow hardware.

## What this checklist establishes

After the tests pass, we know that:

1. The generated Stim circuit is valid.
2. Detector events can be decoded by MWPM.
3. Logical failures are counted consistently.
4. The baseline experiments produce valid output files.
5. The dashboard calls the same circuit and decoder pipeline.
6. The reference-timescale calculations are internally consistent.

## What it does not establish yet

The current tests do not establish a realistic hardware model. OU temporal
noise, leakage injected into the circuit, crosstalk, calibration drift, burst
events, and correlation-aware MWPM still require separate implementation and
validation against time-ordered experimental data.
