"""
My City Video — VSE audio assembly
Blender 3.6+ / 4.x

Place generated/recorded MP3 or WAV files in assets/audio/ using the names below,
then run this script from the saved .blend project. Missing files are skipped
with clear warnings; the script never creates fake/silent dialogue.
"""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
AUDIO_ROOT = ROOT / "assets" / "audio"

# Frame positions are 30 fps, timeline starts at frame 0.
# The five-minute interval is frames 0..8999 (300 seconds).
DIALOGUES = [
    {
        "name": "DIALOGUE_AARAV_HOOK",
        "file": "aarav_hook_alert.mp3",
        "frame": 0,
        "channel": 1,
        "speaker": "Aarav",
        "line": "सिस्टम पूरी तरह लॉक होने में बस 5 मिनट बाकी हैं!",
        "volume": 1.00,
        "fade_in": 2,
        "fade_out": 5,
    },
    {
        "name": "DIALOGUE_MAYA_COMMS",
        "file": "maya_comm_start.mp3",
        "frame": 180,
        "channel": 2,
        "speaker": "Maya",
        "line": "आरव, सेंट्रल ग्रिड का फायरवॉल ब्रीच हो रहा है। जल्दी करो!",
        "volume": 1.00,
        "fade_in": 2,
        "fade_out": 5,
    },
    {
        "name": "DIALOGUE_AARAV_RUNNING",
        "file": "aarav_running_action.mp3",
        "frame": 1900,
        "channel": 1,
        "speaker": "Aarav",
        "line": "मैं मेन सर्वर टावर के पास पहुँच रहा हूँ, माया बैकअप संभालो!",
        "volume": 1.00,
        "fade_in": 2,
        "fade_out": 5,
    },
    {
        "name": "DIALOGUE_MAYA_CLIMAX",
        "file": "maya_climax_countdown.mp3",
        "frame": 6400,
        "channel": 2,
        "speaker": "Maya",
        "line": "बस 10 सेकंड बचे हैं आरव, पेनड्राइव कनेक्ट करो!",
        "volume": 1.00,
        "fade_in": 2,
        "fade_out": 4,
    },
    {
        "name": "DIALOGUE_OUTRO_AARAV_MAYA",
        "file": "aarav_maya_outro.mp3",
        "frame": 8600,
        "channel": 1,
        "speaker": "Aarav + Maya",
        "line": "मिशन सक्सेसफुल।",
        "volume": 1.00,
        "fade_in": 4,
        "fade_out": 12,
    },
]

# Optional beds/effects. They are imported only when the matching file exists.
OPTIONAL_AUDIO = [
    {"name": "MUSIC_OPENING_TENSION", "file": "music_opening_tension.mp3", "frame": 0, "channel": 4, "volume": 0.22, "fade_in": 45, "fade_out": 60},
    {"name": "MUSIC_CITY_CHASE", "file": "music_city_chase.mp3", "frame": 1800, "channel": 4, "volume": 0.20, "fade_in": 45, "fade_out": 60},
    {"name": "MUSIC_CLIMAX", "file": "music_climax.mp3", "frame": 5700, "channel": 4, "volume": 0.24, "fade_in": 30, "fade_out": 45},
    {"name": "MUSIC_OUTRO", "file": "music_rooftop_outro.mp3", "frame": 8550, "channel": 4, "volume": 0.18, "fade_in": 45, "fade_out": 60},
    {"name": "SFX_ALERT_PULSE", "file": "sfx_alert_pulse.wav", "frame": 0, "channel": 3, "volume": 0.55, "fade_in": 2, "fade_out": 15},
    {"name": "SFX_CITY_AMBIENCE", "file": "sfx_city_ambience.wav", "frame": 150, "channel": 5, "volume": 0.30, "fade_in": 45, "fade_out": 45},
    {"name": "SFX_RUNNING_FOOTSTEPS", "file": "sfx_running_footsteps.wav", "frame": 1800, "channel": 3, "volume": 0.45, "fade_in": 8, "fade_out": 20},
    {"name": "SFX_SERVER_USB", "file": "sfx_server_usb_connect.wav", "frame": 6400, "channel": 3, "volume": 0.60, "fade_in": 2, "fade_out": 20},
    {"name": "SFX_SYSTEM_RECOVERY", "file": "sfx_system_recovery.wav", "frame": 6600, "channel": 3, "volume": 0.45, "fade_in": 10, "fade_out": 45},
]

scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.frame_start = 0
scene.frame_end = 8999

editor = scene.sequence_editor_create()
strips = editor.strips if hasattr(editor, "strips") else editor.sequences

# Remove only strips created by this script, preserving other VSE work.
managed_prefixes = ("DIALOGUE_", "MUSIC_", "SFX_")
for strip in list(strips):
    if strip.name.startswith(managed_prefixes):
        strips.remove(strip)

def add_audio(item, folder):
    path = folder / item["file"]
    if not path.is_file():
        print("[AUDIO MISSING] {}".format(path))
        return None

    strip = strips.new_sound(
        name=item["name"],
        filepath=str(path),
        channel=item["channel"],
        frame_start=item["frame"],
    )
    strip.volume = item.get("volume", 1.0)
    strip.mute = False

    fade_in = max(0, int(item.get("fade_in", 0)))
    fade_out = max(0, int(item.get("fade_out", 0)))
    start = int(item["frame"])
    end = start + max(1, int(strip.frame_duration))

    if fade_in:
        strip.volume = 0.0
        strip.keyframe_insert(data_path="volume", frame=start)
        strip.volume = item.get("volume", 1.0)
        strip.keyframe_insert(data_path="volume", frame=min(start + fade_in, end))
    if fade_out:
        strip.volume = item.get("volume", 1.0)
        strip.keyframe_insert(data_path="volume", frame=max(start, end - fade_out))
        strip.volume = 0.0
        strip.keyframe_insert(data_path="volume", frame=end)

    print("[AUDIO ADDED] {} | frame {} | channel {} | {}".format(
        item["name"], start, item["channel"], path.name
    ))
    return strip

# Dialogue clips are required content, but absent files do not stop optional
# tracks from being assembled. A summary is printed at the end.
added_dialogues = []
for cue in DIALOGUES:
    strip = add_audio(cue, AUDIO_ROOT / "dialogues")
    if strip:
        added_dialogues.append(cue["name"])
    print("[DIALOGUE CUE] {}: {}".format(cue["speaker"], cue["line"]))

added_optional = []
for cue in OPTIONAL_AUDIO:
    strip = add_audio(cue, AUDIO_ROOT / "sfx" if cue["name"].startswith("SFX_") else AUDIO_ROOT)
    if strip:
        added_optional.append(cue["name"])

# Scene markers for editorial navigation.
markers = [
    ("HOOK", 0),
    ("CITY_OVERVIEW", 150),
    ("CHASE", 1800),
    ("SERVER_CLIMAX", 6300),
    ("ROOFTOP_OUTRO", 8550),
    ("END", 8999),
]
for marker_name, frame in markers:
    old = scene.timeline_markers.get(marker_name)
    if old:
        scene.timeline_markers.remove(old)
    scene.timeline_markers.new(marker_name, frame=frame)

scene.frame_set(0)
print("\n=== AUDIO ASSEMBLY SUMMARY ===")
print("Dialogue strips added: {}/{}".format(len(added_dialogues), len(DIALOGUES)))
print("Optional music/SFX strips added: {}/{}".format(len(added_optional), len(OPTIONAL_AUDIO)))
print("Missing clips are listed above. Add those files to the named folders and rerun.")
print("No silent placeholder audio was generated.")
