# ☀️ HelioTrace — Interactive CME Propagation Explorer

An interactive Streamlit application for modelling the propagation of
**Interplanetary Coronal Mass Ejections (ICMEs)** through the inner heliosphere
using the **Drag-Based Model (DBM)** and the **Modified DBM (MoDBM)**.

Developed based on research from a Master's Thesis — see [Related Publication](#-related-publication).

---

## ✨ Features

- 🌐 **Interactive 3D Reconstructions** — Turn reconstruction data into interactive 3D flux-rope visualizations.
- 🎯 **Geometric Hit vs. Miss Check** — Quickly distinguish between target-impacting events and off-target misses.
- 📐 **Kinematic Fitting** — Extract initial CME apex velocities from height-time profiles.
- 🎯 **Target-Directed Kinematics** — Auto-extract the Earthward/target-directed velocity.
- 🌬️ **Drag-Based Model (DBM)** — Simulate ICME propagation with the field-standard, highly cited benchmark.
- 🔬 **Physics-Enhanced MoDBM** — Solve ICME propagation numerically, featuring variable solar wind conditions.
- 📊 **Trajectory Analytics** — Visually track and compare ICME kinematics side-by-side for both models.
- 🕐 **Space Weather Forecasting** — Forecast ToA, transit time, and impact speed to help assess risks.

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

Then open [http://localhost:8501](http://localhost:8501) in your browser.

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

Coronal Mass Ejections (CMEs) are explosive eruptions of magnetised plasma from
the Sun's corona. When directed at Earth, ICMEs (their interplanetary counterpart)
can trigger severe geomagnetic storms. To forecast these impacts for Earth and
other targets in the inner heliosphere, HelioTrace simulates the ICME's journey
using a four-step physics workflow:

1. **🛰️ 3D Reconstruction**: A true 3D model of the CME, optimally obtained from multi-viewpoint satellite data, is used to eliminate 2D projection errors common in traditional forecasting methods.
2. **📈 Kinematic Tracking**: By tracking the CME's front (or "apex") height across sequential images,  its initial expansion speed radially outward from the Sun's corona can be approximated.
3. **🎯 Target-Directed Velocity**: Assuming the CME expands self-similarly, the precise velocity component directed at the chosen target (e.g. Earth) can be extracted using a 3D geometric ratio.
4. **🌬️ Interplanetary Propagation**: In interplanetary space, the ambient solar wind acts as a drag force. Thus, fast ICMEs brake, while slow ones accelerate. This drag is modelled to forecast accurate arrival times and speeds.

### Core Physics Frameworks

HelioTrace is built on peer-reviewed heliophysics research, utilizing the following frameworks:

| Component                     | Scientific Model                                                                                                                                                                                                              | What it enables                                                                     |
| :---------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| **3D CME Shape**        | Graduated Cylindrical Shell (GCS) –[Thernisien et al. (2006)](https://doi.org/10.1086/508254)                                                                                                                                   | 3D flux-rope modelling to extract physical dimensions and kinematics.               |
| **Constant-Drag Force** | Drag-Based Model (DBM) –[Vršnak et al. (2013)](https://doi.org/10.1007/s11207-012-0035-4)                                                                                                                                      | Analytical equation of motion featuring a constant solar wind speed estimate.      |
| **Variable-Drag Force** | Modified DBM (MoDBM) –[Müller (2025)]([https://doi.org/10.5281/zenodo.18788366](https://doi.org/10.5281/zenodo.18788366)), solar wind profiles from[Venzmer &amp; Bothmer (2018)](https://doi.org/10.1051/0004-6361/201731831) | Numerically integrated solution with distance- and SSN-dependent solar wind models. |

---

## 📄 Related Publication

This application was developed based on the research done in my Master's Thesis at Georg-August-University Göttingen:

- Müller, E. (2025). 3D Modelling of Coronal Mass Ejections and Simulation of Their Earthward Evolution – Developing Space Weather Forecasting Approaches for the ESA Vigil Mission. Zenodo. [https://doi.org/10.5281/zenodo.18788366](https://doi.org/10.5281/zenodo.18788366)

---

## Acknowledgments

### GCS Geometry Code

Significant portions of `src/heliotrace/physics/geometry.py` are adapted from
**[gcs_python](https://github.com/johan12345/gcs_python)** by **Johan von Forstner**,
a Python port of the original IDL GCS routines by Andreas Thernisien.
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for full details.

### Software

| Package                           | Role                                           |
| --------------------------------- | ---------------------------------------------- |
| [Streamlit](https://streamlit.io)    | Interactive web framework                      |
| [Plotly](https://plotly.com/python/) | Interactive visualisation                      |
| [SciPy](https://scipy.org)           | ODE integration, triangulation, linear algebra |
| [NumPy](https://numpy.org)           | Numerical arrays                               |
| [Astropy](https://www.astropy.org)   | Units and physical constants                   |
| [SunPy](https://sunpy.org)           | Solar coordinate frames (optional)             |
| [Pandas](https://pandas.pydata.org)  | Tabular data handling                          |
