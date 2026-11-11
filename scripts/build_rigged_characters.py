import bpy
import math
from pathlib import Path
from mathutils import Vector

"""
MY CITY VIDEO — RIGGED CHARACTER BUILDER
Blender 4.x. Run AFTER scene_setup.py and BEFORE camera_move.py.
Creates stylized, articulated 3D Aarav and Maya characters with armatures,
rigid-part skinning, run cycles, and a simple interaction gesture.
This is a procedural production block-in, not photorealistic character art.
"""

scene = bpy.context.scene
ROOT = Path(bpy.path.abspath("//"))
OUT = ROOT / "assets" / "characters"
OUT.mkdir(parents=True, exist_ok=True)
ANIM_OUT = ROOT / "assets" / "animations"
ANIM_OUT.mkdir(parents=True, exist_ok=True)

def mat(name, color, metallic=0.0, rough=0.55, emission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if emission:
        p.inputs["Emission Color"].default_value = (*color, 1)
        p.inputs["Emission Strength"].default_value = emission
    return m

SKIN = mat("Hero | warm skin", (0.48, 0.27, 0.18))
DARK = mat("Hero | graphite trousers", (0.018, 0.027, 0.045), 0.18)
SHOE = mat("Hero | boots", (0.012, 0.018, 0.026), 0.25)
HAIR = mat("Hero | dark hair", (0.018, 0.012, 0.01))
EYE = mat("Hero | eyes", (0.008, 0.012, 0.02), rough=0.2)
CYAN = mat("Hero | cyan tech trim", (0.01, 0.55, 0.95), 0.2, 0.25, 2.5)
PINK = mat("Hero | magenta tech trim", (0.9, 0.025, 0.28), 0.2, 0.25, 2.0)
AARAV_COAT = mat("Aarav | midnight blue jacket", (0.018, 0.075, 0.17), 0.25)
MAYA_COAT = mat("Maya | plum tech jacket", (0.20, 0.025, 0.105), 0.22)

def add_bone(eb, name, head, tail, parent=None):
    b = eb.new(name)
    b.head, b.tail = head, tail
    if parent:
        b.parent = parent
        b.use_connect = False
    return b

def make_rig(name, x, y, coat, accent, female=False):
    arm_data = bpy.data.armatures.new(name + "_Armature")
    rig = bpy.data.objects.new(name + "_RIG", arm_data)
    scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones
    root = add_bone(eb, "root", (0,0,0.05), (0,0,0.65))
    pelvis = add_bone(eb, "pelvis", (0,0,0.72), (0,0,1.02), root)
    spine = add_bone(eb, "spine", (0,0,1.02), (0,0,1.62), pelvis)
    chest = add_bone(eb, "chest", (0,0,1.48), (0,0,1.83), spine)
    neck = add_bone(eb, "neck", (0,0,1.82), (0,0,2.02), chest)
    head = add_bone(eb, "head", (0,0,2.00), (0,0,2.48), neck)
    for side, sign in (("L",-1),("R",1)):
        shoulder=(sign*0.34,0,1.70)
        elbow=(sign*0.55,0,1.35)
        wrist=(sign*0.60,-0.01,1.06)
        hand=(sign*0.61,-0.02,0.91)
        upper=add_bone(eb,"upper_arm."+side,shoulder,elbow,chest)
        add_bone(eb,"forearm."+side,elbow,wrist,upper)
        add_bone(eb,"hand."+side,wrist,hand,eb["forearm."+side])
        hip=(sign*0.18,0,0.82)
        knee=(sign*0.19,0,0.43)
        ankle=(sign*0.19,0,0.12)
        thigh=add_bone(eb,"thigh."+side,hip,knee,pelvis)
        add_bone(eb,"shin."+side,knee,ankle,thigh)
        add_bone(eb,"foot."+side,ankle,(sign*0.19,-0.25,0.08),eb["shin."+side])
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.location=(x,y,0)
    rig.show_in_front=True
    rig.data.display_type="OCTAHEDRAL"
    rig.select_set(False)

    def piece(label, loc, scale, material, bone, shape="sphere"):
        if shape=="cube":
            bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
            ob=bpy.context.object
            ob.dimensions=scale
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bevel=ob.modifiers.new("Soft tailored edges","BEVEL")
            bevel.width=0.055
            bevel.segments=3
        elif shape=="cylinder":
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1, depth=1, location=loc)
            ob=bpy.context.object
            ob.dimensions=scale
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bevel=ob.modifiers.new("Rounded segment","BEVEL")
            bevel.width=0.035
            bevel.segments=2
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
            ob=bpy.context.object
            ob.scale=scale
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        ob.name=name+"_"+label
        ob.data.materials.append(material)
        vg=ob.vertex_groups.new(name=bone)
        vg.add(list(range(len(ob.data.vertices))),1.0,"REPLACE")
        ob.parent=rig
        mod=ob.modifiers.new("Character Armature","ARMATURE")
        mod.object=rig
        ob.matrix_parent_inverse=rig.matrix_world.inverted()
        return ob

    # Torso, layered jacket, neck and expressive head.
    piece("Pelvis",(0,0,0.86),(0.46,0.30,0.34),DARK,"pelvis")
    piece("Jacket",(0,0,1.40),(0.72,0.39,0.83),coat,"spine","cube")
    piece("ChestPanel",(0,-0.205,1.48),(0.38,0.035,0.47),accent,"chest","cube")
    piece("Neck",(0,0,1.91),(0.14,0.14,0.22),SKIN,"neck")
    piece("Head",(0,-0.005,2.17),(0.29,0.27,0.36),SKIN,"head")
    piece("HairCap",(0,0.015,2.39),(0.30,0.28,0.19),HAIR,"head")
    piece("HairFringe",(0,-0.235,2.36),(0.28,0.07,0.12),HAIR,"head")
    for s in (-1,1):
        piece("Eye"+str(s),(s*0.105,-0.251,2.20),(0.035,0.018,0.045),EYE,"head")
    # Arms, hands, legs and boots are separate weighted rigid mesh pieces.
    for side, sign in (("L",-1),("R",1)):
        piece("Shoulder"+side,(sign*0.37,0,1.69),(0.27,0.30,0.29),coat,"upper_arm."+side)
        piece("UpperArm"+side,(sign*0.45,0,1.49),(0.21,0.24,0.43),coat,"upper_arm."+side,"cylinder")
        piece("Forearm"+side,(sign*0.57,-0.005,1.20),(0.18,0.21,0.36),coat,"forearm."+side,"cylinder")
        piece("Glove"+side,(sign*0.61,-0.015,0.98),(0.15,0.16,0.16),SKIN,"hand."+side)
        piece("Thigh"+side,(sign*0.18,0,0.62),(0.24,0.27,0.45),DARK,"thigh."+side,"cylinder")
        piece("Shin"+side,(sign*0.19,0,0.28),(0.19,0.22,0.35),DARK,"shin."+side,"cylinder")
        piece("Boot"+side,(sign*0.19,-0.13,0.10),(0.25,0.43,0.17),SHOE,"foot."+side,"cube")
        piece("KneeLight"+side,(sign*0.19,-0.125,0.43),(0.11,0.025,0.07),accent,"shin."+side,"cube")
    # A small communicator on Maya's forearm; a chest badge on Aarav.
    if female:
        piece("WristDisplay",(0.60,-0.13,1.12),(0.16,0.035,0.12),CYAN,"forearm.R","cube")
    else:
        piece("ChestBadge",(0.20,-0.235,1.65),(0.10,0.025,0.12),CYAN,"chest","cube")

    # Reusable run cycle, keyed on the armature's pose bones.
    rig.animation_data_create()
    run = bpy.data.actions.new(name+"_RunCycle")
    rig.animation_data.action=run
    run_keys = [
        (1,0.0),(7,0.62),(13,0.0),(19,-0.62),(25,0.0)
    ]
    for frame, swing in run_keys:
        scene.frame_set(frame)
        for side, sign in (("L",-1),("R",1)):
            thigh=rig.pose.bones["thigh."+side]
            shin=rig.pose.bones["shin."+side]
            upper=rig.pose.bones["upper_arm."+side]
            fore=rig.pose.bones["forearm."+side]
            thigh.rotation_mode="XYZ"
            shin.rotation_mode="XYZ"
            upper.rotation_mode="XYZ"
            fore.rotation_mode="XYZ"
            thigh.rotation_euler.x = swing*sign
            shin.rotation_euler.x = max(0.0,-swing*sign)*0.85
            upper.rotation_euler.x = -swing*sign*0.75
            fore.rotation_euler.x = -0.18
            for pb in (thigh,shin,upper,fore):
                pb.keyframe_insert(data_path="rotation_euler",frame=frame,group=pb.name)
        rig.pose.bones["spine"].rotation_euler.x=0.04*math.sin(frame*math.pi/12)
        rig.pose.bones["spine"].keyframe_insert(data_path="rotation_euler",frame=frame,group="spine")
    for fc in run.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation="BEZIER"
    for fc in run.fcurves:
        fc.modifiers.new("CYCLES")
    run["description"]="Procedural 24-frame run cycle; loop with Cycles modifier"

    # Store a separate reach/communicator action as a named action datablock.
    reach=bpy.data.actions.new(name+"_ReachGesture")
    rig.animation_data.action=reach
    for frame, angle in ((1,0.0),(10,-0.95),(24,-0.95),(36,0.0)):
        scene.frame_set(frame)
        pb=rig.pose.bones["upper_arm.R"]
        pb.rotation_mode="XYZ"
        pb.rotation_euler.x=angle
        pb.keyframe_insert(data_path="rotation_euler",frame=frame,group=pb.name)
        rig.pose.bones["forearm.R"].rotation_euler.x=angle*0.35
        rig.pose.bones["forearm.R"].keyframe_insert(data_path="rotation_euler",frame=frame,group="forearm.R")
    rig.animation_data.action=run
    rig["character_type"]="procedural_rigged_3d"
    rig["animation_actions"]=name+"_RunCycle, "+name+"_ReachGesture"
    return rig

