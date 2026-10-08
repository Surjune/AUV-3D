# SIH26058 transmitter payload digital twin (viewer v3): validation

SYSTEM-LEVEL CAD — PRESENTATION MODEL — NOT FABRICATED.
PCB COMPONENT LAYOUT — PRESENTATION MODEL — NOT FABRICATED.
ARCHITECTURAL CONNECTIONS — NOT PCB ROUTING.

## Source chain

No validated file was overwritten.

| Step | File | Change |
|---|---|---|
| 1 | `SIH26058_PAYLOAD_B300_r02_PRESENTATION_v2.FCStd` | Made from `_PRESENTATION.FCStd`, which is not modified (MD5 a8a34301… unchanged). Adds group `P3B_PCB_COMPONENT_LAYOUT` with 19 presentation objects (below). Existing objects changed: 0. Clashes: 0. Report: `04_EXPORTS/PAYLOAD/PRESENTATION_v2_pcb_layout.json`. |
| 2 | `SIH26058_COMPLETE_AUV_PRESENTATION_r02.FCStd` | Made from r01, which is not written (MD5 03d6b653… unchanged). All 170 payload links re-pointed to v2 (geometry signatures identical). Added links: STM32_FUNCTIONS 4, PCB_COMPONENT_LAYOUT 19, CONNECTIONS 72 (55 architectural links, 15 flow arrows on placeholder cables, 2 acoustic outputs). |
| 3 | `SIH26058_COMPLETE_AUV_r02.glb` | Read-only export: 10,753,436 bytes; 297 meshes; 605,800 triangles. Only the 1–2 mm connection pipes use coarser tessellation; MFR models keep full detail. |

**The 19 presentation objects added in v2:**
- Package leads:
  - THS3491 ×4: DDA 8-pin SO PowerPAD family, per register / MFR.
  - OPA2356 ×2: SOIC-8 style, per the CAD envelope; package TBD.
  - STM32G474RE: 64-pin QFP-class leads, illustrative only; package TBD, NOT VERIFIED.
- Pin-1 markers on 11 major ICs.
- Panasonic EEUFR1H102 drawn as its MFR can (Ø16 × 25) inside the verified envelope.
- No leads are added where the CAD envelope already equals the register footprint (TPS2663, TPS62933, LM5157, INA241A).
- Inductors, transformers and filters remain labelled reserved volumes, because their parts are TBD.

## Functional checks

Automated harness in headless Chrome at 1440×900, results in `04_EXPORTS/PAYLOAD/viewer_v3_functional_checks.json`.

| # | Requirement | Result |
|---|---|---|
| 1 | Opens on COMPLETE AUV | PASS: start mode complete |
| 2 | TRANSMITTER PAYLOAD makes the housing transparent | PASS: B300 shell at 14 % with outline edges |
| 3–4 | PCB visible | PASS: PCBs 100 % in payload mode; 50 % in architecture so both tiers read |
| 5–7 | STM32G474, THS3491 A1/A2/B1/B2, filters and power parts identifiable | PASS: 24 component callouts in payload and architecture modes, none missing |
| 8–9 | 235 kHz PATH highlighted | PASS: 20 register rows; chain STM32 → adaptation → waveform → DAC3 → OPA2356 A → LC filter A → THS3491 A1/A2 → BTL → MATCH A → 235 kHz PZT → water; 0 band-B links shown |
| 10–11 | 500 kHz PATH, visually distinct | PASS: 20 rows; 15 band-B analog / high-power links drawn dashed (CAD geometry) |
| 12–13 | POWER PATH | PASS: 20 POWER rows (PWR-01…20), labelled "POWER ARCHITECTURE — PROPOSED"; logic and PA branches, load switch upstream of the boost |
| 14–15 | SENSING | PASS: 13 rows. Bar30, Celsius, SOS, INA241A and V-sense go to the STM32. Host-provided parameters (DATA-01/02 → FW-01) are shown separately and tagged "HOST PARAMETERS ARE NOT SENSORS" |
| 16 | Hover a major component | PASS: STM32G474, THS3491 A1 and DAC3 give component, role and evidence. A link lifted over a chip defers to the chip |
| — | DAC3 / DAC4 / adaptation engine / waveform generator are not chips | PASS: shown as the CAD functional blocks; roles state "not a physical chip / internal peripheral" |
| — | Register coverage | PASS: 72 of 72 rows resolve to CAD geometry |
| — | No propulsion UI | PASS: nine modes; none propulsion-focused |
| — | Truth labels | PASS: banner is permanent; per-mode tags for the PCB layout, connections and power |
| — | Rotate / zoom / pan | PASS: all enabled, polar 0–π |
| — | Page errors | PASS: none |
| — | Fabrication or test claims | PASS: none found |

