#!/usr/bin/env python3
"""Apara, aplica FX por plano, look filme, concatena vídeo (sem voz)."""
from __future__ import annotations
import sys, subprocess
from pathlib import Path

sys.path.insert(0, "/workspace/cinestudio/06-videos/pipeline/scripts")
sys.path.insert(0, "/workspace/cinestudio/06-videos/avisos-ep01/work")
from film_pipeline import W, H, FPS, film_video_filters, run, ffprobe_dur, escape_filter_path
from fx_planos import (
    upscale_trim, process_p1, track_and_overlay_cartela, process_p5,
    process_p7, process_p9, process_p10,
)

CINE = Path("/workspace/cinestudio")
CLIPS = CINE / "05-cenas/avisos-ep01"
EP = CINE / "06-videos/avisos-ep01"
WORK = EP / "work"
PREP = WORK / "prep"
FX = WORK / "fx"
FILM = WORK / "film"

DURS = {1: 8.0, 2: 5.0, 3: 5.0, 4: 6.0, 5: 9.0, 6: 6.0, 7: 5.0, 8: 8.0, 9: 6.0, 10: 6.0, 11: 2.0}
DUST = WORK / "dust_loop.mp4"


def apply_film_look(src: Path, dst: Path, duration: float, skip_at: float | None = None, strength: float = 1.0, weave=True):
    vf = film_video_filters(strength=strength, weave=weave, skip_scale=True)
    # input already 1080x1920 30fps
    fc = f"[0:v]{vf}[base]"
    if DUST.exists():
        fc += f";[1:v]format=yuv420p,eq=brightness=0.05[ov];[base][ov]blend=all_mode=screen:all_opacity=0.22[v]"
        cmd = ["ffmpeg", "-y", "-i", str(src), "-stream_loop", "-1", "-i", str(DUST),
               "-filter_complex", fc, "-map", "[v]", "-t", f"{duration:.4f}"]
    else:
        cmd = ["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-t", f"{duration:.4f}"]
    if skip_at is not None:
        # apply hitch by dropping 2 frames then cloning end — do as pre-filter on [0:v]
        # Simpler second pass after this.
        pass
    cmd += ["-an", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-movflags", "+faststart", str(dst)]
    run(cmd)
    if skip_at is not None:
        tmp = dst.with_suffix(".skip.mp4")
        # drop 2 frames around skip_at, pad duration by cloning last
        # fps 30 → 2 frames = 1/15 s
        t0, t1 = skip_at, skip_at + 2 / FPS
        vf2 = (
            f"select='not(between(t,{t0:.4f},{t1:.4f}))',setpts=N/FRAME_RATE/TB,"
            f"tpad=stop_mode=clone:stop_duration={2/FPS:.4f}"
        )
        run(["ffmpeg", "-y", "-i", str(dst), "-vf", vf2, "-an",
             "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p",
             "-r", str(FPS), "-t", f"{duration:.4f}", "-movflags", "+faststart", str(tmp)])
        tmp.replace(dst)
    return dst


def main():
    PREP.mkdir(parents=True, exist_ok=True)
    FX.mkdir(parents=True, exist_ok=True)
    FILM.mkdir(parents=True, exist_ok=True)
    prepped = {}
    for i, d in DURS.items():
        src = CLIPS / f"plano-{i:02d}.mp4"
        dst = PREP / f"plano-{i:02d}.mp4"
        print(f"=== upscale p{i:02d} ===", flush=True)
        upscale_trim(src, dst, d)
        prepped[i] = dst

    fxed = dict(prepped)
    print("=== FX p1 window ===", flush=True)
    fxed[1] = process_p1(prepped[1], FX / "plano-01.mp4", DURS[1])
    print("=== FX p2 cartela ===", flush=True)
    out, _ = track_and_overlay_cartela(prepped[2], FX / "plano-02.mp4", DURS[2])
    fxed[2] = out
    print("=== FX p5 chair ===", flush=True)
    fxed[5] = process_p5(prepped[5], FX / "plano-05.mp4", DURS[5])
    print("=== FX p7 AM870 ===", flush=True)
    fxed[7] = process_p7(prepped[7], FX / "plano-07.mp4", DURS[7])
    print("=== FX p9 burn ===", flush=True)
    fxed[9] = process_p9(prepped[9], FX / "plano-09.mp4", DURS[9])
    print("=== FX p10 grain ===", flush=True)
    fxed[10] = process_p10(prepped[10], FX / "plano-10.mp4", DURS[10])

    filmed = {}
    for i, d in DURS.items():
        print(f"=== film look p{i:02d} ===", flush=True)
        skip = None
        strength = 1.0
        weave = True
        if i == 4:
            skip = 3.05
        if i == 10:
            skip = 3.4
        if i == 11:
            strength = 0.55
            weave = False  # keep perforation/flash readable
        if i == 2:
            strength = 0.75  # paper already has texture
        filmed[i] = apply_film_look(fxed[i], FILM / f"plano-{i:02d}.mp4", d, skip_at=skip, strength=strength, weave=weave)

    # normalize each part to identical codec then concat
    parts = []
    for i, d in DURS.items():
        p = WORK / f"part_{i:02d}.mp4"
        run([
            "ffmpeg", "-y", "-i", str(filmed[i]), "-an",
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


if __name__ == "__main__":
    main()
