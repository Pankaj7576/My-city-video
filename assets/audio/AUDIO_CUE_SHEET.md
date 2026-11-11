# MY CITY VIDEO — final audio cue sheet

Project format: 16:9 | 4K UHD | 30 FPS | 5:00
Timeline: frame 0 through 8999 (exactly 9000 frames / 300 seconds).

## Dialogue cues

| File | Start frame | Channel | Speaker | Dialogue |
|---|---:|---:|---|---|
| `dialogues/aarav_hook_alert.mp3` | 0 | 1 | Aarav | सिस्टम पूरी तरह लॉक होने में बस 5 मिनट बाकी हैं! |
| `dialogues/maya_comm_start.mp3` | 180 | 2 | Maya | आरव, सेंट्रल ग्रिड का फायरवॉल ब्रीच हो रहा है। जल्दी करो! |
| `dialogues/aarav_running_action.mp3` | 1900 | 1 | Aarav | मैं मेन सर्वर टावर के पास पहुँच रहा हूँ, माया बैकअप संभालो! |
| `dialogues/maya_climax_countdown.mp3` | 6400 | 2 | Maya | बस 10 सेकंड बचे हैं आरव, पेनड्राइव कनेक्ट करो! |
| `dialogues/aarav_maya_outro.mp3` | 8600 | 1 | Aarav + Maya | मिशन सक्सेसफुल। |

## Optional music beds

Place these files directly in `assets/audio/`:

| File | Start frame | Channel | Suggested level |
|---|---:|---:|---:|
| `music_opening_tension.wav` | 0 | 4 | 0.22 |
| `music_city_chase.wav` | 1800 | 4 | 0.20 |
| `music_climax.wav` | 5700 | 4 | 0.24 |
| `music_rooftop_outro.wav` | 8550 | 4 | 0.18 |

## Optional sound effects

Place these files in `assets/audio/sfx/`:

| File | Start frame | Channel |
|---|---:|---:|
| `sfx_alert_pulse.wav` | 0 | 3 |
| `sfx_city_ambience.wav` | 150 | 5 |
| `sfx_running_footsteps.wav` | 1800 | 3 |
| `sfx_server_usb_connect.wav` | 6400 | 3 |
| `sfx_system_recovery.wav` | 6600 | 3 |

## Automated application

Run `blender --background my_city_project.blend --python scripts/import_dialogues_vse.py`.
The script imports whichever audio files exist, places them on the assigned channels, applies short fades, creates editorial markers, and reports missing clips. It removes only strips with the managed `DIALOGUE_`, `MUSIC_`, and `SFX_` prefixes before rebuilding, preserving unrelated VSE tracks.

**Asset status:** this repository currently contains the cue sheet and importer only. No dialogue recordings, music, or effects are embedded yet. Do not treat missing audio as silence or as completed sound design. Use original/generated or properly licensed audio.
