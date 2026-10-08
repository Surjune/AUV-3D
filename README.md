# AUV-3D · SIH26058 adaptive sonar transmitter payload

Interactive 3D digital twin of the **Lightning Logics** design for Smart India Hackathon 2026, problem statement
**SIH26058**: a low-power, real-time adaptive software-defined sonar transmitter payload for AUVs (Ministry of Earth
Sciences, NIOT).

**Live viewer:** https://auv.lightninglogics.me

> System-level CAD — presentation model — not fabricated. Architectural connections, not PCB routing.

## What it shows
- The B300 transmitter payload inside the AUV payload bay: complete vehicle, payload, cutaway and exploded views.
- The signal chain: STM32G474 → DAC3 → OPA2356 4th-order ~600 kHz filter → TP1 (oscilloscope / FFT) → Band L
  (~120 kHz class) or Band H (500 kHz class) THS3491 bridge amplifier → matching network → PZT projector. Only the
  selected band is enabled for each ping.
- Power and sensing paths, and all 68 rows of the connectivity register drawn on the model.
- A frequency plan: f0 tunes continuously from 100 to 500 kHz at TP1; in water, output is efficient near each
  projector's resonance.
- Guided tour, search (Ctrl K), system diagram, part links, section plane and snapshot.

## Repository layout
| Folder | Contents |
|---|---|
| [`SIH26058_COMPLETE_AUV_3D_VIEWER/`](SIH26058_COMPLETE_AUV_3D_VIEWER) | The viewer: `index.html`, the GLB model, the embedded model fallback, the connectivity register and the [viewer README](SIH26058_COMPLETE_AUV_3D_VIEWER/README.md) and [validation notes](SIH26058_COMPLETE_AUV_3D_VIEWER/VALIDATION.md) |
| [`CAD_SOURCE/`](CAD_SOURCE) | FreeCAD 1.1 presentation sources and the scripts that build them ([CAD README](CAD_SOURCE/README.md)) |

## Run locally
Open `SIH26058_COMPLETE_AUV_3D_VIEWER/index.html` in a browser (internet needed for three.js), or serve the folder:

```bash
python -m http.server 8000 --directory SIH26058_COMPLETE_AUV_3D_VIEWER
```

Then open http://localhost:8000.
