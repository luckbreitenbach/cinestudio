#!/usr/bin/env python3
"""SFX locais + stems de voz (seca e filtrada) + mix do Aviso nº 3."""
from __future__ import annotations
import json, math, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf

SR = 48000
DUR = 68.0
EP = Path("/workspace/cinestudio/06-videos/avisos-ep03")
WORK = EP / "work"
STEMS = EP / "stems"
VOZDIR = STEMS / "voz_guia"
AUDIO = EP / "audio"
CLIPS = Path("/workspace/cinestudio/05-cenas/avisos-ep03")
SHARED = Path("/workspace/cinestudio/06-videos/avisos-shared")
RAW = WORK / "voz_raw"
DURS = [11.0, 8.0, 6.0, 6.0, 6.0, 6.0, 5.0, 7.0, 6.0, 6.0, 1.0]
STARTS = np.cumsum([0.0] + DURS[:-1]).tolist()
CUT_SILENCE = 67.00  # corte seco da sirene / silêncio no p11


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


def dial_whistle(dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 7000 * (400 / 7000) ** (t / dur)
    ph = np.cumsum(2 * np.pi * f / SR)
    return (0.28 * np.sin(ph) * fade(n, 0.05, 0.2)).astype(np.float32)


def clock_bell(dur=2.8, f0=392.0):
    """Sino curto de relógio de praça (parcials inarmônicos)."""
    t = np.arange(int(dur * SR)) / SR
    parts = [(1.0, 1.0), (0.55, 2.0), (0.35, 2.76), (0.22, 4.07), (0.14, 5.4), (0.09, 6.75)]
    y = np.zeros_like(t)
    for a, p in parts:
        y += a * np.sin(2 * np.pi * f0 * p * t) * np.exp(-t * (1.6 + 0.35 * p))
    att = np.minimum(t / 0.008, 1.0)
    rng = np.random.default_rng(1987)
    nse = 0.12 * rng.normal(0, 1, len(t)).astype(np.float64) * np.exp(-t * 35)
    return (0.42 * (y + nse) * att).astype(np.float32)


def am_bed(dur=DUR, hiss=0.045, hum=0.02):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    noise = rng.normal(0, 1, n).astype(np.float32)
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
    w0 = 2 * math.pi * cutoff / sr
    alpha = math.sin(w0) / (2 * q)
    cosw = math.cos(w0)
    b0 = (1 - cosw) / 2
    b1 = 1 - cosw
    b2 = (1 - cosw) / 2
    a0 = 1 + alpha
    a1 = -2 * cosw
    a2 = 1 + alpha
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
    a2 = 1 + alpha
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


def offmic(x):
    """Osvaldo afastado do microfone: mais baixo, abafado, com sala, sem pânico."""
    y = biquad_lp(x.astype(np.float64), 2000)
    y = biquad_hp(y, 180)
    acc = y.copy()
    for dly, g in ((0.016, 0.32), (0.037, 0.18), (0.062, 0.10)):
        d = int(dly * SR)
        c = np.zeros_like(acc)
        if d < len(acc):
            c[d:] = acc[:-d]
        acc = acc + g * c
    y = biquad_lp(acc, 2400)
    return (y * 0.52).astype(np.float32)


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
    """Ajusta in/out com folga, prefere raw natural quando cabe, reporta desvios."""
    by = {f["id"]: dict(f) for f in falas}
    notes = []

    def use_raw(lid, reason):
        raw_p = RAW / f"{lid}_raw.wav"
        if raw_p.exists():
            y = load48(raw_p)
            by[lid]["path"] = str(raw_p)
            by[lid]["final_s"] = len(y) / SR
            by[lid]["atempo"] = 1.0
            by[lid]["used_source"] = "raw"
            notes.append(reason)
        return by[lid]["final_s"]

    # 1a+1b são a mesma frase: vírgula curta, não o buraco até 0:04 da tabela de legendas
    by["osv_1b"]["in"] = by["osv_1a"]["in"] + by["osv_1a"]["final_s"] + 0.22
    by["osv_1c"]["in"] = by["osv_1b"]["in"] + by["osv_1b"]["final_s"] + 1.00
    notes.append(
        f"osv_1b em {by['osv_1b']['in']:.3f} (tabela 4,00) para manter a vírgula da frase única; "
        f"osv_1c em {by['osv_1c']['in']:.3f} (tabela 7,00) com pausa de 1,0s do roteiro."
    )

    # 2c: há folga até 19,00 — usar raw natural, 0,4s após 2b
    use_raw("osv_2c", "osv_2c: raw natural (sem atempo) — a folga até a cartela seguinte comporta.")
    by["osv_2c"]["in"] = by["osv_2b"]["in"] + by["osv_2b"]["final_s"] + 0.40

    # 6a: raw 2,50s cabe com pausa ~0,50s (roteiro 0,6s)
    dur6a = use_raw("osv_6a", "osv_6a: raw natural; pausa até 6b reduzida de 0,6s para ~0,50s.")
    by["osv_6a"]["in"] = 55.00

    # int_4 e int_5: raw cabe no intervalo
    use_raw("int_4", "int_4: raw natural (atempo 1,05 desnecessário); pausa até Correção ~0,42s (roteiro 0,6s).")
    use_raw("int_5", "int_5: raw natural (0,94s) cabe até 'Quem é Teresa?' às 65,00.")

    # int_3: raw 0,94s termina ~47,94, 60ms antes do corte do p8
    use_raw("int_3", "int_3: raw natural 0,94s; termina ~47,94 (folga de ~60ms antes do p8).")

    # int_1 não cabe natural no slot 44,00–45,00: usa fitted 1,079 e começa 80ms antes
    # para não invadir Joaquim Sales e ficar dentro de ~100ms da legenda.
    by["int_1"]["in"] = 45.00 - by["int_1"]["final_s"]
    notes.append(
        f"int_1 ('Lurdes Ventura.') fitted {by['int_1']['final_s']:.3f}s (speed 1,08 + atempo 1,10 no teto); "
        f"in deslocado para {by['int_1']['in']:.3f} (tabela 44,00, desvio {by['int_1']['in']-44.00:+.3f}s) "
        f"para terminar em 45,00 sem invadir a fala seguinte. Palavras intactas."
    )

    for f in by.values():
        f["out"] = f["in"] + f["final_s"]
    return list(by.values()), notes


def extract_amb():
    bed = np.zeros(int(DUR * SR), np.float32)
    for i, (d, st) in enumerate(zip(DURS, STARTS), start=1):
        wav = WORK / f"amb_p{i:02d}.wav"
        src = CLIPS / f"plano-{i:02d}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(src), "-t", f"{d:.4f}",
            "-ac", "1", "-ar", str(SR), "-vn", str(wav),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        y = load48(wav)
        if i == 2:
            y = y * 0.08
        elif i == 11:
            y = y * 0.0  # silêncio no corte
        else:
            y = y * 0.28
        place(bed, y, st, 1.0)
    # hard silence from 67.00
    bed[int(CUT_SILENCE * SR):] = 0
    return bed


def write_ass(timeline):
    """Legendas alinhadas às falas (desvio voz/legenda ≈ 0). Cartela sem o texto já impresso."""
    # texto com quebras iguais às do roteiro
    wraps = {
        "osv_1a": "Se a sirene tocar\\Ne você estiver na rua,",
        "osv_1c": "Elas não procuram\\Nquem já está no fundo.",
        "osv_3a": "A Prefeitura informa que a família Moraes\\Nsegue em casa.",
        "osv_4a": "A partir desta noite, a sirene da barragem\\Nmarcará o recolhimento.",
    }
    style = {
        "osvaldo": "Osvaldo",
        "interferencia": "Interferencia",
    }
    # ordenar por in
    tl = sorted(timeline, key=lambda r: r["in"])
    # 2a usa estilo Cartela; 2b e 2c não ganham legenda (texto já está na cartela)
    skip = {"osv_2b", "osv_2c"}
    events = []
    for i, rec in enumerate(tl):
        if rec["id"] in skip:
            continue
        start = rec["in"]
        # até a próxima fala visível ou um respiro
        if i + 1 < len(tl):
            nxt = tl[i + 1]["in"]
            # se a próxima é 2b/2c (suprimida), olhar a seguinte
            j = i + 1
            while j < len(tl) and tl[j]["id"] in skip:
                j += 1
            end = tl[j]["in"] if j < len(tl) else min(CUT_SILENCE, rec["out"] + 0.8)
        else:
            end = min(CUT_SILENCE, rec["out"] + 0.35)
        # não atravessar o corte do p11
        end = min(end, CUT_SILENCE)
        # garantir duração mínima da placa
        if end < start + 0.35:
            end = min(CUT_SILENCE, start + 0.6)
        st = "Cartela" if rec["id"] == "osv_2a" else style[rec["role"]]
        text = wraps.get(rec["id"], rec["text"])
        if rec["role"] == "interferencia":
            text = "{\\i1}" + text + "{\\i0}"
        def ts(t):
            h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
            return f"{h:d}:{m:02d}:{s:05.2f}"
        events.append(f"Dialogue: 0,{ts(start)},{ts(end)},{st},,0,0,0,,{text}")

    header = """[Script Info]
Title: Avisos à População — Aviso nº 3
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Osvaldo,PT Serif,40,&H00B0D9E8,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,0,2.4,2,80,80,310,1
Style: Interferencia,PT Serif,40,&H00B0D9E8,&H000000FF,&H00000000,&H80000000,0,1,0,0,100,100,0.4,0,1,0,2.4,2,80,80,310,1
Style: Cartela,PT Serif,38,&H00B0D9E8,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,0,2.4,1,90,540,430,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    (WORK / "legendas_avisos_ep03.ass").write_text(header + "\n".join(events) + "\n")
    print("ASS written", len(events), "events", flush=True)


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
        if f["id"] == "osv_7":
            gain = 1.0  # o filtro off-mic já baixa o nível
        place(dry, y * gain, f["in"], 1.0)
        if f["role"] == "interferencia":
            yw = am_filter(y, lo=450, hi=2200, muffle=True) * 0.92
        elif f["id"] == "osv_7":
            yw = offmic(y)
        elif f["id"] in ("osv_6a", "osv_6b"):
            yw = am_filter(y, lo=220, hi=4200, speaker=False)
        else:
            yw = am_filter(y, lo=300, hi=3400)
        yw = yw * gain
        place(wet, yw, f["in"], 1.0)
        # não deixar voz atravessar o silêncio do p11
        cut = int(CUT_SILENCE * SR)
        dry[cut:] = 0
        wet[cut:] = 0
        sf.write(VOZDIR / f"{f['id']}_dry.wav", y, SR)
        sf.write(VOZDIR / f"{f['id']}_filt.wav", yw, SR)
        rec = {
            "id": f["id"], "role": f["role"], "text": f["text"],
            "in": round(f["in"], 4), "out": round(f["in"] + len(y) / SR, 4),
            "dur": round(len(y) / SR, 4),
            "speed": f.get("speed"), "atempo": f.get("atempo", 1.0),
            "gain": gain, "note": f.get("note", ""),
            "source": f.get("used_source", "fitted"),
        }
        timeline.append(rec)
        print(f"place {rec['id']} {rec['in']:.3f}-{rec['out']:.3f} src={rec['source']} atempo={rec['atempo']:.3f}", flush=True)

    # SFX
    sfx = np.zeros(n, np.float32)
    v = vinheta()
    clk = click(0.14, "projector")
    dw = dial_whistle(1.20)
    bell = clock_bell(2.8, 392.0)
    # sirene: MESMO arquivo-assinatura da série
    sir_path = SHARED / "sirene-barragem.wav"
    sir = load48(sir_path)

    # vinheta + clique no começo da cartela (0:11)
    place(sfx, v, 11.00, 0.85)
    place(sfx, clk, 11.05, 0.9)
    # sino curto do relógio na entrada do p6 (0:37)
    bell_at = 37.15
    place(sfx, bell, bell_at, 0.55)
    # assobio de dial na interferência do meio
    place(sfx, dw, 43.00, 0.75)
    # sirene "de verdade", grave, ao longe, sobre o p10; corte seco em 67,00 (p11 silêncio)
    sir_at = 61.00
    sir_use = biquad_lp(sir.astype(np.float64), 1250) * 0.48
    fi = int(0.70 * SR)
    sir_use[:fi] *= np.linspace(0, 1, fi)
    cut = int(CUT_SILENCE * SR)
    start = int(sir_at * SR)
    take = max(0, cut - start)
    place(sfx, sir_use[:take].astype(np.float32), sir_at, 1.0)
    sfx[cut:] = 0

    sf.write(AUDIO / "vinheta-vibrafone.wav", v, SR)
    sf.write(AUDIO / "clique-projetor.wav", clk, SR)
    sf.write(AUDIO / "dial-whistle.wav", dw, SR)
    sf.write(AUDIO / "sino-relogio.wav", bell, SR)
    # não reescrever a assinatura; só copiar referência local
    shutil.copy2(sir_path, AUDIO / "sirene-barragem.wav")

    chi = am_bed(DUR, hiss=0.048, hum=0.018)
    t = np.arange(n) / SR
    # chiado sobe na interferência do meio (43–48) e volta ao normal
    bump_mid = np.clip((t - 43.00) / 0.45, 0, 1) * np.clip((48.00 - t) / 0.6, 0, 1)
    # chiado sobe de novo com a sirene (61–67) e some no corte
    bump_end = np.clip((t - 61.00) / 0.8, 0, 1) * np.clip((CUT_SILENCE - t) / 0.02, 0, 1)
    chi = chi * (1.0 + 1.5 * bump_mid + 1.7 * bump_end)
    chi[cut:] = 0

    amb = extract_amb()

    sf.write(STEMS / "stem_voz_dry.wav", stereo(np.clip(dry, -1, 1)), SR)
    sf.write(STEMS / "stem_voz_guia.wav", stereo(np.clip(wet, -1, 1)), SR)
    sf.write(STEMS / "stem_voz_guia_kokoro.wav", stereo(np.clip(wet, -1, 1)), SR)
    sf.write(STEMS / "stem_ambiente.wav", stereo(np.clip(amb, -1, 1)), SR)
    sf.write(STEMS / "stem_am_chiado.wav", stereo(np.clip(chi, -1, 1)), SR)
    sf.write(STEMS / "stem_sfx_vinheta.wav", stereo(np.clip(sfx, -1, 1)), SR)

    mix = amb * 0.7 + chi * 1.0 + sfx * 1.0
    voice_env = np.convolve(np.abs(wet), np.ones(int(0.05 * SR)) / (0.05 * SR), mode="same")
    duck = 1.0 / (1.0 + 3.2 * voice_env)
    mix = mix * duck * 0.8 + wet * 1.15
    mix[cut:] = 0  # silêncio absoluto no p11
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 0.85
    sf.write(STEMS / "stem_mix_guia_pre_loudnorm.wav", stereo(mix.astype(np.float32)), SR)

    write_ass(timeline)

    payload = {
        "duration": DUR,
        "pack_notes": pack_notes,
        "bell_at": bell_at,
        "sirene_at": sir_at,
        "sirene_cut": CUT_SILENCE,
        "dial_at": 43.00,
        "timeline": timeline,
    }
    (WORK / "voice_timeline_guia.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print("AUDIO DONE bell", bell_at, "sirene", sir_at, "->", CUT_SILENCE, flush=True)


if __name__ == "__main__":
    main()
