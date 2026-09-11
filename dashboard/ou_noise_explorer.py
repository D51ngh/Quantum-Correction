"""Interactive explorer for the OU temporal-correlation model.

Run from the repository root with:

    streamlit run dashboard/ou_noise_explorer.py

This page explains and visualizes the correlated-noise model. It does not
modify the Stim surface-code circuit or implement correlation-aware MWPM.
"""

import numpy as np
import pandas as pd
import streamlit as st


def simulate_ou(rounds, dt, tau_c, mu, sigma, p_max, seed):
    """Generate OU noise, mapped probabilities, and Bernoulli error events."""
    rng = np.random.default_rng(seed)
    x = np.empty(rounds, dtype=float)
    x[0] = mu
    for index in range(1, rounds):
        eta = rng.normal()
        x[index] = x[index - 1] + (dt / tau_c) * (mu - x[index - 1]) + sigma * np.sqrt(dt) * eta
    probabilities = p_max / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))
    errors = rng.random(rounds) < probabilities
    return x, probabilities, errors


def autocorrelation(values, max_lag):
    """Return normalized empirical autocorrelation for lags 0..max_lag."""
    centered = np.asarray(values, dtype=float) - np.mean(values)
    denominator = np.dot(centered, centered)
    if denominator == 0:
        return np.zeros(max_lag + 1)
    return np.array([
        np.dot(centered[: len(centered) - lag], centered[lag:]) / denominator
        for lag in range(max_lag + 1)
    ])


def memory_fraction(decoder_rounds, dt, tau_c):
    """Fraction F(T)=1-exp(-T/tau_c) captured by a decoder window."""
    return 1.0 - np.exp(-(decoder_rounds * dt) / tau_c)


def plain_language(tau_c, dt, decoder_rounds, sigma, mean_probability, error_count):
    ratio = tau_c / dt
    fraction = memory_fraction(decoder_rounds, dt, tau_c)
    return (
        f"The noise remembers roughly {ratio:.1f} QEC rounds. "
        f"A decoder window of {decoder_rounds} rounds captures about {fraction:.1%} "
        f"of the exponential memory. With fluctuation strength sigma={sigma:.3g}, "
        f"the average sampled error probability is {mean_probability:.3%}; "
        f"{error_count} error events appeared in this displayed trace."
    )


st.set_page_config(page_title="OU noise explorer", layout="wide")
st.title("OU correlated-noise explorer")
st.caption("Change one control and see how temporal memory changes the error process.")

with st.sidebar:
    st.header("Model controls")
    rounds = st.slider("Displayed QEC rounds", 20, 500, 120, 10)
    dt = st.number_input("Round duration Delta t", min_value=0.01, max_value=10.0, value=1.0, step=0.1)
    tau_c = st.slider("Correlation time tau_c (time units)", 0.1, 100.0, 10.0, 0.1)
    mu = st.slider("Mean OU level mu", -6.0, 6.0, -4.0, 0.1)
    sigma = st.slider("Fluctuation strength sigma", 0.0, 3.0, 0.8, 0.05)
    p_max = st.slider("Maximum error probability p_max", 0.001, 0.2, 0.02, 0.001)
    decoder_rounds = st.slider("Decoder memory T (rounds)", 1, 100, 10)
    seed = st.number_input("Random seed", min_value=0, max_value=999_999, value=7, step=1)

x, probabilities, errors = simulate_ou(
    int(rounds), float(dt), float(tau_c), float(mu), float(sigma), float(p_max), int(seed)
)
round_index = np.arange(1, int(rounds) + 1)
trace = pd.DataFrame(
    {"OU level x": x, "Error probability p": probabilities, "Error event": errors.astype(int)},
    index=round_index,
)

capture = memory_fraction(int(decoder_rounds), float(dt), float(tau_c))
col1, col2, col3 = st.columns(3)
col1.metric("Correlation length", f"{tau_c / dt:.2f} rounds")
col2.metric("Memory captured by T", f"{capture:.1%}")
col3.metric("Mean displayed p", f"{probabilities.mean():.3%}")

st.subheader("What changes across rounds?")
st.line_chart(trace[["OU level x", "Error probability p"]], height=320)
st.caption("The OU level moves gradually. The sigmoid converts that level into a probability; it is not itself an error event.")

st.subheader("Random error events")
st.bar_chart(trace["Error event"], height=160)
st.caption("Each round draws an event with Bernoulli probability p for that round. A high p makes events more likely, not guaranteed.")

max_lag = min(50, int(rounds) - 1)
empirical = autocorrelation(x, max_lag)
lags = np.arange(max_lag + 1)
correlation_frame = pd.DataFrame(
    {
        "Measured autocorrelation": empirical,
        "Target exp(-lag*Delta t/tau_c)": np.exp(-lags * float(dt) / float(tau_c)),
    },
    index=lags,
)
st.subheader("Does the generated noise have the requested memory?")
st.line_chart(correlation_frame, height=300)
st.caption("The measured curve is noisy because this is one finite random trace. Run with more displayed rounds or another seed to check the trend.")

memory_rounds = np.arange(1, 101)
memory_frame = pd.DataFrame(
    {"Captured memory F(T)": 1.0 - np.exp(-(memory_rounds * float(dt)) / float(tau_c))},
    index=memory_rounds,
)
st.subheader("How decoder memory T changes what it can see")
st.line_chart(memory_frame, height=260)
st.caption(f"At T={decoder_rounds} rounds, the model captures {capture:.1%} of the ideal exponential memory. This is a memory-coverage measure, not a logical-error rate.")

st.info(plain_language(tau_c, dt, decoder_rounds, sigma, probabilities.mean(), int(errors.sum())))

with st.expander("Equations used"):
    st.latex(r"x_{r+1}=x_r+\frac{\Delta t}{\tau_c}(\mu-x_r)+\sigma\sqrt{\Delta t}\,\eta_r")
    st.latex(r"p_r=p_{\max}\frac{1}{1+e^{-x_r}}")
    st.latex(r"e_r\sim\mathrm{Bernoulli}(p_r)")
    st.latex(r"C(k)=e^{-k\Delta t/\tau_c},\qquad F(T)=1-e^{-T\Delta t/\tau_c}")
