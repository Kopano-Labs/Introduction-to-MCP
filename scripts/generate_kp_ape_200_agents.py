#!/usr/bin/env python3
"""Generate KP (Kopano Labs) × APE (Ama-Phu Entertainment) — 200 STEM agents."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "swarm-ops" / "agents" / "KP_APE_200_AGENTS.json"

# (id_suffix, display stem, functionality — must be physical/measurable STEM outcome)
KP_DOMAINS: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "agri_soil",
        "Agriculture & Soil Science",
        [
            ("01", "Soil pH & EC field mapper", "Maps plot-level pH and electrical conductivity with calibrated probes; exports geotagged CSV for lime/gypsum prescriptions."),
            ("02", "Compost maturity NPK estimator", "Estimates C:N and available N-P-K from temperature logs + moisture; flags when windrow is safe to spread."),
            ("03", "Drip irrigation scheduler", "Schedules mm/day from evapotranspiration and soil moisture sensors; reduces over-watering on sandy soils."),
            ("04", "Pest trap image classifier", "Labels sticky-trap photos by pest species count; triggers IPM spray windows only above threshold."),
            ("05", "Cover-crop rotation planner", "Plans legume/grass rotations to fix nitrogen and break nematode cycles on smallholdings."),
            ("06", "Greenhouse VPD controller", "Maintains vapor-pressure deficit bands for tomato/pepper tunnels using RH and leaf temp."),
            ("07", "Livestock forage mass estimator", "Estimates kg DM/ha from pasture height clips and species mix for stocking rate."),
            ("08", "Seed germination lab tracker", "Records germination %, days to emergence, and abnormal seedlings per variety trial."),
            ("09", "Aquaponics nutrient balance", "Balances fish waste ammonia → nitrite → nitrate for safe plant uptake in recirc systems."),
            ("10", "Post-harvest moisture meter", "Predicts safe storage days from grain moisture % and ambient RH to prevent aflatoxin risk."),
        ],
    ),
    (
        "water_hydro",
        "Water & Hydrology",
        [
            ("01", "Borehole yield test logger", "Logs step-drawdown and recovery for sustainable pumping rate (L/s) certification."),
            ("02", "River stage & discharge", "Converts staff-gauge readings + velocity profiles to m³/s for flood early warning."),
            ("03", "Rainfall IDF curve builder", "Builds intensity-duration-frequency curves from raingauge time series for culvert design."),
            ("04", "Dam seepage survey assistant", "Tracks piezometer heads and flags abnormal gradients along embankments."),
            ("05", "Water quality field kit", "Records turbidity, coliform proxy, and nitrate strips with chain-of-custody for lab send-off."),
            ("06", "Wetland delineation helper", "Tags hydrophytic vegetation + hydric soil indicators for buffer setback maps."),
            ("07", "Desalination energy auditor", "kWh per m³ produced for solar-RO plants; compares to grid tariff break-even."),
            ("08", "Greywater reuse calculator", "Sizes surge tanks and filtration for toilet flushing from bath/laundry flows."),
            ("09", "Floodplain inundation mapper", "Combines DEM + design flood level to show depth-duration on parcels."),
            ("10", "Irrigation canal loss tracker", "Estimates seepage and evaporation loss % along unlined canals for rehab priority."),
        ],
    ),
    (
        "energy_renew",
        "Energy & Renewables",
        [
            ("01", "PV string IV curve spot-check", "Flags underperforming strings from Voc/Isc drift vs nameplate at STC."),
            ("02", "Battery cycle health monitor", "Tracks SoC cycles, temperature, and capacity fade % for LiFePO₄ home banks."),
            ("03", "Wind resource mast analyst", "Weibull k/c from anemometer logs for micro-turbine siting."),
            ("04", "Load-shedding schedule optimizer", "Sequences critical loads (medical fridge, borehole) within available kWh blocks."),
            ("05", "Biogas digester gas yield", "Models m³ CH₄/day from feedstock TS% and retention time."),
            ("06", "Thermal comfort passive design", "Sun path + glazing SHGC recommendations to cut HVAC kWh in classrooms."),
            ("07", "Diesel genset efficiency log", "L/kWh and maintenance hours vs manufacturer spec for estate backup."),
            ("08", "Heat-pump COP seasonal tracker", "COP vs outdoor temp to justify air-source vs ground-source upgrade."),
            ("09", "Mini-grid tariff allocator", "Splits kWh costs across tenants with prepayment meter reconciliation."),
            ("10", "Carbon inventory scope-1/2", "tCO₂e from fuel, grid factor, and fleet km for school/campus reporting."),
        ],
    ),
    (
        "materials_mfg",
        "Materials & Manufacturing",
        [
            ("01", "Concrete mix design calculator", "w/c ratio, slump target, and cube strength prediction from aggregate grading."),
            ("02", "Weld procedure qualification log", "Tracks WPS, coupon tensile, and bend test pass/fail per joint type."),
            ("03", "3D print filament moisture guard", "Dry-box RH alerts before brittle PLA/PETG prints in humid climates."),
            ("04", "CNC tool wear estimator", "Minutes-to-tool-change from spindle current and surface finish samples."),
            ("05", "Composite layup cure monitor", "Exotherm peak time and degree-of-cure from thermocouple profiles."),
            ("06", "Powder coating thickness QC", "Micron thickness vs spec per batch with adhesion cross-hatch record."),
            ("07", "Sheet-metal bend allowance", "K-factor calculator for press-brake setups from material thickness."),
            ("08", "Inventory alloy traceability", "Heat lot → certificate → finished part QR for audit recalls."),
            ("09", "Vibration FFT bearing diagnoser", "Orders spectrum peaks to predict bearing failure before line stop."),
            ("10", "Lean cell takt balancer", "Balances operator cycle times to customer takt with Yamazumi chart."),
        ],
    ),
    (
        "biomed_health",
        "Biomedical & Health Technology",
        [
            ("01", "SpO₂ & pulse trend triage", "Flags desaturation episodes with timestamped context for clinic referral."),
            ("02", "Vaccine cold-chain monitor", "2–8 °C excursion log with cumulative degree-hours for vial quarantine."),
            ("03", "Wheelchair pressure mapping", "Interface pressure hotspots to prevent stage ulcers during seating trials."),
            ("04", "Hearing screening audiogram", "Stores PTA dB HL per frequency for school screening follow-up."),
            ("05", "Glucose log pattern analyst", "HbA1c proxy trends from fingerstick logs with meal tags."),
            ("06", "Sterilizer cycle verifier", "Autoclave temp/pressure vs time-at-temperature for load release."),
            ("07", "Defibrillator pad expiry tracker", "Battery and pad shelf-life alerts for community responder kits."),
            ("08", "Maternal ANC visit scheduler", "Gestational week milestones with iron/folate adherence notes."),
            ("09", "Lab LIMS sample barcode", "Chain-of-custody from draw to result with QC Westgard rules."),
            ("10", "Radiation dose ALARA log", "Cumulative mSv for radiographer staff vs regulatory limits."),
        ],
    ),
    (
        "robotics_mech",
        "Robotics & Mechatronics",
        [
            ("01", "Line-follower PID tuner", "Maps Kp/Ki/Kd to track error on competition mats with encoders."),
            ("02", "Drone battery sag planner", "Safe flight time from cell IR and payload mass at altitude."),
            ("03", "Robotic arm inverse kinematics", "Joint limits + reach envelope for pick-place in maker labs."),
            ("04", "Encoder odometry calibrator", "Wheel diameter and slip correction for AGV path repeatability."),
            ("05", "ROS2 nav2 costmap auditor", "Inflation radius vs real robot footprint collision checks."),
            ("06", "Servo horn torque estimator", "Stall current vs mechanical advantage for gripper design."),
            ("07", "IMU sensor fusion validator", "Compares complementary filter yaw to magnetometer ground truth."),
            ("08", "PLC ladder interlock checker", "Verifies e-stop and light-curtain sequences before energize."),
            ("09", "Pneumatic cylinder sizing", "Force vs bore from pressure and stroke time requirements."),
            ("10", "Humanoid gait phase logger", "CoM trajectory and ZMP margin during walking experiments."),
        ],
    ),
    (
        "env_monitor",
        "Environmental Monitoring",
        [
            ("01", "Air PM2.5 school exposure", "Hourly PM maps near playgrounds vs WHO interim targets."),
            ("02", "Noise dBA community survey", "Leq night/day contours for zoning compliance."),
            ("03", "Soil erosion pin plot", "cm soil loss per season from standard erosion pins."),
            ("04", "Wildfire fuel load sampler", "kg/m² dead fuel for fire spread model inputs."),
            ("05", "Marine litter beach transect", "Items per 100 m by material class for cleanup prioritization."),
            ("06", "Ozone UV index educator", "Local UVI + burn time guidance from radiometer."),
            ("07", "Methane landfill flux", "Surface flux chamber ppm·s for gas collection efficiency."),
            ("08", "Biodiversity camera trap ID", "Species hit rate per habitat patch from timelapse metadata."),
            ("09", "Light pollution sky quality", "Bortle class from SQM mag/arcsec² night readings."),
            ("10", "Microplastic filter assay", "Particles/L from grab samples through lab sieve protocol."),
        ],
    ),
    (
        "geospatial_survey",
        "Geospatial & Surveying",
        [
            ("01", "RTK GNSS stakeout", "cm-level setout for building corners from control network."),
            ("02", "UAV photogrammetry DSM", "Point cloud to contour 0.5 m for drainage design."),
            ("03", "Total station traverse adjuster", "Least-squares closure for cadastral re-establishment."),
            ("04", "GIS parcel tenure layer", "Links title deeds to boundary vectors for land admin."),
            ("05", "Slope stability FoS calculator", "Infinite slope FoS from cohesion, φ, and pore pressure."),
            ("06", "Mining pit volume survey", "Cut/fill m³ from monthly drone flights."),
            ("07", "Coastal erosion baseline", "Shoreline retreat m/year from historical orthophotos."),
            ("08", "Tree canopy NDVI health", "Seasonal stress index for urban forestry irrigation."),
            ("09", "Gravity geoid height lookup", "Orthometric correction for leveling runs."),
            ("10", "Cadastral conflict detector", "Overlaps/gaps between adjacent parcel geometries."),
        ],
    ),
    (
        "ict_instrument",
        "ICT-for-STEM (Instrumentation)",
        [
            ("01", "LoRaWAN sensor gateway", "Aggregates field nodes with RSSI/SNR link budget diagnostics."),
            ("02", "Modbus SCADA historian", "Time-series from PLCs with gap-fill for energy meters."),
            ("03", "MQTT lab telemetry bridge", "Publishes Arduino/ESP sensor frames to dashboards with unit tags."),
            ("04", "Oscilloscope capture archiver", "Stores waveforms with trigger metadata for repeatability studies."),
            ("05", "Spectrum analyzer spur hunt", "Identifies interference peaks on RF prototypes."),
            ("06", "Logic analyzer bus decode", "I2C/SPI/UART frames for embedded firmware debug."),
            ("07", "Edge ML anomaly on vibration", "On-device FFT features → bearing fault score without cloud."),
            ("08", "Time-sync NTP lab auditor", "Clock skew ms across distributed loggers for legal metrology."),
            ("09", "Firmware OTA checksum gate", "SHA256 verify before flash on remote field devices."),
            ("10", "Open data API for school labs", "REST export of classroom experiment CSV with schema.org."),
        ],
    ),
    (
        "edu_lab_ops",
        "Education & Lab Operations",
        [
            ("01", "Bunsen burner safety roster", "Gas tap assignment + fire extinguisher check dates."),
            ("02", "Chemical inventory SDS linker", "CAS → hazard pictograms and PPE for prep room."),
            ("03", "Physics kinematics lab grader", "v-t graphs from photogates vs theoretical projectile motion."),
            ("04", "Biology dissection ethics log", "Specimen sourcing and waste disposal compliance."),
            ("05", "Chemistry titration curve fit", "Equivalence point from pH vs mL with uncertainty."),
            ("06", "Engineering capstone Gantt", "Milestone proofs tied to physical prototype demos."),
            ("07", "Math olympiad problem bank", "Tagged difficulty + solution rubric for peer grading."),
            ("08", "Robotics competition scoreboard", "Autonomous + teleop points per rulebook year."),
            ("09", "STEM kit parts manifest", "BOM vs classroom consumption reorder alerts."),
            ("10", "Science fair TRIZ journal", "Hypothesis → experiment → measured outcome → reflection."),
        ],
    ),
]

APE_DOMAINS: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "scicomm_doc",
        "Science Communication & Documentary",
        [
            ("01", "Peer-review explainer writer", "Turns journal abstracts into grade-11 readable scripts with cited figures."),
            ("02", "Climate data storyteller", "Animates temperature anomaly series with uncertainty bands for town halls."),
            ("03", "Epidemic R₀ visual narrator", "Shows doubling time from case data without sensationalism."),
            ("04", "Deep-time fossil timeline", "Correlates strata ages to evolution milestones for museum voice-over."),
            ("05", "Lab safety myth-buster", "Demonstrates PPE physics (splash, inhalation) in short reels."),
            ("06", "Space mission phase drama", "Orbital mechanics beats tied to actual delta-v budgets."),
            ("07", "Ocean acidification lab demo", "pH change on shell dissolution with measured CaCO₃ loss."),
            ("08", "Energy transition cost compare", "LCOE bars with real tariff and capacity factor sources."),
            ("09", "Indigenous knowledge bridge", "Pairs ethnobotany interviews with phytochemistry lab validation."),
            ("10", "Open science replication show", "Documents preregistered replication attempt with raw data drop."),
        ],
    ),
    (
        "music_acoustics",
        "Music, Acoustics & Mathematics",
        [
            ("01", "Fourier timbre decomposer", "Shows harmonic series of traditional instruments from FFT captures."),
            ("02", "Room RT60 measurement plot", "Clap-test decay curves for studio acoustic treatment design."),
            ("03", "Rhythm polyrhythm geometry", "Visualizes LCM of simultaneous African time signatures."),
            ("04", "Scale temperament comparison", "12-TET vs just intonation beating demos on keyboard."),
            ("05", "Djembe membrane mode shapes", "Chladni-style patterns from sand on drumhead experiments."),
            ("06", "Psychoacoustics masking demo", "Critical band masking for hearing conservation workshops."),
            ("07", "Algorithmic composition L-system", "Plants → melody rules with listenable MIDI export."),
            ("08", "Vibrato pitch deviation meter", "Cents deviation histogram for violin pedagogy."),
            ("09", "Concert SPL exposure calculator", "dBA dose vs OSHA/NIOSH limits for venue riders."),
            ("10", "Neuroscience groove EEG pilot", "Optional safe classroom demo of beat-onset ERP discussion."),
        ],
    ),
    (
        "visual_physics",
        "Visual Arts × Physics & Optics",
        [
            ("01", "Camera exposure triangle lab", "ISO/shutter/aperture vs histogram for youth photography."),
            ("02", "Colorimetry pigment mixer", "CMY subtractive vs RGB additive on calibrated displays."),
            ("03", "Hologram interference explainer", "Laser fringe math for science-art installations."),
            ("04", "Perspective projection draft", "Vanishing point construction from measured room dimensions."),
            ("05", "Fluid paint Reynolds reel", "Shows laminar vs turbulent pour at known viscosity."),
            ("06", "Structural shadow sundial art", "Gnomon angle = latitude proof in public sculpture."),
            ("07", "Thermal camera portrait ethics", "Teaches IR radiation vs privacy in street art."),
            ("08", "Moire pattern frequency math", "Beat frequency from overlaid gratings in textiles."),
            ("09", "Golden ratio architecture audit", "Measures claim vs actual proportion in iconic buildings."),
            ("10", "Light painting long-exposure STEM", "Traces LED paths with known speed for distance estimate."),
        ],
    ),
    (
        "museum_exhibit",
        "Interactive Exhibits & Museums",
        [
            ("01", "Touch-table periodic trend", "Atomic radius vs ionization energy interactive scatter."),
            ("02", "Hands-on lever torque bench", "F×d balance for grades 6–9 with force gauges."),
            ("03", "Pendulum wave phase exhibit", "Length ladder produces traveling wave visual."),
            ("04", "Cloud chamber muon counter", "Tracks per minute vs altitude discussion panel."),
            ("05", "DNA extraction demo script", "Strawberry protocol with microliter yield estimate."),
            ("06", "Seismograph shake table", "Magnitude vs building model resonance frequencies."),
            ("07", "Ecology food-web touch graph", "Trophic cascade simulation with biomass constraints."),
            ("08", "Planet scale walk trail", "Log-scaled solar system distances on school field."),
            ("09", "Math topology torus kiosk", "Coffee-cup genus demo with 3D print handouts."),
            ("10", "Accessibility STEM tactile maps", "Relief maps with Braille legend for blind learners."),
        ],
    ),
    (
        "theatre_stem",
        "STEM Theatre & Performance",
        [
            ("01", "Chemistry magic show script", "Reaction stoichiometry behind safe audience demos."),
            ("02", "Physics stunt risk calculator", "Fall height → impact speed for stage wire work."),
            ("03", "Biology outbreak improv", "SIR model narrated through character arcs."),
            ("04", "Astronomy planetarium play", "Seasonal sky tied to axial tilt blocking."),
            ("05", "Engineering bridge collapse drama", "Load test footage synced to dialogue beats."),
            ("06", "Math proof as dialogue", "Euclid elements scene with giant compass prop."),
            ("07", "Robotics puppet teleop", "Servo angles mapped to character motion on stage."),
            ("08", "Sound design Doppler scene", "Passing train pitch shift measured live."),
            ("09", "Materials stress test monologue", "Tensile test video narrated by “steel voice”."),
            ("10", "Climate trial courtroom", "Evidence rules: only peer-reviewed exhibits admitted."),
        ],
    ),
    (
        "game_mechanics",
        "Games with Real Mechanics",
        [
            ("01", "Projectile motion puzzler", "Launch angle solver uses g=9.81 without fantasy physics."),
            ("02", "Orbital mechanics transfer", "Hohmann Δv budget as win condition."),
            ("03", "Ecosystem sim carrying capacity", "Population caps from logistic parameters."),
            ("04", "Circuit builder Ohm’s law", "Kirchhoff check before level pass."),
            ("05", "Genetics Punnett lab game", "Allele frequencies match Hardy-Weinberg homework."),
            ("06", "Bridge truss FEM lite", "Factor of safety > 1.5 to advance."),
            ("07", "Chemistry balance equation", "Atom balance gate for reaction puzzles."),
            ("08", "Geology plate tectonic map", "Velocity vectors from GPS data layer."),
            ("09", "Epidemic policy sim", "R₀ sliders with hospital bed constraint."),
            ("10", "Renewable grid balancer", "Match load to wind/solar forecast curves."),
        ],
    ),
    (
        "cultural_astro",
        "Cultural Astronomy & Indigenous Science",
        [
            ("01", "Southern sky lore mapper", "Links constellation stories to RA/Dec tonight."),
            ("02", "Lunar calendar planting sync", "Phase vs traditional sowing windows with rainfall stats."),
            ("03", "Navigation star compass", "Azimuth of Canopus/Polaris for land/sea orientation teaching."),
            ("04", "Solar calendar henge model", "Shadow length vs solstice at local latitude."),
            ("05", "Meteor shower radiant art", "Radiant point from IMO ephemeris + long-exposure plan."),
            ("06", "Radio astronomy HI line", "21 cm demo dish spectrum for SETI club."),
            ("07", "Archaeoastronomy site align", "Rise/set azimuths vs monument axis measurements."),
            ("08", "Tide tables cultural fishing", "Harmonic constituents explained for safe harvest times."),
            ("09", "Eclipse outreach safety", "ISO 12312-1 filter specs in festival briefing."),
            ("10", "Dark sky reserve advocacy", "SQM trend charts for tourism + conservation pitch."),
        ],
    ),
    (
        "bioethics_society",
        "Bio-Ethics & Science in Society",
        [
            ("01", "CRISPR classroom ethics forum", "Scenario cards with ASBH principles scoring."),
            ("02", "Vaccine hesitancy data dialogue", "Efficacy vs risk in transparent tables."),
            ("03", "AI bias in hiring demo", "Synthetic dataset shows disparate impact metrics."),
            ("04", "Water rights case study", "Allocation math vs historical usage records."),
            ("05", "Mining EIA public hearing", "Decibel, dust, and water models as exhibits."),
            ("06", "Food labeling sugar math", "g/serve vs WHO guideline in market aisle tour."),
            ("07", "Antibiotic stewardship play", "MIC data drives plot about resistance timeline."),
            ("08", "Climate justice map story", "Emissions vs vulnerability choropleth."),
            ("09", "Open hardware patent debate", "Cost fall of lab gear when plans are shared."),
            ("10", "Informed consent theatre", "Readable stats in trial participation scene."),
        ],
    ),
    (
        "youth_stem_media",
        "Youth STEM Media",
        [
            ("01", "TikTok-safe flame test series", "Metal ion colors with ventilation checklist."),
            ("02", "Drone FPV physics shorts", "Bank angle vs centripetal force caption."),
            ("03", "Coding robot challenge vlog", "Encoder error debugging on camera."),
            ("04", "Math trick proof reveal", "Why “magic” works — algebra expansion."),
            ("05", "Eco-footprint wardrobe audit", "kg CO₂e per garment from LCA database."),
            ("06", "Kitchen chemistry emulsion", "Surfactant HLB for mayo stability."),
            ("07", "Sports science jump metrics", "Hang time from force plate if available."),
            ("08", "Music beat frequency beat", "Tuning fork vs phone app frequency."),
            ("09", "Plant timelapse growth curve", "Logistic fit to seedling height pixels."),
            ("10", "Citizen science upload coach", "iNaturalist / rainfall apps with QA tips."),
        ],
    ),
    (
        "creative_engineering",
        "Creative Engineering Showcases",
        [
            ("01", "Kinetic sculpture gear train", "Ratio teeth count → output RPM measured."),
            ("02", "Wearable assistive exo sketch", "Torque required at elbow from anthropometry."),
            ("03", "Stage pyro chemistry safety", "Reaction enthalpy limits for indoor venues."),
            ("04", "Fashion e-textile circuit", "Continuity test and wash-cycle failure modes."),
            ("05", "Public art wind turbine beauty", "Power curve vs aesthetic blade count trade."),
            ("06", "Rube Goldberg energy accounting", "Efficiency % per stage with stopwatch."),
            ("07", "Projection mapping building", "Laser survey anchors content to façade geometry."),
            ("08", "Underwater photography optics", "Snell’s law for port dome refraction correction."),
            ("09", "Firefly bioluminescence art", "Luciferin reaction rate vs temperature demo."),
            ("10", "Maker faire capstone parade", "Each float carries one physical measurement demo."),
        ],
    ),
]


def _build_agents(
    domains: list,
    parent: str,
    dept_code: str,
    dept_id: str,
) -> list[dict]:
    out: list[dict] = []
    n = 0
    for domain_key, domain_name, items in domains:
        stem_letter = {
            "agri_soil": "S",
            "water_hydro": "E",
            "energy_renew": "E",
            "materials_mfg": "E",
            "biomed_health": "T",
            "robotics_mech": "E",
            "env_monitor": "S",
            "geospatial_survey": "M",
            "ict_instrument": "T",
            "edu_lab_ops": "S",
            "scicomm_doc": "S",
            "music_acoustics": "M",
            "visual_physics": "S",
            "museum_exhibit": "S",
            "theatre_stem": "S",
            "game_mechanics": "M",
            "cultural_astro": "S",
            "bioethics_society": "S",
            "youth_stem_media": "T",
            "creative_engineering": "E",
        }.get(domain_key, "STEM")
        for suffix, title, functionality in items:
            n += 1
            agent_id = f"{dept_code.lower()}_{domain_key}_{suffix}"
            out.append(
                {
                    "id": agent_id,
                    "display_name": title,
                    "parent": parent,
                    "department_code": dept_code,
                    "department_id": dept_id,
                    "stem_domain": domain_name,
                    "stem_letter": stem_letter,
                    "functionality": functionality,
                    "bracket_tags": ["[TSAP_PROTOCOL]", "[BLACK_MASK_DRILL]"],
                    "status": "catalog",
                    "apprenticeship": {
                        "eligible": True,
                        "black_mask_required": True,
                    },
                }
            )
    return out


def _attach_kpefs_vectors(agents: list[dict]) -> None:
    import sys

    kroot = REPO / "kopano-core"
    sys.path.insert(0, str(kroot))
    from kopano.kpefs_router import vector_for_stem_domain

    for agent in agents:
        agent["kpefs_vector"] = vector_for_stem_domain(
            agent.get("stem_domain", ""),
            agent.get("department_code", "KP"),
        )


def main() -> None:
    kp = _build_agents(
        KP_DOMAINS,
        "kopano_labs",
        "KP",
        "kopano_labs_experimentation",
    )
    ape = _build_agents(
        APE_DOMAINS,
        "ama_phu",
        "APE",
        "ama_phu_creativity",
    )
    agents = kp + ape
    _attach_kpefs_vectors(agents)
    payload = {
        "schema": "kp_ape_agents_v1",
        "title": "Kopano-Phu Eco-Friendly System — 200 STEM Agents",
        "philosophy_ref": "docs/swarm-ops/agents/SWARM_AGENTS.json#philosophy",
        "bracket_note": "There is no right or wrong in Bracket Protocols — receipts record alignment, not moral verdict.",
        "counts": {"kopano_labs_KP": len(kp), "ama_phu_APE": len(ape), "total": len(kp) + len(ape)},
        "agents": agents,
        "kpefs_vector_tagged_at": "generate_v1",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(kp)} KP + {len(ape)} APE = {len(kp)+len(ape)} agents -> {OUT}")


if __name__ == "__main__":
    main()
