# HelioTrace — Architecture & Design Reference

> Stable reference for the project structure and key decisions.
> See CLAUDE.md for rules/conventions/commands.
> See GitHub Issues (or TODO comments) for the active task list.

---

## Repository Layout

```
app.py                              ← thin entry point: st.set_page_config + st.navigation().run()
pages/
  home.py                           ← Home page content (🏠 Home in nav)
  01_Propagation_Simulator.py       ← Propagation Simulator page (🚀 Propagation Simulator in nav)
src/heliotrace/                     ← installable package (pip install -e .)
  __init__.py                       ← exposes __version__ = "0.1.0"
  config.py                         ← TARGET_PRESETS, DEFAULT_GCS_ROWS, DEFAULT_OBS_ROWS, session-state key constants
  models/
    schemas.py                      ← pure dataclasses: GCSParams, TargetConfig, SimulationConfig,
                                       DerivedGCSParams, PropagationSeries, SimulationResults
  physics/
    geometry.py                     ← GCS mesh maths (ported from IDL shellskeleton.pro / cmecloud.pro)
    drag.py                         ← DBM + MODBM ODE engine (sympy removed; closed-form mass formula)
    fitting.py                      ← weighted linear least-squares H-T fit
    apex_ratio.py                   ← geometric CME→target projection factor
  simulation/
    runner.py                       ← physics pipeline orchestrator (zero Streamlit coupling)
  ui/
    state.py                        ← init_session_state() — Streamlit session state bootstrap
    utils.py                        ← shared UI helpers (format_diff, etc.)
    components/
      sidebar_inputs.py             ← renders full sidebar; returns (SimulationConfig, GCSParams, obs_df, run_clicked, gcs_params_entered)
      ht_plot.py                    ← Plotly Height-Time diagram
      gcs_plot.py                   ← Plotly 3D GCS mesh (scipy.spatial.Delaunay)
      propagation_plot.py           ← two-panel DBM vs MODBM comparison chart
tests/
  test_smoke.py                     ← 9 smoke tests (imports, physics unit, full integration)
pyproject.toml                      ← single source of truth for deps + build
Dockerfile                          ← single-stage python:3.11-slim, pip install .
docker-compose.yml                  ← default (prod) + dev profile (targeted volume mounts)
.streamlit/config.toml              ← headless=true, custom red/dark-blue theme
```

---

## Tech Decisions

### Package layout — `src/` layout

Using a true `src/heliotrace/` layout ensures the installed package is always used during
tests, preventing accidental imports of the raw source tree. `pyproject.toml` with
`[tool.setuptools.packages.find] where = ["src"]` is the single authoritative declaration —
no `sys.path` hacks anywhere.

### Dependency pruning

| Removed              | Reason                                                                | Replacement                                                                            |
| -------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `sympy`            | Called `sympy.solve()` at runtime on every simulation run — slow   | Closed-form:`10^(3.4e-4·v + 15.479)`                                                |
| `matplotlib`       | Pulled into Docker image for a single triangulation call              | `scipy.spatial.Delaunay` (already a dep)                                             |
| `DateTime`         | Unused                                                                | —                                                                                     |
| `sunpy` (core)     | Large; only needed for coordinate-frame GCS variant used in notebooks | Optional extra `[notebooks]`; lazy import with error message in `gcs_mesh_sunpy()` |
| `requirements.txt` | Drifted from `pyproject.toml`; caused version conflicts             | Deleted;`pyproject.toml` is single source of truth                                   |

### Docker

- Single-stage `python:3.11-slim` build; no dev tools in prod image.
- Layer order: `pyproject.toml` + `src/` copied first → `pip install` → app files copied;
  minimises cache invalidation on code-only changes.
- `dev` profile in `docker-compose.yml` mounts only `src/`, `app.py`, `pages/` (not the whole
  repo) so installed packages inside the container are never shadowed by the host tree.

---

## Feature Roadmap

- [X] Data pipeline — GCS data via `st.data_editor`
- [X] Simulation engine — DBM + MODBM in `simulation/runner.py`
- [X] UI layer — sidebar inputs, two-tab layout, KPI cards
- [X] GCS 3D plot (Plotly Mesh3d) + H-T plot
- [X] Enterprise refactor — `src/` layout, type hints, logging, Docker, README
- [X] UI/UX polish sprints (2026-02-26 – 2026-02-27)
- [ ] `st.toast` notifications, responsive layout tweaks
- [ ] Multiple events — save/load named event presets (local JSON)
- [ ] Unit test coverage — parametrised physics edge cases, regression tests for calculation results
- [ ] CI — GitHub Actions (lint + pytest on push)
- [ ] Automatic target positions — JPL Horizons via Astropy / SunPy
- [ ] Shareable simulation URL — encode params via `st.query_params`
- [ ] Export results — download CSV/JSON of propagation series
- [ ] Multi-target comparison — run DBM/MODBM for several targets in one session
