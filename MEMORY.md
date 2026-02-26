# Project Board: HelioTrace

## 🎯 Context

**Goal**: Create an interactive Space Weather portfolio app using Python & Streamlit.
**Source Material**: Jupyter notebooks in `notebooks/` contain the raw science logic.

---

## 📍 Current State (2026-02-26)

**UI Refactor sprint complete (GCS sidebar + reactive plots).** The five GCS geometric
parameters now live as `st.number_input` fields in the sidebar (with tooltips and
out-of-range validation). The observation data table is compact (datetime + height
only) and also lives in the sidebar. Tab 1 of the main page is now fully reactive:
the 3D GCS model renders automatically from the sidebar params (height=1, normalised),
and the H-T diagram + velocity metric appear as soon as ≥2 observations are present.
A new `GCSParams` dataclass cleanly separates the five geometric inputs from
`SimulationConfig`. All 9 smoke tests still pass.

**Previous: Housekeeping sprint complete.** Navigation uses `st.navigation()` (Streamlit ≥ 1.36);
home page content lives in `pages/home.py`; `app.py` is a thin 25-line host. All
"CME Explorer" internal name remnants replaced with "HelioTrace". `geometry.py`
now credits `gcs_python` by name. 27 `__pycache__`/`egg-info` artefacts de-indexed
from git. All 9 smoke tests pass.

### Repository layout (post-housekeeping)

```
app.py                   ← thin entry point: st.set_page_config + st.navigation().run()
pages/
  home.py               ← Home page content (🏠 Home in nav)
  01_CME_Propagation.py ← Propagation Simulator page (🚀 Propagation Simulator in nav)
src/heliotrace/           ← installable package (pip install -e .)
  __init__.py             ← exposes __version__ = "0.1.0"
  config.py               ← TARGET_PRESETS, DEFAULT_GCS_ROWS, DEFAULT_OBS_ROWS, session-state key constants
  models/
    schemas.py            ← pure dataclasses: GCSParams, TargetConfig, SimulationConfig,
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
      sidebar_inputs.py   ← renders full sidebar, returns (SimulationConfig, GCSParams, obs_df, bool)
                             GCS params + Advanced expander (height error) + compact obs table
      ht_plot.py          ← Plotly Height-Time diagram
      gcs_plot.py         ← Plotly 3D GCS mesh (scipy.spatial.Delaunay, no matplotlib)
      propagation_plot.py ← two-panel DBM vs MODBM comparison chart
app.py                    ← clean entry point (no sys.path hacks)
pages/
  01_CME_Propagation.py   ← main simulation page
tests/
  test_smoke.py           ← 9 smoke tests (imports, physics unit, full integration)
pyproject.toml            ← single source of truth for deps + build
Dockerfile                ← single-stage python:3.11-slim, pip install .
docker-compose.yml        ← default (prod) + dev profile (targeted volume mounts)
.streamlit/config.toml    ← headless=true, custom red/dark-blue theme
.env.example              ← documents all env vars
README.md                 ← setup + run instructions
```

### Validation (2026-02-26)

- `pip install -e .` → ✅ resolves all deps, no double-install
- `python -c "import heliotrace; print(heliotrace.__version__)"` → `0.1.0` ✅
- `pytest tests/ -v` → **9/9 passed in 4.21 s** ✅
- End-to-end: 773 km/s apex, ~69.4 h DBM transit to Earth (2023-10-28 event) ✅
- `streamlit run app.py` → navigation shows **🏠 Home** and **🚀 Propagation Simulator** ✅

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
- [X] **UI Layer**: Two-tab layout — Tab 1 (geometry, live) / Tab 2 (propagation, button-triggered)
- [X] **GCS 3D Plot**: Plotly Mesh3d with projection point indicator
- [X] **H-T Plot**: Plotly scatter + linear fit + velocity annotation
- [X] **KPI cards**: Transit time, impact speed, arrival time, ΔToA vs expected
- [X] **Enterprise refactor**: `src/` layout, type hints, logging, tests scaffold, Docker, README
- [X] **GCS UI Refactor (2026-02-26)**:
  - `GCSParams` dataclass added to `models/schemas.py` (lon, lat, tilt, half_angle, kappa)
  - `DEFAULT_OBS_ROWS` added to `config.py` (compact datetime + height only)
  - Sidebar rebuilt: 5 GCS `st.number_input` fields with tooltips + out-of-range
    `st.warning` feedback; height error moved into `st.expander("🔧 Advanced")`;
    compact `st.data_editor` observation table (datetime + height columns only)
  - `render_sidebar()` now returns `(SimulationConfig, GCSParams, obs_df, run_clicked)`
  - Tab 1 (`01_CME_Propagation.py`) fully reactive — no button required:
    - GCS 3D model always visible (height=1 normalised, projection ratio computed live)
    - H-T diagram + `st.metric` velocity result shown when ≥2 obs rows populated
    - `clean_df` assembled by broadcasting GCS params across obs rows (compatible with
      existing `derive_gcs_params()` and `run_full_simulation()` signatures)
  - Tab 2 propagation runner guarded against missing observations
- [X] **Housekeeping sprint (2026-02-26)**:
  - `st.navigation()` host — page labels **🏠 Home** / **🚀 Propagation Simulator**
  - Home page content moved to `pages/home.py`; `app.py` is 25-line thin host
  - All "CME Explorer" internal strings → "HelioTrace"
  - `geometry.py` docstring now credits `gcs_python` (Johan von Forstner) by name
  - `format="%.1f"` added to lon/lat `st.number_input` widgets
  - 27 `__pycache__` / `egg-info` artefacts de-indexed from git (`git rm --cached`)
- [ ] **Polish**: `st.toast` notifications, responsive layout tweaks
- [ ] **Multiple events**: Save/load named event presets (local JSON or `st.session_state` export)
- [ ] **Unit test coverage**: Expand `tests/` beyond smoke — parametrised physics edge cases, and importantly results of calculation methods so future changes don't introduce unexpected inaccuracies that are hard to trace, at least for (but not limited to) the following:
  - [ ] on a mini
- [ ] **CI**: GitHub Actions workflow (lint + pytest on push)
- [ ] **Live target positions**: Replace static `st.caption` placeholder with JPL Horizons lookup via Astropy `get_body_barycentric` or SunPy `get_horizons_coord` (TODO comment already in `pages/home.py`)
- [ ] **Shareable simulation URL**: Encode params in query string via `st.query_params`
- [ ] **Export results**: Download CSV / JSON of propagation series from Tab 2
- [ ] **Multi-target comparison**: Run DBM/MODBM for several targets in a single session

---

## 🧠 Scratchpad / Notes

*(Dump temporary info here: bug descriptions, ideas for future features, or reminders)*
-------------------------------------------------------------------------------------
