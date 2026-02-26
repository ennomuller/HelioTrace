# Project Board: HelioTrace

## 🎯 Context

**Goal**: Create an interactive Space Weather portfolio app using Python & Streamlit.
**Source Material**: Jupyter notebooks in `notebooks/` contain the raw science logic.

---

## 📍 Current State (2026-02-26)

**Plotting Polish Sprint complete.** Tab10 colour palette, legends repositioned above
axes, responsive figure sizing, and comparison-plot legend centering fixes applied.
All 9 smoke tests still pass.

**Previous: UI/UX refinements sprint complete.** Plotting, sidebar, and page-structure polish
pass applied on top of the previous UI/UX polish sprint.  All 9 smoke tests still pass.

**Previous: UI/UX polish sprint complete.** Major improvements to sidebar compactness, results
presentation, and plot readability.  All 9 smoke tests still pass.

**Previous: UI Refactor sprint complete (GCS sidebar + reactive plots).** The five GCS
geometric parameters now live as `st.number_input` fields in the sidebar (with tooltips
and out-of-range validation). The observation data table is compact (datetime + height
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
  01_Propagation_Simulator.py ← Propagation Simulator page (🚀 Propagation Simulator in nav)
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
      sidebar_inputs.py   ← renders full sidebar, returns (SimulationConfig, GCSParams, obs_df, run_clicked, gcs_params_entered)
                             GCS params (value=None/empty by default; placeholders show valid ranges)
                             + Advanced expander (height error) + compact obs table
                             Emojis: 🐚 GCS Parameters, 🪂 Drag Parameters
                             Section dividers: st.divider() before each of the 5 main subheaders
                             "Shared"/"DBM only"/"MODBM only" labels use st.markdown (black, not grey)
      ht_plot.py          ← Plotly Height-Time diagram
      gcs_plot.py         ← Plotly 3D GCS mesh (scipy.spatial.Delaunay, no matplotlib)
      propagation_plot.py ← two-panel DBM vs MODBM comparison chart
app.py                    ← clean entry point (no sys.path hacks)
pages/
  01_Propagation_Simulator.py ← main simulation page (renamed from 01_CME_Propagation.py)
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
- [X] **UI/UX Polish Sprint (2026-02-26)**:
  - **"Fill with example" button** — primary-styled button at top of sidebar; writes the
    2023-10-28 Halloween CME event into all `sb_*` session-state keys and increments
    `sb_editor_counter` to reinitialise the observation data editor from `DEFAULT_OBS_ROWS`.
    By default the sidebar fields are empty / neutral so the app opens clean.
  - **Drag param grouping** — section split into three labelled blocks using `st.caption`:
    *Shared*, *DBM only*, *MODBM only*; c_d is listed first (shared), then w slider, then
    w_type radio + SSN slider.
  - **SSN slider** — step changed from 5 → 1.
  - **Compact sidebar** — `st.header` → `st.subheader` throughout; most inter-section
    `st.divider()` calls removed (only one remains before the Run button); GCS lon/lat/tilt
    packed into a 3-column row, half-angle + κ into a 2-column row; height error moved out
    of the Advanced expander into the main GCS section; `st.info` on obs count → lighter
    `st.caption`; dead duplicate function body removed from `sidebar_inputs.py`.
  - **Keyed widgets** — every widget now carries a `key="sb_*"` so the fill-example button
    can target them via session state; observation table uses a dynamic `f"obs_editor_{counter}"`
    key to support forced reinitialisation.
  - **Results rework (Tab 2)** — side-by-side `st.columns(2)` layout (DBM | MODBM):
    - Compact metric row (Transit / Impact / Arrival) + optional ΔToA metric per model.
    - Collapsed `st.expander("Inputs used — {model}")` listing all relevant parameters.
    - Per-model dual-y-axis Plotly figure (`build_single_model_figure` in
      `propagation_plot.py`): distance [R☉] on left axis, velocity [km/s] on right,
      arrival vline + target hline annotations.
    - Full-width combined comparison chart below the columns; legend repositioned to
      horizontal centre-bottom (`x=0.5, orientation="h"`) so labels for both models are
      equidistant from each panel.
  - **Font sizes** — axis titles, tick labels, annotations, and legend text increased by
    1–2 pt across `ht_plot.py`, `gcs_plot.py`, and `propagation_plot.py`.
  - `PLOT_COLORS` public alias exported from `propagation_plot.py` for use in page modules.
- [X] **UI/UX Refinements Sprint (2026-02-26)**:
  - **Page renamed**: `01_CME_Propagation.py` → `01_Propagation_Simulator.py` (nav title already matched); `app.py` path updated.
  - **GCS empty-state**: all five GCS `st.number_input` fields now use `value=None` and `placeholder` text showing the valid range; before any value is entered the 3D plot section shows an `st.info` hint instead; `proj_ratio` / `target_hit_geometry` default to 0 / False so the H-T metrics section still renders correctly; `render_sidebar()` returns a 5-tuple with a new `gcs_params_entered: bool`.
  - **Sidebar emojis**: 🔭 → 🐚 (GCS Parameters), 🌬️ → 🪂 (Drag Parameters).
  - **Sidebar spacing**: `st.divider()` added before each of the 5 major subheaders (Event Info, Target, GCS Parameters, Observations, Drag Parameters) plus the existing one above the Run button.
  - **Section-label typography**: "Shared — DBM & MODBM", "DBM only", "MODBM only" changed from `st.caption` (grey) to `st.markdown` (black); descriptive captions below subheaders remain as-is.
  - **Inputs-used expanders**: removed `**bold**` from `w` and `w_type` lines only; all other variables unchanged.
  - **Single-model H-T/V-T plots** (`build_single_model_figure`):
    - Legend enabled (`showlegend=True`) with descriptive trace labels `"Distance [R☉] (label)"` / `"Velocity [km/s] (label)"`.
    - Target hline annotation moved to top-center: added as a separate `fig.add_annotation(xref="paper", x=0.5, xanchor="center", yanchor="bottom")` instead of the inline `annotation_position="bottom right"`.
    - Arrival vline colour changed from model colour to `#9B59B6` (purple — `_COLORS["arrival"]`), and `annotation_yshift=8` applied to nudge label slightly higher.
  - **Comparison plot** (`build_propagation_comparison_figure`):
    - Arrival vlines extracted from `_add_model` inner function; added separately after both models so earlier-arriving model gets `"top left"` annotation, later-arriving gets `"top right"` (no overlap); vlines now appear in **both** panels (col 1 unannotated, col 2 annotated).
    - Target hline annotation replaced with a separate `fig.add_annotation(xref="paper", x=0.225)` centred over col 1 (left subplot).
- [X] **Plotting Polish Sprint (2026-02-26)**:
  - **Tab10 colour palette** — `_COLORS` in `propagation_plot.py` and hardcoded hex values in `ht_plot.py` replaced with standard `tab10` values (`DBM=#1f77b4`, `MODBM=#ff7f0e`, `target=#2ca02c`, `arrival=#d62728`; HT fit line `#1f77b4`, scatter points `#d62728`).
  - **Legends above axes** — `build_single_model_figure` legend moved to `y=1.02, yanchor="bottom"` with `margin t=50, b=30`; `build_propagation_comparison_figure` legend moved to `y=1.05, yanchor="bottom"` with `margin t=70, b=50`; eliminates overlap with y-axis labels.
  - **Responsive sizing** — `build_single_model_figure` default height raised 320 → 420 px; `build_ht_figure` gains explicit `height=480` in `update_layout`.
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
