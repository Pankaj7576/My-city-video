# My-city-video — asset and render workflow

## Folder structure

```text
My-city-video/
├── README.md
├── .gitignore
├── assets/
│   ├── characters/
│   │   ├── aarav_base.blend
│   │   ├── maya_base.blend
│   │   └── README.md
│   ├── animations/
│   │   ├── run_cycle.fbx
│   │   ├── interaction.fbx
│   │   └── README.md
│   ├── city_models/
│   │   └── README.md
│   ├── textures/
│   │   └── README.md
│   └── audio/
│       ├── dialogues/
│       ├── sfx/
│       └── AUDIO_CUE_SHEET.md
├── scripts/
│   ├── scene_setup.py
│   ├── camera_move.py
│   ├── render_config.py
│   ├── create_character_assets.py
│   ├── create_animation_assets.py
│   └── setup_visual_placeholders.py
└── output/
    └── .gitkeep
```

## File naming

- Characters: `aarav_base.blend`, `maya_base.blend`; later use versioned names such as `aarav_v002.blend`.
- Animation FBX: `run_cycle.fbx`, `interaction.fbx`; keep action names and armature bone names consistent.
- Audio: `maya_comms_guide.wav`, `aarav_server_guide.wav`, `city_ambience.wav`, `siren_short.wav`.
- Textures: lowercase snake_case and include resolution when useful, e.g. `tower_glass_4k_basecolor.png`.
- Renders: `my_city_preview_####.png`, `my_city_final.mp4`.

## Blender run order

From the repository root:

```bash
blender --background --python scripts/scene_setup.py
blender --background --python scripts/camera_move.py
blender --background --python scripts/render_config.py
blender --background my_city_project.blend --python scripts/import_dialogues_vse.py
```

For a single Blender session, open Blender and run those scripts in that order from the Scripting workspace. If scene_setup and camera_move are run in separate background invocations, save a .blend file between steps or use the combined command below.

### One-session pipeline (recommended)

```bash
blender --background --python-expr "exec(compile(open('scripts/scene_setup.py', encoding='utf-8').read(), 'scripts/scene_setup.py', 'exec')); exec(compile(open('scripts/camera_move.py', encoding='utf-8').read(), 'scripts/camera_move.py', 'exec')); exec(compile(open('scripts/render_config.py', encoding='utf-8').read(), 'scripts/render_config.py', 'exec')); bpy.ops.wm.save_as_mainfile(filepath='my_city_project.blend')"
```

Then render the saved project:

```bash
blender -b my_city_project.blend -a
```

## Audio assembly

The VSE importer is `scripts/import_dialogues_vse.py`. Add the dialogue MP3s listed in `assets/audio/AUDIO_CUE_SHEET.md` to `assets/audio/dialogues/`; optional music beds go in `assets/audio/` and sound effects in `assets/audio/sfx/`. The importer applies available files to the VSE with assigned channels and fades, and reports any missing clips. It does not fabricate silent audio. Actual voice/music assets are not included until generated or supplied.

## Importing final characters

1. Open the final rigged .blend or FBX from Blender's File > Import menu.
2. Keep character forward direction consistent (the project uses +Y as the street depth axis and Z up; check the imported model orientation).
3. Place the character root at the blockout root position, then align scale to roughly 1.8–2.0 Blender units tall.
4. Retarget run_cycle and interaction to the final armature using a compatible retargeting workflow/add-on. Confirm bone naming and rest pose first.
5. Replace the blockout objects only after the final rig and animation have been checked in the chase and climax shots.

## Git and GitHub notes

- Commit Python scripts, Markdown, small original textures, and project configuration.
- Blender .blend files and FBX files are binary assets; Git LFS is recommended as they grow.
- Avoid committing rendered 4K MP4s, caches, temporary renders, and Blender backup files to ordinary Git.
- Never commit copyrighted audio or assets unless you have the rights to use them.

## Current limitations

The Python scripts generate a procedural starting environment and temporary props. They do not create finished human-quality character rigs, final acting, lip-sync, dialogue recordings, or a polished final render. Run and inspect the scripts in your installed Blender version before treating the scene as production-ready.
