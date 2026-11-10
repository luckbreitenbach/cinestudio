#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, "/workspace/cinestudio/06-videos/pipeline/scripts")
sys.path.insert(0, "/workspace/cinestudio/06-videos/avisos-ep01/work")
from assemble_video import DURS, PREP, FX, FILM, apply_film_look, WORK, FPS, run, ffprobe_dur

FILM.mkdir(parents=True, exist_ok=True)
fxed = {}
for i in DURS:
    p = FX / f"plano-{i:02d}.mp4"
    fxed[i] = p if p.exists() else PREP / f"plano-{i:02d}.mp4"

for i, d in DURS.items():
    print(f"=== film look p{i:02d} ===", flush=True)
    skip = {4: 3.05, 10: 3.4}.get(i)
    strength = 1.0
    weave = True
    if i == 11:
        strength = 0.55
        weave = False
    if i == 2:
        strength = 0.75
    apply_film_look(fxed[i], FILM / f"plano-{i:02d}.mp4", d, skip_at=skip, strength=strength, weave=weave)

parts = []
for i, d in DURS.items():
    p = WORK / f"part_{i:02d}.mp4"
    run([
        "ffmpeg", "-y", "-i", str(FILM / f"plano-{i:02d}.mp4"), "-an",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-preset", "medium", "-crf", "15", "-t", f"{d:.4f}",
        "-movflags", "+faststart", str(p),
    ])
    parts.append(p)
lst = WORK / "concat.txt"
lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
out = WORK / "video_film_nosubs.mp4"
run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-preset", "medium", "-crf", "15", "-an", "-movflags", "+faststart", str(out),
])
print("VIDEO_OK", out, "dur", ffprobe_dur(out))