**Viewing notes:**
- LM5157, TPS2663 and the load switch sit on the underside of the lower boards. From the default top view, hovering lands on the link above them; their callouts, the chain panel and the Power path still identify them.
- The hosted copy needs a claude.ai sign-in, so it was not opened here. It loads the same embedded `model_data.js` that the local tests used.

## Viewer v4: interaction / viewer-UX pass (2026-09-30)

Presentation layer only. Unchanged:
- GLB SHA-256 8e1dedff…3ef7b.
- The four FreeCAD files: MD5 a8a34301… / 5449de91… / 03d6b653… / 027bb15a….
- The register data and the component hierarchy.

The v3 page is archived in `07_WEB/_ARCHIVE/viewer_v3/`.

**Root causes found:**
- **Loading overlay could stay on top.** The "Loading 3D model…" overlay covered the whole stage and took every pointer event. It was hidden only through a `[hidden]` rule supplied by the page wrapper, which `viewer.html` did not declare itself. The overlay is now removed and replaced by a small header status chip, and the page declares `[hidden]` itself.
- **Callouts intercepted drags.** A drag that started on a label never reached the canvas. Callouts now take no pointer events; the canvas hit-tests them for hover, click and double-click.
- **Heavy normal computation at load.** The per-vertex crease-normal pass is replaced by per-CAD-face normals: the same look, no main-thread stall.

**Added:**
- Navigation: left-drag orbit, right-drag pan, wheel zoom towards the cursor, one-finger orbit, two-finger pan/pinch.
- Limits: 0.02 m minimum distance and a per-mode maximum; pan is limited to a box around the visible model; clipping planes follow the zoom level.
- Focus and camera: double-click focus with smooth fly-in; Fit view (selection, or the current mode's content); Reset view (the current mode's own default camera).
- Presentation aids: box outline around the selection; orientation gizmo; navigation hint that fades after 9 s.
- Behaviour: camera animations stop as soon as the user grabs the model; shadows re-render only when the scene changes.

**Automated checks.** Headless Chrome at 1280×800, 1366×768, 1920×1080 and 820×1180, with reduced motion so that camera moves are instant and measurable. Results are in `04_EXPORTS/PAYLOAD/viewer_v4_interaction_checks.json`.

| Check | Result |
|---|---|
| Loading element / text after load | gone at all sizes |
| Stage hit test, 63 points | 62–63 reach the canvas; the rest land on the gizmo control |
| Canvas vs stage size | match; drawing buffer = size × DPR (capped at 2) |
| All 9 modes: orbit target inside the mode's content | PASS |
| All 9 modes: Reset view after a user orbit | returns exactly to that mode's default |
| Connections per mode | 72 / 20 / 20 / 20 / 13 |
| Hover STM32G474 through the 14 % housing | identified (component, role, status) |
| Double-click focus: orbit target to part centre | STM32G474 1.3 mm; THS3491 A1 1.1 mm; 235 kHz PZT 1.3 mm; B300 housing → housing group centre (15–23 mm from the tube centre) |
| Fit view | selection 1.7 mm from the STM32 centre; no selection 10.8 mm from the mode-content centre |
| No propulsion UI; start mode | PASS; Complete AUV |
| Page errors | none |

**Manual checks** with real mouse input in the Claude browser pane:
- A left-drag orbits.
- A real drag with the left button temporarily mapped to pan moves the target by 0.15 m; the right button is configured as pan.
- The wheel zooms towards the cursor without scrolling the page.
- Clicking the Transmitter Payload tab flies to the B300.
- A real hover and double-click on the STM32 identify and focus it.
- Reset and Fit buttons work.
- The gizmo's +Y handle animates to a top view, and orbit works afterwards.

**Not tested:**
- Real touch gestures, because no touch device was available. The OrbitControls touch mapping is verified.
- The hosted page, which requires a claude.ai sign-in. It runs the same code.

