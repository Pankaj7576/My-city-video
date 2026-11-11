import bpy
from mathutils import Vector

"""
MY CITY VIDEO — 5-scene camera and timing automation.
Run after scene_setup.py. 5 minutes = 9000 frames at 30 FPS.
Camera cuts are represented by short eased transitions between authored
camera poses; edit the positions/targets to match the final city layout.
"""

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 9000
camera = scene.camera
if camera is None:
    raise RuntimeError("No active camera. Run scripts/scene_setup.py first.")

def look_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

def pose(frame, location, target, lens=48):
    camera.location = location
    look_at(camera, target)
    camera.data.lens = lens
    camera.keyframe_insert(data_path="location", frame=frame)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    camera.data.keyframe_insert(data_path="lens", frame=frame)

# Remove old camera animation to make this script safe to rerun.
if camera.animation_data:
    camera.animation_data_clear()

# Scene 1 — 00:00–00:05 (frames 1–150): fast face push-in.
pose(1,  (-3.0,-15.0,2.8), (-3.0,-4.0,1.85), 38)
pose(36, (-3.0,-9.0,2.45),  (-3.0,-4.0,1.95), 55)
pose(150,(-2.7,-7.2,2.25),  (-3.0,-4.0,2.05), 72)

# Scene 2 — 00:05–01:00 (151–1800): high aerial fly-through.
pose(151, (-245,-265,155), (0,0,25), 34)
pose(780, (-105,-95,95),   (0,0,45), 38)
pose(1350,(45,65,82),      (0,35,25), 42)
pose(1800,(150,105,60),    (65,60,18), 46)

# Scene 3 — 01:00–03:30 (1801–6300): street-level chase.
pose(1801,(-12,-28,6), (-3,-4,1.5), 42)
pose(2700,(-35,45,8), (-65,70,2), 48)
pose(3900,(-90,92,9), (-110,110,2), 50)
pose(5100,(-120,135,7),(-110,110,2), 52)
pose(6300,(-8,195,7),(0,210,5), 60)

# Scene 4 — 03:30–04:45 (6301–8550): USB/server close-up, recovery.
pose(6301,(-5,196,6.5), (0,209,4.5), 70)
pose(6420,(-2.7,204.8,4.9), (-0.4,208.8,4.3), 90)
pose(7200,(-2.7,204.8,4.9), (-0.4,208.8,4.3), 90)
pose(7900,(0,185,12), (0,210,5), 55)
pose(8550,(0,165,22), (0,210,8), 48)

# Scene 5 — 04:45–05:00 (8551–9000): rooftop quiet beat and sky tilt.
pose(8551,(-110,78,8), (-110,110,2), 45)
pose(8800,(-110,78,18),(-110,110,0), 42)
pose(9000,(-110,78,58),(-110,110,90), 38)

# Smooth camera movement between poses. Linear is avoided for more cinematic easing.
if camera.animation_data and camera.animation_data.action:
    for fc in camera.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"

# Exact scene markers, timecode at 30 fps.
scene.timeline_markers.clear()
for name, frame in [
    ("01 HOOK | 00:00",1),
    ("02 CITY OVERVIEW | 00:05",151),
    ("03 CHASE | 01:00",1801),
    ("04 CLIMAX | 03:30",6301),
    ("05 OUTRO | 04:45",8551),
    ("END | 05:00",9000),
]:
    scene.timeline_markers.new(name, frame=frame)

scene.frame_set(1)
print("MY CITY: 5-minute camera animation configured (9000 frames at 30 FPS).")
