import bpy
import random
from mathutils import Vector

# Reproducible procedural city foundation.
random.seed(27)
scene = bpy.context.scene

# Clear default objects only; preserve project collections if re-running.
for obj in list(bpy.data.objects):
    if obj.name in {"Cube", "Camera", "Light"}:
        bpy.data.objects.remove(obj, do_unlink=True)

def make_material(name, color, metallic=0.0, roughness=0.7):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

asphalt = make_material("Road | Asphalt", (0.035, 0.045, 0.055), roughness=0.92)
concrete = make_material("City | Concrete", (0.34, 0.38, 0.42), roughness=0.82)
glass = make_material("City | Blue Glass", (0.055, 0.19, 0.28), metallic=0.55, roughness=0.22)
ground_mat = make_material("Ground | Dark", (0.12, 0.16, 0.13), roughness=1.0)

def cube_obj(name, location, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("Soft architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj

# Large ground plane
cube_obj("Mega City Ground", (0, 0, -0.6), (520, 520, 1), ground_mat)

# City grid: broad avenues with building blocks between them.
road_width = 18
block_spacing = 62
for i in range(-4, 5):
    pos = i * block_spacing
    cube_obj(f"East-West Avenue {i}", (0, pos, -0.05), (520, road_width, 0.18), asphalt)
    cube_obj(f"North-South Avenue {i}", (pos, 0, -0.04), (road_width, 520, 0.18), asphalt)

# Buildings distributed through the city grid.
for gx in range(-4, 5):
    for gy in range(-4, 5):
        if gx == 0 or gy == 0:
            continue
        cx = gx * block_spacing + random.uniform(-12, 12)
        cy = gy * block_spacing + random.uniform(-12, 12)
        width = random.uniform(22, 38)
        depth = random.uniform(22, 38)
        height = random.uniform(24, 115)
        material = glass if random.random() > 0.35 else concrete
        cube_obj(
            f"Tower_{gx}_{gy}",
            (cx, cy, height / 2),
            (width, depth, height),
            material,
            bevel=0.35
        )

# Lighting and world
world = scene.world or bpy.data.worlds.new("MY CITY World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.16, 0.20, 0.28, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45

sun_data = bpy.data.lights.new("City Sun", type="SUN")
sun = bpy.data.objects.new("City Sun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (0.45, -0.35, -0.4)
sun_data.energy = 2.0

# A temporary overview camera; story-specific shots will replace this.
camera_data = bpy.data.cameras.new("City Overview Camera")
camera = bpy.data.objects.new("City Overview Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (300, -360, 270)
target = Vector((0, 0, 20))
direction = target - camera.location
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
camera_data.lens = 42
scene.camera = camera

scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.frame_start = 1
scene.frame_end = 300

print("MY CITY: procedural mega-city foundation created.")
