# AVISOS À POPULAÇÃO · Aviso nº 2 "Contagem" · Prompts finais (Direção visual)

Gerado em 10/11/2026 (horário de Brasília) só com GenerateImage/GenerateVideo (uso incluso) + ffmpeg/Pillow locais. Clipes 720x1280, 9:16, com som ambiente da ferramenta ou chiado sintetizado (sem música de terceiros).
Prefixo (`estetica.md`) usado em todos os prompts de geração "do zero"; nos image-to-video, uma versão curta dele (o 1º quadro já carrega o estilo).

## Referências novas (bible/avisos-a-populacao/)

### ref-estudio-radio-cardiga.png · 2 gerações + correção em Pillow
v1 (`alternativas/ref-estudio-radio-cardiga-v1-orelha.png`, refs: ref-radio-am870.png): 1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), no visible faces, no text, no letters, no numbers, no watermark. Small municipal radio station studio at night, 1987: wooden announcer desk with an old chrome ribbon microphone on a desk stand, a simple mixing console with round knobs and no labels, acoustic-tile wall panels, a plain glowing red light bulb in a small wall fixture (no sign, no lettering). In the foreground, very close to the camera and out of focus, a man seen strictly from BEHIND: only his shoulder, back of neck and short grey hair, wearing a brown knitted cardigan, sitting at the desk facing the microphone. His face is completely hidden. The red bulb and one desk lamp are the only light; deep black shadows. No text, no labels, no logos.
> Orelha e borda da bochecha visíveis, e o homem nítido.
v2 (`alternativas/ref-estudio-radio-cardiga-v2-bruta.png`, ref: v1): mesmo cenário + "In the right foreground, very close to the lens and strongly OUT OF FOCUS (soft blurry shape), a man seen from DIRECTLY BEHIND: only the back of his head with short grey hair and his shoulders in a brown knitted cardigan. No ear, no cheek, no profile visible at all..."
> Saiu quase igual à v1. Final = v2 + desfoque gaussiano com máscara suave sobre o homem + sombra sobre orelha e bochecha + grão novo (Pillow).

### ref-barragem-torre-sirene.png · 2 gerações
v1 (`alternativas/ref-barragem-torre-sirene-v1-antena.png`, ref: ref-represa.png): 1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty, no people... A concrete hydroelectric dam at dusk seen from below at an angle, backlit against a pale washed-out sky. On top of the dam stands a tall slender steel lattice tower with a large old round civil-defense siren horn at its top, a pure black silhouette against the sky. Below, the reservoir water is flat, smooth and dark like glass... Strong contre-jour, deep black shadows. No signs, no lettering.
> A sirene saiu como antena parabólica.
v2 (final, ref: v1): ...tall thin steel pole tower carrying an old 1950s air-raid civil-defense siren at its top: a cylindrical motor siren with several short flared trumpet horns pointing outward like a flower (NOT a dish, NOT an antenna). The tower and siren are a pure black silhouette against a pale washed-out evening sky, backlit. Reflection in the still water...
> Ressalva: o reflexo na água corta antes do topo da torre.

### ref-fachada-41-dia.png · 1 geração (ref: ref-rua-das-paineiras.png)
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty planned small town, no people, no text... Daytime, flat overcast institutional light. Frontal view from the sidewalk of one modest single-story house identical to those in the street reference: grey corrugated fibre-cement roof, pale painted wall, a low front wall with a small closed iron gate, a tiny front step / doorstep by the front door. The kitchen window is closed from inside by a white lace curtain. Symmetric, postcard-like, too quiet. No house number, no signs.

### aux-ep02-desenho-geladeira.png · 1 geração
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir)... Close-up of a child's crayon drawing on white paper held on an old pale refrigerator door by a round magnet. The drawing: a simple family of four faceless stick figures (blank round heads with NO eyes, NO mouth, no facial features at all) in bright crayon colors standing in a row on green grass under a yellow sun, and between them one taller grey stick figure, also with a completely blank featureless head, slightly longer arms. No writing, no names, no letters on the drawing. Hard single light from the side, kitchen in shadow.
> Saíram 3 bonecos coloridos + o cinza (não 4 + cinza), todos sem rosto.

### aux-radio-cozinha.png · 1 geração (refs: ref-radio-am870.png, ref-cozinha-azulejo-verde.png)
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir)... The same old wooden tabletop radio as in <image 1> (... glowing amber tuning dial with plain tick marks and red needle, no numbers) now standing on a small wooden shelf in the corner of the kitchen with the green square ceramic tile wall from <image 2>. Night, the amber dial is the main light, deep shadows.

### cartela-aviso-02.png
`python3 tools/compor_cartela.py 2 "LEIA COM\nATENÇÃO" ../cartela-aviso-02.png` (o carimbo só muda a partir do Aviso 4).

## Clipes (05-cenas/avisos-ep02/)

