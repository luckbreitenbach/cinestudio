#!/usr/bin/env python3
"""Gera falas guia com Kokoro (pm_alex/pm_santa teste; pf_dora interferência)."""
from __future__ import annotations
import json, time, sys
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path("/workspace/cinestudio/06-videos/avisos-ep01")
WORK = ROOT / "work"
RAW = WORK / "voz_raw"
PER = ROOT / "stems/voz_guia"
TTS = Path("/workspace/tts-eval")
sys.path.insert(0, str(TTS))
from kokoro_onnx import Kokoro

SR_OUT = 48000
LINES = [
    # id, role, text, t_in, t_slot (target duration before trailing pause)
    ("osv_1a", "osvaldo", "Caso encontre um parente falecido sentado à sua mesa,", 0.00, 2.95),
    ("osv_1b", "osvaldo", "sirva o jantar normalmente.", 3.00, 1.20),
    ("osv_1c", "osvaldo", "Não o lembre de que ele morreu.", 5.00, 2.50),
    ("osv_2a", "osvaldo", "Boa noite, Vila Aurora.", 9.00, 1.70),
    ("osv_2b", "osvaldo", "Aviso à população número um.", 11.00, 1.35),
    ("osv_2c", "osvaldo", "Número um.", 12.40, 0.70),
    ("osv_3a", "osvaldo", "A Prefeitura informa que, a partir desta semana,", 13.00, 2.90),
    ("osv_3b", "osvaldo", "a cidade receberá Visitas.", 16.00, 2.00),
    ("osv_3c", "osvaldo", "Prezados anfitriões, não há motivo para alarme.", 19.00, 2.40),
    ("osv_3d", "osvaldo", "Basta seguir as orientações.", 22.00, 1.70),
    ("osv_4a", "osvaldo", "Mantenha sempre uma cadeira vazia à mesa.", 24.00, 2.50),
    ("osv_4b", "osvaldo", "Virada para a parede.", 27.00, 1.50),
    ("osv_4c", "osvaldo", "Não pergunte de quem é a cadeira.", 30.00, 2.20),
    ("osv_5a", "osvaldo", "Se os postes da sua rua apagarem um a um, na direção da sua casa,", 33.00, 4.40),
    ("osv_5b", "osvaldo", "desligue o rádio imediatamente.", 38.00, 1.60),
    ("osv_5c", "osvaldo", "Esta transmissão não deve ser ouvida por elas.", 40.00, 3.00),
    ("osv_6a", "osvaldo", "As Visitas são breves.", 44.00, 1.40),
    ("osv_6b", "osvaldo", "Nenhuma Visita passa da meia-noite.", 46.00, 2.20),
    ("osv_6c", "osvaldo", "A Prefeitura agradece a colaboração.", 49.00, 2.20),
    ("osv_7", "osvaldo", "O próximo aviso será transmitido na", 52.00, 2.40),
    ("int_1a", "interferencia", "Aviso à população número dois.", 55.00, 1.70),
    ("int_1b", "interferencia", "Número dois.", 56.80, 0.80),
    ("int_2a", "interferencia", "Família Moraes.", 58.00, 1.10),
    ("int_2b", "interferencia", "Rua das Paineiras, quarenta e um.", 59.20, 1.70),
    ("int_2c", "interferencia", "Arrumem a mesa.", 61.00, 1.80),
    ("osv_8", "osvaldo", "Perdão. Estamos com problemas.", 64.00, 1.85),
]

# last two cuts: trim after generation
TRIM = {
    "osv_8": 0.78,  # keep fraction of duration (cut at "probl-")
}


def resample(y, sr, sr_out):
    if sr == sr_out:
        return y.astype(np.float32)
    n = int(round(len(y) * sr_out / sr))
    x_old = np.linspace(0, 1, len(y), endpoint=False)
    x_new = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x_new, x_old, y.astype(np.float64)).astype(np.float32)


