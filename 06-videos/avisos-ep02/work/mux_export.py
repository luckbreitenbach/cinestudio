#!/usr/bin/env python3
"""Mux voz+stems no vídeo legendado, verifica LUFS/TP, exporta plataformas e frames."""
from __future__ import annotations
import json, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, "/workspace/cinestudio/06-videos/pipeline/scripts")
from film_pipeline import export_platforms, run, ffprobe_dur, ffprobe_json

EP = Path("/workspace/cinestudio/06-videos/avisos-ep02")
WORK = EP / "work"
VIDEO = WORK / "video_film_subs_silent.mp4"
MASTER = EP / "avisos-ep02_master_guia.mp4"
PRESETS = Path("/workspace/cinestudio/06-videos/pipeline/config/export-presets.json")
FRAMES = EP / "frames"


def ebur128(path: Path) -> dict:
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    log = proc.stderr
    # Integrated loudness:    -14.1 LUFS
    # True peak:               -1.02 dBTP
    I = TP = LRA = None
    # summary is at the end
    mI = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", log)
    mTP = re.findall(r"Peak:\s+(-?[\d.]+)\s+dBFS", log)  # may be sample peak
    # true peak
    mTPt = re.findall(r"True peak:\s+Peak:\s+(-?[\d.]+)\s+dBTP", log)
    if not mTPt:
        mTPt = re.findall(r"True peak:.*?Peak:\s+(-?[\d.]+)\s+dB", log, re.S)
    mLRA = re.findall(r"LRA:\s+(-?[\d.]+)\s+LU", log)
    if mI:
        I = float(mI[-1])
    if mTPt:
        TP = float(mTPt[-1])
    elif mTP:
        TP = float(mTP[-1])
    if mLRA:
        LRA = float(mLRA[-1])
    return {"I": I, "TP": TP, "LRA": LRA, "log_tail": "\n".join(log.splitlines()[-40:])}


def extract_frames():
    FRAMES.mkdir(parents=True, exist_ok=True)
    # one mid-frame per shot + adjustment points
    shots = {
        "p01_mesa": 4.5,
        "p02_cartela": 10.5,  # episode time
        "p02_cartela_entrada": 9.3,
        "p03_dia": 19.5,
        "p04_fachada_41": 26.5,
        "p05_copos": 33.5,
        "p06_desenho": 40.0,
        "p07_silhuetas": 47.0,
        "p07_rangido": 50.9,
        "p08_estudio": 53.5,
        "p08_hold_sem_maos": 57.5,
        "p09_am870": 60.5,
        "p10_barragem": 64.5,
        "p11_flash": 67.3,
        "leg_cartela_boa_noite": 10.5,
        "leg_inicio": 1.0,
        "leg_interferencia": 63.5,
    }
    for name, t in shots.items():
        out = FRAMES / f"check_{name}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(MASTER), "-frames:v", "1", "-update", "1", str(out)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print("frame", out.name, flush=True)


def main():
    assert VIDEO.exists(), VIDEO
    print("mux via remix_with_voice.sh", flush=True)
    run([str(EP / "remix_with_voice.sh"), str(EP / "stems/stem_voz_guia_kokoro.wav"), str(MASTER)])
    dur = ffprobe_dur(MASTER)
    print("master dur", dur, flush=True)
    info = ffprobe_json(MASTER)
    loud = ebur128(MASTER)
    print("loudness", loud["I"], "TP", loud["TP"], "LRA", loud["LRA"], flush=True)
    print(loud["log_tail"], flush=True)
    # if TP > -1.0 (warmer than ceiling), re-limit
    if loud["TP"] is not None and loud["TP"] > -1.0:
        print("TP above ceiling, re-limiting", flush=True)
        tmp = WORK / "master_relim.mp4"
        run([
            "ffmpeg", "-y", "-i", str(MASTER),
            "-c:v", "copy",
            "-af", "alimiter=limit=0.89:attack=5:release=40",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(tmp),
        ])
        tmp.replace(MASTER)
        loud = ebur128(MASTER)
        print("after re-limit", loud["I"], "TP", loud["TP"], flush=True)

    presets = json.loads(PRESETS.read_text())
    outs = export_platforms(MASTER, EP, "avisos-ep02", presets)
    # also copy into exports/
    (EP / "exports").mkdir(exist_ok=True)
    for k, p in outs.items():
        shutil.copy2(p, EP / "exports" / p.name)
    shutil.copy2(MASTER, EP / "exports" / MASTER.name)

    extract_frames()
    report = {
        "master": str(MASTER),
        "duration": dur,
        "loudness": {k: loud[k] for k in ("I", "TP", "LRA")},
        "platforms": {k: str(v) for k, v in outs.items()},
        "ffprobe_video": [
            {kk: ss.get(kk) for kk in ("codec_name", "width", "height", "r_frame_rate", "pix_fmt", "duration")}
            for ss in info["streams"]
        ],
    }
    (WORK / "mux_report.json").write_text(json.dumps(report, indent=2))
    print("MUX DONE", report, flush=True)


if __name__ == "__main__":
    main()
