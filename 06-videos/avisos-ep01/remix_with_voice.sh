#!/usr/bin/env bash
set -euo pipefail
# Remixa o vídeo já legendado + stems de ambiente/chiado/SFX + nova faixa de voz,
# sem remontar a imagem. A voz "dry" pode passar pelo filtro AM da rádio.
#
# Uso:
#   ./remix_with_voice.sh                         # usa stem_voz_guia_kokoro.wav (já com AM)
#   ./remix_with_voice.sh stems/stem_voz_final.wav avisos-ep01_master_com_voz.mp4
#   ./remix_with_voice.sh stems/stem_voz_dry.wav  avisos-ep01_master_com_voz.mp4 --am
#
# --am aplica o filtro de microfone AM (300–3400 Hz, compressão, saturação leve)
# na faixa de entrada (útil para trocar depois pelo Gemini/Google WaveNet).
ROOT="$(cd "$(dirname "$0")" && pwd)"
VOICE="${1:-$ROOT/stems/stem_voz_guia_kokoro.wav}"
OUTFILE="${2:-$ROOT/avisos-ep01_master_com_voz.mp4}"
APPLY_AM="${3:-}"
VIDEO="$ROOT/work/video_film_subs_silent.mp4"
# fallback: master guia without replacing
if [[ ! -f "$VIDEO" ]]; then
  VIDEO="$ROOT/avisos-ep01_master_guia.mp4"
fi
AMB="$ROOT/stems/stem_ambiente.wav"
CHIADO="$ROOT/stems/stem_am_chiado.wav"
SFX="$ROOT/stems/stem_sfx_vinheta.wav"

if [[ "$APPLY_AM" == "--am" ]]; then
  VOZ_F="[3:a]highpass=f=300,lowpass=f=3400,acompressor=threshold=-20dB:ratio=3.5:attack=8:release=80:makeup=4,asoftclip=type=tanh,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,pan=stereo|c0=c0|c1=c0,asplit=2[voz1][voz2]"
else
  VOZ_F="[3:a]aformat=sample_fmts=fltp:sample_rates=48000,pan=stereo|c0=c0|c1=c0,asplit=2[voz1][voz2]"
fi

ffmpeg -y -i "$VIDEO" -i "$AMB" -i "$CHIADO" -i "$VOICE" -i "$SFX" \
  -filter_complex "[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.7[amb];\
[2:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[chi];\
[4:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[sfx];\
$VOZ_F;\
[amb][chi][sfx]amix=inputs=3:duration=first:dropout_transition=2:weights=1 1 1[bed];\
[bed][voz1]sidechaincompress=threshold=0.05:ratio=2.2:attack=20:release=250:makeup=1:knee=4[bedd];\
[bedd][voz2]amix=inputs=2:duration=first:dropout_transition=2:weights=0.8 1.15,\
loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart \
  "$OUTFILE"
echo "OK $OUTFILE"
