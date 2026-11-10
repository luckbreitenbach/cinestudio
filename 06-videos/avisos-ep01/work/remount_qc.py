#!/usr/bin/env python3
"""Reaplica look filme só em p7/p9, concatena, corrige o grau magenta e remonta o master (áudio intacto)."""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, "/workspace/cinestudio/06-videos/pipeline/scripts")
sys.path.insert(0, "/workspace/cinestudio/06-videos/avisos-ep01/work")
from assemble_video import apply_film_look, DURS, FX, FILM, WORK, FPS, run, ffprobe_dur
from film_pipeline import escape_filter_path, encode_common, export_platforms

EP = Path("/workspace/cinestudio/06-videos/avisos-ep01")
ASS = WORK / "legendas_avisos_ep01.ass"
FONTS = EP / "fonts"
PRESETS = json.loads((Path("/workspace/cinestudio/06-videos/pipeline/config/export-presets.json")).read_text())

# correção sépia-esverdeada aplicada no concat já filmado (as partes usam o look antigo)
GRADE = (
    "eq=gamma_g=1.18:gamma_r=1.04:gamma_b=0.88:saturation=0.72,"
    "colorbalance=rs=-0.08:gs=0.08:bs=-0.10:rm=-0.05:gm=0.07:bm=-0.08:rh=0.04:gh=0.06:bh=-0.06,"
    "curves=all='0/0.04 0.5/0.48 1/0.94'"
)

ENC = [
    "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30",
    "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M", "-preset", "medium",
    "-movflags", "+faststart",
]


def main():
    print("=== film look p07 ===", flush=True)
    apply_film_look(FX / "plano-07.mp4", FILM / "plano-07.mp4", 5.0, strength=1.0, weave=True)
    print("=== film look p09 ===", flush=True)
    apply_film_look(FX / "plano-09.mp4", FILM / "plano-09.mp4", 6.0, strength=1.0, weave=True)

    for i, d in ((7, 5.0), (9, 6.0)):
        p = WORK / f"part_{i:02d}.mp4"
        print(f"=== part {i:02d} ===", flush=True)
        run([
            "ffmpeg", "-y", "-i", str(FILM / f"plano-{i:02d}.mp4"), "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-preset", "medium", "-crf", "15", "-t", f"{d:.4f}",
            "-movflags", "+faststart", str(p),
        ])
        print("  dur", ffprobe_dur(p))

    parts = [WORK / f"part_{i:02d}.mp4" for i in range(1, 12)]
    for p in parts:
        assert p.exists(), p
        print(p.name, f"{ffprobe_dur(p):.3f}")

    lst = WORK / "concat_qc.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    ass_esc = escape_filter_path(ASS)
    fonts_esc = escape_filter_path(FONTS)
    vf = f"{GRADE},ass={ass_esc}:fontsdir={fonts_esc}"

    nosubs = WORK / "video_film_nosubs.mp4"
    silent = WORK / "video_film_subs_silent.mp4"
    print("=== concat + grade (sem legendas) ===", flush=True)
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-vf", GRADE, "-an", *ENC, str(nosubs),
    ])
    print("nosubs", ffprobe_dur(nosubs))
    print("=== concat + grade + legendas ===", flush=True)
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-vf", vf, "-an", *ENC, str(silent),
    ])
    print("silent", ffprobe_dur(silent))

    master_old = EP / "avisos-ep01_master_guia.mp4"
    master_tmp = WORK / "master_guia_qc.mp4"
    print("=== mux áudio existente ===", flush=True)
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(master_old),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy",
        "-shortest", "-movflags", "+faststart", str(master_tmp),
    ])
    print("master_tmp", ffprobe_dur(master_tmp))
    # replace master atomically
    master_tmp.replace(master_old)
    print("MASTER_OK", master_old, ffprobe_dur(master_old))

    print("=== exports plataformas ===", flush=True)
    dest = EP
    expdir = EP / "exports"
    outs = export_platforms(master_old, dest, "avisos-ep01", PRESETS)
    expdir.mkdir(exist_ok=True)
    for k, p in outs.items():
        # also copy into exports/
        import shutil
        shutil.copy2(p, expdir / p.name)
        print("export", p, ffprobe_dur(p))
    print("REMOUNT_OK")


if __name__ == "__main__":
    main()
