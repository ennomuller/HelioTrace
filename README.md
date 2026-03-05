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


## TODOs

description github: 

☀️ HelioTrace | Space Weather Science ☀️ Modeling the Propagation of Interplanetary ICME Propagation interactively •   Drag Based Model (DBM) and MOdrified Drag Based Model (MODBM) • Built with Streamlit & Python. 🚀 Run the web-app here: 🚀

☀️HelioTrace | Space Weather Physics☀️ Modeling ICME propagation interactively Predicting Space Weather & ICME arrivals  Drag Based Model (DBM) and MOdrified Drag Based Model (MODBM) • Built with Streamlit & Python. 🚀 Run the web-app here: 🚀

was in process:
- establish a bit of space between the "Model Results" number section and the "Inputs used" expander so it looks more professional polished
- revert the "Inputs used" expander content to a bullet point list of input parameter instead of these columns, and put the tooltips at the end of each bullet point line; group values similar in scientific origin together in one bullet point (e.g. r_0 and t_0; alpha and kappa; lon, lat and tilt; v_apex and mass) separated by a "|", and explain their origin in the tooltip together
- review the sizes of the value names and value numbers, and make it look consistent across the "Key Results" and "Model Results" entries, as well as Apex Velocity, Projection Ratio and v₀ toward Target in the first tab
- move Apex Velocity, Projection Ratio and v₀ toward Target above the height-time plot
- make the Advanced expander in the Drag Parameters side bar section a bit more compact
- rename 'DBM only' and 'MODBM only' in the sidebar to be more intuitive/descriptive
- remove the little read and green numbers below the "Δ vs Expected values", like "-1.60 h"

was probably not:

- a neat gif/animation of an expanding CME GCS model shell from sun to earth (left end of page is Sun, right end is Earth, gif has small height) plays for 1 sec;
- the interface then shows a plot of the GCS model once the 5 geometrical GCS parameters are provided that slowly rotates (maybe implement via changing plotly 3d seeing angles) unless hovered over or clicked
- the plots show bad contrast between axis lines, grid, axis descriptions, etc., not really readable
- in the model comparison plot, plot the labels of the arrival lines so that they do not overlap, e.g. by plotting the label of the dotted line of the model that arrives first on the left of the line and of the one arriving later on the right of its dotted arrival line
- in the model comparison plot, show label box for both models either in top middle of entire comparison plot (between both subplots) or bottom middle, whatever is more scientific
- rework the current event info/identifier: make it possible to use any string (with reasonable max length, and explanatory example entry entered like Halo CME + some common scale value or something), and use this string in any descriptions, titles, plots and results where it makes sense; keep the event date as it is now, but like a standard english date, and make the tooltip list all the actual methods/algorithms/positions it is used for/within, and (also) use it for the automatic target position calibration via sunpy
- rewrite all MODBM (MOdified Drag Based Model) mentions to MoDBM (Modified Drag Based Model) since this is how the thesis uses it

### branch:

- the GCS wireframe looks strange and not uniform in the plot, a few triangles are visible randomly on top of a uniform structure, explore a way to make it more appealing, maybe fully uniform without these triangle artifacts

### branch:

- rework how targets and their positions are selected: keep Earth as a selected default, where individual position parameters (lon, lat, height) are displayed below it, all three side by side, and the user can manipulate the values; also make it possible to add targets (but only select max one for simulation) by selecting them from drop down lists, one for celestial bodies and one for satellites/probes, and enter the parameters as above for Earth or hit a button just below those to automatically calculate them for the configured event date; use the sunpy package or source for the automatic calculation, e.g. from sunpy.coordinates with get_body_heliographic_stonyhurst, get_horizons_coord; and also build the drop down lists from its available objects/targets

need branch::

- rework how multiple selected targets are used: multiple targets (max 3) should be able to be selected simultaneously, and if they are, the simulation is performed for every individually and the additional tabs are created for each additional target that then present the simulation results for that target and the other stuff

- add feature to import PyThea JSON files with GCS fit results, and automatically populate the parameters with the values from the file
