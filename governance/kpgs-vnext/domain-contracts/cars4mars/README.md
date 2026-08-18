# Cars4Mars Canonical Build Contract

Status: **ACTIVE — physical-build transition / evidence-gated**  
Canonical timestamp: **2026-08-18 19:17 SAST**  
Project baseline: **DFR-01 — 02 August 2026**

This contract binds the Cars4Mars physical-build work to the same KPGS vNext laws already enforced in `Introduction-to-MCP`.

It does **not** replace DFR-01. It prevents the new fabrication work from drifting away from DFR-01 while allowing bounded prototype parameters to evolve through evidence.

## 1. Authority order

```text
ARC 2026 Rulebook Rev 2.0
        ↓
DFR-01 locked engineering baseline
        ↓
Cars4Mars canonical build contract (this folder)
        ↓
Cars4Mars engineering repository
        ↓
prototype / CAD / fabrication / test receipts
        ↓
public Cars4Mars surfaces
```

A render, generated image, simulation, software test, laboratory-access photograph, or fabrication plan cannot silently promote a physical claim.

## 2. Truth boundary at this timestamp

### Locked / designed

- exactly six wheels;
- six-wheel skid-steer with passive rocker-bogie;
- 250 mm wheel diameter baseline;
- 700 × 650 × 500 mm target rover envelope;
- 28 kg BOM target and 30 kg engineering load case;
- six Rhino IG52 24 V / 60 rpm / 100 W gearmotors;
- three Cytron MDDS30 drivers;
- Teensy 4.1 owns deterministic drive and safety authority;
- Jetson Orin Nano Super owns perception, not motor safety;
- Intel RealSense D455 + RPLIDAR A2M12 sensing baseline;
- 24 V 20 Ah LiFePO4, BMS, 60 A master fuse, contactor and E-stop;
- local Wi-Fi for command/video;
- RFM95W LoRa is heartbeat/fail-stop support only;
- payload tray baseline 350 × 300 × 180 mm for up to 1 kg mission object.

### Software / virtual evidence already present

The canonical Cars4Mars engineering repository already records host-side and native embedded-core software tests. Those receipts remain **software evidence only**. They do not promote the physical rover to assembled/tested/validated.

### New physical-build context — 18 August 2026

The current session adds a new **facility-access observation**, not a rover-validation claim:

- location reported and visually shown: HPI d-school fabrication / 3D lab;
- LightBurn 2 is available in the lab workflow;
- the team is beginning small-part prototyping;
- no wheel, axle, hub, rocker-bogie assembly, complete chassis, or integrated rover is yet promoted by this contract as fabricated or tested.

## 3. Canonical build law

Cars4Mars now follows the existing KPGS vNext progressive-update chain:

```text
Adaptive Progressive Updates (APU)
        ↓
Progressive Update
        ↓
#NB
        ↓
bounded CRUD
        ↓
SWFUS
```

The canonical stage order remains:

```text
1. Telemetry
2. Classification
3. Routing
4. Protocol Selection
5. Invariant Audit
6. POC / FOC Check
7. State Update
8. Distribution
```

For Cars4Mars:

- **Telemetry** = timestamp, person/session, lab/tool, part ID, revision ID.
- **Classification** = design-only / generated / simulated / software-tested / fabricated / physically-tested / validated.
- **Routing** = mechanical / electrical / firmware / perception / payload / evidence lane.
- **Protocol Selection** = the specific Cars4Mars P-step and acceptance contract.
- **Invariant Audit** = DFR-01 constants and challenge limits cannot be silently widened.
- **POC / FOC Check** = evidence must support the state being requested.
- **State Update** = only the bounded part/revision projection changes.
- **Distribution** = repo/site/team surfaces synchronize only after the admitted update.

**SWFUS synchronizes a governed projection; it is never authority.**

## 4. Black Mask / BlackMass application

The repository's existing doctrine is preserved exactly:

- **Black Mask v0.5** = pre-flight inspect and proof discipline;
- **BlackMass v1.5/v2.0** = sandbox/external orchestration only after the inspect gate;
- no fake ACK;
- no production graduation claim without receipts;
- proof before narrative;
- realism before aesthetics.

For physical design work, the BlackMass sandbox is the place to try dimensions, interfaces, inserts, materials, and geometry **without changing DFR-01 truth**.

Promotion from sandbox requires a Black Mask review row and a dated artifact.

## 5. PKA split — x may move, y stays fixed

### y — constants / locked constraints

