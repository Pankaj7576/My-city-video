from pathlib import Path
import runpy
import bpy

"""
MY CITY VIDEO — ONE-COMMAND PROJECT BUILDER
Run from repository root:
blender --background --python scripts/build_project.py

Builds the procedural city, replaces character blockouts with rigged Aarav/Maya,
creates the camera sequence, applies render settings, imports audio if generated,
and saves a complete editable Blender project.
"""

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

def run_script(filename):
    path = SCRIPTS / filename
    if not path.exists():
        raise FileNotFoundError(f"Required build script missing: {path}")
    print(f"\n===== MY CITY BUILD: {filename} =====")
    runpy.run_path(str(path), run_name="__main__")

run_script("scene_setup.py")
run_script("build_rigged_characters.py")
run_script("camera_move.py")
run_script("render_config.py")

# Audio is optional until the free asset-generation workflow has completed.
audio_importer = SCRIPTS / "import_dialogues_vse.py"
if audio_importer.exists():
    run_script("import_dialogues_vse.py")
else:
    print("Audio importer not found; continuing with a silent picture edit.")

project_file = ROOT / "my_city_project.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(project_file))
print("\nBUILD COMPLETE")
print(f"Project: {project_file}")
print("Render with: blender --background my_city_project.blend --render-anim")
print("Note: final 4K rendering time depends heavily on GPU/CPU and scene settings.")
