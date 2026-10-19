# Cheap low-poly models for the room planner's slots and add-ons.
# exec'd by restyle_export.py, so it shares that script's helpers (box, cyl, rod,
# sphere, empty, light_anchor, curtain, use_option, slot_base, hide_with) and M.
# Coordinates: metres, origin at the inner south-west corner, x east, y north.
# Numbers in comments refer to the 100-idea list.

import random

random.seed(4)


def mat(name, color, **kw):
    m = bpy.data.materials.get(name)
    if m is None:
        m = material(name, color, **kw)
        m.use_backface_culling = False
    return m


def torus(name, loc, R, r, m, rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, major_segments=32, minor_segments=6)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = rot
    o.scale = scale
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return _adopt(o)


BOOKS = [M["book1"], M["book2"], M["book3"], M["book4"]]


def books_y(prefix, x0, x1, y0, y1, z, hmin=0.17, hmax=0.25):
    """Books standing on a shelf, spines toward +x, filling y0..y1."""
    y, k = y0, 0
    while y < y1 - 0.02:
        w = random.uniform(0.02, 0.04)
        h = random.uniform(hmin, hmax)
        box(f"{prefix} Book {k}", x0, x1 - random.uniform(0, 0.03), y, min(y + w, y1), z, z + h, random.choice(BOOKS))
        y += w + 0.002
        k += 1


def books_y_east(prefix, x0, x1, y0, y1, z, hmin=0.17, hmax=0.25):
    """Same for shelves on the east wall (spines toward -x)."""
    y, k = y0, 0
    while y < y1 - 0.02:
        w = random.uniform(0.02, 0.04)
        h = random.uniform(hmin, hmax)
        box(f"{prefix} Book {k}", x0 + random.uniform(0, 0.03), x1, y, min(y + w, y1), z, z + h, random.choice(BOOKS))
        y += w + 0.002
        k += 1


def potted(prefix, x, y, z, r, m_pot, leaves=6, spread=None, leaf_r=0.05):
    cyl(f"{prefix} Pot", x, y, z, z + r * 1.6, r, m_pot, r2=r * 0.8)
    spread = spread or r * 1.2
    for k in range(leaves):
        a = k * 2.4
        sphere(f"{prefix} Leaf {k}", (x + spread * math.cos(a) * 0.6, y + spread * math.sin(a) * 0.6, z + r * 1.6 + 0.04 + 0.03 * (k % 3)),
               leaf_r, M["leaf"], scale=(1, 0.6, 0.35), rot=(0.5, 0.2, a))


paper = mat("Paper Lantern", "#f4ecdc", rough=0.9, emit="#ffd6a0", emit_strength=2.5)
paper_rib = mat("Lantern Rib", "#d8ccb4", rough=0.9)
rattan = mat("Rattan", "#b98c55", rough=0.8)
ph_white = mat("PH White", "#f2f0ea", rough=0.25)
bulb = bpy.data.materials["Bulb"]
diffuser = bpy.data.materials["Plafon Diffuser"]
jute = mat("Jute", "#b89a6a", rough=1.0)
jute_dark = mat("Jute Dark", "#8d7148", rough=1.0)
madder = mat("Kilim Madder", "#8e3b2c", rough=1.0)
navy = mat("Kilim Navy", "#283548", rough=1.0)
ochre = mat("Kilim Ochre", "#c8902f", rough=1.0)
ivory = mat("Kilim Ivory", "#e8dcc4", rough=1.0)
cork = mat("Cork", "#b88a5a", rough=0.95)
cane = mat("Cane", "#d9c08a", rough=0.8)
bentwood = mat("Bentwood", "#2e2016", rough=0.5)
felt_grey = mat("Felt Grey", "#5b6670", rough=1.0)
felt_green = mat("Felt Green", "#4f6b5a", rough=1.0)
felt_rust = mat("Felt Rust", "#9a4a2c", rough=1.0)
sage = mat("Wardrobe Sage", "#5f8f78", rough=0.75)
shoji_paper = mat("Shoji Paper", "#f3eee2", rough=0.9)
white_lacq = mat("Shelf Alu White", "#e8e6e1", rough=0.4)
cognac = mat("Cognac Leather", "#7a4424", rough=0.5)
sheep = mat("Sheepskin", "#efe9de", rough=1.0)
lounge = mat("Lounge Fabric", "#cdbfa7", rough=1.0)
veneer = mat("PRL Veneer", "#7a4a2a", rough=0.25)
porcelain = mat("Porcelain", "#f6f4ef", rough=0.15)
marble = mat("Marble", "#e7e3dc", rough=0.2)
birch = mat("Birch Pegboard", "#d8c19a", rough=0.7)
blind = mat("Blind Fabric", "#2a2a2a", rough=0.9)
blackout = mat("Blackout Curtain", "#3a3633", rough=0.95)
film = mat("Window Film", "#e9eef0", rough=0.6)
screen_white = mat("Projector Screen", "#f2f2f2", rough=0.9)
glow = mat("Bias Glow", "#ffcf9a", emit="#ffbf80", emit_strength=4.0)
grow = mat("Grow Glow", "#e6c8ff", emit="#d9a6ff", emit_strength=4.0)
led = mat("LED Orange", "#2a120a", emit="#ff8a3d", emit_strength=3.0)
eink = mat("E-ink", "#d9d9d2", rough=0.8)
globe_blue = mat("Globe Blue", "#6f8fa6", rough=0.5)
lime_green = mat("Lime Leaf", "#4f7a3a", rough=0.4)
textile_ochre = mat("Textile Ochre", "#c08a3e", rough=1.0)
wall_upper = mat("Wall Upper White", "#ece6da", rough=0.85)
night = mat("Night Glow", "#fff1dc", emit="#ffd8a0", emit_strength=1.0)
map_blue = mat("Map Blue", "#9fb6c4", rough=0.8)
desk_leg_white = bpy.data.materials["Desk Leg White"]
cx, cy = W / 2, D / 2

# ================================================================ ceiling light
use_option("light:lantern")  # 15/16 paper lantern pendant
cyl("Lantern Cord", cx, cy, 2.30, H, 0.004, M["black"], verts=8)
sphere("Lantern Body", (cx, cy, 2.05), 0.30, paper, scale=(1, 1, 0.85))
for k, dz in enumerate((-0.18, -0.09, 0.0, 0.09, 0.18)):
    r = 0.30 * math.sqrt(max(0.0, 1 - (dz / 0.255) ** 2))
    torus(f"Lantern Rib {k}", (cx, cy, 2.05 + dz), r, 0.004, paper_rib)

use_option("light:ph")  # PH5-style layered shades
cyl("PH Cord", cx, cy, 2.44, H, 0.004, M["black"], verts=8)
cyl("PH Top", cx, cy, 2.36, 2.44, 0.15, ph_white, r2=0.05, verts=32)
cyl("PH Mid", cx, cy, 2.26, 2.33, 0.21, ph_white, r2=0.09, verts=32)
cyl("PH Bowl", cx, cy, 2.15, 2.22, 0.10, ph_white, r2=0.23, verts=32)
sphere("PH Bulb", (cx, cy, 2.28), 0.04, bulb)

use_option("light:track")  # 11 ceiling track with three spots
box("Track Rail", cx - 0.02, cx + 0.02, 0.80, 2.70, H - 0.04, H, M["black"])
for k, (y, tgt) in enumerate(((1.0, (0.35, 0.80, DZ)), (1.9, (0.60, 2.20, 1.30)), (2.5, (2.20, 2.45, 0.60)))):
    top = Vector((cx, y, H - 0.10))
    d = (Vector(tgt) - top).normalized()
    rod(f"Track Stem {k}", (cx, y, H - 0.04), top, 0.008, M["black"], verts=8)
    rod(f"Track Spot {k}", top, top + d * 0.14, 0.035, M["black"], verts=16)
    sphere(f"Track Lens {k}", top + d * 0.14, 0.026, bulb)

use_option("light:rattan")  # 16 flush rattan shade on the existing smart bulbs
cyl("Rattan Shade", cx, cy, H - 0.12, H, 0.31, rattan, verts=48, caps=False)
cyl("Rattan Diffuser", cx, cy, H - 0.125, H - 0.12, 0.29, diffuser, verts=48)

# ================================================================ desk lamp
use_option("desklamp:angle")  # 19 Anglepoise-style
ax, ay = 0.10, 0.28
cyl("Lamp Angle Base", ax, ay, DZ, DZ + 0.03, 0.08, M["black"], verts=32)
rod("Lamp Angle Low Arm", (ax, ay, DZ + 0.03), (0.18, 0.40, DZ + 0.38), 0.008, M["black"], verts=8)
rod("Lamp Angle High Arm", (0.18, 0.40, DZ + 0.38), (0.38, 0.42, DZ + 0.48), 0.008, M["black"], verts=8)
rod("Lamp Angle Shade", (0.38, 0.42, DZ + 0.48), (0.44, 0.46, DZ + 0.34), 0.03, M["black"], r2=0.08, verts=24)
light_anchor("Light Desk Angle", (0.44, 0.46, DZ + 0.30), "desk")

# ================================================================ desk tops
def desk_frame(prefix, x0, x1, y0, y1, top_mat, leg_mat, legs_y, bevel=0.012):
    box(f"{prefix} Top", x0, x1, y0, y1, DZ - 0.028, DZ, top_mat, bevel=bevel)
    for k, y in enumerate(legs_y):
        box(f"{prefix} Foot {k}", 0.04, 0.66, y - 0.03, y + 0.03, 0, 0.03, leg_mat, bevel=0.01)
        box(f"{prefix} Leg {k}", 0.32, 0.38, y - 0.03, y + 0.03, 0.03, DZ - 0.07, leg_mat)
        box(f"{prefix} Bracket {k}", 0.06, 0.64, y - 0.025, y + 0.025, DZ - 0.07, DZ - 0.028, leg_mat)
    box(f"{prefix} Crossbar", 0.33, 0.37, legs_y[0], legs_y[-1], DZ - 0.10, DZ - 0.06, leg_mat)


use_option("desk:oak")
desk_frame("Desk Oak", 0.0, 0.70, 0.10, 1.50, M["oak"], desk_leg_white, (0.18, 1.42))
use_option("desk:wide")  # 47 160 cm top, legs set in so the PC still fits
desk_frame("Desk Wide", 0.0, 0.70, 0.02, 1.62, M["walnut"], M["black"], (0.18, 1.42))
use_option("desk:l")  # 48 L-shaped, return along the window wall over the radiator
desk_frame("Desk L", 0.0, 0.70, 0.10, 1.50, M["walnut"], M["black"], (0.18, 1.42))
box("Desk L Return", 0.70, 1.48, 0.10, 0.70, DZ - 0.028, DZ, M["walnut"], bevel=0.012)
box("Desk L Post", 1.38, 1.44, 0.37, 0.43, 0.0, DZ - 0.028, M["black"])
box("Desk L Foot", 1.20, 1.46, 0.37, 0.43, 0.0, 0.03, M["black"])

# ================================================================ PC
use_option("pc:mount")  # 76 tower hung under the desk
box("PC Mount Tower", 0.08, 0.54, 1.22, 1.36, 0.25, 0.70, bpy.data.materials["PC Case"], bevel=0.005)
for k, x in enumerate((0.15, 0.47)):
    box(f"PC Mount Strap {k}", x - 0.015, x + 0.015, 1.20, 1.38, 0.24, 0.715, M["black"])

# ================================================================ desk chairs
use_option("chair:kneel")  # 68 kneeling chair
kc = empty("Kneeling Chair", (1.05, 0.75, 0), rot_z=math.radians(40))
for s, yy in (("L", -0.18), ("R", 0.18)):
    rod(f"Kneel Runner {s}", (0.32, yy, 0.05), (-0.34, yy, 0.03), 0.018, M["oak"], verts=8, parent=kc)
    rod(f"Kneel Seat Post {s}", (0.12, yy, 0.03), (0.06, yy, 0.52), 0.02, M["oak"], verts=8, parent=kc)
    rod(f"Kneel Knee Post {s}", (-0.10, yy, 0.03), (-0.24, yy, 0.30), 0.02, M["oak"], verts=8, parent=kc)
kseat = empty("Kneel Seat Pivot", (0.06, 0, 0.53), parent=kc)
kseat.rotation_euler = (0, math.radians(-20), 0)
box("Kneel Seat", -0.18, 0.18, -0.21, 0.21, 0.0, 0.06, felt_grey, bevel=0.02, parent=kseat)
kknee = empty("Kneel Knee Pivot", (-0.26, 0, 0.31), parent=kc)
kknee.rotation_euler = (0, math.radians(-40), 0)
box("Kneel Knee Pad", -0.10, 0.10, -0.21, 0.21, 0.0, 0.05, felt_grey, bevel=0.02, parent=kknee)

use_option("chair:cantilever")  # Thonet S64-style
cc = empty("Cantilever Chair", (1.05, 0.75, 0), rot_z=math.radians(40))
for s, yy in (("L", -0.22), ("R", 0.22)):
    pts = [(0.22, yy, 0.012), (-0.28, yy, 0.012), (-0.27, yy, 0.44), (0.20, yy, 0.46), (0.26, yy, 0.86)]
    for k in range(len(pts) - 1):
        rod(f"Cantilever Tube {s}{k}", pts[k], pts[k + 1], 0.012, M["alu"], verts=10, parent=cc)