def time_stretch(y, sr, ratio):
    """Linear interpolation stretch: ratio>1 makes longer (slower)."""
    if abs(ratio - 1) < 0.01:
        return y
    n = max(8, int(round(len(y) * ratio)))
    x_old = np.linspace(0, 1, len(y), endpoint=False)
    x_new = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x_new, x_old, y.astype(np.float64)).astype(np.float32)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    print("Loading Kokoro...", flush=True)
    k = Kokoro(str(TTS / "kokoro-v1.0.onnx"), str(TTS / "voices-v1.0.bin"))
    # Voice bake-off
    test = "Boa noite, Vila Aurora. A Prefeitura agradece a colaboração. Não o lembre de que ele morreu."
    bake = {}
    for v, spd in (("pm_alex", 0.88), ("pm_santa", 0.88)):
        t0 = time.time()
        s, sr = k.create(test, voice=v, speed=spd, lang="pt-br")
        s = np.asarray(s, dtype=np.float32)
        out = RAW / f"teste_{v}.wav"
        sf.write(out, s, sr)
        # f0 rough
        mid = s[len(s)//5:4*len(s)//5]
        mid = mid - mid.mean()
        step = max(1, sr // 8000)
        sd = mid[::step]; srd = sr / step
        minp, maxp = int(srd/300), int(srd/70)
        ac = np.correlate(sd, sd, mode="full")[len(sd)-1:]
        lag = int(np.argmax(ac[minp:maxp])) + minp
        f0 = srd / lag
        bake[v] = {"dur": len(s)/sr, "f0": f0, "rms": float(np.sqrt(np.mean(s**2))), "path": str(out), "gen_s": time.time()-t0}
        print(f"TEST {v}: dur={len(s)/sr:.2f}s f0~{f0:.1f} rms={bake[v]['rms']:.3f}", flush=True)
    # Prefer lower, calmer, older-sounding. If f0 is octave-ambiguous, prefer santa if closer to 110-140 (mature male),
    # alex if truly low. Radio announcer 61yo typically ~100-130 Hz.
    # We'll also consider "santa" name as possibly deeper character - use measured f0 in 80-160 range (correct octave).
    def norm_f0(f):
        while f < 70: f *= 2
        while f > 180: f /= 2
        return f
    f_alex = norm_f0(bake["pm_alex"]["f0"])
    f_santa = norm_f0(bake["pm_santa"]["f0"])
    # Choose the lower (graver) voice for Osvaldo
    chosen = "pm_alex" if f_alex <= f_santa + 5 else "pm_santa"
    # slight preference for santa if both close? No: graver wins.
    print(f"CHOSEN Osvaldo={chosen} (f0 alex={f_alex:.1f} santa={f_santa:.1f})", flush=True)

    reports = []
    for lid, role, text, t_in, slot in LINES:
        voice = chosen if role == "osvaldo" else "pf_dora"
        # starting speed: osvaldo slower, dora a bit slower/calmer, hook a tad faster
        if role == "interferencia":
            speed = 0.90
        elif lid in ("osv_1a", "osv_1b", "osv_1c"):
            speed = 0.92  # gancho um pouco mais perto de 2.8 wps
        else:
            speed = 0.86
        t0 = time.time()
        s, sr = k.create(text, voice=voice, speed=speed, lang="pt-br")
        s = np.asarray(s, dtype=np.float32)
        # trim trailing silence
        eps = 0.008
        idx = np.where(np.abs(s) > eps)[0]
        if len(idx):
            end = min(len(s), idx[-1] + int(0.08 * sr))
            start = max(0, idx[0] - int(0.02 * sr))
            s = s[start:end]
        raw_p = RAW / f"{lid}_raw.wav"
        sf.write(raw_p, s, sr)
        dur = len(s) / sr
        # fit into slot (leave 40ms)
        target = max(0.25, slot - 0.04)
        note = "ok"
        ratio = 1.0
        atempo = 1.0
        if dur > target:
            atempo = dur / target
            cap = 1.25
            if atempo > cap:
                note = f"APERTADO precisa {atempo:.3f}x; cap {cap}x"
                atempo = cap
            else:
                note = f"ajustado atempo={atempo:.3f}"
            # atempo>1 means faster = shorter. time_stretch ratio = 1/atempo
            s = time_stretch(s, sr, 1.0 / atempo)
        else:
            note = f"cabe natural ({dur:.3f}s em {slot:.3f}s)"
        if lid in TRIM:
            keep = int(len(s) * TRIM[lid])
            s = s[:keep]
            # sharp cut, tiny fade 8ms
            fade = int(0.008 * sr)
            if fade < len(s):
                s[-fade:] *= np.linspace(1, 0, fade)
            note += f" | corte no fim (frac={TRIM[lid]})"
        s48 = resample(s, sr, SR_OUT)
        outp = RAW / f"{lid}_fitted.wav"
        sf.write(outp, s48, SR_OUT)
        rec = {
            "id": lid, "role": role, "voice": voice, "text": text,
            "in": t_in, "slot": slot, "raw_s": dur, "final_s": len(s48)/SR_OUT,
            "atempo": atempo, "note": note, "path": str(outp), "speed": speed,
        }
        rec["out"] = t_in + rec["final_s"]
        rec["overflow"] = max(0.0, rec["final_s"] - slot)
        reports.append(rec)
        print(f"{lid}: {note} final={rec['final_s']:.3f} overflow={rec['overflow']:.3f}", flush=True)

    payload = {"osvaldo_voice": chosen, "bakeoff": bake, "falas": reports,
               "interferencia_voice": "pf_dora"}
    (WORK / "voices_raw_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print("DONE", chosen, flush=True)


if __name__ == "__main__":
    main()
