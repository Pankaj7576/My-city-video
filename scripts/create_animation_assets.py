import bpy
from pathlib import Path
from mathutils import Vector

"""
Create simple editable placeholder actions and export FBX files.
Run after character base assets have been generated.
The run cycle is a reusable blockout action; interaction is a simple
arm/hand reach gesture placeholder. Replace with polished character rigging.
"""

ROOT = Path(bpy.path.abspath("//"))
OUT = ROOT / "assets" / "animations"
OUT.mkdir(parents=True, exist_ok=True)

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def build_rig_stub():
    arm_data=bpy.data.armatures.new("Motion_Blockout_Rig")
    arm=bpy.data.objects.new("Motion_Blockout_Rig",arm_data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    root=arm_data.edit_bones.new("root"); root.head=(0,0,0); root.tail=(0,0,1)
    spine=arm_data.edit_bones.new("spine"); spine.head=(0,0,1); spine.tail=(0,0,2); spine.parent=root
    head=arm_data.edit_bones.new("head"); head.head=(0,0,2); head.tail=(0,0,2.5); head.parent=spine
    arm_l=arm_data.edit_bones.new("arm.L"); arm_l.head=(0,0,1.8); arm_l.tail=(-0.6,0,1.3); arm_l.parent=spine
    arm_r=arm_data.edit_bones.new("arm.R"); arm_r.head=(0,0,1.8); arm_r.tail=(0.6,0,1.3); arm_r.parent=spine
    leg_l=arm_data.edit_bones.new("leg.L"); leg_l.head=(0,0,1); leg_l.tail=(-0.2,0,0); leg_l.parent=root
    leg_r=arm_data.edit_bones.new("leg.R"); leg_r.head=(0,0,1); leg_r.tail=(0.2,0,0); leg_r.parent=root
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.select_set(False)
    return arm

def animate_bone(arm, bone_name, frames):
    pb=arm.pose.bones[bone_name]
    for frame, rot in frames:
        pb.rotation_mode="XYZ"; pb.rotation_euler=rot
        pb.keyframe_insert(data_path="rotation_euler",frame=frame,group=bone_name)

def export_action(arm, action_name, filename):
    action=bpy.data.actions.new(action_name)
    arm.animation_data_create(); arm.animation_data.action=action
    bpy.ops.object.select_all(action="DESELECT"); arm.select_set(True)
    bpy.context.view_layer.objects.active=arm
    bpy.ops.export_scene.fbx(filepath=str(OUT/filename),use_selection=True,object_types={"ARMATURE"},bake_anim=True,add_leaf_bones=False)
    return action

clear_scene()
rig=build_rig_stub()
run=export_action(rig,"Run_Cycle_Blockout","run_cycle.fbx")
for bone, frames in {
    "leg.L":[(1,(0,0,0)),(7,(0.7,0,0)),(13,(0,0,0)),(19,(-0.7,0,0)),(25,(0,0,0))],
    "leg.R":[(1,(0,0,0)),(7,(-0.7,0,0)),(13,(0,0,0)),(19,(0.7,0,0)),(25,(0,0,0))],
    "arm.L":[(1,(0,0,0)),(7,(-0.5,0,0)),(13,(0,0,0)),(19,(0.5,0,0)),(25,(0,0,0))],
    "arm.R":[(1,(0,0,0)),(7,(0.5,0,0)),(13,(0,0,0)),(19,(-0.5,0,0)),(25,(0,0,0))],
}.items(): animate_bone(rig,bone,frames)
bpy.context.scene.frame_start=1; bpy.context.scene.frame_end=25
bpy.ops.object.select_all(action="DESELECT"); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(OUT/"run_cycle.fbx"),use_selection=True,object_types={"ARMATURE"},bake_anim=True,add_leaf_bones=False)

# Interaction gesture: reach forward and return.
for bone, frames in {
    "arm.R":[(1,(0,0,0)),(10,(-0.9,0,0.2)),(24,(-0.9,0,0.2)),(36,(0,0,0))],
    "spine":[(1,(0,0,0)),(10,(0.12,0,0)),(24,(0.12,0,0)),(36,(0,0,0))],
}.items(): animate_bone(rig,bone,frames)
bpy.context.scene.frame_start=1; bpy.context.scene.frame_end=36
bpy.ops.object.select_all(action="DESELECT"); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(OUT/"interaction.fbx"),use_selection=True,object_types={"ARMATURE"},bake_anim=True,add_leaf_bones=False)
print("Exported placeholder FBX actions. Retarget them to final character rigs before final production.")
