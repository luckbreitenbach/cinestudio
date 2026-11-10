#!/usr/bin/env python3
"""SFX sintéticos locais + mix da faixa de voz guia (AM) + stems."""
from __future__ import annotations
import json, math, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

SR = 48000
DUR = 66.0
EP = Path("/workspace/cinestudio/06-videos/avisos-ep01")
WORK = EP / "work"
STEMS = EP / "stems"
VOZDIR = STEMS / "voz_guia"
CLIPS = Path("/workspace/cinestudio/05-cenas/avisos-ep01")


def fade(n, a, b=None):
    if b is None:
        b = a
    env = np.ones(n, np.float32)
    fa, fb = int(a * n) if a < 1 else int(a), int(b * n) if b < 1 else int(b)
    fa = max(1, fa); fb = max(1, fb)
    env[:fa] *= np.linspace(0, 1, fa)
    env[-fb:] *= np.linspace(1, 0, fb)
    return env


def sine(f, t, ph=0):
    return np.sin(2 * np.pi * f * t + ph)


def vibraphone_note(f, dur, amp=0.35, detune=0.0, descend=False):
    t = np.arange(int(dur * SR)) / SR
    freq = f * (2 ** (detune / 12))
    if descend:
        freq = freq * (1 - 0.08 * t / max(dur, 0.01))
    sig = np.zeros_like(t)
    # inharmonic partials of a metal bar
    parts = [(1.0, 1.0), (0.45, 3.95), (0.22, 9.1), (0.1, 12.8)]
    for a, p in parts:
        sig += a * np.sin(2 * np.pi * freq * p * t)
    trem = 1 + 0.35 * np.sin(2 * np.pi * 5.4 * t)
    att = np.minimum(t / 0.008, 1.0)
    env = np.exp(-t * 2.15) * att * trem
    return (amp * sig * env).astype(np.float32)


def vinheta(ascend=True, start_amp=0.4):
    # three notes + prefix tone
    if ascend:
        notes = [196.0, 246.94, 329.63]  # G3 B3 E4
        det = 0.0
        descend = False
    else:
        notes = [329.63, 246.94, 196.0]
        det = -0.35
        descend = True
    parts = []
    gap = int(0.12 * SR)
    for i, f in enumerate(notes):
        parts.append(vibraphone_note(f, 1.15, amp=start_amp * (0.9 + 0.1 * i), detune=det, descend=descend))
        parts.append(np.zeros(gap, np.float32))
    v = np.concatenate(parts)
    # prefix tone (short 1000 Hz, slightly rounded)
    if ascend:
        t = np.arange(int(0.38 * SR)) / SR
        tone = 0.22 * np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 6) * np.minimum(t / 0.01, 1)
        # lay tone over last note
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
        # mechanical thump + tick
        thump = 0.6 * np.sin(2 * np.pi * 80 * t) * np.exp(-t * 40)
        tick = noise * np.exp(-t * 90)
        # crude highpass on tick
        tick = np.convolve(tick, np.array([1, -1], np.float32), mode="same")
        sig = thump + 0.35 * tick
    else:
        # electrical clac
        buzz = 0.5 * np.sin(2 * np.pi * 120 * t) * np.exp(-t * 25)
        snap = noise * np.exp(-t * 120)
        snap = np.convolve(snap, np.array([1, -1, 0], np.float32), mode="same")
        sig = buzz + 0.7 * snap
    return (sig * fade(n, 0.002, 0.04)).astype(np.float32)


