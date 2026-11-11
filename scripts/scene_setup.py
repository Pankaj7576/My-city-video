import bpy
import math
import random
from mathutils import Vector
from pathlib import Path

"""
MY CITY VIDEO — PROCEDURAL CYBER-CITY
Blender 4.x / Eevee Next compatible starting scene.
Run: blender --background --python scripts/scene_setup.py

Creates a reusable generated collection, a large road grid, skyscrapers,
neon accents, animated traffic placeholders, Aarav/Maya blockouts,
Maya's hologram, and a server/USB climax prop.
All generated geometry is placeholder art and can be replaced later.
"""

SEED = 27
random.seed(SEED)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.frame_start = 1
scene.frame_end = 9000
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"

ROOT_NAME = "MY_CITY_GENERATED"
root = bpy.data.collections.get(ROOT_NAME)
if root:
    for obj in list(root.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for child in list(root.children):
        bpy.data.collections.remove(child)
else:
    root = bpy.data.collections.new(ROOT_NAME)
    scene.collection.children.link(root)

def subcollection(name):
    c = bpy.data.collections.new(name)
    root.children.link(c)
    return c

CITY = subcollection("01_CITY_ENVIRONMENT")
ROADS = subcollection("02_ROADS_AND_TRAFFIC")
CHAR = subcollection("03_CHARACTER_BLOCKOUTS")
PROPS = subcollection("04_STORY_PROPS")
LIGHTS = subcollection("05_LIGHTS")

def move_to(obj, collection):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def material(name, color, metallic=0.0, roughness=0.55, emission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    if p:
        p.inputs["Base Color"].default_value = (*color, 1)
        p.inputs["Metallic"].default_value = metallic
        p.inputs["Roughness"].default_value = roughness
        if emission:
            p.inputs["Emission Color"].default_value = (*color, 1)
            p.inputs["Emission Strength"].default_value = emission
    return m

ASPHALT = material("MC | Asphalt", (0.018, 0.025, 0.04), roughness=0.92)
GROUND = material("MC | Ground", (0.025, 0.035, 0.045), roughness=1)
GLASS_A = material("MC | Tower Blue Glass", (0.025, 0.09, 0.16), 0.7, 0.22)
GLASS_B = material("MC | Tower Violet Glass", (0.12, 0.045, 0.17), 0.65, 0.24)
CONCRETE = material("MC | Concrete", (0.19, 0.23, 0.29), 0.25, 0.72)
NEON_CYAN = material("MC | Neon Cyan", (0.01, 0.62, 1.0), 0.15, 0.25, 4.0)
NEON_MAGENTA = material("MC | Neon Magenta", (0.9, 0.025, 0.42), 0.1, 0.25, 4.0)
NEON_GOLD = material("MC | Neon Gold", (1.0, 0.34, 0.025), 0.05, 0.3, 3.0)
WINDOW = material("MC | Lit Windows", (0.35, 0.68, 1.0), 0.0, 0.35, 1.8)
RED = material("MC | Alert Red", (1.0, 0.015, 0.025), 0.0, 0.25, 4.0)
GREEN = material("MC | Recovery Green", (0.015, 1.0, 0.12), 0.0, 0.25, 4.0)
WHITE = material("MC | Holo White", (0.7, 0.9, 1.0), 0.0, 0.2, 2.5)
AARAV_JACKET = material("Aarav | Jacket Placeholder", (0.025, 0.12, 0.28), 0.15, 0.5)
MAYA_JACKET = material("Maya | Jacket Placeholder", (0.32, 0.045, 0.18), 0.15, 0.5)
SKIN = material("Character | Skin Placeholder", (0.48, 0.27, 0.18), 0, 0.75)
DARK = material("Character | Dark Trousers", (0.025, 0.035, 0.055), 0.1, 0.7)
CAR_MATS = [
    material("Traffic | Cyan", (0.015, 0.35, 0.55), 0.65, 0.25),
    material("Traffic | Magenta", (0.42, 0.025, 0.22), 0.6, 0.25),
    material("Traffic | Silver", (0.38, 0.46, 0.54), 0.75, 0.22),
    material("Traffic | Gold", (0.55, 0.22, 0.025), 0.65, 0.25),
]

def cube(name, loc, dims, mat, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Soft edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return move_to(o, collection)

def add_text(name, body, loc, size, mat, collection, rotation=(0,0,0)):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.002
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rotation
    if mat:
        curve.materials.append(mat)
    return obj

# Ground and broad intersecting roads.
cube("Mega City Ground", (0,0,-1.0), (620,620,1.6), GROUND, CITY)
ROAD_SPACING = 72
ROAD_WIDTH = 19
for i in range(-4,5):
    p = i * ROAD_SPACING
    cube(f"Road East West {i}", (0,p,-0.08), (620,ROAD_WIDTH,0.18), ASPHALT, ROADS)
    cube(f"Road North South {i}", (p,0,-0.07), (ROAD_WIDTH,620,0.18), ASPHALT, ROADS)
    # simple lane dashes
    for j in range(-12,13):
        d = j * 22
        cube(f"Lane Dash EW {i}_{j}", (d,p,-0.0), (9,0.22,0.025), NEON_GOLD, ROADS)
        cube(f"Lane Dash NS {i}_{j}", (p,d,0.01), (0.22,9,0.025), NEON_GOLD, ROADS)

# Procedural skyscraper blocks between avenues.
for gx in range(-4,5):
    for gy in range(-4,5):
        if gx == 0 or gy == 0:
            continue
        cx = gx*ROAD_SPACING + random.uniform(-13,13)
        cy = gy*ROAD_SPACING + random.uniform(-13,13)
        w = random.uniform(28,43)
        d = random.uniform(28,43)
        h = random.uniform(42,165)
        base = random.choice([GLASS_A, GLASS_B, CONCRETE])
        tower = cube(f"SKYSCRAPER_{gx}_{gy}", (cx,cy,h/2), (w,d,h), base, CITY, 0.8)
        # rooftop crown
        cube(f"Tower Crown {gx}_{gy}", (cx,cy,h+1.2), (w*0.72,d*0.72,2.4), CONCRETE, CITY, 0.35)
        # neon vertical corner strips
        accent = NEON_CYAN if (gx+gy)%2 == 0 else NEON_MAGENTA
        for sx in (-1,1):
            cube(f"Tower Neon {gx}_{gy}_{sx}", (cx+sx*(w/2+0.035),cy,h/2), (0.10,0.16,h*0.88), accent, CITY)
        # a few readable lit facade bands
        for level in range(4, int(h)-5, 13):
            cube(f"Window band {gx}_{gy}_{level}", (cx,cy-d/2-0.06,level), (w*0.72,0.08,0.28), WINDOW, CITY)

# Central landmark tower.
cube("CENTRAL DATA SPIRE", (0,0,100), (34,34,200), GLASS_A, CITY, 1.0)
for z in range(8,198,12):
    cube(f"Data Spire Neon Band {z}", (0,-17.3,z), (29,0.18,0.32), NEON_CYAN, CITY)

# Traffic cars: simple blocks animated along avenues, loop-like passes.
for idx in range(24):
    lane_y = random.choice([-144,-72,72,144])
    start_x = random.uniform(-270,270)
    length = random.uniform(4.2,6.2)
    car = cube(f"TRAFFIC_CAR_{idx:02d}", (start_x,lane_y,0.95), (length,2.25,1.25),
               random.choice(CAR_MATS), ROADS, 0.28)
    # window block
    cube(f"Traffic Window {idx}", (start_x,lane_y,1.67), (length*0.48,1.72,0.45),
         GLASS_A, ROADS, 0.12)
    start = 1 + idx*7
    end = start + 900
    car.location.x = -290
    car.keyframe_insert(data_path="location", frame=start)
    car.location.x = 290
    car.keyframe_insert(data_path="location", frame=end)
    if car.animation_data and car.animation_data.action:
        for fc in car.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"

# Main character stand-ins. Replace by importing final rigged models.
def make_character(name, x, y, jacket):
    root_obj = bpy.data.objects.new(name+"_ROOT", None)
    CHAR.objects.link(root_obj)
    parts = []
    parts.append(cube(name+"_Torso",(x,y,1.45),(0.72,0.42,0.95),jacket,CHAR,0.12))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.28, location=(x,y,2.17))
    head = move_to(bpy.context.object, CHAR)
    head.name = name+"_Head"
    head.data.materials.append(SKIN)
    parts.append(head)
    parts.append(cube(name+"_Leg_L",(x-0.19,y,0.62),(0.23,0.28,0.78),DARK,CHAR,0.05))
    parts.append(cube(name+"_Leg_R",(x+0.19,y,0.62),(0.23,0.28,0.78),DARK,CHAR,0.05))
    for p in parts:
        p.parent = root_obj
    return root_obj

aarav = make_character("AARAV_BLOCKOUT", -3.0, -4.0, AARAV_JACKET)
maya = make_character("MAYA_BLOCKOUT", 3.0, -4.0, MAYA_JACKET)
# Simple placeholder travel path for the chase blocking; replace with rigged acting later.
for frame, loc in [(1801,(-3.0,-4.0,0.0)), (2700,(-35.0,45.0,0.0)), (3900,(-90.0,92.0,0.0)), (5100,(-110.0,110.0,0.0))]:
    aarav.location = loc
    aarav.keyframe_insert(data_path="location", frame=frame)
for frame, loc in [(1801,(3.0,-4.0,0.0)), (2700,(-30.0,48.0,0.0)), (3900,(-86.0,96.0,0.0)), (5100,(-106.0,113.0,0.0))]:
    maya.location = loc
    maya.keyframe_insert(data_path="location", frame=frame)

# Maya wrist device and hologram panel.
cube("Maya Wrist Device", (3.45,-4.1,1.55), (0.35,0.15,0.20), NEON_CYAN, PROPS, 0.04)
holo = cube("Maya Hologram Panel", (4.4,-3.7,2.35), (1.8,0.06,0.85), NEON_CYAN, PROPS, 0.04)
holo_text = add_text("Maya Hologram Text", "MAYA // LINK ACTIVE", (3.62,-3.65,2.3), 0.16, WHITE, PROPS)
for o in (holo,holo_text):
    o.hide_render = True
    o.keyframe_insert(data_path="hide_render", frame=151)
    o.hide_render = False
    o.keyframe_insert(data_path="hide_render", frame=240)
    o.hide_render = True
    o.keyframe_insert(data_path="hide_render", frame=1750)

# Rooftop chase platform.
cube("CHASE ROOFTOP PLATFORM", (-110,110,2), (72,55,3), CONCRETE, CITY, 0.5)
cube("Rooftop Neon Edge", (-110,82,3.6), (70,0.25,0.18), NEON_MAGENTA, CITY)

# Server rack and USB insertion prop.
rack = cube("SERVER RACK", (0,210,5.0), (7.0,2.0,10.0), CONCRETE, PROPS, 0.25)
for row in range(8):
    z = 1.2 + row*1.05
    cube(f"Server Rack Slot {row}", (0,208.92,z), (3.8,0.08,0.55), ASPHALT, PROPS, 0.035)
status_mat = material("MC | Animated Server Status", (1.0,0.015,0.025), 0.0, 0.25, 4.0)
status = cube("SERVER STATUS LIGHT", (2.35,208.82,8.6), (0.32,0.12,0.32), status_mat, PROPS, 0.05)
usb = cube("USB PENDRIVE", (-1.5,205.5,4.3), (0.25,1.0,0.16), WHITE, PROPS, 0.04)
usb.keyframe_insert(data_path="location", frame=6300)
usb.location.y = 208.75
usb.keyframe_insert(data_path="location", frame=6420)
# Animate the same shader from alert red to recovery green.
status_bsdf = status_mat.node_tree.nodes.get("Principled BSDF")
for frame, color in [(6301,(1.0,0.015,0.025)), (6419,(1.0,0.015,0.025)), (6420,(0.015,1.0,0.12)), (9000,(0.015,1.0,0.12))]:
    status_bsdf.inputs["Base Color"].default_value = (*color,1)
    status_bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=frame)
    status_bsdf.inputs["Emission Color"].default_value = (*color,1)
    status_bsdf.inputs["Emission Color"].keyframe_insert(data_path="default_value", frame=frame)
    status_bsdf.inputs["Emission Strength"].default_value = 4.0
    status_bsdf.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=frame)

