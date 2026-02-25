# Project Board: HelioTrace

## 🎯 Context

**Goal**: Create an interactive Space Weather portfolio app using Python & Streamlit.

---

## 📍 Current State (2026-02-25)

**UI overhaul & attribution pass complete.**

- Project renamed from **CME Explorer → HelioTrace** across all UI, titles, and page configs.
- `pages/01_CME_Propagation.py` **split** into two dedicated pages:
  - `pages/01_GCS_Observations.py` — GCS data table, H-T fit, 3D geometry, projection ratio
  - `pages/02_ICME_Propagation.py` — DBM/MODBM simulation, KPI cards, comparison plots
- `app.py` (**Home**) fully rewritten: tagline, capabilities bullets, science background table,
  acknowledgments expander, TODO-tagged data source placeholder.
- `src/heliotrace/config.py` — added `KEY_DERIVED_PARAMS` and `KEY_CLEAN_DF` session-state keys.
- `src/heliotrace/ui/state.py` — initialises the two new session-state keys.
- `src/heliotrace/ui/components/sidebar_inputs.py` — `render_sidebar(show_run_button=True)` parameter
  added so GCS page suppresses the Run button.
- `src/heliotrace/physics/geometry.py` — full `gcs_python` (Johan von Forstner) attribution added
  to module docstring and to `skeleton()` / `gcs_mesh()` function docstrings.
- `THIRD_PARTY_LICENSES.md` — created to document incorporated gcs_python code.
- `README.md` — full rewrite: Features section, clone-first Quick Start, Science Background table,
  Related Publication section (placeholder links), Acknowledgments section.
- `docs/.gitkeep` — placeholder for thesis excerpt PDF.

### Previous state (2026-02-24)

**Enterprise refactor complete.** The project was migrated from an ad-hoc `app/` layout
to a proper `src/heliotrace/` installable package. All 9 smoke tests pass; the old source
tree (`app/`, `gcs/`, `utils/`, `requirements.txt`) has been deleted. Entry point is now
`streamlit run app.py`.

### Repository layout (post-refactor)

```
src/heliotrace/           ← installable package (pip install -e .)
  __init__.py             ← exposes __version__ = "0.1.0"
  config.py               ← TARGET_PRESETS, DEFAULT_GCS_ROWS, session-state key constants
  models/
    schemas.py            ← pure dataclasses: TargetConfig, SimulationConfig,
                             DerivedGCSParams, PropagationSeries, SimulationResults
  physics/
    geometry.py           ← GCS mesh maths (ported from IDL shellskeleton.pro / cmecloud.pro)
    drag.py               ← DBM + MODBM ODE engine (sympy removed; closed-form mass formula)
    fitting.py            ← weighted linear least-squares H-T fit
    apex_ratio.py         ← geometric CME→target projection factor
  simulation/
    runner.py             ← physics pipeline orchestrator (zero Streamlit coupling)
  ui/
    state.py              ← init_session_state() — Streamlit session state bootstrap
    utils.py              ← shared UI helpers (format_diff, etc.)
    components/
      sidebar_inputs.py   ← renders full sidebar, returns (SimulationConfig, bool)
      ht_plot.py          ← Plotly Height-Time diagram
      gcs_plot.py         ← Plotly 3D GCS mesh (scipy.spatial.Delaunay, no matplotlib)
      propagation_plot.py ← two-panel DBM vs MODBM comparison chart
app.py                    ← Home page (branding, capabilities, acknowledgments, science background)
pages/
  01_GCS_Observations.py  ← Page 1: GCS data table, H-T fit, 3D geometry, projection
  02_ICME_Propagation.py  ← Page 2: DBM/MODBM simulation, KPI cards, comparison plots
tests/
  test_smoke.py           ← 9 smoke tests (imports, physics unit, full integration)
pyproject.toml            ← single source of truth for deps + build
Dockerfile                ← single-stage python:3.11-slim, pip install .
docker-compose.yml        ← default (prod) + dev profile (targeted volume mounts)
.streamlit/config.toml    ← headless=true, custom red/dark-blue theme
.env.example              ← documents all env vars
README.md                 ← setup + run instructions
```

### Validation (2026-02-24)

- `pip install -e .` → ✅ resolves all deps, no double-install
- `python -c "import heliotrace; print(heliotrace.__version__)"` → `0.1.0` ✅
- `pytest tests/ -v` → **9/9 passed in 9.18 s** ✅
- End-to-end: 773 km/s apex, ~69.4 h DBM transit to Earth (2023-10-28 event) ✅