- six-wheel architecture;
- passive rocker-bogie mobility concept;
- 250 mm wheel diameter baseline unless a governed DFR change is explicitly approved;
- 40 kg challenge maximum starting mass;
- DFR-01 control/safety authority;
- challenge envelope limit;
- evidence-state truth boundary.

### x — changeable prototype parameters

Until physically measured and promoted, the following remain changeable:

- wheel width;
- spoke count and spoke geometry;
- hub bolt count / pitch-circle diameter;
- axle-shaft diameter and exact hub fit;
- bearing selection and housing geometry;
- tread-pocket count, dimensions, retention geometry and insert material;
- prototype filament/material;
- tolerances and clearances;
- rocker/bogie link thickness and fastener size.

Generated visuals may suggest values for `x`; they may not silently convert them into `y`.

## 6. P-step build sequence

The current build starts small. Do not fabricate the whole rover from a generated board.

```text
P-001 wheel interface
  -> P-002 hub
  -> P-003 axle shaft
  -> P-004 bearing housing
  -> P-005 mounting bracket
  -> P-006 bogie/rocker link
  -> P-007 dry assembly
  -> P-008 rolling/load prototype
```

Each P-step is independently reviewable, printable/fabricatable and falsifiable.

## 7. P-001 — wheel is now the active part

The first physical-design target is **one wheel**, not the six-wheel assembly.

Canonical intent:

- open-spoke wheel structure;
- a deliberate central mounting face for a separate wheel hub;
- central bore sized by the later hub/axle interface, not guessed from artwork;
- removable screw/bolt interface between wheel and hub;
- outer tread pockets capable of receiving replaceable traction inserts;
- the axle shaft passes through/is retained by the hub interface; it does not rely on the bare wheel shell as its precision bearing surface.

### Tread-pocket experiment

The brown tread elements shown in the generated concept are treated as **replaceable traction inserts**, not a final material decision.

Initial candidate set for small prototypes:

- wheel-body fit prototype: PLA or PETG;
- flexible traction insert: TPU or another rubber-like material;
- stronger later body candidate: nylon or reinforced filament, subject to printer/material availability and test evidence.

Purpose of the insert experiment:

- increase contact compliance on stones/rough terrain;
- reduce hard-plastic slip;
- reduce the chance of the wheel wedging on small rocks by testing tread spacing and compliant contact;
- allow insert geometry/material to change without reprinting the entire wheel.

**None of these materials is promoted as final rover hardware by this document.**

## 8. Minimum design-team packet before P-001 printing

The design team should receive one bounded packet containing:

1. one rough hand sketch;
2. front view;
3. side view;
4. top or section view where needed;
5. 250 mm locked outer-diameter reference;
6. proposed wheel width;
7. proposed center bore;
8. proposed hub mounting face diameter;
9. proposed bolt pattern;
10. proposed tread-pocket dimensions;
11. prototype material + printer/process;
12. revision ID and timestamp.

Unknown dimensions must be marked **TBD**, not inferred from a render.

## 9. Evidence promotion ladder

```text
GENERATED
  -> DIMENSIONED
  -> CAD-RELEASED
  -> SLICED / TOOLPATH-REVIEWED
  -> FABRICATED
  -> FIT-TESTED
  -> ROLL-TESTED
  -> LOAD-TESTED
  -> ACCEPTED | REVISE
```

This ladder is part-specific and does not replace the system-level DFR ladder:

`DESIGNED → FUNDED → ORDERED → RECEIVED → ASSEMBLED → TESTED → VALIDATED`.

## 10. Current generated artifacts

The 18 August concept images are admitted as **generated design references only**:

- Cars4Mars Axle Module Concept Board;
- Cars4Mars Axle Module Assembly Guide;
- Cars4Mars Part 1 — Wheel Concept Poster.

They are useful for communication and geometry discussion. They are not CAD, slicer output, LightBurn toolpaths, fabrication evidence, or measured hardware.

## 11. Drift blockers

Reject or hold any update that:

- changes six wheels to four;
- treats generated measurements as physical measurements;
- marks the rover built because lab access exists;
- treats LightBurn availability as proof that a part was cut;
- treats software simulation as physical mobility evidence;
- lets AI/cloud/perception widen motor authority;
- changes a locked DFR-01 constant without an explicit governed design-change record;
- synchronizes a state to public surfaces before the evidence receipt exists.

## 12. Immediate next gate

**P-001A — Dimension the wheel/hub interface before printing.**

The next admitted update should contain the user's rough sketch plus the three key views and actual proposed dimensions. From that packet the design team can create a dimensioned CAD revision and a first small test coupon / hub-interface prototype before committing material to a full 250 mm wheel.
