"""Interactive surface-code and noise-literature dashboard.

Run from the repository root with:

    streamlit run dashboard/noise_dashboard.py
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "docs" / "noise_literature_database.md"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.noise.willow_model import WillowParameters
from src.circuits.surface_code import create_surface_code
from src.decoders.mwpm import create_mwpm_decoder


def load_literature_records():
    """Read the ten-row main mechanism table from the Markdown database."""
    lines = DATABASE.read_text().splitlines()
    header = None
    records = []
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if header is None and cells and cells[0] == "Noise mechanism":
            header = cells
            continue
        if header is not None and len(cells) == len(header) and cells[0] not in {"---", ""}:
            if cells[0] in {"T1 energy relaxation", "T2 dephasing", "Single-qubit gate errors",
                            "Two-qubit gate errors", "Measurement/readout errors",
                            "Reset/preparation errors", "Leakage", "Crosstalk and stray interactions",
                            "Low-frequency / 1/f noise", "Calibration drift / fluctuating device parameters",
                            "Correlated multi-qubit / high-energy events"}:
                records.append(dict(zip(header, cells)))
    return records


def run_simulation(distance, rounds, shots, gate_rate, measurement_rate, reset_rate):
    circuit = create_surface_code(
        distance=distance,
        rounds=rounds,
        noise_rates={
            "gate": gate_rate,
            "measurement": measurement_rate,
            "reset": reset_rate,
        },
    )
    decoder = create_mwpm_decoder(circuit)
    detectors, observables = circuit.compile_detector_sampler().sample(
        shots=shots, separate_observables=True
    )
    predictions = decoder.decode_batch(detectors)
    failures = int(np.any(predictions != observables, axis=1).sum())
    return {
        "distance": distance,
        "rounds": rounds,
        "shots": shots,
        "logical_failures": failures,
        "logical_error_rate": failures / shots,
        "detector_event_rate": float(detectors.mean()),
        "gate_error_rate": gate_rate,
        "measurement_error_rate": measurement_rate,
        "reset_error_rate": reset_rate,
    }


def explain_result(result):
    """Return a short plain-language interpretation of one run."""
    highest_physical_rate = max(
        result["gate_error_rate"],
        result["measurement_error_rate"],
        result["reset_error_rate"],
    )
    logical_rate = result["logical_error_rate"]
    if logical_rate == 0:
        return (
            f"MWPM corrected every one of the {result['shots']:,} simulated shots. "
            "This means no logical failure was observed in this sample; it does not prove the true rate is exactly zero."
        )
    if logical_rate < highest_physical_rate:
        return (
            f"MWPM left {result['logical_failures']} logical failures out of {result['shots']:,} shots. "
            "The encoded logical error rate is below the largest selected physical noise rate, so the code improved reliability in this run."
        )
    return (
        f"MWPM left {result['logical_failures']} logical failures out of {result['shots']:,} shots. "
        "The selected noise is high enough that the logical rate is not below the largest physical noise rate; try a lower rate or larger distance."
    )


st.set_page_config(page_title="Quantum-Correction dashboard", layout="wide")
st.title("Quantum-Correction dashboard")
st.caption("Adjust active IID noise channels, run Stim + MWPM, and inspect literature reference values.")

with st.sidebar:
    st.header("Simulation controls")
    with st.form("circuit_controls"):
        distance = st.selectbox("Code distance", [3, 5, 7], index=0)
        rounds = st.number_input("QEC rounds", min_value=1, max_value=100, value=3, step=1)
        shots = st.number_input("Monte Carlo shots", min_value=10, max_value=100_000, value=1_000, step=100)
        st.subheader("Active IID noise rates")
        gate_rate = st.number_input("Gate error probability", 0.0, 0.1, 0.001, 0.0001, format="%.4f")
        measurement_rate = st.number_input("Measurement error probability", 0.0, 0.1, 0.001, 0.0001, format="%.4f")
        reset_rate = st.number_input("Reset error probability", 0.0, 0.1, 0.001, 0.0001, format="%.4f")
        run = st.form_submit_button("▶ Play: run circuit", type="primary", use_container_width=True)

if run:
    with st.spinner("Running Stim and MWPM..."):
        result = run_simulation(distance, int(rounds), int(shots), gate_rate, measurement_rate, reset_rate)
    st.session_state["last_result"] = result
    history = st.session_state.setdefault("history", [])
    history.append(result)

result = st.session_state.get("last_result")
if result:
    st.subheader("Simulation result")
    col1, col2, col3 = st.columns(3)
    col1.metric("Logical-error rate", f"{result['logical_error_rate']:.6g}")
    col2.metric("Logical failures", result["logical_failures"])
    col3.metric("Detector-event rate", f"{result['detector_event_rate']:.6g}")
    st.dataframe(pd.DataFrame([result]), use_container_width=True, hide_index=True)
    st.info(explain_result(result))

    st.subheader("What the selected noise is doing")
    noise_plot = pd.DataFrame(
        {
            "Noise channel": ["Gate", "Measurement", "Reset", "Logical result"],
            "Probability": [
                result["gate_error_rate"],
                result["measurement_error_rate"],
                result["reset_error_rate"],
                result["logical_error_rate"],
            ],
        }
    ).set_index("Noise channel")
    st.bar_chart(noise_plot)
    st.caption(
        "The first three bars are input physical-error probabilities. "
        "The last bar is the measured logical-error rate after Stim and MWPM."
    )

    history = pd.DataFrame(st.session_state.get("history", []))
    st.subheader("Run history")
    st.line_chart(history.set_index(history.index)[["logical_error_rate", "detector_event_rate"]])
else:
    st.info("Choose the noise rates and press **Run simulation**.")

st.divider()
st.header("Literature reference")
records = load_literature_records()
names = [record["Noise mechanism"] for record in records]
selected_name = st.selectbox("Choose a documented noise mechanism", names)
selected = next(record for record in records if record["Noise mechanism"] == selected_name)
reference = pd.DataFrame({"Field": list(selected), "Value": list(selected.values())})
st.dataframe(reference, use_container_width=True, hide_index=True)

willow = WillowParameters()
st.caption(
    f"Willow reference: T1={willow.t1_us:g} us, T2,CPMG={willow.t2_cpmg_us:g} us, "
    f"QEC cycle={willow.qec_cycle_us:g} us, leakage lifetime={willow.leakage_decay_cycles:g} cycles. "
    "These references are not automatically substituted for the active IID rates above."
)
