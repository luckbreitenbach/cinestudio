#!/usr/bin/env python3
"""Mux voz+stems no vídeo legendado, loudnorm 2 pass + teto -1 dBTP, exporta plataformas e frames."""
from __future__ import annotations
import json, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, "/workspace/cinestudio/06-videos/pipeline/scripts")
from film_pipeline import export_platforms, run, ffprobe_dur, ffprobe_json

EP = Path("/workspace/cinestudio/06-videos/avisos-ep03")
WORK = EP / "work"
STEMS = EP / "stems"
VIDEO = WORK / "video_film_subs_silent.mp4"
MASTER = EP / "avisos-ep03_master_guia.mp4"
PRESETS = Path("/workspace/cinestudio/06-videos/pipeline/config/export-presets.json")
FRAMES = EP / "frames"


def ebur128(path: Path) -> dict:
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    log = proc.stderr
    I = TP = LRA = None
    mI = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", log)
    mTP = re.findall(r"Peak:\s+(-?[\d.]+)\s+dBFS", log)
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
    return {"I": I, "TP": TP, "LRA": LRA, "log_tail": "\n".join(log.splitlines()[-50:])}


def _ln_json(stderr: str) -> dict:
    start = stderr.rfind("{")
    end = stderr.rfind("}") + 1
    if start < 0 or end <= start:
        raise RuntimeError("loudnorm json not found\n" + stderr[-2000:])
    return json.loads(stderr[start:end])


def loudnorm_two_pass(src: Path, dst: Path) -> dict:
    """Dois passos EBU R128, alvo -14 LUFS / -1.3 dBTP (folga), depois atenua se ainda quente."""
    # se o mix estiver muito quente, atenua antes (o linear do loudnorm estoura com I≈0)
    probe = subprocess.run(
        ["ffmpeg", "-i", str(src), "-af", "loudnorm=I=-14:TP=-1.3:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    meas0 = _ln_json(probe.stderr)
    print("loudnorm probe", meas0, flush=True)
    work_src = src
    pre_att = 0.0
    try:
        in_i = float(meas0["input_i"])
    except Exception:
        in_i = -14.0
    if in_i > -10.0:
        pre_att = in_i - (-14.0)
        pre = WORK / "mix_pre_att.wav"
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-af", f"volume=-{pre_att:.2f}dB",
            "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", str(pre),
        ])
        work_src = pre
        print(f"pre-attenuated {pre_att:.2f} dB (input_i={in_i})", flush=True)
    p1 = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(work_src),
            "-af", "loudnorm=I=-14:TP=-1.3:LRA=11:print_format=json",
            "-f", "null", "-",
        ],
        capture_output=True, text=True,
    )
    src = work_src
    start = p1.stderr.rfind("{")
    end = p1.stderr.rfind("}") + 1
    tail = p1.stderr[start:end]
    (WORK / "loudnorm_p1.json.txt").write_text(tail)
    if start < 0 or end <= start:
        raise RuntimeError("loudnorm json not found\n" + p1.stderr[-2000:])
    meas = json.loads(tail)
    print("loudnorm p1", meas, flush=True)
    filt = (
        "loudnorm=I=-14:TP=-1.3:LRA=11:"
        f"measured_I={meas['input_i']}:"
        f"measured_TP={meas['input_tp']}:"
        f"measured_LRA={meas['input_lra']}:"
        f"measured_thresh={meas['input_thresh']}:"
        f"offset={meas['target_offset']}:"
        "linear=true:print_format=summary,"
        "alimiter=limit=0.86:attack=5:release=50"
    )
    mid = WORK / "mix_ln2.wav"
    run([
        "ffmpeg", "-y", "-i", str(src), "-af", filt,
        "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", str(mid),
    ])
    loud = ebur128(mid)
    print("after ln2", loud["I"], "TP", loud["TP"], "LRA", loud["LRA"], flush=True)
    (WORK / "ebur_ln2.txt").write_text(loud["log_tail"])
    src_use = mid
    extra = 0.0
    # folga: I no máximo -14.15, TP no máximo -1.15
    if loud["TP"] is not None and loud["I"] is not None:
        need_tp = max(0.0, (loud["TP"] - (-1.20)))
        need_i = max(0.0, (loud["I"] - (-14.15)))
        extra = max(need_tp, need_i)
        if extra > 0.02:
            # pequena folga extra
            extra = extra + 0.10
            out_att = WORK / "mix_ln2_att.wav"
            run([
                "ffmpeg", "-y", "-i", str(mid),
                "-af", f"volume=-{extra:.2f}dB",
                "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", str(out_att),
            ])
            src_use = out_att
            loud = ebur128(src_use)
            print("after att", extra, "dB ->", loud["I"], "TP", loud["TP"], flush=True)
    if src_use != dst:
        shutil.copy2(src_use, dst)
    loud["att_db"] = extra
    return loud


