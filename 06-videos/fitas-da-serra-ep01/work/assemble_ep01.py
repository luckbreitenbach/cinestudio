#!/usr/bin/env python3
"""Montagem completa Ep.01 Fitas da Serra — ~92s."""
from __future__ import annotations
import csv, json, math, os, random, shutil, subprocess, sys, tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path("/workspace/cinestudio")
CENAS = ROOT / "05-cenas/fitas-da-serra-ep01"
PIPE = ROOT / "06-videos/pipeline"
OUT = ROOT / "06-videos/fitas-da-serra-ep01"
WORK = OUT / "work"
AUDIO = ROOT / "bible/audio/sfx"
STEMS = OUT / "stems"
FRAMES = OUT / "frames"
EXPORTS = OUT / "exports"
FONTS = PIPE / "fonts"
sys.path.insert(0, str(PIPE / "scripts"))
from vhs_pipeline import (  # noqa
    apply_vhs, make_cartela_azul, make_cartela_preta, make_glitch,
    make_rewind, make_tela_azul_vhs, burn_subs, concat_list,
    export_platforms, encode_common, W, H, FPS, FONT_OSD, FONT_SYM,
)

PY = sys.executable
W, H, FPS = 1080, 1920, 30


def run(cmd, check=True):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=check)


def upscale_lanczos(src: Path, dst: Path, duration: float | None = None):
    """720x1280 → 1080x1920 sem distorcer (scale+pad)."""
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS},format=yuv420p"
    )
    cmd = ["ffmpeg", "-y", "-i", str(src), "-vf", vf,
           "-an", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p"]
    if duration: cmd += ["-t", str(duration)]
    cmd.append(str(dst))
    run(cmd)


def find_photo_bbox(frame_bgr):
    h, w = frame_bgr.shape[:2]
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 120)
    edges = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), 2)
    cnts, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cands = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 8000 or area > w * h * 0.55:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        x, y, bw, bh = cv2.boundingRect(approx if len(approx) >= 4 else c)
        ar = bw / max(bh, 1)
        if 0.5 < ar < 1.5 and bh > 120 and bw > 100:
            cx, cy = x + bw / 2, y + bh / 2
            dist = ((cx - w / 2) ** 2 + (cy - h * 0.45) ** 2) ** 0.5
            cands.append((dist, area, (x, y, bw, bh)))
    if not cands:
        # fallback center photo estimate
        return (w // 2 - 180, h // 2 - 220, 360, 400)
    cands.sort()
    return cands[0][2]


def make_tear_patch(bw, bh, seed=7):
    """Rasgo/mancha de foto velha (branco sujo + fibras) cobrindo a zona do rosto."""
    rng = np.random.RandomState(seed)
    patch = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(patch)
    # irregular torn polygon covering most of patch
    pts = []
    for i in range(14):
        ang = 2 * math.pi * i / 14
        r = 0.42 + 0.12 * rng.rand()
        px = bw * (0.5 + r * math.cos(ang) * 0.95)
        py = bh * (0.48 + r * math.sin(ang) * 1.05)
        pts.append((px, py))
    # paper white / cream with dirt
    base = (236, 228, 210, 245)
    draw.polygon(pts, fill=base)
    # jagged tear edge darker
    for _ in range(40):
        x0 = rng.randint(0, bw)
        y0 = rng.randint(0, bh)
        if patch.getpixel((x0, y0))[3] > 0:
            draw.ellipse([x0 - 3, y0 - 2, x0 + 3, y0 + 2], fill=(210, 200, 180, 220))
    # coffee/water stain
    for _ in range(3):
        cx, cy = rng.randint(bw // 4, 3 * bw // 4), rng.randint(bh // 4, 3 * bh // 4)
        rw, rh = rng.randint(bw // 6, bw // 3), rng.randint(bh // 8, bh // 4)
        draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(160, 130, 90, 90))
    # fiber scratches
    for _ in range(25):
        x0, y0 = rng.randint(0, bw), rng.randint(0, bh)
        x1, y1 = x0 + rng.randint(-40, 40), y0 + rng.randint(-8, 8)
        draw.line([(x0, y0), (x1, y1)], fill=(180, 170, 150, 160), width=1)
    patch = patch.filter(ImageFilter.GaussianBlur(radius=0.8))
    return patch


def process_plano07(src: Path, dst: Path):
    """Usa v1 com rosto: cobre com rasgo + texto lápis 'Benedito · 1931'."""
    cap = cv2.VideoCapture(str(src))
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 24
    w0 = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h0 = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp_avi = WORK / "p07_fixed_raw.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(tmp_avi), fourcc, fps_in, (w0, h0))
    font_path = str(FONTS / "PatrickHand-Regular.ttf")
    last_bbox = None
    fi = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        bbox = find_photo_bbox(frame)
        # temporal smooth
        if last_bbox is not None:
            a = 0.65
            bbox = tuple(int(a * bbox[i] + (1 - a) * last_bbox[i]) for i in range(4))
        last_bbox = bbox
        x, y, bw, bh = bbox
        # face zone
        fh = int(bh * 0.40)
        tear = make_tear_patch(max(bw - 16, 20), max(fh, 20), seed=7 + fi // 8)
        pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
        pil.paste(tear, (x + 8, y + 8), tear)
        # pencil text lower third of photo
        draw = ImageDraw.Draw(pil)
        try:
            font = ImageFont.truetype(font_path, size=max(18, bw // 11))
        except Exception:
            font = ImageFont.load_default()
        text = "Benedito · 1931"
        # position near bottom of photo, pencil gray
        tx = x + bw // 8
        ty = y + int(bh * 0.78)
        # slight shadow for graphite
        for dx, dy, col in [(1, 1, (40, 40, 40, 100)), (0, 0, (55, 55, 50, 210))]:
            draw.text((tx + dx, ty + dy), text, font=font, fill=col)
        out = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        writer.write(out)
        fi += 1
    cap.release()
    writer.release()
    upscale_lanczos(tmp_avi, dst)
    print(f"plano07 done frames={fi}")


def process_plano06(src: Path, dst: Path):
    """Suaviza/escurece mancha humanóide na casca."""
    cap = cv2.VideoCapture(str(src))
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 24
    w0 = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h0 = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp = WORK / "p06_fixed_raw.mp4"
    writer = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"), fps_in, (w0, h0))
    # soft ellipse over mid trunk (humanoid stain)
    yy, xx = np.mgrid[0:h0, 0:w0]
    cx, cy = w0 * 0.50, h0 * 0.38
    rx, ry = w0 * 0.16, h0 * 0.22
    mask = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    alpha = np.clip(1.2 - mask, 0, 1).astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (51, 51), 0)
    alpha3 = alpha[..., None]
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        blurred = cv2.GaussianBlur(frame, (31, 31), 0)
        # darken + desaturate the stain region toward bark
        dark = (blurred.astype(np.float32) * np.array([0.85, 0.88, 0.90])).astype(np.float32)
        # mix more toward neighboring bark by additional blur of original
        bark = cv2.GaussianBlur(frame, (61, 61), 0).astype(np.float32)
        mixed = dark * 0.45 + bark * 0.55
        out = frame.astype(np.float32) * (1 - alpha3) + mixed * alpha3
        writer.write(np.clip(out, 0, 255).astype(np.uint8))
    cap.release()
    writer.release()
    upscale_lanczos(tmp, dst)


def process_plano10(src: Path, dst: Path):
    """Levanta sombras para silhueta aparecer na borda da luz."""
    tmp = WORK / "p10_fixed_raw.mp4"
    # colorlevels / curves: lift shadows, keep highlights
    vf = (
        "eq=brightness=0.06:contrast=1.08:gamma=1.25:saturation=0.9,"
        "curves=all='0/0.08 0.25/0.32 0.5/0.52 1/1',"
        "unsharp=5:5:0.4"
    )
    run(["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-an",
         "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", str(tmp)])
    upscale_lanczos(tmp, dst)


def process_plano11(src: Path, dst: Path, ref_upscaled: Path):
    """Iguala exposição ao plano 10."""
    # measure mean luma of ref
    cap = cv2.VideoCapture(str(ref_upscaled))
    ok, fr = cap.read()
    cap.release()
    if ok:
        mean_ref = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).mean()
    else:
        mean_ref = 40.0
    cap = cv2.VideoCapture(str(src))
    ok, fr = cap.read()
    cap.release()
    mean_src = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).mean() if ok else 30.0
    # brightness offset roughly
    delta = (mean_ref - mean_src) / 255.0
    delta = float(np.clip(delta, -0.15, 0.2))
    gamma = 1.0 + max(0, (mean_ref - mean_src) / 200.0)
    tmp = WORK / "p11_fixed_raw.mp4"
    vf = f"eq=brightness={delta:.3f}:contrast=1.05:gamma={gamma:.3f}:saturation=0.9"
    run(["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-an",
         "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", str(tmp)])
    upscale_lanczos(tmp, dst)
    print(f"plano11 exposure match mean_ref={mean_ref:.1f} mean_src={mean_src:.1f} delta={delta:.3f}")


def prep_simple(src: Path, dst: Path, duration: float):
    upscale_lanczos(src, dst, duration=duration)


def build_audio_stem(timeline_events, total_dur: float, out_wav: Path):
    """Monta stem de ambiente/SFX (sem vozes) a partir dos eventos."""
    # Generate base hiss
    hiss = WORK / "hiss.wav"
    run(["ffmpeg", "-y", "-f", "lavfi",
         "-i", f"anoisesrc=color=pink:amplitude=0.012:sample_rate=48000:duration={total_dur}",
         "-c:a", "pcm_s16le", str(hiss)])
    # Build filter_complex mixing
    inputs = ["-i", str(hiss)]
    filters = []
    labels = ["[0:a]"]
    idx = 1
    # map short names to files
    sfx_map = {
        "cicadas": AUDIO / "cicadas-samwd-414411.mp3",
        "wind": AUDIO / "wind-borgory-751473.mp3",
        "leaves": AUDIO / "leaves-wax_vibe-635875.mp3",
        "breath": AUDIO / "breathing-owlstorm-151206.mp3",
        "branch": AUDIO / "branches-kierankeegan-434555.mp3",
        "rewind": AUDIO / "vcr-rewind-lukacafuka-750857.mp3",
        "vcr": AUDIO / "vcr-vhs-playback-bigsoundbank-2691.mp3",
        "click": AUDIO / "electric-switch-bigsoundbank-0026.mp3",
        "fall": AUDIO / "iron-bar-falls-bigsoundbank-0235.mp3",
        "horse": AUDIO / "horse-borzsounds-843303.mp3",
        "chain": AUDIO / "heavy-chain-bigsoundbank-0359.mp3",
        "chain2": AUDIO / "chain-bruno-670853.mp3",
    }
    for ev in timeline_events:
        path = sfx_map.get(ev["sfx"])
        if not path or not path.exists():
            print("SKIP missing sfx", ev)
            continue
        inputs += ["-i", str(path)]
        start = ev["start"]
        vol = ev.get("vol", 0.4)
        dur = ev.get("dur")
        # atrim + adelay + volume
        # adelay in ms
        delay_ms = int(start * 1000)
        lab_in = f"[{idx}:a]"
        chain = f"{lab_in}aformat=sample_rates=48000:channel_layouts=mono,volume={vol}"
        if dur:
            chain += f",atrim=0:{dur},asetpts=PTS-STARTPTS"
        chain += f",adelay={delay_ms}|{delay_ms}[a{idx}]"
        filters.append(chain)
        labels.append(f"[a{idx}]")
        idx += 1
    if len(labels) == 1:
        # only hiss
        run(["ffmpeg", "-y", "-i", str(hiss), "-t", str(total_dur), "-c:a", "pcm_s16le", str(out_wav)])
        return
    mix_in = "".join(labels)
    filters.append(f"{mix_in}amix=inputs={len(labels)}:duration=longest:dropout_transition=2:normalize=0,volume=1.0,atrim=0:{total_dur},alimiter=limit=0.95[outa]")
    fc = ";".join(filters)
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[outa]",
           "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1", str(out_wav)]
    run(cmd)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    STEMS.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    prepared = WORK / "prepared"
    prepared.mkdir(exist_ok=True)
    vhs_dir = WORK / "vhs"
    vhs_dir.mkdir(exist_ok=True)

    # --- Corrections + upscale ---
    print("=== CORRECTIONS ===")
    process_plano06(CENAS / "plano-06.mp4", prepared / "plano-06.mp4")
    process_plano07(CENAS / "alternativas/plano-07-v1-rosto-visivel.mp4", prepared / "plano-07.mp4")
    process_plano10(CENAS / "plano-10.mp4", prepared / "plano-10.mp4")
    process_plano11(CENAS / "plano-11.mp4", prepared / "plano-11.mp4", prepared / "plano-10.mp4")

    simples = {
        1: (CENAS / "plano-01.mp4", 3.0),
        3: (CENAS / "plano-03.mp4", 7.0),
        4: (CENAS / "plano-04.mp4", 8.0),
        5: (CENAS / "plano-05.mp4", 7.0),
        8: (CENAS / "plano-08.mp4", 7.0),
        9: (CENAS / "plano-09.mp4", 7.0),  # playback dedicated clip
        12: (CENAS / "plano-12.mp4", 8.0),
        13: (CENAS / "plano-01.mp4", 3.5),
    }
    for pid, (src, dur) in simples.items():
        prep_simple(src, prepared / f"plano-{pid:02d}.mp4", dur)

    # trim corrected ones to script durations
    for pid, dur in [(6, 7.0), (7, 7.0), (10, 8.0), (11, 8.0)]:
        src = prepared / f"plano-{pid:02d}.mp4" if pid >= 10 else prepared / f"plano-0{pid}.mp4"
        # already named plano-06 etc
        pass
    for pid, dur in [(6, 7.0), (7, 7.0), (10, 8.0), (11, 8.0)]:
        p = prepared / f"plano-{pid:02d}.mp4"
        tmp = prepared / f"plano-{pid:02d}_t.mp4"
        run(["ffmpeg", "-y", "-i", str(p), "-t", str(dur), "-c", "copy", str(tmp)])
        tmp.replace(p)

    # --- Cartelas / FX ---
    print("=== CARTELAS / FX ===")
    azul = WORK / "cartela_azul.mp4"
    make_cartela_azul(azul, 5.5, [
        "TV MANTIQUEIRA · CANAL 7",
        "CAUSOS DA SERRA",
        "BRUTO · NÃO EDITAR",
        "FITA 01 · CAPELA DO SERENO",
    ])
    azul_osd = vhs_dir / "02_cartela_azul.mp4"
    apply_vhs(azul, azul_osd, "17:40:00", mode="REC", strength=0.5, duration=5.5, soft_look=True)

    glitch = WORK / "fx_glitch.mp4"
    make_glitch(glitch, 0.35)
    tela_azul = WORK / "fx_tela_azul.mp4"
    make_tela_azul_vhs(tela_azul, 0.5)
    c1 = WORK / "final1.mp4"
    make_cartela_preta(c1, 2.0, "Marta Lins e Sebastião Prado\nnunca foram encontrados.")
    c2 = WORK / "final2.mp4"
    make_cartela_preta(c2, 2.0, "Eduardo Reis entregou outras 11 fitas\nà polícia em 1995.")
    c3 = WORK / "final3.mp4"
    make_cartela_preta(c3, 0.7, "FITA 02")

    # flash fita 02: dark road color + horse/chain will be audio
    flash = WORK / "flash_fita02.mp4"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x050508:s={W}x{H}:d=0.55:r={FPS}",
         "-f", "lavfi", "-i", "anoisesrc=color=pink:amplitude=0.02:sample_rate=48000:duration=0.55",
         "-shortest", "-vf", f"noise=alls=20:allf=t+u,drawtext=fontfile={FONTS/'VT323-Regular.ttf'}:fontsize=42:fontcolor=white:borderw=2:bordercolor=black:x=w-tw-48:y=h-th-96:text='SET 02 1994 21\\:14'",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", str(flash)])

    # --- Apply VHS to prepared clips ---
    print("=== VHS ===")
    specs = [
        (1, "03:31:00", "PLAY", 3.0),
        (3, "17:42:00", "REC", 7.0),
        (4, "17:58:00", "REC", 8.0),
        (5, "18:36:00", "REC", 7.0),
        (6, "18:51:00", "REC", 7.0),
        (7, "18:53:00", "REC", 7.0),
        (8, "18:55:00", "REC", 7.0),
        (9, "17:59:00", "PLAY", 6.5),
        (10, "03:12:00", "REC", 8.0),
        (11, "03:13:00", "REC", 8.0),
        (12, "03:14:00", "REC", 8.0),
        (13, "03:31:00", "PLAY", 3.5),
    ]
    vhs_clips = {}
    for pid, tc, mode, dur in specs:
        src = prepared / f"plano-{pid:02d}.mp4"
        dst = vhs_dir / f"plano-{pid:02d}_vhs.mp4"
        apply_vhs(src, dst, tc, mode=mode, duration=dur)
        vhs_clips[pid] = dst

    # rewind from plan 4 / 9 source
    rw = vhs_dir / "rewind.mp4"
    make_rewind(prepared / "plano-04.mp4", rw, dur=1.0)

    # opening cartela text overlay on plan 1 via ASS later

    # --- Concat video (silent-ish, we'll replace audio) ---
    print("=== CONCAT ===")
    parts = [
        vhs_clips[1],
        glitch,
        azul_osd,
        vhs_clips[3],
        vhs_clips[4],
        vhs_clips[5],
        vhs_clips[6],
        vhs_clips[7],
        vhs_clips[8],
        rw,
        vhs_clips[9],
        vhs_clips[10],
        vhs_clips[11],
        vhs_clips[12],
        vhs_clips[13],
        tela_azul,
        c1, c2,
        flash,
        c3,
    ]
    # ensure all have audio — generate silent if missing
    norm_parts = []
    for i, p in enumerate(parts):
        outp = WORK / f"part_{i:02d}.mp4"
        run(["ffmpeg", "-y", "-i", str(p),
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
             "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-ar", "48000", "-ac", "1", "-movflags", "+faststart", str(outp)])
        norm_parts.append(outp)

    concat_raw = WORK / "concat_video.mp4"
    concat_list(norm_parts, concat_raw)
    info = subprocess.check_output([
        "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(concat_raw)
    ])
    total_dur = float(json.loads(info)["format"]["duration"])
    print("CONCAT DUR", total_dur)

    # --- Timeline for audio + voice template ---
    # Approximate starts based on part durations
    # We'll compute from ffprobe of each part
    starts = []
    t = 0.0
    for p in norm_parts:
        d = float(json.loads(subprocess.check_output([
            "ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(p)
        ]))["format"]["duration"])
        starts.append((t, d))
        t += d

    # Map: part index → name
    # 0 p1, 1 glitch, 2 azul, 3 p3, 4 p4, 5 p5, 6 p6, 7 p7, 8 p8, 9 rw, 10 p9, 11 p10, 12 p11, 13 p12, 14 p13, 15 blue, 16 c1, 17 c2, 18 flash, 19 c3
    def S(i): return starts[i][0]

    audio_events = [
        {"sfx": "breath", "start": S(0), "dur": 3.0, "vol": 0.55},
        {"sfx": "click", "start": S(2) + 0.2, "dur": 0.4, "vol": 0.7},
        {"sfx": "vcr", "start": S(2), "dur": 5.5, "vol": 0.15},
        {"sfx": "cicadas", "start": S(3), "dur": 7.0, "vol": 0.35},
        {"sfx": "wind", "start": S(3), "dur": 7.0, "vol": 0.2},
        {"sfx": "cicadas", "start": S(4), "dur": 8.0, "vol": 0.15},
        {"sfx": "cicadas", "start": S(5), "dur": 5.5, "vol": 0.45},  # stop before silence beat
        {"sfx": "leaves", "start": S(5), "dur": 7.0, "vol": 0.35},
        {"sfx": "wind", "start": S(6), "dur": 7.0, "vol": 0.35},
        {"sfx": "wind", "start": S(7), "dur": 7.0, "vol": 0.25},
        {"sfx": "leaves", "start": S(7), "dur": 2.0, "vol": 0.2},
        {"sfx": "wind", "start": S(8), "dur": 7.0, "vol": 0.2},
        {"sfx": "rewind", "start": S(9), "dur": 1.0, "vol": 0.7},
        {"sfx": "vcr", "start": S(10), "dur": 6.5, "vol": 0.2},
        {"sfx": "breath", "start": S(10) + 4.0, "dur": 2.5, "vol": 0.5},
        {"sfx": "cicadas", "start": S(11), "dur": 5.0, "vol": 0.2},  # crickets stand-in
        {"sfx": "branch", "start": S(11) + 6.5, "dur": 1.2, "vol": 0.8},
        {"sfx": "leaves", "start": S(12), "dur": 8.0, "vol": 0.5},
        {"sfx": "breath", "start": S(12), "dur": 8.0, "vol": 0.35},
        {"sfx": "fall", "start": S(12) + 6.5, "dur": 1.0, "vol": 0.85},
        {"sfx": "breath", "start": S(13), "dur": 8.0, "vol": 0.55},
        {"sfx": "breath", "start": S(14), "dur": 3.5, "vol": 0.5},
        {"sfx": "horse", "start": S(18), "dur": 0.55, "vol": 0.7},
        {"sfx": "chain", "start": S(18), "dur": 0.55, "vol": 0.6},
    ]

    stem_amb = STEMS / "stem_ambiente_sfx.wav"
    build_audio_stem(audio_events, total_dur, stem_amb)

    # empty voice stem (silence) for remix template
    stem_voice = STEMS / "stem_voz_placeholder.wav"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={total_dur}",
         "-c:a", "pcm_s16le", str(stem_voice)])

    # Mix video + ambient stem
    master_nosubs = WORK / "master_nosubs.mp4"
    run(["ffmpeg", "-y", "-i", str(concat_raw), "-i", str(stem_amb),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-shortest", "-movflags", "+faststart", str(master_nosubs)])

    # --- Subtitles ASS (cinematic short) aligned to starts ---
    ass_path = WORK / "legendas_ep01_timed.ass"
    # Dialogue times relative to master
    # Opening cartela on plan1
    dialogues = [
        (S(0) + 0.3, S(0) + 2.8, "Cartela", "Esta fita foi encontrada\\Ndentro de uma árvore."),
        (S(2) + 1.5, S(2) + 3.0, "Legenda", "Tá gravando, Tião?"),
        (S(2) + 3.2, S(2) + 4.5, "Legenda", "Tá. Pode ir."),
        (S(3) + 0.5, S(3) + 6.0, "Legenda", "Em Capela do Sereno,\\Na terra recusou um homem."),
        (S(4) + 0.5, S(4) + 4.5, "Legenda", "Bateu na mãe.\\NA terra cuspiu ele de volta."),
        (S(4) + 4.6, S(4) + 6.2, "Legenda", "Seco. Tá lá na figueira."),
        (S(4) + 6.3, S(4) + 7.8, "Legenda", "— Já viu ele?\\N— Todo dia."),
        (S(5) + 0.4, S(5) + 3.0, "Legenda", "Tião, a bateria aguenta?\\NMeia hora."),
        (S(5) + 4.5, S(5) + 6.5, "Legenda", "[as cigarras param]"),
        (S(6) + 3.0, S(6) + 5.5, "Legenda", "Não tem nada aqui."),
        (S(7) + 3.5, S(7) + 6.5, "Legenda", "É a varanda do seu Benedito."),
        (S(8) + 0.5, S(8) + 4.5, "Legenda", "Ele vê ele todo dia.\\NNunca filmamos a cara dele."),
        (S(8) + 5.0, S(8) + 6.5, "Legenda", "Volta a fita."),
        (S(10) + 4.0, S(10) + 6.0, "Legenda", "[respiração]"),
        (S(11) + 6.2, S(11) + 7.5, "Legenda", "[galho estala]"),
        (S(12) + 0.5, S(12) + 3.5, "Legenda", "Corre, Tião! Dudu!"),
        (S(13) + 1.0, S(13) + 6.0, "Legenda", "[silêncio]"),
        (S(14) + 1.0, S(14) + 3.0, "Legenda", "Tião?"),
    ]

    def ts(sec):
        if sec < 0: sec = 0
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    ass = f"""[Script Info]
Title: Fitas da Serra Ep01
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,DejaVu Sans,36,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,4,0,2,70,70,300,1
Style: Cartela,VT323,44,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for a, b, style, text in dialogues:
        if style == "Cartela":
            ass += f"Dialogue: 0,{ts(a)},{ts(b)},{style},,0,0,0,,{{\\an5\\pos(540,900)}}{text}\n"
        else:
            ass += f"Dialogue: 0,{ts(a)},{ts(b)},{style},,0,0,0,,{text}\n"
    ass_path.write_text(ass)

    master = OUT / "fitas-da-serra-ep01_master.mp4"
    burn_subs(master_nosubs, ass_path, master)

    # Voice timeline template
    voice_timeline = {
        "episodio": "fitas-da-serra-ep01",
        "master_video": str(master),
        "stem_ambiente_sfx": str(stem_amb),
        "stem_voz_placeholder": str(stem_voice),
        "sample_rate": 48000,
        "duration_s": total_dur,
        "instrucao": "Substitua stem_voz_placeholder.wav por uma faixa de voz mixada (mesma duração/sample rate). Rode remix_with_voice.sh sem refazer a montagem de vídeo.",
        "falas": [
            {"id": "marta_gravando", "personagem": "Marta", "in": S(2) + 1.5, "out": S(2) + 3.0, "texto": "Tá gravando, Tião?"},
            {"id": "tiao_pode", "personagem": "Tião", "in": S(2) + 3.2, "out": S(2) + 4.5, "texto": "Tá. Pode ir."},
            {"id": "marta_standup", "personagem": "Marta", "in": S(3) + 0.5, "out": S(3) + 6.0, "texto": "Em Capela do Sereno, dizem que a terra recusou um homem."},
            {"id": "benedito_1", "personagem": "Benedito", "in": S(4) + 0.5, "out": S(4) + 4.5, "texto": "Bateu na mãe. Quando morreu, a terra cuspiu ele de volta."},
            {"id": "benedito_2", "personagem": "Benedito", "in": S(4) + 4.6, "out": S(4) + 6.2, "texto": "Seco. Tá lá na figueira."},
            {"id": "marta_viu", "personagem": "Marta", "in": S(4) + 6.3, "out": S(4) + 7.0, "texto": "O senhor já viu ele?"},
            {"id": "benedito_todo", "personagem": "Benedito", "in": S(4) + 7.0, "out": S(4) + 7.8, "texto": "Todo dia."},
            {"id": "dudu_bateria", "personagem": "Dudu", "in": S(5) + 0.4, "out": S(5) + 2.0, "texto": "Tião, a bateria aguenta?"},
            {"id": "tiao_meia", "personagem": "Tião", "in": S(5) + 2.0, "out": S(5) + 3.0, "texto": "Meia hora."},
            {"id": "marta_nada", "personagem": "Marta", "in": S(6) + 3.0, "out": S(6) + 5.5, "texto": "Não tem nada aqui."},
            {"id": "dudu_varanda", "personagem": "Dudu", "in": S(7) + 3.5, "out": S(7) + 6.5, "texto": "Marta... é a varanda do seu Benedito."},
            {"id": "marta_todo", "personagem": "Marta", "in": S(8) + 0.5, "out": S(8) + 2.5, "texto": "Ele disse que vê ele todo dia."},
            {"id": "tiao_cara", "personagem": "Tião", "in": S(8) + 2.5, "out": S(8) + 4.5, "texto": "A gente nunca filmou a cara dele."},
            {"id": "marta_volta", "personagem": "Marta", "in": S(8) + 5.0, "out": S(8) + 6.5, "texto": "Volta a fita."},
            {"id": "marta_corre", "personagem": "Marta", "in": S(12) + 0.5, "out": S(12) + 3.5, "texto": "Corre, Tião! Dudu!"},
            {"id": "marta_tiao", "personagem": "Marta", "in": S(14) + 1.0, "out": S(14) + 3.0, "texto": "Tião?"},
        ],
    }
    (OUT / "voice_timeline.json").write_text(json.dumps(voice_timeline, indent=2, ensure_ascii=False))
    # simple EDL-like
    edl_lines = ["TITLE: Fitas da Serra Ep01 Voice EDL", "FCM: NON-DROP FRAME", ""]
    for i, f in enumerate(voice_timeline["falas"], 1):
        edl_lines.append(f"{i:03d}  VOZ       AA/V  C        {ts(f['in'])} {ts(f['out'])} {ts(f['in'])} {ts(f['out'])}")
        edl_lines.append(f"* FROM CLIP NAME: {f['id']} | {f['personagem']}: {f['texto']}")
    (OUT / "voice_timeline.edl").write_text("\n".join(edl_lines))

    remix_sh = OUT / "remix_with_voice.sh"
    remix_sh.write_text(f"""#!/usr/bin/env bash
set -euo pipefail
# Remixa master de vídeo + stem ambiente + nova faixa de voz, sem remontar.
ROOT="$(cd "$(dirname "$0")" && pwd)"
VOICE="${{1:-$ROOT/stems/stem_voz_placeholder.wav}}"
OUTFILE="${{2:-$ROOT/fitas-da-serra-ep01_master_com_voz.mp4}}"
VIDEO="$ROOT/fitas-da-serra-ep01_master.mp4"
AMB="$ROOT/stems/stem_ambiente_sfx.wav"
ffmpeg -y -i "$VIDEO" -i "$AMB" -i "$VOICE" \\
  -filter_complex "[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[a]" \\
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart \\
  "$OUTFILE"
echo "OK $OUTFILE"
""")
    remix_sh.chmod(0o755)

    # Export platforms
    presets = json.loads((PIPE / "config/export-presets.json").read_text())
    # export into OUT and exports/
    for key in ("tiktok", "reels", "shorts"):
        suf = presets["plataformas"][key]["arquivo_sufixo"]
        out = OUT / f"fitas-da-serra-ep01{suf}"
        cmd = ["ffmpeg", "-y", "-i", str(master), *encode_common(key, presets), str(out)]
        run(cmd)
        shutil.copy2(out, EXPORTS / out.name)

    # Check frames
    checks = {
        "plano02_cartela_azul": S(2) + 2.0,
        "plano06_arvore": S(6) + 3.5,
        "plano07_foto": S(7) + 4.0,
        "plano10_silhueta": S(11) - starts[11][1] + 4.0 if False else S(11) - (starts[11][0] - starts[11][0]),
    }
    # fix plano10 time
    check_times = {
        "02_cartela_azul": S(2) + 2.5,
        "06_arvore": S(6) + 3.5,
        "07_foto": S(7) + 4.0,
        "10_silhueta": S(11) - starts[11][1] + 4.0,
    }
    # S(11) is start of plan 11; plan 10 starts at S(11)-dur10
    check_times["10_silhueta"] = S(11) - starts[11][1]  # wrong
    check_times["10_silhueta"] = starts[11][0] - starts[11][1]  # still wrong
    # part index 11 is plan 10
    check_times = {
        "02_cartela_azul": starts[2][0] + 2.5,
        "06_arvore": starts[6][0] + 3.5,
        "07_foto": starts[7][0] + 4.0,
        "10_silhueta": starts[11][0] + 4.0,
        "11_fuga": starts[12][0] + 2.0,
        "final_desaparecidos": starts[16][0] + 0.8,
        "final_eduardo": starts[17][0] + 0.8,
        "final_fita02": starts[19][0] + 0.3,
    }
    for name, tsec in check_times.items():
        outf = FRAMES / f"check_{name}.png"
        run(["ffmpeg", "-y", "-ss", f"{tsec:.3f}", "-i", str(master),
             "-frames:v", "1", "-update", "1", str(outf)])

    meta = {
        "duration_s": total_dur,
        "master": str(master),
        "starts": starts,
        "check_times": check_times,
    }
    (OUT / "assemble_meta.json").write_text(json.dumps(meta, indent=2))
    print("MASTER_OK", total_dur, master)


if __name__ == "__main__":
    main()
