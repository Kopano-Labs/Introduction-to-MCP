# KP + APE — 200 STEM Agents (Index)

Full JSON: [KP_APE_200_AGENTS.json](./KP_APE_200_AGENTS.json)

## KP — Kopano Labs (100 agents)

| # | ID | Name | STEM domain | Functionality |
|---|-----|------|-------------|---------------|
| 1 | `kp_agri_soil_01` | Soil pH & EC field mapper | Agriculture & Soil Science | Maps plot-level pH and electrical conductivity with calibrated probes; exports geotagged CSV for lime/gypsum prescriptions. |
| 2 | `kp_agri_soil_02` | Compost maturity NPK estimator | Agriculture & Soil Science | Estimates C:N and available N-P-K from temperature logs + moisture; flags when windrow is safe to spread. |
| 3 | `kp_agri_soil_03` | Drip irrigation scheduler | Agriculture & Soil Science | Schedules mm/day from evapotranspiration and soil moisture sensors; reduces over-watering on sandy soils. |
| 4 | `kp_agri_soil_04` | Pest trap image classifier | Agriculture & Soil Science | Labels sticky-trap photos by pest species count; triggers IPM spray windows only above threshold. |
| 5 | `kp_agri_soil_05` | Cover-crop rotation planner | Agriculture & Soil Science | Plans legume/grass rotations to fix nitrogen and break nematode cycles on smallholdings. |
| 6 | `kp_agri_soil_06` | Greenhouse VPD controller | Agriculture & Soil Science | Maintains vapor-pressure deficit bands for tomato/pepper tunnels using RH and leaf temp. |
| 7 | `kp_agri_soil_07` | Livestock forage mass estimator | Agriculture & Soil Science | Estimates kg DM/ha from pasture height clips and species mix for stocking rate. |
| 8 | `kp_agri_soil_08` | Seed germination lab tracker | Agriculture & Soil Science | Records germination %, days to emergence, and abnormal seedlings per variety trial. |
| 9 | `kp_agri_soil_09` | Aquaponics nutrient balance | Agriculture & Soil Science | Balances fish waste ammonia → nitrite → nitrate for safe plant uptake in recirc systems. |
| 10 | `kp_agri_soil_10` | Post-harvest moisture meter | Agriculture & Soil Science | Predicts safe storage days from grain moisture % and ambient RH to prevent aflatoxin risk. |
| 11 | `kp_water_hydro_01` | Borehole yield test logger | Water & Hydrology | Logs step-drawdown and recovery for sustainable pumping rate (L/s) certification. |
| 12 | `kp_water_hydro_02` | River stage & discharge | Water & Hydrology | Converts staff-gauge readings + velocity profiles to m³/s for flood early warning. |
| 13 | `kp_water_hydro_03` | Rainfall IDF curve builder | Water & Hydrology | Builds intensity-duration-frequency curves from raingauge time series for culvert design. |
| 14 | `kp_water_hydro_04` | Dam seepage survey assistant | Water & Hydrology | Tracks piezometer heads and flags abnormal gradients along embankments. |
| 15 | `kp_water_hydro_05` | Water quality field kit | Water & Hydrology | Records turbidity, coliform proxy, and nitrate strips with chain-of-custody for lab send-off. |
| 16 | `kp_water_hydro_06` | Wetland delineation helper | Water & Hydrology | Tags hydrophytic vegetation + hydric soil indicators for buffer setback maps. |
| 17 | `kp_water_hydro_07` | Desalination energy auditor | Water & Hydrology | kWh per m³ produced for solar-RO plants; compares to grid tariff break-even. |
| 18 | `kp_water_hydro_08` | Greywater reuse calculator | Water & Hydrology | Sizes surge tanks and filtration for toilet flushing from bath/laundry flows. |
| 19 | `kp_water_hydro_09` | Floodplain inundation mapper | Water & Hydrology | Combines DEM + design flood level to show depth-duration on parcels. |
| 20 | `kp_water_hydro_10` | Irrigation canal loss tracker | Water & Hydrology | Estimates seepage and evaporation loss % along unlined canals for rehab priority. |
| 21 | `kp_energy_renew_01` | PV string IV curve spot-check | Energy & Renewables | Flags underperforming strings from Voc/Isc drift vs nameplate at STC. |
| 22 | `kp_energy_renew_02` | Battery cycle health monitor | Energy & Renewables | Tracks SoC cycles, temperature, and capacity fade % for LiFePO₄ home banks. |
| 23 | `kp_energy_renew_03` | Wind resource mast analyst | Energy & Renewables | Weibull k/c from anemometer logs for micro-turbine siting. |
| 24 | `kp_energy_renew_04` | Load-shedding schedule optimizer | Energy & Renewables | Sequences critical loads (medical fridge, borehole) within available kWh blocks. |
| 25 | `kp_energy_renew_05` | Biogas digester gas yield | Energy & Renewables | Models m³ CH₄/day from feedstock TS% and retention time. |
| 26 | `kp_energy_renew_06` | Thermal comfort passive design | Energy & Renewables | Sun path + glazing SHGC recommendations to cut HVAC kWh in classrooms. |
| 27 | `kp_energy_renew_07` | Diesel genset efficiency log | Energy & Renewables | L/kWh and maintenance hours vs manufacturer spec for estate backup. |
| 28 | `kp_energy_renew_08` | Heat-pump COP seasonal tracker | Energy & Renewables | COP vs outdoor temp to justify air-source vs ground-source upgrade. |
| 29 | `kp_energy_renew_09` | Mini-grid tariff allocator | Energy & Renewables | Splits kWh costs across tenants with prepayment meter reconciliation. |
| 30 | `kp_energy_renew_10` | Carbon inventory scope-1/2 | Energy & Renewables | tCO₂e from fuel, grid factor, and fleet km for school/campus reporting. |
| 31 | `kp_materials_mfg_01` | Concrete mix design calculator | Materials & Manufacturing | w/c ratio, slump target, and cube strength prediction from aggregate grading. |
| 32 | `kp_materials_mfg_02` | Weld procedure qualification log | Materials & Manufacturing | Tracks WPS, coupon tensile, and bend test pass/fail per joint type. |
| 33 | `kp_materials_mfg_03` | 3D print filament moisture guard | Materials & Manufacturing | Dry-box RH alerts before brittle PLA/PETG prints in humid climates. |
| 34 | `kp_materials_mfg_04` | CNC tool wear estimator | Materials & Manufacturing | Minutes-to-tool-change from spindle current and surface finish samples. |
| 35 | `kp_materials_mfg_05` | Composite layup cure monitor | Materials & Manufacturing | Exotherm peak time and degree-of-cure from thermocouple profiles. |
| 36 | `kp_materials_mfg_06` | Powder coating thickness QC | Materials & Manufacturing | Micron thickness vs spec per batch with adhesion cross-hatch record. |
| 37 | `kp_materials_mfg_07` | Sheet-metal bend allowance | Materials & Manufacturing | K-factor calculator for press-brake setups from material thickness. |
| 38 | `kp_materials_mfg_08` | Inventory alloy traceability | Materials & Manufacturing | Heat lot → certificate → finished part QR for audit recalls. |
| 39 | `kp_materials_mfg_09` | Vibration FFT bearing diagnoser | Materials & Manufacturing | Orders spectrum peaks to predict bearing failure before line stop. |
| 40 | `kp_materials_mfg_10` | Lean cell takt balancer | Materials & Manufacturing | Balances operator cycle times to customer takt with Yamazumi chart. |
| 41 | `kp_biomed_health_01` | SpO₂ & pulse trend triage | Biomedical & Health Technology | Flags desaturation episodes with timestamped context for clinic referral. |
| 42 | `kp_biomed_health_02` | Vaccine cold-chain monitor | Biomedical & Health Technology | 2–8 °C excursion log with cumulative degree-hours for vial quarantine. |
| 43 | `kp_biomed_health_03` | Wheelchair pressure mapping | Biomedical & Health Technology | Interface pressure hotspots to prevent stage ulcers during seating trials. |
| 44 | `kp_biomed_health_04` | Hearing screening audiogram | Biomedical & Health Technology | Stores PTA dB HL per frequency for school screening follow-up. |
| 45 | `kp_biomed_health_05` | Glucose log pattern analyst | Biomedical & Health Technology | HbA1c proxy trends from fingerstick logs with meal tags. |
| 46 | `kp_biomed_health_06` | Sterilizer cycle verifier | Biomedical & Health Technology | Autoclave temp/pressure vs time-at-temperature for load release. |
| 47 | `kp_biomed_health_07` | Defibrillator pad expiry tracker | Biomedical & Health Technology | Battery and pad shelf-life alerts for community responder kits. |
| 48 | `kp_biomed_health_08` | Maternal ANC visit scheduler | Biomedical & Health Technology | Gestational week milestones with iron/folate adherence notes. |
| 49 | `kp_biomed_health_09` | Lab LIMS sample barcode | Biomedical & Health Technology | Chain-of-custody from draw to result with QC Westgard rules. |
| 50 | `kp_biomed_health_10` | Radiation dose ALARA log | Biomedical & Health Technology | Cumulative mSv for radiographer staff vs regulatory limits. |
| 51 | `kp_robotics_mech_01` | Line-follower PID tuner | Robotics & Mechatronics | Maps Kp/Ki/Kd to track error on competition mats with encoders. |
| 52 | `kp_robotics_mech_02` | Drone battery sag planner | Robotics & Mechatronics | Safe flight time from cell IR and payload mass at altitude. |
| 53 | `kp_robotics_mech_03` | Robotic arm inverse kinematics | Robotics & Mechatronics | Joint limits + reach envelope for pick-place in maker labs. |
| 54 | `kp_robotics_mech_04` | Encoder odometry calibrator | Robotics & Mechatronics | Wheel diameter and slip correction for AGV path repeatability. |
| 55 | `kp_robotics_mech_05` | ROS2 nav2 costmap auditor | Robotics & Mechatronics | Inflation radius vs real robot footprint collision checks. |
| 56 | `kp_robotics_mech_06` | Servo horn torque estimator | Robotics & Mechatronics | Stall current vs mechanical advantage for gripper design. |
| 57 | `kp_robotics_mech_07` | IMU sensor fusion validator | Robotics & Mechatronics | Compares complementary filter yaw to magnetometer ground truth. |
| 58 | `kp_robotics_mech_08` | PLC ladder interlock checker | Robotics & Mechatronics | Verifies e-stop and light-curtain sequences before energize. |
| 59 | `kp_robotics_mech_09` | Pneumatic cylinder sizing | Robotics & Mechatronics | Force vs bore from pressure and stroke time requirements. |
| 60 | `kp_robotics_mech_10` | Humanoid gait phase logger | Robotics & Mechatronics | CoM trajectory and ZMP margin during walking experiments. |
| 61 | `kp_env_monitor_01` | Air PM2.5 school exposure | Environmental Monitoring | Hourly PM maps near playgrounds vs WHO interim targets. |
| 62 | `kp_env_monitor_02` | Noise dBA community survey | Environmental Monitoring | Leq night/day contours for zoning compliance. |
| 63 | `kp_env_monitor_03` | Soil erosion pin plot | Environmental Monitoring | cm soil loss per season from standard erosion pins. |
| 64 | `kp_env_monitor_04` | Wildfire fuel load sampler | Environmental Monitoring | kg/m² dead fuel for fire spread model inputs. |
| 65 | `kp_env_monitor_05` | Marine litter beach transect | Environmental Monitoring | Items per 100 m by material class for cleanup prioritization. |
| 66 | `kp_env_monitor_06` | Ozone UV index educator | Environmental Monitoring | Local UVI + burn time guidance from radiometer. |
| 67 | `kp_env_monitor_07` | Methane landfill flux | Environmental Monitoring | Surface flux chamber ppm·s for gas collection efficiency. |
| 68 | `kp_env_monitor_08` | Biodiversity camera trap ID | Environmental Monitoring | Species hit rate per habitat patch from timelapse metadata. |
| 69 | `kp_env_monitor_09` | Light pollution sky quality | Environmental Monitoring | Bortle class from SQM mag/arcsec² night readings. |
| 70 | `kp_env_monitor_10` | Microplastic filter assay | Environmental Monitoring | Particles/L from grab samples through lab sieve protocol. |
| 71 | `kp_geospatial_survey_01` | RTK GNSS stakeout | Geospatial & Surveying | cm-level setout for building corners from control network. |
| 72 | `kp_geospatial_survey_02` | UAV photogrammetry DSM | Geospatial & Surveying | Point cloud to contour 0.5 m for drainage design. |
| 73 | `kp_geospatial_survey_03` | Total station traverse adjuster | Geospatial & Surveying | Least-squares closure for cadastral re-establishment. |
| 74 | `kp_geospatial_survey_04` | GIS parcel tenure layer | Geospatial & Surveying | Links title deeds to boundary vectors for land admin. |
| 75 | `kp_geospatial_survey_05` | Slope stability FoS calculator | Geospatial & Surveying | Infinite slope FoS from cohesion, φ, and pore pressure. |
| 76 | `kp_geospatial_survey_06` | Mining pit volume survey | Geospatial & Surveying | Cut/fill m³ from monthly drone flights. |
| 77 | `kp_geospatial_survey_07` | Coastal erosion baseline | Geospatial & Surveying | Shoreline retreat m/year from historical orthophotos. |
| 78 | `kp_geospatial_survey_08` | Tree canopy NDVI health | Geospatial & Surveying | Seasonal stress index for urban forestry irrigation. |
| 79 | `kp_geospatial_survey_09` | Gravity geoid height lookup | Geospatial & Surveying | Orthometric correction for leveling runs. |
| 80 | `kp_geospatial_survey_10` | Cadastral conflict detector | Geospatial & Surveying | Overlaps/gaps between adjacent parcel geometries. |
| 81 | `kp_ict_instrument_01` | LoRaWAN sensor gateway | ICT-for-STEM (Instrumentation) | Aggregates field nodes with RSSI/SNR link budget diagnostics. |
| 82 | `kp_ict_instrument_02` | Modbus SCADA historian | ICT-for-STEM (Instrumentation) | Time-series from PLCs with gap-fill for energy meters. |
| 83 | `kp_ict_instrument_03` | MQTT lab telemetry bridge | ICT-for-STEM (Instrumentation) | Publishes Arduino/ESP sensor frames to dashboards with unit tags. |
| 84 | `kp_ict_instrument_04` | Oscilloscope capture archiver | ICT-for-STEM (Instrumentation) | Stores waveforms with trigger metadata for repeatability studies. |
| 85 | `kp_ict_instrument_05` | Spectrum analyzer spur hunt | ICT-for-STEM (Instrumentation) | Identifies interference peaks on RF prototypes. |
| 86 | `kp_ict_instrument_06` | Logic analyzer bus decode | ICT-for-STEM (Instrumentation) | I2C/SPI/UART frames for embedded firmware debug. |
| 87 | `kp_ict_instrument_07` | Edge ML anomaly on vibration | ICT-for-STEM (Instrumentation) | On-device FFT features → bearing fault score without cloud. |
| 88 | `kp_ict_instrument_08` | Time-sync NTP lab auditor | ICT-for-STEM (Instrumentation) | Clock skew ms across distributed loggers for legal metrology. |
| 89 | `kp_ict_instrument_09` | Firmware OTA checksum gate | ICT-for-STEM (Instrumentation) | SHA256 verify before flash on remote field devices. |
| 90 | `kp_ict_instrument_10` | Open data API for school labs | ICT-for-STEM (Instrumentation) | REST export of classroom experiment CSV with schema.org. |
| 91 | `kp_edu_lab_ops_01` | Bunsen burner safety roster | Education & Lab Operations | Gas tap assignment + fire extinguisher check dates. |
| 92 | `kp_edu_lab_ops_02` | Chemical inventory SDS linker | Education & Lab Operations | CAS → hazard pictograms and PPE for prep room. |
| 93 | `kp_edu_lab_ops_03` | Physics kinematics lab grader | Education & Lab Operations | v-t graphs from photogates vs theoretical projectile motion. |
| 94 | `kp_edu_lab_ops_04` | Biology dissection ethics log | Education & Lab Operations | Specimen sourcing and waste disposal compliance. |
| 95 | `kp_edu_lab_ops_05` | Chemistry titration curve fit | Education & Lab Operations | Equivalence point from pH vs mL with uncertainty. |
| 96 | `kp_edu_lab_ops_06` | Engineering capstone Gantt | Education & Lab Operations | Milestone proofs tied to physical prototype demos. |
| 97 | `kp_edu_lab_ops_07` | Math olympiad problem bank | Education & Lab Operations | Tagged difficulty + solution rubric for peer grading. |
| 98 | `kp_edu_lab_ops_08` | Robotics competition scoreboard | Education & Lab Operations | Autonomous + teleop points per rulebook year. |
| 99 | `kp_edu_lab_ops_09` | STEM kit parts manifest | Education & Lab Operations | BOM vs classroom consumption reorder alerts. |
| 100 | `kp_edu_lab_ops_10` | Science fair TRIZ journal | Education & Lab Operations | Hypothesis → experiment → measured outcome → reflection. |