## Viewer v5: start-up robustness and layout pass (2026-10-03)

Presentation layer only. The GLB, `model_data.js`, the register data and the component hierarchy are unchanged.

**Root cause found:**
- **Blank 3D view on some loads.** If the stage had zero width when the start-up view was solved (late layout, a hidden or embedded frame), `resize()` set the camera aspect to 0. The solved view was `NaN`, and so were the camera and orbit target. Fit view and Reset view could not recover it, because both start from the camera's current position.

**Fixes:**
- `resize()` ignores a zero-size stage and keeps the last valid aspect.
- `setMode()` stores and flies to a view only when it is finite and the stage has a size. Otherwise the view is marked pending.
- The render loop re-solves a pending view, or recovers from a non-finite camera (at most three attempts), as soon as the stage has a size.
- The mode caption keeps clear of the evidence tags (it previously ran under them in Sensing).
- On narrow screens the tags sit bottom-left above the camera buttons instead of over the model's callouts.
- All nine view tabs fit at 1000 px and wider. The active tab is scrolled into view on phones.
- The navigation hint wraps instead of running under the Fit / Reset buttons on narrower stages.
- Page description, share tags and an inline SVG favicon added to `index.html`.

**Checks** (local static server, desktop and 375 px):

| Check | Result |
|---|---|
| Page loaded in a zero-size frame, then resized to 1100 × 760 | v4: camera `NaN` after the resize and after Reset view. v5: camera valid at zero size, after the resize and after Reset view; model framed correctly |
| All 9 modes | camera valid, no console errors, no `NaN` leader lines |
| Caption vs tags, all modes | no overlap |
| View tabs at 1094 px and 1000 px windows | all nine visible, no overflow (strip 1060 px / 966 px) |
| 375 px, 235 kHz path and Sensing | tags clear of callouts; active tab visible; no horizontal page scroll |

## Viewer v6: web model r03 and interface redesign (2026-10-05)

**Model and data (r03).** Edited from the r02 export (the FreeCAD sources are not on this machine; their update is pending):
Band L – ~120 kHz class PZT (PROPOSED / CANDIDATE, placeholder envelope dia 30 x 17 mm until a part is selected) replaces the
earlier low-band projector; Band H – 500 kHz class PZT kept (PROPOSED / CANDIDATE); Band L matching network "initial calculated
value – TO BE TUNED FROM IMPEDANCE MEASUREMENT" (no final inductor value); 500 kHz matching network "initial calculated target
~27 µH – TO BE TUNED FROM IMPEDANCE MEASUREMENT"; one common chain STM32G474 → DAC3 → OPA2356 → common 4th-order Butterworth
reconstruction filter (~600 kHz) → TP1, then Band L PA / Band H PA (only the selected band is enabled for each ping). Register
r03: 66 rows. AUV mechanical geometry (B300 housing, mounting, acoustic window, penetrators, hull, thrusters, payload axis)
unchanged: 278 meshes byte-identical to r02. Sections above this one record earlier revisions (r02) and keep their
original wording.

**Interface.** New layout: header with team, title, permanent truth label, theme / presentation-layout / full-screen
buttons; left view rail in two groups (icon rail up to 1599 px); inspector tabs (Inspect, Components, Display); project
summary card with key figures, band shortcuts and the transmit chain; loading screen with download progress; dark default
with a light theme (remembered per browser); keys 1–9 / F / R / P / Esc; the address follows the current view. Stage
overlays adapt to the stage's own width (container queries). The loading screen takes no pointer events and is removed
from the page once the model is ready. Callouts keep a 62 px strip clear above the bottom edge for the camera toolbar.

**Checks** (local static server, 1720 × 940, 1440 × 860, 1366 × 768, 1024 × 700, 375 px; dark and light):

| Check | Result |
|---|---|
| All 9 views (rail buttons and keys 1–9) | correct caption, labels, path steps (Band L 12, 500 kHz 12, Power 10, Sensing 8 steps); no console errors |
| Deep links | `#pathA` opens Band L and rewrites to `#pathL`; address follows the view |
| Selection | opens the Inspect tab with the selection card; Esc clears it |
| Presentation layout (P) | side panels hidden, stage 1004 px at 1024 px; restored on the second press |
| 1024 × 700 | rail fits without scrolling; evidence tags move bottom-left; caption full width; no horizontal scroll |
| 375 px | chip strip with the active view centred; inspector below the stage; no horizontal scroll |
| Leftover scan of index.html, viewer.html, README.md | none of the retired r02 low-band labels, part number or inductor values |

