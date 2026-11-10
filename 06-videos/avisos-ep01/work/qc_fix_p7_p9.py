#!/usr/bin/env python3
"""Corrige tracking do AM 870 (p7) e a queima de película (p9). Não refaz os outros planos."""
from __future__ import annotations
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/workspace/cinestudio/06-videos/avisos-ep01/work")
from fx_planos import W, H, FPS, FONT_OSD, write_frames, iter_frames
from fix_fx import projector_slide, cartela_rgb

EP = Path("/workspace/cinestudio/06-videos/avisos-ep01")
PREP = EP / "work/prep"
FX = EP / "work/fx"


def find_dial_bbox(fr: np.ndarray):
    """Mostrador âmbar brilhante (ignora o reflexo quente da prateleira)."""
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


def redo_p7():
    font_cache = {}
    last = None
    frames = []
    src = PREP / "plano-07.mp4"
    debug = []
    for i, fr, t in iter_frames(src):
        box = find_dial_bbox(fr)
        if box is None:
            box = last
        else:
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
        if i % 15 == 0 or i < 3:
            debug.append((t, box, fs, (tx, ty)))
    for row in debug:
        print("p7", row, flush=True)
    return write_frames(FX / "plano-07.mp4", frames, audio_from=src, duration=5.0)


def burn_masks(h, w, t, start=2.0, t_full=5.65):
    z = np.zeros((h, w), np.float32)
    if t < start:
        return z, z, z
    u = float(np.clip((t - start) / (t_full - start), 0, 1))
    u2 = u ** 0.62
    cx = w * 0.50 + 22 * np.sin(t * 1.15 + 0.4)
    cy = h * 0.40 + 16 * np.cos(t * 0.85 + 0.2)
    r = 18 + u2 * 0.80 * max(h, w)
    yy, xx = np.mgrid[0:h, 0:w]
    ang = np.arctan2(yy - cy, xx - cx)
    jitter = (
        0.15 * np.sin(5 * ang + 0.4)
        + 0.09 * np.sin(11 * ang - 1.1)
        + 0.05 * np.sin(19 * ang + 2.0)
        + 0.03 * np.sin(29 * ang + 0.7)
    )
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    rr = r * (1.0 + jitter)
    edge = 14 + 64 * u2
    hole = np.clip((rr - dist) / edge, 0, 1) ** 0.65
    ember_w = 9 + 26 * u2
    ember = np.clip(1.0 - np.abs(dist - rr) / ember_w, 0, 1) ** 1.05
    char_w = 20 + 58 * u2
    char = np.clip(1.0 - np.abs(dist - (rr + ember_w * 0.7)) / char_w, 0, 1) ** 1.25
    return hole.astype(np.float32), ember.astype(np.float32), char.astype(np.float32)


def redo_p9():
    base_frames = projector_slide(6.0, slam=False)
    rng = np.random.default_rng(17)
    out_frames = []
    for i, fr in enumerate(base_frames):
        t = i / FPS
        hole, ember, char = burn_masks(H, W, t, start=2.0, t_full=5.65)
        composed = fr.astype(np.float32)
        if t < 2.0:
            out_frames.append(fr)
            continue
        flick = 0.86 + 0.14 * np.sin(t * 37.0) + 0.06 * np.sin(t * 11.0)
        char_col = np.array([18, 24, 32], np.float32)
        ember_col = np.array([18, 95 * flick, 255 * flick], np.float32)
        inner_col = np.array([40, 170 * flick, 255 * flick], np.float32)
        # buraco: luz estourada morna, não branco chapado
        grain = rng.normal(0, 7, (H, W, 1)).astype(np.float32)
        hole_col = np.array([228, 242, 255], np.float32) * (0.93 + 0.07 * flick) + grain
        out = composed
        out = out * (1 - char[:, :, None] * 0.88) + char_col * (char[:, :, None] * 0.88)
        # anel de brasa laranja + filete mais quente por dentro
        mix_e = ember[:, :, None]
        hot = ember_col * (0.55 + 0.45 * ember[:, :, None] ** 0.7)
        inner = inner_col * (ember[:, :, None] ** 2.2)
        out = out * (1 - mix_e * 0.95) + (0.7 * hot + 0.3 * inner) * 0.95
        out = out * (1 - hole[:, :, None]) + np.clip(hole_col, 0, 255) * hole[:, :, None]
        out_frames.append(np.clip(out, 0, 255).astype(np.uint8))
    return write_frames(FX / "plano-09.mp4", out_frames, audio_from=PREP / "plano-09.mp4", duration=6.0)


if __name__ == "__main__":
    print("redo p7", flush=True)
    redo_p7()
    print("redo p9", flush=True)
    redo_p9()
    # preview frames (pre-film)
    prev = EP / "work/qc_preview"
    prev.mkdir(exist_ok=True)
    for name, times in (
        ("plano-07", [0.05, 1.0, 2.5, 4.7]),
        ("plano-09", [0.5, 1.9, 2.15, 3.5, 5.4]),
    ):
        src = FX / f"{name}.mp4"
        for t in times:
            dst = prev / f"{name}_{t:.2f}.png"
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", "-update", "1", str(dst)],
                check=True,
                capture_output=True,
            )
            print("preview", dst)
    print("FX_QC_OK")
