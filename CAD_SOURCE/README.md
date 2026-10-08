# SIH26058 FreeCAD sources for web model r06

PRESENTATION LEVEL. Presentation geometry, not engineering; no verified specification.

| File | Contents |
|---|---|
| `SIH26058_AUV_PLATFORM_DETAIL_r04.FCStd` + `build_platform_r04.py` | AUV platform detail (yellow / black vehicle): foil-section fins, 4 ducted thrusters (motor pod, Kort-type nozzle with stator vanes, 3-blade propeller, pylon), joint rings, tail end plate. Envelopes and positions as web model r03. |
| `SIH26058_PAYLOAD_DETAIL_r06.FCStd` + `build_payload_r06.py` (+ `bbox_r04.json`, the r04 object envelopes it reads) | B300 transmitter payload presentation detail: boards with rounded corners and M3 holes, shrouded connectors with pins, toroidal tuning inductors and vertical-mount transformers with copper windings, shielded boost inductor, EEUFR1H102 can detail, reconstruction-filter daughterboard on headers, desiccant sachet, chassis bulkheads with lightening holes. |

Every payload shape is a presentation stylisation drawn inside the reserved envelope of an existing CAD object; names,
positions, register links and status (LOCKED / CANDIDATE / PROPOSED / TBD, placeholder or verified) are unchanged.
The small parts (decoupling / bias passives, IC leads and pads, hex standoffs, M3 screws, crystal, projector electrodes)
are generated with the web-model build, placed by collision checking against the existing geometry.

Frame: web-model frame in millimetres - X along the vehicle (nose tip 0 -> tail 1150), Y up, Z lateral.
Run either script with `freecadcmd <script>`; each writes its FCStd and one tessellation per part into `tess/`.
The original FCStd sources (SIH26058_COMPLETE_AUV_PRESENTATION_r02.FCStd, SIH26058_PAYLOAD_B300_r02_PRESENTATION_v2.FCStd)
are not on this machine; their update is pending.
