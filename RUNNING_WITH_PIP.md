# Running with pip + venv (macOS)

The project's default workflow uses `uv` (see [README.md](README.md)). If you'd
rather use a plain `pip` + `venv` setup — e.g. on a Mac without `uv` installed —
follow the steps below from the project root.

```bash
python3 --version
```
Confirms which Python you have and that it meets the project's requirement of
**3.12+** (see `requires-python` in `pyproject.toml`). If this prints an older
version, install 3.12+ first (e.g. `brew install python@3.12`) and use that
binary in the next step.

```bash
python3 -m venv .venv
```
Creates an isolated virtual environment in a local `.venv/` folder, so the
packages this app needs don't get installed into your system/global Python.

```bash
source .venv/bin/activate
```
Activates the virtual environment for your current shell session — your
prompt should now show `(.venv)`. All `pip install` and `python`/`streamlit`
commands after this point run inside that isolated environment. Run
`deactivate` any time to leave it.

```bash
pip install "numpy>=2.5.2" "pandas>=3.0.5" "plotly>=6.9.0" "streamlit>=1.61.1"
```
Installs the app's dependencies directly, matching the versions declared in
`pyproject.toml`. (`pip install -e .` isn't used here — this project has no
`[build-system]` config, and setuptools' automatic package discovery trips
over the app's loose top-level folders (`tabs/`, `data/`, `data_gen/`) when
asked to build it as an installable package.)

```bash
streamlit run app.py
```
Starts the Streamlit dev server and opens the app in your browser (usually at
`http://localhost:8501`).

## Regenerating the demo data

Same as the `uv` workflow, just without the `uv run` prefix:

```bash
python -m data_gen
```