## Web model r04: AUV-platform detail and realistic finishes (2026-10-05)

**Geometry (FreeCAD 1.1.4, `SIH26058_AUV_PLATFORM_DETAIL_r04.FCStd`, script `build_platform_r04.py`).** Real CAD solids
(all `isValid`) built inside the r03 envelopes, tessellated per CAD face with MeshPart (linear 0.05-0.06 mm, angular
0.1-0.3 rad) and merged into the r03 GLB under the same node names, groups and extras:

| Part (x4 unless noted) | r03 | r04 |
|---|---|---|
| Stabiliser fin | 3 mm flat plate (24 vertices) | NACA 0008-class foil, same planform (LE 930 -> 960 mm, TE 1010 mm, tip edge kept) |
| Thruster motor | cylinder with nose | bullet nose, can with two service grooves, rear bell, shaft; X 1025-1117 mm, r 15.2 mm |
| Thruster duct | plain tube r 27.8-31.2 mm | Kort-type foil-section ring (throat r ~28 mm), three stator vanes |
| Propeller | three flat bars (72 vertices) | 3 twisted blades (55 mm pitch, skew), hub and spinner; tip r 27 mm inside the duct throat |
| Strut | box | streamlined foil pylon on the thruster diagonal |
| Joint rings (2, new) | - | nose/hull (X 200) and hull/tail (X 900) clamp rings, 8 socket cap screws each, 1 mm proud of the hull |
| Tail end plate (new) | flat painted end face | chamfered end plate on r 30 mm, six cap screws, 1.5 mm proud of the tail end |

20 meshes replaced, 3 added; the other 268 meshes (B300 payload, hull midbody, nose, tail cone, mounting, acoustic window,
penetrators, connections) are byte-identical to r03. Overall length grows about 2 mm (tail end plate and its screw heads). 291 meshes; GLB 13.2 MB.

**Finishes (viewer).** Hull, nose and tail cone in safety-yellow paint with a clear coat (MeshPhysicalMaterial); B300 tube,
flanges and caps in blue anodised aluminium; cradle and rails in black anodised aluminium; composite fins; black polymer
thrusters; anodised clamp rings; boards in green-teal solder mask; chassis in machined aluminium. Opaque parts receive
shadows (self-shadowing). Presentation colours for the projectors, sensors, connections and path highlights are unchanged.

**Checks** (local static server, 1440 x 860): model loads (291 meshes), no console errors; all views render; cutaway
clips the new joint rings and end plate with the hull; exploded, payload and path views keep their labels and colours.

## Web model r05: AUV detailing and context systems (2026-10-06)

**Geometry (FreeCAD 1.1.4, `SIH26058_AUV_PLATFORM_DETAIL_r05.FCStd`, script `build_platform_r05.py`, 43 valid solids).**
All r04 parts (stator vanes moved 1 mm forward: blade clearance now 0.8 mm), plus:
- Hull hardware: 20 mm clamp bands with two over-centre latches at the nose/hull and hull/tail joints (replace the r04
  joint rings); payload-bay bulkheads rebuilt inside their r03 envelope with 8 bolts and a cable gland each; flush hull
  screws at the bulkhead stations; screws around the acoustic-window frame (frame unchanged); carry handle on top
  (X 524-596); antenna mast (X 865, top at Y 131.5 mm); nose sensor window and bezel (0.2 mm ahead of the nose tip).
- AUV context systems (new group `AUV_SYSTEMS`, own row in the Components tree): forward sensor module in the nose,
  battery pack in the aft hull compartment (X 808-894), thruster driver stack in the tail cone (X 920-972) with
  wiring to the four thruster pylons. Labelled AUV context; no capacity, rating or part number is claimed.
- Finishes: satin-black nose and tail cone, yellow hull, black clamp bands, per-part finishes from the CAD extras.

22 meshes replaced, 21 added; the other 266 meshes (B300 payload, hull midbody, nose, tail cone, mounting,
acoustic-window frame, connections) are byte-identical to r03. 309 meshes; GLB 14.6 MB.

