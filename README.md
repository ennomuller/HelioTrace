# ☀️ HelioTrace — Interactive CME Propagation Explorer

An interactive Streamlit application for modelling the propagation of
**Interplanetary Coronal Mass Ejections (ICMEs)** through the inner heliosphere
using the **Drag-Based Model (DBM)** and the **MOdified DBM (MODBM)**.

---

## Quick start — Docker

The fastest way to run the app with zero local setup:

```bash
docker-compose up
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

For a live-reload development session:

```bash
docker-compose --profile dev up
```

---

## Local development

### 1. Install the package

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

### 2. Run the app

```bash
streamlit run app.py
```

### 3. Run tests

```bash
pytest
```

---

## Science background

CMEs are magnetised plasma clouds expelled from the Sun during solar eruptions.
The arrival time of ICMEs at Earth (or any other target) has direct space-weather
implications. HelioTrace combines the following components:

- **GCS (Graduated Cylindrical Shell model**, [Thernisien et al. 2006](https://doi.org/10.1086/508254))
  geometry to describe the 3D CME shape, as derived e.g. from multi-viewpoint coronagraph images.
- **Target-directed velocity scaling**
  based on self-similar expansion, where the velocity toward a target ($v_{target}$) is derived by scaling the apex velocity by the ratio of the CME’s target-directed height to its apex height ($h_{target}/h_{apex}$).
- **DBM (Drag Based Model**, [Vršnak et al. 2013](https://doi.org/10.1007/s11207-012-0035-4))
  featuring a constant drag parameter and analytic solution.
- **MODBM (MOdified Drag Based Model**, based on data from [Venzmer &amp; Bothmer 2018](https://doi.org/10.1051/0004-6361/201731831))
  featuring distance-dependent solar wind speed profiles and a distance- and SSN-dependent ambient solar wind density profile, having to be solved numerically.

---

## References

- Dumbović, M., et al. (2021). *Frontiers in Astronomy and Space Sciences*, 8.
- Vršnak, B. et al. (2013). *Solar Physics*, 285(1-2):295–315.
- Venzmer, M. S. & Bothmer, V. (2018). *A&A* 611, A36.
- Thernisien, A. et al. (2006). *ApJ* 652, 763.
- Cremades, H. and Bothmer, V. (2004). *A&A*, 422:307.
- Leblanc, Y., Dulk, G. A., and Bougeret, J. L. (1998). *Solar Physics*, 183:165–180.
- Pluta, A. (2018). Ph.D. dissertation, Georg-August-Universität Göttingen.
