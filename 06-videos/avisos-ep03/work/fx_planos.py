#!/usr/bin/env python3
"""Ajustes por plano do Aviso nº 3, antes do look filme.
p2 cartela com tremor de projetor; p3 endereço na fachada (dia já lê);
p5 crop/zoom 10% sem espelhar; p6 zoom 1,3x centrado no coreto (silhuetas);
p7 AM 870 no mostrador; p8 faixa de luz escurecida de leve no fim.
"""
from __future__ import annotations
import math, subprocess, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
CINE = Path("/workspace/cinestudio")
BIBLE = CINE / "bible/avisos-a-populacao"
CLIPS = CINE / "05-cenas/avisos-ep03"
EP = CINE / "06-videos/avisos-ep03"
PREP = EP / "work/prep"
FX = EP / "work/fx"
FONT_OSD = EP / "fonts/Oswald-Medium.ttf"
FONT_SERIF = EP / "fonts/PTSerif-Regular.ttf"
CARTELA = BIBLE / "cartela-aviso-03.png"

# durações de roteiro (apare os +0,04s)
DURS = {
    1: 11.0, 2: 8.0, 3: 6.0, 4: 6.0, 5: 6.0,
    6: 6.0, 7: 5.0, 8: 7.0, 9: 6.0, 10: 6.0, 11: 1.0,
}

# p3 já é de dia; lift leve só para não murchar no grade filme
DAY_VF = (
    "eq=brightness=0.06:contrast=0.92:gamma=1.08:saturation=0.92,"
    "curves=all='0/0.06 0.5/0.54 1/1'"
)

# p6: 1.3x no source 720x1280, x0=140 para manter o relógio e o coreto
# (silhuetas minúsculas; QC pede zoom 1,3x centrado no coreto — leve viés à esquerda)
P6_ZOOM_VF = "crop=554:985:140:218,scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p"

# p5: 10% zoom, sem espelhar; leve viés à direita para preservar a torre
P5_ZOOM_VF = "crop=655:1164:45:58,scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p"


def run(cmd, check=True):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=check)


def upscale_trim(src: Path, dst: Path, duration: float, extra_vf: str | None = None, replace_vf: str | None = None) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if replace_vf:
        vf = replace_vf
    else:
        vf = f"scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p"
        if extra_vf:
            vf = extra_vf + "," + vf
    run([
        "ffmpeg", "-y", "-i", str(src), "-t", f"{duration:.4f}",
        "-vf", vf,
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an", "-movflags", "+faststart", str(dst),
    ])
    return dst


def iter_frames(path: Path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or FPS
    i = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        yield i, fr, i / fps
        i += 1
    cap.release()


def write_frames(path: Path, frames, fps=FPS, duration: float | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".raw.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(str(tmp), fourcc, fps, (W, H))
    n = 0
    for fr in frames:
        if fr.shape[1] != W or fr.shape[0] != H:
            fr = cv2.resize(fr, (W, H), interpolation=cv2.INTER_LANCZOS4)
        vw.write(fr)
        n += 1
    vw.release()
    cmd = ["ffmpeg", "-y", "-i", str(tmp)]
    if duration is not None:
        cmd += ["-t", f"{duration:.4f}"]
    cmd += [
        "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an", "-movflags", "+faststart", str(path),
    ]
    run(cmd)
    tmp.unlink(missing_ok=True)
    return path


def cartela_rgb():
    im = Image.open(CARTELA).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def projector_slide(duration, slam=True):
    base = cartela_rgb()
    frames = []
    n = int(round(duration * FPS))
    for i in range(n):
        t = i / FPS
        fr = base.copy()
        dy, dx, blur, rot = 0.0, 0.0, 0.0, 0.0
        if slam and t < 0.70:
            u = min(1.0, t / 0.55)
            u_e = 1 - (1 - u) ** 3
            dy = (1 - u_e) * 220
            dx = (1 - u_e) * 18
            blur = (1 - u_e) * 9
            rot = (1 - u_e) * -1.2
        dx += 2.4 * math.sin(2 * math.pi * (t * 2.4 + 0.3)) + 1.1 * math.sin(2 * math.pi * t * 5.1)
        dy += 1.8 * math.sin(2 * math.pi * (t * 1.7 + 1.1)) + 0.8 * math.sin(2 * math.pi * t * 4.3)
        rot += 0.18 * math.sin(2 * math.pi * t * 1.9)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), rot, 1.0)
        M[0, 2] += dx
        M[1, 2] += dy
        out = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(8, 8, 6))
        if blur > 0.4:
            k = int(blur) * 2 + 1
            out = cv2.GaussianBlur(out, (k, k), blur * 0.6)
        frames.append(out)
    return frames


def find_dial_bbox(fr: np.ndarray):
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (8, 60, 90), (35, 255, 255))
    m = cv2.medianBlur(m, 7)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 13), np.uint8))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best, score = None, -1.0
    for c in cnts:
        x, y, ww, hh = cv2.boundingRect(c)
        if ww * hh < 800 or hh < 24:
            continue
        aspect = ww / max(hh, 1)
        if not (1.15 <= aspect <= 2.8):
            continue
        roi = hsv[y : y + hh, x : x + ww]
        if roi.size == 0:
            continue
        mean_v = float(roi[:, :, 2].mean())
        if mean_v < 130:
            continue
        sc = mean_v * (ww * hh) ** 0.5
        if sc > score:
            score, best = sc, (x, y, ww, hh)
    return best


