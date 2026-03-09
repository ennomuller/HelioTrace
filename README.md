# ☀️ HelioTrace — Interactive CME Propagation Explorer

An interactive Streamlit application for modelling the propagation of
**Interplanetary Coronal Mass Ejections (ICMEs)** through the inner heliosphere
using the **Drag-Based Model (DBM)** and the **MOdified DBM (MODBM)**.

Developed as part of a Master's Thesis — see [Related Publication](#-related-publication).

---

## ✨ Features

- 📋 **Interactive GCS data table** — enter multi-epoch coronagraph height-time observations
- 📐 **Height-Time fit** — weighted linear least-squares with velocity annotation and error bars
- 🌐 **Live 3D GCS geometry** — Plotly Mesh3d visualisation of the CME flux-rope shell
- 🎯 **Geometric hit/miss check** — projection ratio and initial velocity toward any heliospheric target
- 🌬️ **DBM** — fast analytic Drag-Based Model with configurable constant solar wind speed
- 🔬 **MODBM** — Modified DBM with distance- and SSN-dependent solar wind density (solved numerically)
- 📊 **Comparison plots** — side-by-side Distance-vs-Time and Velocity-vs-Time for both models
- 🕐 **Arrival prediction** — transit time, impact speed, and ΔToA vs expected observation

---

## Quick Start — Docker

The fastest way to run the app with zero local setup:

```bash
# 1. Clone the repository
git clone https://github.com/ennomuller/HelioTrace.git
cd HelioTrace

# 2. Start the app
docker-compose up
```

Then open <http://localhost:8501> in your browser.

For a live-reload development session:

```bash
docker-compose --profile dev up
```

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/ennomuller/HelioTrace.git
cd HelioTrace
```

### 2. Install the package

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows PowerShell

# Core app
pip install -e .

# With notebook extras (sunpy, matplotlib)
pip install -e ".[notebooks]"

# With dev/test extras
pip install -e ".[dev]"
```

### 3. Run the app

```bash
streamlit run app.py
```

### 4. Run tests

```bash
pytest
```

---

## 🔬 Science Background

CMEs are large-scale eruptions of magnetised plasma from the Sun's corona.
When directed toward Earth or other targets in the inner heliosphere, their arrival
can trigger geomagnetic storms — making accurate transit-time forecasting a core challenge
in operational space weather.  HelioTrace chains three physics components:

| Component | Model | What it enables |
|---|---|---|
| **3D CME shape** | GCS — Graduated Cylindrical Shell ([Thernisien et al. 2006](https://doi.org/10.1086/508254)) | Live 3D mesh, initial velocity, and projection ratio from multi-epoch coronagraph data |
| **Constant-drag propagation** | DBM ([Vršnak et al. 2013](https://doi.org/10.1007/s11207-012-0035-4)) | Fast analytic transit-time estimate with a single solar wind speed parameter |
| **Physics-enhanced propagation** | MODBM (density profile from [Venzmer & Bothmer 2018](https://doi.org/10.1051/0004-6361/201731831)) | Numerically integrated solution with distance- and SSN-dependent solar wind |

The **target-directed velocity** is derived from the apex velocity by self-similar
expansion scaling: v_target = v_apex × (h_target / h_apex),
where the height ratio is extracted directly from the GCS geometry.

---

## 📄 Related Publication

This application was developed as part of a Master's Thesis at **[University — placeholder]**.

- 📖 [Full Thesis](...)  ← placeholder link
- 📄 [Thesis Excerpt (PDF)](docs/thesis_excerpt.pdf)  ← to be added to `docs/`

---

## Acknowledgments

#### GCS Geometry Code
Significant portions of `src/heliotrace/physics/geometry.py` are adapted from
**[gcs_python](https://github.com/johan12345/gcs_python)** by **Johan von Forstner**,
a Python port of the original IDL GCS routines by Andreas Thernisien.
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for full details.

#### Software
| Package | Role |
|---|---|
| [Streamlit](https://streamlit.io) | Interactive web framework |
| [Plotly](https://plotly.com/python/) | Interactive visualisation |
| [SciPy](https://scipy.org) | ODE integration, triangulation, linear algebra |
| [NumPy](https://numpy.org) | Numerical arrays |
| [Astropy](https://www.astropy.org) | Units and physical constants |
| [SunPy](https://sunpy.org) | Solar coordinate frames (optional) |
| [Pandas](https://pandas.pydata.org) | Tabular data handling |
