"""SIH26058 B300 payload detail r06 (FreeCAD 1.1, run with freecadcmd).

Presentation detail for the transmitter payload electronics, built inside the r03/r04 envelopes of the existing CAD
objects (names, positions and envelopes unchanged; register endpoints unchanged):
  boards with rounded corners and M3 holes at their standoffs, shrouded board connectors with pins, toroidal
  tuning inductors and transformers with copper windings, shielded boost inductor, Panasonic EEUFR1H102 can detail,
  reconstruction-filter daughterboard on headers, desiccant sachet, chassis bulkheads with lightening holes.
Every shape is a presentation stylisation: placeholders stay placeholders (status unchanged).
Frame: web-model frame in millimetres - X along the vehicle, Y up, Z lateral. Writes SIH26058_PAYLOAD_DETAIL_r06.FCStd
and one tessellation per part (per CAD face, metres) into tess/.
"""
import math, os, json
import numpy as np
import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector as V

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
os.makedirs(os.path.join(OUT, "tess"), exist_ok=True)
BB = json.load(open(os.path.join(OUT, "bbox_r04.json")))
UPPER_TOP, LOWER_BOT = -13.4, -26.6                     # component faces of the two board tiers


def lohi(n):
    lo, hi = BB[n]
    return np.array(lo, dtype=float), np.array(hi, dtype=float)


def vec(a):
    return V(*[float(x) for x in a])


def box(lo, hi):
    return Part.makeBox(*[float(x) for x in (hi - lo)], vec(lo))


def vert_edges(shape):
    return [e for e in shape.Edges if abs(e.Vertexes[0].Point.y - e.Vertexes[-1].Point.y) > 0.5
            and abs(e.Vertexes[0].Point.x - e.Vertexes[-1].Point.x) < 1e-6 and abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) < 1e-6]


def standoffs_of(board):
    lo, hi = lohi(board)
    upper = hi[1] > -20
    out = []
    for n in BB:
        if not n.startswith("STANDOFF_"):
            continue
        a, b = lohi(n)
        c = (a + b) / 2
        if lo[0] < c[0] < hi[0] and lo[2] < c[2] < hi[2] and ((b[1] <= -14.9) if upper else (a[1] >= -25.1)) and abs((b[1] if upper else a[1]) - (lo[1] if upper else hi[1])) < 0.2:
            out.append((float(c[0]), float(c[2])))
    return out


# ---------- boards: rounded corners, M3 clearance holes at their standoffs
def board(n):
    lo, hi = lohi(n)
    s = box(lo, hi)
    s = s.makeFillet(2.0, vert_edges(s))
    for x, z in standoffs_of(n):
        s = s.cut(Part.makeCylinder(1.6, float(hi[1] - lo[1] + 2), V(x, float(lo[1] - 1), z), V(0, 1, 0)))
    return s


