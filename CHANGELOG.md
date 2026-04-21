# Changelog

All notable changes to HelioTrace are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.4.0] — 2026-04-21

### Added

#### Application

- **Sidebar Input Rework** — Completely refactored the sidebar component for better modularity, readability, and user feedback.
- **Task Status Indicators** — Visual "LED" markers in the sidebar sections (Event, Target, GCS, Observations, Drag) indicate whether inputs are in a default state (white), ready (green), or missing/incomplete (gray).
- **Interactive Observation Editor** — Stabilized `st.data_editor` for height-time observations, ensuring user edits persist correctly during the session.

#### i18n

- Expanded English and German locales with comprehensive keys for all sidebar sections, tooltips, and validation messages.
- Synchronized translation labels across all UI components.

#### Testing

- **Component Unit Tests** — Added a substantial test suite for sidebar components, including GCS normalization logic and task state computation.
- **i18n Coverage** — Added tests ensuring all locale keys are present and non-empty for both English and German.
- **Integration Tests** — Added smoke tests verifying sidebar behavior and data flow between components.

### Changed

- **Run Simulation Button** — Moved to the top of the sidebar for immediate accessibility, regardless of scroll position.
- **GCS Parameter Normalization** — Longitude, latitude, tilt, and half-angle are now automatically normalized/clamped to valid physical ranges with appropriate user warnings.

### Fixed

- **Sidebar Typing** — Fixed type annotations in sidebar tests to align with project standards.
- **Package Housekeeping** — Removed deprecated `gen-test` SKILL documentation.

---

## [0.3.1] — 2026-04-01

### Changed

#### Application

- **Responsive page header language toggle** — Replaced the previous inline/mobile split language switch with a shared page header helper that adapts cleanly between desktop and mobile layouts while keeping the single-action EN↔DE toggle behavior.

#### i18n

- Extracted deterministic language-toggle metadata into a dedicated helper and kept `render_lang_toggle()` as a compatibility alias for existing page code.

### Fixed

- Added focused tests covering language-toggle props and fallback behavior.
- Synchronized package version metadata with the released application version.

---

## [0.3.0] — 2026-03-25

### Added

#### Application

- **CME Kinematics tab** — New middle tab in the Propagation Simulator extracts the
  height-time diagram and velocity metrics out of the GCS Geometry tab into a dedicated
  dashboard-style view. The tab features enhanced KPI cards (apex velocity with uncertainty,
  projection ratio with HIT/MISS badge, v₀ → target), the height-time plot, and a collapsible
  Fit Details section showing slope, intercept, χ², observation count, and height error.

- **KPI card component** — New `_kpi_card()` HTML helper renders styled dashboard cards with
  a colored left-border accent, label, large value, and optional subtitle. Uses custom CSS
  class names per project convention.

#### i18n

- New locale keys for the kinematics tab and fit detail labels in both EN and DE
  (`tab_kinematics`, `fit_details_subheader`, `fit_detail.*`).

### Fixed

- **Sidebar state lost on language switch** — Observation table no longer reverts to example
  data on every rerun; user edits are preserved in session state and only reset when "Fill
  with example" is explicitly clicked.
- **Widget values reset on language change** — Added explicit `key` parameters to target
  selectbox, custom target inputs (name, lon, lat, dist), and mass override so Streamlit
  retains their values when translated labels change.

### Changed

- **GCS Geometry tab** now shows only the 3D GCS plot; the height-time diagram and velocity
  metrics have moved to the new CME Kinematics tab.
- GCS projection ratio is computed above the tab definitions so all tabs can access it
  without recomputation.
- Tab label shortened from "GCS Geometry & Height-Time" to "GCS Geometry" in both locales.

---

## [0.2.0] — 2026-03-25

### Added

#### Application

- **EN↔DE Language Toggle** — Zero-dependency i18n system supporting English and German
  UI translations. Two flag-emoji buttons (🇬🇧 / 🇩🇪) rendered inline with the page title
  switch the active locale via `st.session_state`; the page reruns to apply the new language
  immediately. All labels, headings, units, and result descriptions are covered by the locale
  dictionaries in `locale/en.py` and `locale/de.py`, resolved through `i18n.py`.

#### Developer Tooling

- **Pre-push quality gates** — Three pre-push hooks added to `.pre-commit-config.yaml`
  enforce quality before changes reach CI: `uv lock --check` (ensures `uv.lock` is in sync
  with `pyproject.toml`), `pyright src/` (type checking), and `pytest` (full test suite).