def process_p3(src: Path, dst: Path, duration: float):
    font = ImageFont.truetype(str(FONT_SERIF), 34)
    text = "Rua das Paineiras, 41"
    frames = []
    for i, fr, t in iter_frames(src):
        img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        bb = draw.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = (W - tw) // 2
        ty = H - 430  # acima da zona de legenda (MarginV=310)
        draw.text((tx + 2, ty + 2), text, font=font, fill=(20, 16, 10))
        draw.text((tx, ty), text, font=font, fill=(232, 217, 176))
        frames.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
    return write_frames(dst, frames, duration=duration)


def process_p7(src: Path, dst: Path, duration: float):
    font_cache = {}
    last = None
    frames = []
    hits = 0
    for i, fr, t in iter_frames(src):
        box = find_dial_bbox(fr)
        if box is None:
            box = last
        else:
            hits += 1
            if last is not None:
                a = 0.45
                box = tuple(int(a * box[j] + (1 - a) * last[j]) for j in range(4))
            last = box
        if box is None:
            frames.append(fr)
            continue
        x, y, ww, hh = box
        img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        fs = max(11, int(hh * 0.125))
        if fs not in font_cache:
            font_cache[fs] = ImageFont.truetype(str(FONT_OSD), fs)
        font = font_cache[fs]
        text = "AM  870"
        bb = draw.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = int(x + ww * 0.50 - tw / 2)
        ty = int(y + hh * 0.11)
        mx = int(ww * 0.06)
        tx = int(np.clip(tx, x + mx, x + ww - tw - mx))
        ty = int(np.clip(ty, y + int(hh * 0.05), y + int(hh * 0.38) - th))
        draw.text((tx + 1, ty + 1), text, font=font, fill=(28, 16, 8))
        draw.text((tx, ty), text, font=font, fill=(58, 36, 18))
        frames.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
    print(f"p7 AM870 hits={hits}/{len(frames)} last={last}", flush=True)
    return write_frames(dst, frames, duration=duration)


def process_p8(src: Path, dst: Path, duration: float):
    """Escurece de leve a faixa de luz amarela no fim do plano (últimos ~2,5 s)."""
    # no 1080x1920, a faixa brilha por volta de y=1333-1360 (0.695 * 1920)
    ys = np.arange(H, dtype=np.float32)
    # máscara em pluma: faixa (y 1280-1420) + chão iluminado (até ~1650)
    sigma1, mu1 = 55.0, 1345.0
    sigma2, mu2 = 140.0, 1480.0
    w1 = np.exp(-0.5 * ((ys - mu1) / sigma1) ** 2)
    w2 = 0.55 * np.exp(-0.5 * ((ys - mu2) / sigma2) ** 2)
    row_w = np.clip(w1 + w2, 0, 1).astype(np.float32)[:, None, None]
    frames = []
    fade_start = duration - 2.5
    for i, fr, t in iter_frames(src):
        if t < fade_start:
            frames.append(fr)
            continue
        u = (t - fade_start) / 2.5  # 0..1
        # no máximo ~22% mais escuro na faixa (leve)
        amount = 0.22 * (u ** 1.15)
        f = fr.astype(np.float32)
        # também amortece um pouco o brilho específico (não os pretos das sombras)
        lum = 0.114 * f[:, :, 0] + 0.587 * f[:, :, 1] + 0.299 * f[:, :, 2]
        bright = np.clip((lum - 40.0) / 80.0, 0.0, 1.0)[:, :, None]
        mask = row_w * (0.35 + 0.65 * bright)
        f = f * (1.0 - amount * mask)
        frames.append(np.clip(f, 0, 255).astype(np.uint8))
    return write_frames(dst, frames, duration=duration)


def main():
    PREP.mkdir(parents=True, exist_ok=True)
    FX.mkdir(parents=True, exist_ok=True)

    for i, dur in DURS.items():
        src = CLIPS / f"plano-{i:02d}.mp4"
        dst = PREP / f"plano-{i:02d}.mp4"
        if i == 2:
            continue  # cartela gerada
        extra = None
        replace = None
        if i == 3:
            extra = DAY_VF
        elif i == 5:
            replace = P5_ZOOM_VF
        elif i == 6:
            replace = P6_ZOOM_VF
        print(f"=== prep p{i} ===", flush=True)
        upscale_trim(src, dst, dur, extra_vf=extra, replace_vf=replace)

    print("=== p2 cartela ===", flush=True)
    frames = projector_slide(DURS[2], slam=True)
    write_frames(FX / "plano-02.mp4", frames, duration=DURS[2])

    print("=== p3 endereço ===", flush=True)
    process_p3(PREP / "plano-03.mp4", FX / "plano-03.mp4", DURS[3])

    print("=== p7 AM 870 ===", flush=True)
    process_p7(PREP / "plano-07.mp4", FX / "plano-07.mp4", DURS[7])

    print("=== p8 faixa de luz ===", flush=True)
    process_p8(PREP / "plano-08.mp4", FX / "plano-08.mp4", DURS[8])

    for i, dur in DURS.items():
        fx = FX / f"plano-{i:02d}.mp4"
        if fx.exists():
            continue
        src = PREP / f"plano-{i:02d}.mp4"
        if src.exists():
            if fx.exists():
                fx.unlink()
            try:
                fx.hardlink_to(src)
            except Exception:
                subprocess.run(["cp", "-f", str(src), str(fx)], check=True)
    print("FX DONE", flush=True)
    for i in range(1, 12):
        p = FX / f"plano-{i:02d}.mp4"
        print(" ", p, "ok" if p.exists() else "MISSING", flush=True)


if __name__ == "__main__":
    main()
