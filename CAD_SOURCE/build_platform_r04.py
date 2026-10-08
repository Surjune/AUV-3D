"""SIH26058 AUV platform detail r04 (FreeCAD 1.1, run with freecadcmd).

Rebuilds the AUV-context propulsion and fins as real CAD solids inside the r03 envelopes, adds hull joint
clamp rings and a tail cap, saves SIH26058_AUV_PLATFORM_DETAIL_r04.FCStd and writes one tessellation per
part (per CAD face, metres) for the web-model merge.

Frame = web-model frame, millimetres: X along the vehicle (nose tip 0 -> tail end 1150), Y up, Z lateral.
Positions and outer envelopes follow the r03 web model:
  thruster axes at (Y, Z) = (+-55, +-55); motor X 1025-1129, r 15.2; duct X 1111-1141, r <= 31.4;
  propeller X 1116-1135 inside the duct; strut on the diagonal at X 1054-1084;
  fins at 0 / 90 / 180 / 270 deg, leading edge (930, r 86.2) -> (960, r 110.2), trailing edge X 1010,
  tip edge (960, 110.2) -> (1010, 105.2).
"""
import math, os, json
import numpy as np
import FreeCAD as App
import Part
import MeshPart
from FreeCAD import Vector as V

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()   # outputs next to this script
os.makedirs(os.path.join(OUT, "tess"), exist_ok=True)
THRUSTERS = {1: (55.0, 55.0), 2: (-55.0, 55.0), 3: (-55.0, -55.0), 4: (55.0, -55.0)}
FIN_ANGLE = {1: 0.0, 2: 90.0, 3: 180.0, 4: 270.0}          # rotation about +X from the +Y fin


# ---------- helpers
def seg(a, b):
    return Part.LineSegment(V(*a), V(*b)).toShape()


def curve(pts):
    bs = Part.BSplineCurve()
    bs.interpolate([V(*p) for p in pts])
    return bs.toShape()


def xy(pts):
    return [(x, r, 0.0) for x, r in pts]


def revolve(edges):
    """Closed profile in the X-Y half plane (Y = radius) revolved 360 deg about the X axis."""
    return Part.Face(Part.Wire(edges)).revolve(V(0, 0, 0), V(1, 0, 0), 360)


def polyline(pts):
    p = xy(pts)
    return [seg(p[i], p[i + 1]) for i in range(len(p) - 1)]


def naca(t, n=36, closed_te=False):
    """Symmetric NACA 4-digit section, unit chord: (s, half thickness) from TE over the upper side to LE and back."""
    k4 = -0.1036 if closed_te else -0.1015
    s = (1 - np.cos(np.linspace(0, math.pi, n))) / 2
    yt = 5 * t * (0.2969 * np.sqrt(s) - 0.1260 * s - 0.3516 * s ** 2 + 0.2843 * s ** 3 + k4 * s ** 4)
    up = list(zip(s[::-1], yt[::-1]))                 # TE -> LE, upper
    lo = list(zip(s[1:], -yt[1:]))                    # LE -> TE, lower
    return up + lo


def foil_wire(points3d):
    """Closed wire: B-spline through the section points, short straight segment across the open trailing edge."""
    e = [curve(points3d)]
    if (V(*points3d[0]) - V(*points3d[-1])).Length > 1e-6:
        e.append(seg(points3d[-1], points3d[0]))
    return Part.Wire(e)


def rotx(shape, deg):
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(1, 0, 0), deg)
    return s


def moved(shape, dy, dz):
    s = shape.copy()
    s.translate(V(0, dy, dz))
    return s


# ---------- thruster parts (local frame: thruster axis = X axis)
def motor():
    nose = [(1040 - 15 * math.cos(a), 15.2 * math.sin(a)) for a in np.linspace(0, math.pi / 2, 14)]
    e = [curve(xy(nose))]
    e += polyline([(1040, 15.2), (1056, 15.2), (1056, 14.6), (1058, 14.6), (1058, 15.2), (1084, 15.2), (1084, 14.6),
                   (1086, 14.6), (1086, 15.2), (1099.5, 15.2), (1101, 14.4), (1112, 14.4), (1115, 12.2), (1115, 3.0),
                   (1117, 3.0), (1117, 0.0), (1025, 0.0)])
    return revolve(e)


