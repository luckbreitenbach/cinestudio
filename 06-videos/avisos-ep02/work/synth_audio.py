#!/usr/bin/env python3
"""SFX locais + stems de voz (seca e filtrada) + mix do Aviso nº 2."""
from __future__ import annotations
import json, math, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf

SR = 48000
DUR = 68.0
EP = Path("/workspace/cinestudio/06-videos/avisos-ep02")
WORK = EP / "work"
STEMS = EP / "stems"
VOZDIR = STEMS / "voz_guia"
AUDIO = EP / "audio"
CLIPS = Path("/workspace/cinestudio/05-cenas/avisos-ep02")
SHARED = Path("/workspace/cinestudio/06-videos/avisos-shared")
DURS = [9.0, 7.0, 7.0, 7.0, 7.0, 6.0, 9.0, 7.0, 3.0, 5.0, 1.0]
STARTS = np.cumsum([0.0] + DURS[:-1]).tolist()


def fade(n, a, b=None):
    if b is None:
        b = a
    env = np.ones(n, np.float32)
    fa = int(a * n) if a < 1 else int(a)
    fb = int(b * n) if b < 1 else int(b)
    fa = max(1, fa); fb = max(1, fb)
    env[:fa] *= np.linspace(0, 1, fa)
    env[-fb:] *= np.linspace(1, 0, fb)
    return env


def vibraphone_note(f, dur, amp=0.35, detune=0.0, descend=False):
    t = np.arange(int(dur * SR)) / SR
    freq = f * (2 ** (detune / 12))
    if descend:
        freq = freq * (1 - 0.08 * t / max(dur, 0.01))
    sig = np.zeros_like(t)
    for a, p in [(1.0, 1.0), (0.45, 3.95), (0.22, 9.1), (0.1, 12.8)]:
        sig += a * np.sin(2 * np.pi * freq * p * t)
    trem = 1 + 0.35 * np.sin(2 * np.pi * 5.4 * t)
    att = np.minimum(t / 0.008, 1.0)
    env = np.exp(-t * 2.15) * att * trem
    return (amp * sig * env).astype(np.float32)


def vinheta():
    notes = [196.0, 246.94, 329.63]
    parts = []
    gap = int(0.12 * SR)
    for i, f in enumerate(notes):
        parts.append(vibraphone_note(f, 1.15, amp=0.4 * (0.9 + 0.1 * i)))
        parts.append(np.zeros(gap, np.float32))
    v = np.concatenate(parts)
    t = np.arange(int(0.38 * SR)) / SR
    tone = 0.22 * np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 6) * np.minimum(t / 0.01, 1)
    pos = len(v) - len(tone) - int(0.15 * SR)
    if pos < 0:
        pos = 0
        v = np.pad(v, (0, len(tone)))
    if pos + len(tone) > len(v):
        v = np.pad(v, (0, pos + len(tone) - len(v)))
    v[pos:pos + len(tone)] += tone.astype(np.float32)
    return v


def click(dur=0.12, kind="projector"):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3 if kind == "projector" else 11)
    noise = rng.normal(0, 1, n).astype(np.float32)
    if kind == "projector":
        thump = 0.6 * np.sin(2 * np.pi * 80 * t) * np.exp(-t * 40)
        tick = np.convolve(noise * np.exp(-t * 90), np.array([1, -1], np.float32), mode="same")
        sig = thump + 0.35 * tick
    else:
        buzz = 0.5 * np.sin(2 * np.pi * 120 * t) * np.exp(-t * 25)
        snap = np.convolve(noise * np.exp(-t * 120), np.array([1, -1, 0], np.float32), mode="same")
        sig = buzz + 0.7 * snap
    return (sig * fade(n, 0.002, 0.04)).astype(np.float32)


def creak(dur=0.85):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(21)
    f = 420 + 180 * np.sin(2 * np.pi * 3.2 * t) + 80 * t
    ph = np.cumsum(2 * np.pi * f / SR)
    wood = 0.25 * np.sin(ph) + 0.15 * np.sin(2 * ph)
    noise = rng.normal(0, 0.4, n)
    bp = noise.copy()
    for _ in range(2):
        bp = np.convolve(bp, np.array([1, 0, -1], np.float32), mode="same")
    sig = wood + 0.2 * bp
    env = np.exp(-((t - 0.2) ** 2) / (2 * 0.15 ** 2)) * (0.4 + 0.6 * (np.sin(2 * np.pi * 6 * t) * 0.5 + 0.5))
    return (0.45 * sig * env * fade(n, 0.02, 0.12)).astype(np.float32)


