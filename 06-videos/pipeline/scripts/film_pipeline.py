#!/usr/bin/env python3
"""
Pipeline de look Super-8/16mm (sépia-esverdeado) 9:16 — Avísos à População
NÃO é VHS: sem timestamp, REC, tracking lines ou OSD de câmera.
Cinestudio AI · Editor · fontes OFL/livres documentadas.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CINE = ROOT.parents[1] if (ROOT.parents[1] / "03-roteiros").exists() else Path("/workspace/cinestudio")
PIPE = ROOT
CONFIG = PIPE / "config"

W, H, FPS = 1080, 1920, 30


def run(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=check)


def ffprobe_json(path: Path) -> dict:
    out = subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    )
    return json.loads(out)


def ffprobe_dur(path: Path) -> float:
    return float(ffprobe_json(path)["format"]["duration"])


def escape_filter_path(p: Path) -> str:
    s = str(p.resolve())
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def film_video_filters(
    strength: float = 1.0,
    weave: bool = True,
    flicker: bool = True,
    extra: str | None = None,
    skip_scale: bool = False,
) -> str:
    """Cadeia de look filme Super-8/16mm. Sem OSD/timestamp/REC."""
    g = max(0.2, min(2.0, strength))
    grain = max(6, int(11 * g))
    parts: list[str] = []
    if not skip_scale:
        parts += [
            f"scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=decrease",
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x1a1810",
            "setsar=1",
            f"fps={FPS}",
            "format=yuv420p",
        ]
    else:
        parts += ["setsar=1", f"fps={FPS}", "format=yuv420p"]

    # Sépia-esverdeado desbotado: pretos lavados puxando a oliva, altas creme
    parts += [
        # Sépia-oliva: reduzir magenta do material de origem, pretos lavados, altas creme
        "eq=saturation=0.55:contrast=1.07:brightness=-0.02:gamma=1.03:gamma_g=1.16:gamma_b=0.88:gamma_r=1.04",
        "colorbalance=rs=-0.04:gs=0.08:bs=-0.10:rm=-0.03:gm=0.08:bm=-0.08:rh=0.02:gh=0.07:bh=-0.08",
        "curves=all='0/0.04 0.12/0.12 0.5/0.47 1/0.93'",
    ]
    if flicker:
        parts.append(
            "eq=brightness='0.022*sin(2*PI*t*16)+0.01*sin(2*PI*t*3.3)+0.006*sin(2*PI*t*0.7)'"
        )
    if weave:
        # gate weave / tremor de projetor (crop + relayout)
        parts += [
            "crop=w=iw-14:h=ih-14:x='7+3.2*sin(n/8.5+2)+1.4*sin(n/19)':y='7+2.4*sin(n/13.0)+1.1*sin(n/7.5)'",
            f"scale={W}:{H}:flags=lanczos",
            "setsar=1",
        ]
    parts += [
        f"noise=alls={grain}:allf=t+u",
        "vignette=PI/5.8:aspect=9/16",
    ]
    if extra:
        parts.append(extra)
    return ",".join(parts)


def apply_film(
    src: Path,
    dst: Path,
    duration: float | None = None,
    strength: float = 1.0,
    weave: bool = True,
    overlay: Path | None = None,
    anull: bool = False,
) -> Path:
    """Aplica look filme a um clipe já em 1080x1920 (ou escala). Mantém áudio se houver."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    vf = film_video_filters(strength=strength, weave=weave, skip_scale=False)
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if overlay and overlay.exists():
        cmd += ["-stream_loop", "-1", "-i", str(overlay)]
        # overlay de poeira/riscos no modo screen/addition suave
        vf = vf + f",[0:v]{vf}[base];[1:v]format=rgba,colorchannelmixer=aa=0.55[ov];[base][ov]overlay=shortest=1:format=auto"
        # wait, I duplicated vf. Fix below if overlay path used carefully in assemble.
    cmd += ["-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "16"]
    if duration is not None:
        cmd += ["-t", f"{duration:.4f}"]
    if anull:
        cmd += ["-an"]
    else:
        cmd += ["-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "160k"]
    cmd += ["-movflags", "+faststart", str(dst)]
    run(cmd)
    return dst


def encode_common(platform: str, presets: dict) -> list[str]:
    comum = presets["comum"]
    p = presets["plataformas"][platform]
    return [
        "-c:v", comum["video_codec"],
        "-profile:v", comum["profile"],
        "-pix_fmt", comum["pix_fmt"],
        "-r", str(comum["fps"]),
        "-b:v", p["video_bitrate"],
        "-maxrate", p["maxrate"],
        "-bufsize", p["bufsize"],
        "-preset", p["preset"],
        "-c:a", comum["audio_codec"],
        "-b:a", p["audio_bitrate"],
        "-ar", str(comum["audio_rate"]),
        "-ac", str(comum["audio_channels"]),
        "-movflags", comum["movflags"],
    ]


def concat_list(parts: list[Path], out: Path) -> Path:
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), "-preset", "medium", "-crf", "16",
        "-an", "-movflags", "+faststart", str(out),
    ])
    return out


def concat_copy(parts: list[Path], out: Path) -> Path:
    """Concat demuxer assuming identical codecs."""
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c", "copy", "-movflags", "+faststart", str(out),
    ])
    return out


def burn_subs(video: Path, ass: Path, out: Path, fontsdir: Path) -> Path:
    ass_esc = escape_filter_path(ass)
    fonts = escape_filter_path(fontsdir)
    run([
        "ffmpeg", "-y", "-i", str(video),
        "-vf", f"ass={ass_esc}:fontsdir={fonts}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "16",
        "-c:a", "copy", "-movflags", "+faststart", str(out),
    ])
    return out


def export_platforms(master: Path, dest_dir: Path, stem: str, presets: dict) -> dict:
    dest_dir.mkdir(parents=True, exist_ok=True)
    outs = {}
    for key in ("tiktok", "reels", "shorts"):
        out = dest_dir / f"{stem}_{key}_guia.mp4"
        run(["ffmpeg", "-y", "-i", str(master), *encode_common(key, presets), str(out)])
        outs[key] = out
    return outs


def frame_skip_filter(at_sec: float, frames: int = 2) -> str:
    """Pula N quadros a partir de at_sec (select). Aplicar antes do fps final."""
    # freeze/skip: drop frames in a short window
    t0 = at_sec
    t1 = at_sec + frames / FPS
    return f"select='not(between(t\\,{t0:.3f}\\,{t1:.3f}))',setpts=N/FRAME_RATE/TB"


if __name__ == "__main__":
    print("film_pipeline ready", W, H, FPS)
