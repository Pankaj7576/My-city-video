import bpy
import math
from mathutils import Vector

"""
MY CITY VIDEO — 5-minute cinematic sequence scaffold.
Run scene_setup.py first, then this file, then render_config.py.
Characters are clearly labelled blockout stand-ins until final models are supplied.
Timeline: 30 FPS, 9000 frames, 16:9 UHD.
"""

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 9000

def mat(name, color, emission=0.0, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    if p:
        p.inputs["Base Color"].default_value = (*color, 1)
        p.inputs["Metallic"].default_value = metallic
        p.inputs["Roughness"].default_value = 0.35
        if emission:
            p.inputs["Emission Color"].default_value = (*color, 1)
            p.inputs["Emission Strength"].default_value = emission
    return m

red = mat("Siren Red", (0.8, 0.015, 0.025), 3.0)
blue = mat("Siren Blue", (0.015, 0.12, 0.9), 3.0)
green = mat("Digital Wave Green", (0.02, 0.9, 0.18), 4.0)
white = mat("UI White", (0.9, 0.95, 1.0), 1.5)
dark = mat("Character Blockout Dark", (0.035, 0.045, 0.065))
skin_a = mat("Aarav Blockout", (0.48, 0.25, 0.15))
skin_m = mat("Maya Blockout", (0.68, 0.39, 0.25))
cloth_a = mat("Aarav Jacket Blockout", (0.08, 0.22, 0.38))
cloth_m = mat("Maya Jacket Blockout", (0.42, 0.08, 0.24))
roadmat = mat("Market Road", (0.045, 0.052, 0.06))

def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material: o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new("Edge softness", "BEVEL")
        b.width = bevel
        b.segments = 3
    return o

def text_obj(name, body, loc, size, material):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = 0.012
    ob = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(ob)
    ob.location = loc
    if material: cu.materials.append(material)
    return ob

def key_loc(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert(data_path="location", frame=frame)

def key_scale(obj, frame, scale):
    obj.scale = scale
    obj.keyframe_insert(data_path="scale", frame=frame)

# Named collections keep the generated sequence organized.
def get_collection(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    return c

# Main characters: simple placeholder mannequins, not final character assets.
def make_character(name, x, y, jacket, skin):
    root = bpy.data.objects.new(name + "_ROOT", None)
    get_collection("CHARACTER_BLOCKOUTS").objects.link(root)
    parts = []
    parts.append(cube(name+"_Torso", (x,y,1.55), (0.72,0.42,1.0), jacket, 0.12))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.28, location=(x,y,2.28))
    head = bpy.context.object
    head.name = name+"_Head"
    head.data.materials.append(skin)
    parts.append(head)
    parts.append(cube(name+"_Leg_L", (x-0.19,y,0.62), (0.22,0.28,0.85), dark, 0.06))
    parts.append(cube(name+"_Leg_R", (x+0.19,y,0.62), (0.22,0.28,0.85), dark, 0.06))
    for p in parts:
        for c in list(p.users_collection): c.objects.unlink(p)
        get_collection("CHARACTER_BLOCKOUTS").objects.link(p)
        p.parent = root
    return root

aarav = make_character("AARAV_PLACEHOLDER", 0, 0, cloth_a, skin_a)
maya = make_character("MAYA_PLACEHOLDER", 2.5, 1, cloth_m, skin_m)

# Rooftop platform and warning beacons.
cube("Central Skyline Rooftop", (0,0,0), (34,26,1.2), dark, 0.4)
for i, x in enumerate((-8, 8)):
    beacon = cube("Warning Beacon " + str(i), (x,0,1.1), (0.7,0.7,0.35), red if i == 0 else blue, 0.12)
    beacon.scale = (1,1,1)
    beacon.keyframe_insert(data_path="scale", frame=1)
    beacon.scale = (1.25,1.25,1)
    beacon.keyframe_insert(data_path="scale", frame=12)
    beacon.scale = (1,1,1)
    beacon.keyframe_insert(data_path="scale", frame=24)

countdown = text_obj("Countdown Screen", "SYSTEM ALERT  |  00:05", (-7, -5, 2.5), 1.1, red)
countdown.rotation_euler = (math.radians(70), 0, 0)
countdown.keyframe_insert(data_path="hide_render", frame=1)
countdown.hide_render = False
countdown.keyframe_insert(data_path="hide_render", frame=150)

# Market street set dressing.
cube("Market Street", (0,35,-0.45), (110,22,0.5), roadmat)
for side in (-1,1):
    for i in range(8):
        x = -46 + i*13
        shop = cube(f"Market Shop {side}_{i}", (x,35+side*17,3.2), (10,9,6.4), mat(f"ShopMat_{side}_{i}", (0.18+0.03*i,0.16,0.2+0.02*i)), 0.18)
        sign = text_obj(f"Shop Sign {side}_{i}", "MARKET", (x-2.2,35+side*12.35,4.2), 0.7, white)
        sign.rotation_euler[0] = math.radians(90)

# Main server tower, intentionally fictional visual prop.
tower = cube("MAIN SERVER TOWER", (0,78,28), (24,24,56), dark, 0.5)
for z in range(5,55,7):
    band = cube(f"Server Tower Light Band {z}", (0,65.7,z), (20,0.35,0.32), blue, 0.04)

usb = cube("Story USB Drive Prop", (0,74,2), (0.22,0.8,0.12), white, 0.035)
usb.keyframe_insert(data_path="location", frame=5400)
usb.location = (0,76,2.2)
usb.keyframe_insert(data_path="location", frame=5700)

# Stylized digital wave ribbon appears green during climax.
for i in range(18):
    x = -22 + i*2.6
    wave = cube(f"Green Digital Wave {i}", (x,78,7+math.sin(i*0.7)*2), (1.8,0.16,0.28), green, 0.08)
    wave.keyframe_insert(data_path="location", frame=5900)
    wave.location.z += 5
    wave.keyframe_insert(data_path="location", frame=6500)

# Rooftop end-credit text.
credit = text_obj("End Credit", "NIRANJAN KUMAR", (-7, -7, 5), 1.25, white)
credit.rotation_euler = (math.radians(72), 0, 0)
credit.hide_render = True
credit.keyframe_insert(data_path="hide_render", frame=8549)
credit.hide_render = False
credit.keyframe_insert(data_path="hide_render", frame=8550)

# Camera creation/reuse and cinematic 5-shot movement.
camera = scene.camera
if camera is None:
    data = bpy.data.cameras.new("Story Cinematic Camera")
    camera = bpy.data.objects.new("Story Cinematic Camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
camera.data.lens = 45

def aim_at(obj, point):
    obj.rotation_euler = (Vector(point)-obj.location).to_track_quat("-Z","Y").to_euler()

shots = [
    (1, (0,-10,3.0), (0,0,2.0)),             # Rooftop face-height push-in
    (150, (0,-8,4.0), (0,0,2.0)),
    (151, (210,-220,155), (0,30,15)),         # City aerial start
    (1800, (75,-80,70), (0,35,20)),           # Fly-through
    (1801, (-18,15,5), (0,35,2)),             # Market chase
    (5400, (0,25,5), (0,78,18)),              # Server tower
    (8100, (0,78,15), (0,78,25)),             # Climax hold
    (8101, (0,-10,8), (0,0,1)),               # Quiet rooftop
    (9000, (0,-18,24), (0,0,0)),              # Pan up to sky
]
for frame, loc, target in shots:
    camera.location = loc
    aim_at(camera, target)
    camera.keyframe_insert(data_path="location", frame=frame)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)

if camera.animation_data and camera.animation_data.action:
    for fc in camera.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"

# Scene markers: 30 FPS, 5 minutes total.
for name, frame in [
    ("SCENE 1 | HOOK",1), ("SCENE 2 | MEGA CITY OVERVIEW",151),
    ("SCENE 3 | MARKET CHASE",1801), ("SCENE 4 | SERVER TOWER CLIMAX",5400),
    ("SCENE 5 | ROOFTOP ENDING",8101)
]:
    scene.timeline_markers.new(name, frame=frame)

scene.frame_set(1)
print("MY CITY VIDEO: five-scene 5-minute sequence scaffold created.")
print("NOTE: character blockouts and visual story props are placeholders; final models, detailed acting, dialogue and sound remain to be produced.")