def dial_whistle(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 7000 * (400 / 7000) ** (t / dur)
    ph = np.cumsum(2 * np.pi * f / SR)
    return (0.28 * np.sin(ph) * fade(n, 0.05, 0.2)).astype(np.float32)


def am_bed(dur=DUR, hiss=0.045, hum=0.02):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    noise = rng.normal(0, 1, n).astype(np.float32)
    for i in range(1, len(noise)):
        noise[i] = 0.6 * noise[i] + 0.4 * noise[i - 1]
    hums = hum * (0.7 * np.sin(2 * np.pi * 60 * t) + 0.2 * np.sin(2 * np.pi * 120 * t))
    return (hiss * noise + hums).astype(np.float32)


def sirene(dur=12.0, seed=870):
    """Sirene grave de barragem (arquivo-assinatura da série)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    # ciclo lento ~0.22 Hz, tom grave 150–260 Hz + harmônicos de buzina
    lfo = 0.5 * (1 + np.sin(2 * np.pi * 0.22 * t - np.pi / 2))
    f = 155 + 95 * lfo
    ph = np.cumsum(2 * np.pi * f / SR)
    y = 0.62 * np.sin(ph) + 0.28 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    y += 0.05 * np.sin(np.cumsum(2 * np.pi * (f * 1.01) / SR))  # beating leve
    y = np.tanh(y * 1.25)
    # ataque lento, sem corte no fim (o mix é que corta)
    att = np.minimum(t / 0.8, 1.0)
    y = y * att
    return y.astype(np.float32)


def place(canvas, sig, at, gain=1.0):
    i = int(round(at * SR))
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = i + len(sig)
    if j > len(canvas):
        sig = sig[: len(canvas) - i]
        j = len(canvas)
    if len(sig) <= 0:
        return
    canvas[i:j] += sig * gain


def biquad_lp(x, cutoff, sr=SR, q=0.7):
    w0 = 2 * math.pi * cutoff / sr
    alpha = math.sin(w0) / (2 * q)
    cosw = math.cos(w0)
    b0 = (1 - cosw) / 2
    b1 = 1 - cosw
    b2 = (1 - cosw) / 2
    a0 = 1 + alpha
    a1 = -2 * cosw
    a2 = 1 - alpha
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, xn in enumerate(x):
        yn = b0 * xn + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        y[i] = yn
        x2, x1, y2, y1 = x1, xn, y1, yn
    return y


def biquad_hp(x, cutoff, sr=SR, q=0.7):
    w0 = 2 * math.pi * cutoff / sr
    alpha = math.sin(w0) / (2 * q)
    cosw = math.cos(w0)
    b0 = (1 + cosw) / 2
    b1 = -(1 + cosw)
    b2 = (1 + cosw) / 2
    a0 = 1 + alpha
    a1 = -2 * cosw
    a2 = 1 - alpha
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, xn in enumerate(x):
        yn = b0 * xn + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        y[i] = yn
        x2, x1, y2, y1 = x1, xn, y1, yn
    return y


def compress(x, thresh=0.15, ratio=3.0, makeup=1.4):
    env = np.zeros_like(x)
    atk, rel = 0.003 * SR, 0.05 * SR
    a_a, a_r = 1 / atk, 1 / rel
    e = 0.0
    ax = np.abs(x)
    for i, v in enumerate(ax):
        e += (a_a if v > e else a_r) * (v - e)
        env[i] = e
    g = np.ones_like(x)
    over = env > thresh
    g[over] = (thresh + (env[over] - thresh) / ratio) / (env[over] + 1e-9)
    return np.clip(x * g * makeup, -0.99, 0.99)


def am_filter(x, lo=300, hi=3400, speaker=False, muffle=False):
    y = biquad_hp(x, lo)
    y = biquad_lp(y, hi)
    if speaker:
        d = int(0.004 * SR)
        c = np.zeros_like(y)
        c[d:] = y[:-d]
        y = 0.85 * y + 0.25 * c
        y = biquad_lp(y, 2800)
    if muffle:
        y = biquad_lp(y, 2200)
        y = biquad_hp(y, 450)
    y = compress(y, thresh=0.12, ratio=3.5, makeup=1.55)
    y = np.tanh(y * 1.3) * 0.92
    return y.astype(np.float32)


def load48(path):
    y, sr = sf.read(path, always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        n = int(round(len(y) * SR / sr))
        y = np.interp(np.linspace(0, 1, n, endpoint=False), np.linspace(0, 1, len(y), endpoint=False), y)
    return y.astype(np.float32)


def stereo(x):
    if x.ndim == 2:
        return x
    return np.stack([x, x], axis=1)


def pack_lines(falas):
    """Ajusta in/out com folga, sem atempo extra, reportando desvios."""
    by = {f["id"]: dict(f) for f in falas}
    notes = []
    # 2c natural ~1.10s: começa 0,4s após 2b (roteiro), termina antes de 16.00
    b_out = by["osv_2b"]["in"] + by["osv_2b"]["final_s"]
    by["osv_2c"]["in"] = b_out + 0.40
    by["osv_2c"]["out"] = by["osv_2c"]["in"] + by["osv_2c"]["final_s"]
    notes.append(f"osv_2c deslocado para {by['osv_2c']['in']:.3f}–{by['osv_2c']['out']:.3f} (pausa 0,4s após 2b; folga até 16,00 = {16.0-by['osv_2c']['out']:.3f}s). Sem atempo.")
    # 3d natural ~2.38s: começa 27.00, pausa até 30 reduzida de 1,2s para ~0,62s
    by["osv_3d"]["in"] = 27.00
    by["osv_3d"]["out"] = 27.00 + by["osv_3d"]["final_s"]
    notes.append(f"osv_3d natural até {by['osv_3d']['out']:.3f}; pausa seguinte {30.0-by['osv_3d']['out']:.3f}s (roteiro pedia 1,2s).")
    # 6a natural ~2.60s: começa no corte do p8 (52.00), pausa até 6b reduzida de 0,6s para ~0,40s
    by["osv_6a"]["in"] = 52.00
    by["osv_6a"]["out"] = 52.00 + by["osv_6a"]["final_s"]
    notes.append(f"osv_6a natural até {by['osv_6a']['out']:.3f}; pausa até Neide {55.0-by['osv_6a']['out']:.3f}s (roteiro 0,6s).")
    # recompute out for all
    for f in by.values():
        f["out"] = f["in"] + f["final_s"]
    return list(by.values()), notes


def extract_amb():
    bed = np.zeros(int(DUR * SR), np.float32)
    for i, (d, st) in enumerate(zip(DURS, STARTS), start=1):
        wav = WORK / f"amb_p{i:02d}.wav"
        src = CLIPS / f"plano-{i:02d}.mp4"
        tt = d if i != 8 else 2.80
        subprocess.run([
            "ffmpeg", "-y", "-i", str(src), "-t", f"{tt:.4f}",
            "-ac", "1", "-ar", str(SR), "-vn", str(wav),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        y = load48(wav)
        if i == 2:
            y = y * 0.08
        elif i == 11:
            y = y * 0.15
        else:
            y = y * 0.28
        place(bed, y, st, 1.0)
        # p8 hold: não repetir áudio das mãos; silêncio no freeze
    return bed


def main():
    STEMS.mkdir(parents=True, exist_ok=True)
    VOZDIR.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    SHARED.mkdir(parents=True, exist_ok=True)
    report = json.loads((WORK / "voices_raw_report.json").read_text())
    falas, pack_notes = pack_lines(report["falas"])
    print("PACK:", *pack_notes, sep="\n  ", flush=True)

    n = int(DUR * SR)
    dry = np.zeros(n, np.float32)
    wet = np.zeros(n, np.float32)
    timeline = []

    for f in falas:
        y = load48(f["path"])
        fa = int(0.008 * SR)
        if len(y) > 2 * fa:
            y[:fa] *= np.linspace(0, 1, fa)
            y[-fa:] *= np.linspace(1, 0, fa)
        gain = 1.0
        if f["id"] == "osv_6c":
            gain = 0.78  # correção um pouco mais baixa
        elif f["id"] == "osv_6b":
            gain = 1.0
        place(dry, y, f["in"], gain)
        # filtro por papel
        if f["role"] == "interferencia":
            yw = am_filter(y, lo=450, hi=2200, muffle=True)
            yw = yw * 0.92
        elif f["id"] in ("osv_6a", "osv_6b", "osv_6c"):
            # close de microfone no estúdio: AM um pouco mais aberto
            yw = am_filter(y, lo=220, hi=4200, speaker=False)
        else:
            yw = am_filter(y, lo=300, hi=3400)
        yw = yw * gain
        place(wet, yw, f["in"], 1.0)
        sf.write(VOZDIR / f"{f['id']}_dry.wav", y, SR)
        sf.write(VOZDIR / f"{f['id']}_filt.wav", yw, SR)
        rec = {
            "id": f["id"], "role": f["role"], "text": f["text"],
            "in": round(f["in"], 4), "out": round(f["in"] + len(y) / SR, 4),
            "dur": round(len(y) / SR, 4),
            "speed": f.get("speed"), "atempo": f.get("atempo", 1.0),
            "gain": gain, "note": f.get("note", ""),
        }
        timeline.append(rec)
        print(f"place {rec['id']} {rec['in']:.3f}-{rec['out']:.3f}", flush=True)

    # SFX
    sfx = np.zeros(n, np.float32)
    v = vinheta()
    clk = click(0.14, "projector")
    crk = creak(0.90)
    dw = dial_whistle(1.55)
    sir = sirene(12.0)
    # vinheta + clique no começo da cartela (0:09)
    place(sfx, v, 9.00, 0.85)
    place(sfx, clk, 9.05, 0.9)
    # rangido depois de "ocupada" (fala termina ~50.70)
    ocupada_out = next(t for t in timeline if t["id"] == "osv_5b")["out"]
    creak_at = ocupada_out + 0.12
    place(sfx, crk, creak_at, 0.7)
    print(f"creak at {creak_at:.3f}", flush=True)
    # assobio de dial na entrada da interferência
    place(sfx, dw, 58.95, 0.75)
    # sirene muito longe a partir de ~1:04, corte seco em 1:07
    sir_at = 64.00
    sir_use = sir.copy()
    # lowpass + nível baixo (longe)
    sir_use = biquad_lp(sir_use, 900) * 0.18
    # fade in 1.2s
    fi = int(1.2 * SR)
    sir_use[:fi] *= np.linspace(0, 1, fi)
    # hard cut at 67.00
    cut = int(67.00 * SR)
    start = int(sir_at * SR)
    take = cut - start
    place(sfx, sir_use[:take], sir_at, 1.0)
    # tiny click of cut already silence after

    # isolated audio files
    sf.write(AUDIO / "vinheta-vibrafone.wav", v, SR)
    sf.write(AUDIO / "clique-projetor.wav", clk, SR)
    sf.write(AUDIO / "rangido-madeira.wav", crk, SR)
    sf.write(AUDIO / "dial-whistle.wav", dw, SR)
    sf.write(AUDIO / "sirene-barragem.wav", sir, SR)
    sf.write(SHARED / "sirene-barragem.wav", sir, SR)

    chi = am_bed(DUR, hiss=0.048, hum=0.018)
    # chiado sobe na interferência (59–67)
    t = np.arange(n) / SR
    bump = np.clip((t - 58.8) / 0.8, 0, 1) * np.clip((67.0 - t) / 0.05, 0, 1)
    # hard zero after 67
    bump[t >= 67.0] = 0
    chi = chi * (1.0 + 1.6 * bump)

    amb = extract_amb()

    # stems
    sf.write(STEMS / "stem_voz_dry.wav", stereo(np.clip(dry, -1, 1)), SR)
    sf.write(STEMS / "stem_voz_guia.wav", stereo(np.clip(wet, -1, 1)), SR)
    sf.write(STEMS / "stem_voz_guia_kokoro.wav", stereo(np.clip(wet, -1, 1)), SR)
    sf.write(STEMS / "stem_ambiente.wav", stereo(np.clip(amb, -1, 1)), SR)
    sf.write(STEMS / "stem_am_chiado.wav", stereo(np.clip(chi, -1, 1)), SR)
    sf.write(STEMS / "stem_sfx_vinheta.wav", stereo(np.clip(sfx, -1, 1)), SR)

    # guide mix (pre-loudnorm; o mux final normaliza)
    mix = amb * 0.7 + chi * 1.0 + sfx * 1.0
    # duck simples
    voice_env = np.convolve(np.abs(wet), np.ones(int(0.05 * SR)) / (0.05 * SR), mode="same")
    duck = 1.0 / (1.0 + 3.2 * voice_env)
    mix = mix * duck * 0.8 + wet * 1.15
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 0.85
    sf.write(STEMS / "stem_mix_guia_pre_loudnorm.wav", stereo(mix.astype(np.float32)), SR)

    payload = {
        "duration": DUR,
        "pack_notes": pack_notes,
        "creak_at": creak_at,
        "sirene_at": sir_at,
        "sirene_cut": 67.00,
        "timeline": timeline,
    }
    (WORK / "voice_timeline_guia.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print("AUDIO DONE creak", creak_at, "sirene", sir_at, "->67.00", flush=True)


if __name__ == "__main__":
    main()
