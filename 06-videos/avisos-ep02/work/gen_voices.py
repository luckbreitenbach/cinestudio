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

ROOT = Path("/workspace/cinestudio/06-videos/avisos-ep02")
WORK = ROOT / "work"
RAW = WORK / "voz_raw"
TTS = Path("/workspace/tts-eval")
sys.path.insert(0, str(TTS))
from kokoro_onnx import Kokoro

SR_OUT = 48000
# id, role, text, t_in preferido, slot (duração máxima da fala antes da pausa seguinte)
# slots deixam a pausa do roteiro sempre que possível
LINES = [
    ("osv_1a", "osvaldo", "Se sobrar uma pessoa à sua mesa,", 0.00, 2.90),
    ("osv_1b", "osvaldo", "não conte de novo.", 3.00, 2.20),
    ("osv_1c", "osvaldo", "A primeira conta é a certa.", 6.00, 2.80),
    ("osv_2a", "osvaldo", "Boa noite, Vila Aurora.", 10.00, 1.75),
    ("osv_2b", "osvaldo", "Aviso à população número dois.", 12.10, 2.70),
    ("osv_2c", "osvaldo", "Número dois.", 14.90, 0.95),
    ("osv_3a", "osvaldo", "Na última terça-feira, a família Moraes, da Rua das Paineiras,", 16.00, 4.35),
    ("osv_3b", "osvaldo", "recebeu sua Visita, conforme previsto.", 21.00, 2.80),
    ("osv_3c", "osvaldo", "A mesa estava arrumada.", 24.00, 2.35),
    ("osv_3d", "osvaldo", "A Prefeitura parabeniza a família.", 27.00, 2.00),
    ("osv_4a", "osvaldo", "Durante o jantar, não conte os presentes em voz alta.", 30.00, 4.20),
    ("osv_4b", "osvaldo", "As Visitas gostam de ser incluídas.", 35.30, 2.70),
    ("osv_4c", "osvaldo", "Se uma criança contar, não a corrija.", 39.00, 3.15),
    ("osv_5a", "osvaldo", "A família Moraes informa que não precisa mais da cadeira vazia.", 43.00, 5.15),
    ("osv_5b", "osvaldo", "Ela já está ocupada.", 49.00, 1.90),
    ("osv_6a", "osvaldo", "A Prefeitura agradece a colaboração.", 52.00, 2.35),
    ("osv_6b", "osvaldo", "Boa noite, Neide.", 55.00, 1.55),
    ("osv_6c", "osvaldo", "Boa noite, Vila Aurora.", 57.00, 1.85),
    ("int_1", "interferencia", "Aviso número três.", 60.00, 1.55),
    ("int_2", "interferencia", "Quando a sirene tocar, não espere ninguém.", 63.00, 3.50),
]

# limites de seção (fala não pode invadir)
HARD_END = {
    "osv_1c": 8.95,
    "osv_2c": 15.95,
    "osv_3d": 29.90,
    "osv_4c": 42.95,
    "osv_5b": 51.95,
    "osv_6c": 58.95,
    "int_2": 66.85,
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
        elif lid.startswith("osv_1"):
            speed = 0.92
        elif lid == "osv_6b":
            speed = 0.88  # Neide, natural, sem pressa
        elif lid == "osv_6c":
            speed = 0.90  # correção calma
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
            # precisa mais speed nativo
            need = used_speed * (raw_dur / (target * ATEMPO_MAX))
            new_speed = min(SPEED_MAX, max(used_speed + 0.03, need))
            if new_speed <= used_speed + 0.005:
                note_parts.append(f"speed no teto {used_speed:.3f}")
                break
            note_parts.append(f"subiu speed {used_speed:.3f}->{new_speed:.3f}")
            used_speed = new_speed

        atempo = 1.0
        if raw_dur > target:
            atempo = min(ATEMPO_MAX, raw_dur / target)
            s = time_stretch(s, sr, 1.0 / atempo)
            note_parts.append(f"atempo={atempo:.3f}")
        else:
            note_parts.append(f"cabe natural ({raw_dur:.3f}s em {slot:.3f}s)")

        s48 = resample(s, sr, SR_OUT)
        outp = RAW / f"{lid}_fitted.wav"
        sf.write(outp, s48, SR_OUT)
        sf.write(RAW / f"{lid}_raw.wav", resample(s, sr, SR_OUT) if False else resample(
            # keep a pre-atempo copy already consumed; raw_dur file:
            # re-read not needed; write fitted only + metadata
            s, sr, SR_OUT
        ), SR_OUT)

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
