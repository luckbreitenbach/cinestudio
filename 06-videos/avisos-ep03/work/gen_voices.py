#!/usr/bin/env python3
"""Gera falas guia Kokoro (Osvaldo=pm_alex, interferência=pf_dora).
Nunca aplica atempo > 1.1x. Se não couber, sobe o speed nativo do Kokoro
(dentro do natural) ou sinaliza deslocamento de in/out.
"""
from __future__ import annotations
import json, time, sys
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path("/workspace/cinestudio/06-videos/avisos-ep03")
WORK = ROOT / "work"
RAW = WORK / "voz_raw"
TTS = Path("/workspace/tts-eval")
sys.path.insert(0, str(TTS))
from kokoro_onnx import Kokoro

SR_OUT = 48000
# id, role, text, t_in preferido, slot (duração máxima da fala antes da pausa seguinte)
LINES = [
    ("osv_1a", "osvaldo", "Se a sirene tocar e você estiver na rua,", 0.00, 3.95),
    ("osv_1b", "osvaldo", "deite-se e prenda a respiração.", 4.00, 2.95),
    ("osv_1c", "osvaldo", "Elas não procuram quem já está no fundo.", 7.00, 3.85),
    ("osv_2a", "osvaldo", "Boa noite, Vila Aurora.", 12.00, 1.75),
    ("osv_2b", "osvaldo", "Aviso à população número três.", 14.10, 2.70),
    ("osv_2c", "osvaldo", "Número três.", 16.80, 0.95),
    ("osv_3a", "osvaldo", "A Prefeitura informa que a família Moraes segue em casa.", 19.00, 4.95),
    ("osv_3b", "osvaldo", "Com visita.", 24.00, 1.50),
    ("osv_3c", "osvaldo", "Pedimos aos vizinhos que não batam à porta.", 26.00, 3.70),
    ("osv_4a", "osvaldo", "A partir desta noite, a sirene da barragem marcará o recolhimento.", 31.00, 5.90),
    ("osv_4b", "osvaldo", "Ao primeiro toque, entre em casa.", 37.00, 2.50),
    ("osv_4c", "osvaldo", "Não espere ninguém.", 40.00, 1.85),
    ("int_1", "interferencia", "Lurdes Ventura.", 44.00, 0.95),
    ("int_2", "interferencia", "Joaquim Sales.", 45.00, 1.90),
    ("int_3", "interferencia", "Teresa Brum.", 47.00, 0.90),
    ("osv_5a", "osvaldo", "Teresa Brum.", 48.00, 1.40),
    ("osv_5b", "osvaldo", "Favor deixar a porta destrancada.", 51.00, 3.20),
    ("osv_6a", "osvaldo", "A Prefeitura agradece a colaboração.", 55.00, 2.35),
    ("osv_6b", "osvaldo", "Boa noite, Vila Aurora.", 58.00, 1.85),
    ("int_4", "interferencia", "Aviso número quatro.", 62.00, 1.55),
    ("int_5", "interferencia", "Correção.", 64.00, 0.90),
    ("osv_7", "osvaldo", "Quem é Teresa?", 65.00, 1.70),
]

HARD_END = {
    "osv_1c": 10.95,
    "osv_2c": 18.95,
    "osv_3a": 23.95,
    "osv_3c": 30.90,
    "osv_4a": 36.95,
    "osv_4c": 42.90,
    "int_1": 44.98,
    "int_3": 47.92,
    "osv_5b": 54.90,
    "osv_6b": 60.90,
    "int_5": 64.95,
    "osv_7": 66.90,
}

ATEMPO_MAX = 1.10
SPEED_MIN = 0.86
SPEED_MAX = 1.08  # ainda natural para locutor


def resample(y, sr, sr_out):
    if sr == sr_out:
        return y.astype(np.float32)
    n = int(round(len(y) * sr_out / sr))
    x_old = np.linspace(0, 1, len(y), endpoint=False)
    x_new = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x_new, x_old, y.astype(np.float64)).astype(np.float32)


