"""Adds every restyle variant to room.blend and exports the viewer model.

Run after build_room.py:
  blender --background room-model/room.blend --python room-model/restyle_export.py

The room is split into slots (ceiling light, desk, chair, wardrobe, ...). Each
variant lives in its own collection named "slot:variant"; add-ons are "x:name".
catalog.py holds the cheap low-poly models for most of them. Objects carry glTF
extras so the web viewer can switch them:
  opt       - "slot:variant" or "x:name" the object belongs to
  slotBase  - slot whose default ("today") this base object is
  hideWith  - variant or add-on that replaces this base object
  side      - wall side (S/N/E/W/C) for dollhouse cut-away
  light     - empty marking a light position for the viewer
Writes room-model/room_options.blend and room-model/viewer/room.json (a gzipped GLB
wrapped in JSON; artifacts serve .json but not .glb).
"""
import math
import os

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
W, D, H = 2.762, 3.336, 2.70
DZ = 0.74  # desk height


# ---------------------------------------------------------------- helpers
def srgb(hexstr):
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def material(name, color, rough=0.6, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = srgb(color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = srgb(emit)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    return m


CURRENT = {"coll": None, "opt": None}


def use_option(opt):
    c = bpy.data.collections.new(opt)
    bpy.context.scene.collection.children.link(c)
    CURRENT["coll"] = c
    CURRENT["opt"] = opt


def _adopt(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    CURRENT["coll"].objects.link(o)
    if CURRENT["opt"]:
        o["opt"] = CURRENT["opt"]
    return o


def box(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    if parent:
        o.parent = parent
    return _adopt(o)


def cyl(name, x, y, z0, z1, r, mat, verts=24, r2=None, parent=None, caps=True):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0,
                                            location=(x, y, (z0 + z1) / 2),
                                            end_fill_type="NGON" if caps else "NOTHING")
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return _adopt(o)


def rod(name, p1, p2, r, mat, r2=None, verts=12, parent=None):
    """Cylinder (or cone when r2 is given) from p1 to p2."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(p1 + p2) / 2)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=d.length, location=(p1 + p2) / 2)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return _adopt(o)


def sphere(name, loc, r, mat, scale=(1, 1, 1), parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=20, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    o.rotation_euler = rot
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return _adopt(o)


def empty(name, loc, rot_z=0.0, parent=None):
    o = bpy.data.objects.new(name, None)
    o.location = loc
    o.rotation_euler = (0, 0, rot_z)
    CURRENT["coll"].objects.link(o)
    if CURRENT["opt"]:
        o["opt"] = CURRENT["opt"]
    if parent:
        o.parent = parent
    return o


def light_anchor(name, loc, kind, parent=None):
    """Empty the viewer turns into a light. kind: ceiling/desk/bulb/pendant/mushroom/floor."""
    o = empty(name, loc, parent=parent)
    o["light"] = kind
    return o


def slot_base(names, slot):
    for n in names:
        o = bpy.data.objects[n]
        for x in [o, *o.children_recursive]:
            x["slotBase"] = slot


def hide_with(names, opt):
    for n in names:
        o = bpy.data.objects[n]
        for x in [o, *o.children_recursive]:
            x["hideWith"] = opt


def curtain(name, x0, x1, y, z0, z1, folds, amp, mat):
    n = 64
    verts, faces = [], []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + t * (x1 - x0)
        yy = y + amp * math.sin(t * folds * 2 * math.pi)
        verts += [(x, yy, z0), (x, yy, z1)]
    for i in range(n - 1):
        a = 2 * i
        faces.append((a, a + 2, a + 3, a + 1))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat)
    CURRENT["coll"].objects.link(o)
    if CURRENT["opt"]:
        o["opt"] = CURRENT["opt"]
    return o


# ---------------------------------------------------------------- materials
M = {
    "walnut": material("Walnut", "#6b4429", rough=0.45),
    "oak": material("Light Oak", "#b98a55", rough=0.5),
    "black": material("Matte Black", "#1a1a1a", rough=0.5),
    "brass": material("Brass", "#b8913f", rough=0.3, metal=1.0),
    "alu": material("Polished Aluminium", "#d0d0d0", rough=0.22, metal=1.0),
    "leather": material("Black Leather", "#161616", rough=0.45),
    "rug_rust": material("Rug Rust", "#a4532c", rough=1.0),
    "rug_mustard": material("Rug Mustard", "#d29a35", rough=1.0),
    "rug_cream": material("Rug Cream", "#e9dcc3", rough=1.0),
    "rug_ink": material("Rug Ink", "#2a2a2a", rough=1.0),
    "p_cream": material("Poster Cream", "#efe6d2", rough=0.8),
    "p_red": material("Poster Red", "#c9412f", rough=0.8),
    "p_black": material("Poster Black", "#1b1b1b", rough=0.8),
    "p_mustard": material("Poster Mustard", "#d6a23a", rough=0.8),
    "p_teal": material("Poster Teal", "#2f6f6a", rough=0.8),
    "leaf": material("Rubber Plant Leaf", "#26401f", rough=0.3),
    "terracotta": material("Terracotta", "#b8613d", rough=0.8),
    "armchair": material("Armchair Mustard Wool", "#b8862f", rough=1.0),
    "linen_shade": material("Linen Shade", "#efe3c8", rough=0.9, emit="#ffd9a0", emit_strength=1.2),
    "opal": material("Opal Glass", "#fff6e8", rough=0.2, emit="#ffe2b8", emit_strength=4.0),
    "mushroom": material("Mushroom Lamp", "#efe4d0", rough=0.3, emit="#ffd8a0", emit_strength=0.8),
    "curtain": material("Linen Curtain", "#d9ccb4", rough=0.95),
    "reeded": material("Reeded Oak", "#b98950", rough=0.5),
    "book1": material("Book Rust", "#9c4a2a", rough=0.8),
    "book2": material("Book Olive", "#6d6a3a", rough=0.8),
    "book3": material("Book Cream", "#e3d6bb", rough=0.8),
    "book4": material("Book Navy", "#2c3a52", rough=0.8),
    "ceramic": material("Ceramic White", "#ece6da", rough=0.3),
}
for m in M.values():
    m.use_backface_culling = False

# ---------------------------------------------------------------- base light anchors
use_option("base_lights")
light_anchor("Light Ceiling", (W / 2, D / 2, H - 0.10), "ceiling")
light_anchor("Light Desk Arm", (0.22, 0.30, DZ + 0.38), "desk")
light_anchor("Light Bulb", (0.20, 0.42, DZ + 0.14), "bulb")
for o in list(CURRENT["coll"].objects):
    del o["opt"]
slot_base(["Light Desk Arm", "Light Bulb"], "desklamp")

# ---------------------------------------------------------------- 1. globe pendant + mushroom lamp (replace plafon, arm and bulb lamps)
use_option("light:globe")
slot_base(["Lamp Clamp", "Lamp Pole", "Lamp Bar", "Lamp Head", "Bulb Base", "Bulb Stem", "Bulb Glass"], "desklamp")
slot_base(["Plafon Body", "Plafon Diffuser"], "light")
cx, cy = W / 2, D / 2
cyl("Pendant Cord", cx, cy, 2.42, H, 0.004, M["black"], verts=8)
cyl("Pendant Cap", cx, cy, 2.40, 2.44, 0.035, M["brass"])
sphere("Pendant Globe", (cx, cy, 2.24), 0.19, M["opal"])
light_anchor("Light Pendant", (cx, cy, 2.24), "pendant")
# Mushroom lamp on the desk (replaces arm + bulb lamps)
use_option("desklamp:mushroom")
mx, my = 0.22, 0.32
cyl("Mushroom Base", mx, my, DZ, DZ + 0.02, 0.075, M["mushroom"], verts=32)
cyl("Mushroom Stem", mx, my, DZ + 0.02, DZ + 0.24, 0.025, M["mushroom"], r2=0.018)
sphere("Mushroom Cap", (mx, my, DZ + 0.25), 0.15, M["mushroom"], scale=(1, 1, 0.55))
light_anchor("Light Mushroom", (mx, my, DZ + 0.20), "mushroom")

# ---------------------------------------------------------------- 2. rug
use_option("rug:geo")
rx0, rx1, ry0, ry1 = 0.71, 2.31, 0.40, 2.70
box("Rug Base", rx0, rx1, ry0, ry1, 0.0, 0.008, M["rug_rust"])
b = 0.09
for nm, a in (("S", (rx0 + b, rx1 - b, ry0 + b, ry0 + b + 0.04)),
              ("N", (rx0 + b, rx1 - b, ry1 - b - 0.04, ry1 - b)),
              ("W", (rx0 + b, rx0 + b + 0.04, ry0 + b, ry1 - b)),
              ("E", (rx1 - b - 0.04, rx1 - b, ry0 + b, ry1 - b))):
    box(f"Rug Border {nm}", *a, 0.008, 0.010, M["rug_mustard"])
for i, (yy, mat) in enumerate(((0.95, M["rug_cream"]), (1.55, M["rug_mustard"]), (2.15, M["rug_cream"]))):
    cyl(f"Rug Disc {i}", (rx0 + rx1) / 2 + (0.25 if i % 2 else -0.25), yy, 0.008, 0.011, 0.22, mat, verts=48)
for i in range(5):
    x = rx0 + 0.30 + i * 0.25
    box(f"Rug Line {i}", x, x + 0.015, ry0 + 0.25, ry1 - 0.25, 0.008, 0.0105, M["rug_ink"])

# ---------------------------------------------------------------- 3. posters
use_option("art:posters")


def poster_west(name, y0, y1, z0, z1, bg, shapes):
    box(f"{name} Frame", 0.0, 0.022, y0, y1, z0, z1, M["oak"])
    box(f"{name} Paper", 0.022, 0.024, y0 + 0.03, y1 - 0.03, z0 + 0.03, z1 - 0.03, bg)
    for s in shapes:
        s()


py0, py1, pz0, pz1 = 1.00, 1.40, 1.32, 1.86
poster_west("Poster A", py0, py1, pz0, pz1, M["p_cream"], [
    lambda: rod("Poster A Sun", (0.024, 1.20, 1.66), (0.027, 1.20, 1.66), 0.11, M["p_red"], verts=40),
    lambda: box("Poster A Bar", 0.024, 0.027, 1.06, 1.34, 1.43, 1.47, M["p_black"]),
    lambda: box("Poster A Bar2", 0.024, 0.027, 1.06, 1.24, 1.39, 1.41, M["p_black"]),
])
# Poster B on the shaft's room-facing side (x = 0.52)
sx = 0.52
box("Poster B Frame", sx, sx + 0.022, D - 0.48, D - 0.06, 1.22, 1.84, M["oak"])
box("Poster B Paper", sx + 0.022, sx + 0.024, D - 0.45, D - 0.09, 1.25, 1.81, M["p_mustard"])
rod("Poster B Circle", (sx + 0.024, D - 0.27, 1.62), (sx + 0.027, D - 0.27, 1.62), 0.12, M["p_teal"], verts=40)
rod("Poster B Tri", (sx + 0.024, D - 0.27, 1.40), (sx + 0.027, D - 0.27, 1.40), 0.13, M["p_black"], verts=3)

# ---------------------------------------------------------------- 4. plant + tidy PC
use_option("pc:caddy")
slot_base(["PC Tower", "PC Front Vent"], "pc")
box("PC Tower Tidy", 0.06, 0.52, 1.22, 1.36, 0.06, 0.52, bpy.data.materials["PC Case"], bevel=0.005)
box("PC Caddy", 0.05, 0.53, 1.21, 1.37, 0.02, 0.06, M["walnut"])
for i, (x, y) in enumerate(((0.08, 1.23), (0.50, 1.23), (0.08, 1.35), (0.50, 1.35))):
    sphere(f"PC Caddy Wheel {i}", (x, y, 0.015), 0.015, M["black"])
use_option("plant:rubber")
px, py = 1.95, 3.08
for i in range(3):
    a = i * 2 * math.pi / 3 + 0.3
    rod(f"Plant Stand Leg {i}", (px + 0.12 * math.cos(a), py + 0.12 * math.sin(a), 0.30),
        (px + 0.20 * math.cos(a), py + 0.20 * math.sin(a), 0.0), 0.014, M["walnut"], r2=0.009)
cyl("Plant Stand Ring", px, py, 0.27, 0.30, 0.16, M["walnut"], verts=32)
cyl("Plant Pot", px, py, 0.30, 0.58, 0.17, M["terracotta"], r2=0.14, verts=32)
cyl("Plant Soil", px, py, 0.56, 0.575, 0.15, M["black"], verts=24)
rod("Plant Trunk", (px, py, 0.56), (px + 0.03, py - 0.02, 1.75), 0.018, M["walnut"], verts=8)
for i in range(22):
    t = i / 21
    z = 0.80 + t * 0.95
    a = i * 2.4
    r = 0.20 - 0.06 * t
    cxl, cyl_ = px + 0.03 * t + r * math.cos(a), py - 0.02 * t + r * math.sin(a)
    sphere(f"Plant Leaf {i}", (cxl, cyl_, z), 0.09, M["leaf"], scale=(1.0, 0.45, 0.12),
           rot=(math.radians(-25), math.radians(15), a))

# ---------------------------------------------------------------- 5. walnut desk top + black legs
use_option("desk:walnut")
desk_parts = [o.name for o in bpy.data.objects
              if o.name.startswith(("Desk Top", "Desk Foot", "Desk Leg", "Desk Bracket", "Desk Crossbar"))
              and "opt" not in o]
slot_base(desk_parts, "desk")
box("Desk Top Walnut", 0.0, 0.70, 0.10, 1.50, DZ - 0.028, DZ, M["walnut"], bevel=0.012)
for side, y in (("S", 0.18), ("N", 1.42)):
    box(f"Desk Foot Black {side}", 0.04, 0.66, y - 0.03, y + 0.03, 0, 0.03, M["black"], bevel=0.01)
    box(f"Desk Leg Black {side}", 0.32, 0.38, y - 0.03, y + 0.03, 0.03, DZ - 0.07, M["black"])
    box(f"Desk Bracket Black {side}", 0.06, 0.64, y - 0.025, y + 0.025, DZ - 0.07, DZ - 0.028, M["black"])
box("Desk Crossbar Black", 0.33, 0.37, 0.18, 1.42, DZ - 0.10, DZ - 0.06, M["black"])
box("Cable Tray", 0.10, 0.30, 0.40, 1.20, DZ - 0.12, DZ - 0.10, M["black"])

# ---------------------------------------------------------------- 6. wall shelving above the desk
use_option("shelf:string")
sy0, sy1 = 0.15, 0.95
for i, y in enumerate((sy0 + 0.03, sy1 - 0.03)):
    box(f"Shelf Rail {i}", 0.0, 0.012, y - 0.012, y + 0.012, 1.18, 2.02, M["black"])
    for j, z in enumerate((1.25, 1.55, 1.85)):
        box(f"Shelf Bracket {i}{j}", 0.0, 0.20, y - 0.006, y + 0.006, z - 0.03, z - 0.02, M["black"])
for j, z in enumerate((1.25, 1.55, 1.85)):
    box(f"Shelf {j}", 0.0, 0.22, sy0, sy1, z - 0.02, z, M["walnut"])
books = [M["book1"], M["book2"], M["book3"], M["book4"]]
y = sy0 + 0.06
for k in range(9):
    w = 0.025 + (k % 3) * 0.008
    h = 0.20 + (k * 37 % 5) * 0.02
    box(f"Book Low {k}", 0.02, 0.18, y, y + w, 1.25, 1.25 + h, books[k % 4])
    y += w + 0.002
cyl("Vase Low", 0.11, 0.82, 1.25, 1.43, 0.05, M["ceramic"], r2=0.03)
y = sy0 + 0.40
for k in range(6):
    w = 0.03 + (k % 2) * 0.01
    box(f"Book Mid {k}", 0.02, 0.17, y, y + w, 1.55, 1.55 + 0.17 + (k % 3) * 0.02, books[(k + 2) % 4])
    y += w + 0.002
sphere("Ceramic Ball", (0.11, 0.30, 1.61), 0.055, M["p_teal"])
box("Record", 0.03, 0.035, 0.22, 0.52, 1.85, 2.15, M["p_red"])
cyl("Vase Top", 0.11, 0.75, 1.85, 2.02, 0.04, M["terracotta"], r2=0.05)

# ---------------------------------------------------------------- 7. linen curtains on a ceiling track
use_option("window:linen")
box("Curtain Track", 0.72, 2.0, 0.34, 0.38, H - 0.03, H, M["black"])
curtain("Curtain Left", 0.72, 1.04, 0.36, 0.02, H - 0.03, 5, 0.035, M["curtain"])
curtain("Curtain Right", 1.52, 1.96, 0.36, 0.02, H - 0.03, 7, 0.035, M["curtain"])

# ---------------------------------------------------------------- 8. reading corner (366 armchair)
use_option("corner:reading")
arm = empty("366 Armchair", (2.20, 2.45, 0), rot_z=math.radians(20))
# Local frame: front at -x. Back legs rise to a pivot and continue as posts
# tilted 16 degrees back; the back cushion and its rails ride on those posts.
BACK_X, BACK_Z, TILT = 0.20, 0.42, math.radians(16)
box("Armchair Seat", -0.28, 0.19, -0.27, 0.27, 0.33, 0.45, M["armchair"], bevel=0.035, parent=arm)
backp = empty("Armchair Back Pivot", (BACK_X, 0, BACK_Z), parent=arm)
backp.rotation_euler = (0, TILT, 0)  # +y rotation leans local z toward +x (backwards)
box("Armchair Back", -0.10, -0.02, -0.26, 0.26, 0.06, 0.52, M["armchair"], bevel=0.035, parent=backp)
box("Armchair Back Rail Top", -0.015, 0.015, -0.30, 0.30, 0.46, 0.50, M["walnut"], parent=backp)
box("Armchair Back Rail Low", -0.015, 0.015, -0.30, 0.30, 0.06, 0.10, M["walnut"], parent=backp)
post_top = 0.52
arm_z = 0.60
post_x_at_arm = BACK_X + math.tan(TILT) * (arm_z - BACK_Z)
for s, yy in (("L", -0.31), ("R", 0.31)):
    box(f"Armchair Back Post {s}", -0.015, 0.015, yy - 0.016, yy + 0.016, 0.0, post_top, M["walnut"], parent=backp)
    rod(f"Armchair Back Leg {s}", (BACK_X, yy, BACK_Z), (BACK_X + 0.12, yy * 1.05, 0.0), 0.019, M["walnut"], r2=0.013, parent=arm)
    rod(f"Armchair Front Leg {s}", (-0.25, yy, arm_z), (-0.29, yy * 1.05, 0.0), 0.019, M["walnut"], r2=0.013, parent=arm)
    box(f"Armchair Arm {s}", -0.31, post_x_at_arm + 0.02, yy - 0.025, yy + 0.025, arm_z, arm_z + 0.03, M["walnut"], bevel=0.008, parent=arm)
    box(f"Armchair Rail {s}", -0.25, BACK_X, yy - 0.014, yy + 0.014, 0.28, 0.33, M["walnut"], parent=arm)
box("Armchair Front Rail", -0.27, -0.23, -0.31, 0.31, 0.28, 0.33, M["walnut"], parent=arm)
box("Armchair Rear Rail", BACK_X - 0.02, BACK_X + 0.02, -0.31, 0.31, 0.28, 0.33, M["walnut"], parent=arm)
# Tripod floor lamp
lx, ly = 2.50, 3.05
for i in range(3):
    a = i * 2 * math.pi / 3 + 0.5
    rod(f"Floor Lamp Leg {i}", (lx, ly, 1.15), (lx + 0.26 * math.cos(a), ly + 0.26 * math.sin(a), 0.0),
        0.012, M["walnut"])
rod("Floor Lamp Stem", (lx, ly, 1.10), (lx, ly, 1.30), 0.008, M["brass"])
cyl("Floor Lamp Shade", lx, ly, 1.28, 1.58, 0.22, M["linen_shade"], verts=40, caps=False)
light_anchor("Light Floor Lamp", (lx, ly, 1.40), "floor")
# Round side table
tx, ty = 2.50, 1.98
cyl("Side Table Top", tx, ty, 0.50, 0.53, 0.22, M["walnut"], verts=40)
for i in range(3):
    a = i * 2 * math.pi / 3
    rod(f"Side Table Leg {i}", (tx + 0.12 * math.cos(a), ty + 0.12 * math.sin(a), 0.50),
        (tx + 0.19 * math.cos(a), ty + 0.19 * math.sin(a), 0.0), 0.016, M["walnut"], r2=0.01)
cyl("Side Table Mug", tx - 0.05, ty, 0.53, 0.62, 0.04, M["p_mustard"])
box("Side Table Book", tx - 0.02, tx + 0.16, ty - 0.12, ty + 0.02, 0.53, 0.56, M["book4"])
for o in list(CURRENT["coll"].objects):
    if o.name.startswith("Side Table"):
        o["sidetable"] = 1

# ---------------------------------------------------------------- 9. Eames Aluminum Group-style desk chair
use_option("chair:ag")
slot_base(["MARKUS Chair"], "chair")
ch = empty("Aluminium Group Chair", (1.05, 0.75, 0), rot_z=math.radians(40))
for i in range(5):
    a = i * 2 * math.pi / 5
    rod(f"AG Leg {i}", (0, 0, 0.10), (0.33 * math.cos(a), 0.33 * math.sin(a), 0.07), 0.022, M["alu"], parent=ch)
    sphere(f"AG Caster {i}", (0.33 * math.cos(a), 0.33 * math.sin(a), 0.03), 0.028, M["black"], parent=ch)
cyl("AG Hub", 0, 0, 0.07, 0.13, 0.045, M["alu"], parent=ch)
cyl("AG Column", 0, 0, 0.13, 0.42, 0.022, M["black"], parent=ch)
cyl("AG Column Cover", 0, 0, 0.13, 0.30, 0.03, M["alu"], parent=ch)
for s, yy in (("L", -0.235), ("R", 0.235)):
    box(f"AG Seat Rail {s}", -0.25, 0.22, yy - 0.012, yy + 0.012, 0.43, 0.47, M["alu"], bevel=0.008, parent=ch)
box("AG Seat Pad", -0.24, 0.21, -0.222, 0.222, 0.435, 0.465, M["leather"], parent=ch)
for k in range(5):
    x = -0.20 + k * 0.09
    box(f"AG Seat Rib {k}", x - 0.035, x + 0.035, -0.20, 0.20, 0.465, 0.48, M["leather"], bevel=0.008, parent=ch)
agb = empty("AG Back Pivot", (0.22, 0, 0.47), parent=ch)
agb.rotation_euler = (0, math.radians(12), 0)  # lean back, not forward
for s, yy in (("L", -0.235), ("R", 0.235)):
    box(f"AG Back Rail {s}", -0.012, 0.012, yy - 0.012, yy + 0.012, 0.0, 0.58, M["alu"], bevel=0.008, parent=agb)
box("AG Back Pad", -0.005, 0.01, -0.222, 0.222, 0.06, 0.56, M["leather"], parent=agb)
for k in range(5):
    z = 0.12 + k * 0.095
    box(f"AG Back Rib {k}", -0.02, -0.005, -0.20, 0.20, z - 0.038, z + 0.038, M["leather"], bevel=0.008, parent=agb)
for s, yy in (("L", -0.26), ("R", 0.26)):
    rod(f"AG Arm Post {s}", (0.10, yy * 0.92, 0.46), (0.02, yy, 0.65), 0.012, M["alu"], parent=ch)
    box(f"AG Arm Pad {s}", -0.18, 0.08, yy - 0.025, yy + 0.025, 0.65, 0.675, M["leather"], bevel=0.01, parent=ch)

# ---------------------------------------------------------------- 10. reeded oak wardrobe + radiator credenza
use_option("wardrobe:reeded")
slot_base(["Wardrobe Carcass", "Wardrobe Door S", "Wardrobe Door N", "Wardrobe Handle"], "wardrobe")
WD = 0.597
wy_a, wy_b = D - 1.67, D - 0.56
WH = H - 0.003
box("Wardrobe Carcass Oak", 0, WD - 0.02, wy_a, wy_b, 0, WH, M["reeded"])
wmid = (wy_a + wy_b) / 2
for d_, (a, b_) in (("S", (wy_a, wmid - 0.002)), ("N", (wmid + 0.002, wy_b))):
    box(f"Reeded Backer {d_}", WD - 0.02, WD - 0.008, a, b_, 0.005, WH, M["reeded"])
    n = int((b_ - a) / 0.022)
    for i in range(n):
        yy = a + 0.011 + i * (b_ - a) / n
        cyl(f"Reed {d_} {i}", WD - 0.006, yy, 0.005, WH, 0.0105, M["reeded"], verts=10)
box("Wardrobe Pull", WD + 0.004, WD + 0.02, wmid + 0.006, wmid + 0.026, 0.95, 1.15, M["walnut"], bevel=0.004)
# Credenza that boxes in the radiator, doubling as a bench
use_option("x:bench")
c0, c1, cy0, cy1 = 0.74, 1.56, 0.02, 0.32
box("Credenza Top", c0, c1, cy0, cy1 + 0.01, 0.76, 0.79, M["walnut"], bevel=0.006)
box("Credenza Side W", c0, c0 + 0.02, cy0, cy1, 0.10, 0.76, M["oak"])
box("Credenza Side E", c1 - 0.02, c1, cy0, cy1, 0.10, 0.76, M["oak"])
box("Credenza Bottom", c0, c1, cy0, cy1, 0.10, 0.12, M["oak"])
n = int((c1 - c0 - 0.04) / 0.035)
for i in range(n):
    x = c0 + 0.02 + 0.0175 + i * 0.035
    box(f"Credenza Slat {i}", x - 0.01, x + 0.01, cy1 - 0.02, cy1, 0.12, 0.76, M["oak"])
for i, (x, y) in enumerate(((c0 + 0.05, cy0 + 0.05), (c1 - 0.05, cy0 + 0.05), (c0 + 0.05, cy1 - 0.05), (c1 - 0.05, cy1 - 0.05))):
    rod(f"Credenza Leg {i}", (x, y, 0.10), (x + (0.02 if x > 1.1 else -0.02), y + (0.02 if y > 0.2 else 0), 0.0),
        0.02, M["walnut"], r2=0.012)
box("Bench Cushion", c0 + 0.06, c0 + 0.48, cy0 + 0.03, cy1 - 0.02, 0.79, 0.84, M["armchair"], bevel=0.02)

# ---------------------------------------------------------------- pieces for the wall opposite the desk
# Built against the east wall (back at +x). The viewer shows one at a time
# (glTF extra "piece") and moves them with the layout.
M["steel"] = material("Powder Steel", "#232323", rough=0.45, metal=0.6)
M["dried"] = material("Dried Grass", "#c9b48a", rough=0.9)
M["pegboard"] = material("Pegboard", "#34363a", rough=0.6)
M["device"] = material("Device Grey", "#3c3e41", rough=0.4, metal=0.3)
M["device_light"] = material("Device Light", "#c9cbcd", rough=0.4, metal=0.2)
M["scope_screen"] = material("Scope Screen", "#0f2a28", emit="#58d6c8", emit_strength=2.0)
M["psu_screen"] = material("PSU Screen", "#2a120a", emit="#ff7a3d", emit_strength=2.0)
M["spool_a"] = material("Spool Orange", "#e0662c", rough=0.4)
M["spool_b"] = material("Spool Teal", "#2f8a83", rough=0.4)
M["copper"] = material("Copper Wire", "#b8703a", rough=0.3, metal=1.0)
M["glass"] = bpy.data.materials["Glass"]
for k in ("steel", "pegboard"):
    M[k].use_backface_culling = False


def use_piece(piece):
    use_option("opp:" + piece)


def steel_frame(prefix, x0, x1, y0, y1, h, t=0.02):
    for i, (x, y) in enumerate(((x0, y0), (x1 - t, y0), (x0, y1 - t), (x1 - t, y1 - t))):
        box(f"{prefix} Leg {i}", x, x + t, y, y + t, 0, h - 0.03, M["steel"])
    for z, nm in ((0.10, "Low"), (0.50, "Mid"), (h - 0.05, "Top")):
        box(f"{prefix} Rail {nm} F", x0, x0 + t, y0, y1, z, z + t, M["steel"])
        box(f"{prefix} Rail {nm} B", x1 - t, x1, y0, y1, z, z + t, M["steel"])
        box(f"{prefix} Rail {nm} S", x0, x1, y0, y0 + t, z, z + t, M["steel"])
        box(f"{prefix} Rail {nm} N", x0, x1, y1 - t, y1, z, z + t, M["steel"])
    box(f"{prefix} Shelf", x0 + t, x1 - t, y0 + t, y1 - t, 0.12, 0.135, M["steel"])


def framed_print(name, y0, y1, z0, z1, bg, dots):
    box(f"{name} Frame", W - 0.025, W, y0, y1, z0, z1, M["oak"])
    box(f"{name} Paper", W - 0.028, W - 0.025, y0 + 0.04, y1 - 0.04, z0 + 0.04, z1 - 0.04, bg)
    for k, (y, z, r, mat) in enumerate(dots):
        rod(f"{name} Shape {k}", (W - 0.029, y, z), (W - 0.031, y, z), r, mat, verts=40)


def drawer_run(prefix, y0, modules, mw, wall_art):
    """Modular black-steel drawer units with an oak top, 75 cm high, one drawer each.
    Objects of the third module get the extra module3 so the viewer can drop it
    where the wall is too short."""
    kx0, kx1, KH = W - 0.46, W - 0.01, 0.75
    for i in range(modules):
        before = set(CURRENT["coll"].objects)
        a, b_ = y0 + i * mw, y0 + (i + 1) * mw
        steel_frame(f"{prefix} {i}", kx0, kx1, a, b_, KH)
        box(f"{prefix} {i} Top", kx0 - 0.01, kx1, a, b_, KH - 0.03, KH, M["oak"], bevel=0.003)
        box(f"{prefix} {i} Drawer", kx0 + 0.005, kx1 - 0.02, a + 0.025, b_ - 0.025, 0.53, KH - 0.055, M["oak"], bevel=0.003)
        box(f"{prefix} {i} Pull", kx0 - 0.012, kx0 + 0.005, (a + b_) / 2 - 0.07, (a + b_) / 2 + 0.07, 0.60, 0.615, M["steel"])
        c = (a + b_) / 2
        kind = i % 3
        if kind == 0:
            box(f"{prefix} {i} Basket", kx0 + 0.06, kx1 - 0.06, a + 0.07, b_ - 0.07, 0.135, 0.33, M["dried"], bevel=0.02)
            cyl(f"{prefix} {i} Lamp Base", kx0 + 0.22, a + 0.16, KH, KH + 0.18, 0.06, M["ceramic"], r2=0.045)
            sphere(f"{prefix} {i} Lamp Globe", (kx0 + 0.22, a + 0.16, KH + 0.29), 0.11, M["opal"])
            light_anchor(f"Light {prefix} {i}", (kx0 + 0.22, a + 0.16, KH + 0.29), "console")
            cyl(f"{prefix} {i} Vase", kx0 + 0.24, b_ - 0.15, KH, KH + 0.24, 0.07, M["terracotta"], r2=0.04)
            for k in range(7):
                ang = k * 0.9
                rod(f"{prefix} {i} Grass {k}", (kx0 + 0.24, b_ - 0.15, KH + 0.22),
                    (kx0 + 0.24 + 0.12 * math.cos(ang), b_ - 0.15 + 0.12 * math.sin(ang), KH + 0.62 + 0.05 * (k % 3)),
                    0.006, M["dried"], verts=6)
        elif kind == 1:
            for k in range(5):
                box(f"{prefix} {i} Low Book {k}", kx0 + 0.08, kx0 + 0.36, a + 0.10, a + 0.40,
                    0.135 + k * 0.035, 0.135 + (k + 1) * 0.035 - 0.003, [M["book1"], M["book3"], M["book4"], M["book2"], M["book3"]][k])
            for k in range(3):
                box(f"{prefix} {i} Book {k}", kx0 + 0.10 + k * 0.006, kx0 + 0.32 - k * 0.01, a + 0.08, a + 0.28 - k * 0.02,
                    KH + k * 0.03, KH + (k + 1) * 0.03 - 0.002, [M["book4"], M["book1"], M["book3"]][k])
            sphere(f"{prefix} {i} Sculpture", (kx0 + 0.20, a + 0.18, KH + 0.13), 0.04, M["brass"])
            box(f"{prefix} {i} Tray", kx0 + 0.10, kx0 + 0.30, b_ - 0.24, b_ - 0.08, KH, KH + 0.012, M["walnut"])
            cyl(f"{prefix} {i} Bowl", kx0 + 0.20, b_ - 0.16, KH + 0.012, KH + 0.06, 0.06, M["ceramic"], r2=0.07)
        else:
            for k, yy in enumerate((a + 0.18, b_ - 0.18)):
                box(f"{prefix} {i} Box {k}", kx0 + 0.06, kx1 - 0.08, yy - 0.12, yy + 0.12, 0.135, 0.33,
                    [M["p_cream"], M["book2"]][k], bevel=0.01)
            cyl(f"{prefix} {i} Pot", kx0 + 0.22, c, KH, KH + 0.16, 0.09, M["ceramic"], r2=0.08)
            for k in range(11):
                ang = k * 0.6
                sphere(f"{prefix} {i} Leaf {k}", (kx0 + 0.22 + 0.10 * math.cos(ang), c + 0.10 * math.sin(ang),
                                                  KH + 0.12 - 0.05 * (k % 4)), 0.045, M["leaf"], scale=(1, 0.7, 0.3), rot=(0.4, 0.2, ang))
        if wall_art == "ledge":
            box(f"{prefix} {i} Ledge", W - 0.08, W, a + 0.02, b_ - 0.02, 1.22, 1.24, M["oak"])
            lean = box(f"{prefix} {i} Print", -0.005, 0.005, -0.20, 0.20, 0.0, 0.50 - 0.06 * (i % 2), M["oak"])
            lean.location = (W - 0.04, c, 1.24)
            lean.rotation_euler = (0, math.radians(6), 0)
            paper = box(f"{prefix} {i} Print Paper", -0.0065, -0.005, -0.17, 0.17, 0.03, 0.47 - 0.06 * (i % 2),
                        [M["p_mustard"], M["p_cream"], M["p_teal"]][i % 3])
            paper.parent = lean
        if i == 2:
            for o in set(CURRENT["coll"].objects) - before:
                o["module3"] = 1
    if wall_art == "print":
        mid = y0 + modules * mw / 2
        framed_print(f"{prefix} Print", mid - 0.36, mid + 0.36, 1.20, 1.74, M["p_cream"],
                     ((mid - 0.12, 1.50, 0.13, M["p_mustard"]), (mid + 0.13, 1.40, 0.09, M["p_teal"]), (mid + 0.02, 1.58, 0.05, M["p_red"])))


# Steel drawers, 120 cm: two 60 cm modules, a framed print above
use_piece("console")
drawer_run("Console", 0.35, 2, 0.60, "print")
console_coll = CURRENT["coll"]

# Long steel drawer run, 195 cm: three 65 cm modules, prints on a picture ledge
use_piece("long")
drawer_run("Long", 0.05, 3, 0.65, "ledge")
long_coll = CURRENT["coll"]

# Electronics bench: steel frame, butcher-block top, pegboard, scope, PSU,
# soldering station, enclosed 3D printer, parts cabinet, magnifier lamp
use_piece("bench")
bx0, bx1, by0, by1, BH = W - 0.61, W - 0.01, 0.25, 1.55, 0.75
steel_frame("Bench", bx0, bx1, by0, (by0 + by1) / 2, BH)
steel_frame("Bench B", bx0, bx1, (by0 + by1) / 2, by1, BH)
box("Bench Top", bx0 - 0.01, bx1, by0, by1, BH - 0.04, BH, M["oak"], bevel=0.004)
box("Pegboard", W - 0.018, W - 0.003, by0 + 0.02, by1 - 0.02, 0.95, 1.75, M["pegboard"])
# 3D printer (enclosed cube) at the window end
box("Printer Body", bx0 + 0.12, bx1 - 0.06, by0 + 0.02, by0 + 0.44, BH, BH + 0.46, M["device"], bevel=0.01)
box("Printer Door", bx0 + 0.115, bx0 + 0.12, by0 + 0.05, by0 + 0.41, BH + 0.04, BH + 0.42, M["glass"])
box("Printer Plate", bx0 + 0.16, bx1 - 0.10, by0 + 0.06, by0 + 0.40, BH + 0.10, BH + 0.11, M["p_black"])
box("Printer Screen", bx0 + 0.114, bx0 + 0.118, by0 + 0.33, by0 + 0.40, BH + 0.01, BH + 0.035, M["scope_screen"])
# Oscilloscope
box("Scope Body", bx1 - 0.28, bx1 - 0.10, by0 + 0.52, by0 + 0.88, BH, BH + 0.19, M["device_light"], bevel=0.008)
box("Scope Screen", bx1 - 0.285, bx1 - 0.28, by0 + 0.55, by0 + 0.75, BH + 0.04, BH + 0.16, M["scope_screen"])
for k in range(6):
    cyl(f"Scope Knob {k}", 0, 0, 0, 0.01, 0.009, M["device"])
    kn = bpy.data.objects[f"Scope Knob {k}"]
    kn.location = (bx1 - 0.288, by0 + 0.78 + (k % 2) * 0.05, BH + 0.05 + (k // 2) * 0.045)
    kn.rotation_euler = (0, math.radians(90), 0)
# Bench power supply
box("PSU Body", bx1 - 0.32, bx1 - 0.10, by0 + 0.92, by0 + 1.06, BH, BH + 0.15, M["device"], bevel=0.006)
box("PSU Screen", bx1 - 0.325, bx1 - 0.32, by0 + 0.94, by0 + 1.04, BH + 0.08, BH + 0.13, M["psu_screen"])
for k, mat in enumerate((M["p_red"], M["p_black"])):
    cyl(f"PSU Jack {k}", 0, 0, 0, 0.012, 0.007, mat)
    j = bpy.data.objects[f"PSU Jack {k}"]
    j.location = (bx1 - 0.326, by0 + 0.96 + k * 0.05, BH + 0.035)
    j.rotation_euler = (0, math.radians(90), 0)
# Soldering station with iron in its holder, and a cutting mat
box("Solder Station", bx0 + 0.04, bx0 + 0.20, by0 + 1.10, by0 + 1.24, BH, BH + 0.09, M["device"], bevel=0.006)
box("Solder Display", bx0 + 0.036, bx0 + 0.04, by0 + 1.13, by0 + 1.21, BH + 0.04, BH + 0.07, M["psu_screen"])
cyl("Iron Holder", bx0 + 0.12, by0 + 1.20, BH + 0.09, BH + 0.17, 0.02, M["steel"], r2=0.03)
rod("Iron", (bx0 + 0.12, by0 + 1.20, BH + 0.12), (bx0 + 0.02, by0 + 1.12, BH + 0.24), 0.01, M["p_black"], verts=8)
box("Cutting Mat", bx0 + 0.04, bx0 + 0.34, by0 + 0.50, by0 + 1.06, BH, BH + 0.003, M["p_teal"])
# Magnifier lamp clamped at the back
rod("Magnifier Post", (bx1 - 0.05, by1 - 0.10, BH), (bx1 - 0.05, by1 - 0.10, BH + 0.45), 0.012, M["device_light"])
rod("Magnifier Arm", (bx1 - 0.05, by1 - 0.10, BH + 0.45), (bx0 + 0.20, by1 - 0.20, BH + 0.38), 0.01, M["device_light"])
rod("Magnifier Head", (bx0 + 0.20, by1 - 0.20, BH + 0.36), (bx0 + 0.20, by1 - 0.20, BH + 0.39), 0.08, M["device_light"], verts=32)
light_anchor("Light Bench", (bx0 + 0.20, by1 - 0.20, BH + 0.33), "bench")
# Lower shelf: parts cabinet and bins
box("Parts Cabinet", bx0 + 0.08, bx1 - 0.06, by0 + 0.05, by0 + 0.45, 0.135, 0.42, M["device_light"], bevel=0.004)
for r in range(4):
    for c_ in range(3):
        y_ = by0 + 0.07 + c_ * 0.125
        z_ = 0.15 + r * 0.068
        box(f"Parts Drawer {r}{c_}", bx0 + 0.075, bx0 + 0.08, y_, y_ + 0.11, z_, z_ + 0.058, M["glass"])
for k, (a, mat) in enumerate(((by0 + 0.70, M["book2"]), (by1 - 0.40, M["p_cream"]))):
    box(f"Bench Bin {k}", bx0 + 0.06, bx1 - 0.06, a, a + 0.32, 0.135, 0.36, mat, bevel=0.01)
# Pegboard: tools, wire spools, a filament shelf
box("Peg Shelf", W - 0.16, W - 0.003, by0 + 0.10, by0 + 0.60, 1.52, 1.535, M["steel"])
for k, (y, mat) in enumerate(((by0 + 0.20, M["spool_a"]), (by0 + 0.45, M["spool_b"]))):
    rod(f"Filament Spool {k}", (W - 0.14, y, 1.635), (W - 0.07, y, 1.635), 0.10, mat, verts=32)
for k in range(3):
    y = by0 + 0.75 + k * 0.10
    rod(f"Wire Spool {k}", (W - 0.06, y, 1.40), (W - 0.02, y, 1.40), 0.035, [M["p_red"], M["p_black"], M["copper"]][k], verts=20)
for k in range(5):
    y = by0 + 0.75 + k * 0.08
    rod(f"Screwdriver {k}", (W - 0.03, y, 1.15), (W - 0.03, y, 1.30), 0.008, [M["p_red"], M["p_mustard"], M["p_teal"], M["p_red"], M["p_black"]][k], verts=8)
for k in range(3):
    y = by0 + 1.15 + k * 0.06
    box(f"Pliers {k}", W - 0.03, W - 0.018, y - 0.012, y + 0.012, 1.10, 1.30, M["p_red"] if k % 2 else M["steel"])
box("Bench Power Strip", W - 0.05, W - 0.01, by0 + 0.50, by1 - 0.10, 0.96, 1.00, M["device_light"])
bench_coll = CURRENT["coll"]


# ---------------------------------------------------------------- the rest of the catalog
exec(open(os.path.join(HERE, "catalog.py")).read())

# ---------------------------------------------------------------- layout groups
def group(name, pivot, members, extras=None):
    """Parent top-level members under an empty at pivot; the viewer moves the empty."""
    g = bpy.data.objects.new(name, None)
    g.location = (pivot[0], pivot[1], 0)
    bpy.context.scene.collection.objects.link(g)
    for k, v in (extras or {}).items():
        g[k] = v
    bpy.context.view_layer.update()
    for o in members:
        if o.parent is not None:
            continue
        mw = o.matrix_world.copy()
        o.parent = g
        o.matrix_parent_inverse = g.matrix_world.inverted()
        o.matrix_world = mw
    return g


def named(*prefixes, exact=()):
    return [o for o in bpy.data.objects
            if o.type in ("MESH", "EMPTY") and not o.name.startswith("grp_")
            and (o.name.startswith(prefixes) or o.name in exact)]


group("grp_desk", (0.35, 0.80), named(
    "Desk ", "Monitor ", "Laptop ", "Lamp ", "Bulb ", "Orchid ", "Keyboard", "Mouse", "PC ", "Cable Tray",
    "Mushroom ", "Light Desk", "Light Bulb", "Light Mushroom", exact=("Glass",)))
group("grp_chair", (1.05, 0.75), named("Chairx ", exact=("MARKUS Chair", "Aluminium Group Chair", "Kneeling Chair", "Cantilever Chair")))
group("grp_deskwall", (0.0, 0.80), named(
    "Shelf", "Book Low", "Book Mid", "Vase Low", "Vase Top", "Ceramic Ball", "Record", "Poster A ", "Wallfeat "))
group("grp_console", (W - 0.235, 0.95), list(console_coll.objects), {"opt": "opp:console"})
group("grp_long", (W - 0.235, 1.025), list(long_coll.objects), {"opt": "opp:long"})
group("grp_bench", (W - 0.31, 0.90), list(bench_coll.objects), {"opt": "opp:bench"})
for name, pivot in OPP_GROUPS.items():
    group("grp_" + name, pivot, list(bpy.data.collections["opp:" + name].objects), {"opt": "opp:" + name})


# ---------------------------------------------------------------- tag walls for the cut-away viewer
for o in bpy.data.objects:
    n = o.name
    side = None
    if n.startswith(("Wall South", "Win ", "Roller Blind", "Skirting S")):
        side = "S"
    elif n.startswith(("Wall North", "Door ", "AC ", "Skirting N")):
        side = "N"
    elif n.startswith(("Wall East", "Skirting E")):
        side = "E"
    elif n.startswith(("Wall West", "Skirting W")):
        side = "W"
    elif n == "Ceiling":
        side = "C"
    if side:
        o["side"] = side

# ---------------------------------------------------------------- flatten procedural wood for glTF
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    inp = bsdf.inputs["Base Color"]
    if inp.is_linked:
        ramp = next((nd for nd in m.node_tree.nodes if nd.type == "VALTORGB"), None)
        if ramp:
            c0_, c1_ = ramp.color_ramp.elements[0].color, ramp.color_ramp.elements[1].color
            inp.default_value = tuple((c0_[i] * 0.45 + c1_[i] * 0.55) for i in range(4))
        for link in list(inp.links):
            m.node_tree.links.remove(link)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "room_options.blend"))
os.makedirs(os.path.join(HERE, "viewer"), exist_ok=True)
glb = os.path.join(HERE, "viewer", "room.glb")
bpy.ops.export_scene.gltf(
    filepath=glb,
    export_format="GLB",
    export_extras=True,
    export_lights=False,
    export_cameras=False,
    export_apply=True,
    export_yup=True,
)

# Artifacts serve .json but not .glb, and cap a file at 16 MB, so ship the GLB
# gzipped and base64-encoded inside a small JSON wrapper; the viewer inflates it
# with the browser's DecompressionStream.
import base64
import gzip
import json

with open(glb, "rb") as f:
    packed = gzip.compress(f.read(), compresslevel=9)
with open(os.path.join(HERE, "viewer", "room.json"), "w") as f:
    json.dump({"format": "glb+gzip+base64", "data": base64.b64encode(packed).decode()}, f)
os.remove(glb)
print("EXPORT OK")
