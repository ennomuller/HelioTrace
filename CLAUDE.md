# Project: HelioTrace

Interactive CME propagation modelling — DBM & MODBM.
Streamlit portfolio app; source in `src/heliotrace/`.

## Stack

- Language: Python 3.11
- Framework: Streamlit ~1.41
- Plotting: Plotly
- Physics: numpy, scipy, astropy
- Data: pandas
- Test runner: pytest
- Linter: ruff (line-length 100, rules E/F/W/I)
- Type checker: pyright (basic mode)

## Layer Hierarchy

Strict — never import upward across layers.

```
models/schemas.py    ← pure dataclasses; no imports from physics or ui
physics/*            ← pure functions; numpy/scipy only, no Streamlit
simulation/runner.py ← orchestrates physics; no Streamlit
ui/*                 ← all Streamlit; imports physics/simulation
app.py / pages/*     ← thin glue; calls ui layer only
```

## Key Files

- `src/heliotrace/models/schemas.py` — dataclasses: `GCSParams`, `SimulationConfig`, `SimulationResults`, etc.
- `src/heliotrace/config.py` — presets, defaults, session-state key constants
- `src/heliotrace/ui/components/sidebar_inputs.py` — full sidebar renderer; returns `(SimulationConfig, GCSParams, obs_df, run_clicked, gcs_params_entered)`
- `pages/01_Propagation_Simulator.py` — main simulation page
- `tests/test_smoke.py` — 9 smoke tests (must stay green)

## Conventions

- `logging.getLogger(__name__)` at module top — no bare `print()` calls
- Type hints on every function signature (`numpy.typing.ArrayLike`, `Optional`, dataclass types)
- Private helpers prefixed with `_`
- `@st.cache_data` on expensive computations
- Streamlit widget keys use `sb_*` prefix for sidebar inputs
- All deps declared in `pyproject.toml` — no `requirements.txt`

## Rules

- Never modify `.venv/` or anything outside `src/`, `pages/`, `app.py`, `tests/` without asking first
- Run `pytest tests/ -v` after any change to `src/` or `tests/`
- No new dependencies without explicit approval
- `physics/` must never import `streamlit`
- `models/schemas.py` must stay pure data (no imports from physics or ui)

## Common Commands

- Dev server:    `streamlit run app.py`
- Tests:         `pytest tests/ -v`
- Lint:          `ruff check src/`
- Type check:    `pyright src/`
- Install (dev): `pip install -e ".[dev]"`

## UI Conventions

- KPI / result cards use `st.metric` uniformly — do not mix with raw `st.markdown` HTML size hacks
- Inline parameter descriptions in expanders use parenthetical plain text, not custom tooltip widgets
- Sidebar model-selection labels must be human-readable and descriptive; string literals used in comparisons must be updated in sync across all files when renamed
- `st.divider()` is the standard spacer between major result sections