### Plano 01 (9s) · 1 geração · reference: ref-cozinha-azulejo-verde.png
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty planned small town, no visible faces, no text, no letters, no numbers, no watermark. Top-down overhead shot (plongée) looking straight down at a dinner table in the kitchen from <IMAGE_0>: white crochet tablecloth, many white porcelain plates all served with rice, beans and meat, glasses, serving dishes, steam rising gently from the food. No people, no hands, nobody in frame. One hard lamp light from above, dark edges. Very slow mechanical push-in from above toward the table. Only the steam moves. Ambient sound: faint AM radio hiss and distant cutlery clinks. No music.

### Plano 02 (7s) · reaproveitado · ep01/plano-02.mp4 (slide sem texto) + 2s de quadro congelado com grão (ffmpeg tpad + noise)
A Edição sobrepõe `bible/avisos-a-populacao/cartela-aviso-02.png`.

### Plano 03 (7s) · 1 geração · reference: ref-rua-das-paineiras.png + ref-fachada-41-dia.png
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty planned small town... Daytime, flat overcast light. The empty street from <IMAGE_0> by day: a row of identical small single-story houses with grey corrugated fibre-cement roofs and low front walls like the house in <IMAGE_1>, big trees along the sidewalk, street lamps. In one front yard a clothesline with white sheets and shirts hanging perfectly still, no wind at all. No people, no cars, no animals. Slow steady institutional pan across the houses. Ambient sound: silence, faint AM radio hiss. No music.

### Plano 04 (7s) · 1 geração · image-to-video: ref-fachada-41-dia.png
Static tripod shot, the house facade stays perfectly still. Nothing moves except very faint film grain, dust, slight gate weave and a barely perceptible breath of the lace curtain behind the closed window glass. Faded sepia-green 1970s–1980s Brazilian municipal archival 16mm film look, soft vignette, flat overcast daylight. No people, no cars. Ambient sound: quiet daytime silence, faint AM radio hiss. No music, no text, no numbers.

### Plano 05 (7s) · 1 geração · reference: ref-cozinha-azulejo-verde.png
1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), no visible faces, no text... Static close shot on the white crochet tablecloth from <IMAGE_0>: a row of plain glass tumblers filled with dark fizzy soda, bubbles rising, and in the middle of them one identical glass filled with murky, cloudy, dark greenish-brown water like water from the bottom of a reservoir, perfectly still, with tiny particles suspended. Hard single side light, deep shadows behind. No people, no hands, no bottles, no labels. Ambient sound: faint soda fizz and AM radio hiss. No music.

### Plano 06 (6s) · sem geração de vídeo · aux-ep02-desenho-geladeira.png → `tools/still_para_filme.sh ... 6 1.12 0.55`
Push-in de 12%, saturação 0,55 pra puxar o giz pro sépia, grão, gate weave, flicker e chiado AM sintetizado. Plano de elemento estático: assim não há risco de o modelo desenhar rostos nem mexer na figura cinza.

### Plano 07 (9s) · reaproveitado · ep01/alternativas/plano-10-v2-bruto.mp4 (fachada à noite, vidro fosco, 4 silhuetas sentadas, sem a figura de pé) desacelerado 1,5x (setpts/atempo)

### Plano 08 (7s) · 1 geração · image-to-video: ref-estudio-radio-cardiga.png
Very slow steady mechanical push-in toward the microphone on the desk, past the blurred out-of-focus shoulder and back of the head of the man in the brown cardigan in the foreground. The man stays completely still, always seen from behind, he never turns his head; his face is never visible. The red bulb on the wall glows steadily. Faded sepia-green 1970s–1980s archival 16mm film look, film grain, dust, slight gate weave, deep noir shadows. Ambient sound: quiet studio room tone, a calm low male breath close to the microphone, faint AM hiss. No music, no text, no letters.

### Plano 09 (3s) · 1 geração · image-to-video: aux-radio-cozinha.png
Static tripod shot. The amber tuning dial of the old wooden radio on the kitchen shelf flickers and trembles irregularly, the glow pulsing dim and bright as if the signal is being disturbed; the light flickers on the green tiles. Nothing else moves. Faded sepia-green 1970s–1980s archival 16mm film look, film grain, dust, slight gate weave, deep noir shadows. No people. Ambient sound: a radio dial whistle and rising AM static. No music, no text, no numbers.

### Plano 10 (5s) · 1 geração (6s, também usada no ep03 plano 5) · image-to-video: ref-barragem-torre-sirene.png · cortada nos 5s iniciais
Static tripod shot, backlit. The dam and the siren tower stay perfectly still as a black silhouette against the pale evening sky; the smooth reservoir below barely ripples, the reflection trembles slightly. Faded sepia-green 1970s–1980s archival 16mm film look, film grain, dust, slight gate weave, deep noir shadows. No people, no birds. Ambient sound: still water, wind, and very far away the first low deep tone of a siren starting to rise. No music, no text.
Bruto de 6s em `alternativas/plano-10-bruto-6s.mp4`.

### Plano 11 (1s) · reaproveitado · ep01/plano-11.mp4 acelerado 2x (flash, perfuração, preto)
