# Pool Chemistry Analyzer

A 3-tab Streamlit app for tracking one pool's weekly water chemistry:
upload your own readings, see a traffic-light view of the current state,
and chart how each parameter has trended over time.

## Run it

```bash
uv run streamlit run app.py
```

## Regenerate the synthetic demo data

```bash
uv run python -m data_gen
```

Writes 260 weekly readings (5 years) to `data/pool_chemistry_history.csv`,
plus a header-only `data/csv_upload_template.csv` for the upload tab.

## Layout

- `app.py` — Streamlit entry point, wires up the 3 tabs.
- `thresholds.py` — the single source of truth for green/yellow/red bands,
  shared by the generator and the UI.
- `tabs/` — one module per tab (upload, current state, history).
- `data_gen/` — synthetic data generation logic (`uv run python -m data_gen`).
- `data/` — generated CSVs.

## Roadmap

Not built yet — the current app is upload/CSV-driven only. Planned next:

1. **Bluetooth reading tab.** A 4th tab that pairs with a Bluetooth pool
   test device and pulls a live reading directly into the app, instead of
   requiring a CSV export first. That reading would append to the same
   history schema `thresholds.py` and the CSV upload already use, so
   Current State and Historical Trends need no changes to consume it.
2. **AI summary on the Current State tab.** An agentic feature that sends
   the latest reading (and recent trend) to an LLM and renders a
   plain-language summary of the pool's state alongside the traffic-light
   cards — going beyond "red/yellow/green" into "here's what's actually
   going on and why."
3. **AI Pool Analyzer chatbot.** A new conversational tab: a pool-chemistry
   expert chatbot with tool access to the current reading and history,
   able to answer questions and give step-by-step dosing guidance (e.g.
   how much muriatic acid to add) grounded in the same threshold bands
   the rest of the app uses.
