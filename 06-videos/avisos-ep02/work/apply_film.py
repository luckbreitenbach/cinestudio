#!/usr/bin/env python3
"""Aplica o look filme (sépia-oliva corrigido) a cada plano, concatena, queima legendas."""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, "/workspace/cinestudio/06-videos/pipeline/scripts")
from film_pipeline import (
    W, H, FPS, film_video_filters, concat_copy, concat_list, burn_subs, escape_filter_path, run, ffprobe_dur
)

EP = Path("/workspace/cinestudio/06-videos/avisos-ep02")
FX = EP / "work/fx"
FILM = EP / "work/film"
WORK = EP / "work"
DUST = WORK / "dust_loop.mp4"
ASS = WORK / "legendas_avisos_ep02.ass"
FONTS = EP / "fonts"
DURS = [9.0, 7.0, 7.0, 7.0, 7.0, 6.0, 9.0, 7.0, 3.0, 5.0, 1.0]


def apply_one(src: Path, dst: Path, duration: float, overlay: Path | None):
    vf = film_video_filters(strength=1.0, weave=True, flicker=True, skip_scale=False)
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if overlay and overlay.exists():
        cmd += ["-stream_loop", "-1", "-i", str(overlay)]
        # poeira suave por overlay; o look já está em [0:v]
        fc = (
            f"[0:v]{vf}[base];"
            f"[1:v]format=gbrp,eq=brightness=0.15,format=yuva420p,colorchannelmixer=aa=0.22[ov];"
            f"[base][ov]overlay=shortest=1:format=auto[v]"
        )
        cmd += ["-filter_complex", fc, "-map", "[v]"]
    else:
        cmd += ["-vf", vf]
    cmd += [
        "-t", f"{duration:.4f}", "-r", str(FPS),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "16",
        "-an", "-movflags", "+faststart", str(dst),
    ]
    run(cmd)
    return dst


def main():
    FILM.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, dur in enumerate(DURS, start=1):
        src = FX / f"plano-{i:02d}.mp4"
        dst = FILM / f"part_{i:02d}.mp4"
        print(f"=== film p{i} ===", flush=True)
        apply_one(src, dst, dur, DUST if DUST.exists() else None)
        got = ffprobe_dur(dst)
        print(f"  dur={got:.3f} target={dur:.3f}", flush=True)
        parts.append(dst)

    silent = WORK / "video_film_nosubs.mp4"
    print("=== concat ===", flush=True)
    try:
        concat_copy(parts, silent)
    except Exception as e:
        print("concat copy failed, re-encode", e, flush=True)
        concat_list(parts, silent)
    print("concat dur", ffprobe_dur(silent), flush=True)

    with_subs = WORK / "video_film_subs_silent.mp4"
    print("=== burn subs ===", flush=True)
    burn_subs(silent, ASS, with_subs, FONTS)
    print("subs dur", ffprobe_dur(with_subs), flush=True)
    print("FILM DONE", flush=True)


if __name__ == "__main__":
    main()
