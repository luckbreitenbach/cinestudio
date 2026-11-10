#!/usr/bin/env python3
"""
Pipeline de edição VHS 9:16 — Fitas da Serra Ep. 01
Cinestudio AI · Editor · uso comercial com fontes OFL/livres documentadas.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # .../pipeline
CINE = ROOT.parents[1] if (ROOT.parents[1] / "03-roteiros").exists() else Path("/workspace/cinestudio")
PIPE = ROOT
FONTS = PIPE / "fonts"
CONFIG = PIPE / "config"
TEST = PIPE / "test-clips"
PREVIEW = PIPE / "preview"
EXPORTS = PIPE / "exports"
FRAMES = PREVIEW / "frames"

W, H, FPS = 1080, 1920, 30
FONT_OSD = FONTS / "VT323-Regular.ttf"
FONT_SYM = FONTS / "DejaVuSans.ttf"
FONT_ALT = FONTS / "ShareTechMono-Regular.ttf"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=check)


def ffprobe_json(path: Path) -> dict:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", str(path),
        ]
    )
    return json.loads(out)


def tc_to_seconds(tc: str) -> int:
    """HH:MM:SS or MM:SS -> seconds from midnight (or just total seconds if MM:SS)."""
    parts = [int(p) for p in tc.split(":")]
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        raise ValueError(tc)
    return h * 3600 + m * 60 + s


def escape_drawtext_path(p: Path) -> str:
    # ffmpeg drawtext fontfile: escape : and \
    s = str(p.resolve())
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def escape_filter_path(p: Path) -> str:
    s = str(p.resolve())
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def vhs_video_filters(
    start_seconds: int,
    date_label: str = "AGO 14 1994",
    mode: str = "REC",
    strength: float = 1.0,
    soft_look: bool = False,
) -> str:
    """
    Cadeia de filtros VHS + overlays OSD.
    Timestamp canto inferior direito; REC/PLAY canto superior esquerdo.
    Símbolos ●/▶ via DejaVu (OFL/livre); texto via VT323 (OFL).
    """
    g = max(0.2, min(2.0, strength))
    font = escape_drawtext_path(FONT_OSD)
    font_sym = escape_drawtext_path(FONT_SYM)

    # Relógio correndo a partir de start_seconds
    # eif expressions: hours, minutes, seconds
    h_expr = f"%{{eif\\:mod(floor(({start_seconds}+t)/3600)\\,24)\\:d\\:2}}"
    m_expr = f"%{{eif\\:mod(floor(({start_seconds}+t)/60)\\,60)\\:d\\:2}}"
    s_expr = f"%{{eif\\:mod(floor({start_seconds}+t)\\,60)\\:d\\:2}}"
    clock = f"{date_label} {h_expr}\\:{m_expr}\\:{s_expr}"

    # Safe zones: REC below top UI (~y=140), timestamp above bottom UI (~y=h-110)
    # Legendas ASS usam MarginV=300 para ficarem acima do timestamp.
    ts = (
        f"drawtext=fontfile={font}:fontsize=46:fontcolor=white@0.92:"
        f"borderw=3:bordercolor=black@0.85:"
        f"x=w-tw-48:y=h-th-96:text='{clock}'"
    )

    if mode.upper() == "PLAY":
        mode_text = (
            f"drawtext=fontfile={font_sym}:fontsize=40:fontcolor=white@0.95:"
            f"borderw=3:bordercolor=black@0.85:"
            f"x=48:y=148:text='▶'"
            f","
            f"drawtext=fontfile={font}:fontsize=46:fontcolor=white@0.95:"
            f"borderw=3:bordercolor=black@0.85:"
            f"x=96:y=144:text='PLAY'"
        )
    else:
        # REC + círculo desenhado (fallback visual se glifo falhar) + ● DejaVu
        mode_text = (
            f"drawtext=fontfile={font}:fontsize=46:fontcolor=white@0.95:"
            f"borderw=3:bordercolor=black@0.85:"
            f"x=48:y=144:text='REC'"
            f","
            f"drawtext=fontfile={font_sym}:fontsize=36:fontcolor=white@0.95:"
            f"borderw=2:bordercolor=black@0.85:"
            f"x=160:y=150:text='●'"
        )

    # Escala / letterbox → look VHS
    # wobble via crop animado; grain; chroma bleed; sat baixa; pretos esmagados;
    # linhas de tracking periódicas com geq overlay sutil
    grain = int(18 * g)
    cbh = max(1, int(3 * g))
    crh = -max(1, int(2 * g))
    sat = 0.55 / (0.7 + 0.3 * g)

    # geq: tracking lines + reforço de bleed nos vermelhos (cr alto)
    geq = (
        "geq=lum='lum(X,Y)"
        "+if(eq(mod(floor(T*3)\\,17)\\,0)\\,if(eq(mod(Y\\,48)\\,0)\\,-18\\,0)\\,0)"
        "+if(between(Y\\,200+20*sin(T*2)\\,206+20*sin(T*2))\\,-30\\,0)':"
        "cb='cb(X,Y)':"
        "cr='cr(X,Y)+if(gt(cr(X,Y)\\,140)\\,8\\,0)'"
    )

    if soft_look:
        # cartelas/telas de emissora: preserva cor (azul), só grão leve + OSD
        parts = [
            f"scale={W}:{H}:force_original_aspect_ratio=decrease",
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black",
            "setsar=1",
            f"fps={FPS}",
            "format=yuv420p",
            "eq=saturation=0.85:contrast=1.05:brightness=0.02",
            f"noise=alls={max(6, grain // 2)}:allf=t+u",
            mode_text,
            ts,
        ]
    else:
        parts = [
            f"scale={W}:{H}:force_original_aspect_ratio=decrease",
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black",
            "setsar=1",
            f"fps={FPS}",
            "format=yuv420p",
            f"eq=saturation={sat:.3f}:contrast=1.18:brightness=-0.06:gamma=0.92",
            "curves=all='0/0 0.08/0.02 0.5/0.45 1/0.92'",
            f"chromashift=cbh={cbh}:crh={crh}:cbv=1:crv=-1",
            "crop=w=iw-10:h=ih-10:x='5+3*sin(n/8)':y='5+2*sin(n/13)'",
            f"scale={W}:{H}",
            "setsar=1",
            f"noise=alls={grain}:allf=t+u",
            geq,
            "vignette=PI/5",
            mode_text,
            ts,
        ]
    return ",".join(parts)


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


def gen_test_clips() -> dict[str, Path]:
    """Gera clipes lavfi coloridos/texturizados 9:16 para o preview."""
    TEST.mkdir(parents=True, exist_ok=True)
    clips = {}

    specs = [
        # nome, duração, lavfi video source
        ("gancho", 3.0, "color=c=0x0a1208:s=1080x1920:d=3:r=30,drawgrid=w=80:h=80:t=1:c=0x1a2a18@0.4"),
        ("standup", 5.0, "testsrc2=s=1080x1920:d=5:r=30"),
        ("entrevista", 4.0, "color=c=0x3a2a22:s=1080x1920:d=4:r=30,drawgrid=w=40:h=40:t=1:c=0x5a4030@0.3"),
        ("trilha", 3.0, "testsrc2=s=1080x1920:d=3:r=30,hue=s=0.4"),
        ("noite", 4.0, "color=c=0x050508:s=1080x1920:d=4:r=30,drawgrid=w=120:h=120:t=1:c=0x101018@0.5"),
        ("fuga", 3.0, "testsrc2=s=1080x1920:d=3:r=30,eq=brightness=0.1:saturation=0.5"),
    ]

    # áudio: hiss VHS sintético (anoisesrc) — gerado localmente
    for name, dur, vsrc in specs:
        out = TEST / f"{name}.mp4"
        if out.exists() and out.stat().st_size > 1000:
            clips[name] = out
            continue
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"{vsrc}",
            "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude=0.02:sample_rate=48000:duration={dur}",
            "-shortest",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
            "-movflags", "+faststart",
            str(out),
        ]
        # vsrc may contain commas — already a single arg
        run(cmd)
        clips[name] = out
    return clips


def make_cartela_azul(out: Path, dur: float, linhas: list[str]) -> Path:
    """Tela azul VHS estilo emissora + textos do roteiro."""
    font = escape_drawtext_path(FONT_OSD)
    # fundo azul clássico ~#0012A8 com leve ruído depois
    draws = []
    # título centralizado verticalmente
    base_y = 640
    for i, line in enumerate(linhas):
        # escape special for drawtext
        safe = line.replace(":", "\\:").replace("'", "\\'")
        fs = 56 if i == 1 else 42
        y = base_y + i * 90
        draws.append(
            f"drawtext=fontfile={font}:fontsize={fs}:fontcolor=white:"
            f"borderw=2:bordercolor=black@0.5:"
            f"x=(w-tw)/2:y={y}:text='{safe}'"
        )
    # logo texto amarelo no topo
    draws.insert(
        0,
        f"drawtext=fontfile={font}:fontsize=36:fontcolor=0xFFE14A:"
        f"borderw=2:bordercolor=black@0.6:"
        f"x=(w-tw)/2:y=420:text='▲ TV MANTIQUEIRA'",
    )
    vf = (
        f"scale={W}:{H},setsar=1,fps={FPS},"
        f"noise=alls=10:allf=t+u,"
        f"eq=saturation=0.7:contrast=1.05,"
        + ",".join(draws)
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0A2AD4:s={W}x{H}:d={dur}:r={FPS}",
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude=0.015:sample_rate=48000:duration={dur}",
        "-shortest",
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
        "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)
    return out


def make_cartela_preta(out: Path, dur: float, texto: str) -> Path:
    font = escape_drawtext_path(FONT_OSD)
    # multilinha: usar \N não funciona em drawtext; múltiplos drawtext ou textfile
    lines = texto.split("\n")
    draws = []
    total = len(lines)
    start_y = H // 2 - (total * 70) // 2
    for i, line in enumerate(lines):
        safe = line.replace(":", "\\:").replace("'", "\\'")
        draws.append(
            f"drawtext=fontfile={font}:fontsize=48:fontcolor=white:"
            f"borderw=2:bordercolor=black:"
            f"x=(w-tw)/2:y={start_y + i * 70}:text='{safe}'"
        )
    vf = f"scale={W}:{H},setsar=1,fps={FPS}," + ",".join(draws) if draws else f"scale={W}:{H}"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:d={dur}:r={FPS}",
        "-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.008:sample_rate=48000:duration={dur}",
        "-shortest",
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", "-ar", "48000",
        "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)
    return out


def make_glitch(out: Path, dur: float = 0.45) -> Path:
    """Glitch de tracking curto (tela com barras / deslocamento)."""
    vf = (
        f"scale={W}:{H},setsar=1,fps={FPS},"
        f"geq=lum='lum(X,Y+10*sin(X/20+T*40))+20*eq(mod(Y\\,12)\\,0)':"
        f"cb='cb(X+8*sin(T*30),Y)':cr='cr(X-6*sin(T*25),Y)',"
        f"noise=alls=40:allf=t+u,"
        f"eq=saturation=0.4:contrast=1.4"
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"testsrc2=s={W}x{H}:d={dur}:r={FPS}",
        "-f", "lavfi", "-i", f"anoisesrc=color=white:amplitude=0.05:sample_rate=48000:duration={dur}",
        "-shortest",
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000",
        str(out),
    ]
    run(cmd)
    return out


def make_rewind(src: Path, out: Path, dur: float = 1.2) -> Path:
    """Rebobinar: reverse acelerado + distorção de tracking."""
    # pega trecho, reverse, speed up, vhs-ish distortion
    vf = (
        f"reverse,setpts=0.35*PTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
        f"eq=saturation=0.45:contrast=1.3,"
        f"chromashift=cbh=6:crh=-6,"
        f"noise=alls=30:allf=t+u,"
        f"geq=lum='lum(X,Y)+if(eq(mod(Y\\,10)\\,0)\\,-25\\,0)':cb='cb(X,Y)':cr='cr(X,Y)',"
        f"fps={FPS}"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-vf", vf,
        "-af", "areverse,atempo=1.5,atempo=1.5,volume=0.7",
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000",
        str(out),
    ]
    run(cmd)
    return out


def make_tela_azul_vhs(out: Path, dur: float = 0.8) -> Path:
    vf = f"scale={W}:{H},noise=alls=12:allf=t+u,eq=saturation=0.6"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0A2AD4:s={W}x{H}:d={dur}:r={FPS}",
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude=0.02:sample_rate=48000:duration={dur}",
        "-shortest",
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000",
        str(out),
    ]
    run(cmd)
    return out


def apply_vhs(
    src: Path,
    out: Path,
    start_tc: str,
    mode: str = "REC",
    date_label: str = "AGO 14 1994",
    strength: float = 1.0,
    duration: float | None = None,
    soft_look: bool = False,
) -> Path:
    start_s = tc_to_seconds(start_tc)
    vf = vhs_video_filters(start_s, date_label=date_label, mode=mode, strength=strength, soft_look=soft_look)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-movflags", "+faststart",
    ]
    if duration is not None:
        cmd.extend(["-t", str(duration)])
    cmd.append(str(out))
    run(cmd)
    return out


def burn_subs(src: Path, ass: Path, out: Path) -> Path:
    # fontsdir so ASS finds VT323 / DejaVu
    fontsdir = escape_filter_path(FONTS)
    ass_esc = escape_filter_path(ass)
    vf = f"ass={ass_esc}:fontsdir={fontsdir}"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)
    return out


def concat_list(paths: list[Path], out: Path) -> Path:
    """Concat demuxer — todos devem ter mesmos codecs. Reencode para garantir."""
    # reencode approach via filter concat for safety
    if not paths:
        raise ValueError("sem clips")
    cmd = ["ffmpeg", "-y"]
    for p in paths:
        cmd.extend(["-i", str(p)])
    n = len(paths)
    streams = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(n))
    fc = f"{streams}concat=n={n}:v=1:a=1[v][a]"
    cmd.extend([
        "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-movflags", "+faststart",
        str(out),
    ])
    run(cmd)
    return out


def export_platforms(src: Path, stem: str, presets: dict) -> dict[str, Path]:
    outs = {}
    for key in ("tiktok", "reels", "shorts"):
        suf = presets["plataformas"][key]["arquivo_sufixo"]
        out = EXPORTS / f"{stem}{suf}"
        # also copy into preview/
        out_prev = PREVIEW / f"{stem}{suf}"
        cmd = [
            "ffmpeg", "-y", "-i", str(src),
            *encode_common(key, presets),
            str(out),
        ]
        run(cmd)
        shutil.copy2(out, out_prev)
        outs[key] = out_prev
    return outs


def extract_frames(src: Path, times: list[float], prefix: str = "frame") -> list[Path]:
    FRAMES.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, t in enumerate(times):
        out = FRAMES / f"{prefix}_{i+1:02d}_{t:.2f}s.png"
        run([
            "ffmpeg", "-y", "-ss", str(t), "-i", str(src),
            "-frames:v", "1", "-update", "1", "-q:v", "2", str(out),
        ])
        paths.append(out)
    return paths


def build_preview() -> Path:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="vhs_prev_"))
    try:
        clips = gen_test_clips()
        parts: list[Path] = []

        # 1) gancho PLAY + timestamp 03:31
        g1 = tmp / "01_gancho_vhs.mp4"
        apply_vhs(clips["gancho"], g1, "03:31:00", mode="PLAY", duration=2.5)
        parts.append(g1)

        # glitch cut
        gl = tmp / "02_glitch.mp4"
        make_glitch(gl, 0.4)
        parts.append(gl)

        # 2) cartela azul TV Mantiqueira
        azul = tmp / "03_cartela_azul.mp4"
        make_cartela_azul(
            azul,
            3.2,
            [
                "TV MANTIQUEIRA · CANAL 7",
                "CAUSOS DA SERRA",
                "BRUTO · NÃO EDITAR",
                "FITA 01 · CAPELA DO SERENO",
            ],
        )
        # apply REC overlay lightly? cartela already has text; still add subtle vhs noise only
        # apply thin vhs without rewriting texts too hard — skip heavy OSD on cartela, add small REC
        azul_osd = tmp / "03_cartela_azul_osd.mp4"
        apply_vhs(azul, azul_osd, "17:40:00", mode="REC", strength=0.5, duration=3.2, soft_look=True)
        parts.append(azul_osd)

        # 3) standup REC 17:42
        st = tmp / "04_standup.mp4"
        apply_vhs(clips["standup"], st, "17:42:00", mode="REC", duration=4.0)
        parts.append(st)

        # 4) entrevista
        en = tmp / "05_entrevista.mp4"
        apply_vhs(clips["entrevista"], en, "17:58:00", mode="REC", duration=3.0)
        parts.append(en)

        # rewind
        rw = tmp / "06_rewind.mp4"
        make_rewind(clips["entrevista"], rw, dur=1.1)
        parts.append(rw)

        # playback PLAY
        pb = tmp / "07_playback.mp4"
        apply_vhs(clips["entrevista"], pb, "17:59:00", mode="PLAY", duration=2.0)
        parts.append(pb)

        # noite
        nt = tmp / "08_noite.mp4"
        apply_vhs(clips["noite"], nt, "03:12:00", mode="REC", duration=2.5)
        parts.append(nt)

        # fuga + glitch
        fg = tmp / "09_fuga.mp4"
        apply_vhs(clips["fuga"], fg, "03:13:00", mode="REC", duration=2.0)
        parts.append(fg)
        gl2 = tmp / "10_glitch2.mp4"
        make_glitch(gl2, 0.35)
        parts.append(gl2)

        # tela azul transição
        ta = tmp / "11_tela_azul.mp4"
        make_tela_azul_vhs(ta, 0.6)
        parts.append(ta)

        # cartelas finais
        c1 = tmp / "12_final1.mp4"
        make_cartela_preta(
            c1, 2.0,
            "Marta Lins e Sebastião Prado\nnunca foram encontrados.",
        )
        parts.append(c1)
        c2 = tmp / "13_final2.mp4"
        make_cartela_preta(
            c2, 2.0,
            "Eduardo Reis entregou outras 11 fitas\nà polícia em 1995.",
        )
        parts.append(c2)
        c3 = tmp / "14_fita02.mp4"
        make_cartela_preta(c3, 0.9, "FITA 02")
        parts.append(c3)

        concat_raw = tmp / "concat_raw.mp4"
        concat_list(parts, concat_raw)

        # burn preview subtitles
        with_subs = tmp / "with_subs.mp4"
        burn_subs(concat_raw, CONFIG / "legendas-preview.ass", with_subs)

        master = PREVIEW / "preview-teste_master.mp4"
        shutil.copy2(with_subs, master)

        presets = json.loads((CONFIG / "export-presets.json").read_text())
        outs = export_platforms(master, "preview-teste", presets)

        # frames de verificação em momentos-chave
        # durations approximate — probe master
        info = ffprobe_json(master)
        dur = float(info["format"]["duration"])
        sample_times = [
            min(1.0, dur * 0.05),
            min(4.5, dur * 0.22),
            min(9.0, dur * 0.40),
            min(max(dur - 3.5, 1.0), dur * 0.88),
        ]
        extract_frames(master, sample_times, prefix="preview")

        # write probe report
        report = {
            "master": str(master),
            "exports": {k: str(v) for k, v in outs.items()},
            "duration_s": dur,
            "streams": info.get("streams", []),
            "format": {
                "format_name": info["format"].get("format_name"),
                "bit_rate": info["format"].get("bit_rate"),
                "duration": info["format"].get("duration"),
            },
        }
        (PREVIEW / "ffprobe-master.json").write_text(json.dumps(report, indent=2))
        print(f"PREVIEW_OK duration={dur:.2f}s master={master}")
        return master
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def apply_to_real_clip(args: argparse.Namespace) -> None:
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    apply_vhs(
        Path(args.input),
        out,
        args.start_tc,
        mode=args.mode,
        date_label=args.date,
        strength=args.strength,
        duration=args.duration,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Pipeline VHS Fitas da Serra Ep.01")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_prev = sub.add_parser("preview", help="Gera preview de teste completo")
    p_prev.set_defaults(func=lambda a: build_preview())

    p_app = sub.add_parser("apply", help="Aplica VHS+OSD a um clipe")
    p_app.add_argument("-i", "--input", required=True)
    p_app.add_argument("-o", "--output", required=True)
    p_app.add_argument("--start-tc", default="17:42:00")
    p_app.add_argument("--mode", choices=["REC", "PLAY"], default="REC")
    p_app.add_argument("--date", default="AGO 14 1994")
    p_app.add_argument("--strength", type=float, default=1.0)
    p_app.add_argument("--duration", type=float, default=None)
    p_app.set_defaults(func=apply_to_real_clip)

    p_exp = sub.add_parser("export", help="Exporta master para TikTok/Reels/Shorts")
    p_exp.add_argument("-i", "--input", required=True)
    p_exp.add_argument("--stem", default="fitas-da-serra-ep01")
    def _exp(a):
        presets = json.loads((CONFIG / "export-presets.json").read_text())
        EXPORTS.mkdir(parents=True, exist_ok=True)
        export_platforms(Path(a.input), a.stem, presets)
    p_exp.set_defaults(func=_exp)

    p_cart = sub.add_parser("cartelas", help="Gera cartelas azul e finais")
    def _cart(a):
        assets = PIPE / "assets" / "cartelas"
        assets.mkdir(parents=True, exist_ok=True)
        make_cartela_azul(
            assets / "tv-mantiqueira-bruto.mp4",
            6.0,
            [
                "TV MANTIQUEIRA · CANAL 7",
                "CAUSOS DA SERRA",
                "BRUTO · NÃO EDITAR",
                "FITA 01 · CAPELA DO SERENO",
            ],
        )
        make_cartela_preta(
            assets / "final-desaparecidos.mp4",
            2.5,
            "Marta Lins e Sebastião Prado\nnunca foram encontrados.",
        )
        make_cartela_preta(
            assets / "final-eduardo.mp4",
            2.5,
            "Eduardo Reis entregou outras 11 fitas\nà polícia em 1995.",
        )
        make_cartela_preta(assets / "final-fita02.mp4", 1.0, "FITA 02")
        make_glitch(assets / "fx-glitch-tracking.mp4", 0.5)
        make_tela_azul_vhs(assets / "fx-tela-azul.mp4", 1.0)
        print("cartelas em", assets)
    p_cart.set_defaults(func=_cart)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
