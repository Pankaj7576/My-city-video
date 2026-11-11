import bpy
from pathlib import Path
from mathutils import Vector

"""
Generate separate low-poly Blender base files for Aarav and Maya.
Run with Blender's Scripting workspace or:
blender --background --python scripts/create_character_assets.py
These are editable placeholder designs, not final approved character likenesses.
"""

ROOT = Path(bpy.path.abspath("//"))
OUT = ROOT / "assets" / "characters"
OUT.mkdir(parents=True, exist_ok=True)

def material(name, color, roughness=0.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    return m

def make_person(name, jacket_color, trouser_color, skin_color, hair_color, feminine=False):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    mats = {
        "skin": material(name+"_Skin", skin_color),
        "jacket": material(name+"_Jacket", jacket_color),
        "pants": material(name+"_Trousers", trouser_color),
        "hair": material(name+"_Hair", hair_color),
        "eye": material(name+"_Eyes", (0.025,0.018,0.015), 0.25),
        "shoe": material(name+"_Shoes", (0.025,0.03,0.04)),
    }
    parts = []
    def cube(label, loc, scale, mat, bevel=0.05):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        o=bpy.context.object; o.name=name+"_"+label; o.dimensions=scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.data.materials.append(mat)
        if bevel:
            mod=o.modifiers.new("Rounded low-poly edges","BEVEL"); mod.width=bevel; mod.segments=2
        parts.append(o); return o
    def sphere(label, loc, scale, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, location=loc)
        o=bpy.context.object; o.name=name+"_"+label; o.scale=scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.data.materials.append(mat); parts.append(o); return o

    cube("Torso",(0,0,1.42),(0.72,0.42,0.9),mats["jacket"],0.1)
    sphere("Head",(0,0,2.15),(0.31,0.29,0.37),mats["skin"])
    sphere("Hair",(0,0.015,2.39),(0.32,0.30,0.20),mats["hair"])
    for ex in (-0.115,0.115):
        sphere("Eye",(ex,-0.275,2.20),(0.035,0.018,0.045),mats["eye"])
    # Arms
    for side in (-1,1):
        arm=cube("Arm_"+str(side),(side*0.48,0,1.48),(0.22,0.25,0.78),mats["jacket"],0.08)
        arm.rotation_euler[1]=side*-0.12
        sphere("Hand_"+str(side),(side*0.51,-0.01,1.04),(0.13,0.13,0.13),mats["skin"])
    # Legs and shoes
    for side in (-1,1):
        cube("Leg_"+str(side),(side*0.19,0,0.65),(0.25,0.30,0.78),mats["pants"],0.06)
        cube("Shoe_"+str(side),(side*0.19,-0.10,0.17),(0.30,0.48,0.18),mats["shoe"],0.04)
    root=bpy.data.objects.new(name+"_ROOT",None); bpy.context.collection.objects.link(root)
    for p in parts: p.parent=root
    root.location=(0,0,0)
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True); bpy.context.view_layer.objects.active=root
    return root

characters = [
    ("Aarav",(0.08,0.22,0.42),(0.08,0.09,0.12),(0.48,0.27,0.18),(0.035,0.022,0.018),False,"aarav_base.blend"),
    ("Maya",(0.48,0.10,0.25),(0.12,0.13,0.20),(0.66,0.40,0.27),(0.06,0.025,0.018),True,"maya_base.blend"),
]
for name,jacket,pants,skin,hair,feminine,filename in characters:
    make_person(name,jacket,pants,skin,hair,feminine)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/filename))
print("Created Aarav and Maya low-poly placeholder .blend files in assets/characters.")
