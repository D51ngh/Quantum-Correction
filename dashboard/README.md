# Interactive dashboards

Click here to open the browser dashboard directly:

[Open the interactive HTML dashboard](https://htmlpreview.github.io/?https://github.com/D51ngh/Quantum-Correction/blob/main/dashboard/noise_dashboard.html)

If the preview service is unavailable, enable GitHub Pages and use the direct
site URL:

`https://d51ngh.github.io/Quantum-Correction/dashboard/noise_dashboard.html`

The HTML page is a browser-only preview. It does not run Stim or MWPM.

OU model explainer (browser-only):

[Open the OU correlated-noise explorer](https://htmlpreview.github.io/?https://github.com/D51ngh/Quantum-Correction/blob/main/dashboard/ou_noise_explorer.html)

For the real Python simulation dashboard, run this from the repository root:

```bash
streamlit run dashboard/noise_dashboard.py
```

For the separate OU correlated-noise learning dashboard, run:

```bash
streamlit run dashboard/ou_noise_explorer.py
```

It visualizes the Euler–Maruyama OU equation, the sigmoid mapping to a
time-varying error probability, Bernoulli error events, exponential
autocorrelation, and decoder-memory coverage. It is an educational model
explorer; it does not yet implement correlation-aware MWPM.