---

## [0.1.0] — 2026-03-11

Initial public release of HelioTrace — an interactive CME propagation explorer
built on peer-reviewed heliophysics models and developed based on research done in a Master's
Thesis at Georg-August-University Göttingen.

### Features

#### Physics & Science

- **GCS 3D Reconstruction** — Graduated Cylindrical Shell geometry (Thernisien et al. 2006)
  for modeling CME flux-rope shape from coronagraph observations.
- **Kinematic Fitting** — Extract initial CME apex velocity from height-time profiles
  via least-squares fitting.
- **Apex Ratio** — Compute the geometric ratio that maps the CME apex speed to the
  target-directed component (Earth or arbitrary target).
- **Drag-Based Model (DBM)** — ODE-integrated propagation solution (Vršnak et al. 2013)
  with constant solar wind speed and drag parameter.
- **Modified DBM (MoDBM)** — Numerically integrated propagation (Müller 2025) featuring
  distance- and SSN-dependent solar wind profiles (Venzmer & Bothmer 2018),
  extending the standard DBM to variable solar wind conditions.
- **Hit/Miss Detection** — Geometric check determining whether a reconstructed CME
  flux rope intersects a chosen propagation target.
- **Space weather forecasts** — Time of Arrival (ToA), transit time, and impact speed
  for both DBM and MoDBM.

#### Application

- Streamlit-based interactive web app (`app.py`) with declarative multi-page navigation.
- Sidebar-driven input controls for GCS parameters, observations, and propagation settings.
- Tab 1 ("GCS Geometry & Height-Time"): 3D GCS flux-rope visualization (Plotly, grid wireframe
  rendering) with hit/miss indicator, followed by the height-time diagram with linear fit overlay,
  ±velocity uncertainty, χ², and apex velocity / projection ratio / v₀ metrics.
- Tab 2 ("Propagation Results"): side-by-side DBM and MoDBM result panels (arrival time, transit
  time, impact speed), individual single-model trajectory plots, and a full-width combined
  comparison figure overlaying both model trajectories.
- Propagation results panel with ToA, transit time, and arrival speed for both models.
- Fill-example sidebar button for quick demonstration with a pre-loaded event.
- Free-form event label.
- Tab10 color palette and responsive plot sizing.

#### Infrastructure

- `src/heliotrace/` package layout with `physics/`, `models/`, `simulation/`, and `ui/` sub-packages.
- Python dataclass-based data schemas (`models/schemas.py`) for validated parameter passing.
- Simulation runner (`simulation/runner.py`) decoupling physics from the UI layer.
- Centralized configuration (`config.py`) for app defaults, target presets, and default observation data.
- Docker and Docker Compose setup for zero-config deployment and live-reload dev mode.
- `uv`-managed dependency locking (`uv.lock`) for reproducible environments.
- `uv sync --group dev` for development environment setup (pytest, ruff, pyright).

#### Testing

- Analytic test suite for `drag.py` (`test_drag.py`) — 39 functions covering DBM/MoDBM edge cases, unit consistency, ODE stability, and closed-form solutions.
- Simulation runner test suite (`test_runner.py`) — 47 tests across 12 groups (A–L) covering
  slope recovery, unit conversion, geometric miss, coasting benchmarks, override propagation,
  monotone scaling, and reference event regression.
- End-to-end smoke tests (`test_smoke.py`) — module import verification and reference event
  regression for the 2023-10-28 CME event (apex velocity ≈ 773 km/s, DBM transit ≈ 69.4 h).
- `test_geometry.py` — GCS geometry correctness checks.
- `test_fitting.py` — Kinematic fitting analytic benchmarks.
- `test_apex_ratio.py` — Apex ratio boundary and correctness tests.

#### Documentation

- README with science background, four-step physics workflow, model reference table,
  quick-start (Docker) and local development instructions.
- `CONTRIBUTING.md` with development setup and contribution guidelines.
- `THIRD_PARTY_LICENSES.md` attributing the GCS geometry code adapted from
  [gcs_python](https://github.com/johan12345/gcs_python) by Johan von Forstner.
- MIT License.
- Related publication citation (Müller 2025, Zenodo DOI: 10.5281/zenodo.18788366).

### Fixed

- N/A (initial release)

---

[0.3.1]: https://github.com/ennomuller/HelioTrace/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/ennomuller/HelioTrace/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ennomuller/HelioTrace/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ennomuller/HelioTrace/releases/tag/v0.1.0