---

## 🛠️ Tech Decisions & Design Rationale

### Package layout — `src/` layout

Using a true `src/heliotrace/` layout (not `heliotrace/` at root) ensures the installed
package is always used during tests, preventing accidental imports of the raw source tree.
`pyproject.toml` with `[tool.setuptools.packages.find] where = ["src"]` is the single
authoritative declaration — no `sys.path` hacks anywhere.

### Dependency pruning

| Removed              | Reason                                                                | Replacement                                                                            |
| -------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `sympy`            | Called `sympy.solve()` at runtime on every simulation run — slow   | Closed-form:`10^(3.4e-4·v + 15.479)`                                                |
| `matplotlib`       | Pulled into Docker image for a single triangulation call              | `scipy.spatial.Delaunay` (already a dep)                                             |
| `DateTime`         | Unused                                                                | —                                                                                     |
| `sunpy` (core)     | Large; only needed for coordinate-frame GCS variant used in notebooks | Optional extra `[notebooks]`; lazy import with error message in `gcs_mesh_sunpy()` |
| `requirements.txt` | Drifted from `pyproject.toml`; caused version conflicts             | Deleted;`pyproject.toml` is single source of truth                                   |

### Layer separation

```
models/schemas.py    ← pure data; no imports from physics or UI
physics/*            ← pure functions; no Streamlit, no pandas — numpy/scipy only
simulation/runner.py ← orchestrates physics; accepts dataclasses, returns dataclasses
ui/*                 ← all Streamlit; imports from physics/simulation but never vice-versa
app.py / pages/*     ← thin glue; calls ui layer only
```

This hierarchy means physics can be unit-tested independently of Streamlit, and the
simulation can be re-used from a CLI or notebook without importing any UI code.

### Code quality conventions (applied throughout `src/`)

- **`logging` module** everywhere — `logger = logging.getLogger(__name__)` at module top; no bare `print()` calls
- **Type hints** on every function signature (`numpy.typing.ArrayLike`, `Optional`, dataclass types)
- **Private helpers** prefixed with `_` (e.g., `_dr_dt_DBM`, `_dr_dt_MODBM`, `_sample_solution`)
- **`@st.cache_data`** on `_cached_derived_params()` in the page to avoid recomputing GCS geometry on every widget interaction

### Docker

- Single-stage `python:3.11-slim` build; no dev tools in prod image
- Layer order: `pyproject.toml` + `src/` copied first → `pip install` → app files copied; minimises cache invalidation on code-only changes
- `dev` profile in `docker-compose.yml` mounts only `src/`, `app.py`, `pages/` (not the whole repo) so installed packages inside the container are never shadowed by the host tree

---

## 🚀 Feature Roadmap

- [X] **Data Pipeline**: GCS data entered via `st.data_editor` table
- [X] **Simulation Engine**: DBM + MODBM fully ported to `simulation/runner.py`
- [X] **UI Layer**: Page 1 (GCS Observations, live) / Page 2 (ICME Propagation, button-triggered)
- [X] **GCS 3D Plot**: Plotly Mesh3d with projection point indicator
- [X] **H-T Plot**: Plotly scatter + linear fit + velocity annotation
- [X] **KPI cards**: Transit time, impact speed, arrival time, ΔToA vs expected
- [X] **Enterprise refactor**: `src/` layout, type hints, logging, tests scaffold, Docker, README
- [X] **Branding**: Renamed CME Explorer → HelioTrace globally; updated README + all page configs
- [X] **Attribution**: gcs_python (Johan von Forstner) documented in geometry.py, THIRD_PARTY_LICENSES.md, README, and app.py Home page
- [X] **Page split**: GCS Observations (page 1) + ICME Propagation (page 2); session-state cross-page data flow via KEY_DERIVED_PARAMS / KEY_CLEAN_DF
- [ ] **Polish**: `st.toast` notifications, responsive layout tweaks
- [ ] **Multiple events**: Save/load named event presets (local JSON or `st.session_state` export)
- [ ] **Unit test coverage**: Expand `tests/` beyond smoke — parametrised physics edge cases, and importantly results of calculation methods so future changes don't introduce unexpected inaccuracies that are hard to trace, at least for (but not limited to) the following:
  - [ ] on a mini
- [ ] **CI**: GitHub Actions workflow (lint + pytest on push)

---

## 🧠 Scratchpad / Notes

*(Dump temporary info here: bug descriptions, ideas for future features, or reminders)*
-------------------------------------------------------------------------------------