# World and atmospheric city lighting.
world = scene.world or bpy.data.worlds.new("MY CITY NIGHT WORLD")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.006,0.012,0.035,1)
bg.inputs["Strength"].default_value = 0.32

def area_light(name, loc, color, energy, size, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name,data)
    LIGHTS.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    return obj

area_light("Neon Fill Cyan", (0,-80,90), (0.05,0.35,1.0), 7000, 80, (0,0,20))
area_light("Neon Fill Magenta", (90,20,75), (1.0,0.04,0.32), 5500, 70, (0,0,15))
area_light("Rooftop Key", (-110,65,45), (0.25,0.45,1.0), 3000, 35, (-110,110,0))

# Opening camera: face-height hook, then an establishing aerial camera move.
cam_data = bpy.data.cameras.new("MY CITY CINEMATIC CAMERA")
camera = bpy.data.objects.new("MY CITY CINEMATIC CAMERA", cam_data)
scene.collection.objects.link(camera)
camera.data.lens = 48
camera.location = (-3,-13,2.1)
camera.rotation_euler = (Vector((-3,-4,1.8))-camera.location).to_track_quat("-Z","Y").to_euler()
scene.camera = camera

scene.timeline_markers.clear()
for name, frame in [
    ("HOOK 00:00",1),("CITY OVERVIEW 00:05",151),("CHASE 01:00",1801),
    ("CLIMAX 03:30",6301),("OUTRO 04:45",8551),("END 05:00",9000)
]:
    scene.timeline_markers.new(name, frame=frame)

scene.frame_set(1)
print("MY CITY: cyber-city environment, traffic, character and story placeholders created.")
print("Next: run scripts/camera_move.py, then scripts/render_config.py.")
