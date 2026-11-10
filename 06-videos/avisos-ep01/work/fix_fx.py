#!/usr/bin/env python3
"""Refaz p2 (cartela com tremor), p7 (tipografia), p9 (cartela íntegra até 2s + queima), p10 (grão mais leve)."""
from __future__ import annotations
import math, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, "/workspace/cinestudio/06-videos/avisos-ep01/work")
from fx_planos import (
    W, H, FPS, CARTELA, write_frames, iter_frames, process_p7,
    film_burn_mask, find_dial_bbox, FONT_OSD, soft_mask_from_bool,
)

EP = Path("/workspace/cinestudio/06-videos/avisos-ep01")
PREP = EP / "work/prep"
FX = EP / "work/fx"


def cartela_rgb():
    im = Image.open(CARTELA).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def projector_slide(duration, slam=True):
    """Gera o slide da cartela oficial com entrada de projetor + tremor."""
    base = cartela_rgb()
    frames = []
    n = int(round(duration * FPS))
    for i in range(n):
        t = i / FPS
        fr = base.copy()
        dy, dx, blur, rot = 0.0, 0.0, 0.0, 0.0
        if slam and t < 0.70:
            # entra de baixo e foca
            u = min(1.0, t / 0.55)
            u_e = 1 - (1 - u) ** 3
            dy = (1 - u_e) * 220
            dx = (1 - u_e) * 18
            blur = (1 - u_e) * 9
            rot = (1 - u_e) * -1.2
        # tremor contínuo do projetor (mesmo depois)
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


def redo_p2():
    frames = projector_slide(5.0, slam=True)
    return write_frames(FX / "plano-02.mp4", frames, audio_from=PREP / "plano-02.mp4", duration=5.0)


def redo_p9():
    # cartela íntegra (cobre a queima precoce da fonte) até 2s, depois queima gerada
    base_frames = projector_slide(6.0, slam=False)
    out_frames = []
    for i, fr in enumerate(base_frames):
        t = i / FPS
        hole, ring = film_burn_mask(H, W, t, start=2.0, t_full=5.65)
        composed = fr.astype(np.float32)
        ember = np.zeros_like(composed)
        ember[:, :, 0] = 30 + 160 * ring
        ember[:, :, 1] = 50 + 210 * ring
        ember[:, :, 2] = 20 + 255 * ring
        char = composed * np.array([0.12, 0.16, 0.20], np.float32)
        white = np.array([252, 253, 255], np.float32)
        out = composed
        out = out * (1 - ring[:, :, None] * 0.9) + (0.3 * char + 0.7 * ember) * ring[:, :, None]
        out = out * (1 - hole[:, :, None]) + white * hole[:, :, None]
        out_frames.append(np.clip(out, 0, 255).astype(np.uint8))
    return write_frames(FX / "plano-09.mp4", out_frames, audio_from=PREP / "plano-09.mp4", duration=6.0)


def redo_p7():
    """AM 870 mais fino, cor de tinta do mostrador, acompanha o dial."""
    font_cache = {}
    last = None
    frames = []
    src = PREP / "plano-07.mp4"
    for i, fr, t in iter_frames(src):
        box = find_dial_bbox(fr)
        if box is None:
            box = last
        else:
            if last is not None:
                a = 0.4
                box = tuple(int(a * box[j] + (1 - a) * last[j]) for j in range(4))
            last = box
        if box is None:
            frames.append(fr)
            continue
        x, y, ww, hh = box
        img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        fs = max(12, int(hh * 0.16))
        if fs not in font_cache:
            font_cache[fs] = ImageFont.truetype(str(FONT_OSD), fs)
        font = font_cache[fs]
        text = "AM  870"
        bb = draw.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = int(x + ww * 0.50 - tw / 2)
        ty = int(y + hh * 0.11)
        # letterpress brown, not sticker-black
        draw.text((tx + 1, ty + 1), text, font=font, fill=(28, 16, 8, 90))
        draw.text((tx, ty), text, font=font, fill=(58, 36, 18))
        frames.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
    return write_frames(FX / "plano-07.mp4", frames, audio_from=src, duration=5.0)


def redo_p10():
    rng = np.random.default_rng(41)
    src = PREP / "plano-10.mp4"
    frames = []
    for i, fr, t in iter_frames(src):
        h, w = fr.shape[:2]
        hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        win = cv2.inRange(hsv, (8, 40, 50), (40, 255, 255))
        cnts, _ = cv2.findContours(win, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        wm = np.zeros((h, w), np.float32)
        fm = np.zeros((h, w), np.float32)
        if cnts:
            x, y, ww, hh = cv2.boundingRect(max(cnts, key=cv2.contourArea))
            pad = 6
            x0, y0 = max(0, x - pad), max(0, y - pad)
            x1, y1 = min(w, x + ww + pad), min(h, y + hh + pad)
            mask = np.zeros((h, w), np.uint8)
            mask[y0:y1, x0:x1] = 255
            roi = cv2.cvtColor(fr[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
            fig = (roi < 85).astype(np.uint8) * 255
            fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((5, 3), np.uint8))
            # prefer taller central blob (standing figure)
            fig_full = np.zeros((h, w), np.uint8)
            fig_full[y0:y1, x0:x1] = fig
            # keep upper half of window more (standing head/torso)
            fig_full[: y0 + int(0.28 * (y1 - y0))] = 0
            wm = soft_mask_from_bool(mask > 0, 25) * 0.35
            fm = soft_mask_from_bool(fig_full > 0, 17)
        grain = rng.normal(0, 1, (h, w)).astype(np.float32)
        grain = cv2.GaussianBlur(grain, (0, 0), 0.7)
        amt = 4.0 * wm + 8.5 * fm  # milder than before
        out = fr.astype(np.float32) + grain[:, :, None] * amt[:, :, None]
        frames.append(np.clip(out, 0, 255).astype(np.uint8))
    return write_frames(FX / "plano-10.mp4", frames, audio_from=src, duration=6.0)


if __name__ == "__main__":
    print("redo p2", flush=True); redo_p2()
    print("redo p7", flush=True); redo_p7()
    print("redo p9", flush=True); redo_p9()
    print("redo p10", flush=True); redo_p10()
    print("FX_FIX_OK")
