import bpy
from mathutils import Vector

scene = bpy.context.scene
camera = scene.camera

if camera is None:
    raise RuntimeError("Run scene_setup.py first: no active camera found.")

# Reusable establishing-shot move. Story-specific camera paths will be
# authored after the complete script/story and scene timings are provided.
camera.location = (300, -360, 270)
camera.keyframe_insert(data_path="location", frame=1)

camera.location = (170, -210, 150)
camera.keyframe_insert(data_path="location", frame=150)

camera.location = (65, -95, 75)
camera.keyframe_insert(data_path="location", frame=300)

for frame in (1, 150, 300):
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)

if camera.animation_data and camera.animation_data.action:
    for fcurve in camera.animation_data.action.fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = "BEZIER"

scene.frame_set(1)
print("MY CITY: overview camera animation added (frames 1–300).")
