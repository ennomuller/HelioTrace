"""English locale strings."""

EN: dict[str, str] = {
    # ------------------------------------------------------------------ #
    # Home page
    # ------------------------------------------------------------------ #
    "page.home.title": "☀️ HelioTrace",
    "page.home.subtitle": "Interactive CME Propagation Explorer",
    "page.home.intro": (
        "**HelioTrace** is an interactive application for **space weather analysis**. "
        "It streamlines the **workflow** from coronagraph observations to impact "
        "forecasts of **Coronal Mass Ejections (CMEs)**, by integrating 3D GCS "
        "geometric reconstruction with drag-based physics modelling."
    ),
    "page.home.quickstart_title": "🚀 Quick Start",
    "page.home.quickstart_flow": (
        "📈 **Enter GCS and Height-Time Data** ➢ "
        "📐 **Inspect 3D Shape and Speed Fit** ➢ "
        "🎯 **Set Target & Drag Parameters** ➢ "
        "▶️ **Run Simulation** ➢ "
        "📊 **Get Arrival Forecast** "
    ),
    "page.home.quickstart_tip": (
        "Hit **⚡ Fill with example** to explore the full workflow with real CME data instantly!"
    ),
    "page.home.features_title": "✨ Features",
    "page.home.features_col1": (
        """
        - 🌐 **Interactive 3D Reconstructions** — Turn reconstruction data into interactive 3D flux-rope visualizations.
        - 🎯 **Geometric Hit vs. Miss Check** — Quickly distinguish between target-impacting events and off-target misses.
        - 📐 **Kinematic Fitting** — Extract initial CME apex velocities from height-time profiles.
        - 🏹 **Target-Directed Kinematics** — Auto-extract the Earthward/target-directed velocity.
        """
    ),
    "page.home.features_col2": (
        """
        - 🌊 **Drag-Based Model (DBM)** — Simulate ICME propagation with the field-standard, highly cited benchmark.
        - 🔬 **Physics-Enhanced MoDBM** — Solve ICME propagation numerically, featuring variable solar wind conditions.
        - 📊 **Trajectory Analytics** — Visually track and compare ICME kinematics side-by-side for both models.
        - 🕐 **Space Weather Forecasting** — Forecast ToA, transit time, and impact speed to help assess risks.
        """
    ),
    "page.home.science_title": "🔬 Science Background",
    "page.home.science_body": (
        """
    Coronal Mass Ejections (CMEs) are explosive eruptions of magnetised plasma from
    the Sun's corona. When directed at Earth, ICMEs (their interplanetary counterpart)
    can trigger severe geomagnetic storms. To forecast these impacts for Earth and
    other targets in the inner heliosphere, HelioTrace simulates the ICME's journey
    using a four-step physics workflow:

    1. **📷 3D Reconstruction**: A true 3D model of the CME, optimally obtained from
       multi-viewpoint satellite data, is used to eliminate 2D projection errors common
       in traditional forecasting methods.
    2. **📈 Kinematic Tracking**: By tracking the CME's front (or "apex") height across
       sequential images, its initial expansion speed radially outward from the Sun's
       corona can be approximated.
    3. **🎯 Target-Directed Velocity**: Assuming the CME expands self-similarly, the
       precise velocity component directed at the chosen target (e.g. Earth) can be
       extracted using a 3D geometric ratio.
    4. **🌊 Interplanetary Propagation**: In interplanetary space, the ambient solar wind
       acts as a drag force. Thus, fast ICMEs brake, while slow ones accelerate. This drag
       is modelled to forecast accurate arrival times and speeds.
    """
    ),
    "page.home.frameworks_title": "#### Core Physics Frameworks",
    "page.home.frameworks_intro": (
        "HelioTrace is built on heliophysics research, utilizing the following frameworks:"
    ),
    "page.home.frameworks_table": (
        "| Component | Scientific Model | What it enables |\n"
        "| :--- | :--- | :--- |\n"
        "| **3D CME Shape** "
        "| Graduated Cylindrical Shell (GCS) – "
        "[Thernisien et al. (2006)](https://doi.org/10.1086/508254) "
        "| 3D flux-rope modelling to extract physical dimensions and kinematics. |\n"
        "| **Constant-Drag Force** "
        "| Drag-Based Model (DBM) – "
        "[Vršnak et al. (2013)](https://doi.org/10.1007/s11207-012-0035-4) "
        "| Analytical equation of motion featuring a constant solar wind speed estimate. |\n"
        "| **Variable-Drag Force** "
        "| Modified DBM (MoDBM) – "
        "[Müller (2025)](https://doi.org/10.5281/zenodo.18788366), "
        "solar wind profiles from "
        "[Venzmer & Bothmer (2018)](https://doi.org/10.1051/0004-6361/201731831) "
        "| Numerically integrated solution with distance- and SSN-dependent solar wind models. |"
    ),
    "page.home.ack_expander": "Acknowledgments & Credits",
    "page.home.ack_body": (
        """
        #### GCS Geometry Code
        Significant portions of the GCS mesh geometry in this project
        (`src/heliotrace/physics/geometry.py`) are adapted from the
        **[gcs_python](https://github.com/johan12345/gcs_python)** library
        by **Johan von Forstner**, which is itself a Python port of IDL routines
        from the original GCS model implementation. I gratefully acknowledge
        this foundational work.

        #### Scientific Models & Citations
        - **GCS Model**: Thernisien, A. F. R., Howard, R. A., & Vourlidas, A. (2006).
        ApJ, 652, 763. [doi:10.1086/508254](https://doi.org/10.1086/508254)
        - **DBM**: Vršnak, B. et al. (2013). Solar Phys, 285, 295–315.
        [doi:10.1007/s11207-012-0035-4](https://doi.org/10.1007/s11207-012-0035-4)
        - **MoDBM solar wind speed/density profiles**: Venzmer, M. S. & Bothmer, V. (2018).
          A&A, 611, A36. [doi:10.1051/0004-6361/201731831](https://doi.org/10.1051/0004-6361/201731831)

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
        """
    ),
    "page.home.data_caption": (
        "📡 Data source: GCS parameters derived from multi-viewpoint coronagraph observations "
        "(LASCO C2/C3, STEREO COR1/COR2) using the Graduated Cylindrical Shell model."
    ),
    # ------------------------------------------------------------------ #
    # Propagation Simulator page
    # ------------------------------------------------------------------ #
    "page.sim.title": "Propagation Simulator",
    "page.sim.caption": "Event: **{event}** | Target: **{target}** ({dist:.2f} AU) | Models: DBM · MoDBM",
    "page.sim.tab_gcs": "📡 GCS Geometry",
    "page.sim.tab_kinematics": "📊 CME Kinematics",
    "page.sim.tab_prop": "📈 Propagation Results",
    "page.sim.gcs_subheader": "GCS Model (3D Geometry)",
    "page.sim.gcs_info": (
        "ℹ️ Enter all five **GCS parameters** in the sidebar — or press "
        "**⚡ Fill with example** — to view the 3D geometry."
    ),
    "page.sim.gcs_spinner": "Computing GCS geometry…  (cached after first run)",
    "page.sim.gcs_hit": (
        "✓ **GEOMETRY: HIT** — The CME flank intercepts **{target}** "
        "at a projection ratio of **{ratio:.4f}** (≥ 0.3 threshold)."
    ),
    "page.sim.gcs_miss": (
        "**GEOMETRY: MISS** — Projection ratio {ratio:.4f} < 0.3. "
        "The GCS CME body does not sufficiently encompass the target direction. "
        "Adjust longitude, latitude, or half-angle."
    ),
    "page.sim.ht_subheader": "Height-Time Diagram",
    "page.sim.ht_info": (
        "ℹ️ Add at least **2 observations** in the sidebar to compute the H-T fit and apex velocity."
    ),
    "page.sim.metric.apex_velocity": "Apex Velocity",
    "page.sim.metric.apex_velocity_help": (
        "CME apex velocity and 1σ uncertainty from the weighted linear H-T fit."
    ),
    "page.sim.metric.proj_ratio": "Projection Ratio",
    "page.sim.metric.proj_ratio_help": (
        "Fraction of apex height reached at the target latitude/longitude."
    ),
    "page.sim.metric.v0_target": "v₀ toward Target",
    "page.sim.metric.v0_target_help": "Initial velocity component directed at the selected target.",
    "page.sim.fit_details_subheader": "Fit Details",
    "page.sim.fit_detail.slope": "Slope",
    "page.sim.fit_detail.intercept": "Intercept",
    "page.sim.fit_detail.chi_squared": "χ²",
    "page.sim.fit_detail.n_obs": "Observations",
    "page.sim.fit_detail.height_error": "Height Error",
    "page.sim.prop_subheader": "Drag-Based Propagation",
    "page.sim.prop_info": (
        "Press **▶ Run Simulation** in the sidebar to compute DBM and MoDBM trajectories "
        "and arrival predictions at the selected target."
    ),
    "page.sim.no_obs_warning": "⚠️ Add at least 2 observations in the sidebar before running.",
    "page.sim.sim_spinner": "Running DBM & MoDBM simulations…",
    "page.sim.sim_success": "✅ Simulation complete!",
    "page.sim.sim_err_invalid": "⚠️ Invalid input: {exc}",
    "page.sim.sim_err_unexpected": (
        "Simulation failed with an unexpected error: {exc_type}: {exc}"
    ),
    "page.sim.no_results_info": (
        "No results yet. Configure parameters in the sidebar and press **▶ Run Simulation**."
    ),
    "page.sim.geom_miss": (
        "**GEOMETRY: MISS** — The simulation was run but the ICME does not intercept "
        "**{target}**. No propagation result is available."
    ),
    "page.sim.key_results": "Key Results",
    "page.sim.metric.target_dist": "Target Distance",
    "page.sim.metric.v0_override_note": "overridden",
    "page.sim.model_results": "Model Results",
    "page.sim.metric.arrival": "Arrival",
    "page.sim.metric.delta_expected": "Δ vs Expected",
    "page.sim.metric.transit": "Transit",
    "page.sim.metric.impact": "Impact",
    "page.sim.dbm_no_arrival": "DBM did not reach the target within the integration window.",
    "page.sim.modbm_no_arrival": "MoDBM did not reach the target within the integration window.",
    "page.sim.inputs_dbm": "Inputs used — DBM",
    "page.sim.inputs_modbm": "Inputs used — MoDBM",
    "page.sim.metric.r0_help": (
        "Initial apex height 𝒓₀: greatest observed coronagraph height, used as the "
        "starting position r(t=0) of the drag ODE [R☉]."
    ),
    "page.sim.metric.t0_help": (
        "Reference launch time: timestamp of the last (highest) coronagraph "
        "observation, used as t=0 for the ODE integration."
    ),
    "page.sim.metric.vapex_help": (
        "CME apex velocity and $1\\sigma$ uncertainty from the weighted linear "
        "height-time fit. Represents the outward speed of the outermost "
        "point of the GCS flux rope."
    ),
    "page.sim.metric.v0_help": (
        "Initial CME speed projected onto the Sun–target line of sight: "
        "$v_0 = v_{\\rm apex} \\times$ projection ratio. This is the starting velocity "
        "fed into the 1-D drag equation."
    ),
    "page.sim.metric.alpha_help": (
        "GCS half-angle 𝜶: angular half-width of the CME flux-rope shell. "
        "Controls the lateral (longitudinal) extent of the ejecta."
    ),
    "page.sim.metric.kappa_help": (
        "GCS aspect ratio 𝜿: ratio of the cross-section radius to the apex "
        "distance. Determines how 'fat' the flux rope appears in projection."
    ),
    "page.sim.metric.phi_help": (
        "Stonyhurst heliographic longitude 𝝓 of the CME source region "
        "(Carrington frame, Earth at 0°)."
    ),
    "page.sim.metric.theta_help": "Stonyhurst heliographic latitude 𝜽 of the CME source region.",
    "page.sim.metric.gamma_help": (
        "Tilt 𝜸 of the CME flux-rope axis relative to the solar equatorial plane. "
        "Positive tilt = north-east orientation of the axis."
    ),
    "page.sim.metric.w_help": (
        "Constant ambient solar wind speed used by the standard DBM as the "
        "asymptotic drag velocity (CME decelerates toward w). Typical: 300–600 km/s."
    ),
    "page.sim.metric.cd_help": (
        "Dimensionless aerodynamic drag coefficient. Theoretical value ≈1 for a "
        "sphere; converges to ≈1 for CMEs beyond ∼12 R☉ (Cargill 2004)."
    ),
    "page.sim.metric.wind_regime_help": (
        "Background solar wind regime used by the MoDBM density profile "
        "(Venzmer & Bothmer 2018). 'slow' ≈ 300–400 km/s; 'fast' ≈ 600–800 km/s."
    ),
    "page.sim.metric.ssn_help": (
        "Monthly smoothed total sunspot number. Controls the amplitude of the "
        "structured solar wind density profile in MoDBM (higher SSN = denser wind "
        "near solar maximum)."
    ),
    "page.sim.metric.mass_help": (
        "Total CME mass used in the momentum equation. Either a manual override "
        r"or the Pluta (2018) empirical formula: "
        r"$\log_{10}(M/{\rm g}) = 3.4\times10^{-4}\,v + 15.479$, "
        "where v is the apex velocity in km/s."
    ),
    "page.sim.combined_comparison": "Combined Comparison",
    # ------------------------------------------------------------------ #
    # Sidebar
    # ------------------------------------------------------------------ #
    "sidebar.title": "⚙️ Configuration",
    "sidebar.fill_example": "⚡ Fill with example",
    "sidebar.fill_example_help": "Auto-fill all fields with the 2023-10-28 Halloween CME event.",
    "sidebar.event_title": "📅 Event Info",
    "sidebar.event_label": "Event Label",
    "sidebar.event_placeholder": "e.g. Halo CME · 2023-10-28",
    "sidebar.event_help": "Free-form label used in plot titles and descriptions (max 40 characters).",
    "sidebar.target_title": "🎯 Target",
    "sidebar.target_body": "Target body",
    "sidebar.target_body_help": (
        "Select a preconfigured target, or choose 'Custom' to enter coordinates manually."
    ),
    "sidebar.target_name": "Target name",
    "sidebar.target_lon": "Lon [deg]",
    "sidebar.target_lat": "Lat [deg]",
    "sidebar.target_dist": "Distance [AU]",
    "sidebar.target_caption": "Lon: **{lon}°** | Lat: **{lat}°** | Distance: **{dist} AU**",
    "sidebar.gcs_title": "🐚 GCS Parameters",
    "sidebar.gcs_lon": "Lon 𝝓 [deg]",
    "sidebar.gcs_lon_placeholder": "[-180, 180]",
    "sidebar.gcs_lon_help": "Stonyhurst heliographic longitude 𝝓 of the CME source region [deg].",
    "sidebar.gcs_lat": "Lat 𝜽 [deg]",
    "sidebar.gcs_lat_placeholder": "[-90, 90]",
    "sidebar.gcs_lat_help": "Stonyhurst heliographic latitude 𝜽 of the CME source [deg].",
    "sidebar.gcs_tilt": "Tilt 𝜸 [deg]",
    "sidebar.gcs_tilt_placeholder": "[-90, 90]",
    "sidebar.gcs_tilt_help": (
        "Tilt 𝜸 of the CME flux-rope axis relative to the solar equatorial plane [deg]."
    ),
    "sidebar.gcs_lon_warn": (
        "❌ Longitude 𝝓 = {lon:.1f}° is outside [-180, 180]. Wrapped to {wrapped:.1f}°."
    ),
    "sidebar.gcs_lat_err": (
        "❌ Latitude 𝜽 = {lat:.1f}° is outside [-90, 90]. Clamped to {clamped:.1f}°."
    ),
    "sidebar.gcs_tilt_warn": (
        "❌ Tilt 𝜸 = {tilt:.1f}° is outside [-90, 90]. Clamped to {clamped:.1f}°."
    ),
    "sidebar.gcs_ha": "Half-angle 𝜶 [deg]",
    "sidebar.gcs_ha_placeholder": "[1, 89]",
    "sidebar.gcs_ha_help": (
        "GCS half-angle 𝜶: angular half-width of the CME shell [deg]. "
        "Valid: (0°, 90°). Typical: 5–60°."
    ),
    "sidebar.gcs_kappa": "Aspect ratio 𝜿",
    "sidebar.gcs_kappa_placeholder": "[0.01, 0.99]",
    "sidebar.gcs_kappa_help": (
        "GCS aspect ratio 𝜿: cross-section radius / apex distance. "
        "Valid: (0, 1). Typical: 0.15–0.7."
    ),
    "sidebar.gcs_ha_err_lo": "❌ Half-angle 𝜶 must be > 0°. Clamped to 1°.",
    "sidebar.gcs_ha_err_hi": "❌ Half-angle 𝜶 must be < 90°. Clamped to 89.99°.",
    "sidebar.gcs_kappa_err_hi": "❌ Aspect ratio 𝜿 must be < 1. Clamped to 0.99.",
    "sidebar.gcs_kappa_err_lo": "❌ Aspect ratio 𝜿 must be > 0. Clamped to 0.01.",
    "sidebar.obs_title": "📋 Observations",
    "sidebar.obs_caption": "CME apex heights from coronagraph images.",
    "sidebar.obs_time_col": "Time (UTC)",
    "sidebar.obs_time_help": (
        "UTC observation timestamp from the coronagraph image on which the fit was performed."
    ),
    "sidebar.obs_height_col": "Height 𝒓 [R☉]",
    "sidebar.obs_height_help": "Fitted CME apex height in solar radii [R☉].",
    "sidebar.obs_need_more": "ℹ️ Need ≥2 observations for H-T fit. ({n} so far)",
    "sidebar.obs_valid": "✓ {n} valid observations.",
    "sidebar.advanced": "⚙️ Advanced",
    "sidebar.height_error": "Height error ± [R☉]",
    "sidebar.height_error_help": (
        "Symmetric ±uncertainty applied to every height measurement [R☉]."
    ),
    "sidebar.height_error_warn": "⚠️ Invalid height error — using default 0.25 R☉.",
    "sidebar.height_error_neg_warn": ("⚠️ Height error must be ≥ 0. Using |{val}| = {abs_val} R☉."),
    "sidebar.height_error_zero_info": (
        "ℹ️ Height error = 0 R☉: all observations treated as exact (unweighted fit)."
    ),
    "sidebar.drag_title": "🪂 Drag Parameters",
    "sidebar.dbm_only": "**DBM only**",
    "sidebar.wind_speed": "Solar wind speed w [km/s]",
    "sidebar.wind_speed_help": "Constant ambient solar wind speed used by the standard DBM.",
    "sidebar.modbm_only": "**MoDBM only**",
    "sidebar.wind_regime": "Solar wind regime",
    "sidebar.wind_regime_help": "Venzmer & Bothmer (2018) background wind profile.",
    "sidebar.ssn": "Smoothed SSN",
    "sidebar.ssn_help": "Monthly smoothed total sunspot number for the MoDBM density profile.",
    "sidebar.drag_settings": "Drag settings",
    "sidebar.c_d": "Drag coefficient c_d",
    "sidebar.c_d_help": (
        "Dimensionless drag coefficient (converges to ~1 beyond ~12 R☉, Cargill 2004)."
    ),
    "sidebar.c_d_warn": "⚠️ Invalid drag coefficient — using default 1.0.",
    "sidebar.c_d_err": "❌ Drag coefficient must be > 0. Clamped to 0.01.",
    "sidebar.c_d_info": ("ℹ️ c_d = {val} is on the high end (typical: 0.5–2.0, Cargill 2004)."),
    "sidebar.optional_overrides": "Optional overrides",
    "sidebar.toa": "Expected arrival time (optional)",
    "sidebar.toa_placeholder": "DD/MM/YYYY HH:MM:SS",
    "sidebar.toa_help": "Observed/predicted arrival for comparison. Leave blank to skip.",
    "sidebar.toa_valid": "✓ Valid arrival time format",
    "sidebar.toa_invalid": "⚠ Expected format: DD/MM/YYYY HH:MM:SS",
    "sidebar.mass_override": "CME mass override [g]  (0 = Pluta formula)",
    "sidebar.mass_override_help": (
        "Override the Pluta (2018) mass formula. Enter 0 to keep the formula."
    ),
    "sidebar.v0_override": "v₀ override [km/s]  (blank = geometry-derived)",
    "sidebar.v0_override_placeholder": "e.g. 600",
    "sidebar.v0_override_help": (
        "Hard override for the CME velocity component directed at the target. "
        r"Replaces the geometry-derived $v_0 = v_{\rm apex} \times$ projection ratio."
    ),
    "sidebar.v0_override_err": "❌ v₀ override must be > 0 km/s. Override ignored.",
    "sidebar.v0_override_info": (
        "ℹ️ v₀ = {v0:.0f} km/s is above the fastest CME on record (~3000 km/s)."
    ),
    "sidebar.run_simulation": "▶ Run Simulation",
    # ------------------------------------------------------------------ #
    # H-T plot
    # ------------------------------------------------------------------ #
    "plot.ht.gcs_heights": "GCS heights",
    "plot.ht.linear_fit": "Linear fit (χ² = {chi:.2f})",
    "plot.ht.xaxis": "Date & Time [UT]",
    "plot.ht.yaxis": "CME Front Height [R<sub>☉</sub>]",
    # ------------------------------------------------------------------ #
    # GCS 3D plot
    # ------------------------------------------------------------------ #
    "plot.gcs.wireframe": "GCS wireframe",
    "plot.gcs.sun_to_target_inside": "Sun → {target} (inside CME)",
    "plot.gcs.sun_to_target_outside": "Sun → {target} (outside CME)",
    "plot.gcs.proj_point": "Projection point ({target}): {ratio:.4f}",
    "plot.gcs.target_miss": "{target} direction (MISS)",
    "plot.gcs.zaxis": "Z \u2192 {target}",
    # ------------------------------------------------------------------ #
    # Propagation plot
    # ------------------------------------------------------------------ #
    "plot.prop.distance": "Distance [R\u2609] ({label})",
    "plot.prop.velocity": "Velocity [km/s] ({label})",
    "plot.prop.target_ref": "Target ({dist:.2f} AU)",
    "plot.prop.arrival_annotation": "Arrival {elapsed:.1f} h",
    "plot.prop.xaxis": "Propagation Time [h]",
    "plot.prop.dist_yaxis": "Distance from Sun [R<sub>☉</sub>]",
    "plot.prop.vel_yaxis": "Radial Velocity [km/s]",
    "plot.prop.dist_vs_time": "Distance vs. Time",
    "plot.prop.vel_vs_time": "Velocity vs. Time",
    "plot.prop.dbm_arrival": "DBM arrival",
    "plot.prop.modbm_arrival": "MoDBM arrival",
}