rod("Cantilever Floor Bar", (0.22, -0.22, 0.012), (0.22, 0.22, 0.012), 0.012, M["alu"], verts=10, parent=cc)
box("Cantilever Seat Frame", -0.26, 0.20, -0.21, 0.21, 0.44, 0.47, M["oak"], bevel=0.01, parent=cc)
box("Cantilever Seat Cane", -0.23, 0.17, -0.18, 0.18, 0.471, 0.474, cane, parent=cc)
cb = empty("Cantilever Back Pivot", (0.23, 0, 0.60), parent=cc)
cb.rotation_euler = (0, math.radians(14), 0)
box("Cantilever Back Frame", -0.012, 0.012, -0.21, 0.21, 0.0, 0.26, M["oak"], bevel=0.008, parent=cb)
box("Cantilever Back Cane", -0.016, -0.012, -0.18, 0.18, 0.03, 0.23, cane, parent=cb)

# ================================================================ wardrobe
WD = 0.597
wy_a, wy_b = D - 1.67, D - 0.56
WH = H - 0.003
wmid = (wy_a + wy_b) / 2
use_option("wardrobe:sage")  # 3 painted to match the wall
box("Wardrobe Sage Carcass", 0, WD - 0.02, wy_a, wy_b, 0, WH, sage)
box("Wardrobe Sage Door S", WD - 0.02, WD, wy_a, wmid - 0.0015, 0.005, WH, sage, bevel=0.002)
box("Wardrobe Sage Door N", WD - 0.02, WD, wmid + 0.0015, wy_b, 0.005, WH, sage, bevel=0.002)
box("Wardrobe Sage Handle", WD, WD + 0.012, wmid + 0.012, wmid + 0.022, 0.02, 1.05, M["brass"])

use_option("wardrobe:bookcase")  # 52 open floor-to-ceiling bookcase
BD = 0.40
box("Wardrobe Books Side S", 0, BD, wy_a, wy_a + 0.022, 0, WH, M["oak"])
box("Wardrobe Books Side N", 0, BD, wy_b - 0.022, wy_b, 0, WH, M["oak"])
box("Wardrobe Books Mid", 0, BD, wmid - 0.011, wmid + 0.011, 0, WH, M["oak"])
for j, z in enumerate((0.05, 0.42, 0.80, 1.18, 1.56, 1.94, 2.32, WH - 0.025)):
    box(f"Wardrobe Books Shelf {j}", 0, BD, wy_a, wy_b, z, z + 0.025, M["oak"])
    if j < 7:
        for half, (a, b_) in enumerate(((wy_a + 0.03, wmid - 0.02), (wmid + 0.02, wy_b - 0.03))):
            if (j + half) % 3 == 2:
                potted(f"Wardrobe Books Pot {j}{half}", BD * 0.5, (a + b_) / 2, z + 0.025, 0.06, M["terracotta"])
            else:
                books_y(f"Wardrobe Books {j}{half}", 0.03, BD - 0.03, a, b_ if (j + half) % 2 else (a + b_) / 2 + 0.05, z + 0.025)

use_option("wardrobe:shoji")  # 100 shoji-style sliding fronts
box("Wardrobe Shoji Carcass", 0, WD - 0.03, wy_a, wy_b, 0, WH, M["oak"])
for p, (a, b_, x) in enumerate(((wy_a, wmid + 0.03, WD - 0.03), (wmid - 0.03, wy_b, WD - 0.012))):
    box(f"Wardrobe Shoji Paper {p}", x, x + 0.004, a + 0.02, b_ - 0.02, 0.04, WH - 0.04, shoji_paper)
    for k in range(4):
        yy = a + (b_ - a) * k / 3
        box(f"Wardrobe Shoji Stile {p}{k}", x + 0.004, x + 0.018, yy - 0.01, yy + 0.01, 0.0, WH, M["oak"])
    for k in range(9):
        z = 0.02 + k * (WH - 0.04) / 8
        box(f"Wardrobe Shoji Rail {p}{k}", x + 0.004, x + 0.016, a, b_, z - 0.008, z + 0.008, M["oak"])

# ================================================================ window
use_option("window:venetian")  # 21 wooden Venetian blind, half down, slats open
box("Venetian Headrail", 0.08, 1.50, -0.02, 0.03, 2.33, 2.38, M["oak"])
for k in range(20):
    z = 2.30 - k * 0.04
    s_ = box(f"Venetian Slat {k}", -0.71, 0.71, -0.025, 0.025, -0.002, 0.002, M["oak"])
    s_.location = (0.79, 0.005, z)
    s_.rotation_euler = (math.radians(35), 0, 0)
box("Venetian Bottom", 0.08, 1.50, -0.02, 0.03, 1.47, 1.50, M["oak"])

use_option("window:cafe")  # 22 café curtain on the lower half
rod("Cafe Rod", (0.05, 0.03, 1.56), (1.53, 0.03, 1.56), 0.008, M["brass"], verts=8)
curtain("Cafe Curtain", 0.07, 1.51, 0.03, 0.87, 1.55, 12, 0.014, M["curtain"])

use_option("window:motor")  # 75 motorised roller blind, half down
box("Motor Blind Fabric", 0.04, 1.54, 0.045, 0.05, 1.55, 2.44, blind)
box("Motor Blind Bar", 0.04, 1.54, 0.04, 0.055, 1.53, 1.56, M["alu"])

use_option("window:blackout")  # 99 blackout curtains on the ceiling track
box("Blackout Track", 0.72, 2.0, 0.34, 0.38, H - 0.03, H, M["black"])
curtain("Blackout Left", 0.72, 1.04, 0.36, 0.02, H - 0.03, 5, 0.035, blackout)
curtain("Blackout Right", 1.52, 1.96, 0.36, 0.02, H - 0.03, 7, 0.035, blackout)

# ================================================================ rugs
use_option("rug:jute")  # 31 round jute rug under the reading corner
for k, (r, m) in enumerate(((0.65, jute), (0.52, jute_dark), (0.50, jute), (0.28, jute_dark), (0.26, jute))):
    cyl(f"Jute Ring {k}", 2.05, 2.45, 0.0, 0.006 + k * 0.001, r, m, verts=48)

use_option("rug:kilim")  # 38 kilim
kx0, kx1, ky0, ky1 = 0.80, 2.20, 0.55, 2.55
box("Kilim Base", kx0, kx1, ky0, ky1, 0, 0.007, madder)
for nm, a in (("S", (kx0, kx1, ky0, ky0 + 0.10)), ("N", (kx0, kx1, ky1 - 0.10, ky1)),
              ("W", (kx0, kx0 + 0.10, ky0, ky1)), ("E", (kx1 - 0.10, kx1, ky0, ky1))):
    box(f"Kilim Border {nm}", *a, 0.007, 0.009, navy)
for k, y in enumerate((0.95, 1.35, 1.75, 2.15)):
    d_ = box(f"Kilim Diamond {k}", -0.16, 0.16, -0.16, 0.16, 0.007, 0.010, ochre if k % 2 else ivory)
    d_.location = ((kx0 + kx1) / 2, y, 0)
    d_.rotation_euler = (0, 0, math.radians(45))
    d2 = box(f"Kilim Dot {k}", -0.06, 0.06, -0.06, 0.06, 0.010, 0.012, navy)
    d2.location = ((kx0 + kx1) / 2, y, 0)
    d2.rotation_euler = (0, 0, math.radians(45))
for k, x in enumerate((kx0 + 0.22, kx1 - 0.22)):
    box(f"Kilim Stripe {k}", x - 0.02, x + 0.02, ky0 + 0.15, ky1 - 0.15, 0.007, 0.009, ivory)

# ================================================================ art
use_option("art:film")  # 84 vintage Polish film posters
item("above desk")
deep = mat("Film Blue", "#23395b", rough=0.8)
box("Poster A Film Frame", 0.0, 0.022, 1.00, 1.40, 1.22, 1.96, M["black"])
box("Poster A Film Paper", 0.022, 0.024, 1.02, 1.38, 1.24, 1.94, deep)
rod("Poster A Film Head", (0.024, 1.20, 1.70), (0.027, 1.20, 1.70), 0.08, M["p_red"], verts=32)
box("Poster A Film Body", 0.024, 0.027, 1.14, 1.26, 1.36, 1.62, M["p_red"])
box("Poster A Film Title", 0.024, 0.027, 1.05, 1.35, 1.27, 1.31, M["p_cream"])
sx = 0.52
item("on shaft")
box("Poster B Film Frame", sx, sx + 0.022, D - 0.46, D - 0.08, 1.12, 1.92, M["black"])
box("Poster B Film Paper", sx + 0.022, sx + 0.024, D - 0.44, D - 0.10, 1.14, 1.90, M["p_black"])
rod("Poster B Film Eye", (sx + 0.024, D - 0.27, 1.60), (sx + 0.027, D - 0.27, 1.60), 0.11, M["p_mustard"], verts=32)
rod("Poster B Film Pupil", (sx + 0.027, D - 0.27, 1.60), (sx + 0.029, D - 0.27, 1.60), 0.04, M["p_black"], verts=24)
box("Poster B Film Title", sx + 0.024, sx + 0.027, D - 0.41, D - 0.13, 1.20, 1.25, M["p_mustard"])

use_option("art:gallery")  # 81/85 gallery wall on the white door wall, map included
for k, (x0, x1, z0, z1, fm, pm) in enumerate((
        (1.72, 2.02, 1.55, 1.95, M["black"], M["p_cream"]), (2.06, 2.30, 1.70, 1.95, M["oak"], M["p_teal"]),
        (2.34, 2.60, 1.55, 1.95, M["brass"], M["p_mustard"]), (1.72, 1.96, 1.20, 1.50, M["oak"], map_blue),
        (2.00, 2.30, 1.20, 1.65, M["black"], M["book3"]), (2.34, 2.60, 1.25, 1.50, M["walnut"], M["p_red"]))):
    box(f"Gallery Frame {k}", x0, x1, D - 0.022, D, z0, z1, fm)
    box(f"Gallery Paper {k}", x0 + 0.03, x1 - 0.03, D - 0.025, D - 0.022, z0 + 0.03, z1 - 0.03, pm)
rod("Gallery Dot", (1.87, D - 0.025, 1.76), (1.87, D - 0.028, 1.76), 0.07, M["p_red"], verts=24)
for k in range(4):
    box(f"Gallery Map Line {k}", 1.76 + k * 0.04, 1.765 + k * 0.04, D - 0.027, D - 0.025, 1.24, 1.46, M["p_cream"])

use_option("art:clock")  # 82 sunburst clock on the shaft
ccx, ccy, ccz = 0.52, D - 0.27, 1.55
rod("Sunburst Hub", (ccx, ccy, ccz), (ccx + 0.04, ccy, ccz), 0.07, M["walnut"], verts=32)
for k in range(16):
    a = k * 2 * math.pi / 16
    L = 0.24 if k % 2 else 0.18
    end = (ccx + 0.02, ccy + L * math.cos(a), ccz + L * math.sin(a))
    rod(f"Sunburst Ray {k}", (ccx + 0.02, ccy, ccz), end, 0.005, M["brass"], verts=6)
    sphere(f"Sunburst Tip {k}", end, 0.012, M["brass"])

use_option("art:textile")  # 39/90 woven wall hanging above the corner
rod("Textile Dowel", (W - 0.03, 2.08, 2.07), (W - 0.03, 2.92, 2.07), 0.012, M["oak"], verts=10)
box("Textile Panel", W - 0.014, W - 0.006, 2.12, 2.88, 1.15, 2.05, textile_ochre)
for k, (z0, z1, m) in enumerate(((1.25, 1.38, M["rug_rust"]), (1.48, 1.52, M["rug_cream"]), (1.62, 1.80, M["book2"]), (1.88, 1.92, M["rug_cream"]))):
    box(f"Textile Band {k}", W - 0.016, W - 0.014, 2.12, 2.88, z0, z1, m)

use_option("art:mcm")  # mid-century paintings; the viewer paints each canvas from its material name
for key, it, yc, zc, w, h, fr in (
        ("greengrad", "green gradient", 0.45, 1.55, 0.50, 0.70, "walnut"),
        ("mauvegrad", "mauve gradient", 1.05, 1.55, 0.50, 0.70, "walnut"),
        ("duo", "green into mauve", 1.75, 1.55, 0.60, 0.90, "oak"),
        ("arches", "sunset arches", 2.45, 1.55, 0.50, 0.50, "walnut"),
        ("circles", "circles", 3.00, 1.55, 0.40, 0.50, "black"),
        ("leaves", "cut-out leaves", 0.60, 2.15, 0.40, 0.40, "oak"),
        ("hills", "layered hills", 1.30, 2.15, 0.60, 0.40, "walnut"),
        ("sun", "sun and horizon", 2.00, 2.15, 0.40, 0.40, "oak"),
        ("field", "colour field", 2.60, 2.15, 0.40, 0.50, "walnut"),
        ("boomerang", "boomerangs", 3.05, 2.15, 0.30, 0.30, "black")):
    item(it)
    b = 0.025
    box(f"Painting {key} Frame", W - 0.03, W, yc - w / 2 - b, yc + w / 2 + b, zc - h / 2 - b, zc + h / 2 + b, M[fr])
    box(f"Painting {key} Canvas", W - 0.032, W - 0.03, yc - w / 2, yc + w / 2, zc - h / 2, zc + h / 2, mat(f"Painting {key}", "#ffffff", rough=0.9))
