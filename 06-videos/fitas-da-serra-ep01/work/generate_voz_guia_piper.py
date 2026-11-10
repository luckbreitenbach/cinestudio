#!/usr/bin/env python3
"""Gera voz guia Piper pt-BR (cadu/jeff, CC0) para Ep.01 — não sobrescreve masters sem voz."""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/workspace/cinestudio")
EP = ROOT / "06-videos/fitas-da-serra-ep01"
PIPER = ROOT / "bible/audio-tests/piper-venv/bin/piper"
VOICES = ROOT / "bible/audio-tests/voices"
CADU = VOICES / "pt_BR-cadu-medium.onnx"
JEFF = VOICES / "pt_BR-jeff-medium.onnx"
SR = 48000
DUR = 92.1
ATEMPO_MAX = 1.25

RAW = EP / "work/voz_guia_raw"
PER = EP / "stems/voz_guia"
STEM = EP / "stems/stem_voz_guia_piper.wav"
TIMELINE = EP / "voice_timeline.json"

# Character → model + synthesis/FX profile
# Marta: male guide with raised pitch (jeff)
# Tião: cadu, grave, lento
# Dudu: jeff, rápido
# Benedito: cadu, rouco/lento/baixo + aspereza
PROFILES = {
    "Marta": {
        "model": JEFF,
        "length_scale": 0.95,
        "pitch_semitones": 3.5,  # raise
        "noise_scale": 0.5,
        "noise_w": 0.4,
        "post": "marta",
    },
    "Tião": {
        "model": CADU,
        "length_scale": 1.18,
        "pitch_semitones": -1.5,
        "noise_scale": 0.45,
        "noise_w": 0.3,
        "post": "tiao",
    },
    "Dudu": {
        "model": JEFF,
        "length_scale": 0.88,
        "pitch_semitones": 0.5,
        "noise_scale": 0.55,
        "noise_w": 0.45,
        "post": "dudu",
    },
    "Benedito": {
        "model": CADU,
        "length_scale": 1.28,
        "pitch_semitones": -4.0,
        "noise_scale": 0.65,
        "noise_w": 0.55,
        "post": "benedito",
    },
}


def run(cmd, **kw):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, check=True, **kw)


def ffprobe_dur(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def piper_synth(text: str, model: Path, out_wav: Path, length_scale: float, noise_scale: float, noise_w: float):
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(PIPER),
        "-m",
        str(model),
        "-f",
        str(out_wav),
        "--length-scale",
        str(length_scale),
        "--noise-scale",
        str(noise_scale),
        "--noise-w-scale",
        str(noise_w),
        "--sentence-silence",
        "0.05",
    ]
    subprocess.run(cmd, input=text + "\n", text=True, check=True)


def chain_atempo(factor: float) -> str:
    """Split atempo into 0.5–2.0 chunks."""
    parts = []
    f = factor
    while f > 2.0:
        parts.append("atempo=2.0")
        f /= 2.0
    while f < 0.5:
        parts.append("atempo=0.5")
        f /= 0.5
    parts.append(f"atempo={f:.6f}")
    return ",".join(parts)


def post_fx(character_post: str, pitch_st: float) -> str:
    """Build af filter for character color + pitch (rubberband) before fit."""
    pitch_ratio = 2 ** (pitch_st / 12.0)
    # rubberband pitch keeps duration
    rb = f"rubberband=pitch={pitch_ratio:.6f}:tempo=1.0"
    if character_post == "benedito":
        # lower + slight grit/hoarseness
        return (
            f"{rb},"
            "highpass=f=80,lowpass=f=3800,"
            "afftfilt=real='re*0.92':imag='im*0.92',"
            "acompressor=threshold=-22dB:ratio=3:attack=12:release=80,"
            "asubboost=dry=0.6:wet=0.35:decay=0.1,"
            "volume=1.05"
        )
    if character_post == "marta":
        return f"{rb},highpass=f=120,treble=g=2,volume=1.0"
    if character_post == "tiao":
        return f"{rb},highpass=f=90,bass=g=2,treble=g=-1,volume=0.95"
    if character_post == "dudu":
        return f"{rb},highpass=f=110,treble=g=1.5,volume=1.0"
    return rb


