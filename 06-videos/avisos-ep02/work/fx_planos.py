#!/usr/bin/env python3
"""Ajustes por plano do Aviso nº 2, antes do look filme.
p2 cartela com tremor de projetor; p3 clarear como dia;
p4 legenda 'Rua das Paineiras, 41'; p6 dessaturação leve;
p8 corte antes das mãos + hold até 7s; p9 AM 870 no mostrador.
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
CLIPS = CINE / "05-cenas/avisos-ep02"
EP = CINE / "06-videos/avisos-ep02"
PREP = EP / "work/prep"
FX = EP / "work/fx"
FONT_OSD = EP / "fonts/Oswald-Medium.ttf"
FONT_SERIF = EP / "fonts/PTSerif-Regular.ttf"
CARTELA = BIBLE / "cartela-aviso-02.png"

# durações de roteiro (apare os +0,04s)
DURS = {
    1: 9.0, 2: 7.0, 3: 7.0, 4: 7.0, 5: 7.0,
    6: 6.0, 7: 9.0, 8: 7.0, 9: 3.0, 10: 5.0, 11: 1.0,
}
# inspeção: mãos entram ~3.0s (nuca/ombro ok até ~2.8s)
P8_CUT = 2.80

DAY_VF = (
    "eq=brightness=0.16:contrast=0.78:gamma=1.22:saturation=0.85,"
    "curves=all='0/0.12 0.5/0.58 1/1'"
)


def run(cmd, check=True):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=check)


def upscale_trim(src: Path, dst: Path, duration: float, extra_vf: str | None = None) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
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


def process_p8():
    """Corta antes das mãos e segura o último quadro limpo até 7s."""
    src = CLIPS / "plano-08.mp4"
    dst = FX / "plano-08.mp4"
    live = P8_CUT
    hold = DURS[8] - live
    # tpad clone no fps 30 já escalado
    vf = (
        f"scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p,"
        f"tpad=stop_mode=clone:stop_duration={hold:.4f}"
    )
    run([
        "ffmpeg", "-y", "-i", str(src), "-ss", "0", "-t", f"{live:.4f}",
        "-vf", vf, "-t", f"{DURS[8]:.4f}",
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an", "-movflags", "+faststart", str(dst),
    ])
    return dst


def process_p4(src: Path, dst: Path, duration: float):
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


def process_p9(src: Path, dst: Path, duration: float):
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
    print(f"p9 AM870 hits={hits}/{len(frames)} last={last}", flush=True)
    return write_frames(dst, frames, duration=duration)


def main():
    PREP.mkdir(parents=True, exist_ok=True)
    FX.mkdir(parents=True, exist_ok=True)

    # 1. prep/trim de todos, com ajustes de cor em p3 e p6
    for i, dur in DURS.items():
        src = CLIPS / f"plano-{i:02d}.mp4"
        dst = PREP / f"plano-{i:02d}.mp4"
        if i == 8:
            continue  # tratado à parte
        if i == 2:
            continue  # cartela gerada
        extra = None
        if i == 3:
            extra = DAY_VF
        elif i == 6:
            extra = "eq=saturation=0.72:contrast=1.02"
        print(f"=== prep p{i} ===", flush=True)
        upscale_trim(src, dst, dur, extra_vf=extra)

    print("=== p2 cartela ===", flush=True)
    frames = projector_slide(DURS[2], slam=True)
    write_frames(FX / "plano-02.mp4", frames, duration=DURS[2])

    print("=== p8 corte+hold ===", flush=True)
    process_p8()

    print("=== p4 endereço ===", flush=True)
    process_p4(PREP / "plano-04.mp4", FX / "plano-04.mp4", DURS[4])

    print("=== p9 AM 870 ===", flush=True)
    process_p9(PREP / "plano-09.mp4", FX / "plano-09.mp4", DURS[9])

    # copiar os demais prep -> fx
    for i, dur in DURS.items():
        fx = FX / f"plano-{i:02d}.mp4"
        if fx.exists():
            continue
        src = PREP / f"plano-{i:02d}.mp4"
        if src.exists():
            # hardlink or copy
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
