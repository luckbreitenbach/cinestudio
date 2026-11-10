# AVISOS À POPULAÇÃO · Aviso nº 3 "Sirene" · Prompts finais (Direção visual)

Gerado em 10/11/2026 (horário de Brasília) só com GenerateImage/GenerateVideo (uso incluso) + ffmpeg/Pillow locais. Clipes 720x1280, 9:16. As refs do estúdio, da barragem, da fachada e do rádio na cozinha estão em `avisos-ep02-prompts.md`.

## Referência nova

### ref-hall-sombra-pes.png · 1 geração (ref: ref-cozinha-azulejo-verde.png)
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), no people, no text, no letters, no numbers, no watermark. Entrance hall of a modest 1980s Brazilian house seen from inside at night, almost completely dark. A closed plain dark wooden front door, centered, on a simple tiled floor. Under the door, a thin horizontal strip of warm yellow streetlight leaks in across the floor. In the middle of that strip of light, two dark shadows interrupt it: the clear shadows of two feet standing perfectly still just outside the door. Nothing else is lit. A small piece of the green tile wall at the side. Eerie, static, minimal composition.
> Ressalva: as sombras saem compridas pra dentro do hall (como pernas projetadas pela luz baixa), mais que "pés" na faixa. Lê bem como alguém parado do lado de fora.

### aux-praca-frame-ep01p04.png
Quadro em t=0,3s do ep01/plano-04.mp4 (praça), usado como 1º quadro do plano 6, pra manter a mesma praça.

### cartela-aviso-03.png
`python3 tools/compor_cartela.py 3 "LEIA COM\nATENÇÃO" ../cartela-aviso-03.png`

## Clipes (05-cenas/avisos-ep03/)

### Plano 01 (11s) · 1 geração · reference: ref-rua-das-paineiras.png
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty planned small town, no visible faces, no text... Night. Camera placed right at ground level on the wet asphalt of the empty street from <IMAGE_0>, as if lying on the road: rough wet asphalt texture fills the foreground, a still puddle reflects the warm yellow light of a street lamp, the row of identical houses and trees blurred in the background. Tiny drops fall into the puddle making small ripples. Very slow mechanical push-in toward the puddle. No people, no body, no feet in frame. Ambient sound: dripping water, faint AM radio hiss. No music.

### Plano 02 (8s) · reaproveitado · ep01/plano-02.mp4 + 3s congelados com grão
A Edição sobrepõe `cartela-aviso-03.png`.

### Plano 03 (6s) · 1 geração + correção · reference: ref-fachada-41-dia.png
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty planned small town, no visible faces, no text... Static tripod shot by day of the same house as in <IMAGE_0>: grey fibre-cement roof, pale wall, low front wall with small iron gate, kitchen window closed by a white lace curtain. On the doorstep in front of the closed front door, many unopened glass milk bottles full of milk and several rolled-up newspapers tied with string have piled up, untouched for days. Nothing moves. No people. Ambient sound: quiet daytime silence, faint AM hiss. No music, no labels, no printed text on bottles or newspapers.
> Os jornais vieram com pseudo-texto e foto impressos. Final = bruto (`alternativas/plano-03-bruto-jornal-com-pseudotexto.mp4`) + desfoque gaussiano (sigma 2,6) com máscara suave só sobre os jornais (ffmpeg).

### Plano 04 (6s) · 1 geração · reference: ref-fachada-41-dia.png
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty planned small town... Daytime, flat overcast light. Close view of a neighbor's low concrete front wall and a small closed iron gate, identical to the wall and gate in <IMAGE_0>. Behind the wall, in the yard, a clothesline with white sheets and shirts hanging perfectly still, no wind at all. Slow steady pan along the wall. No people, no animals. Ambient sound: silence, faint AM hiss. No music.

### Plano 05 (6s) · reaproveitado · ep02/alternativas/plano-10-bruto-6s.mp4 (barragem com sirene, inteiro)

### Plano 06 (6s) · 1 geração · image-to-video: aux-praca-frame-ep01p04.png
Static tripod shot of the empty town square at dusk with long hard shadows. The clock post, bandstand and still clothesline do not move. Very far away in the background, beyond the bandstand, a few tiny human silhouettes seen only from behind slowly walk away toward the houses, small dark shapes, no details, never turning around. Faded sepia-green 1970s–1980s archival 16mm film look, film grain, dust, slight gate weave, deep noir shadows. Ambient sound: quiet, faint AM hiss, one short chime of the square clock bell. No music, no text, no numbers.

### Plano 07 (5s) · 1 geração · image-to-video: aux-radio-cozinha.png
A quick short mechanical zoom-in toward the glowing amber tuning dial of the old wooden radio on the kitchen shelf, then holding close on the dial as its glow flickers and trembles. Faded sepia-green 1970s–1980s archival 16mm film look, film grain, dust, slight gate weave, deep noir shadows. No people. Ambient sound: radio dial whistle, AM static, a distant muffled calm female voice. No music, no text, no numbers.

### Plano 08 (7s) · sem geração de vídeo · ref-hall-sombra-pes.png → `tools/still_para_filme.sh ... 7 1.0 1.0`
Plano fixo: grão, gate weave, flicker leve de luz e chiado AM sintetizado. A sombra dos pés fica garantidamente imóvel (lição do nº 1: não depender do modelo pra manter um elemento parado).

### Plano 09 (6s) · 2 gerações · reference: ref-estudio-radio-cardiga.png
v1 (`alternativas/plano-09-v1-perfil.mp4`, image-to-video da ref): Static tripod shot. The out-of-focus man in the brown cardigan, always seen strictly from behind, slowly leans back in his chair, moving his head and shoulders away from the microphone, and then stays still, sitting farther back, never turning his head; his face is never visible. The microphone stands alone in focus under the steady red bulb... Ambient sound: studio room tone, a chair creak, faint AM hiss. No music, no text.
> Descartada: a cabeça entra em foco e vira de perfil (orelha, bochecha e nariz).
v2 (final, enquadramento simplificado): 1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), no visible faces, no text... Static tripod shot of the radio studio from <IMAGE_0>: the old chrome microphone on its desk stand stands alone in sharp focus in the center, under the steady red wall bulb, with an empty gap of desk in front of it. At the far right edge of the frame, strongly out of focus, only the brown knitted cardigan back and one shoulder of a man sitting far back from the desk, leaning back in his chair; his head is cut off above the top edge of the frame, never visible. He stays almost still, a slow breath moves the shoulder. Ambient sound: studio room tone, faint AM hiss, a chair creak. No music.

### Plano 10 (6s) · reaproveitado · ep01/plano-08.mp4 (represa com luzes debaixo d'água) cortado nos 6s iniciais

### Plano 11 (1s) · reaproveitado · ep01/plano-11.mp4 acelerado 2x
