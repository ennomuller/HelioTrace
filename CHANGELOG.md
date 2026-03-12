# Changelog

All notable changes to HelioTrace are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
- **Drag-Based Model (DBM)** — Analytical propagation solution (Vršnak et al. 2013)
  with constant solar wind speed.
- **Modified DBM (MoDBM)** — Numerically integrated propagation featuring
  distance- and SSN-dependent solar wind profiles (Venzmer & Bothmer 2018),
  extending the standard DBM to variable solar wind conditions.
- **Hit/Miss Detection** — Geometric check determining whether a reconstructed CME
  flux rope intersects a chosen propagation target.
- **Space weather forecasts** — Time of Arrival (ToA), transit time, and impact speed
  for both DBM and MoDBM.

#### Application

- Streamlit-based interactive web app (`app.py`) with declarative multi-page navigation.
- Sidebar-driven input controls for GCS parameters, observations, and propagation settings.
- Tab 1: interactive 3D GCS flux-rope visualization (Plotly, grid wireframe rendering).
- Tab 2: height-time plot with kinematic fit overlay and projection indicators.
- Tab 3: side-by-side DBM / MoDBM trajectory and kinematics comparison plots.
- Propagation results panel with ToA, transit time, and arrival speed for both models.
- Fill-example sidebar button for quick demonstration with a pre-loaded event.
- Free-form event label (replaces the previous YYYYMMDD-only constraint).
- Tab10 color palette and responsive plot sizing for consistent visual style.

#### Infrastructure

- `src/heliotrace/` package layout with `physics/`, `models/`, `simulation/`, and `ui/` sub-packages.
- Pydantic-based data schemas (`models/schemas.py`) for validated parameter passing.
- Simulation runner (`simulation/runner.py`) decoupling physics from the UI layer.
- Centralized configuration (`config.py`) for physical constants and app defaults.
- Docker and Docker Compose setup for zero-config deployment and live-reload dev mode.
- `uv`-managed dependency locking (`uv.lock`) for reproducible environments.
- `pip install -e ".[dev]"` extras for development and testing.

#### Testing

- Analytic test suite for `drag.py` — 39 functions covering DBM/MoDBM edge cases,
  unit consistency, ODE stability, and closed-form solutions.
- `test_geometry.py` — GCS geometry correctness checks.
- `test_fitting.py` — Kinematic fitting regression tests.
- `test_apex_ratio.py` — Apex ratio boundary and correctness tests.

#### Documentation

- README with science background, four-step physics workflow, model reference table,
  quick-start (Docker) and local development instructions.
- `THIRD_PARTY_LICENSES.md` attributing the GCS geometry code adapted from
  [gcs_python](https://github.com/johan12345/gcs_python) by Johan von Forstner.
- MIT License.
- Related publication citation (Müller 2025, Zenodo DOI: 10.5281/zenodo.18788366).

### Fixed

- N/A (initial release)

---

[0.1.0]: https://github.com/ennomuller/HelioTrace/releases/tag/v0.1.0
