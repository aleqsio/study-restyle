"""Renders the social preview card (viewer/og.png, 1200 x 630) from room_options.blend.

Run after restyle_export.py:
  blender --background room-model/room_options.blend --python room-model/render_og.py
Shows the Mid-century preset from the dollhouse angle, near walls and ceiling cut away.
"""
import os

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
W, D = 2.762, 3.336

KEEP = {"light:globe", "desklamp:mushroom", "desk:walnut", "pc:caddy", "shelf:string", "rug:geo", "art:posters",
        "corner:reading", "opp:console", "plant:rubber", "x:bias", "x:throw", "x:acc"}
REPLACED = {"light", "desklamp", "desk", "pc"}  # today's versions these replace
CUT = ("Wall South", "Wall East", "Win ", "Roller Blind", "Skirting S", "Skirting E", "Ceiling", "Plafon",
       "Console Print")  # the print hangs on the cut-away east wall

for o in bpy.data.objects:
    opt, base, hide = o.get("opt"), o.get("slotBase"), o.get("hideWith")
    hidden = (opt is not None and opt not in KEEP) or (base in REPLACED) or (hide in KEEP) or o.name.startswith(CUT)
    o.hide_render = hidden
# Children inherit nothing in Blender's render visibility, so hide whole subtrees explicitly
for o in bpy.data.objects:
    if o.hide_render:
        for c in o.children_recursive:
            c.hide_render = True

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1200, 630
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
world = sc.world
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.20, 0.16, 0.13, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.6
for l in bpy.data.lights:
    l.energy *= 1.6

cam = bpy.data.objects.new("OG Camera", bpy.data.cameras.new("OG Camera"))
sc.collection.objects.link(cam)
cam.data.lens = 34
cam.location = (W + 2.35, -2.05, 3.25)
cam.rotation_euler = (Vector((W / 2 - 0.05, D / 2 + 0.15, 0.85)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
sc.render.filepath = os.path.join(HERE, "viewer", "og.png")
bpy.ops.render.render(write_still=True)
