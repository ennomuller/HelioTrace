# ☀️ HelioTrace — Interactive CME Propagation Explorer

> GCS fitting + DBM/MODBM propagation · Python · Streamlit · MIT License

An interactive Streamlit application for modelling the propagation of
**Coronal Mass Ejections (CMEs)** through the inner heliosphere.
It combines **3-D GCS shape reconstruction** from multi-viewpoint coronagraph
images with physics-based CME propagation using the **Drag-Based Model (DBM)**
and the **Modified DBM (MODBM)**.

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
# Requires the [dev] extras
pip install -e ".[dev]"
pytest
```

---

## Project structure

```
HelioTrace/
├── app.py                  Entry point (streamlit run app.py)
├── pages/
│   └── 01_CME_Propagation.py
├── src/heliotrace/         Installable Python package
│   ├── config.py           Presets and constants
│   ├── models/schemas.py   Pure dataclass schemas
│   ├── physics/            Science layer (no Streamlit)
│   │   ├── geometry.py     GCS mesh mathematics
│   │   ├── drag.py         DBM & MODBM ODE engine
│   │   ├── fitting.py      Linear H-T fitting
│   │   └── apex_ratio.py   Geometric projection factor
│   ├── simulation/runner.py  Orchestration pipeline
│   └── ui/                 Streamlit components
│       ├── state.py
│       ├── utils.py
│       └── components/
├── tests/                  pytest suite
├── .streamlit/config.toml  Theme & server settings
├── Dockerfile
└── docker-compose.yml
```

---

## Science background

CMEs are magnetised plasma clouds expelled from the Sun during solar eruptions.
Their arrival time at Earth (or any spacecraft) has direct space-weather
implications.  HelioTrace implements:

- **GCS (Graduated Cylindrical Shell)** geometry to extract the 3D CME shape
  from multi-viewpoint coronagraph images (Thernisien et al. 2006).
- **DBM** (Vršnak et al. 2013) — constant drag parameter; yields an analytic
  closed-form solution for CME transit time and arrival speed.
- **MODBM** (Venzmer & Bothmer 2018) — position-dependent drag coefficient
  combined with a sunspot-number-dependent ambient solar-wind density profile
  (Leblanc et al. 1998); solved numerically.

For a full scientific derivation and validation of the models implemented here,
see the accompanying Master's Thesis:
[Link to Master's Thesis for accurate scientific explanation]

---

## References

- Vršnak, B. et al. (2013). *A&A* 553, A53. <https://doi.org/10.1051/0004-6361/201220779>
- Venzmer, M. S. & Bothmer, V. (2018). *A&A* 611, A36. <https://doi.org/10.1051/0004-6361/201731831>
- Thernisien, A. et al. (2006). *ApJ* 652, 763. <https://doi.org/10.1086/508254>
- Leblanc, Y. et al. (1998). *Solar Physics* 183, 165. <https://doi.org/10.1023/A:1005049730506>
- Pluta, A. (2018). Master's thesis, University of Göttingen.

---

## Citing HelioTrace

If you use HelioTrace in your research, please cite:

```text
Müller, E. (2026). HelioTrace: Solar Propagation Suite [Software].
GitHub. https://github.com/ennomuller/HelioTrace

[Link to Master's Thesis for accurate scientific explanation]
```

### Third-party attribution

The GCS geometry core (`src/heliotrace/physics/geometry.py`) is adapted from
[**gcs_python**](https://github.com/johan12345/gcs_python) by **Johan von Forstner**,
used under the MIT License.

---

## License

MIT License — see [`LICENSE`](LICENSE) for details.
