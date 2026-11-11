import bpy
import math
from mathutils import Vector
from pathlib import Path

"""
MY CITY VIDEO — additional placeholder visuals.
Run after scripts/story_sequence.py in Blender.
Adds Maya's communication device + hologram, and a dedicated server/USB
close-up with an animated red-to-green status light.
All assets are temporary, editable primitives.
"""

scene = bpy.context.scene

def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    return c

def move_to_collection(obj, name):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection(name).objects.link(obj)
    return obj

def emission_material(name, color, strength):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = strength
        bsdf.inputs["Roughness"].default_value = 0.28
    return m

def cube(name, location, dimensions, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft placeholder edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    return move_to_collection(o, "VISUAL_PLACEHOLDERS")

def text_obj(name, body, location, size, material):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.002
    obj = bpy.data.objects.new(name, curve)
    collection("VISUAL_PLACEHOLDERS").objects.link(obj)
    obj.location = location
    curve.materials.append(material)
    return obj

def set_emission_keyframes(material, keys):
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    socket = bsdf.inputs.get("Emission Color")
    strength = bsdf.inputs.get("Emission Strength")
    for frame, color, power in keys:
        socket.default_value = (*color, 1)
        socket.keyframe_insert(data_path="default_value", frame=frame)
        strength.default_value = power
        strength.keyframe_insert(data_path="default_value", frame=frame)

cyan = emission_material("Hologram Cyan", (0.02, 0.65, 1.0), 3.5)
red = emission_material("Server Status Red", (1.0, 0.015, 0.02), 4.0)
green = emission_material("Server Status Green", (0.02, 1.0, 0.12), 4.0)
metal = bpy.data.materials.get("Story USB Metal") or bpy.data.materials.new("Story USB Metal")
metal.diffuse_color = (0.24, 0.28, 0.34, 1)
metal.use_nodes = True
metal.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.24, 0.28, 0.34, 1)
metal.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.82

# Maya's wrist communicator — set beside her existing placeholder.
device = cube("Maya Wrist Communicator", (2.95, 0.55, 1.58), (0.34, 0.12, 0.22), metal, 0.045)
screen = cube("Maya Communicator Screen", (2.95, 0.475, 1.59), (0.27, 0.018, 0.15), cyan, 0.012)
holo = cube("Maya Hologram Panel", (3.2, 0.25, 2.25), (1.35, 0.035, 0.72), cyan, 0.025)
holo_text = text_obj("Maya Hologram Message", "MAYA  //  LINK ACTIVE", (2.62, 0.205, 2.23), 0.105, cyan)
# Keep the panel subtle until the city communication beat.
for obj in (holo, holo_text):
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=150)
    obj.hide_render = False
    obj.keyframe_insert(data_path="hide_render", frame=180)
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=1799)

# Server terminal front panel and visible USB slot, placed in front of tower.
terminal = cube("Server Terminal Closeup Panel", (0, 64.2, 5.0), (5.8, 0.42, 3.4), metal, 0.16)
slot = cube("Server USB Slot", (0, 63.96, 4.8), (0.92, 0.06, 0.18), red, 0.025)
status = cube("Server Status Indicator", (1.8, 63.93, 5.9), (0.22, 0.06, 0.22), red, 0.035)
usb = cube("USB Drive Closeup", (-1.6, 62.8, 4.8), (0.24, 0.82, 0.14), metal, 0.035)
usb_tip = cube("USB Connector Tip", (-1.6, 62.38, 4.8), (0.15, 0.12, 0.10), metal, 0.012)
for obj in (usb, usb_tip):
    obj.keyframe_insert(data_path="location", frame=5700)
    obj.location.y = 63.82
    obj.keyframe_insert(data_path="location", frame=5850)

set_emission_keyframes(red, [
    (5400, (1.0, 0.015, 0.02), 4.0),
    (5849, (1.0, 0.015, 0.02), 4.0),
    (5850, (0.02, 1.0, 0.12), 4.0),
    (9000, (0.02, 1.0, 0.12), 4.0),
])
set_emission_keyframes(green, [
    (5400, (1.0, 0.015, 0.02), 0.0),
    (5849, (1.0, 0.015, 0.02), 0.0),
    (5850, (0.02, 1.0, 0.12), 4.0),
    (9000, (0.02, 1.0, 0.12), 4.0),
])
# Assign animated green material to status after the red state is represented by keyframes.
status.data.materials.clear()
status.data.materials.append(green)
set_emission_keyframes(green, [
    (5400, (1.0, 0.015, 0.02), 4.0),
    (5849, (1.0, 0.015, 0.02), 4.0),
    (5850, (0.02, 1.0, 0.12), 4.0),
    (9000, (0.02, 1.0, 0.12), 4.0),
])

# Add a dedicated close-up camera beat without disturbing the overall 5-minute length.
camera = scene.camera
if camera is None:
    data = bpy.data.cameras.new("Server USB Closeup Camera")
    camera = bpy.data.objects.new("Server USB Closeup Camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
camera.data.lens = 70
for frame, location, target in [
    (5699, (0, 51, 7.4), (0, 64, 5.0)),
    (5700, (-2.8, 60.2, 5.8), (-0.2, 64.0, 5.0)),
    (6000, (-2.8, 60.2, 5.8), (-0.2, 64.0, 5.0)),
    (6001, (0, 25, 5), (0, 78, 18)),
]:
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.keyframe_insert(data_path="location", frame=frame)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)

scene.timeline_markers.new("MAYA COMMUNICATION HOLOGRAM", frame=180)
scene.timeline_markers.new("USB INSERTION CLOSEUP", frame=5700)
scene.timeline_markers.new("SERVER STATUS RED TO GREEN", frame=5850)
scene.frame_set(1)
print("Added communicator, hologram, server USB close-up, and animated status-light placeholders.")
