#!/usr/bin/env python3
"""Create original free Hindi dialogue, music and SFX assets for My City Video.

Uses eSpeak NG (Hindi voice) plus original synthesized instrumental audio.
Aarav/Maya are distinct pitch/speed treatments of the included Hindi voice;
they are functional draft voices, not studio voice acting.
"""
from pathlib import Path
import math
import subprocess
import numpy as np
import wave

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "assets" / "audio"
DIALOGUES = AUDIO / "dialogues"
SFX = AUDIO / "sfx"
for folder in (DIALOGUES, SFX):
    folder.mkdir(parents=True, exist_ok=True)

def run(args):
    subprocess.run(args, check=True)

def speak(text, out_mp3, pitch, speed, amplitude=170):
    wav_path = out_mp3.with_suffix(".wav")
    run(["espeak-ng", "-v", "hi", "-s", str(speed), "-p", str(pitch),
         "-a", str(amplitude), "-w", str(wav_path), text])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-b:a", "96k", str(out_mp3)])
    wav_path.unlink(missing_ok=True)

# Aarav: lower-pitched male-presenting Hindi voice; Maya: brighter/higher pitch.
speak("सिस्टम पूरी तरह लॉक होने में बस पाँच मिनट बाकी हैं!",
      DIALOGUES / "aarav_hook_alert.mp3", 34, 145)
speak("आरव, सेंट्रल ग्रिड का फायरवॉल ब्रीच हो रहा है। जल्दी करो!",
      DIALOGUES / "maya_comm_start.mp3", 70, 152)
speak("मैं मेन सर्वर टावर के पास पहुँच रहा हूँ, माया बैकअप संभालो!",
      DIALOGUES / "aarav_running_action.mp3", 34, 150)
speak("बस दस सेकंड बचे हैं आरव, पेनड्राइव कनेक्ट करो!",
      DIALOGUES / "maya_climax_countdown.mp3", 70, 158)

# Outro: blend both character voices saying the same short line together.
speak("मिशन सक्सेसफुल।", DIALOGUES / "outro_aarav_temp.mp3", 34, 145)
speak("मिशन सक्सेसफुल।", DIALOGUES / "outro_maya_temp.mp3", 70, 152)
run(["ffmpeg", "-y", "-loglevel", "error",
     "-i", str(DIALOGUES / "outro_aarav_temp.mp3"),
     "-i", str(DIALOGUES / "outro_maya_temp.mp3"),
     "-filter_complex", "[0:a]volume=0.85[a];[1:a]volume=0.85[b];[a][b]amix=inputs=2:duration=longest:normalize=0",
     "-codec:a", "libmp3lame", "-b:a", "96k",
     str(DIALOGUES / "aarav_maya_outro.mp3")])
(DIALOGUES / "outro_aarav_temp.mp3").unlink(missing_ok=True)
(DIALOGUES / "outro_maya_temp.mp3").unlink(missing_ok=True)

# Original synthesized music beds. Smooth pads + slow arpeggio; no borrowed melody.
SR = 22050
def music_bed(filename, seconds, root_hz, mood):
    total = int(SR * seconds)
    block = 5 * SR
    with wave.open(str(AUDIO / filename), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        for start in range(0, total, block):
            n = min(block, total - start)
            t = (np.arange(n, dtype=np.float64) + start) / SR
            chord_phase = 2 * np.pi * root_hz * t
            pad = (0.22*np.sin(chord_phase) +
                   0.13*np.sin(chord_phase*1.5 + 0.4) +
                   0.10*np.sin(chord_phase*2.0 + 0.9) +
                   0.06*np.sin(chord_phase*2.5 + 0.2))
            slow = 0.65 + 0.35*np.sin(2*np.pi*t/19.0)
            pulse = (0.5 + 0.5*np.sin(2*np.pi*t*(0.7 if mood == "calm" else 1.4)))**3
            shimmer = 0.035*np.sin(2*np.pi*(root_hz*4.01)*t)
            if mood == "tense":
                beat = 0.11*pulse*np.sin(2*np.pi*root_hz*0.5*t)
            elif mood == "chase":
                beat = 0.17*pulse*np.sin(2*np.pi*root_hz*0.5*t)
            elif mood == "climax":
                beat = 0.14*pulse*np.sin(2*np.pi*root_hz*0.75*t)
            else:
                beat = 0.035*pulse*np.sin(2*np.pi*root_hz*0.5*t)
            fade = np.minimum(1.0, (start + np.arange(n))/ (SR*3))
            tail = np.minimum(1.0, (total - (start + np.arange(n))) / (SR*4))
            audio = (pad*slow + beat + shimmer) * np.clip(fade,0,1) * np.clip(tail,0,1)
            audio = np.clip(audio*0.55, -0.95, 0.95)
            pcm = (audio*32767).astype("<i2")
            wf.writeframes(pcm.tobytes())
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(AUDIO / filename),
         "-codec:a", "libmp3lame", "-b:a", "112k",
         str(AUDIO / filename.replace(".wav", ".mp3"))])
    (AUDIO / filename).unlink(missing_ok=True)

music_bed("music_opening_tension.wav", 60, 55.0, "tense")
music_bed("music_city_chase.wav", 150, 65.4, "chase")
music_bed("music_climax.wav", 75, 73.4, "climax")
music_bed("music_rooftop_outro.wav", 20, 49.0, "calm")

# Short original synthetic sound effects, written as 16-bit mono WAV.
def write_sfx(filename, seconds, builder):
    n = int(SR * seconds)
    t = np.arange(n, dtype=np.float64) / SR
    y = builder(t, seconds)
    y = np.clip(y, -0.95, 0.95)
    with wave.open(str(SFX / filename), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((y*32767).astype("<i2").tobytes())

def alert(t, d):
    env = np.maximum(0, np.sin(np.pi*t*2.2))**2
    return 0.45*env*np.sin(2*np.pi*(680 + 220*np.sin(2*np.pi*t/d))*t)
def city(t, d):
    rng = np.random.default_rng(22)
    noise = rng.normal(0, 0.035, len(t))
    hum = 0.045*np.sin(2*np.pi*58*t) + 0.02*np.sin(2*np.pi*92*t)
    return noise + hum
def footsteps(t, d):
    y = np.zeros_like(t)
    for at in np.arange(0.2, d, 0.48):
        env = np.exp(-np.maximum(0,t-at)*18) * (t >= at)
        y += 0.48*env*np.sin(2*np.pi*(85+25*np.exp(-np.maximum(0,t-at)*12))*t)
    return y
def usb(t, d):
    env = np.exp(-t*5)
    return env*(0.4*np.sin(2*np.pi*120*t) + 0.18*np.sin(2*np.pi*820*t))
def recovery(t, d):
    rise = np.clip(t/d,0,1)
    env = np.sin(np.pi*rise)**1.3
    freq = 420 + 620*rise
    phase = 2*np.pi*np.cumsum(freq)/SR
    return 0.38*env*np.sin(phase) + 0.10*env*np.sin(phase*2)

write_sfx("sfx_alert_pulse.wav", 4, alert)
write_sfx("sfx_city_ambience.wav", 60, city)
write_sfx("sfx_running_footsteps.wav", 12, footsteps)
write_sfx("sfx_server_usb_connect.wav", 3, usb)
write_sfx("sfx_system_recovery.wav", 8, recovery)

print("Generated 5 dialogue MP3s, 4 original music MP3s and 5 SFX WAVs.")