# ---------- shrouded board connector: housing with an open mating cavity, pins in one row
def connector(n):
    lo, hi = lohi(n)
    upper = lo[1] >= UPPER_TOP - 0.05
    sx, sy, sz = hi - lo
    along_z = sz >= sx
    L, W = (sz, sx) if along_z else (sx, sz)
    wall, floor = 0.6, 1.4
    sx, sy, sz = float(sx), float(sy), float(sz)
    lo, hi = [float(x) for x in lo], [float(x) for x in hi]
    housing = Part.makeBox(sx, sy, sz, V(*lo))
    cav_y = lo[1] + floor if upper else lo[1]
    housing = housing.cut(Part.makeBox(sx - 2 * wall, sy - floor, sz - 2 * wall, V(lo[0] + wall, cav_y, lo[2] + wall)))
    key = Part.makeBox(1.0 if along_z else 1.2, sy - floor, 1.2 if along_z else 1.0,
                       V(lo[0] - 0.01 if along_z else (lo[0] + hi[0]) / 2 - 0.6, cav_y, (lo[2] + hi[2]) / 2 - 0.6 if along_z else lo[2] - 0.01))
    housing = housing.cut(key)                           # polarising slot in one long wall
    npin = max(2, int((L - 2 * wall) // 2.5))
    pitch = (L - 2 * wall) / npin
    y0, y1 = (lo[1], hi[1] - 1.0) if upper else (lo[1] + 1.0, hi[1])
    pins = []
    for k in range(npin):
        t = (lo[2] if along_z else lo[0]) + wall + pitch * (k + 0.5)
        cx, cz = ((lo[0] + hi[0]) / 2, t) if along_z else (t, (lo[2] + hi[2]) / 2)
        pins.append(Part.makeBox(0.64, y1 - y0, 0.64, V(cx - 0.32, y0, cz - 0.32)))
    return housing, Part.makeCompound(pins)


# ---------- toroid with windings (axis along Y; sign +1 builds upwards from the board, -1 downwards)
def winding_loop(ri, ro, h, wire, rc=0.9):
    a, b, c, d = ri - wire - 0.15, ro + wire + 0.15, -wire - 0.15, h + wire + 0.15
    e = [Part.LineSegment(V(a + rc, c, 0), V(b - rc, c, 0)).toShape(),
         Part.Arc(V(b - rc, c, 0), V(b - rc + rc * math.sqrt(0.5), c + rc - rc * math.sqrt(0.5), 0), V(b, c + rc, 0)).toShape(),
         Part.LineSegment(V(b, c + rc, 0), V(b, d - rc, 0)).toShape(),
         Part.Arc(V(b, d - rc, 0), V(b - rc + rc * math.sqrt(0.5), d - rc + rc * math.sqrt(0.5), 0), V(b - rc, d, 0)).toShape(),
         Part.LineSegment(V(b - rc, d, 0), V(a + rc, d, 0)).toShape(),
         Part.Arc(V(a + rc, d, 0), V(a + rc - rc * math.sqrt(0.5), d - rc + rc * math.sqrt(0.5), 0), V(a, d - rc, 0)).toShape(),
         Part.LineSegment(V(a, d - rc, 0), V(a, c + rc, 0)).toShape(),
         Part.Arc(V(a, c + rc, 0), V(a + rc - rc * math.sqrt(0.5), c + rc - rc * math.sqrt(0.5), 0), V(a + rc, c, 0)).toShape()]
    path = Part.Wire(e)
    prof = Part.Wire(Part.makeCircle(wire, V(a + rc, c, 0), V(1, 0, 0)))
    return path.makePipeShell([prof], True, True)


def place(shape, cx, y0, cz, sign, theta=0.0):
    s = shape.copy()
    if sign < 0:
        s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    if theta:
        s.rotate(V(0, 0, 0), V(0, 1, 0), theta)
    s.translate(V(cx, y0, cz))
    return s


def toroid(cx, cz, board_y, sign, od, idd, h, sets, wire):
    """sets: list of (start deg, end deg, turns). Returns core, windings (incl. leads), mount."""
    base_t, gap = 1.5, 0.3
    Y = V(0, 1, 0)
    mount = place(Part.makeCylinder(od / 2 + 0.5, base_t, V(0, 0, 0), Y), cx, board_y, cz, sign)
    core = Part.makeCylinder(od / 2, h, V(0, 0, 0), Y).cut(Part.makeCylinder(idd / 2, h, V(0, 0, 0), Y))
    core = core.makeFillet(min(1.0, h / 4), [e for e in core.Edges if isinstance(e.Curve, Part.Circle)])
    core = place(core, cx, board_y + sign * (base_t + gap), cz, sign)
    loop = winding_loop(idd / 2, od / 2, h, wire)
    turns, leads = [], []
    for a0, a1, n in sets:
        for k in range(n):
            th = a0 + (a1 - a0) * (k + 0.5) / n
            turns.append(place(loop, cx, board_y + sign * (base_t + gap), cz, sign, th))
        for th in (a0, a1):                               # lead-outs down to the board
            r = od / 2 + wire + 0.15
            x, z = cx + r * math.cos(math.radians(th)), cz - r * math.sin(math.radians(th))
            y_top = board_y + sign * (base_t + gap)
            leads.append(Part.makeCylinder(wire, abs(y_top - board_y) + 0.2, V(x, min(board_y, y_top) - 0.1, z), V(0, 1, 0)))
    return core, Part.makeCompound(turns + leads), mount


def vtoroid(cx, cz, board_y, sign, od, idd, h, sets, wire):
    """Vertical-mount toroid (axis along X) on a moulded base with four pins; the top reaches the reserved envelope."""
    Y = V(0, 1, 0)
    core = Part.makeCylinder(od / 2, h, V(0, -h / 2, 0), Y).cut(Part.makeCylinder(idd / 2, h, V(0, -h / 2, 0), Y))
    core = core.makeFillet(min(1.0, h / 4), [e for e in core.Edges if isinstance(e.Curve, Part.Circle)])
    loop = winding_loop(idd / 2, od / 2, h, wire)
    loop.translate(V(0, -h / 2, 0))
    turns = []
    for a0, a1, n in sets:
        for k in range(n):
            t = loop.copy()
            t.rotate(V(0, 0, 0), Y, a0 + (a1 - a0) * (k + 0.5) / n)
            turns.append(t)
    wind = Part.makeCompound(turns)
    yc = board_y + sign * (1.8 + wire + 0.15 + od / 2)
    for sh in (core, wind):
        sh.rotate(V(0, 0, 0), V(0, 0, 1), 90)
        sh.translate(V(cx, yc, cz))
    bw, bd = h + 3.0, od * 0.75
    base = Part.makeBox(bw, 1.8, bd, V(cx - bw / 2, board_y if sign > 0 else board_y - 1.8, cz - bd / 2))
    base = base.makeFillet(0.5, vert_edges(base))
    pins = [Part.makeCylinder(0.4, 1.0, V(cx + dx, board_y - (1.0 if sign > 0 else 0.0) + (0.0 if sign > 0 else 0.0), cz + dz), Y)
            for dx in (-bw / 2 + 1.2, bw / 2 - 1.2) for dz in (-bd / 2 + 1.5, bd / 2 - 1.5)]
    return core, wind, Part.makeCompound([base] + pins)


# ---------- shielded SMD power inductor
def smd_inductor(n):
    lo, hi = lohi(n)
    s = box(lo, hi)
    s = s.makeFillet(2.4, vert_edges(s))
    return s


# ---------- Panasonic EEUFR1H102 radial can (16 x 25), hanging below the PA-power board
def eeufr_can():
    lo, hi = lohi("PKG_EEUFR1H102_CAN")
    cx, cz = float(lo[0] + hi[0]) / 2, float(lo[2] + hi[2]) / 2
    top = float(hi[1])                                    # board side (rubber bung)
    prof = [(0, 0), (7.6, 0), (7.6, 0.8), (8.0, 1.0), (8.0, 2.6), (7.6, 3.0), (7.6, 3.6), (8.0, 4.0), (8.0, 24.3),
            (7.5, 24.8), (7.0, 24.8), (7.0, 24.6), (0, 24.6), (0, 0)]
    e = [Part.LineSegment(V(prof[i][0], -prof[i][1], 0), V(prof[i + 1][0], -prof[i + 1][1], 0)).toShape() for i in range(len(prof) - 1)]
    sleeve = Part.Face(Part.Wire(e)).revolve(V(0, 0, 0), V(0, 1, 0), 360)
    sleeve.translate(V(cx, top, cz))
    disc = Part.makeCylinder(7.2, 0.4, V(cx, top - 25.0, cz), V(0, 1, 0))
    for a in (90, 210, 330):                              # K-vent score lines
        cut = Part.makeBox(5.5, 0.25, 0.5, V(0, -0.1, -0.25))
        cut.rotate(V(0, 0, 0), V(0, 1, 0), a)
        cut.translate(V(cx, top - 25.0, cz))                 # scored into the outer (vent) face
        disc = disc.cut(cut)
    stripe = Part.makeCylinder(8.06, 20.0, V(cx, top - 24.2, cz), V(0, 1, 0), 55).cut(Part.makeCylinder(7.98, 20.0, V(cx, top - 24.2, cz), V(0, 1, 0), 55))
    stripe.rotate(V(cx, 0, cz), V(0, 1, 0), 200)
    return sleeve, disc, stripe


# ---------- reconstruction-filter daughterboard on two 1x4 headers
def recon_daughterboard():
    lo, hi = lohi("RECON_FILTER")
    lo, hi = [float(x) for x in lo], [float(x) for x in hi]
    pcb = Part.makeBox(hi[0] - lo[0], 1.4, hi[2] - lo[2], V(lo[0], -9.4, lo[2]))
    pcb = pcb.makeFillet(1.0, vert_edges(pcb))
    heads, pins = [], []
    for x0 in (lo[0] + 0.5, hi[0] - 3.0):
        heads.append(Part.makeBox(2.5, 4.0, hi[2] - lo[2] - 2.0, V(x0, UPPER_TOP, lo[2] + 1.0)))   # flush under the daughterboard
        for k in range(4):
            z = lo[2] + 1.0 + (hi[2] - lo[2] - 2.0) * (k + 0.5) / 4
            pins.append(Part.makeBox(0.64, 6.0, 0.64, V(x0 + 1.25 - 0.32, UPPER_TOP, z - 0.32)))
    return pcb, Part.makeCompound(heads), Part.makeCompound(pins)


def sachet():
    lo, hi = lohi("DESICCANT")
    s = box(lo, hi)
    return s.makeFillet(2.5, s.Edges)


def chassis_bulkhead(n):
    lo, hi = lohi(n)
    lo, hi = [float(x) for x in lo], [float(x) for x in hi]
    cy, cz, r = (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2, (hi[2] - lo[2]) / 2
    s = Part.makeCylinder(r, hi[0] - lo[0], V(lo[0], cy, cz), V(1, 0, 0))
    for a, rr, rh in [(60, 34, 5.0), (120, 34, 5.0), (240, 34, 5.0), (300, 34, 5.0), (90, 40, 4.0), (270, 40, 4.0)]:
        y, z = cy + rr * math.sin(math.radians(a)), cz + rr * math.cos(math.radians(a))
        s = s.cut(Part.makeCylinder(rh, hi[0] - lo[0] + 2, V(lo[0] - 1, y, z), V(1, 0, 0)))
    for a in range(0, 360, 60):                           # M3 screw holes on the rim
        y, z = cy + (r - 4) * math.sin(math.radians(a + 30)), cz + (r - 4) * math.cos(math.radians(a + 30))
        s = s.cut(Part.makeCylinder(1.6, hi[0] - lo[0] + 2, V(lo[0] - 1, y, z), V(1, 0, 0)))
    return s


# ---------- build: name -> (shape, (linear, angular), finish, mode)   mode: "replace" or (parent, group, component)
parts = {}
for n in sorted(BB):
    if n.startswith("PCB_"):
        parts[n] = (board(n), (0.03, 0.3), None, "replace")
for n in sorted(BB):
    if n.startswith("J_"):
        h, p = connector(n)
        parts[n] = (h, (0.03, 0.3), "nylon", "replace")
        parts[f"PKG_{n}_PINS"] = (p, (0.03, 0.3), "gold", (n, "PCB_COMPONENT_LAYOUT", f"{n} contact pins (presentation)"))
for n, sign, (od, idd, h), sets, wire in [
        ("L_TUNE_L", 1, (26.0, 13.0, 12.6), [(25, 335, 20)], 0.45),         # winding top meets the reserved envelope (1.6)
        ("L_TUNE_H", -1, (26.0, 13.0, 12.6), [(25, 335, 20)], 0.45),
        ("XFMR_L", 1, (12.2, 6.0, 6.0), [(15, 165, 8), (195, 345, 8)], 0.35),  # vertical mount: top meets the envelope
        ("XFMR_H", -1, (12.2, 6.0, 6.0), [(15, 165, 8), (195, 345, 8)], 0.35)]:
    lo, hi = lohi(n)
    fn = vtoroid if n.startswith("XFMR") else toroid
    core, wind, mount = fn(float(lo[0] + hi[0]) / 2, float(lo[2] + hi[2]) / 2, UPPER_TOP if sign > 0 else LOWER_BOT, sign, od, idd, h, sets, wire)
    parts[n] = (core, (0.04, 0.3), "ferrite", "replace")
    parts[f"PKG_{n}_WINDING"] = (wind, (0.05, 0.45), "copper", (n, "PCB_COMPONENT_LAYOUT", f"{n} copper winding (presentation stylisation)"))
    parts[f"PKG_{n}_MOUNT"] = (mount, (0.04, 0.3), "black_polymer", (n, "PCB_COMPONENT_LAYOUT", f"{n} mounting base (presentation)"))
parts["L_BOOST"] = (smd_inductor("L_BOOST"), (0.03, 0.3), "ferrite", "replace")
sl, disc, stripe = eeufr_can()
parts["PKG_EEUFR1H102_CAN"] = (sl, (0.03, 0.25), "sleeve_black", "replace")
parts["PKG_EEUFR1H102_TOP"] = (disc, (0.03, 0.3), "aluminium", ("EEUFR1H102", "PCB_COMPONENT_LAYOUT", "EEUFR1H102 aluminium top with K-vent (presentation)"))
parts["PKG_EEUFR1H102_STRIPE"] = (stripe, (0.03, 0.3), "stripe_grey", ("EEUFR1H102", "PCB_COMPONENT_LAYOUT", "EEUFR1H102 polarity stripe (presentation)"))
pcb, heads, pins = recon_daughterboard()
parts["RECON_FILTER"] = (pcb, (0.03, 0.3), "pcb_teal", "replace")
parts["PKG_RECON_FILTER_HEADERS"] = (heads, (0.03, 0.3), "black_polymer", ("RECON_FILTER", "PCB_COMPONENT_LAYOUT", "Filter daughterboard headers (presentation stylisation)"))
parts["PKG_RECON_FILTER_PINS"] = (pins, (0.03, 0.3), "gold", ("RECON_FILTER", "PCB_COMPONENT_LAYOUT", "Filter daughterboard header pins (presentation)"))
parts["DESICCANT"] = (sachet(), (0.05, 0.3), "sachet", "replace")
for n in ("CHASSIS_BULKHEAD_FWD", "CHASSIS_BULKHEAD_AFT"):
    parts[n] = (chassis_bulkhead(n), (0.05, 0.2), None, "replace")

doc = App.newDocument("SIH26058_PAYLOAD_DETAIL_r06")
meta = {}
for name, (shape, tol, fin, mode) in parts.items():
    assert shape.isValid(), name
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    P, T, off = [], [], 0
    for face in shape.Faces:
        msh = MeshPart.meshFromShape(Shape=face, LinearDeflection=tol[0], AngularDeflection=tol[1], Relative=False)
        v, t = msh.Topology
        if not t:
            continue
        P += [(q.x, q.y, q.z) for q in v]
        T += [(a + off, b + off, c + off) for a, b, c in t]
        off += len(v)
    P = np.array(P, dtype=np.float64)
    np.savez(os.path.join(OUT, "tess", name + ".npz"), pos=(P / 1000.0).astype(np.float32), idx=np.array(T, dtype=np.uint32))
    m = {"verts": len(P), "tris": len(T), "finish": fin, "bbox_mm": [round(float(v), 2) for v in list(P.min(0)) + list(P.max(0))]}
    if mode != "replace":
        m.update(parent=mode[0], group=mode[1], component=mode[2])
    meta[name] = m
doc.recompute()
doc.saveAs(os.path.join(OUT, "SIH26058_PAYLOAD_DETAIL_r06.FCStd"))
json.dump(meta, open(os.path.join(OUT, "tess", "meta_fc.json"), "w"), indent=1)
for n, m in meta.items():
    print(n, m["verts"], m["bbox_mm"])
print("saved", len(meta), "parts; verts", sum(m["verts"] for m in meta.values()))
