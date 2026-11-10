#!/usr/bin/env bash
set -euo pipefail
# Remixa master de vídeo + stem ambiente + faixa de voz, sem remontar.
# Ducking leve do ambiente via sidechaincompress quando a voz está presente.
ROOT="$(cd "$(dirname "$0")" && pwd)"
VOICE="${1:-$ROOT/stems/stem_voz_guia_piper.wav}"
OUTFILE="${2:-$ROOT/fitas-da-serra-ep01_master_com_voz.mp4}"
VIDEO="$ROOT/fitas-da-serra-ep01_master.mp4"
AMB="$ROOT/stems/stem_ambiente_sfx.wav"
ffmpeg -y -i "$VIDEO" -i "$AMB" -i "$VOICE" \
  -filter_complex "[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[amb];\
[2:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,pan=stereo|c0=c0|c1=c0[voz];\
[amb][voz]sidechaincompress=threshold=0.05:ratio=2.5:attack=20:release=280:makeup=1:knee=4[ambd];\
[ambd][voz]amix=inputs=2:duration=first:dropout_transition=2:weights=0.75 1.0,\
loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart \
  "$OUTFILE"
echo "OK $OUTFILE"
