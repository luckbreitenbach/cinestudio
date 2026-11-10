#!/bin/bash
# Transforma um still 720x1280 num clipe "de arquivo" (grão, gate weave, flicker, vinheta) + chiado AM sintetizado.
# uso: still_para_filme.sh entrada.png saida.mp4 duracao zoom_final(1.0=fixo) saturacao
in=$1; out=$2; d=$3; z=${4:-1.0}; sat=${5:-1.0}; fr=$((d*24))
ffmpeg -v error -y -loop 1 -i "$in" -f lavfi -i "anoisesrc=c=pink:a=0.02:d=$d" -f lavfi -i "sine=f=60:d=$d" -filter_complex "\
[0:v]scale=1440:2560,zoompan=z='1+($z-1)*on/$fr':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$fr:s=736x1308:fps=24,\
crop=720:1280:'8+3*sin(t*9)+2*sin(t*23)':'14+3*cos(t*7)+2*sin(t*19)',\
eq=saturation=$sat:brightness='0.015*sin(t*31)+0.01*sin(t*13)':eval=frame,noise=alls=10:allf=t,vignette=PI/5,format=yuv420p[v];\
[2:a]volume=0.03[h];[1:a][h]amix=inputs=2:normalize=0,lowpass=f=3400,highpass=f=300[a]" \
-map "[v]" -map "[a]" -t $d -c:v libx264 -crf 17 -c:a aac -b:a 128k "$out"