item(None)

use_option("piece:wire")  # chrome wire cube shelf (Panton Wire style) with a donut lamp and chrome bits
chrome = mat("Chrome Wire", "#e4e7ea", rough=0.2, metal=0.45)


def join(objs, name):
    """One mesh instead of hundreds of wire rods."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


item("wire shelf")
sx0, sx1, sy0, sy1, cube, wr = 1.95, 2.65, D - 0.36, D - 0.01, 0.35, 0.0022
levels = [k * cube for k in range(4)]
rods = []
for zi in range(3):
    zb, zt = levels[zi] + 0.004, levels[zi + 1] - 0.004
    n = int(round((sy1 - sy0) / 0.025))
    for xs in (sx0, (sx0 + sx1) / 2, sx1):  # side walls of the cubes: vertical wires
        for k in range(n + 1):
            y = sy0 + k * (sy1 - sy0) / n
            rods.append(rod("Wire Side", (xs, y, zb), (xs, y, zt), wr, chrome, verts=5))
    m = int(round((sx1 - sx0) / 0.025))
    for k in range(m + 1):
        x = sx0 + k * (sx1 - sx0) / m
        rods.append(rod("Wire Back", (x, sy1, zb), (x, sy1, zt), wr, chrome, verts=5))
        rods.append(rod("Wire Floor", (x, sy0, zb), (x, sy1, zb), wr, chrome, verts=5))
    for z in (zb, zt):  # the loop round each tier
        rods.append(rod("Wire Rim F", (sx0, sy0, z), (sx1, sy0, z), wr * 1.6, chrome, verts=6))
        rods.append(rod("Wire Rim B", (sx0, sy1, z), (sx1, sy1, z), wr * 1.6, chrome, verts=6))
        for xs in (sx0, (sx0 + sx1) / 2, sx1):
            rods.append(rod("Wire Rim S", (xs, sy0, z), (xs, sy1, z), wr * 1.6, chrome, verts=6))
for k in range(m + 1):  # open wire top, no board
    x = sx0 + k * (sx1 - sx0) / m
    rods.append(rod("Wire Top", (x, sy0, levels[3] - 0.004), (x, sy1, levels[3] - 0.004), wr, chrome, verts=5))
join(rods, "Wire Shelf Frame")

item("donut lamp")
donut = mat("Donut Glass", "#ff7a1a", rough=0.15, emit="#ff6a00", emit_strength=0.9)
lx, ly, lz = 2.40, D - 0.19, cube + 0.004
torus("Donut Lamp Glass", (lx, ly, lz + 0.045), 0.085, 0.05, donut, scale=(1, 1, 0.85))
light_anchor("Light Donut", (lx, ly, lz + 0.07), "donut")

item("u candle holder")
ux, uy, uz = 2.45, D - 0.19, levels[3] - 0.002
cyl("U Holder Foot", ux, uy, uz, uz + 0.01, 0.035, chrome, verts=20)
pts = [(ux + 0.045 * math.cos(a), uy, uz + 0.06 - 0.045 * math.sin(a)) for a in [math.pi * k / 6 for k in range(7)]]
for k in range(6):
    rod(f"U Holder Bend {k}", pts[k], pts[k + 1], 0.009, chrome, verts=8)
rod("U Holder Stem", (ux, uy, uz + 0.01), (ux, uy, uz + 0.015), 0.012, chrome, verts=8)
for k, sx in enumerate((-0.045, 0.045)):
    rod(f"U Holder Arm {k}", (ux + sx, uy, uz + 0.06), (ux + sx, uy, uz + 0.17), 0.009, chrome, verts=8)
    cyl(f"U Holder Candle {k}", ux + sx, uy, uz + 0.17, uz + 0.36, 0.009, M["p_cream"], verts=10)

item("chrome vase")
cyl("Chrome Vase", 2.10, D - 0.17, levels[3] - 0.002, levels[3] + 0.29, 0.055, chrome, verts=24)
item(None)

# IKEA HYLLIS (60x27x74 cm, galvanised steel, three shelves) with oak inserts and one oak top
# running over 1, 2 or 3 units side by side along the wall opposite the desk
galv = mat("Galvanised Steel", "#b7bbbd", rough=0.35, metal=0.45)
HW, HD, HH, HP = 0.60, 0.27, 0.74, 0.022  # unit width, depth, height, corner post
for n in (1, 2, 3):
    use_option(f"piece:hyllis{n}")
    hx1 = W - 0.01
    hx0 = hx1 - HD
    run = n * HW
    hy0 = 1.05 - run / 2
    for u in range(n):
        uy0, uy1 = hy0 + u * HW, hy0 + (u + 1) * HW
        for px in (hx0, hx1 - HP):
            for py in (uy0, uy1 - HP):
                box(f"Hyllis {n} Post {u}", px, px + HP, py, py + HP, 0, HH, galv)
        for z in (0.07, 0.40, HH - 0.02):
            box(f"Hyllis {n} Shelf {u}", hx0, hx1, uy0 + 0.002, uy1 - 0.002, z, z + 0.02, galv)
            if z < 0.5:  # oak boards on the lower two shelves, as in the photo
                box(f"Hyllis {n} Board {u}", hx0 + 0.008, hx1 - 0.008, uy0 + 0.01, uy1 - 0.01, z + 0.02, z + 0.032, M["oak"])
    box(f"Hyllis {n} Top", hx0 - 0.02, hx1, hy0 - 0.01, hy0 + run + 0.01, HH, HH + 0.028, M["oak"], bevel=0.003)

use_option("piece:globelamp")  # opal glass globe lamp, sits on a bottom shelf
opal = mat("Globe Opal", "#f6eee2", rough=0.4, emit="#ffd9a6", emit_strength=1.2)
gx, gy = W - 0.145, 0.95
cyl("Globe Lamp Base", gx, gy, 0.09, 0.105, 0.07, mat("Clear Acrylic", "#e8eef0", rough=0.1), verts=24)
sphere("Globe Lamp Glass", (gx, gy, 0.105 + 0.12), 0.12, opal)
light_anchor("Light Globe Lamp", (gx, gy, 0.225), "globe")

# ================================================================ wall features
use_option("wf:slats")  # 5 oak slats behind the desk (moves with the desk wall)
box("Wallfeat Slat Felt", 0.0, 0.004, 0.0, 1.64, 0.0, H, mat("Slat Felt", "#1e1e1e", rough=1.0))
for k in range(36):
    y = 0.012 + k * 0.045
    box(f"Wallfeat Slat {k}", 0.004, 0.022, y, y + 0.03, 0.0, H, M["oak"])

use_option("wf:cork")  # 7 cork wall behind the desk
box("Wallfeat Cork", 0.0, 0.012, 0.15, 1.45, 0.80, 1.95, cork)
for k in range(9):
    y = 0.22 + (k % 3) * 0.40 + random.uniform(-0.05, 0.05)
    z = 1.05 + (k // 3) * 0.30
    box(f"Wallfeat Note {k}", 0.012, 0.014, y, y + random.uniform(0.10, 0.20), z, z + random.uniform(0.10, 0.18),
        random.choice([M["p_cream"], M["p_mustard"], M["p_teal"], M["book3"]]))

use_option("wf:rail")  # 8 picture rail all round, with two hanging frames
RZ = 2.25
for nm, a in (("W", (0.0, 0.02, 0.0, D - 0.52)), ("E", (W - 0.02, W, 0.0, D)), ("N", (0.52, W, D - 0.02, D)),
              ("S", (1.56, W, 0.0, 0.02)), ("Shaft", (0.52, 0.54, D - 0.52, D))):
    box(f"Picture Rail {nm}", *a, RZ, RZ + 0.03, M["oak"])
for k, (y0, y1, z0, z1, pm) in enumerate(((0.55, 0.95, 1.30, 1.80, M["p_teal"]), (1.10, 1.40, 1.45, 1.85, M["p_mustard"]))):
    box(f"Picture Rail Frame {k}", W - 0.025, W - 0.005, y0, y1, z0, z1, M["walnut"])
    box(f"Picture Rail Print {k}", W - 0.028, W - 0.025, y0 + 0.03, y1 - 0.03, z0 + 0.03, z1 - 0.03, pm)
    for j, y in enumerate((y0 + 0.05, y1 - 0.05)):
        rod(f"Picture Rail Cord {k}{j}", (W - 0.01, y, RZ), (W - 0.01, y, z1), 0.0015, M["black"], verts=4)

use_option("paint:twotone")  # 2 sage below 110 cm, warm white above, oak rail at the line
box("Twotone Upper", 0.0005, 0.003, 0.0, D - 0.52, 1.11, H, wall_upper)
box("Twotone Rail", 0.0, 0.02, 0.0, D - 0.52, 1.09, 1.12, M["oak"])

# ================================================================ shelving over the desk (moves with the desk wall)
use_option("shelf:planks")  # thick floating oak planks with bookends
for k, (y0, y1, z) in enumerate(((0.15, 0.95, 1.25), (0.35, 0.95, 1.55), (0.15, 0.75, 1.85))):
    box(f"Shelf Plank {k}", 0.0, 0.24, y0, y1, z - 0.04, z, M["oak"], bevel=0.004)
books_y("Shelf Plank Low", 0.02, 0.20, 0.20, 0.60, 1.25)
box("Shelf Plank Bookend 0", 0.03, 0.18, 0.61, 0.65, 1.25, 1.39, marble)
potted("Shelf Plank Pot", 0.12, 0.82, 1.25, 0.06, M["ceramic"])
books_y("Shelf Plank Mid", 0.02, 0.20, 0.62, 0.92, 1.55)
box("Shelf Plank Bookend 1", 0.03, 0.18, 0.57, 0.61, 1.55, 1.69, marble)
box("Shelf Plank Photo", 0.06, 0.07, 0.40, 0.52, 1.55, 1.70, M["black"])
sphere("Shelf Plank Ball", (0.12, 0.25, 1.89), 0.04, M["brass"])
books_y("Shelf Plank Top", 0.02, 0.20, 0.38, 0.70, 1.85)

use_option("shelf:rails")  # 606-style aluminium tracks, white shelves and a cabinet
for k, y in enumerate((0.16, 0.55, 0.94)):
    box(f"Shelf Track {k}", 0.0, 0.012, y - 0.012, y + 0.012, 1.10, 2.45, M["alu"])
for k, z in enumerate((1.25, 1.95, 2.25)):
    box(f"Shelf Alu {k}", 0.0, 0.23, 0.14, 0.96, z - 0.02, z, white_lacq)
box("Shelf Cabinet", 0.0, 0.30, 0.14, 0.55, 1.50, 1.80, white_lacq)
box("Shelf Cabinet Line", 0.30, 0.302, 0.344, 0.346, 1.52, 1.78, M["black"])
box("Shelf Rail Shelf", 0.0, 0.23, 0.56, 0.96, 1.60, 1.62, white_lacq)
books_y("Shelf Rails Low", 0.02, 0.20, 0.58, 0.94, 1.25)
books_y("Shelf Rails Mid", 0.02, 0.20, 0.58, 0.85, 1.62)
potted("Shelf Rails Pot", 0.12, 0.30, 1.95, 0.06, M["terracotta"])
books_y("Shelf Rails Top", 0.02, 0.20, 0.50, 0.90, 2.25, 0.12, 0.18)

use_option("shelf:cubes")  # open walnut wall boxes, staggered


def open_box(prefix, y0, z0, w, h, d=0.25, t=0.015):
    box(f"{prefix} Back", 0.0, t, y0, y0 + w, z0, z0 + h, M["walnut"])
    box(f"{prefix} Bottom", 0.0, d, y0, y0 + w, z0, z0 + t, M["walnut"])
    box(f"{prefix} Top", 0.0, d, y0, y0 + w, z0 + h - t, z0 + h, M["walnut"])
    box(f"{prefix} Side S", 0.0, d, y0, y0 + t, z0, z0 + h, M["walnut"])
    box(f"{prefix} Side N", 0.0, d, y0 + w - t, y0 + w, z0, z0 + h, M["walnut"])


for k, (y0, z0, w, h) in enumerate(((0.15, 1.20, 0.32, 0.30), (0.52, 1.38, 0.32, 0.30), (0.20, 1.62, 0.28, 0.28), (0.60, 1.80, 0.30, 0.30))):
    open_box(f"Shelf Cube {k}", y0, z0, w, h)
    if k % 2:
        potted(f"Shelf Cube Pot {k}", 0.13, y0 + w / 2, z0 + 0.015, 0.06, M["ceramic"])
    else:
        books_y(f"Shelf Cube {k}", 0.02, 0.22, y0 + 0.02, y0 + w - 0.06, z0 + 0.015, 0.15, h - 0.06)

use_option("shelf:pegboard")  # wooden pegboard with pegs and two small shelves
box("Shelf Peg Board", 0.0, 0.015, 0.15, 0.95, 1.15, 2.0, birch)
for k, (y, z) in enumerate(((0.25, 1.45), (0.55, 1.45), (0.35, 1.75), (0.85, 1.75), (0.70, 1.30), (0.80, 1.90))):
    rod(f"Shelf Peg {k}", (0.015, y, z - 0.012), (0.09, y, z - 0.012), 0.007, M["oak"], verts=8)
box("Shelf Peg Ledge 0", 0.015, 0.16, 0.20, 0.60, 1.45, 1.465, M["oak"])
box("Shelf Peg Ledge 1", 0.015, 0.16, 0.30, 0.90, 1.75, 1.765, M["oak"])
cyl("Shelf Peg Cup", 0.09, 0.30, 1.465, 1.57, 0.035, M["p_mustard"])
potted("Shelf Peg Pot", 0.09, 0.48, 1.465, 0.05, M["terracotta"])
books_y("Shelf Peg Books", 0.02, 0.15, 0.45, 0.80, 1.765, 0.14, 0.20)
rod("Shelf Peg Scissors", (0.07, 0.70, 1.30), (0.07, 0.70, 1.16), 0.006, M["p_red"], verts=6)

# ================================================================ corner by the door
use_option("corner:rocker")  # 63 bentwood rocker + 15 paper floor lantern
item("rocker")
rk = empty("Rocker", (2.15, 2.45, 0), rot_z=math.radians(20))
for s, yy in (("L", -0.24), ("R", 0.24)):
    pts = [(-0.42, yy, 0.10), (-0.25, yy, 0.03), (0.0, yy, 0.01), (0.25, yy, 0.05), (0.42, yy, 0.16), (0.52, yy, 0.30)]
    for k in range(len(pts) - 1):
        rod(f"Rocker Runner {s}{k}", pts[k], pts[k + 1], 0.016, bentwood, verts=8, parent=rk)
    rod(f"Rocker Front Leg {s}", (-0.25, yy, 0.03), (-0.22, yy * 0.95, 0.45), 0.016, bentwood, verts=8, parent=rk)
    rod(f"Rocker Back Leg {s}", (0.25, yy, 0.05), (0.18, yy * 0.9, 0.45), 0.016, bentwood, verts=8, parent=rk)
    arm_pts = [(-0.22, yy * 0.95, 0.45), (-0.20, yy * 1.05, 0.62), (0.05, yy * 1.08, 0.66), (0.24, yy * 0.95, 0.62)]
    for k in range(len(arm_pts) - 1):
        rod(f"Rocker Arm {s}{k}", arm_pts[k], arm_pts[k + 1], 0.013, bentwood, verts=8, parent=rk)
    rod(f"Rocker Back Post {s}", (0.18, yy * 0.75, 0.45), (0.34, yy * 0.65, 1.05), 0.016, bentwood, verts=8, parent=rk)
torus("Rocker Seat Ring", (-0.02, 0, 0.46), 0.22, 0.015, bentwood, scale=(1.05, 1.0, 1.0), parent=rk)
cyl("Rocker Seat Cane", -0.02, 0, 0.455, 0.465, 0.21, cane, verts=32, parent=rk)
rbk = empty("Rocker Back Pivot", (0.26, 0, 0.75), parent=rk)
rbk.rotation_euler = (0, math.radians(-75), 0)
torus("Rocker Back Ring", (0, 0, 0), 0.23, 0.014, bentwood, scale=(1.3, 0.75, 1.0), parent=rbk)
cyl("Rocker Back Cane", 0, 0, -0.004, 0.004, 0.21, cane, verts=32, parent=rbk).scale = (1.3, 0.72, 1.0)
item("lantern")
lx2, ly2 = 2.50, 3.05
for k in range(3):
    a = k * 2 * math.pi / 3 + 0.4
    rod(f"Floor Lantern Leg {k}", (lx2, ly2, 0.32), (lx2 + 0.16 * math.cos(a), ly2 + 0.16 * math.sin(a), 0.0), 0.007, M["black"], verts=6)
cyl("Floor Lantern Paper", lx2, ly2, 0.32, 1.42, 0.20, paper, verts=32)
for k in range(6):
    torus(f"Floor Lantern Rib {k}", (lx2, ly2, 0.40 + k * 0.19), 0.202, 0.003, paper_rib)
light_anchor("Light Floor Lantern", (lx2, ly2, 0.9), "floor")

use_option("corner:bookcase")  # tall open bookcase by the door
bx0, by0, by1, BH2 = W - 0.35, 2.25, 3.05, 2.0
box("Corner Case Side S", bx0, W, by0, by0 + 0.022, 0, BH2, M["oak"])
box("Corner Case Side N", bx0, W, by1 - 0.022, by1, 0, BH2, M["oak"])
for j, z in enumerate((0.05, 0.40, 0.75, 1.10, 1.45, BH2 - 0.025)):
    box(f"Corner Case Shelf {j}", bx0, W, by0, by1, z, z + 0.025, M["oak"])
    if j < 5:
        if j == 2:
            potted("Corner Case Pot", bx0 + 0.18, (by0 + by1) / 2, z + 0.025, 0.07, M["terracotta"])
        else:
            books_y_east(f"Corner Case {j}", bx0 + 0.03, W - 0.02, by0 + 0.03, by1 - 0.03 - 0.15 * (j % 2), z + 0.025)
potted("Corner Case Top Pot", bx0 + 0.18, by0 + 0.2, BH2, 0.06, M["ceramic"], leaves=9)

use_option("corner:pair")  # 62 two 366 armchairs and a coffee table
# The reading corner's chair is reused by copying its objects.
src = bpy.data.objects["366 Armchair"]
for k, (loc, rz) in enumerate((((2.25, 2.50, 0), 20), ((1.40, 1.95, 0), 200))):
    item(f"armchair {k + 1}")
    root = src.copy()
    root.name = f"Pair Armchair {k}"
    CURRENT["coll"].objects.link(root)
    tag(root)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rz))
    stack = [(src, root)]
    while stack:
        s_, d_ = stack.pop()
        for ch in s_.children:
            c2 = ch.copy()
            CURRENT["coll"].objects.link(c2)
            tag(c2)
            c2.parent = d_
            stack.append((ch, c2))
item("coffee table")
cyl("Pair Table Top", 1.85, 2.25, 0.40, 0.43, 0.30, M["walnut"], verts=40)
cyl("Pair Table Stem", 1.85, 2.25, 0.03, 0.40, 0.04, M["walnut"], verts=16)
cyl("Pair Table Foot", 1.85, 2.25, 0.0, 0.03, 0.20, M["walnut"], verts=32)
box("Pair Table Book", 1.80, 1.98, 2.15, 2.28, 0.43, 0.46, M["book1"])

use_option("corner:hanging")  # 67 hanging rattan egg chair
rod("Hanging Chain", (2.15, 2.55, H), (2.15, 2.55, 1.62), 0.008, M["black"], verts=6)
sphere("Hanging Shell", (2.15, 2.55, 1.10), 0.45, rattan, scale=(1.0, 1.0, 1.15))
sphere("Hanging Cushion", (2.02, 2.50, 0.88), 0.36, M["armchair"], scale=(1.0, 1.0, 0.35))

use_option("corner:beanbag")  # 70 leather bean bag and a lamp
item("bean bag")
sphere("Beanbag", (2.25, 2.55, 0.28), 0.45, cognac, scale=(1.0, 1.0, 0.62))
item("floor lamp")
cyl("Beanbag Lamp Base", 2.55, 3.10, 0.0, 0.03, 0.12, M["black"])
rod("Beanbag Lamp Pole", (2.55, 3.10, 0.03), (2.55, 3.10, 1.45), 0.01, M["black"], verts=8)
cyl("Beanbag Lamp Shade", 2.55, 3.10, 1.40, 1.62, 0.18, M["linen_shade"], verts=32, caps=False)
light_anchor("Light Beanbag Lamp", (2.55, 3.10, 1.48), "floor")

use_option("corner:secretary")  # 50 secretary desk with a stool
item("secretary")
sx0, sy0, sy1 = W - 0.42, 2.30, 3.05
box("Secretary Body", sx0, W, sy0, sy1, 0.10, 1.10, M["walnut"], bevel=0.004)
box("Secretary Flap", sx0 - 0.38, sx0, sy0 + 0.02, sy1 - 0.02, 0.72, 0.74, M["walnut"])
box("Secretary Flap Leather", sx0 - 0.34, sx0 - 0.02, sy0 + 0.08, sy1 - 0.08, 0.74, 0.742, M["book2"])
for k in range(4):
    y = sy0 + 0.06 + k * 0.17
    box(f"Secretary Pigeonhole {k}", sx0 - 0.002, sx0, y, y + 0.14, 0.80, 1.02, M["black"])
for i, (x, y) in enumerate(((sx0 + 0.05, sy0 + 0.05), (W - 0.05, sy0 + 0.05), (sx0 + 0.05, sy1 - 0.05), (W - 0.05, sy1 - 0.05))):
    rod(f"Secretary Leg {i}", (x, y, 0.10), (x - 0.02, y, 0.0), 0.018, M["walnut"], r2=0.011, verts=8)
item("stool")
cyl("Secretary Stool Seat", 1.98, 2.68, 0.44, 0.48, 0.18, M["armchair"], verts=24)
for k in range(3):
    a = k * 2 * math.pi / 3
    rod(f"Secretary Stool Leg {k}", (1.98 + 0.10 * math.cos(a), 2.68 + 0.10 * math.sin(a), 0.44),
        (1.98 + 0.17 * math.cos(a), 2.68 + 0.17 * math.sin(a), 0.0), 0.014, M["walnut"], verts=8)

# ================================================================ opposite the desk (east wall, back at +x)
OPP_GROUPS = {}

use_piece("hifi")  # 72 hi-fi unit for your turntable (57 record storage inside)
hx0, hy0, hy1, HH = W - 0.41, 0.35, 1.55, 0.50
box("Hifi Body", hx0, W - 0.01, hy0, hy1, 0.14, HH, M["walnut"], bevel=0.005)
box("Hifi Door", hx0 - 0.006, hx0, hy0 + 0.02, hy0 + 0.40, 0.17, HH - 0.03, M["walnut"])
box("Hifi Opening", hx0 - 0.001, hx0 + 0.30, hy0 + 0.42, hy0 + 0.80, 0.17, HH - 0.03, M["black"])
box("Hifi Amp", hx0 + 0.02, hx0 + 0.32, hy0 + 0.45, hy0 + 0.77, 0.18, 0.28, M["alu"])
for k in range(2):
    rod(f"Hifi Knob {k}", (hx0 + 0.02, hy0 + 0.52 + k * 0.18, 0.23), (hx0 + 0.005, hy0 + 0.52 + k * 0.18, 0.23), 0.02, M["black"], verts=16)
for k in range(24):
    y = hy0 + 0.83 + k * 0.014
    box(f"Hifi Record {k}", hx0 + 0.01, hx0 + 0.33, y, y + 0.006, 0.17, 0.47, random.choice([M["p_red"], M["p_black"], M["p_cream"], M["p_teal"], M["p_mustard"]]))
for i, (x, y) in enumerate(((hx0 + 0.05, hy0 + 0.05), (W - 0.06, hy0 + 0.05), (hx0 + 0.05, hy1 - 0.05), (W - 0.06, hy1 - 0.05))):
    rod(f"Hifi Leg {i}", (x, y, 0.14), (x - 0.02, y, 0.0), 0.018, M["walnut"], r2=0.011, verts=8)
box("Hifi Turntable", hx0 + 0.04, hx0 + 0.38, hy0 + 0.40, hy0 + 0.84, HH, HH + 0.08, M["walnut"], bevel=0.005)
rod("Hifi Platter", (hx0 + 0.21, hy0 + 0.60, HH + 0.08), (hx0 + 0.21, hy0 + 0.60, HH + 0.095), 0.15, M["black"], verts=40)
for k, y in enumerate((hy0 + 0.17, hy1 - 0.17)):
    box(f"Hifi Speaker {k}", hx0 + 0.08, hx0 + 0.32, y - 0.10, y + 0.10, HH, HH + 0.34, M["walnut"], bevel=0.005)
    box(f"Hifi Grille {k}", hx0 + 0.075, hx0 + 0.08, y - 0.09, y + 0.09, HH + 0.02, HH + 0.32, felt_grey)
item("print")
framed_print("Hifi Print", 0.55, 1.35, 1.15, 1.70, M["p_cream"],
             ((0.80, 1.45, 0.12, M["p_red"]), (1.05, 1.40, 0.12, M["p_teal"])))
OPP_GROUPS["hifi"] = (W - 0.21, 0.95)

use_piece("daybed")  # 61 mid-century daybed
dx0, dy0, dy1 = W - 0.80, 0.05, 1.95
box("Daybed Frame", dx0, W - 0.02, dy0, dy1, 0.18, 0.30, M["walnut"], bevel=0.008)
box("Daybed Mattress", dx0 + 0.02, W - 0.04, dy0 + 0.02, dy1 - 0.02, 0.30, 0.45, lounge, bevel=0.03)
for k, y in enumerate((dy0 + 0.10, dy1 - 0.10)):
    rod(f"Daybed Bolster {k}", (dx0 + 0.05, y, 0.53), (W - 0.06, y, 0.53), 0.09, M["armchair"], verts=24)
for k, y in enumerate((0.55, 1.00, 1.45)):
    c = box(f"Daybed Cushion {k}", -0.06, 0.06, -0.22, 0.22, 0.0, 0.40, lounge if k != 1 else M["rug_rust"], bevel=0.04)
    c.location = (W - 0.12, y, 0.44)
    c.rotation_euler = (0, math.radians(12), 0)
box("Daybed Throw", dx0 + 0.05, dx0 + 0.55, 1.30, 1.75, 0.45, 0.47, M["rug_mustard"], bevel=0.01)
for i, (x, y) in enumerate(((dx0 + 0.06, dy0 + 0.08), (W - 0.08, dy0 + 0.08), (dx0 + 0.06, dy1 - 0.08), (W - 0.08, dy1 - 0.08))):
    rod(f"Daybed Leg {i}", (x, y, 0.18), (x - 0.03 if x < 2.3 else x, y + (-0.03 if y < 1 else 0.03), 0.0), 0.022, M["walnut"], r2=0.013, verts=8)
OPP_GROUPS["daybed"] = (W - 0.40, 1.00)

use_piece("prl")  # 56 PRL wall-unit section
px0, py0, py1 = W - 0.45, 0.35, 1.55
box("PRL Low", px0, W - 0.01, py0, py1, 0.08, 0.75, veneer, bevel=0.004)
for k in range(3):
    a = py0 + 0.02 + k * 0.39
    box(f"PRL Door {k}", px0 - 0.006, px0, a, a + 0.37, 0.11, 0.72, veneer)
    box(f"PRL Pull {k}", px0 - 0.014, px0 - 0.006, a + 0.15, a + 0.22, 0.62, 0.635, M["brass"])
box("PRL Upper", px0 + 0.10, W - 0.01, py0, py1, 0.75, 1.85, veneer)
box("PRL Vitrine Glass", px0 + 0.095, px0 + 0.10, py0 + 0.03, py1 - 0.03, 0.80, 1.80, M["glass"])
for j, z in enumerate((1.12, 1.46)):
    box(f"PRL Glass Shelf {j}", px0 + 0.10, W - 0.02, py0 + 0.02, py1 - 0.02, z, z + 0.008, M["glass"])
for k in range(10):
    y = py0 + 0.10 + (k % 5) * 0.24
    z = 0.80 if k < 5 else 1.128
    if k % 2:
        cyl(f"PRL Crystal {k}", px0 + 0.28, y, z, z + 0.16, 0.04, M["glass"], r2=0.025)
    else:
        sphere(f"PRL Porcelain {k}", (px0 + 0.28, y, z + 0.07), 0.05, porcelain, scale=(0.8, 0.8, 1.3))
for i, (x, y) in enumerate(((px0 + 0.04, py0 + 0.04), (W - 0.05, py0 + 0.04), (px0 + 0.04, py1 - 0.04), (W - 0.05, py1 - 0.04))):
    cyl(f"PRL Foot {i}", x, y, 0.0, 0.08, 0.02, M["black"], verts=8)
OPP_GROUPS["prl"] = (W - 0.225, 0.95)

use_piece("planchest")  # 59 plan chest for prints, PCBs and paper
qx0, qy0, qy1 = W - 0.72, 0.35, 1.45
box("Planchest Body", qx0, W - 0.02, qy0, qy1, 0.08, 0.72, M["oak"], bevel=0.004)
box("Planchest Top", qx0 - 0.01, W - 0.02, qy0 - 0.01, qy1 + 0.01, 0.72, 0.75, M["walnut"], bevel=0.004)
for k in range(6):
    z = 0.10 + k * 0.102
    box(f"Planchest Drawer {k}", qx0 - 0.004, qx0, qy0 + 0.02, qy1 - 0.02, z, z + 0.095, M["oak"])
    box(f"Planchest Pull {k}", qx0 - 0.014, qx0 - 0.004, (qy0 + qy1) / 2 - 0.10, (qy0 + qy1) / 2 + 0.10, z + 0.06, z + 0.075, M["steel"])
box("Planchest Base", qx0 + 0.02, W - 0.04, qy0 + 0.02, qy1 - 0.02, 0.0, 0.08, M["black"])
box("Planchest Print", qx0 + 0.08, qx0 + 0.50, qy0 + 0.15, qy0 + 0.75, 0.75, 0.752, M["p_cream"])
cyl("Planchest Lamp Base", qx0 + 0.55, qy1 - 0.15, 0.75, 0.77, 0.07, M["black"])
rod("Planchest Lamp Arm", (qx0 + 0.55, qy1 - 0.15, 0.77), (qx0 + 0.40, qy1 - 0.30, 1.15), 0.008, M["black"], verts=8)
rod("Planchest Lamp Head", (qx0 + 0.40, qy1 - 0.30, 1.15), (qx0 + 0.32, qy1 - 0.36, 1.05), 0.025, M["black"], r2=0.06, verts=16)
OPP_GROUPS["planchest"] = (W - 0.37, 0.90)

use_piece("lounge")  # 66 low modular floor sofa
lx0, ly0, ly1 = W - 0.80, 0.10, 2.00
for k in range(3):
    a = ly0 + k * (ly1 - ly0) / 3
    b_ = a + (ly1 - ly0) / 3 - 0.01
    box(f"Lounge Seat {k}", lx0, W - 0.02, a, b_, 0.0, 0.22, lounge, bevel=0.04)
    c = box(f"Lounge Back {k}", -0.10, 0.10, a - (a + b_) / 2 + 0.02, b_ - (a + b_) / 2 - 0.02, 0.0, 0.42, lounge, bevel=0.05)
    c.location = (W - 0.14, (a + b_) / 2, 0.22)
    c.rotation_euler = (0, math.radians(10), 0)
for k, y in enumerate((0.55, 1.45)):
    box(f"Lounge Pillow {k}", lx0 + 0.25, lx0 + 0.40, y - 0.18, y + 0.18, 0.22, 0.52, M["rug_rust"] if k else M["rug_mustard"], bevel=0.04)
OPP_GROUPS["lounge"] = (W - 0.41, 1.05)

# ================================================================ plants
use_option("plant:monstera")  # 97 monstera by the door
mpx, mpy = 1.95, 3.05
cyl("Monstera Pot", mpx, mpy, 0.0, 0.38, 0.20, M["ceramic"], r2=0.17, verts=32)
for k in range(9):
    a = k * 0.7 + 0.3
    h = 0.75 + 0.35 * ((k * 37) % 5) / 5
    tip = (mpx + 0.40 * math.cos(a), mpy + 0.40 * math.sin(a) * 0.7, h)
    rod(f"Monstera Stem {k}", (mpx, mpy, 0.36), tip, 0.006, lime_green, verts=6)
    sphere(f"Monstera Leaf {k}", tip, 0.16, M["leaf"], scale=(1.0, 0.85, 0.08), rot=(0.4, 0.3, a))

use_option("plant:ladder")  # 91 plant ladder by the window
for k, x in enumerate((1.70, 1.95)):
    rod(f"Plant Ladder Rail {k}", (x, 0.44, 0.0), (x, 0.04, 1.80), 0.014, M["oak"], verts=8)
for j, t in enumerate((0.15, 0.40, 0.65, 0.88)):
    z = 1.80 * t
    y = 0.44 - 0.40 * t
    box(f"Plant Ladder Step {j}", 1.70, 1.95, y - 0.10, y + 0.06, z, z + 0.018, M["oak"])
    potted(f"Plant Ladder Pot {j}", 1.825, y - 0.02, z + 0.018, 0.055, [M["terracotta"], M["ceramic"]][j % 2], leaves=7)

use_option("plant:hanging")  # 92 macramé hangers with trailing pothos
for k, (hx, hy) in enumerate(((1.20, 0.45), (2.10, 0.38))):
    for j in range(3):
        a = j * 2 * math.pi / 3
        rod(f"Hanging Cord {k}{j}", (hx, hy, H), (hx + 0.09 * math.cos(a), hy + 0.09 * math.sin(a), 1.86), 0.003, M["rug_cream"], verts=4)
    cyl(f"Hanging Pot {k}", hx, hy, 1.72, 1.86, 0.09, M["ceramic"], r2=0.07, verts=24)
    for j in range(10):
        a = j * 0.63
        sphere(f"Hanging Vine {k}{j}", (hx + 0.10 * math.cos(a), hy + 0.10 * math.sin(a), 1.80 - 0.04 * (j % 5)),
               0.04, M["leaf"], scale=(1, 0.7, 0.35), rot=(0.6, 0.2, a))

use_option("plant:windowrod")  # 30 rod across the window reveal with small hanging pots
rod("Window Rod", (0.08, -0.05, 2.20), (1.50, -0.05, 2.20), 0.008, M["brass"], verts=8)
for k, x in enumerate((0.40, 0.79, 1.18)):
    rod(f"Window Rod Cord {k}", (x, -0.05, 2.20), (x, -0.05, 1.98), 0.002, M["rug_cream"], verts=4)
    potted(f"Window Rod Pot {k}", x, -0.05, 1.86, 0.06, M["ceramic"], leaves=5)

# ================================================================ add-ons (x:...)
use_option("x:bias")  # 12/78 bias light behind the monitor
box("Desk Bias Strip", 0.085, 0.095, 0.45, 1.09, DZ + 0.12, DZ + 0.38, glow)
light_anchor("Light Desk Bias", (0.04, 0.77, DZ + 0.25), "bias")

use_option("x:sconces")  # 13 swing-arm sconces on the window wall
for k, x in enumerate((1.70, 2.55)):
    box(f"Sconce Plate {k}", x - 0.05, x + 0.05, 0.0, 0.02, 1.55, 1.65, M["brass"])
    rod(f"Sconce Arm {k}", (x, 0.02, 1.60), (x, 0.28, 1.70), 0.007, M["brass"], verts=8)
    rod(f"Sconce Shade {k}", (x, 0.28, 1.72), (x, 0.28, 1.58), 0.03, M["linen_shade"], r2=0.08, verts=24)
    light_anchor(f"Light Sconce {k}", (x, 0.28, 1.60), "sconce")

use_option("x:piclights")  # 14 picture lights over the posters
item("above desk")
box("Poster A Light", 0.0, 0.10, 1.06, 1.34, 1.98, 2.01, M["brass"])
item("on shaft")
box("Poster B Light", 0.52, 0.62, D - 0.42, D - 0.12, 1.94, 1.97, M["brass"])

use_option("x:uplight")  # 18 uplight washing the green shaft
cyl("Uplight Can", 0.64, 3.06, 0.0, 0.12, 0.06, M["black"])
light_anchor("Light Uplight", (0.62, 3.06, 0.30), "uplight")

use_option("x:nightlight")  # 20 motion night light at skirting height
box("Night Light", W - 0.012, W, 3.00, 3.07, 0.14, 0.19, night)

use_option("x:pelmet")  # 27/28 wooden pelmet over the blind box
box("Pelmet Front", -0.02, 1.62, 0.14, 0.16, 2.40, 2.62, M["oak"])
box("Pelmet Top", -0.02, 1.62, 0.0, 0.16, 2.60, 2.62, M["oak"])

use_option("x:sill")  # 23 deeper oak sill as a plant shelf
box("Deep Sill", 0.04, 1.54, -0.10, 0.16, 0.85, 0.88, M["oak"], bevel=0.003)
potted("Deep Sill Pot", 1.30, 0.06, 0.88, 0.05, M["terracotta"])

use_option("x:film")  # 29 reeded window film on the lower panes
box("Window Film", 0.10, 1.48, -0.054, -0.052, 0.92, 1.55, film)

use_option("x:colrad")  # 25 low black column radiator
hide_with([o.name for o in bpy.data.objects if o.name.startswith("Radiator ")], "x:colrad")
for k in range(16):
    x = 0.82 + k * 0.042
    cyl(f"Column Rad Tube {k}", x, 0.10, 0.12, 0.60, 0.016, M["black"], verts=10)
box("Column Rad Top", 0.80, 1.48, 0.08, 0.12, 0.56, 0.58, M["black"])
box("Column Rad Bottom", 0.80, 1.48, 0.08, 0.12, 0.13, 0.15, M["black"])

use_option("x:trv")  # 26 smart radiator valve
cyl("Smart Valve", 1.52, 0.10, 0.52, 0.62, 0.028, M["ceramic"])

use_option("x:runner")  # 33 runner along the wardrobe
box("Runner", 0.66, 1.26, 1.72, 2.76, 0, 0.007, navy)
for k in range(5):
    y = 1.80 + k * 0.22
    box(f"Runner Stripe {k}", 0.70, 1.22, y, y + 0.05, 0.007, 0.009, ochre if k % 2 else ivory)

use_option("x:chairmat")  # 32 felt chair mat (moves with the chair)
cyl("Chairx Mat", 0, 0, 0.0, 0.004, 0.55, felt_grey, verts=40).location = (1.05, 0.75, 0.002)

use_option("x:sheepskin")  # 34 sheepskin over the desk chair
sphere("Chairx Sheepskin", (1.04, 0.74, 0.50), 0.27, sheep, scale=(1.0, 1.0, 0.12))

use_option("x:throw")  # 35 throw and cushions on the armchair
box("Throw Drape", 2.28, 2.52, 2.20, 2.42, 0.45, 0.62, M["rug_mustard"], bevel=0.02)
box("Throw Cushion", 2.22, 2.36, 2.38, 2.62, 0.45, 0.70, M["rug_rust"], bevel=0.04)

use_option("x:pouf")  # 37 leather pouf
cyl("Pouf", 1.82, 1.45, 0.0, 0.38, 0.25, cognac, verts=32)

use_option("x:ottoman")  # 64 ottoman for the armchair
box("Ottoman Top", 1.42, 1.82, 2.02, 2.46, 0.24, 0.40, M["armchair"], bevel=0.03)
for i, (x, y) in enumerate(((1.46, 2.06), (1.78, 2.06), (1.46, 2.42), (1.78, 2.42))):
    rod(f"Ottoman Leg {i}", (x, y, 0.24), (x, y, 0.0), 0.016, M["walnut"], r2=0.01, verts=8)

use_option("x:monarm")  # 41 monitor arm (moves with the desk)
hide_with(["Monitor Base", "Monitor Neck"], "x:monarm")
box("Desk Arm Clamp", 0.0, 0.05, 0.74, 0.80, DZ - 0.05, DZ + 0.02, M["black"])
rod("Desk Arm Post", (0.025, 0.77, DZ), (0.025, 0.77, DZ + 0.32), 0.014, M["black"], verts=10)
rod("Desk Arm Link", (0.025, 0.77, DZ + 0.30), (0.10, 0.77, DZ + 0.25), 0.012, M["black"], verts=10)

use_option("x:pedestal")  # 42 drawer pedestal on castors
box("Desk Pedestal", 0.12, 0.56, 0.18, 0.58, 0.04, 0.60, M["walnut"], bevel=0.004)
for k, z in enumerate((0.22, 0.40)):
    box(f"Desk Pedestal Line {k}", 0.56, 0.562, 0.19, 0.57, z, z + 0.004, M["black"])
for i, (x, y) in enumerate(((0.15, 0.21), (0.53, 0.21), (0.15, 0.55), (0.53, 0.55))):
    sphere(f"Desk Pedestal Wheel {i}", (x, y, 0.02), 0.02, M["black"])

use_option("x:pad")  # 43 felt desk pad
box("Desk Pad", 0.27, 0.64, 0.55, 1.25, DZ, DZ + 0.003, felt_grey)

use_option("x:riser")  # 44 walnut monitor riser
box("Desk Riser", 0.04, 0.30, 0.45, 1.10, DZ, DZ + 0.06, M["walnut"], bevel=0.004)

use_option("x:spine")  # 45 cable spine
for k in range(12):
    z = DZ - 0.04 - k * (DZ - 0.04) / 11
    cyl(f"Desk Spine {k}", 0.42, 1.22, z - 0.025, z + 0.025, 0.022, M["black"], verts=10)

use_option("x:screen2")  # 46 vertical second monitor
hide_with([o.name for o in bpy.data.objects if o.name.startswith("Orchid ")], "x:screen2")
box("Desk Screen2 Panel", 0.11, 0.14, 1.14, 1.48, DZ + 0.14, DZ + 0.74, bpy.data.materials["Monitor Black"])
box("Desk Screen2 Glow", 0.14, 0.142, 1.16, 1.46, DZ + 0.16, DZ + 0.72, bpy.data.materials["Screen"])
box("Desk Screen2 Base", 0.06, 0.26, 1.21, 1.41, DZ, DZ + 0.012, bpy.data.materials["Monitor Black"])
box("Desk Screen2 Neck", 0.08, 0.11, 1.29, 1.33, DZ, DZ + 0.30, bpy.data.materials["Monitor Black"])

use_option("x:charger")  # 49 wireless charger set into the top
cyl("Desk Charger", 0.56, 1.10, DZ, DZ + 0.004, 0.05, M["alu"])
box("Desk Charger Phone", 0.52, 0.60, 1.03, 1.17, DZ + 0.004, DZ + 0.013, M["black"])

use_option("x:acc")  # 86 teak and brass desk accessories
box("Desk Acc Tray", 0.06, 0.24, 0.56, 0.74, DZ, DZ + 0.015, M["walnut"])
cyl("Desk Acc Pen Cup", 0.12, 0.62, DZ + 0.015, DZ + 0.12, 0.03, M["brass"])
box("Desk Acc Letters", 0.16, 0.22, 0.60, 0.72, DZ + 0.015, DZ + 0.10, M["walnut"])

use_option("x:mic")  # 79 mic arm for calls
box("Desk Mic Clamp", 0.0, 0.05, 1.20, 1.26, DZ - 0.05, DZ + 0.02, M["black"])
rod("Desk Mic Post", (0.025, 1.23, DZ), (0.025, 1.23, DZ + 0.28), 0.01, M["black"], verts=8)
rod("Desk Mic Arm", (0.025, 1.23, DZ + 0.28), (0.36, 1.05, DZ + 0.42), 0.008, M["black"], verts=8)
rod("Desk Mic Body", (0.36, 1.05, DZ + 0.42), (0.40, 1.02, DZ + 0.28), 0.025, M["black"], verts=16)

use_option("x:perch")  # 65 standing perch stool (moves with the desk)
cyl("Desk Perch Base", 0.95, 1.30, 0.0, 0.03, 0.18, M["black"])
rod("Desk Perch Post", (0.95, 1.30, 0.03), (0.92, 1.30, 0.62), 0.02, M["alu"], verts=10)
sphere("Desk Perch Seat", (0.92, 1.30, 0.66), 0.16, M["armchair"], scale=(1.0, 0.8, 0.25))

use_option("x:rack")  # 77 10-inch mini rack for a home lab
box("Desk Rack Case", 0.08, 0.40, 0.68, 1.00, 0.02, 0.38, M["black"], bevel=0.004)
for k in range(4):
    z = 0.06 + k * 0.08
    box(f"Desk Rack Unit {k}", 0.40, 0.402, 0.70, 0.98, z, z + 0.06, M["device"])
    box(f"Desk Rack LED {k}", 0.402, 0.404, 0.72 + k * 0.02, 0.735 + k * 0.02, z + 0.02, z + 0.03, led)

use_option("x:shaftshelves")  # 53 floating shelves on the shaft
for k, z in enumerate((1.05, 1.40, 1.75)):
    box(f"Shaft Shelf {k}", 0.52, 0.74, D - 0.46, D - 0.08, z - 0.03, z, M["oak"])
books_y_east("Shaft Shelf Low", 0.54, 0.72, D - 0.44, D - 0.22, 1.05)
potted("Shaft Shelf Pot", 0.63, D - 0.27, 1.40, 0.06, M["terracotta"])
sphere("Shaft Shelf Vase", (0.63, D - 0.20, 1.83), 0.06, porcelain, scale=(0.8, 0.8, 1.3))

use_option("x:laddershelf")  # 54 leaning ladder shelf right of the door
for k, x in enumerate((1.68, 1.98)):
    rod(f"Ladder Shelf Rail {k}", (x, D - 0.42, 0.0), (x, D - 0.03, 1.75), 0.014, M["oak"], verts=8)
for j, t in enumerate((0.15, 0.40, 0.65)):
    z = 1.75 * t
    y = D - 0.42 + 0.39 * t
    box(f"Ladder Shelf Step {j}", 1.68, 1.98, y - 0.02, D - 0.03, z, z + 0.018, M["oak"])
    box(f"Ladder Shelf Box {j}", 1.72, 1.94, y + 0.01, min(y + 0.20, D - 0.04), z + 0.018, z + 0.14, [M["book3"], M["book2"], M["p_cream"]][j], bevel=0.01)

use_option("x:hooks")  # 55 hook rail on the door
box("Door Hook Rail", 0.92, 1.44, D + 0.004, D + 0.02, 1.70, 1.74, M["oak"])
for k in range(4):
    x = 0.98 + k * 0.13
    rod(f"Door Hook {k}", (x, D + 0.004, 1.72), (x, D - 0.04, 1.74), 0.006, M["brass"], verts=6)
box("Door Hook Coat", 1.04, 1.30, D - 0.06, D - 0.01, 1.05, 1.72, M["book4"], bevel=0.02)

use_option("x:abovedoor")  # 58 cabinet above the door
box("Above Door Cabinet", 0.66, 1.70, D - 0.38, D, 2.18, H - 0.002, M["walnut"], bevel=0.004)
box("Above Door Line", 1.178, 1.182, D - 0.382, D - 0.38, 2.20, H - 0.02, M["black"])

use_option("x:baskets")  # 60 woven baskets
for k, x in enumerate((1.22, 1.40)):
    cyl(f"Sill Basket {k}", x, -0.03, 0.85, 0.97, 0.07, rattan, verts=20)

use_option("x:pegrail")  # 69 Shaker peg rail with folding chairs
box("Peg Rail", 1.70, 2.62, D - 0.02, D, 1.78, 1.86, M["oak"])
for k in range(5):
    x = 1.78 + k * 0.19
    rod(f"Peg Rail Peg {k}", (x, D - 0.02, 1.82), (x, D - 0.09, 1.83), 0.012, M["oak"], verts=8)
for k, x in enumerate((1.97, 2.35)):
    box(f"Peg Rail Chair {k}", x - 0.20, x + 0.20, D - 0.08, D - 0.05, 0.98, 1.82, M["oak"])
    box(f"Peg Rail Chair Seat {k}", x - 0.17, x + 0.17, D - 0.085, D - 0.08, 1.05, 1.40, cane)

use_option("x:projector")  # 71 projector and pull-down screen in front of the window
box("Projector Mount", W / 2 - 0.02, W / 2 + 0.02, 2.88, 2.92, H - 0.20, H, M["black"])
box("Projector Body", W / 2 - 0.15, W / 2 + 0.15, 2.80, 3.02, H - 0.30, H - 0.20, M["ceramic"], bevel=0.01)
rod("Projector Lens", (W / 2, 2.80, H - 0.25), (W / 2, 2.77, H - 0.25), 0.035, M["black"], verts=16)
box("Screen Cassette", 0.08, 1.52, 0.42, 0.48, 2.58, 2.65, M["ceramic"])
box("Screen Cloth", 0.10, 1.50, 0.449, 0.451, 1.25, 2.58, screen_white)
box("Screen Bar", 0.10, 1.50, 0.44, 0.46, 1.23, 1.25, M["black"])

use_option("x:eink")  # 73 e-ink dashboard by the door
box("Eink Frame", 0.555, 0.725, D - 0.015, D, 1.30, 1.56, M["ceramic"])
box("Eink Screen", 0.57, 0.71, D - 0.017, D - 0.015, 1.32, 1.54, eink)
for k in range(4):
    box(f"Eink Line {k}", 0.58, 0.70 - k * 0.02, D - 0.018, D - 0.017, 1.50 - k * 0.04, 1.51 - k * 0.04, M["black"])

use_option("x:co2")  # 74 CO2 and temperature sensor
box("CO2 Sensor", 0.10, 0.18, -0.06, 0.0, 0.85, 0.92, M["ceramic"], bevel=0.005)
box("CO2 Sensor LED", 0.12, 0.16, 0.0, 0.002, 0.89, 0.90, mat("LED Green", "#0a2a12", emit="#4cff7a", emit_strength=3.0))

use_option("x:matrix")  # 80 LED matrix clock
box("Matrix Clock", 0.28, 0.48, -0.06, 0.0, 0.85, 0.93, M["black"], bevel=0.004)
box("Matrix Clock Face", 0.29, 0.47, 0.0, 0.002, 0.865, 0.915, led)

use_option("x:figurines")  # 83 Ćmielów porcelain figurines
for k, x in enumerate((0.56, 0.66, 0.76)):
    cyl(f"Figurine Base {k}", x, -0.03, 0.85, 0.87, 0.025, porcelain, verts=12)
    sphere(f"Figurine Body {k}", (x, -0.03, 0.92 + 0.02 * (k % 2)), 0.03 + 0.008 * k, porcelain, scale=(0.7, 0.9, 1.4))

use_option("x:flipclock")  # 88 flip clock on the side table
box("Flip Clock", 2.52, 2.62, 2.00, 2.14, 0.53, 0.61, M["p_cream"], bevel=0.005)
box("Flip Clock Face", 2.519, 2.521, 2.02, 2.12, 0.55, 0.59, M["p_black"])

use_option("x:globe")  # 89 vintage floor globe
for k in range(3):
    a = k * 2 * math.pi / 3
    rod(f"Globe Leg {k}", (1.80, 0.30, 0.55), (1.80 + 0.18 * math.cos(a), 0.30 + 0.18 * math.sin(a), 0.0), 0.012, M["walnut"], verts=8)
sphere("Globe Ball", (1.80, 0.30, 0.78), 0.16, globe_blue)
torus("Globe Meridian", (1.80, 0.30, 0.78), 0.175, 0.006, M["brass"], rot=(math.radians(90), math.radians(23), 0))

use_option("x:growlight")  # 93 grow light under the lowest shelf (moves with the desk wall)
box("Shelf Grow Light", 0.02, 0.06, 0.20, 0.90, 1.17, 1.19, grow)

use_option("x:felt")  # 94 hexagonal felt acoustic panels
for k, (y, m) in enumerate(((0.55, felt_green), (0.95, felt_grey), (1.35, felt_rust))):
    rod(f"Felt Panel {k}", (W - 0.03, y, 2.15 + 0.08 * (k % 2)), (W, y, 2.15 + 0.08 * (k % 2)), 0.20, m, verts=6)

use_option("x:excluder")  # 95 draught excluder at the door
rod("Draught Excluder", (0.80, D - 0.05, 0.045), (1.56, D - 0.05, 0.045), 0.045, M["rug_mustard"], verts=16)

use_option("x:humidifier")  # 96 ceramic humidifier
cyl("Humidifier", 1.58, 0.30, 0.0, 0.26, 0.10, M["ceramic"], r2=0.07, verts=24)
cyl("Humidifier Top", 1.58, 0.30, 0.26, 0.28, 0.06, M["walnut"], verts=24)

use_option("x:terrarium")  # 98 terrarium on the sill
sphere("Terrarium Glass", (0.95, -0.03, 0.94), 0.08, M["glass"])
sphere("Terrarium Moss", (0.95, -0.03, 0.89), 0.06, lime_green, scale=(1, 1, 0.4))

# ================================================================ where the wardrobe was (west wall, y 1.70-2.78)
# Only shown when the wardrobe is removed; the viewer picks the clothes rail by default.


def copy_tree(src_name, new_name, loc, rz):
    src = bpy.data.objects[src_name]
    root = src.copy()
    root.name = new_name
    CURRENT["coll"].objects.link(root)
    tag(root)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rz))
    stack = [(src, root)]
    while stack:
        s_, d_ = stack.pop()
        for ch in s_.children:
            c2 = ch.copy()
            CURRENT["coll"].objects.link(c2)
            tag(c2)
            c2.parent = d_
            stack.append((ch, c2))
    return root


FY0, FY1 = 1.72, 2.76
use_option("freed:rail")  # open clothes rail to replace the hanging space
for k, y in enumerate((FY0 + 0.03, FY1 - 0.03)):
    rod(f"Freed Rail Upright {k}", (0.30, y, 0.0), (0.30, y, 1.78), 0.014, M["steel"], verts=10)
    box(f"Freed Rail Foot {k}", 0.06, 0.54, y - 0.015, y + 0.015, 0.0, 0.03, M["steel"])
rod("Freed Rail Bar", (0.30, FY0 + 0.03, 1.76), (0.30, FY1 - 0.03, 1.76), 0.013, M["steel"], verts=10)
box("Freed Rail Shelf", 0.08, 0.52, FY0 + 0.05, FY1 - 0.05, 0.18, 0.20, M["oak"])
for k in range(4):
    y = FY0 + 0.12 + k * 0.24
    box(f"Freed Rail Shoes {k}", 0.14, 0.46, y - 0.08, y + 0.08, 0.20, 0.30, random.choice([M["book3"], M["p_black"], M["book1"]]), bevel=0.01)
for k in range(10):
    y = FY0 + 0.10 + k * 0.088
    h = random.uniform(0.62, 1.00)
    rod(f"Freed Rail Hanger {k}", (0.30, y, 1.76), (0.30, y, 1.70), 0.003, M["black"], verts=4)
    box(f"Freed Rail Garment {k}", 0.08, 0.52, y - 0.02, y + 0.02, 1.70 - h, 1.70,
        random.choice([M["book4"], M["book2"], M["p_cream"], M["rug_rust"], M["p_black"], M["book3"]]), bevel=0.012)

use_option("freed:dresser")  # low dresser with a lamp and a print above
box("Freed Dresser Body", 0.0, 0.45, FY0 + 0.08, FY1 - 0.08, 0.12, 0.82, M["walnut"], bevel=0.005)
for c_ in range(2):
    for r in range(3):
        y0 = FY0 + 0.10 + c_ * 0.44
        z0 = 0.15 + r * 0.22
        box(f"Freed Dresser Drawer {c_}{r}", 0.45, 0.456, y0, y0 + 0.42, z0, z0 + 0.20, M["walnut"])
        box(f"Freed Dresser Pull {c_}{r}", 0.456, 0.466, y0 + 0.17, y0 + 0.25, z0 + 0.09, z0 + 0.11, M["brass"])
for i, y in enumerate((FY0 + 0.12, FY1 - 0.12)):
    for j, x in enumerate((0.04, 0.41)):
        rod(f"Freed Dresser Leg {i}{j}", (x, y, 0.12), (x + (0.02 if j else -0.0), y, 0.0), 0.018, M["walnut"], r2=0.011, verts=8)
cyl("Freed Dresser Lamp Base", 0.22, FY0 + 0.25, 0.82, 1.00, 0.06, M["ceramic"], r2=0.045)
sphere("Freed Dresser Lamp", (0.22, FY0 + 0.25, 1.11), 0.11, M["opal"])
light_anchor("Light Freed Dresser", (0.22, FY0 + 0.25, 1.11), "console")
potted("Freed Dresser Pot", 0.22, FY1 - 0.30, 0.82, 0.07, M["terracotta"], leaves=8)
box("Freed Dresser Print Frame", 0.0, 0.022, FY0 + 0.20, FY1 - 0.20, 1.20, 1.72, M["oak"])
box("Freed Dresser Print", 0.022, 0.024, FY0 + 0.24, FY1 - 0.24, 1.24, 1.68, M["p_cream"])
rod("Freed Dresser Print Sun", (0.024, (FY0 + FY1) / 2, 1.48), (0.027, (FY0 + FY1) / 2, 1.48), 0.13, M["p_mustard"], verts=32)

use_option("freed:desk2")  # second, screen-free hobby desk
item("desk")
box("Freed Desk Top", 0.0, 0.60, FY0 + 0.04, FY1 - 0.04, 0.72, 0.75, M["oak"], bevel=0.004)
for k, y in enumerate((FY0 + 0.15, FY1 - 0.15)):
    rod(f"Freed Desk Trestle A {k}", (0.08, y, 0.0), (0.30, y, 0.72), 0.016, M["black"], verts=8)
    rod(f"Freed Desk Trestle B {k}", (0.52, y, 0.0), (0.30, y, 0.72), 0.016, M["black"], verts=8)
board = box("Freed Desk Board", -0.20, 0.20, -0.28, 0.28, 0.0, 0.015, M["p_cream"])
board.location = (0.26, (FY0 + FY1) / 2, 0.80)
board.rotation_euler = (0, math.radians(20), 0)
rod("Freed Desk Lamp Post", (0.05, FY1 - 0.15, 0.75), (0.05, FY1 - 0.15, 1.15), 0.008, M["black"], verts=8)
rod("Freed Desk Lamp Arm", (0.05, FY1 - 0.15, 1.15), (0.30, FY1 - 0.30, 1.18), 0.008, M["black"], verts=8)
rod("Freed Desk Lamp Shade", (0.30, FY1 - 0.30, 1.18), (0.34, FY1 - 0.32, 1.06), 0.025, M["black"], r2=0.07, verts=16)
light_anchor("Light Freed Desk", (0.34, FY1 - 0.32, 1.04), "desk")
item("stool")
cyl("Freed Desk Stool", 0.80, (FY0 + FY1) / 2, 0.44, 0.48, 0.17, M["oak"], verts=24)
for k in range(3):
    a = k * 2 * math.pi / 3
    rod(f"Freed Desk Stool Leg {k}", (0.80 + 0.09 * math.cos(a), (FY0 + FY1) / 2 + 0.09 * math.sin(a), 0.44),
        (0.80 + 0.16 * math.cos(a), (FY0 + FY1) / 2 + 0.16 * math.sin(a), 0.0), 0.013, M["oak"], verts=8)

use_option("freed:nook")  # reading nook in the alcove
item("armchair")
copy_tree("366 Armchair", "Freed Nook Armchair", (0.42, 2.20, 0), 180)
item("floor lamp")
for k in range(3):
    a = k * 2 * math.pi / 3 + 0.5
    rod(f"Freed Nook Lamp Leg {k}", (0.18, 2.66, 1.15), (0.18 + 0.15 * math.cos(a), 2.66 + 0.15 * math.sin(a), 0.0), 0.011, M["walnut"], verts=8)
cyl("Freed Nook Lamp Shade", 0.18, 2.66, 1.28, 1.56, 0.20, M["linen_shade"], verts=32, caps=False)
rod("Freed Nook Lamp Stem", (0.18, 2.66, 1.10), (0.18, 2.66, 1.30), 0.008, M["brass"], verts=8)
light_anchor("Light Freed Nook", (0.18, 2.66, 1.40), "floor")
item("shelf")
box("Freed Nook Shelf", 0.0, 0.20, FY0 + 0.15, FY0 + 0.75, 1.48, 1.51, M["oak"])
books_y("Freed Nook", 0.02, 0.18, FY0 + 0.18, FY0 + 0.60, 1.51)
potted("Freed Nook Pot", 0.10, FY0 + 0.68, 1.51, 0.05, M["ceramic"])

use_option("freed:plants")  # a cluster of big plants
item("fig")
cyl("Freed Fig Pot", 0.25, 1.95, 0.0, 0.34, 0.17, M["terracotta"], r2=0.14, verts=24)
rod("Freed Fig Trunk", (0.25, 1.95, 0.30), (0.27, 1.96, 1.55), 0.016, M["walnut"], verts=8)
for k in range(16):
    t = k / 15
    a = k * 2.3
    sphere(f"Freed Fig Leaf {k}", (0.27 + 0.18 * math.cos(a), 1.96 + 0.18 * math.sin(a), 0.95 + 0.65 * t), 0.09, M["leaf"],
           scale=(0.8, 1.0, 0.12), rot=(0.3, 0.6, a))
item("snake plant")
cyl("Freed Snake Pot", 0.25, 2.38, 0.0, 0.28, 0.14, M["ceramic"], verts=24)
for k in range(9):
    a = k * 0.7
    rod(f"Freed Snake Leaf {k}", (0.25 + 0.05 * math.cos(a), 2.38 + 0.05 * math.sin(a), 0.26),
        (0.25 + 0.10 * math.cos(a), 2.38 + 0.10 * math.sin(a), 0.70 + 0.18 * (k % 3)), 0.02, lime_green, r2=0.004, verts=6)
item("fern")
cyl("Freed Fern Stand", 0.28, 2.64, 0.0, 0.45, 0.10, M["walnut"], verts=16)
cyl("Freed Fern Pot", 0.28, 2.64, 0.45, 0.65, 0.12, M["ceramic"], verts=24)
for k in range(12):
    a = k * 0.52
    sphere(f"Freed Fern Frond {k}", (0.28 + 0.16 * math.cos(a), 2.64 + 0.16 * math.sin(a), 0.68), 0.12, M["leaf"],
           scale=(1.0, 0.3, 0.08), rot=(0.0, 0.4, a))

# ================================================================ opposite the desk: bean bag set
use_piece("beanbag")  # big corduroy bean bag, a pouf table, a floor lamp and a book basket
item("bean bag")
cord = mat("Corduroy Olive", "#6b6a3e", rough=1.0)
sphere("Opp Beanbag", (W - 0.52, 0.85, 0.30), 0.50, cord, scale=(1.0, 1.0, 0.62))
sphere("Opp Beanbag Dent", (W - 0.62, 0.80, 0.52), 0.30, cord, scale=(1.0, 1.0, 0.35))
item("pouf")
cyl("Opp Beanbag Pouf", W - 0.32, 1.50, 0.0, 0.36, 0.20, cognac, verts=24)
box("Opp Beanbag Tray", W - 0.42, W - 0.22, 1.40, 1.60, 0.36, 0.38, M["walnut"])
cyl("Opp Beanbag Mug", W - 0.36, 1.46, 0.38, 0.47, 0.04, M["p_mustard"])
item("floor lamp")
cyl("Opp Beanbag Lamp Base", W - 0.15, 0.30, 0.0, 0.03, 0.12, M["black"])
rod("Opp Beanbag Lamp Pole", (W - 0.15, 0.30, 0.03), (W - 0.15, 0.30, 1.40), 0.01, M["black"], verts=8)
cyl("Opp Beanbag Lamp Shade", W - 0.15, 0.30, 1.36, 1.58, 0.18, M["linen_shade"], verts=32, caps=False)
light_anchor("Light Opp Beanbag", (W - 0.15, 0.30, 1.44), "floor")
item("basket")
cyl("Opp Beanbag Basket", W - 0.20, 1.10, 0.0, 0.30, 0.15, rattan, verts=20)
for k in range(4):
    box(f"Opp Beanbag Book {k}", W - 0.28, W - 0.12, 1.02 + k * 0.035, 1.05 + k * 0.035, 0.20, 0.42, random.choice(BOOKS))
OPP_GROUPS["beanbag"] = (W - 0.40, 0.95)

# ================================================================ super long desk (only once the wardrobe is gone)
use_option("desk:long")  # walnut worktop along the whole west wall, three leg frames
desk_frame("Desk Long", 0.0, 0.70, 0.02, 2.76, M["walnut"], M["black"], (0.18, 1.42, 2.60))
box("Desk Long Cable Tray", 0.10, 0.30, 0.40, 2.40, DZ - 0.12, DZ - 0.10, M["black"])
# A second, analogue end of the desk: lamp, books, plant, a sketchbook
cyl("Desk Long Lamp Base", 0.12, 2.55, DZ, DZ + 0.03, 0.07, M["black"], verts=24)
rod("Desk Long Lamp Arm", (0.12, 2.55, DZ + 0.03), (0.22, 2.40, DZ + 0.42), 0.008, M["black"], verts=8)
rod("Desk Long Lamp Shade", (0.22, 2.40, DZ + 0.42), (0.30, 2.30, DZ + 0.30), 0.03, M["black"], r2=0.075, verts=16)
light_anchor("Light Desk Long", (0.30, 2.30, DZ + 0.28), "desk")
for k in range(4):
    box(f"Desk Long Book {k}", 0.06 + k * 0.004, 0.30 - k * 0.01, 2.00, 2.22 - k * 0.015, DZ + k * 0.035, DZ + (k + 1) * 0.035 - 0.003, random.choice(BOOKS))
potted("Desk Long Pot", 0.14, 1.80, DZ, 0.07, M["terracotta"], leaves=8)
box("Desk Long Sketchbook", 0.30, 0.55, 2.20, 2.55, DZ, DZ + 0.012, M["p_cream"])
rod("Desk Long Pencil", (0.42, 2.25, DZ + 0.017), (0.50, 2.45, DZ + 0.017), 0.004, M["p_mustard"], verts=6)

# ================================================================ 130 cm desk (makes room between desk and wardrobe)
use_option("desk:short")
desk_frame("Desk Short", 0.0, 0.70, 0.10, 1.40, M["walnut"], M["black"], (0.18, 1.10))
# The PC moves under the shorter desk; it only shows while the PC slot is "on the floor"
hide_with(["PC Tower", "PC Front Vent"], "desk:short")
pcs = box("Desk Short PC", 0.06, 0.52, 1.15, 1.29, 0.0, 0.46, bpy.data.materials["PC Case"], bevel=0.005)
pcs["slotBase"] = "pc"

# ================================================================ between the desk and the wardrobe (layout A)
# Thin ones fit the 16 cm gap; tower, plant and folding screen need the 130 cm desk.
reeded_glass = mat("Reeded Glass", "#dfe8e6", rough=0.35)
cord_mat = mat("Cotton Cord", "#e8dfcc", rough=1.0)
zone = mat("Desk Zone Paint", "#a65a3a", rough=0.85)
GY = 1.58  # middle of the 16 cm gap

use_option("between:fin")  # a single floor-to-ceiling oak fin
box("Between Fin", 0.0, 0.66, GY - 0.012, GY + 0.012, 0.0, H, M["oak"])

use_option("between:slats")  # see-through slatted screen
for k in range(15):
    x = 0.02 + k * 0.045
    box(f"Between Slat {k}", x, x + 0.025, GY - 0.015, GY + 0.015, 0.0, H, M["oak"])
box("Between Slat Rail", 0.0, 0.68, GY - 0.02, GY + 0.02, H - 0.04, H, M["oak"])

use_option("between:glass")  # reeded glass panel in an oak frame
box("Between Glass Frame Top", 0.0, 0.66, GY - 0.015, GY + 0.015, 2.02, 2.06, M["oak"])
box("Between Glass Frame Front", 0.62, 0.66, GY - 0.015, GY + 0.015, 0.0, 2.06, M["oak"])
box("Between Glass Frame Wall", 0.0, 0.03, GY - 0.015, GY + 0.015, 0.0, 2.06, M["oak"])
box("Between Glass Pane", 0.03, 0.62, GY - 0.006, GY + 0.006, 0.0, 2.02, reeded_glass)
for k in range(12):
    x = 0.06 + k * 0.047
    box(f"Between Glass Reed {k}", x, x + 0.006, GY - 0.008, GY + 0.008, 0.0, 2.02, mat("Reed Line", "#f2f6f5", rough=0.3))

use_option("between:felt")  # felt screen clamped to the desk end
box("Between Felt", 0.02, 0.68, 1.505, 1.525, 0.42, 1.30, felt_green, bevel=0.01)
for k, z in enumerate((0.66, 0.78)):
    box(f"Between Felt Clamp {k}", 0.30, 0.38, 1.48, 1.53, z, z + 0.04, M["black"])

use_option("between:pinboard")  # cork on the wardrobe's side
box("Between Pinboard", 0.02, 0.58, 1.646, 1.666, 0.80, 2.00, cork)
for k in range(8):
    x = 0.06 + (k % 4) * 0.13 + random.uniform(-0.02, 0.02)
    z = 1.00 + (k // 4) * 0.45 + random.uniform(-0.05, 0.05)
    box(f"Between Pinboard Note {k}", x, x + random.uniform(0.08, 0.14), 1.644, 1.646, z, z + random.uniform(0.10, 0.18),
        random.choice([M["p_cream"], M["p_mustard"], M["p_teal"], M["book3"]]))

use_option("between:cords")  # cotton cord curtain from a ceiling batten
box("Between Cord Batten", 0.0, 0.68, GY - 0.02, GY + 0.02, H - 0.03, H, M["oak"])
for k in range(22):
    x = 0.02 + k * 0.03
    rod(f"Between Cord {k}", (x, GY, H - 0.03), (x, GY + 0.004 * ((k % 3) - 1), 0.02), 0.003, cord_mat, verts=4)

use_option("between:paint")  # paint the desk niche a different colour, oak strip at the edge
box("Between Zone Paint", 0.0005, 0.003, 0.0, 1.52, 0.0, H, zone)
box("Between Zone Strip", 0.0, 0.015, 1.52, 1.545, 0.0, H, M["oak"])

use_option("between:tower")  # slim open shelf tower (with the 130 cm desk)
TY0, TY1 = 1.42, 1.65
for k, (x, y) in enumerate(((0.01, TY0), (0.62, TY0), (0.01, TY1 - 0.02), (0.62, TY1 - 0.02))):
    box(f"Between Tower Post {k}", x, x + 0.02, y, y + 0.02, 0.0, 1.85, M["walnut"])
for j, z in enumerate((0.05, 0.42, 0.79, 1.16, 1.53, 1.83)):
    box(f"Between Tower Shelf {j}", 0.01, 0.64, TY0, TY1, z, z + 0.02, M["walnut"])
cyl("Between Tower Basket", 0.33, (TY0 + TY1) / 2, 0.07, 0.33, 0.10, rattan, verts=20)
for j, z in enumerate((0.44, 1.18)):
    for k in range(8):
        x = 0.06 + k * 0.035
        box(f"Between Tower Book {j}{k}", x, x + 0.03, TY0 + 0.02, TY1 - 0.03, z, z + random.uniform(0.20, 0.27), random.choice(BOOKS))
potted("Between Tower Pot", 0.33, (TY0 + TY1) / 2, 0.81, 0.07, M["terracotta"], leaves=8)
sphere("Between Tower Vase", (0.45, (TY0 + TY1) / 2, 1.62), 0.06, porcelain, scale=(0.8, 0.8, 1.4))
potted("Between Tower Top Pot", 0.30, (TY0 + TY1) / 2, 1.85, 0.06, M["ceramic"], leaves=9)

use_option("between:plant")  # trough of snake plants (with the 130 cm desk)
box("Between Trough", 0.06, 0.62, 1.44, 1.63, 0.0, 0.42, M["ceramic"], bevel=0.01)
for k in range(16):
    x = 0.10 + (k % 8) * 0.065
    y = 1.49 + (k // 8) * 0.09
    rod(f"Between Snake {k}", (x, y, 0.40), (x + random.uniform(-0.04, 0.04), y + random.uniform(-0.03, 0.03), random.uniform(1.1, 1.75)),
        0.022, lime_green, r2=0.004, verts=6)

use_option("between:folding")  # three-panel oak and cane folding screen (with the 130 cm desk)
for k, (x, a) in enumerate(((0.12, 25), (0.34, -25), (0.56, 25))):
    p_ = empty(f"Between Fold Pivot {k}", (x, 1.53, 0), rot_z=math.radians(a))
    box(f"Between Fold Frame {k}", -0.11, 0.11, -0.012, 0.012, 0.02, 1.72, M["oak"], parent=p_)
    box(f"Between Fold Cane {k}", -0.09, 0.09, -0.014, 0.014, 0.12, 1.62, cane, parent=p_)

# ================================================================ Eames lounge chair + ottoman (opposite the desk, or the door corner)
leather = M["leather"]


def eames_set(prefix, chair_xy, ottoman_xy, lamp):
    """Chair faces -x (into the room), back square to the east wall; the reclined back
    reaches ~0.6 m behind the chair's centre, so keep the centre at least that far off the wall."""
    item("chair")
    ec = empty(f"{prefix} Lounge", (*chair_xy, 0))
    for k in range(5):
        a = k * 2 * math.pi / 5
        rod(f"{prefix} Leg {k}", (0, 0, 0.12), (0.34 * math.cos(a), 0.34 * math.sin(a), 0.03), 0.018, M["alu"], verts=10, parent=ec)
        sphere(f"{prefix} Glide {k}", (0.34 * math.cos(a), 0.34 * math.sin(a), 0.02), 0.02, M["black"], parent=ec)
    cyl(f"{prefix} Column", 0, 0, 0.10, 0.30, 0.035, M["black"], parent=ec)
    seat = empty(f"{prefix} Seat Pivot", (0, 0, 0.32), parent=ec)
    seat.rotation_euler = (0, math.radians(8), 0)  # front edge a little higher, like the real chair
    box(f"{prefix} Seat Shell", -0.32, 0.24, -0.38, 0.38, 0.0, 0.05, M["walnut"], bevel=0.02, parent=seat)
    box(f"{prefix} Seat Cushion", -0.31, 0.20, -0.34, 0.34, 0.05, 0.16, leather, bevel=0.04, parent=seat)
    for s_, yy in (("L", -0.41), ("R", 0.41)):
        box(f"{prefix} Arm {s_}", -0.26, 0.14, yy - 0.04, yy + 0.04, 0.22, 0.27, leather, bevel=0.02, parent=seat)
        box(f"{prefix} Arm Support {s_}", -0.02, 0.14, yy - 0.012, yy + 0.012, 0.03, 0.22, M["alu"], parent=seat)
    back = empty(f"{prefix} Back Pivot", (0.22, 0, 0.42), parent=ec)
    back.rotation_euler = (0, math.radians(28), 0)  # leans back
    box(f"{prefix} Back Shell", 0.0, 0.03, -0.37, 0.37, 0.0, 0.42, M["walnut"], bevel=0.015, parent=back)
    box(f"{prefix} Back Cushion", -0.11, 0.0, -0.33, 0.33, 0.02, 0.40, leather, bevel=0.04, parent=back)
    box(f"{prefix} Head Shell", 0.0, 0.03, -0.31, 0.31, 0.45, 0.70, M["walnut"], bevel=0.015, parent=back)
    box(f"{prefix} Head Cushion", -0.10, 0.0, -0.28, 0.28, 0.47, 0.68, leather, bevel=0.04, parent=back)
    box(f"{prefix} Back Spine", 0.03, 0.05, -0.04, 0.04, 0.10, 0.60, M["alu"], parent=back)
    item("ottoman")
    eo = empty(f"{prefix} Ottoman", (*ottoman_xy, 0))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        rod(f"{prefix} Ottoman Leg {k}", (0, 0, 0.12), (0.28 * math.cos(a), 0.28 * math.sin(a), 0.03), 0.016, M["alu"], verts=10, parent=eo)
    cyl(f"{prefix} Ottoman Column", 0, 0, 0.10, 0.27, 0.03, M["black"], parent=eo)
    box(f"{prefix} Ottoman Shell", -0.28, 0.28, -0.32, 0.32, 0.27, 0.31, M["walnut"], bevel=0.02, parent=eo)
    box(f"{prefix} Ottoman Cushion", -0.26, 0.26, -0.29, 0.29, 0.31, 0.42, leather, bevel=0.04, parent=eo)
    # Slim floor lamp with a dome shade, arcing over the chair
    item("floor lamp")
    (bx, by), (hx, hy) = lamp
    cyl(f"{prefix} Lamp Base", bx, by, 0.0, 0.03, 0.12, M["black"], verts=24)
    rod(f"{prefix} Lamp Pole", (bx, by, 0.03), (bx, by, 1.45), 0.01, M["black"], verts=8)
    rod(f"{prefix} Lamp Arm", (bx, by, 1.45), (hx, hy, 1.50), 0.008, M["black"], verts=8)
    cyl(f"{prefix} Lamp Dome", hx, hy, 1.40, 1.50, 0.15, M["black"], r2=0.05, verts=24)
    light_anchor(f"Light {prefix} Lamp", (hx, hy, 1.38), "floor")


use_piece("eames")  # opposite the desk; ottoman kept clear of the desk chair
eames_set("Eames", (W - 0.62, 1.35), (1.58, 1.40), ((W - 0.18, 0.55), (W - 0.45, 0.85)))
OPP_GROUPS["eames"] = (W - 0.55, 1.05)

use_option("corner:eames")  # in the door corner, square to the east wall, ottoman clear of the door swing
eames_set("Corner Eames", (W - 0.62, 2.45), (1.58, 2.40), ((W - 0.15, 3.15), (W - 0.42, 2.85)))
