#!/usr/bin/env python3
"""Efeitos por plano (p1 janela, p2/p9 cartela+tracking, p5 giro, p7 AM 870, p9 queima, p10 grão)."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
CINE = Path("/workspace/cinestudio")
BIBLE = CINE / "bible/avisos-a-populacao"
EP = CINE / "06-videos/avisos-ep01"
FONT_OSD = EP / "fonts/Oswald-Medium.ttf"
CARTELA = BIBLE / "cartela-aviso-01.png"
CARTELA_BASE = BIBLE / "cartela-aviso-01-base.png"


def upscale_trim(src: Path, dst: Path, duration: float) -> Path:
    import subprocess
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(src), "-t", f"{duration:.4f}",
        "-vf", f"scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k",
        "-movflags", "+faststart", str(dst),
    ], check=True)
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


def write_frames(path: Path, frames, fps=FPS, audio_from: Path | None = None, duration: float | None = None):
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
    import subprocess
    cmd = ["ffmpeg", "-y", "-i", str(tmp)]
    if audio_from is not None:
        cmd += ["-i", str(audio_from)]
        if duration is not None:
            cmd += ["-t", f"{duration:.4f}"]
        cmd += ["-map", "0:v", "-map", "1:a?", "-shortest"]
    elif duration is not None:
        cmd += ["-t", f"{duration:.4f}"]
    cmd += [
        "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k",
        "-movflags", "+faststart", str(path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp.unlink(missing_ok=True)
    return path


def soft_mask_from_bool(mask: np.ndarray, blur: int = 31) -> np.ndarray:
    m = (mask.astype(np.float32) * 255).astype(np.uint8)
    k = blur | 1
    m = cv2.GaussianBlur(m, (k, k), 0)
    return m.astype(np.float32) / 255.0


# ---------- p1: darken window ----------
def process_p1(src: Path, dst: Path, duration: float) -> Path:
    frames_out = []
    for i, fr, t in iter_frames(src):
        img = fr.astype(np.float32)
        h, w = fr.shape[:2]
        gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        # window is upper-middle bright frosted glass
        # spatial prior: central band, y ~ 0.08-0.48 of frame at start, grows with push-in
        # use brightness + position
        yy, xx = np.ogrid[:h, :w]
        # window roughly centered, above mid
        # adaptive: brightest connected region in upper 55%
        upper = np.zeros_like(gray)
        upper[: int(h * 0.52)] = gray[: int(h * 0.52)]
        # exclude very top wall (darker)
        thr = max(170, int(np.percentile(upper[upper > 0], 78)))
        cand = (upper > thr) & (xx > w * 0.18) & (xx < w * 0.82) & (yy > h * 0.06) & (yy < h * 0.52)
        # also include slightly less bright pane interiors
        cand2 = (upper > thr - 35) & (xx > w * 0.22) & (xx < w * 0.78) & (yy > h * 0.10) & (yy < h * 0.48)
        mask = cand | cand2
        # remove steam-ish? keep glass; steam is mid-gray wispy — don't include mid values
        m = soft_mask_from_bool(mask, 51)
        # darken strongly toward night, slight cool then amber street-lamp residual
        night = img.copy()
        # lower luminance, keep a faint warm glow
        night *= np.array([0.42, 0.38, 0.32], dtype=np.float32)  # BGR: keep a bit of amber (B low)
        night += np.array([6, 10, 14], dtype=np.float32)  # residual lamp
        # don't crush the silhouette (it's darker already); mask is the glass
        # slightly preserve highlights near the head rim by reducing mask where very edge contrast
        m3 = m[:, :, None]
        out = img * (1 - m3 * 0.88) + night * (m3 * 0.88)
        frames_out.append(np.clip(out, 0, 255).astype(np.uint8))
    return write_frames(dst, frames_out, audio_from=src, duration=duration)


# ---------- cartela ink layer ----------
def cartela_ink_rgba() -> np.ndarray:
    """Texto/brasão/carimbo da cartela com alpha, papel transparente."""
    full = np.array(Image.open(CARTELA).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS))
    base = np.array(Image.open(CARTELA_BASE).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS))
    # difference in RGB
    diff = np.abs(full[:, :, :3].astype(np.int16) - base[:, :, :3].astype(np.int16)).max(axis=2)
    alpha = np.clip((diff.astype(np.float32) - 8) * 3.2, 0, 255).astype(np.uint8)
    # slight dilate to keep serifs
    alpha = cv2.dilate(alpha, np.ones((2, 2), np.uint8), 1)
    out = full.copy()
    out[:, :, 3] = alpha
    return out


def ecc_warp(prev_g, g, prev_warp=None):
    warp = np.eye(2, 3, dtype=np.float32) if prev_warp is None else prev_warp.copy()
    try:
        # work smaller for speed
        sc = 0.5
        a = cv2.resize(prev_g, (0, 0), fx=sc, fy=sc)
        b = cv2.resize(g, (0, 0), fx=sc, fy=sc)
        w = warp.copy()
        w[:, 2] *= sc
        cv2.findTransformECC(
            a, b, w, cv2.MOTION_EUCLIDEAN,
            (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-4),
        )
        w[:, 2] /= sc
        return w
    except cv2.error:
        return np.eye(2, 3, dtype=np.float32) if prev_warp is None else prev_warp


def track_and_overlay_cartela(src: Path, dst: Path, duration: float, until: float | None = None, fade_out: float = 0.0):
    ink = cartela_ink_rgba()  # BGRA later
    ink_bgr = cv2.cvtColor(ink, cv2.COLOR_RGBA2BGRA)
    frames_out = []
    prev_g = None
    acc = np.eye(2, 3, dtype=np.float32)
    first_g = None
    for i, fr, t in iter_frames(src):
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        if first_g is None:
            first_g = g
            # align cartela paper to first frame? ink already matches official cartela;
            # first frame may be entering from below — track vs first stable later.
            acc = np.eye(2, 3, dtype=np.float32)
        else:
            # warp from previous
            step = ecc_warp(prev_g, g, np.eye(2, 3, dtype=np.float32))
            # accumulate: step ∘ acc
            acc_h = np.vstack([acc, [0, 0, 1]])
            step_h = np.vstack([step, [0, 0, 1]])
            acc = (step_h @ acc_h)[:2]
        prev_g = g
        # opacity schedule
        op = 1.0
        if until is not None:
            if t >= until + fade_out:
                op = 0.0
            elif t >= until:
                op = 1.0 - (t - until) / max(0.01, fade_out)
        if op <= 0.01:
            frames_out.append(fr)
            continue
        warped = cv2.warpAffine(ink_bgr, acc, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        a = (warped[:, :, 3].astype(np.float32) / 255.0) * op
        # match slight blur of the slide (estimate from Laplacian variance)
        var = cv2.Laplacian(g, cv2.CV_64F).var()
        if var < 40:
            k = 7 if var < 20 else 3
            blurred = cv2.GaussianBlur(warped, (k, k), 0)
            warped = blurred
            a = (warped[:, :, 3].astype(np.float32) / 255.0) * op
        a3 = a[:, :, None]
        rgb = warped[:, :, :3].astype(np.float32)
        base = fr.astype(np.float32)
        out = base * (1 - a3) + rgb * a3
        frames_out.append(np.clip(out, 0, 255).astype(np.uint8))
    return write_frames(dst, frames_out, audio_from=src, duration=duration), acc


# ---------- p5: tighter crop + 2cm turn ----------
def process_p5(src: Path, dst: Path, duration: float) -> Path:
    frames_out = []
    # tighter crop: 86% at start, slowly to 82%, centered a bit low (chair)
    for i, fr, t in iter_frames(src):
        h, w = fr.shape[:2]
        # crop fraction
        frac = 0.86 - 0.03 * min(1.0, t / duration)
        # pivot slightly below center (chair seat)
        cx, cy = 0.52 * w, 0.58 * h
        cw, ch = w * frac, h * frac
        x0 = int(np.clip(cx - cw / 2, 0, w - cw))
        y0 = int(np.clip(cy - ch / 2, 0, h - ch))
        crop = fr[y0:y0 + int(ch), x0:x0 + int(cw)]
        # 2 cm giro from mid (~4.5s): ~1.6 degrees around chair feet
        # ease in 4.4–5.6s then hold
        if t < 4.4:
            ang = 0.0
        elif t < 5.8:
            u = (t - 4.4) / 1.4
            u = u * u * (3 - 2 * u)
            ang = 1.7 * u
        else:
            ang = 1.7
        # rotate around a point near the chair's floor contact (lower mid of crop)
        chh, cww = crop.shape[:2]
        pivot = (cww * 0.52, chh * 0.78)
        M = cv2.getRotationMatrix2D(pivot, ang, 1.0)
        # also a tiny horizontal skew suggesting yaw toward the wall (to the right / into wall)
        if ang:
            shift = 6 * (ang / 1.7)  # pixels ~ "2 cm"
            M[0, 2] += shift
        rot = cv2.warpAffine(crop, M, (cww, chh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = cv2.resize(rot, (W, H), interpolation=cv2.INTER_LANCZOS4)
        frames_out.append(out)
    return write_frames(dst, frames_out, audio_from=src, duration=duration)


# ---------- p7: AM 870 on dial ----------
def find_dial_bbox(fr: np.ndarray):
    """Amber illuminated dial window."""
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    # amber/yellow-orange
    m1 = cv2.inRange(hsv, (8, 60, 90), (35, 255, 255))
    # also bright yellowish
    m = m1
    m = cv2.medianBlur(m, 7)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 13), np.uint8))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    # pick largest in mid-right of radio (center of frame-ish)
    h, w = fr.shape[:2]
    best, ba = None, 0
    for c in cnts:
        x, y, ww, hh = cv2.boundingRect(c)
        a = ww * hh
        cx, cy = x + ww / 2, y + hh / 2
        if a < 800:
            continue
        # dial should be reasonably wide
        if ww < hh * 0.8:
            continue
        if a > ba:
            ba, best = a, (x, y, ww, hh)
    return best


_am_font = None


def draw_am870(fr: np.ndarray, bbox):
    global _am_font
    if bbox is None:
        return fr
    x, y, ww, hh = bbox
    # text sits in the upper third of the dial, dark brown like ticks
    img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fs = max(14, int(hh * 0.22))
    if _am_font is None or getattr(_am_font, "size", None) != fs:
        _am_font = ImageFont.truetype(str(FONT_OSD), fs)
    text = "AM  870"
    # center roughly, a bit left of needle (needle is slightly right of center)
    bbox_t = draw.textbbox((0, 0), text, font=_am_font)
    tw, th = bbox_t[2] - bbox_t[0], bbox_t[3] - bbox_t[1]
    tx = int(x + ww * 0.50 - tw / 2)
    ty = int(y + hh * 0.10)
    # slight perspective: the dial is receding to the right; squeeze? keep simple
    # shadow then ink
    col_sh = (40, 22, 8)
    col = (42, 28, 14)
    # print with slight letterpress
    draw.text((tx + 1, ty + 1), text, font=_am_font, fill=(20, 12, 6))
    draw.text((tx, ty), text, font=_am_font, fill=col)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def process_p7(src: Path, dst: Path, duration: float) -> Path:
    frames_out = []
    last = None
    for i, fr, t in iter_frames(src):
        box = find_dial_bbox(fr)
        if box is None:
            box = last
        else:
            if last is not None:
                # smooth
                a = 0.35
                box = tuple(int(a * box[j] + (1 - a) * last[j]) for j in range(4))
            last = box
        frames_out.append(draw_am870(fr, box))
    return write_frames(dst, frames_out, audio_from=src, duration=duration)


# ---------- p9: cartela until ~2s + generated film burn ----------
def film_burn_mask(h, w, t, start=2.0, t_full=5.6, cx=None, cy=None):
    """Irregular expanding burn hole, 0=paper, 1=burned through (white)."""
    if t < start:
        return np.zeros((h, w), np.float32), np.zeros((h, w), np.float32)
    u = np.clip((t - start) / (t_full - start), 0, 1)
    # ease
    u2 = u ** 0.72
    if cx is None:
        cx, cy = w * 0.50, h * 0.46
    # radius in pixels
    r = (20 + u2 * 0.72 * max(h, w)) 
    yy, xx = np.mgrid[0:h, 0:w]
    # irregular radius with several sine terms + frozen noise
    ang = np.arctan2(yy - cy, xx - cx)
    jitter = (
        0.10 * np.sin(5 * ang + 0.4)
        + 0.07 * np.sin(9 * ang - 1.1)
        + 0.04 * np.sin(17 * ang + 2.0)
    )
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    rr = r * (1.0 + jitter)
    # hole (through)
    hole = np.clip((rr - dist) / (8 + 40 * u2), 0, 1)
    # char ring outside hole
    ring = np.clip(1.0 - np.abs(dist - rr) / (18 + 50 * u2), 0, 1)
    ring = ring ** 1.4
    return hole.astype(np.float32), ring.astype(np.float32)


def process_p9(src: Path, dst: Path, duration: float) -> Path:
    ink = cartela_ink_rgba()
    ink_bgr = cv2.cvtColor(ink, cv2.COLOR_RGBA2BGRA)
    frames_out = []
    prev_g = None
    acc = np.eye(2, 3, dtype=np.float32)
    for i, fr, t in iter_frames(src):
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        if prev_g is not None:
            step = ecc_warp(prev_g, g, np.eye(2, 3, dtype=np.float32))
            acc_h = np.vstack([acc, [0, 0, 1]])
            step_h = np.vstack([step, [0, 0, 1]])
            acc = (step_h @ acc_h)[:2]
        prev_g = g
        # cartela ink: full until 2.0s, then stays on remaining paper (masked by hole)
        warped = cv2.warpAffine(ink_bgr, acc, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        a = warped[:, :, 3].astype(np.float32) / 255.0
        base = fr.astype(np.float32)
        rgb = warped[:, :, :3].astype(np.float32)
        composed = base * (1 - a[:, :, None]) + rgb * a[:, :, None]
        hole, ring = film_burn_mask(H, W, t, start=2.0, t_full=5.7)
        # ember colors
        ember = np.zeros_like(composed)
        ember[:, :, 0] = 40 + 180 * ring  # B
        ember[:, :, 1] = 40 + 200 * ring
        ember[:, :, 2] = 20 + 255 * ring  # R yellow-orange
        # char brown
        char = composed * np.array([0.15, 0.18, 0.22], np.float32)
        # white projector light through hole
        white = np.array([250, 252, 255], np.float32)
        # source already may have a burn — mix in highlights of source if brighter
        src_lum = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        # final
        out = composed
        out = out * (1 - ring[:, :, None] * 0.85) + (0.35 * char + 0.65 * ember) * ring[:, :, None]
        out = out * (1 - hole[:, :, None]) + white * hole[:, :, None]
        # if original already blew out, keep some of that after t=2
        if t >= 2.0:
            blow = np.clip((src_lum - 0.85) / 0.15, 0, 1)[:, :, None]
            out = out * (1 - blow * 0.6) + fr.astype(np.float32) * (blow * 0.6)
        frames_out.append(np.clip(out, 0, 255).astype(np.uint8))
    return write_frames(dst, frames_out, audio_from=src, duration=duration)


# ---------- p10: grain on standing figure / window ----------
def process_p10(src: Path, dst: Path, duration: float) -> Path:
    rng = np.random.default_rng(41)
    frames_out = []
    for i, fr, t in iter_frames(src):
        h, w = fr.shape[:2]
        hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        # warm window glow
        win = cv2.inRange(hsv, (8, 40, 50), (40, 255, 255))
        # also include darker silhouettes inside a window bounding box
        cnts, _ = cv2.findContours(win, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros((h, w), np.uint8)
        if cnts:
            x, y, ww, hh = cv2.boundingRect(max(cnts, key=cv2.contourArea))
            pad = 8
            x0, y0 = max(0, x - pad), max(0, y - pad)
            x1, y1 = min(w, x + ww + pad), min(h, y + hh + pad)
            mask[y0:y1, x0:x1] = 255
            # standing figure is the taller central dark blob inside the window
            roi = fr[y0:y1, x0:x1]
            g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # darker than glow
            fig = (g < 80).astype(np.uint8) * 255
            # keep components in the upper-middle (standing)
            fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((9, 5), np.uint8))
            fig_full = np.zeros((h, w), np.uint8)
            fig_full[y0:y1, x0:x1] = fig
            # window glass + extra on figure
            wm = soft_mask_from_bool(mask > 0, 21)
            fm = soft_mask_from_bool(fig_full > 0, 15)
        else:
            wm = np.zeros((h, w), np.float32)
            fm = np.zeros((h, w), np.float32)
        grain = rng.normal(0, 1, (h, w)).astype(np.float32)
        grain = cv2.GaussianBlur(grain, (0, 0), 0.6)
        # stronger grain on figure, moderate on rest of window
        amt = 7.5 * wm + 14.0 * fm
        out = fr.astype(np.float32)
        out += grain[:, :, None] * amt[:, :, None]
        frames_out.append(np.clip(out, 0, 255).astype(np.uint8))
    return write_frames(dst, frames_out, audio_from=src, duration=duration)


# ---------- p4 / p10 frame skip helper applied in ffmpeg later ----------

def process_identity(src: Path, dst: Path, duration: float) -> Path:
    # just copy/trim already done; symlink-like encode to dest
    if src.resolve() == dst.resolve():
        return dst
    import shutil
    shutil.copy2(src, dst)
    return dst


if __name__ == "__main__":
    print("fx_planos loaded")