def time_stretch(y, sr, ratio):
    if abs(ratio - 1) < 0.008:
        return y
    n = max(8, int(round(len(y) * ratio)))
    x_old = np.linspace(0, 1, len(y), endpoint=False)
    x_new = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x_new, x_old, y.astype(np.float64)).astype(np.float32)


def trim_silence(s, sr, eps=0.008):
    idx = np.where(np.abs(s) > eps)[0]
    if len(idx):
        end = min(len(s), idx[-1] + int(0.08 * sr))
        start = max(0, idx[0] - int(0.02 * sr))
        s = s[start:end]
    return s


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    print("Loading Kokoro...", flush=True)
    k = Kokoro(str(TTS / "kokoro-v1.0.onnx"), str(TTS / "voices-v1.0.bin"))
    chosen = "pm_alex"
    reports = []

    for lid, role, text, t_in, slot in LINES:
        voice = chosen if role == "osvaldo" else "pf_dora"
        if role == "interferencia":
            speed = 0.90
        elif lid == "osv_7":
            speed = 0.86  # baixo, intrigado, sem pressa
        elif lid.startswith("osv_1"):
            speed = 0.90
        elif lid in ("osv_3a", "osv_4a"):
            speed = 0.94  # falas longas no limite do slot
        else:
            speed = 0.88

        target = max(0.25, slot - 0.04)
        note_parts = []
        used_speed = speed
        s = None
        sr = 24000
        raw_dur = 0.0

        for attempt in range(6):
            t0 = time.time()
            s, sr = k.create(text, voice=voice, speed=used_speed, lang="pt-br")
            s = trim_silence(np.asarray(s, dtype=np.float32), sr)
            raw_dur = len(s) / sr
            print(f"  gen {lid} speed={used_speed:.3f} raw={raw_dur:.3f}s (target {target:.3f}) {time.time()-t0:.1f}s", flush=True)
            if raw_dur <= target * ATEMPO_MAX:
                break
            need = used_speed * (raw_dur / (target * ATEMPO_MAX))
            new_speed = min(SPEED_MAX, max(used_speed + 0.03, need))
            if new_speed <= used_speed + 0.005:
                note_parts.append(f"speed no teto {used_speed:.3f}")
                break
            note_parts.append(f"subiu speed {used_speed:.3f}->{new_speed:.3f}")
            used_speed = new_speed

        atempo = 1.0
        stretched = s
        if raw_dur > target:
            atempo = min(ATEMPO_MAX, raw_dur / target)
            stretched = time_stretch(s, sr, 1.0 / atempo)
            note_parts.append(f"atempo={atempo:.3f}")
        else:
            note_parts.append(f"cabe natural ({raw_dur:.3f}s em {slot:.3f}s)")

        s48 = resample(stretched, sr, SR_OUT)
        raw48 = resample(s, sr, SR_OUT)
        outp = RAW / f"{lid}_fitted.wav"
        sf.write(outp, s48, SR_OUT)
        sf.write(RAW / f"{lid}_raw.wav", raw48, SR_OUT)

        rec = {
            "id": lid, "role": role, "voice": voice, "text": text,
            "in": t_in, "slot": slot, "raw_s": raw_dur, "final_s": len(s48) / SR_OUT,
            "atempo": atempo, "speed": used_speed, "speed_inicial": speed,
            "note": "; ".join(note_parts), "path": str(outp),
        }
        rec["out"] = t_in + rec["final_s"]
        rec["overflow"] = max(0.0, rec["final_s"] - slot)
        rec["hard_end"] = HARD_END.get(lid)
        if rec["hard_end"] and rec["out"] > rec["hard_end"]:
            rec["invades_boundary"] = True
        reports.append(rec)
        print(f"{lid}: {rec['note']} final={rec['final_s']:.3f} overflow={rec['overflow']:.3f}", flush=True)

    payload = {
        "osvaldo_voice": chosen,
        "interferencia_voice": "pf_dora",
        "atempo_max": ATEMPO_MAX,
        "falas": reports,
    }
    (WORK / "voices_raw_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print("DONE", chosen, flush=True)


if __name__ == "__main__":
    main()