# Remove old character blockout roots and their children from the previous scene build.
for ob in list(bpy.data.objects):
    if ob.name.startswith(("AARAV_BLOCKOUT","MAYA_BLOCKOUT")):
        bpy.data.objects.remove(ob,do_unlink=True)

aarav=make_rig("AARAV",-3.0,-4.0,AARAV_COAT,CYAN,False)
maya=make_rig("MAYA",3.0,-4.0,MAYA_COAT,PINK,True)

# Chase travel is animated on the rig root, while pose animation remains reusable.
for frame, loc in ((1801,(-3.0,-4.0,0.0)),(2700,(-35.0,45.0,0.0)),(3900,(-90.0,92.0,0.0)),(5100,(-110.0,110.0,0.0))):
    aarav.location=loc
    aarav.keyframe_insert(data_path="location",frame=frame)
for frame, loc in ((1801,(3.0,-4.0,0.0)),(2700,(-30.0,48.0,0.0)),(3900,(-86.0,96.0,0.0)),(5100,(-106.0,113.0,0.0))):
    maya.location=loc
    maya.keyframe_insert(data_path="location",frame=frame)

# Return scene to opening frame and save a character asset file with both rigs.
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"my_city_rigged_characters.blend"))
print("RIGGED CHARACTERS BUILT: Aarav and Maya, armatures, weighted body parts, run and reach actions.")
