# Third-Party Licenses

This file documents third-party code that has been directly incorporated into
this project's source tree, as opposed to packages installed via
`pyproject.toml` (which carry their own license files).

---

## gcs_python

- **Author**: Johan von Forstner
- **Repository**: <https://github.com/johan12345/gcs_python>
- **License**: MIT

**Incorporated code**: A substantial portion of
`src/heliotrace/physics/geometry.py` — specifically the `skeleton()` and
`gcs_mesh()` functions and the rotation helpers derived from them — is
adapted from *gcs_python*.  *gcs_python* is itself a Python port of the
IDL routines `shellskeleton.pro` and `cmecloud.pro` by Andreas Thernisien,
implementing the Graduated Cylindrical Shell (GCS) model.

**Original scientific reference**:

> Thernisien, A. F. R., Howard, R. A., & Vourlidas, A. (2006).
> *Modeling of Flux Rope Coronal Mass Ejections.*
> ApJ, 652, 763. <https://doi.org/10.1086/508254>

---

*All other dependencies are standard open-source packages listed in
`pyproject.toml` and governed by their respective upstream licenses.*