## APE — Ama-Phu Entertainment (100 agents)

| # | ID | Name | STEM domain | Functionality |
|---|-----|------|-------------|---------------|
| 1 | `ape_scicomm_doc_01` | Peer-review explainer writer | Science Communication & Documentary | Turns journal abstracts into grade-11 readable scripts with cited figures. |
| 2 | `ape_scicomm_doc_02` | Climate data storyteller | Science Communication & Documentary | Animates temperature anomaly series with uncertainty bands for town halls. |
| 3 | `ape_scicomm_doc_03` | Epidemic R₀ visual narrator | Science Communication & Documentary | Shows doubling time from case data without sensationalism. |
| 4 | `ape_scicomm_doc_04` | Deep-time fossil timeline | Science Communication & Documentary | Correlates strata ages to evolution milestones for museum voice-over. |
| 5 | `ape_scicomm_doc_05` | Lab safety myth-buster | Science Communication & Documentary | Demonstrates PPE physics (splash, inhalation) in short reels. |
| 6 | `ape_scicomm_doc_06` | Space mission phase drama | Science Communication & Documentary | Orbital mechanics beats tied to actual delta-v budgets. |
| 7 | `ape_scicomm_doc_07` | Ocean acidification lab demo | Science Communication & Documentary | pH change on shell dissolution with measured CaCO₃ loss. |
| 8 | `ape_scicomm_doc_08` | Energy transition cost compare | Science Communication & Documentary | LCOE bars with real tariff and capacity factor sources. |
| 9 | `ape_scicomm_doc_09` | Indigenous knowledge bridge | Science Communication & Documentary | Pairs ethnobotany interviews with phytochemistry lab validation. |
| 10 | `ape_scicomm_doc_10` | Open science replication show | Science Communication & Documentary | Documents preregistered replication attempt with raw data drop. |
| 11 | `ape_music_acoustics_01` | Fourier timbre decomposer | Music, Acoustics & Mathematics | Shows harmonic series of traditional instruments from FFT captures. |
| 12 | `ape_music_acoustics_02` | Room RT60 measurement plot | Music, Acoustics & Mathematics | Clap-test decay curves for studio acoustic treatment design. |
| 13 | `ape_music_acoustics_03` | Rhythm polyrhythm geometry | Music, Acoustics & Mathematics | Visualizes LCM of simultaneous African time signatures. |
| 14 | `ape_music_acoustics_04` | Scale temperament comparison | Music, Acoustics & Mathematics | 12-TET vs just intonation beating demos on keyboard. |
| 15 | `ape_music_acoustics_05` | Djembe membrane mode shapes | Music, Acoustics & Mathematics | Chladni-style patterns from sand on drumhead experiments. |
| 16 | `ape_music_acoustics_06` | Psychoacoustics masking demo | Music, Acoustics & Mathematics | Critical band masking for hearing conservation workshops. |
| 17 | `ape_music_acoustics_07` | Algorithmic composition L-system | Music, Acoustics & Mathematics | Plants → melody rules with listenable MIDI export. |
| 18 | `ape_music_acoustics_08` | Vibrato pitch deviation meter | Music, Acoustics & Mathematics | Cents deviation histogram for violin pedagogy. |
| 19 | `ape_music_acoustics_09` | Concert SPL exposure calculator | Music, Acoustics & Mathematics | dBA dose vs OSHA/NIOSH limits for venue riders. |
| 20 | `ape_music_acoustics_10` | Neuroscience groove EEG pilot | Music, Acoustics & Mathematics | Optional safe classroom demo of beat-onset ERP discussion. |
| 21 | `ape_visual_physics_01` | Camera exposure triangle lab | Visual Arts × Physics & Optics | ISO/shutter/aperture vs histogram for youth photography. |
| 22 | `ape_visual_physics_02` | Colorimetry pigment mixer | Visual Arts × Physics & Optics | CMY subtractive vs RGB additive on calibrated displays. |
| 23 | `ape_visual_physics_03` | Hologram interference explainer | Visual Arts × Physics & Optics | Laser fringe math for science-art installations. |
| 24 | `ape_visual_physics_04` | Perspective projection draft | Visual Arts × Physics & Optics | Vanishing point construction from measured room dimensions. |
| 25 | `ape_visual_physics_05` | Fluid paint Reynolds reel | Visual Arts × Physics & Optics | Shows laminar vs turbulent pour at known viscosity. |
| 26 | `ape_visual_physics_06` | Structural shadow sundial art | Visual Arts × Physics & Optics | Gnomon angle = latitude proof in public sculpture. |
| 27 | `ape_visual_physics_07` | Thermal camera portrait ethics | Visual Arts × Physics & Optics | Teaches IR radiation vs privacy in street art. |
| 28 | `ape_visual_physics_08` | Moire pattern frequency math | Visual Arts × Physics & Optics | Beat frequency from overlaid gratings in textiles. |
| 29 | `ape_visual_physics_09` | Golden ratio architecture audit | Visual Arts × Physics & Optics | Measures claim vs actual proportion in iconic buildings. |
| 30 | `ape_visual_physics_10` | Light painting long-exposure STEM | Visual Arts × Physics & Optics | Traces LED paths with known speed for distance estimate. |
| 31 | `ape_museum_exhibit_01` | Touch-table periodic trend | Interactive Exhibits & Museums | Atomic radius vs ionization energy interactive scatter. |
| 32 | `ape_museum_exhibit_02` | Hands-on lever torque bench | Interactive Exhibits & Museums | F×d balance for grades 6–9 with force gauges. |
| 33 | `ape_museum_exhibit_03` | Pendulum wave phase exhibit | Interactive Exhibits & Museums | Length ladder produces traveling wave visual. |
| 34 | `ape_museum_exhibit_04` | Cloud chamber muon counter | Interactive Exhibits & Museums | Tracks per minute vs altitude discussion panel. |
| 35 | `ape_museum_exhibit_05` | DNA extraction demo script | Interactive Exhibits & Museums | Strawberry protocol with microliter yield estimate. |
| 36 | `ape_museum_exhibit_06` | Seismograph shake table | Interactive Exhibits & Museums | Magnitude vs building model resonance frequencies. |
| 37 | `ape_museum_exhibit_07` | Ecology food-web touch graph | Interactive Exhibits & Museums | Trophic cascade simulation with biomass constraints. |
| 38 | `ape_museum_exhibit_08` | Planet scale walk trail | Interactive Exhibits & Museums | Log-scaled solar system distances on school field. |
| 39 | `ape_museum_exhibit_09` | Math topology torus kiosk | Interactive Exhibits & Museums | Coffee-cup genus demo with 3D print handouts. |
| 40 | `ape_museum_exhibit_10` | Accessibility STEM tactile maps | Interactive Exhibits & Museums | Relief maps with Braille legend for blind learners. |
| 41 | `ape_theatre_stem_01` | Chemistry magic show script | STEM Theatre & Performance | Reaction stoichiometry behind safe audience demos. |
| 42 | `ape_theatre_stem_02` | Physics stunt risk calculator | STEM Theatre & Performance | Fall height → impact speed for stage wire work. |
| 43 | `ape_theatre_stem_03` | Biology outbreak improv | STEM Theatre & Performance | SIR model narrated through character arcs. |
| 44 | `ape_theatre_stem_04` | Astronomy planetarium play | STEM Theatre & Performance | Seasonal sky tied to axial tilt blocking. |
| 45 | `ape_theatre_stem_05` | Engineering bridge collapse drama | STEM Theatre & Performance | Load test footage synced to dialogue beats. |
| 46 | `ape_theatre_stem_06` | Math proof as dialogue | STEM Theatre & Performance | Euclid elements scene with giant compass prop. |
| 47 | `ape_theatre_stem_07` | Robotics puppet teleop | STEM Theatre & Performance | Servo angles mapped to character motion on stage. |
| 48 | `ape_theatre_stem_08` | Sound design Doppler scene | STEM Theatre & Performance | Passing train pitch shift measured live. |
| 49 | `ape_theatre_stem_09` | Materials stress test monologue | STEM Theatre & Performance | Tensile test video narrated by “steel voice”. |
| 50 | `ape_theatre_stem_10` | Climate trial courtroom | STEM Theatre & Performance | Evidence rules: only peer-reviewed exhibits admitted. |
| 51 | `ape_game_mechanics_01` | Projectile motion puzzler | Games with Real Mechanics | Launch angle solver uses g=9.81 without fantasy physics. |
| 52 | `ape_game_mechanics_02` | Orbital mechanics transfer | Games with Real Mechanics | Hohmann Δv budget as win condition. |
| 53 | `ape_game_mechanics_03` | Ecosystem sim carrying capacity | Games with Real Mechanics | Population caps from logistic parameters. |
| 54 | `ape_game_mechanics_04` | Circuit builder Ohm’s law | Games with Real Mechanics | Kirchhoff check before level pass. |
| 55 | `ape_game_mechanics_05` | Genetics Punnett lab game | Games with Real Mechanics | Allele frequencies match Hardy-Weinberg homework. |
| 56 | `ape_game_mechanics_06` | Bridge truss FEM lite | Games with Real Mechanics | Factor of safety > 1.5 to advance. |
| 57 | `ape_game_mechanics_07` | Chemistry balance equation | Games with Real Mechanics | Atom balance gate for reaction puzzles. |
| 58 | `ape_game_mechanics_08` | Geology plate tectonic map | Games with Real Mechanics | Velocity vectors from GPS data layer. |
| 59 | `ape_game_mechanics_09` | Epidemic policy sim | Games with Real Mechanics | R₀ sliders with hospital bed constraint. |
| 60 | `ape_game_mechanics_10` | Renewable grid balancer | Games with Real Mechanics | Match load to wind/solar forecast curves. |
| 61 | `ape_cultural_astro_01` | Southern sky lore mapper | Cultural Astronomy & Indigenous Science | Links constellation stories to RA/Dec tonight. |
| 62 | `ape_cultural_astro_02` | Lunar calendar planting sync | Cultural Astronomy & Indigenous Science | Phase vs traditional sowing windows with rainfall stats. |
| 63 | `ape_cultural_astro_03` | Navigation star compass | Cultural Astronomy & Indigenous Science | Azimuth of Canopus/Polaris for land/sea orientation teaching. |
| 64 | `ape_cultural_astro_04` | Solar calendar henge model | Cultural Astronomy & Indigenous Science | Shadow length vs solstice at local latitude. |
| 65 | `ape_cultural_astro_05` | Meteor shower radiant art | Cultural Astronomy & Indigenous Science | Radiant point from IMO ephemeris + long-exposure plan. |
| 66 | `ape_cultural_astro_06` | Radio astronomy HI line | Cultural Astronomy & Indigenous Science | 21 cm demo dish spectrum for SETI club. |
| 67 | `ape_cultural_astro_07` | Archaeoastronomy site align | Cultural Astronomy & Indigenous Science | Rise/set azimuths vs monument axis measurements. |
| 68 | `ape_cultural_astro_08` | Tide tables cultural fishing | Cultural Astronomy & Indigenous Science | Harmonic constituents explained for safe harvest times. |
| 69 | `ape_cultural_astro_09` | Eclipse outreach safety | Cultural Astronomy & Indigenous Science | ISO 12312-1 filter specs in festival briefing. |
| 70 | `ape_cultural_astro_10` | Dark sky reserve advocacy | Cultural Astronomy & Indigenous Science | SQM trend charts for tourism + conservation pitch. |
| 71 | `ape_bioethics_society_01` | CRISPR classroom ethics forum | Bio-Ethics & Science in Society | Scenario cards with ASBH principles scoring. |
| 72 | `ape_bioethics_society_02` | Vaccine hesitancy data dialogue | Bio-Ethics & Science in Society | Efficacy vs risk in transparent tables. |
| 73 | `ape_bioethics_society_03` | AI bias in hiring demo | Bio-Ethics & Science in Society | Synthetic dataset shows disparate impact metrics. |
| 74 | `ape_bioethics_society_04` | Water rights case study | Bio-Ethics & Science in Society | Allocation math vs historical usage records. |
| 75 | `ape_bioethics_society_05` | Mining EIA public hearing | Bio-Ethics & Science in Society | Decibel, dust, and water models as exhibits. |
| 76 | `ape_bioethics_society_06` | Food labeling sugar math | Bio-Ethics & Science in Society | g/serve vs WHO guideline in market aisle tour. |
| 77 | `ape_bioethics_society_07` | Antibiotic stewardship play | Bio-Ethics & Science in Society | MIC data drives plot about resistance timeline. |
| 78 | `ape_bioethics_society_08` | Climate justice map story | Bio-Ethics & Science in Society | Emissions vs vulnerability choropleth. |
| 79 | `ape_bioethics_society_09` | Open hardware patent debate | Bio-Ethics & Science in Society | Cost fall of lab gear when plans are shared. |
| 80 | `ape_bioethics_society_10` | Informed consent theatre | Bio-Ethics & Science in Society | Readable stats in trial participation scene. |
| 81 | `ape_youth_stem_media_01` | TikTok-safe flame test series | Youth STEM Media | Metal ion colors with ventilation checklist. |
| 82 | `ape_youth_stem_media_02` | Drone FPV physics shorts | Youth STEM Media | Bank angle vs centripetal force caption. |
| 83 | `ape_youth_stem_media_03` | Coding robot challenge vlog | Youth STEM Media | Encoder error debugging on camera. |
| 84 | `ape_youth_stem_media_04` | Math trick proof reveal | Youth STEM Media | Why “magic” works — algebra expansion. |
| 85 | `ape_youth_stem_media_05` | Eco-footprint wardrobe audit | Youth STEM Media | kg CO₂e per garment from LCA database. |
| 86 | `ape_youth_stem_media_06` | Kitchen chemistry emulsion | Youth STEM Media | Surfactant HLB for mayo stability. |
| 87 | `ape_youth_stem_media_07` | Sports science jump metrics | Youth STEM Media | Hang time from force plate if available. |
| 88 | `ape_youth_stem_media_08` | Music beat frequency beat | Youth STEM Media | Tuning fork vs phone app frequency. |
| 89 | `ape_youth_stem_media_09` | Plant timelapse growth curve | Youth STEM Media | Logistic fit to seedling height pixels. |
| 90 | `ape_youth_stem_media_10` | Citizen science upload coach | Youth STEM Media | iNaturalist / rainfall apps with QA tips. |
| 91 | `ape_creative_engineering_01` | Kinetic sculpture gear train | Creative Engineering Showcases | Ratio teeth count → output RPM measured. |
| 92 | `ape_creative_engineering_02` | Wearable assistive exo sketch | Creative Engineering Showcases | Torque required at elbow from anthropometry. |
| 93 | `ape_creative_engineering_03` | Stage pyro chemistry safety | Creative Engineering Showcases | Reaction enthalpy limits for indoor venues. |
| 94 | `ape_creative_engineering_04` | Fashion e-textile circuit | Creative Engineering Showcases | Continuity test and wash-cycle failure modes. |
| 95 | `ape_creative_engineering_05` | Public art wind turbine beauty | Creative Engineering Showcases | Power curve vs aesthetic blade count trade. |
| 96 | `ape_creative_engineering_06` | Rube Goldberg energy accounting | Creative Engineering Showcases | Efficiency % per stage with stopwatch. |
| 97 | `ape_creative_engineering_07` | Projection mapping building | Creative Engineering Showcases | Laser survey anchors content to façade geometry. |
| 98 | `ape_creative_engineering_08` | Underwater photography optics | Creative Engineering Showcases | Snell’s law for port dome refraction correction. |
| 99 | `ape_creative_engineering_09` | Firefly bioluminescence art | Creative Engineering Showcases | Luciferin reaction rate vs temperature demo. |
| 100 | `ape_creative_engineering_10` | Maker faire capstone parade | Creative Engineering Showcases | Each float carries one physical measurement demo. |