def propeller(blades=3, pitch=55.0):
    spin = [(1126.5 + 8.5 * math.sin(a), 6.6 * math.cos(a)) for a in np.linspace(0, math.pi / 2, 10)]
    hub = revolve(polyline([(1115.5, 0.0), (1115.5, 6.6), (1126.5, 6.6)]) + [curve(xy(spin))] + polyline([(1135, 0.0), (1115.5, 0.0)]))
    #          radius  chord  thickness   (blade sections, radial along +Z)
    sections = [(5.5, 9.0, 2.2), (9.0, 13.0, 1.8), (14.0, 17.0, 1.4), (19.0, 18.0, 1.1), (23.5, 15.5, 0.9),
                (26.2, 11.0, 0.7), (27.0, 6.0, 0.6)]
    wires = []
    for r, c, t in sections:
        b = math.atan(pitch / (2 * math.pi * r))       # blade pitch angle to the plane of rotation
        d = V(math.sin(b), math.cos(b), 0)            # chord direction (axial, tangential)
        n = V(math.cos(b), -math.sin(b), 0)
        cen = V(1121.0, 0.4 * (r - 5.5) ** 0.5, r)   # slight skew towards the tip
        wires.append(Part.Wire(Part.Ellipse(cen + d * (c / 2), cen + n * (t / 2), cen).toShape()))
    blade = Part.makeLoft(wires, True, False)
    return Part.makeCompound([hub] + [rotx(blade, k * 360.0 / blades) for k in range(blades)])


def duct():
    le, te, chord = (1111.0, 30.0), (1141.0, 28.9), 30.0
    pts = []
    for s, h in naca(0.113, 40):                      # thickness 3.4 mm, camber line tilts 1.1 mm inwards (nozzle)
        pts.append((le[0] + chord * s, le[1] + (te[1] - le[1]) * s + chord * h, 0.0))
    ring = Part.Face(foil_wire(pts)).revolve(V(0, 0, 0), V(1, 0, 0), 360)
    vane_pts = [(1112.5 + 4.0 * s, 0.0 + 4.0 * h * 1.6, 12.0) for s, h in naca(0.22, 16)]
    vane = Part.Face(foil_wire(vane_pts)).extrude(V(0, 0, 17.6))   # stator vane, r 12 -> 29.6
    return Part.makeCompound([ring] + [rotx(vane, 60 + k * 120) for k in range(3)])


def strut():
    pts = [(1054.0 + 30.0 * s, 30.0 * h, 50.0) for s, h in naca(0.16, 24)]
    return Part.Face(foil_wire(pts)).extrude(V(0, 0, 20.0))   # pylon from inside the tail cone (r 50) into the motor (r 70)


# ---------- fins (fin 1 spans +Y, chord along X, thickness along Z)
def fin():
    def le_x(r):
        return 930.0 + (r - 86.2) * 30.0 / 24.0
    secs = []
    for r in (70.0, 111.0):
        c = 1010.0 - le_x(r)
        secs.append(foil_wire([(le_x(r) + c * s, r, c * h) for s, h in naca(0.08, 32)]))
    body = Part.makeLoft(secs, True, True)
    cut = Part.makeBox(200, 40, 60, V(960.0, 110.2, -30.0))
    cut.rotate(V(960.0, 110.2, 0.0), V(0, 0, 1), math.degrees(math.atan2(105.2 - 110.2, 1010.0 - 960.0)))
    return body.cut(cut)


# ---------- hull details
def joint_ring(x0, screws=8):
    ring = revolve(polyline([(x0 - 4, 87.6), (x0 - 4, 90.5), (x0 - 3.5, 91.0), (x0 + 3.5, 91.0), (x0 + 4, 90.5),
                             (x0 + 4, 87.6), (x0 - 4, 87.6)]))
    head = Part.makeCylinder(1.9, 0.9, V(x0, 0, 90.9), V(0, 0, 1))
    sock = Part.makeCylinder(0.8, 0.6, V(x0, 0, 91.3), V(0, 0, 1))
    head = head.cut(sock)
    return Part.makeCompound([ring] + [rotx(head, 22.5 + k * 360.0 / screws) for k in range(screws)])


