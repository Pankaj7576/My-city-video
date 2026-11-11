# MY CITY VIDEO

A Blender-based cinematic 3D video project.

## Current setup
- Aspect ratio: 16:9
- Resolution: 3840 × 2160 (4K)
- Frame rate: 30 FPS
- Main characters: Aarav and Maya (visual designs/story details pending)
- Environment: large procedural city foundation

## Folder layout
- `assets/characters/` — character models
- `assets/city_models/` — city models and props
- `assets/textures/` — materials and textures
- `scripts/` — Blender Python setup and animation scripts
- `output/` — rendered video output

## Run in Blender
Open Blender, switch to the Scripting workspace, load and run:
1. `scripts/scene_setup.py`
2. `scripts/camera_move.py`
3. `scripts/render_config.py`

The city is a procedural starting environment. Final character designs, story scenes, dialogue, sound, and shot timing will be added after the complete story prompt is supplied.

## Render
The render script configures 4K, 16:9, 30 FPS and an MP4/H.264 output in `output/`. Rendering requires Blender on a computer with sufficient memory and storage.