def creak(dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(21)
    # noisy oscillator with slow freq sweep
    f = 420 + 180 * np.sin(2 * np.pi * 3.2 * t) + 80 * t
    ph = np.cumsum(2 * np.pi * f / SR)
    wood = 0.25 * np.sin(ph) + 0.15 * np.sin(2 * ph)
    noise = rng.normal(0, 0.4, n)
    # band-pass-ish via simple differences + smooth
    bp = noise.copy()
    for _ in range(2):
        bp = np.convolve(bp, np.array([1, 0, -1], np.float32), mode="same")
    sig = wood + 0.2 * bp
    env = np.exp(-((t - 0.2) ** 2) / (2 * 0.15 ** 2)) * (0.4 + 0.6 * (np.sin(2 * np.pi * 6 * t) * 0.5 + 0.5))
    return (0.45 * sig * env * fade(n, 0.02, 0.12)).astype(np.float32)


def dial_whistle(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    # exponential sweep 7k -> 400
    f = 7000 * (400 / 7000) ** (t / dur)
    ph = np.cumsum(2 * np.pi * f / SR)
    sig = 0.28 * np.sin(ph)
    return (sig * fade(n, 0.05, 0.2)).astype(np.float32)


def sizzle(dur=4.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(99)
    noise = rng.normal(0, 1, n).astype(np.float32)
    # highpassed hiss that grows
    hp = np.convolve(noise, np.array([1, -1], np.float32), mode="same")
    env = np.clip((t / 1.2) ** 1.2, 0, 1) * (0.15 + 0.25 * (t / dur))
    return (0.22 * hp * env * fade(n, 0.05, 0.4)).astype(np.float32)


def am_bed(dur=DUR, hiss=0.045, hum=0.02):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    noise = rng.normal(0, 1, n).astype(np.float32)
    # slightly brown
    for i in range(1, len(noise)):
        noise[i] = 0.6 * noise[i] + 0.4 * noise[i - 1]
    hums = hum * (0.7 * np.sin(2 * np.pi * 60 * t) + 0.2 * np.sin(2 * np.pi * 120 * t))
    return (hiss * noise + hums).astype(np.float32)


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
    """Simple RBJ lowpass."""
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
        if v > e:
            e += a_a * (v - e)
        else:
            e += a_r * (v - e)
        env[i] = e
    g = np.ones_like(x)
    over = env > thresh
    g[over] = (thresh + (env[over] - thresh) / ratio) / (env[over] + 1e-9)
    return np.clip(x * g * makeup, -0.99, 0.99)


def am_filter(x, lo=300, hi=3400, speaker=False, muffle=False):
    y = biquad_hp(x, lo)
    y = biquad_lp(y, hi)
    if speaker:
        # box resonance ~1.2k
        t = np.arange(len(y)) / SR
        # short comb
        d = int(0.004 * SR)
        c = np.zeros_like(y)
        c[d:] = y[:-d]
        y = 0.85 * y + 0.25 * c
        y = biquad_lp(y, 2800)
    if muffle:
        y = biquad_lp(y, 2200)
        y = biquad_hp(y, 450)
        # slight delay already applied outside
    y = compress(y, thresh=0.12, ratio=3.5, makeup=1.55)
    # gentle saturate
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


def extract_amb(planos, durs, starts):
    """Extract/trim original clip audio as ambient bed, mute p7 murmur (keep very low)."""
    bed = np.zeros(int(DUR * SR), np.float32)
    for i, (p, d, st) in enumerate(zip(planos, durs, starts), start=1):
        wav = WORK / f"amb_p{i:02d}.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(p), "-t", f"{d:.4f}",
            "-ac", "1", "-ar", str(SR), "-vn", str(wav)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        y = load48(wav)
        if i == 7:
            y = y * 0.04  # almost drop murmur
        else:
            y = y * 0.35
        place(bed, y, st, 1.0)
    return bed


def main():
    STEMS.mkdir(parents=True, exist_ok=True)
    VOZDIR.mkdir(parents=True, exist_ok=True)
    report = json.loads((WORK / "voices_raw_report.json").read_text())
    falas = report["falas"]
    # fix osv_5b collision: start earlier after 5a
    by = {f["id"]: f for f in falas}
    # 5a ends ~37.27; start 5b at 37.85 (sub 38.00 is 150ms — borderline, report it)
    by["osv_5b"]["in"] = 37.85
    by["osv_5b"]["out"] = 37.85 + by["osv_5b"]["final_s"]
    # resolve overlaps with planned sub times (report residuals later)
    by["osv_2b"]["in"] = 10.85
    by["osv_2b"]["out"] = 10.85 + by["osv_2b"]["final_s"]  # ~12.52
    by["osv_2c"]["in"] = 12.55
    by["osv_2c"]["out"] = 12.55 + by["osv_2c"]["final_s"]  # ~13.31
    by["osv_3a"]["in"] = 13.28
    by["osv_3a"]["out"] = 13.28 + by["osv_3a"]["final_s"]
    by["int_1b"]["in"] = max(by["int_1a"]["out"] + 0.06, 56.85)
    by["int_1b"]["out"] = by["int_1b"]["in"] + by["int_1b"]["final_s"]
    # keep 3a's slight start delay; 3b still at 16.00

    n = int(DUR * SR)
    dry = np.zeros(n, np.float32)
    for f in falas:
        y = load48(f["path"])
        # tiny fade in
        fa = int(0.008 * SR)
        if len(y) > 2 * fa:
            y[:fa] *= np.linspace(0, 1, fa)
            if f["id"] not in ("osv_7", "osv_8"):
                y[-fa:] *= np.linspace(1, 0, fa)
        place(dry, y, f["in"], 1.0)
        # save per-line wet later
        sf.write(VOZDIR / f"{f['id']}_dry.wav", y, SR)

    # apply character filters in regions
    # default AM on all osvaldo; speaker 39-44; interference muffled
    wet = np.zeros_like(dry)
    # process in chunks by role using a mask would be hard because overlap none
    # simpler: filter each line separately
    for f in falas:
        y = load48(f["path"])
        fa = int(0.008 * SR)
        if len(y) > 2 * fa:
            y[:fa] *= np.linspace(0, 1, fa)
            if f["id"] not in ("osv_7", "osv_8"):
                y[-fa:] *= np.linspace(1, 0, fa)
        t0, t1 = f["in"], f["in"] + len(y) / SR
        if f["role"] == "interferencia":
            y = am_filter(y, lo=450, hi=2200, muffle=True)
            # slight pre-delay 40ms
            y = np.concatenate([np.zeros(int(0.04 * SR), np.float32), y])
            y *= 0.9
        else:
            speaker = (t0 < 44.0 and t1 > 39.0)  # overlaps p7
            if speaker and t0 >= 39.0:
                y = am_filter(y, lo=320, hi=3000, speaker=True)
            else:
                y = am_filter(y, lo=300, hi=3400, speaker=False)
        # osv_8 closer to mic (less filter, a bit more presence) still AM
        if f["id"] == "osv_8":
            y = am_filter(load48(f["path"]), lo=250, hi=4000, speaker=False)
            y *= 1.15
        sf.write(VOZDIR / f"{f['id']}.wav", y, SR)
        place(wet, y, f["in"], 1.0)

    # hard cut after probl—
    cut_at = int(min(DUR, by["osv_8"]["in"] + by["osv_8"]["final_s"] + 0.02) * SR)
    wet[cut_at:] = 0
    dry[cut_at:] = 0

    sf.write(STEMS / "stem_voz_guia_kokoro.wav", np.clip(wet, -0.99, 0.99), SR)
    sf.write(STEMS / "stem_voz_guia_dry.wav", np.clip(dry, -0.99, 0.99), SR)

    # SFX bed
    sfx = np.zeros(n, np.float32)
    # vinheta at 8.00 (about 1s, voice enters on last note ~9.00)
    vin = vinheta(True)
    # we want last note around 8.7-9.0, first note at 8.00
    # vinheta length is ~3 notes * 1.15 + gaps — too long. Trim/compress placement:
    # place so start is 8.00 and last-note attack ~8.85
    # rebuild shorter notes
    def short_vin(asc=True, note_dur=0.55, amp=0.38):
        notes = [196.0, 246.94, 329.63] if asc else [311.0, 220.0, 174.0]
        chunks = []
        for i, f0 in enumerate(notes):
            chunks.append(vibraphone_note(f0, note_dur + 0.35, amp=amp, detune=0 if asc else -0.5, descend=not asc))
            if i < 2:
                chunks.append(np.zeros(int(0.05 * SR), np.float32))
        v = np.concatenate(chunks)
        if asc:
            t = np.arange(int(0.28 * SR)) / SR
            tone = 0.2 * np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 8) * np.minimum(t / 0.008, 1)
            # over last note
            pos = int((2 * (note_dur + 0.35 + 0.05) + 0.12) * SR)
            if pos + len(tone) > len(v):
                v = np.pad(v, (0, pos + len(tone) - len(v)))
            v[pos:pos + len(tone)] += tone.astype(np.float32)
        return v

    v1 = short_vin(True)
    place(sfx, v1, 8.00, 1.0)
    place(sfx, click(0.14, "projector"), 8.00, 0.9)
    # detuned descending after arrumem a mesa (~62.3)
    v2 = short_vin(False, note_dur=0.5, amp=0.32)
    place(sfx, v2, 62.35, 1.0)

    # clacs p6 at 2.0 and 3.6 → 35.0, 36.6
    place(sfx, click(0.16, "clac"), 35.00, 1.1)
    place(sfx, click(0.16, "clac"), 36.60, 1.1)
    # creak after "cadeira" ~32.2
    place(sfx, creak(0.75), 32.20, 0.7)
    # dial whistle when osvaldo cuts ~54.4
    place(sfx, dial_whistle(1.5), 54.35, 1.0)
    # rising hiss 54.4-56
    rise = am_bed(2.2, hiss=0.12, hum=0.03) * np.linspace(0.3, 1.0, int(2.2 * SR))
    place(sfx, rise, 54.35, 1.0)
    # burn sizzle p9 54-58
    place(sfx, sizzle(4.0), 54.0, 0.8)

    bed_am = am_bed(DUR, hiss=0.04, hum=0.018)
    # hiss up during interference 54.5-64, then cut
    bed_am[int(54.5 * SR):cut_at] *= np.linspace(1.0, 2.2, cut_at - int(54.5 * SR))
    bed_am[cut_at:] = 0
    sfx[cut_at:] = 0

    sf.write(STEMS / "stem_sfx_vinheta.wav", np.clip(sfx, -0.99, 0.99), SR)
    sf.write(STEMS / "stem_am_chiado.wav", np.clip(bed_am, -0.99, 0.99), SR)

    # ambient from source clips
    durs = [8, 5, 5, 6, 9, 6, 5, 8, 6, 6, 2]
    starts = list(np.cumsum([0] + durs[:-1]))
    planos = [CLIPS / f"plano-{i:02d}.mp4" for i in range(1, 12)]
    amb = extract_amb(planos, durs, starts)
    amb[cut_at:] = 0
    sf.write(STEMS / "stem_ambiente.wav", np.clip(amb, -0.99, 0.99), SR)

    # mix: amb + am bed + sfx + voice (voice already filtered)
    # light ducking of amb+bed when voice present
    mix_bed = amb * 0.7 + bed_am * 1.0 + sfx * 0.9
    # envelope of voice
    hop = 512
    env = np.zeros_like(wet)
    wabs = np.abs(wet)
    # simple follow
    e = 0
    for i, v in enumerate(wabs):
        e = 0.92 * e + 0.08 * v if v < e else 0.3 * e + 0.7 * v
        env[i] = e
    duck = 1.0 - 0.45 * np.clip(env / 0.12, 0, 1)
    mixed = mix_bed * duck + wet * 1.15
    mixed = np.clip(mixed, -0.99, 0.99)
    # stereo slight
    st = np.stack([mixed, mixed], axis=1)
    sf.write(STEMS / "stem_mix_pre_loudnorm.wav", st, SR)

    # save updated timeline
    (WORK / "voice_timeline_guia.json").write_text(json.dumps({
        "osvaldo_voice": report["osvaldo_voice"],
        "interferencia_voice": "pf_dora",
        "duration_s": DUR,
        "falas": falas,
        "cut_silence_s": cut_at / SR,
    }, indent=2, ensure_ascii=False))
    print("AUDIO_OK", "cut", cut_at / SR)


if __name__ == "__main__":
    main()