**Design check (r05 geometry, mm):**

| Check | Result |
|---|---|
| B300 tube axis | (Y, Z) = (-20, 0), r 56; clearance to the hull bore (r 87): tube 11.0, flanges 9.8, end caps 6.8 |
| Payload inside the bay (X 225-800) and the hull bore | yes; only the acoustic-output ring symbols lie outside (presentation symbols) |
| Projectors over the acoustic window (X 220-317.5, Z -14.2..42.3) | Band L X 234-264, Band H X 269.5-301, both Z 2.3-33.7; faces at Y -90 (flush with the hull) |
| Propeller tip to duct throat | 0.5 mm |
| Fins to thrusters | 15 mm axial gap |
| AUV context parts | inside the hull bore / tail cone (battery frame r 84.2, driver frame r 83.1) |
| Thruster pods vs tail cone (r03 positions, unchanged) | **finding:** motor noses intersect the tail-cone surface by up to 5.5 mm and the duct leading edges touch it (-0.4 mm). A build would move the thruster axes out (about 84 mm radius instead of 77.8 mm) or fair the pods into the cone. |

**Checks** (local static server, 1440 x 860): model loads (309 meshes), no console errors; AUV context systems visible only in
Complete AUV and Cutaway; Cutaway shows 9 callouts (3 AUV context); AUV SYSTEMS tree row hides all 12 context parts;
selection shows the CAD description, status and source; presentation layout (P) re-frames the view for the new stage size.

## Web model r06: payload detail on the r04 vehicle (2026-10-06)

r05 (black nose / tail, handle, antenna, AUV context systems) is withdrawn at the team's request: the r04 yellow / black
vehicle is restored unchanged, and the detail effort goes into the B300 transmitter payload.

**Payload detail.** 70 payload objects get detailed geometry inside their r03 envelopes (name, position, register links,
status and representation unchanged) and 94 `PKG_*` detail parts are added, each linked to its component through the
extras `Parent` (the r02 package-lead convention), so hover, selection and path highlighting treat them as that component:

| Item | r04 | r06 |
|---|---|---|
| 8 PCBs | flat slabs | rounded corners, M3 clearance holes at their standoffs; pan-head screws where a head fits (collision checked) |
| 32 standoffs | cylinders | hex standoffs (nickel) |
| 18 board connectors (type TBD) | boxes | shrouded headers with an open mating cavity, polarising slot and gold pins (one row) |
| Tuning inductors L / H | reserved blocks | toroids (26 / 13 x 12.6 mm) with 20 copper turns on a mounting base; winding top meets the reserved height |
| Transformers L / H (TBD) | blocks | vertical-mount toroids with two 8-turn windings on a moulded base |
| Boost inductor | block | shielded SMD inductor with board-side pads |
| EEUFR1H102 (LOCKED, dia 16 x 25) | plain can | sleeve with groove and bung, aluminium top with K-vent, polarity stripe |
| Reconstruction filter (values CALC, parts TBD) | block | 12 x 12 daughterboard on two 1x4 headers with an R / C network |
| ICs without leads (INA241A, TPS62933, TPS2663, LM5157, load switch) | bodies | leads / pads |
| Passives | none | 54 decoupling / bias / feedback parts around the ICs, I2C pull-ups, MCU crystal; all placed with collision checks |
| VSENSE, SHUNT, FUSE, TVS | blocks | terminations / leads added (bodies unchanged) |
| Projectors | bodies | fired-silver electrodes on both faces |
| Desiccant, chassis bulkheads | box, discs | sachet; lightening and screw holes |

All new parts carry Representation "E. PRESENTATION STYLISATION" and Evidence "not taken from a schematic or a PCB
layout"; placeholders keep "D. PLACEHOLDER - DIMENSIONS NOT VERIFIED". 221 other meshes (the whole r04 vehicle, B300
housing, sensors, connections, cables) are byte-identical to r04. 385 meshes; GLB 15.9 MB.

**Checks** (local static server, 1440 x 860): model loads, no console errors; all 9 views (labels and paths unchanged);
Band L path highlights the Band L winding, transformer, PA passives, connector pins and filter network and not the Band H
parts; selecting a winding shows the inductor's role and its TBD / placeholder evidence; connection links still meet the
component tops (magnetics sized to their reserved heights).