def tail_cap():
    """End plate on the tail cone's flat end face (X 1150): 1.5 mm proud, chamfered, six cap screws on r 24."""
    cap = revolve(polyline([(1149.0, 0.0), (1149.0, 30.0), (1150.6, 30.0), (1151.5, 29.1), (1151.5, 0.0), (1149.0, 0.0)]))
    head = Part.makeCylinder(1.6, 0.7, V(1151.4, 0, 24.0), V(1, 0, 0))
    head = head.cut(Part.makeCylinder(0.7, 0.5, V(1151.7, 0, 24.0), V(1, 0, 0)))
    return Part.makeCompound([cap] + [rotx(head, 30 + k * 60) for k in range(6)])


# ---------- build
parts = {}                                             # GLB node name -> (shape, (linear mm, angular rad) deflection, group)
m, p, d, s = motor(), propeller(), duct(), strut()
for k, (cy, cz) in THRUSTERS.items():
    a = math.degrees(math.atan2(-cy, cz))              # rotate local +Z (strut radial) onto the thruster's radial line
    grp = f"REAR_PROPULSION/THRUSTER_{k}"
    parts[f"THRUSTER_{k}_MOTOR"] = (moved(m, cy, cz), (0.05, 0.18), grp)
    parts[f"THRUSTER_{k}_PROPELLER"] = (moved(p, cy, cz), (0.06, 0.3), grp)
    parts[f"THRUSTER_{k}_DUCT"] = (moved(d, cy, cz), (0.05, 0.18), grp)
    parts[f"THRUSTER_{k}_STRUT"] = (rotx(s, a), (0.05, 0.25), grp)
f = fin()
for k, ang in FIN_ANGLE.items():
    parts[f"STABILISER_FIN_{k}"] = (rotx(f, ang), (0.05, 0.25), "REAR_PROPULSION")
parts["NOSE_JOINT_RING"] = (joint_ring(200.0), (0.05, 0.1), "NOSE_SECTION")
parts["TAIL_JOINT_RING"] = (joint_ring(900.0), (0.05, 0.1), "REAR_PROPULSION")
parts["TAIL_CAP"] = (tail_cap(), (0.05, 0.1), "REAR_PROPULSION")

doc = App.newDocument("SIH26058_AUV_PLATFORM_DETAIL_r04")
groups = {}
meta = {}
for name, (shape, tol, grp) in parts.items():
    assert shape.isValid(), name
    g = None
    for i, gname in enumerate(grp.split("/")):
        key = "/".join(grp.split("/")[: i + 1])
        if key not in groups:
            groups[key] = doc.addObject("App::DocumentObjectGroup", gname)
            if g is not None:
                g.addObject(groups[key])
        g = groups[key]
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.Label = name
    g.addObject(obj)
    P, T, off = [], [], 0
    for face in shape.Faces:                           # one vertex set per CAD face: smooth inside, sharp between faces
        msh = MeshPart.meshFromShape(Shape=face, LinearDeflection=tol[0], AngularDeflection=tol[1], Relative=False)
        v, t = msh.Topology
        if not t:
            continue
        P += [(q.x, q.y, q.z) for q in v]
        T += [(a + off, b + off, c + off) for a, b, c in t]
        off += len(v)
    P = np.array(P, dtype=np.float64)
    bb = shape.optimalBoundingBox()
    tb = (P.min(0), P.max(0))
    assert np.allclose(tb[0], (bb.XMin, bb.YMin, bb.ZMin), atol=0.5) and np.allclose(tb[1], (bb.XMax, bb.YMax, bb.ZMax), atol=0.5), (name, tb, bb)
    np.savez(os.path.join(OUT, "tess", name + ".npz"), pos=(P / 1000.0).astype(np.float32), idx=np.array(T, dtype=np.uint32))
    meta[name] = {"group": grp, "verts": len(P), "tris": len(T), "volume_mm3": round(shape.Volume, 1),
                  "bbox_mm": [round(bb.XMin, 2), round(bb.YMin, 2), round(bb.ZMin, 2), round(bb.XMax, 2), round(bb.YMax, 2), round(bb.ZMax, 2)]}
doc.recompute()
doc.saveAs(os.path.join(OUT, "SIH26058_AUV_PLATFORM_DETAIL_r04.FCStd"))
json.dump(meta, open(os.path.join(OUT, "tess", "meta.json"), "w"), indent=1)
for n, mt in meta.items():
    print(n, mt["verts"], mt["tris"], mt["bbox_mm"])
print("saved", len(meta), "parts")
