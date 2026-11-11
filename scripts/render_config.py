import bpy
from pathlib import Path

scene = bpy.context.scene

# 16:9 UHD 4K output
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.render.fps_base = 1.0

# High-quality render defaults
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "HIGH"
scene.render.ffmpeg.ffmpeg_preset = "GOOD"

# Save output relative to the project file.
project_dir = Path(bpy.path.abspath("//"))
output_dir = project_dir / "output"
output_dir.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(output_dir / "my_city_final.mp4")

# Color management
scene.view_settings.view_transform = "AgX"

print("MY CITY VIDEO: 4K 16:9, 30 FPS render configuration applied.")
print(f"Output: {scene.render.filepath}")
