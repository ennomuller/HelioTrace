"""German locale strings."""

DE: dict[str, str] = {
    # ------------------------------------------------------------------ #
    # Home page
    # ------------------------------------------------------------------ #
    "page.home.title": "☀️ HelioTrace",
    "page.home.subtitle": "Interaktiver CME-Ausbreitungs-Explorer",
    "page.home.intro": (
        "**HelioTrace** ist eine interaktive Anwendung zur **Weltraumwetter-Analyse**. "
        "Sie optimiert den **Workflow** von Koronagraphen-Beobachtungen bis zu "
        "Ankunftsvorhersagen von **Koronalen Massenauswürfen (CMEs)**, indem sie "
        "3D-GCS-Geometrie-Rekonstruktion mit reibungsbasierter Physikmodellierung verbindet."
    ),
    "page.home.quickstart_title": "🚀 Schnellstart",
    "page.home.quickstart_flow": (
        "📈 **GCS- und Höhen-Zeit-Daten eingeben** ➢ "
        "📐 **3D-Form und Geschwindigkeitsfit prüfen** ➢ "
        "🎯 **Ziel & Ausbreitungsparameter setzen** ➢ "
        "▶️ **Simulation starten** ➢ "
        "📊 **Ankunftsprognose erhalten** "
    ),
    "page.home.quickstart_tip": (
        "**⚡ Beispiel laden** drücken, um den vollständigen Workflow sofort mit "
        "echten CME-Daten auszuprobieren!"
    ),
    "page.home.features_title": "✨ Funktionen",
    "page.home.features_col1": (
        """
        - 🌐 **Interaktive 3D-Rekonstruktionen** — Rekonstruktionsdaten in interaktive 3D-Flussrohr-Visualisierungen verwandeln.
        - 🎯 **Geometrische Treffer-Prüfung** — Schnell identifizieren, ob das Ereignis zielgerichtet ist.
        - 📐 **Kinematisches Fitting** — Initiale CME-Apex-Geschwindigkeiten aus Höhen-Zeit-Profilen extrahieren.
        - 🏹 **Zielgerichtete Kinematik** — Die auf Erde/Ziel gerichtete Geschwindigkeitskomponente automatisch extrahieren.
        """
    ),
    "page.home.features_col2": (
        """
        - 🌊 **Drag-Based Model (DBM)** — ICME-Ausbreitung mit dem vielfach zitierten Benchmark-Modell simulieren.
        - 🔬 **Physik-erweitertes MoDBM** — ICME-Ausbreitung numerisch lösen, mit variablen Sonnenwind-Bedingungen.
        - 📊 **Trajektorien-Analyse** — ICME-Kinematik beider Modelle visuell nebeneinander verfolgen und vergleichen.
        - 🕐 **Weltraumwetter-Prognose** — Ankunftszeit, Transitzeit und Ankunftsgeschwindigkeit vorhersagen.
        """
    ),
    "page.home.science_title": "🔬 Wissenschaftlicher Hintergrund",
    "page.home.science_body": (
        """
    Koronale Massenauswürfe (CMEs) sind explosive Ausbrüche magnetisierten Plasmas aus
    der Sonnenkorona. Wenn sie auf die Erde gerichtet sind, können ICMEs (ihr
    interplanetares Gegenstück) beispielsweise geomagnetische Stürme auslösen. Um die
    Ankunft bei der Erde und anderen Zielen in der inneren Heliosphäre vorherzusagen,
    simuliert HelioTrace den Transit des ICME mit einem vierstufigen Physik-Workflow:

    1. **📷 3D-Rekonstruktion**: Ein echtes 3D-Modell des CME, optimal aus
       multi-perspektivischen Satellitendaten gewonnen, eliminiert 2D-Projektionsfehler,
       die bei herkömmlichen Vorhersagemethoden auftreten.
    2. **📈 Kinematisches Tracking**: Durch das Verfolgen der Fronthöhe (oder des „Apex")
       des CME über sequenzielle Bilder kann seine initiale radiale Expansionsgeschwindigkeit
       von der Sonnenkorona aus angenähert werden.
    3. **🎯 Zielgerichtete Geschwindigkeit**: Unter der Annahme selbstähnlicher Expansion
       des CME kann die präzise Geschwindigkeitskomponente in Richtung des gewählten Ziels
       (z.B. Erde) mithilfe eines 3D-geometrischen Verhältnisses extrahiert werden.
    4. **🌊 Interplanetare Ausbreitung**: Im interplanetaren Raum wirkt der Sonnenwind als
       Bremskraft. Schnelle ICMEs werden daher abgebremst, langsame beschleunigt. Diese
       Bremswirkung wird modelliert, um genaue Ankunftszeiten und -geschwindigkeiten
       vorherzusagen.
    """
    ),
    "page.home.frameworks_title": "#### Zentrale Physik-Frameworks",
    "page.home.frameworks_intro": (
        "HelioTrace basiert auf heliophysikalischer Forschung und nutzt folgende Frameworks:"
    ),
    "page.home.frameworks_table": (
        "| Komponente | Wissenschaftliches Modell | Was es ermöglicht |\n"
        "| :--- | :--- | :--- |\n"
        "| **3D CME-Form** "
        "| Graduated Cylindrical Shell (GCS) – "
        "[Thernisien et al. (2006)](https://doi.org/10.1086/508254) "
        "| 3D-Flussrohr-Modellierung zur Extraktion physikalischer Dimensionen und Kinematik. |\n"
        "| **Konstante Reibungskraft** "
        "| Drag-Based Model (DBM) – "
        "[Vršnak et al. (2013)](https://doi.org/10.1007/s11207-012-0035-4) "
        "| Analytische Bewegungsgleichung mit konstanter Sonnenwindgeschwindigkeit. |\n"
        "| **Variable Reibungskraft** "
        "| Modified DBM (MoDBM) – "
        "[Müller (2025)](https://doi.org/10.5281/zenodo.18788366), "
        "Sonnenwindprofile von "
        "[Venzmer & Bothmer (2018)](https://doi.org/10.1051/0004-6361/201731831) "
        "| Numerisch integrierte Lösung mit abstands- und SSN-abhängigen Sonnenwindmodellen. |"
    ),
    "page.home.ack_expander": "Anerkennungen & Referenzen",
    "page.home.ack_body": (
        """
        #### GCS-Geometrie-Code
        Wesentliche Teile der GCS-Gitter-Geometrie in diesem Projekt
        (`src/heliotrace/physics/geometry.py`) basieren auf der
        **[gcs_python](https://github.com/johan12345/gcs_python)**-Bibliothek
        von **Johan von Forstner**, die selbst eine Python-Portierung von IDL-Routinen
        der ursprünglichen GCS-Modell-Implementierung ist. Diese grundlegende Arbeit
        wird dankend anerkannt.

        #### Wissenschaftliche Modelle & Zitate
        - **GCS-Modell**: Thernisien, A. F. R., Howard, R. A., & Vourlidas, A. (2006).
        ApJ, 652, 763. [doi:10.1086/508254](https://doi.org/10.1086/508254)
        - **DBM**: Vršnak, B. et al. (2013). Solar Phys, 285, 295–315.
        [doi:10.1007/s11207-012-0035-4](https://doi.org/10.1007/s11207-012-0035-4)
        - **MoDBM Sonnenwind-Geschwindigkeits-/Dichteprofile**: Venzmer, M. S. & Bothmer, V. (2018).
          A&A, 611, A36. [doi:10.1051/0004-6361/201731831](https://doi.org/10.1051/0004-6361/201731831)

        #### Software
        | Paket | Rolle |
        |---|---|
        | [Streamlit](https://streamlit.io) | Interaktives Web-Framework |
        | [Plotly](https://plotly.com/python/) | Interaktive Visualisierung |
        | [SciPy](https://scipy.org) | ODE-Integration, Triangulation, lineare Algebra |
        | [NumPy](https://numpy.org) | Numerische Arrays |
        | [Astropy](https://www.astropy.org) | Einheiten und physikalische Konstanten |
        | [SunPy](https://sunpy.org) | Solare Koordinatensysteme (optional) |
        | [Pandas](https://pandas.pydata.org) | Tabellarische Datenverarbeitung |
        """
    ),
    "page.home.data_caption": (
        "📡 Datenquelle: GCS-Parameter abgeleitet aus Multi-Perspektiven-Koronagraphen-"
        "Beobachtungen (LASCO C2/C3, STEREO COR1/COR2) mit dem Graduated Cylindrical Shell Modell."
    ),
    # ------------------------------------------------------------------ #
    # Propagation Simulator page
    # ------------------------------------------------------------------ #
    "page.sim.title": "Propagations-Simulator",
    "page.sim.caption": (
        "Ereignis: **{event}** | Ziel: **{target}** ({dist:.2f} AU) | Modelle: DBM · MoDBM"
    ),
    "page.sim.tab_gcs": "📡 GCS-Geometrie",
    "page.sim.tab_kinematics": "📊 CME-Kinematik",
    "page.sim.tab_prop": "📈 Ausbreitungsergebnisse",
    "page.sim.gcs_subheader": "GCS-Modell (3D-Geometrie)",
    "page.sim.gcs_info": (
        "ℹ️ Alle fünf **GCS-Parameter** in der Seitenleiste eingeben — oder "
        "**⚡ Beispiel laden** drücken — um die 3D-Geometrie anzuzeigen."
    ),
    "page.sim.gcs_spinner": "GCS-Geometrie berechnen… (nach dem ersten Durchlauf gecacht)",
    "page.sim.gcs_hit": (
        "✓ **GEOMETRIE: TREFFER** — Die CME-Flanke schneidet **{target}** "
        "bei einem Projektionsverhältnis von **{ratio:.4f}** (≥ 0.3 Schwellwert)."
    ),
    "page.sim.gcs_miss": (
        "**GEOMETRIE: KEIN TREFFER** — Projektionsverhältnis {ratio:.4f} < 0.3. "
        "Der GCS-CME-Körper umfasst die Zielrichtung nicht ausreichend. "
        "Längengrad, Breitengrad oder Halbwinkel anpassen."
    ),
    "page.sim.ht_subheader": "Höhen-Zeit-Diagramm",
    "page.sim.ht_info": (
        "ℹ️ Mindestens **2 Beobachtungen** in der Seitenleiste hinzufügen, "
        "um den H-T-Fit und die Apex-Geschwindigkeit zu berechnen."
    ),
    "page.sim.metric.apex_velocity": "Apex-Geschwindigkeit",
    "page.sim.metric.apex_velocity_help": (
        "CME-Apex-Geschwindigkeit und 1σ-Unsicherheit aus dem gewichteten linearen H-T-Fit."
    ),
    "page.sim.metric.proj_ratio": "Projektionsverhältnis",
    "page.sim.metric.proj_ratio_help": (
        "Anteil der Apex-Höhe, die beim Ziel-Breiten-/Längengrad erreicht wird."
    ),
    "page.sim.metric.v0_target": "v₀ Richtung Ziel",
    "page.sim.metric.v0_target_help": (
        "Initiale Geschwindigkeitskomponente in Richtung des gewählten Ziels."
    ),
    "page.sim.fit_details_subheader": "Fit-Details",
    "page.sim.fit_detail.slope": "Steigung",
    "page.sim.fit_detail.intercept": "Achsenabschnitt",
    "page.sim.fit_detail.chi_squared": "χ²",
    "page.sim.fit_detail.n_obs": "Beobachtungen",
    "page.sim.fit_detail.height_error": "Höhenfehler",
    "page.sim.prop_subheader": "Reibungsbasierte Ausbreitung",
    "page.sim.prop_info": (
        "**▶ Simulation starten** in der Seitenleiste drücken, um DBM- und MoDBM-Trajektorien "
        "und Ankunftsvorhersagen für das gewählte Ziel zu berechnen."
    ),
    "page.sim.no_obs_warning": (
        "⚠️ Vor dem Start mindestens 2 Beobachtungen in der Seitenleiste hinzufügen."
    ),
    "page.sim.sim_spinner": "DBM- & MoDBM-Simulationen laufen…",
    "page.sim.sim_success": "✅ Simulation abgeschlossen!",
    "page.sim.sim_err_invalid": "⚠️ Ungültige Eingabe: {exc}",
    "page.sim.sim_err_unexpected": (
        "Simulation mit unerwartetem Fehler abgebrochen: {exc_type}: {exc}"
    ),
    "page.sim.no_results_info": (
        "Noch keine Ergebnisse. Parameter in der Seitenleiste konfigurieren "
        "und **▶ Simulation starten** drücken."
    ),
    "page.sim.geom_miss": (
        "**GEOMETRIE: FEHLSCHUSS** — Die Simulation wurde ausgeführt, aber der ICME "
        "schneidet **{target}** nicht. Kein Ausbreitungsergebnis verfügbar."
    ),
    "page.sim.key_results": "Schlüsselergebnisse",
    "page.sim.metric.target_dist": "Zielentfernung",
    "page.sim.metric.v0_override_note": "überschrieben",
    "page.sim.model_results": "Modellergebnisse",
    "page.sim.metric.arrival": "Ankunft",
    "page.sim.metric.delta_expected": "Δ vs. Erwartet",
    "page.sim.metric.transit": "Transit",
    "page.sim.metric.impact": "Ankunft",
    "page.sim.dbm_no_arrival": (
        "DBM hat das Ziel nicht innerhalb des Integrationsfensters erreicht."
    ),
    "page.sim.modbm_no_arrival": (
        "MoDBM hat das Ziel nicht innerhalb des Integrationsfensters erreicht."
    ),
    "page.sim.inputs_dbm": "Verwendete Eingaben — DBM",
    "page.sim.inputs_modbm": "Verwendete Eingaben — MoDBM",
    "page.sim.metric.r0_help": (
        "Initiale Apex-Höhe 𝒓₀: größte beobachtete Koronagraphenhöhe, verwendet als "
        "Startposition r(t=0) der Ausbreitungs-ODE [R☉]."
    ),
    "page.sim.metric.t0_help": (
        "Referenz-Startzeit: Zeitstempel der letzten (höchsten) Koronagraphen-Beobachtung, "
        "verwendet als t=0 für die ODE-Integration."
    ),
    "page.sim.metric.vapex_help": (
        "CME-Apex-Geschwindigkeit und $1\\sigma$-Unsicherheit aus dem gewichteten linearen "
        "Höhen-Zeit-Fit. Entspricht der radialen Ausbreitungsgeschwindigkeit des äußersten "
        "Punktes des GCS-Flussrohrs."
    ),
    "page.sim.metric.v0_help": (
        "Initiale CME-Geschwindigkeit projiziert auf die Sonne-Ziel-Sichtlinie: "
        "$v_0 = v_{\\rm apex} \\times$ Projektionsverhältnis. Dies ist die Startgeschwindigkeit "
        "für die 1D-Ausbreitungsgleichung."
    ),
    "page.sim.metric.alpha_help": (
        "GCS-Halbwinkel 𝜶: angulare Halbbreite der CME-Flussrohr-Hülle. "
        "Bestimmt die laterale (longitudinale) Ausdehnung des Ejektas."
    ),
    "page.sim.metric.kappa_help": (
        "GCS-Seitenverhältnis 𝜿: Verhältnis des Querschnittsradius zum Apex-Abstand. "
        "Bestimmt, wie 'dick' das Flussrohr in Projektion erscheint."
    ),
    "page.sim.metric.phi_help": (
        "Stonyhurst-heliografische Länge 𝝓 der CME-Quellregion (Carrington-System, Erde bei 0°)."
    ),
    "page.sim.metric.theta_help": ("Stonyhurst-heliografische Breite 𝜽 der CME-Quellregion."),
    "page.sim.metric.gamma_help": (
        "Neigung 𝜸 der CME-Flussrohr-Achse relativ zur Sonnenäquatorialebene. "
        "Positive Neigung = nord-östliche Ausrichtung der Achse."
    ),
    "page.sim.metric.w_help": (
        "Konstante Sonnenwindgeschwindigkeit im Standard-DBM als asymptotische "
        "Bremsgeschwindigkeit (CME bremst auf w ab). Typisch: 300–600 km/s."
    ),
    "page.sim.metric.cd_help": (
        "Dimensionsloser aerodynamischer Reibungskoeffizient. Theoretischer Wert ≈1 "
        "für eine Kugel; konvergiert für CMEs jenseits von ∼12 R☉ gegen ≈1 (Cargill 2004)."
    ),
    "page.sim.metric.wind_regime_help": (
        "Hintergrund-Sonnenwindregime für das MoDBM-Dichteprofil "
        "(Venzmer & Bothmer 2018). 'slow' ≈ 300–400 km/s; 'fast' ≈ 600–800 km/s."
    ),
    "page.sim.metric.ssn_help": (
        "Monatlich geglättete Gesamtfleckenzahl. Kontrolliert die Amplitude des "
        "strukturierten Sonnenwind-Dichteprofils im MoDBM (höhere SSN = dichterer Wind "
        "nahe Sonnenmaximum)."
    ),
    "page.sim.metric.mass_help": (
        "Gesamtmasse des CME in der Impulsgleichung. Entweder manuell überschrieben "
        r"oder Pluta-(2018)-Formel: "
        r"$\log_{10}(M/{\rm g}) = 3.4\times10^{-4}\,v + 15.479$, "
        "wobei v die Apex-Geschwindigkeit in km/s ist."
    ),
    "page.sim.combined_comparison": "Kombinierter Vergleich",
    # ------------------------------------------------------------------ #
    # Sidebar
    # ------------------------------------------------------------------ #
    "sidebar.title": "⚙️ Konfiguration",
    "sidebar.fill_example": "⚡ Beispiel laden",
    "sidebar.fill_example_help": (
        "Alle Felder mit dem Halloween-CME-Ereignis vom 2023-10-28 befüllen."
    ),
    "sidebar.event_title": "📅 Ereignisinfo",
    "sidebar.event_label": "Ereignisbezeichnung",
    "sidebar.event_placeholder": "z.B. Halo CME · 2023-10-28",
    "sidebar.event_help": (
        "Freitext-Bezeichnung für Plot-Titel und Beschreibungen (max. 40 Zeichen)."
    ),
    "sidebar.target_title": "🎯 Ziel",
    "sidebar.target_body": "Zielkörper",
    "sidebar.target_body_help": (
        "Vorkonfiguriertes Ziel auswählen oder 'Benutzerdefiniert' für "
        "manuelle Koordinateneingabe wählen."
    ),
    "sidebar.target_name": "Zielname",
    "sidebar.target_lon": "Lon [deg]",
    "sidebar.target_lat": "Lat [deg]",
    "sidebar.target_dist": "Entfernung [AU]",
    "sidebar.target_caption": "Lon: **{lon}°** | Lat: **{lat}°** | Entfernung: **{dist} AU**",
    "sidebar.gcs_title": "🐚 GCS-Parameter",
    "sidebar.gcs_lon": "Lon 𝝓 [deg]",
    "sidebar.gcs_lon_placeholder": "[-180, 180]",
    "sidebar.gcs_lon_help": "Stonyhurst-heliografische Länge 𝝓 der CME-Quellregion [deg].",
    "sidebar.gcs_lat": "Lat 𝜽 [deg]",
    "sidebar.gcs_lat_placeholder": "[-90, 90]",
    "sidebar.gcs_lat_help": "Stonyhurst-heliografische Breite 𝜽 der CME-Quelle [deg].",
    "sidebar.gcs_tilt": "Neigung 𝜸 [deg]",
    "sidebar.gcs_tilt_placeholder": "[-90, 90]",
    "sidebar.gcs_tilt_help": (
        "Neigung 𝜸 der CME-Flussrohr-Achse relativ zur Sonnenäquatorialebene [deg]."
    ),
    "sidebar.gcs_lon_warn": (
        "❌ Länge 𝝓 = {lon:.1f}° liegt außerhalb [-180, 180]. Normiert auf {wrapped:.1f}°."
    ),
    "sidebar.gcs_lat_err": (
        "❌ Breite 𝜽 = {lat:.1f}° liegt außerhalb [-90, 90]. Begrenzt auf {clamped:.1f}°."
    ),
    "sidebar.gcs_tilt_warn": (
        "❌ Neigung 𝜸 = {tilt:.1f}° liegt außerhalb [-90, 90]. Begrenzt auf {clamped:.1f}°."
    ),
    "sidebar.gcs_ha": "Halbwinkel 𝜶 [deg]",
    "sidebar.gcs_ha_placeholder": "[1, 89]",
    "sidebar.gcs_ha_help": (
        "GCS-Halbwinkel 𝜶: angulare Halbbreite der CME-Hülle [deg]. "
        "Gültig: (0°, 90°). Typisch: 5–60°."
    ),
    "sidebar.gcs_kappa": "Seitenverhältnis 𝜿",
    "sidebar.gcs_kappa_placeholder": "[0.01, 0.99]",
    "sidebar.gcs_kappa_help": (
        "GCS-Seitenverhältnis 𝜿: Querschnittsradius / Apex-Abstand. "
        "Gültig: (0, 1). Typisch: 0.15–0.7."
    ),
    "sidebar.gcs_ha_err_lo": "❌ Halbwinkel 𝜶 muss > 0° sein. Begrenzt auf 1°.",
    "sidebar.gcs_ha_err_hi": "❌ Halbwinkel 𝜶 muss < 90° sein. Begrenzt auf 89.99°.",
    "sidebar.gcs_kappa_err_hi": "❌ Seitenverhältnis 𝜿 muss < 1 sein. Begrenzt auf 0.99.",
    "sidebar.gcs_kappa_err_lo": "❌ Seitenverhältnis 𝜿 muss > 0 sein. Begrenzt auf 0.01.",
    "sidebar.obs_title": "📋 Beobachtungen",
    "sidebar.obs_caption": "CME-Apex-Höhen aus Koronagraphen-Bildern.",
    "sidebar.obs_time_col": "Zeit (UTC)",
    "sidebar.obs_time_help": (
        "UTC-Beobachtungs-Zeitstempel des Koronagraphen-Bildes, auf dem der Fit durchgeführt wurde."
    ),
    "sidebar.obs_height_col": "Höhe 𝒓 [R☉]",
    "sidebar.obs_height_help": "Gefittete CME-Apex-Höhe in Sonnenradien [R☉].",
    "sidebar.obs_need_more": "ℹ️ Mindestens 2 Beobachtungen für H-T-Fit benötigt. ({n} bisher)",
    "sidebar.obs_valid": "✓ {n} gültige Beobachtungen.",
    "sidebar.advanced": "⚙️ Erweitert",
    "sidebar.height_error": "Höhenfehler ± [R☉]",
    "sidebar.height_error_help": ("Symmetrische ±-Unsicherheit für jede Höhenmessung [R☉]."),
    "sidebar.height_error_warn": "⚠️ Ungültiger Höhenfehler — Standardwert 0.25 R☉ wird verwendet.",
    "sidebar.height_error_neg_warn": (
        "⚠️ Höhenfehler muss ≥ 0 sein. Verwende |{val}| = {abs_val} R☉."
    ),
    "sidebar.height_error_zero_info": (
        "ℹ️ Höhenfehler = 0 R☉: Alle Beobachtungen als exakt behandelt (ungewichteter Fit)."
    ),
    "sidebar.drag_title": "🪂 Reibungsparameter",
    "sidebar.dbm_only": "**Nur DBM**",
    "sidebar.wind_speed": "Sonnenwindgeschwindigkeit w [km/s]",
    "sidebar.wind_speed_help": "Konstante Sonnenwindgeschwindigkeit im Standard-DBM.",
    "sidebar.modbm_only": "**Nur MoDBM**",
    "sidebar.wind_regime": "Sonnenwindregime",
    "sidebar.wind_regime_help": "Venzmer & Bothmer (2018) Hintergrund-Windprofil.",
    "sidebar.ssn": "Geglättete SSN",
    "sidebar.ssn_help": ("Monatlich geglättete Gesamtfleckenzahl für das MoDBM-Dichteprofil."),
    "sidebar.drag_settings": "Reibungseinstellungen",
    "sidebar.c_d": "Reibungskoeffizient c_d",
    "sidebar.c_d_help": (
        "Dimensionsloser Reibungsskoeffizient "
        "(konvergiert jenseits von ~12 R☉ gegen ~1, Cargill 2004)."
    ),
    "sidebar.c_d_warn": "⚠️ Ungültiger Reibungskoeffizient — Standardwert 1.0 wird verwendet.",
    "sidebar.c_d_err": "❌ Reibungskoeffizient muss > 0 sein. Begrenzt auf 0.01.",
    "sidebar.c_d_info": ("ℹ️ c_d = {val} ist ungewöhnlich hoch (typisch: 0.5–2.0, Cargill 2004)."),
    "sidebar.optional_overrides": "Optionale Überschreibungen",
    "sidebar.toa": "Erwartete Ankunftszeit (optional)",
    "sidebar.toa_placeholder": "DD/MM/YYYY HH:MM:SS",
    "sidebar.toa_help": (
        "Beobachtete/vorhergesagte Ankunft zum Vergleich. Leer lassen zum Überspringen."
    ),
    "sidebar.toa_valid": "✓ Gültiges Ankunftszeitformat",
    "sidebar.toa_invalid": "⚠ Erwartetes Format: DD/MM/YYYY HH:MM:SS",
    "sidebar.mass_override": "CME-Masse überschreiben [g]  (0 = Pluta-Formel)",
    "sidebar.mass_override_help": (
        "Pluta-(2018)-Massenformel überschreiben. 0 eingeben, um die Formel beizubehalten."
    ),
    "sidebar.v0_override": "v₀ überschreiben [km/s]  (leer = geometrisch abgeleitet)",
    "sidebar.v0_override_placeholder": "z.B. 600",
    "sidebar.v0_override_help": (
        "Harte Überschreibung der CME-Geschwindigkeitskomponente in Richtung Ziel. "
        r"Ersetzt das geometrisch abgeleitete $v_0 = v_{\rm apex} \times$ Projektionsverhältnis."
    ),
    "sidebar.v0_override_err": "❌ v₀ muss > 0 km/s sein. Überschreibung ignoriert.",
    "sidebar.v0_override_info": (
        "ℹ️ v₀ = {v0:.0f} km/s liegt über dem schnellsten je gemessenen CME (~3000 km/s)."
    ),
    "sidebar.run_simulation": "▶ Simulation starten",
    # ------------------------------------------------------------------ #
    # H-T plot
    # ------------------------------------------------------------------ #
    "plot.ht.gcs_heights": "GCS-Höhen",
    "plot.ht.linear_fit": "Linearer Fit (χ² = {chi:.2f})",
    "plot.ht.xaxis": "Datum & Zeit [UT]",
    "plot.ht.yaxis": "CME-Fronthöhe [R<sub>☉</sub>]",
    # ------------------------------------------------------------------ #
    # GCS 3D plot
    # ------------------------------------------------------------------ #
    "plot.gcs.wireframe": "GCS-Gitter",
    "plot.gcs.sun_to_target_inside": "Sonne → {target} (innerhalb CME)",
    "plot.gcs.sun_to_target_outside": "Sonne → {target} (außerhalb CME)",
    "plot.gcs.proj_point": "Projektionspunkt ({target}): {ratio:.4f}",
    "plot.gcs.target_miss": "{target} Richtung (FEHLSCHUSS)",
    "plot.gcs.zaxis": "Z \u2192 {target}",
    # ------------------------------------------------------------------ #
    # Propagation plot
    # ------------------------------------------------------------------ #
    "plot.prop.distance": "Abstand [R\u2609] ({label})",
    "plot.prop.velocity": "Geschwindigkeit [km/s] ({label})",
    "plot.prop.target_ref": "Ziel ({dist:.2f} AU)",
    "plot.prop.arrival_annotation": "Ankunft {elapsed:.1f} h",
    "plot.prop.xaxis": "Ausbreitungszeit [h]",
    "plot.prop.dist_yaxis": "Sonnenabstand [R<sub>☉</sub>]",
    "plot.prop.vel_yaxis": "Radialgeschwindigkeit [km/s]",
    "plot.prop.dist_vs_time": "Abstand vs. Zeit",
    "plot.prop.vel_vs_time": "Geschwindigkeit vs. Zeit",
    "plot.prop.dbm_arrival": "DBM-Ankunft",
    "plot.prop.modbm_arrival": "MoDBM-Ankunft",
}
