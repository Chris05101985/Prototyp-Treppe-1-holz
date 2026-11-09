import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

# ---------------- Parameter (alles in mm) ----------------
N = 15                 # Anzahl Stufen
RISE = 180.0           # Steigung pro Stufe
PITCH = 360.0 / N      # Drehwinkel pro Stufe (Grad)
SPAN = PITCH - 3.0     # Keilwinkel einer Stufe (Grad)
OUTER_R = 950.0        # Außenradius der Stufen
COL_R = 100.0          # Radius der Mittelsäule
TREAD_T = 45.0         # Stufendicke
RAIL_R = 880.0         # Handlauf-Radius
RAIL_H = 900.0         # Handlaufhöhe über Trittfläche
RAIL_D = 50.0          # Handlauf-Durchmesser
BAL_R = 6.0            # Baluster-Radius (Stahl Ø12)
R_WALK = 600.0         # Lauflinie (für Bemaßung)
H = N * RISE           # Geschoßhöhe
COL_H = H + 200.0      # Säulenhöhe

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# Farben (RGBA, 0-1)
C_TREAD = (0.36, 0.23, 0.13, 1)   # Nussbaum
C_OAK = (0.60, 0.44, 0.27, 1)     # Eiche
C_RAIL = (0.30, 0.19, 0.11, 1)    # Nussbaum dunkel
C_STEEL = (0.23, 0.24, 0.27, 1)   # Stahl
C_LED = (1.00, 0.72, 0.25, 1)     # LED warm


def sector_poly(r_in, r_out, a0, a1, n=28):
    a_out = np.linspace(a0, a1, n)
    a_in = np.linspace(a1, a0, n)
    pts = [(r_out * math.cos(a), r_out * math.sin(a)) for a in a_out]
    pts += [(r_in * math.cos(a), r_in * math.sin(a)) for a in a_in]
    return Polygon(pts)


def wedge(r_in, r_out, a0, a1, z, h):
    m = trimesh.creation.extrude_polygon(sector_poly(r_in, r_out, a0, a1), h)
    m.apply_translation([0, 0, z])
    return m


def seg(p0, p1, r, sections=12):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    length = np.linalg.norm(d)
    if length == 0:
        return None, 0.0
    m = trimesh.creation.cylinder(radius=r, height=length, sections=sections)
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d / length))
    m.apply_translation((p0 + p1) / 2)
    return m, length


def P(r, a_deg, z):
    return [r * math.cos(math.radians(a_deg)), r * math.sin(math.radians(a_deg)), z]


def walk_z(a_deg):
    """Höhe der Trittfläche entlang der Wendel (linear in Winkel)."""
    return a_deg * RISE / PITCH + TREAD_T


# ---------------- Geometrie aufbauen ----------------
parts = []  # (name, mesh, farbe, kante_zeichnen)

col = trimesh.creation.cylinder(radius=COL_R, height=COL_H, sections=64)
col.apply_translation([0, 0, COL_H / 2])
parts.append(("saeule_eiche", col, C_OAK, True))

base = trimesh.creation.cylinder(radius=200, height=20, sections=48)
base.apply_translation([0, 0, -10])
parts.append(("fussplatte", base, C_STEEL, False))

top = trimesh.creation.cylinder(radius=150, height=15, sections=48)
top.apply_translation([0, 0, COL_H + 7.5])
parts.append(("kopfplatte", top, C_STEEL, False))

rail_segs = []
rail_len = 0.0
th = np.linspace(-20.0, 380.0, 220)
for a, b in zip(th[:-1], th[1:]):
    s, l = seg(P(RAIL_R, a, walk_z(a) + RAIL_H),
               P(RAIL_R, b, walk_z(b) + RAIL_H), RAIL_D / 2, sections=10)
    if s is not None:
        rail_segs.append(s)
        rail_len += l
rail = trimesh.util.concatenate(rail_segs)
parts.append(("handlauf", rail, C_RAIL, True))

for i in range(N):
    a0 = i * PITCH
    a1 = a0 + SPAN
    z = i * RISE
    ac = (a0 + a1) / 2
    parts.append((f"stufe_{i+1:02d}",
                  wedge(COL_R + 8, OUTER_R, math.radians(a0), math.radians(a1), z, TREAD_T),
                  C_TREAD, True))
    span_rad = math.radians(SPAN - 1.6)
    r_mid = OUTER_R - 85
    chord = 2 * r_mid * math.sin(span_rad / 2) * 0.95
    led = trimesh.creation.box(extents=[chord, 150, 12])
    led.apply_transform(trimesh.transformations.rotation_matrix(math.radians(ac) + math.pi / 2, [0, 0, 1]))
    led.apply_translation(P(r_mid, ac, z - 6))
    parts.append((f"led_{i+1:02d}", led, C_LED, False))
    conn, _ = seg(P(COL_R - 5, ac, z + TREAD_T / 2), P(COL_R + 85, ac, z + TREAD_T / 2), 26)
    parts.append((f"verbinder_{i+1:02d}", conn, C_STEEL, False))
    bal, _ = seg(P(RAIL_R, ac, z + TREAD_T), P(RAIL_R, ac, walk_z(ac) + RAIL_H), BAL_R, sections=10)
    parts.append((f"baluster_{i+1:02d}", bal, C_STEEL, False))