def extract_frames():
    FRAMES.mkdir(parents=True, exist_ok=True)
    shots = {
        "p01_rua_chao": 5.0,
        "p02_cartela": 13.0,
        "p02_cartela_entrada": 11.3,
        "p03_fachada_41": 22.0,
        "p04_muro": 28.0,
        "p05_barragem_zoom": 34.0,
        "p06_silhuetas_zoom": 40.0,
        "p07_am870": 45.5,
        "p08_faixa_luz_ini": 48.8,
        "p08_faixa_luz_fim": 54.6,
        "p09_estudio": 58.0,
        "p10_represa_sirene": 64.0,
        "p11_flash": 67.4,
        "leg_inicio": 1.0,
        "leg_cartela_boa_noite": 12.5,
        "leg_lurdes": 44.2,
        "leg_teresa_osvaldo": 48.5,
        "leg_quem_e_teresa": 65.4,
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
    pre = STEMS / "stem_mix_guia_pre_loudnorm.wav"
    assert pre.exists(), pre
    final_wav = WORK / "mix_final.wav"
    print("loudnorm two-pass", flush=True)
    loud = loudnorm_two_pass(pre, final_wav)
    print("mux video + mix_final", flush=True)
    run([
        "ffmpeg", "-y", "-i", str(VIDEO), "-i", str(final_wav),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", "-movflags", "+faststart", str(MASTER),
    ])
    dur = ffprobe_dur(MASTER)
    print("master dur", dur, flush=True)
    info = ffprobe_json(MASTER)
    loud_m = ebur128(MASTER)
    print("master loudness", loud_m["I"], "TP", loud_m["TP"], "LRA", loud_m["LRA"], flush=True)
    print(loud_m["log_tail"], flush=True)
    (WORK / "ebur128_final.txt").write_text(loud_m["log_tail"])

    # se o AAC tiver levantado o TP, re-limita
    if loud_m["TP"] is not None and loud_m["TP"] > -1.0:
        print("AAC TP above ceiling, re-limiting", flush=True)
        tmp = WORK / "master_relim.mp4"
        # atenua o wav um pouco mais e remux
        att = WORK / "mix_final_re.wav"
        extra = (loud_m["TP"] - (-1.20)) + 0.10
        run([
            "ffmpeg", "-y", "-i", str(final_wav), "-af", f"volume=-{extra:.2f}dB",
            "-c:a", "pcm_s24le", str(att),
        ])
        run([
            "ffmpeg", "-y", "-i", str(VIDEO), "-i", str(att),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest", "-movflags", "+faststart", str(MASTER),
        ])
        loud_m = ebur128(MASTER)
        print("after remux att", extra, loud_m["I"], "TP", loud_m["TP"], flush=True)
        shutil.copy2(att, final_wav)

    presets = json.loads(PRESETS.read_text())
    outs = export_platforms(MASTER, EP, "avisos-ep03", presets)
    (EP / "exports").mkdir(exist_ok=True)
    for k, p in outs.items():
        shutil.copy2(p, EP / "exports" / p.name)
    shutil.copy2(MASTER, EP / "exports" / MASTER.name)

    extract_frames()
    report = {
        "master": str(MASTER),
        "duration": dur,
        "loudness": {k: loud_m[k] for k in ("I", "TP", "LRA")},
        "loudness_wav": {k: loud[k] for k in ("I", "TP", "LRA") if k in loud},
        "att_db": loud.get("att_db"),
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