def vhs_mic_filter() -> str:
    # band-pass ~200–4500, light compression/saturation, a bit of room
    return (
        "highpass=f=200,lowpass=f=4500,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=60:makeup=3,"
        "aexciter=amount=0.2:drive=2.5:blend=0,"
        "asoftclip=type=tanh,"
        "aecho=0.8:0.7:28:0.18,"
        "volume=0.95"
    )


def process_line(fala: dict) -> dict:
    fid = fala["id"]
    personagem = fala["personagem"]
    text = fala["texto"]
    t_in = float(fala["in"])
    t_out = float(fala["out"])
    slot = max(0.15, t_out - t_in)
    prof = PROFILES[personagem]

    raw = RAW / f"{fid}_raw.wav"
    pitched = RAW / f"{fid}_pitched.wav"
    fitted = PER / f"{fid}.wav"

    piper_synth(
        text,
        prof["model"],
        raw,
        prof["length_scale"],
        prof["noise_scale"],
        prof["noise_w"],
    )

    fx = post_fx(prof["post"], prof["pitch_semitones"])
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(raw),
            "-af",
            fx,
            "-ar",
            str(SR),
            "-ac",
            "1",
            str(pitched),
        ]
    )
    dur = ffprobe_dur(pitched)

    # leave ~40ms pad at end of slot
    target = max(0.12, slot - 0.04)
    note = "ok"
    atempo = 1.0
    if dur > target:
        atempo = dur / target
        if atempo > ATEMPO_MAX:
            note = f"APERTADO: precisa {atempo:.3f}x; capado em {ATEMPO_MAX}x (pode estourar o slot)"
            atempo = ATEMPO_MAX
        else:
            note = f"ajustado atempo={atempo:.3f}x para caber em {slot:.3f}s"
        af = chain_atempo(atempo) + "," + vhs_mic_filter()
    else:
        # pad silence at end to fill gently (not full slot — keep natural)
        af = vhs_mic_filter()
        note = f"cabe natural ({dur:.3f}s em slot {slot:.3f}s)"

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(pitched),
            "-af",
            af,
            "-ar",
            str(SR),
            "-ac",
            "1",
            str(fitted),
        ]
    )
    final_dur = ffprobe_dur(fitted)
    overflow = max(0.0, final_dur - slot)
    return {
        "id": fid,
        "personagem": personagem,
        "model": prof["model"].name,
        "in": t_in,
        "out": t_out,
        "slot_s": slot,
        "raw_pitched_s": dur,
        "final_s": final_dur,
        "atempo": atempo,
        "overflow_s": overflow,
        "note": note,
        "path": str(fitted),
        "text": text,
    }


def build_stem(reports: list[dict]):
    """Place each clip on timeline via adelay + amix."""
    # Build filter: anullsrc base + each delayed clip
    inputs = ["-f", "lavfi", "-t", f"{DUR}", "-i", f"anullsrc=r={SR}:cl=mono"]
    # index 0 = silence bed
    labels = ["[0:a]"]
    for i, r in enumerate(reports):
        inputs += ["-i", r["path"]]
        delay_ms = int(round(r["in"] * 1000))
        # adelay for mono needs one value
        labels.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms},apad=whole_dur={DUR}[v{i}]")
    # rebuild properly
    filter_parts = []
    mix_ins = ["[0:a]"]
    for i, r in enumerate(reports):
        delay_ms = int(round(r["in"] * 1000))
        filter_parts.append(
            f"[{i+1}:a]adelay={delay_ms}|{delay_ms},apad=whole_dur={DUR}[v{i}]"
        )
        mix_ins.append(f"[v{i}]")
    n = len(mix_ins)
    filter_parts.append(
        f"{''.join(mix_ins)}amix=inputs={n}:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.95[aout]"
    )
    fc = ";".join(filter_parts)
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[aout]", "-t", str(DUR), "-ar", str(SR), "-ac", "1", str(STEM)]
    run(cmd)