meshes = []
for name, m, color, edges in parts:
    m.visual.face_colors = color
    meshes.append((name, m, color, edges))

# ---------------- Export 3D ----------------
scene = trimesh.Scene()
for name, m, color, edges in meshes:
    scene.add_geometry(m, geom_name=name)
scene.export(os.path.join(OUT, "treppe.glb"))

allm = trimesh.util.concatenate([m for _, m, _, _ in meshes])
allm.export(os.path.join(OUT, "treppe.stl"))

# ---------------- Renderings ----------------
LIGHT = np.array([-0.45, -0.55, 0.75])
LIGHT /= np.linalg.norm(LIGHT)


def draw(path, elev, azim, zoom=None):
    tris, fcs, ecs = [], [], []
    for name, m, color, edges in meshes:
        tri = m.vertices[m.faces]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1)
        ln[ln == 0] = 1
        n /= ln[:, None]
        b = 0.55 + 0.45 * np.abs(n @ LIGHT)
        base = np.array(color[:3])
        fc = np.clip(base[None, :] * b[:, None], 0, 1)
        tris.append(tri)
        fcs.append(fc)
        if edges:
            ecs.append(np.column_stack([np.tile(base * 0.55, (len(tri), 1)),
                                        np.full(len(tri), 0.4)]))
        else:
            ecs.append(np.zeros((len(tri), 4)))
    tris = np.vstack(tris)
    fcs = np.vstack(fcs)
    ecs = np.vstack(ecs)
    fig = plt.figure(figsize=(12, 9), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.view_init(elev=elev, azim=azim)
    pc = Poly3DCollection(tris, facecolors=fcs, edgecolors=ecs,
                          linewidths=0.3, shade=False)
    ax.add_collection3d(pc)
    if zoom:
        (x0, x1), (y0, y1), (z0, z1) = zoom
    else:
        mn, mx = allm.vertices.min(0), allm.vertices.max(0)
        c = (mn + mx) / 2
        r = (mx - mn).max() / 2 * 1.05
        x0, x1 = c[0] - r, c[0] + r
        y0, y1 = c[1] - r, c[1] + r
        z0, z1 = mn[2] - 20, mx[2] + 20
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_zlim(z0, z1)
    ax.set_box_aspect((x1 - x0, y1 - y0, z1 - z0))
    ax.set_axis_off()
    fig.patch.set_facecolor("#f6f3ee")
    ax.set_facecolor("#f6f3ee")
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


draw(os.path.join(OUT, "ansicht_perspektive.png"), 22, -58)
draw(os.path.join(OUT, "ansicht_front.png"), 6, -90)
draw(os.path.join(OUT, "ansicht_oben.png"), 89, -90)
draw(os.path.join(OUT, "detail_stufen.png"), 24, -120,
     zoom=((-1050, -150), (0, 950), (750, 2400)))
draw(os.path.join(OUT, "ansicht_led_unten.png"), -32, -58)
draw(os.path.join(OUT, "detail_led.png"), -35, -100,
     zoom=((-1050, -650), (-250, 350), (1050, 1500)))

# ---------------- Zeichnungen (SVG) ----------------
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect("equal")
ax.axis("off")
for r, style, lw in [(OUTER_R, "--", 1), (RAIL_R, ":", 1), (COL_R, "-", 1.2), (200, "-", 1)]:
    ax.add_patch(plt.Circle((0, 0), r, fill=False, ls=style, color="gray", lw=lw))
for i in range(N):
    poly = sector_poly(COL_R + 8, OUTER_R, math.radians(i * PITCH),
                       math.radians(i * PITCH + SPAN))
    x, y = poly.exterior.xy
    ax.fill(x, y, color=C_TREAD[:3], alpha=0.9, ec="black", lw=0.4)
    ac = math.radians(i * PITCH + PITCH / 2)
    ax.plot(RAIL_R * math.cos(ac), RAIL_R * math.sin(ac), "o", ms=3, color="black")
ax.annotate("", xy=(OUTER_R, 0), xytext=(-OUTER_R, 0),
            arrowprops=dict(arrowstyle="<->", color="black"))
ax.text(0, 40, "Ø 1900", ha="center", fontsize=11)
ax.annotate("", xy=(COL_R * 0.7071, COL_R * 0.7071), xytext=(-COL_R * 0.7071, -COL_R * 0.7071),
            arrowprops=dict(arrowstyle="<->", color="black"))
ax.text(0, -COL_R - 60, "Ø 200 Säule", ha="center", fontsize=10)
ax.set_xlim(-1150, 1150)
ax.set_ylim(-1150, 1150)
ax.set_title("Grundriss – Wendeltreppe Nussbaum/Eiche, 15 Stufen, Ø 1900 mm")
fig.savefig(os.path.join(OUT, "grundriss.svg"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "grundriss.png"), bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(14, 7))
th = np.linspace(0, 360, 400)
s = R_WALK * np.radians(th)
ax.plot(s, walk_z(th) + RAIL_H, color=C_RAIL[:3], lw=3, label="Handlauf (900 über Tritt)")
ax.plot(s, walk_z(th) + 2100, "--", color="gray", lw=1, label="Kopfhöhe 2100")
for i in range(N):
    a0, a1 = i * PITCH, i * PITCH + SPAN
    z = i * RISE
    s0, s1 = R_WALK * math.radians(a0), R_WALK * math.radians(a1)
    ax.fill([s0, s1, s1, s0], [z, z, z + TREAD_T, z + TREAD_T],
            color=C_TREAD[:3], ec="black", lw=0.4)
ax.axhline(0, color="black", lw=1.5)
ax.axhline(H, color="black", lw=1.5)
ax.text(20, -120, "EG", fontsize=10)
ax.text(20, H + 60, "OG (2700)", fontsize=10)
going = R_WALK * math.radians(PITCH)
ax.annotate(f"Auftritt Lauflinie: {going:.0f} mm / Steigung: {RISE:.0f} mm",
            xy=(0.5, 0.05), xycoords="axes fraction", ha="center", fontsize=11)
ax.set_xlabel("Bogenlänge an der Lauflinie (r = 600 mm)")
ax.set_ylabel("Höhe (mm)")
ax.set_title("Abwicklung der Lauflinie")
ax.legend(loc="upper left")
ax.set_xlim(-60, R_WALK * math.radians(370))
fig.savefig(os.path.join(OUT, "lauflinie.svg"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "lauflinie.png"), bbox_inches="tight")
plt.close(fig)

# ---------------- Teileliste ----------------
led_arc = (OUTER_R - 90) * math.radians(SPAN - 1.6)
rows = [
    ["Bauteil", "Anzahl", "Material", "Abmessungen (mm)"],
    ["Mittelsäule", 1, "Eiche massiv", f"Ø {2*COL_R:.0f} x {COL_H:.0f} hoch"],
    ["Fußplatte", 1, "Stahl", "Ø 400 x 20"],
    ["Kopfplatte", 1, "Stahl", "Ø 300 x 15"],
    ["Keilstufe", N, "Nussbaum massiv", f"Keil R {COL_R+8:.0f}-{OUTER_R:.0f}, Winkel {SPAN:.0f}°, 45 dick"],
    ["Handlauf (Helix)", 1, "Nussbaum rund", f"Ø {RAIL_D:.0f}, R {RAIL_R:.0f}, Länge ca. {rail_len:.0f}"],
    ["Baluster", N, "Stahl rund", f"Ø {2*BAL_R:.0f} x {RAIL_H:.0f}"],
    ["LED-Band unter Stufe", N, "LED 2700K", f"Bogen ca. {led_arc:.0f} x 20 breit, in Nut gefräst"],
    ["Stufenverbinder", N, "Stahl", "Ø 52 x 90, in Säule eingelassen"],
]
with open(os.path.join(OUT, "teileliste.csv"), "w", newline="") as f:
    csv.writer(f).writerows(rows)

# ---------------- README ----------------
readme = f"""# Prototyp: Wendeltreppe "Walnut Spiral"

Freitragende Wendeltreppe aus Massivholz: Mittelsäule aus Eiche (Ø 200 mm),
15 Keilstufen aus Nussbaum (45 mm), geschwungener Handlauf als Helix (R 880 mm,
900 mm über Trittfläche), Stahl-Baluster und verdecktes LED-Band unter jeder
Stufe (schwebender Lichteffekt).

## Kennwerte
- Geschoßhöhe: {H:.0f} mm ({N} Stufen x {RISE:.0f} mm Steigung)
- Durchmesser: {2*OUTER_R:.0f} mm, Auftritt an der Lauflinie (r={R_WALK:.0f}): {going:.0f} mm
- Drehung: 360° über die gesamte Treppe ({PITCH:.1f}° pro Stufe)
- Handlauflänge: ca. {rail_len:.0f} mm

## Dateien in out/
- treppe.stl / treppe.glb – 3D-Modell (STL für 3D-Druck/CAD, GLB mit Farben)
- ansicht_perspektive.png, ansicht_front.png, ansicht_oben.png, detail_stufen.png,
  ansicht_led_unten.png, detail_led.png – Renderings
- grundriss.svg – Grundriss mit Bemaßung
- lauflinie.svg – Abwicklung der Lauflinie (Steigung/Kopfhöhe)
- teileliste.csv – Stückliste für den Prototypenbau

## Anpassen
Alle Maße stehen oben in treppe.py als Parameter (N, RISE, OUTER_R, ...).
Dann neu ausführen:

    pip install numpy matplotlib trimesh shapely mapbox-earcut
    python3 treppe.py
"""
with open(os.path.join(OUT, "README.md"), "w") as f:
    f.write(readme)

print(f"Fertig. {len(meshes)} Bauteile, {len(allm.faces)} Faces, "
      f"Handlauf {rail_len:.0f} mm, Bounding Box {allm.extents.round(0)}")
for fn in sorted(os.listdir(OUT)):
    print(" -", fn)
