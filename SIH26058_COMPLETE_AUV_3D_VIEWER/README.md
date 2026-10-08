# SIH26058 transmitter payload · interactive digital twin (viewer v8, web model r06)

SYSTEM-LEVEL CAD — PRESENTATION MODEL — NOT FABRICATED.
PCB COMPONENT LAYOUT — PRESENTATION MODEL — NOT FABRICATED. ARCHITECTURAL CONNECTIONS — NOT PCB ROUTING.
AUV platform geometry is proposed presentation-level geometry. Transmitter payload is linked from the SIH26058 B300
presentation model (SIH26058_PAYLOAD_B300_r02_PRESENTATION_v2.FCStd). Web model r03 is edited from the r02 export for the
Band L (~120 kHz class) / Band H (500 kHz class) transducer architecture. Web model r06 = the r04 vehicle (AUV-platform detail,
SIH26058_AUV_PLATFORM_DETAIL_r04.FCStd) plus B300 payload presentation detail (SIH26058_PAYLOAD_DETAIL_r06.FCStd); both
FreeCAD 1.1 sources are kept in ../CAD_SOURCE, not deployed. The payload FreeCAD source
update is pending.

## Open it
- Double-click `index.html` (the model is embedded; three.js loads from cdn.jsdelivr.net, so internet is needed), or
- host this folder on any static web server and open `index.html`. Deep links: `#payload`, `#cutaway`, `#exploded`,
  `#arch`, `#pathL`, `#pathH`, `#power`, `#sensing` (the older `#pathA` / `#pathB` links still open the two band paths).
  The address follows the current view, so a copied link reopens the same view. `#view:PART` (for example
  `#payload:L_TUNE_L`) opens one part in that view; the selection's Copy link button writes it.

## Files
| File | Purpose |
|---|---|
| index.html | Viewer page (three.js 0.160.0 from cdn.jsdelivr.net) |
| SIH26058_COMPLETE_AUV_r06.glb | Web 3D model (glTF 2.0 binary, metres, Y up): r03 (edited from the r02 export of SIH26058_COMPLETE_AUV_PRESENTATION_r02.FCStd) plus the platform detail of SIH26058_AUV_PLATFORM_DETAIL_r04.FCStd and the payload presentation detail of SIH26058_PAYLOAD_DETAIL_r06.FCStd |
| model_data.js | Same GLB as base64, used automatically when the page is opened from disk |
| viewer.html | Page source used for the hosted version (68-row connectivity register embedded) |
| SIH26058_CONNECTIVITY_REGISTER_r04.csv | Connectivity register r04 (68 rows): r03 plus CTRL-05 / CTRL-06, the power-down links to THS3491 L2 / H2 |
| SIH26058_CONNECTIVITY_REGISTER_r03.csv | Connectivity register r03 (66 rows), kept for reference |

GLB SHA-256: 1697a81f950a7177d15f9bcda67574cdcf09077fb30c0f1ddbd96676ce825bf0  (15,859,640 bytes)

## Layout
Header: team, page title, search, the permanent truth label, guided tour, theme (dark / light), presentation layout
(hides the side panels) and full screen. Left rail: the nine views in two groups (model views; signal and power paths).
Centre: the 3D stage with Fit view, Reset view, Snapshot (2x PNG with labels) and, in Cutaway, the section-plane slider.
Right: the inspector with three tabs — Inspect (selection with Focus / Isolate / Copy link, path steps, legend, system
diagram, frequency plan, low-power design, project summary), Components (subsystem trees with show / hide, all CAD
objects) and Display (opacity, controls, evidence-status key). Under 820 px the rail becomes a scrolling chip strip and
the page scrolls.

The guided tour walks through ten steps (vehicle, payload, common chain, Band L, Band H, matching, projectors, power,
sensing, all connections). The frequency plan separates what the waveform does at TP1 (f0 tunes continuously from 100 to
500 kHz) from what reaches the water (efficient near the Band L and Band H projector resonances; spans to be measured).

## Navigation
Left-drag: rotate · right-drag: pan · wheel: zoom (towards the cursor) · double-click: focus a part.
Touch: one finger rotates, two fingers pan / pinch-zoom. Keys: Ctrl K or / search, T guided tour (arrows step, Esc
ends), 1–9 views (rail order), F fit, R reset, P presentation layout, ? shortcut list, Esc ends isolation and then
clears the selection. FIT VIEW frames the selection (or the current view's content); RESET VIEW returns to the
current view's default camera; the axis gizmo (bottom-right) snaps to a principal direction.

## Modes
Complete AUV · Transmitter payload · Cutaway · Payload exploded · Payload architecture · Band L – ~120 kHz path ·
500 kHz path · Power path · Sensing. Paths are the rows of SIH26058_CONNECTIVITY_REGISTER_r04.csv; the inspector lists
each step with its register IDs. Hover shows component, role (component register / connectivity register) and evidence
status; click shows CAD evidence, source object and the component's register connections.
