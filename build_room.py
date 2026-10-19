"""Builds the study room in Blender.

Run:  blender --background --python room-model/build_room.py
Writes room-model/room.blend and preview renders next to this script.

Coordinates (metres): origin = inner south-west corner.
  x -> east (276.2 cm), y -> north (333.6 cm), z -> up (270 cm).
South wall: window + radiator. West wall: desk, PC, wardrobe, concrete shaft
in the NW corner. North wall: door + air conditioner.
"""
import math
import os

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))

W, D, H = 2.762, 3.336, 2.70  # inner room size
T = 0.12  # wall thickness


# ---------------------------------------------------------------- helpers
def srgb(hexstr):
    """'#rrggbb' -> linear RGBA for Principled BSDF."""
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def material(name, color, rough=0.6, metal=0.0, emit=None, emit_strength=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = srgb(color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = srgb(emit)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        bsdf.inputs["Transmission Weight"].default_value = 1.0
    return m


def wood_material(name, light, dark, scale=(1.0, 12.0, 1.0), rough=0.45):
    """Procedural plank-ish wood: stretched noise mixed between two tones."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = scale
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Distortion"].default_value = 2.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb(dark)
    ramp.color_ramp.elements[1].color = srgb(light)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


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
    return o


def cyl(name, x, y, z0, z1, r, mat, verts=24, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def empty(name, loc, rot_z=0.0):
    o = bpy.data.objects.new(name, None)
    o.location = loc
    o.rotation_euler = (0, 0, rot_z)
    bpy.context.collection.objects.link(o)
    return o


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    layer = bpy.context.view_layer.layer_collection.children[name]
    bpy.context.view_layer.active_layer_collection = layer
    return c


# ---------------------------------------------------------------- reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"

# ---------------------------------------------------------------- materials
M = {
    "green": material("Wall Green", "#5f8f78", rough=0.85),
    "white_wall": material("Wall White", "#e9e7e1", rough=0.85),
    "door_wall": material("Wall Door", "#e9e7e1", rough=0.85),
    "east_wall": material("Wall East", "#e9e7e1", rough=0.85),
    "ceiling": material("Ceiling", "#6d9a84", rough=0.9),
    "concrete": material("Shaft", "#5f8f78", rough=0.85),
    "floor": wood_material("Oak Floor", "#b07a45", "#7f5126", scale=(1.0, 14.0, 1.0)),
    "skirting": material("Skirting Black", "#1c1c1c", rough=0.5),
    "door": material("Door White", "#f2f1ec", rough=0.35),
    "window_wood": wood_material("Window Oak", "#c88a3e", "#9a5f22", scale=(1, 1, 10), rough=0.35),
    "glass": material("Glass", "#c9d6dc", rough=0.02, alpha=0.15),
    "sill": material("Sill Stone", "#d8cfbf", rough=0.3),
    "radiator": material("Radiator White", "#f4f4f2", rough=0.35),
    # Wardrobe: matte dusty mauve sampled from the photo
    "wardrobe": material("Wardrobe Mauve", "#8a5459", rough=0.75),
    "handle": material("Handle Black", "#151515", rough=0.35, metal=0.6),
    "desk_top": wood_material("Desk Black Ash", "#2b2522", "#141110", scale=(8, 1, 1), rough=0.5),
    "desk_leg": material("Desk Leg White", "#ecebe6", rough=0.3, metal=0.2),
    "chair_fabric": material("Chair Fabric", "#3a3a3c", rough=0.95),
    "chair_mesh": material("Chair Mesh", "#1d1d1f", rough=0.9),
    "chair_plastic": material("Chair Plastic Black", "#121212", rough=0.4),
    "pc": material("PC Case", "#111111", rough=0.4, metal=0.3),
    "monitor": material("Monitor Black", "#0d0d0d", rough=0.3),
    "laptop": material("Laptop Silver", "#c9c9cb", rough=0.25, metal=0.9),
    "screen": material("Screen", "#dfe3ea", emit="#dfe3ea", emit_strength=1.5),
    "ac": material("AC White", "#f3f3f1", rough=0.3),
    "lamp_metal": material("Lamp Metal", "#9c9c9c", rough=0.3, metal=0.8),
    "lamp_head": material("Lamp Head", "#202020", rough=0.4),
    "bulb": material("Bulb", "#ffd28a", emit="#ffb85c", emit_strength=8.0),
    "pot": material("Pot", "#dcdcd5", rough=0.5),
    "leaf": material("Leaf", "#3f6b3a", rough=0.6),
    "flower": material("Orchid", "#f0c6d6", rough=0.6),
    "blind": material("Roller Blind Box", "#1a1a1a", rough=0.5),
    "plafon": material("Plafon Black", "#151515", rough=0.5),
    "plafon_diffuser": material("Plafon Diffuser", "#fff1dc", rough=0.3, emit="#ffd29a", emit_strength=3.0),
}

# ---------------------------------------------------------------- shell
collection("Room")
box("Floor", -T, W + T, -T, D + T, -0.02, 0, M["floor"])
box("Ceiling", -T, W + T, -T, D + T, H, H + 0.02, M["ceiling"])
# Black ceiling plafon, 60 cm across, with smart bulbs set warm
cyl("Plafon Body", W / 2, D / 2, H - 0.08, H, 0.30, M["plafon"], verts=64)
cyl("Plafon Diffuser", W / 2, D / 2, H - 0.085, H - 0.08, 0.27, M["plafon_diffuser"], verts=64)

# West wall (desk + wardrobe), full height
box("Wall West", -T, 0, 0, D, 0, H, M["green"])
# East wall (camera side), white like the door wall
box("Wall East", W, W + T, 0, D, 0, H, M["east_wall"])

# South wall with window opening x 0.07..1.51, sill 0.85, head 2.40
WIN_X0, WIN_X1, WIN_Z0, WIN_Z1 = 0.07, 1.51, 0.85, 2.40
box("Wall South L", -T, WIN_X0, -T, 0, 0, H, M["white_wall"])
box("Wall South R", WIN_X1, W + T, -T, 0, 0, H, M["white_wall"])
box("Wall South Below", WIN_X0, WIN_X1, -T, 0, 0, WIN_Z0, M["white_wall"])
box("Wall South Above", WIN_X0, WIN_X1, -T, 0, WIN_Z1, H, M["white_wall"])

# North wall with door opening x 0.76..1.60, height 2.05
DOOR_X0, DOOR_X1, DOOR_H = 0.76, 1.60, 2.05
box("Wall North L", -T, DOOR_X0, D, D + T, 0, H, M["door_wall"])
box("Wall North R", DOOR_X1, W + T, D, D + T, 0, H, M["door_wall"])
box("Wall North Above", DOOR_X0, DOOR_X1, D, D + T, DOOR_H, H, M["door_wall"])

# Concrete shaft boxed in the NW corner (52 x 52 cm)
box("Shaft NW", 0, 0.52, D - 0.52, D, 0, H, M["concrete"])

# Skirting boards (6 cm, black)
SK = 0.06
box("Skirting W", 0, 0.012, 0, D - 0.52, 0, SK, M["skirting"])
box("Skirting E", W - 0.012, W, 0, D, 0, SK, M["skirting"])
box("Skirting S", 0, W, 0, 0.012, 0, SK, M["skirting"])
box("Skirting N1", 0.52, DOOR_X0, D - 0.012, D, 0, SK, M["skirting"])
box("Skirting N2", DOOR_X1, W, D - 0.012, D, 0, SK, M["skirting"])

# ---------------------------------------------------------------- window
collection("Window")
fw = 0.07  # frame width
wx0, wx1, wz0, wz1 = WIN_X0, WIN_X1, WIN_Z0, WIN_Z1
wy0, wy1 = -0.09, -0.02
box("Win Frame Bottom", wx0, wx1, wy0, wy1, wz0, wz0 + fw, M["window_wood"])
box("Win Frame Top", wx0, wx1, wy0, wy1, wz1 - fw, wz1, M["window_wood"])
box("Win Frame Left", wx0, wx0 + fw, wy0, wy1, wz0, wz1, M["window_wood"])
box("Win Frame Right", wx1 - fw, wx1, wy0, wy1, wz0, wz1, M["window_wood"])
mid = (wx0 + wx1) / 2
box("Win Mullion", mid - 0.05, mid + 0.05, wy0, wy1 + 0.01, wz0, wz1, M["window_wood"])
# Sash frames
for i, (sx0, sx1) in enumerate(((wx0 + fw, mid - 0.05), (mid + 0.05, wx1 - fw))):
    box(f"Win Sash {i} B", sx0, sx1, wy0 + 0.01, wy1 + 0.015, wz0 + fw, wz0 + fw + 0.06, M["window_wood"])
    box(f"Win Sash {i} T", sx0, sx1, wy0 + 0.01, wy1 + 0.015, wz1 - fw - 0.06, wz1 - fw, M["window_wood"])
    box(f"Win Sash {i} L", sx0, sx0 + 0.06, wy0 + 0.01, wy1 + 0.015, wz0 + fw, wz1 - fw, M["window_wood"])
    box(f"Win Sash {i} R", sx1 - 0.06, sx1, wy0 + 0.01, wy1 + 0.015, wz0 + fw, wz1 - fw, M["window_wood"])
    box(f"Win Glass {i}", sx0 + 0.06, sx1 - 0.06, -0.06, -0.055, wz0 + fw + 0.06, wz1 - fw - 0.06, M["glass"])
# Handle on the right sash
box("Win Handle", mid + 0.08, mid + 0.10, -0.015, 0.02, 1.55, 1.68, M["laptop"])
# Reveals (white plaster) and sill
box("Win Reveal L", wx0 - 0.002, wx0, -T, 0, wz0, wz1, M["white_wall"])
box("Win Sill", wx0 - 0.03, wx1 + 0.03, -0.10, 0.04, wz0 - 0.02, wz0, M["sill"])
# Roller blind cassette above window (black box seen in photo)
box("Roller Blind Box", wx0 - 0.05, wx1 + 0.05, 0.0, 0.10, WIN_Z1 + 0.03, WIN_Z1 + 0.15, M["blind"])

# ---------------------------------------------------------------- radiator (tops out under desk height; the desk fits over it)
collection("Radiator")
rx0, rx1 = 0.78, 1.48
box("Radiator Body", rx0, rx1, 0.05, 0.15, 0.14, 0.70, M["radiator"], bevel=0.004)
for i in range(int((rx1 - rx0) / 0.03)):
    x = rx0 + 0.015 + i * 0.03
    box(f"Radiator Fin {i}", x - 0.006, x + 0.006, 0.148, 0.156, 0.18, 0.66, M["radiator"])
box("Radiator Valve", rx1 - 0.02, rx1 + 0.03, 0.08, 0.12, 0.62, 0.70, M["radiator"])

# ---------------------------------------------------------------- door + AC
collection("Door")
box("Door Leaf", DOOR_X0 + 0.02, DOOR_X1 - 0.02, D + 0.02, D + 0.06, 0, DOOR_H - 0.02, M["door"])
box("Door Frame L", DOOR_X0 - 0.06, DOOR_X0, D - 0.015, D + T, 0, DOOR_H + 0.06, M["door"])
box("Door Frame R", DOOR_X1, DOOR_X1 + 0.06, D - 0.015, D + T, 0, DOOR_H + 0.06, M["door"])
box("Door Frame Top", DOOR_X0 - 0.06, DOOR_X1 + 0.06, D - 0.015, D + T, DOOR_H, DOOR_H + 0.06, M["door"])
box("Door Handle", DOOR_X1 - 0.16, DOOR_X1 - 0.04, D + 0.0, D + 0.02, 1.03, 1.05, M["laptop"])

collection("AirCon")
box("AC Unit", 1.75, 2.62, D - 0.24, D, 2.28, 2.58, M["ac"], bevel=0.03)
box("AC Vent", 1.78, 2.59, D - 0.245, D - 0.20, 2.29, 2.33, M["skirting"])

# ---------------------------------------------------------------- wardrobe (110 cm, mauve)
collection("Wardrobe")
WD = 0.597  # depth
wy_a = D - 1.67  # south edge (from plan: 56..167 cm off the north wall)
wy_b = D - 0.56
WH = H - 0.003  # floor-to-ceiling
box("Wardrobe Carcass", 0, WD - 0.02, wy_a, wy_b, 0, WH, M["wardrobe"])
wmid = (wy_a + wy_b) / 2
box("Wardrobe Door S", WD - 0.02, WD, wy_a, wmid - 0.0015, 0.005, WH, M["wardrobe"], bevel=0.002)
box("Wardrobe Door N", WD - 0.02, WD, wmid + 0.0015, wy_b, 0.005, WH, M["wardrobe"], bevel=0.002)
# Long black bar handle on the north door, lower half
box("Wardrobe Handle", WD, WD + 0.012, wmid + 0.012, wmid + 0.022, 0.02, 1.05, M["handle"])

# ---------------------------------------------------------------- desk (IKEA BEKANT-style, 140x70)
collection("Desk")
DX0, DX1 = 0.0, 0.70
DY0, DY1 = 0.10, 1.50
DZ = 0.74
box("Desk Top", DX0, DX1, DY0, DY1, DZ - 0.025, DZ, M["desk_top"], bevel=0.003)
for side, y in (("S", DY0 + 0.08), ("N", DY1 - 0.08)):
    box(f"Desk Foot {side}", DX0 + 0.04, DX1 - 0.04, y - 0.03, y + 0.03, 0, 0.03, M["desk_leg"], bevel=0.01)
    box(f"Desk Leg {side}", 0.32, 0.38, y - 0.03, y + 0.03, 0.03, DZ - 0.07, M["desk_leg"])
    box(f"Desk Bracket {side}", DX0 + 0.06, DX1 - 0.06, y - 0.025, y + 0.025, DZ - 0.07, DZ - 0.025, M["desk_leg"])
box("Desk Crossbar", 0.33, 0.37, DY0 + 0.08, DY1 - 0.08, DZ - 0.10, DZ - 0.06, M["desk_leg"])

# Monitor (34" ultrawide-ish, on a stand)
box("Monitor Base", 0.10, 0.28, 0.62, 0.92, DZ, DZ + 0.012, M["monitor"])
box("Monitor Neck", 0.12, 0.15, 0.75, 0.79, DZ, DZ + 0.16, M["monitor"])
box("Monitor Panel", 0.10, 0.13, 0.43, 1.11, DZ + 0.10, DZ + 0.40, M["monitor"])

# Laptop (MacBook-ish), open, lid leaning back toward the wall
box("Laptop Base", 0.30, 0.52, 0.62, 0.93, DZ, DZ + 0.015, M["laptop"])
lid = box("Laptop Lid", -0.003, 0.003, -0.155, 0.155, 0, 0.21, M["laptop"])
lid.location = (0.30, 0.775, DZ + 0.015)
lid.rotation_euler = (0, math.radians(-15), 0)
scr = box("Laptop Screen", 0.0035, 0.005, -0.145, 0.145, 0.01, 0.20, M["screen"])
scr.parent = lid

# Desk lamp (arm lamp near the window end)
cyl("Lamp Clamp", 0.06, 0.20, DZ, DZ + 0.03, 0.03, M["lamp_metal"])
pole = cyl("Lamp Pole", 0.06, 0.20, DZ + 0.03, DZ + 0.42, 0.01, M["lamp_metal"])
box("Lamp Bar", 0.06, 0.28, 0.19, 0.21, DZ + 0.42, DZ + 0.44, M["lamp_head"])
box("Lamp Head", 0.10, 0.36, 0.17, 0.23, DZ + 0.40, DZ + 0.42, M["lamp_head"])

# Edison bulb lamp on a round wood base
cyl("Bulb Base", 0.20, 0.42, DZ, DZ + 0.03, 0.05, M["window_wood"])
cyl("Bulb Stem", 0.20, 0.42, DZ + 0.03, DZ + 0.09, 0.006, M["lamp_metal"])
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0.20, 0.42, DZ + 0.14))
bpy.context.active_object.name = "Bulb Glass"
bpy.context.active_object.data.materials.append(M["bulb"])

# Orchid in a ribbed pot
cyl("Orchid Pot", 0.12, 1.20, DZ, DZ + 0.10, 0.055, M["pot"])
cyl("Orchid Stem", 0.12, 1.20, DZ + 0.10, DZ + 0.38, 0.004, M["leaf"])
for i in range(4):
    a = i * math.pi / 2 + 0.4
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(0.12 + 0.06 * math.cos(a), 1.20 + 0.06 * math.sin(a), DZ + 0.12))
    leaf = bpy.context.active_object
    leaf.name = f"Orchid Leaf {i}"
    leaf.scale = (1.8, 0.6, 0.25)
    leaf.rotation_euler = (0, 0, a)
    leaf.data.materials.append(M["leaf"])
for i, (dy, dz) in enumerate(((-0.05, 0.36), (0.0, 0.33), (0.05, 0.30), (0.08, 0.26), (-0.07, 0.28))):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(0.13, 1.20 + dy, DZ + dz))
    bpy.context.active_object.name = f"Orchid Flower {i}"
    bpy.context.active_object.data.materials.append(M["flower"])

# Keyboard, mouse, glass
box("Keyboard", 0.38, 0.52, 0.86, 1.14, DZ, DZ + 0.02, M["flower"], bevel=0.004)
box("Mouse", 0.45, 0.55, 1.17, 1.23, DZ, DZ + 0.025, M["laptop"], bevel=0.01)
cyl("Glass", 0.60, 0.52, DZ, DZ + 0.09, 0.03, M["glass"])

# ---------------------------------------------------------------- PC tower
collection("PC")
box("PC Tower", 0.04, 0.50, 1.52, 1.66, 0, 0.46, M["pc"], bevel=0.005)
box("PC Front Vent", 0.50, 0.505, 1.54, 1.64, 0.05, 0.25, M["handle"])

# ---------------------------------------------------------------- chair (IKEA MARKUS)
collection("Chair")
# Local frame: chair faces -x (towards the desk); root sits on the floor.
chair = empty("MARKUS Chair", (1.05, 0.75, 0), rot_z=math.radians(40))

# 5-star base + casters
for i in range(5):
    a = i * 2 * math.pi / 5
    leg = box(f"Chair Leg {i}", 0, 0.32, -0.02, 0.02, 0.07, 0.10, M["chair_plastic"], parent=chair)
    leg.rotation_euler = (0, 0, a)
    leg.location = (0, 0, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(0.32 * math.cos(a), 0.32 * math.sin(a), 0.03))
    c = bpy.context.active_object
    c.name = f"Chair Caster {i}"
    c.data.materials.append(M["chair_plastic"])
    c.parent = chair
cyl("Chair Hub", 0, 0, 0.06, 0.12, 0.05, M["chair_plastic"], parent=chair)
cyl("Chair Gas Lift", 0, 0, 0.12, 0.42, 0.025, M["chair_plastic"], parent=chair)

# Seat
box("Chair Seat", -0.25, 0.25, -0.25, 0.25, 0.42, 0.50, M["chair_fabric"], bevel=0.035, parent=chair)
# Armrests (posts + pads)
for side, y in (("L", -0.27), ("R", 0.27)):
    box(f"Chair Arm Post {side}", 0.02, 0.10, y - 0.015, y + 0.015, 0.44, 0.66, M["chair_plastic"], parent=chair)
    box(f"Chair Arm Pad {side}", -0.20, 0.10, y - 0.03, y + 0.03, 0.66, 0.69, M["chair_plastic"], bevel=0.01, parent=chair)
# High mesh back + headrest, tilted back a little
back = empty("Chair Back Pivot", (0.24, 0, 0.50))
back.parent = chair
back.rotation_euler = (0, math.radians(10), 0)  # +y leans the back toward +x (behind the seat)
box("Chair Back Frame", -0.03, 0.02, -0.24, 0.24, 0.05, 0.72, M["chair_plastic"], bevel=0.02, parent=back)
box("Chair Back Mesh", -0.035, -0.025, -0.22, 0.22, 0.08, 0.70, M["chair_mesh"], parent=back)
box("Chair Headrest", -0.05, 0.03, -0.15, 0.15, 0.78, 0.92, M["chair_fabric"], bevel=0.03, parent=back)
box("Chair Headrest Post", 0.0, 0.02, -0.02, 0.02, 0.70, 0.80, M["chair_plastic"], parent=back)
box("Chair Back Spine", 0.0, 0.03, -0.03, 0.03, -0.05, 0.10, M["chair_plastic"], parent=back)

# ---------------------------------------------------------------- lights + camera
collection("Lights & Camera")
bpy.ops.object.light_add(type="AREA", location=(W / 2, D / 2, H - 0.05))
ceil = bpy.context.active_object
ceil.name = "Ceiling Light"
ceil.data.energy = 220
ceil.data.size = 0.5
ceil.data.color = (1.0, 0.80, 0.58)  # 2700K smart bulbs

# Bounce fill: lights the ceiling and upper walls the way the real fixture does.
bpy.ops.object.light_add(type="AREA", location=(W / 2, D / 2, H - 0.40))
bounce = bpy.context.active_object
bounce.name = "Ceiling Bounce"
bounce.rotation_euler = (math.pi, 0, 0)
bounce.data.energy = 120
bounce.data.size = 1.5
bounce.data.color = (1.0, 0.80, 0.58)
bounce.visible_camera = False

bpy.ops.object.light_add(type="SPOT", location=(0.22, 0.30, DZ + 0.40))
desk_light = bpy.context.active_object
desk_light.name = "Desk Lamp Light"
desk_light.data.energy = 60
desk_light.data.color = (1.0, 0.95, 0.75)
desk_light.data.spot_size = math.radians(110)
desk_light.rotation_euler = (0, 0, 0)  # points straight down

bpy.ops.object.light_add(type="POINT", location=(0.20, 0.42, DZ + 0.14))
bulb_light = bpy.context.active_object
bulb_light.name = "Bulb Light"
bulb_light.data.energy = 6
bulb_light.data.color = (1.0, 0.7, 0.4)
bulb_light.data.shadow_soft_size = 0.05

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.025, 0.04, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5


def add_camera(name, loc, target, lens):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return cam


# Matches the reference photo: standing by the east wall, looking west.
photo_cam = add_camera("Camera Photo", (2.68, 1.45, 1.35), (0.0, 1.55, 1.15), 14)
# Overhead cut-away view, ceiling hidden from camera rays.
top_cam = add_camera("Camera Top", (W / 2, D / 2, 7.5), (W / 2, D / 2, 0), 30)
top_cam.data.type = "ORTHO"
top_cam.data.ortho_scale = 3.9

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.view_settings.view_transform = "AgX"
scene.camera = photo_cam

blend_path = os.path.join(HERE, "room.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

if os.environ.get("ROOM_RENDER"):
    scene.render.filepath = os.path.join(HERE, "render_photo_view.png")
    bpy.ops.render.render(write_still=True)

    ceiling = bpy.data.objects["Ceiling"]
    ceiling.hide_render = True
    scene.camera = top_cam
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1200
    scene.render.filepath = os.path.join(HERE, "render_top_view.png")
    bpy.ops.render.render(write_still=True)