def remix_with_ducking(voice: Path, outfile: Path):
    video = EP / "fitas-da-serra-ep01_master.mp4"
    amb = EP / "stems/stem_ambiente_sfx.wav"
    # Light sidechain ducking: ambient ducks when voice present
    # sidechaincompress: main=amb, sidechain=voice
    fc = (
        f"[1:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo[amb];"
        f"[2:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=mono,"
        f"pan=stereo|c0=c0|c1=c0[voz];"
        f"[amb][voz]sidechaincompress=threshold=0.05:ratio=2.5:attack=20:release=280:makeup=1:knee=4[ambd];"
        f"[ambd][voz]amix=inputs=2:duration=first:dropout_transition=2:weights=0.75 1.0,"
        f"loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary,"
        f"alimiter=limit=0.95[a]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(amb),
            "-i",
            str(voice),
            "-filter_complex",
            fc,
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(SR),
            "-ac",
            "2",
            "-shortest",
            "-movflags",
            "+faststart",
            str(outfile),
        ]
    )


def export_platforms(master_guia: Path):
    presets = json.loads((ROOT / "06-videos/pipeline/config/export-presets.json").read_text())
    sys.path.insert(0, str(ROOT / "06-videos/pipeline/scripts"))
    from vhs_pipeline import encode_common

    outs = {}
    for key, suf_name in (("tiktok", "_tiktok_guia"), ("reels", "_reels_guia"), ("shorts", "_shorts_guia")):
        out = EP / f"fitas-da-serra-ep01{suf_name}.mp4"
        # encode_common uses arquivo_sufixo from preset — build manually instead
        args = encode_common(key, presets)
        run(["ffmpeg", "-y", "-i", str(master_guia), *args, str(out)])
        shutil.copy2(out, EP / "exports" / out.name)
        outs[key] = str(out)
    return outs


def measure_loudness(path: Path) -> dict:
    # two-pass style via loudnorm print
    proc = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    err = proc.stderr
    # extract last JSON object
    start = err.rfind("{")
    end = err.rfind("}")
    if start >= 0 and end > start:
        return json.loads(err[start : end + 1])
    return {"raw": err[-2000:]}


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    PER.mkdir(parents=True, exist_ok=True)
    data = json.loads(TIMELINE.read_text())
    reports = []
    for fala in data["falas"]:
        print(f"\n=== {fala['id']} ({fala['personagem']}) ===", flush=True)
        reports.append(process_line(fala))

    print("\n=== building stem ===", flush=True)
    build_stem(reports)

    master_guia = EP / "fitas-da-serra-ep01_master_guia.mp4"
    print("\n=== remix with ducking ===", flush=True)
    remix_with_ducking(STEM, master_guia)

    print("\n=== platform exports ===", flush=True)
    outs = export_platforms(master_guia)

    print("\n=== loudness ===", flush=True)
    loud = measure_loudness(master_guia)

    report_path = EP / "work/voz_guia_report.json"
    payload = {
        "licenses": {
            "pt_BR-cadu-medium": {
                "license": "CC0",
                "source": "https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/cadu/medium",
                "model_card": str(VOICES / "MODEL_CARD_cadu.md"),
                "dataset": "https://github.com/OHF-Voice/voice-datasets",
            },
            "pt_BR-jeff-medium": {
                "license": "CC0",
                "source": "https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/jeff/medium",
                "model_card": str(VOICES / "MODEL_CARD_jeff.md"),
                "dataset": "https://github.com/OHF-Voice/voice-datasets",
            },
        },
        "stem": str(STEM),
        "master_guia": str(master_guia),
        "exports": outs,
        "loudness": loud,
        "falas": reports,
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print("REPORT", report_path)
    for r in reports:
        print(f"{r['id']}: {r['note']} final={r['final_s']:.3f}s overflow={r['overflow_s']:.3f}s")
    print("LOUDNESS", json.dumps(loud, indent=2))


if __name__ == "__main__":
    main()
