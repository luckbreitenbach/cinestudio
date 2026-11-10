# AVISOS À POPULAÇÃO · Aviso nº 2 · "Contagem" (guia)

Montagem completa com voz guia sintética local (Kokoro). **Não publicado.**

## Saídas

| Arquivo | Papel |
|---|---|
| `avisos-ep02_master_guia.mp4` | Master 1080×1920, 30 fps, 68,0 s |
| `avisos-ep02_tiktok_guia.mp4` | Export TikTok |
| `avisos-ep02_reels_guia.mp4` | Export Reels |
| `avisos-ep02_shorts_guia.mp4` | Export Shorts |
| `stems/` | Ambiente, chiado AM, SFX, voz seca, voz com filtro, mix |
| `stems/voz_guia/` | Falas avulsas (`*_dry.wav` e `*_filt.wav`) |
| `audio/` | SFX isolados (vinheta, clique, rangido, dial, sirene) |
| `frames/check_*.png` | Quadros de checagem |
| `remix_with_voice.sh` | Troca a faixa de voz sem remontar a imagem |
| `work/video_film_subs_silent.mp4` | Imagem + legendas, sem áudio (entrada do remix) |

## Voz guia

- **Osvaldo:** Kokoro `pm_alex`, filtro AM (300–3400 Hz; no estúdio, p8, um pouco mais aberto: 220–4200 Hz). "Boa noite, Vila Aurora." da correção (após "Neide") está 0,78× mais baixo.
- **Interferência:** Kokoro `pf_dora`, filtro abafado (450–2200 Hz).
- Licença do modelo e do voicepack: **Apache-2.0**. O treino do Kokoro inclui Koniwa (CC BY 3.0) e SIWIS (CC BY 4.0) — atribuição exigida. Arquivos em `fonts/licenses/` (Apache-2.0-Kokoro.txt, MIT-kokoro-onnx.txt). Registrado em `../licencas-audio.csv`.
- **Atempo nunca acima de 1,1×.** Quase todas as falas cabem na velocidade nativa 0,86–0,92. Dois atempos leves: `osv_2a` 1,033× e `osv_6b` 1,020×. Três falas que não cabiam no slot com folga do roteiro foram regeneradas no speed natural e deslocadas dentro do respiro (sem cortar palavras):
  - `osv_2c` "Número dois." — in 14,80 s (pausa 0,4 s após 2b), out 15,90 s (folga 0,10 s até o plano 3).
  - `osv_3d` "A Prefeitura parabeniza a família." — out 29,38 s; pausa seguinte 0,62 s (o roteiro pedia 1,2 s).
  - `osv_6a` "A Prefeitura agradece a colaboração." — out 54,60 s; pausa até "Neide" 0,40 s (o roteiro pedia 0,6 s).
- Também: pausa entre `osv_3b` e `osv_3c` ficou em 0,30 s (o roteiro pedia 1,0 s) para não atrasar a cartela de 0:24 nem invadir o plano.

## Sincronia voz / legenda

Desvio = início da fala − início da legenda correspondente. Teto ~100 ms. Nenhuma fala invade a cartela seguinte nem o plano seguinte.

| id | in voz | in legenda | desvio | out voz | ok? |
|---|---:|---:|---:|---:|---|
| osv_1a | 0,000 | 0,00 | 0 ms | 2,104 | sim |
| osv_1b | 3,000 | 3,00 | 0 ms | 4,419 | sim |
| osv_1c | 6,000 | 6,00 | 0 ms | 7,903 | sim |
| osv_2a | 10,000 | 10,00 | 0 ms | 11,710 | sim |
| osv_2b | 12,100 | (suprimida: a cartela já mostra o aviso) | — | 14,387 | — |
| osv_2c | 14,799 | (suprimida, idem) | — | 15,898 | — |
| osv_3a | 16,000 | 16,00 | 0 ms | 20,057 | sim |
| osv_3b | 21,000 | 21,00 | 0 ms | 23,703 | sim |
| osv_3c | 24,000 | 24,00 | 0 ms | 25,734 | sim |
| osv_3d | 27,000 | 27,00 | 0 ms | 29,378 | sim |
| osv_4a | 30,000 | 30,00 | 0 ms | 33,501 | sim |
| osv_4b | 35,000 | 35,00 | 0 ms | 37,564 | sim (ajustado de 35,30) |
| osv_4c | 39,000 | 39,00 | 0 ms | 41,379 | sim |
| osv_5a | 43,000 | 43,00 | 0 ms | 47,180 | sim |
| osv_5b | 49,000 | 49,00 | 0 ms | 50,702 | sim |
| osv_6a | 52,000 | 52,00 | 0 ms | 54,602 | sim |
| osv_6b | 55,000 | 55,00 | 0 ms | 56,510 | sim |
| osv_6c | 57,000 | 57,00 | 0 ms | 58,766 | sim |
| int_1 | 60,000 | 60,00 | 0 ms | 61,482 | sim |
| int_2 | 63,000 | 63,00 | 0 ms | 65,497 | sim |

A legenda "Aviso à população número dois. Número dois." foi **suprimida** durante a cartela, que já traz "AVISO À POPULAÇÃO Nº 2". "Boa noite, Vila Aurora." foi deslocada para a esquerda do carimbo "LEIA COM ATENÇÃO" (não cruza o carimbo nem o Nº 2). Carimbo detectado em y=1401–1715, x=548–1002 (1080×1920).

## Áudio / loudness

- Alvo: ≈ **−14 LUFS** integrados, teto **−1 dBTP**.
- Medição EBU R 128 (`ebur128=peak=true`) no master: **I = −14,2 LUFS**, **TP = −1,6 dBTP**, **LRA = 4,2 LU**.
- Normalização em duas passagens (`loudnorm` linear) + atenuação residual de −0,10 dB, sem o auto-level do `alimiter` (ele re-entregava o pico).
- Rangido de madeira em **0:50,822** (logo após "ocupada", ~0:49 do roteiro).
- Sirene grave de barragem (arquivo-assinatura em `audio/sirene-barragem.wav` e `06-videos/avisos-shared/`) entra longe em **1:04** e **corta seco em 1:07**.
- Assobio de dial em 0:58,95. Vinheta de vibrafone + clique de projetor em 0:09.
- Todo o SFX foi sintetizado localmente (numpy) e está em `../licencas-audio.csv`. Sem música de terceiros.

## Imagem

Look Super-8/16 mm do `film_pipeline.py` (sépia-oliva corrigido, sem magenta): grain, poeira, weave de projetor, flicker, vinheta. 1080×1920, 30 fps, upscale lanczos.

Ajustes da Direção:

- **p3:** clareado (exposição ↑, contraste ↓, curvas) para ler como dia. Os postes ainda têm um brilho residual — o céu e a rua já leem como dia encoberto.
- **p7:** quatro silhuetas sentadas, sem figura de pé; rangido depois de "ocupada".
- **p8:** as mãos entram no bruto por volta de 3,0 s (antes dos ~5 s estimados no QC). O plano foi cortado em **2,60 s** e o último quadro limpo (só ombro/nuca fora de foco) foi segurado com `tpad` até completar os 7 s. Frames de checagem no hold confirmam: mãos não aparecem.
- **p2:** cartela oficial com entrada de slide e tremor de projetor.
- **p4:** "Rua das Paineiras, 41" composto (PT Serif creme), acima da zona de legenda.
- **p6:** dessaturação extra no giz, para não destoar.
- **p9:** "AM 870" em letterpress no mostrador, com tracking.

Fontes: PT Serif e Oswald, OFL (cópias das licenças em `fonts/licenses/`).

## Remix da voz

```bash
./remix_with_voice.sh                         # usa stems/stem_voz_guia_kokoro.wav
./remix_with_voice.sh stems/stem_voz_final.wav avisos-ep02_master_com_voz.mp4
./remix_with_voice.sh stems/stem_voz_dry.wav  avisos-ep02_master_com_voz.mp4 --am
```

O script aplica ducking e um `loudnorm` de uma passagem. **Depois da troca, confira o true peak** (o AAC pode estourar o teto; o master final desta pasta foi normalizado em duas passagens + trim, I=−14,2 / TP=−1,6). Se o pico passar de −1 dBTP, atenue o WAV (sem `alimiter` com auto-level) e remuxe com `-c:v copy`.

## Pontos fracos (honestos)

- No p3 os postes continuam discretamente acesos; o clareamento lê "dia", mas não apaga as lâmpadas.
- A pausa depois de "conforme previsto" e a pausa depois de "parabeniza a família" ficaram mais curtas que o roteiro (0,30 s e 0,62 s) para não invadir o plano seguinte.
- O hold do p8 (2,6–7,0 s) é um quadro congelado com o tremor/grão do look filme por cima — o push-in para no corte.
- A sirene de 1:04–1:07 é propositalmente baixa (muito longe); no telemóvel pode quase não se perceber. No nº 3 ela entra como assinatura a pleno.

## Melhores frames de checagem

- `frames/check_p03_dia.png` — rua lendo como dia, look oliva
- `frames/check_leg_cartela_boa_noite.png` — legenda à esquerda do carimbo
- `frames/check_p04_fachada_41.png` — endereço e legenda sem colisão
- `frames/check_p08_hold_sem_maos.png` — estúdio, sem mãos
- `frames/check_p09_am870.png` — AM 870 no mostrador
- `frames/check_p07_silhuetas.png` — quatro silhuetas à mesa
- `frames/check_p10_barragem.png` — torre da sirene, interferência em itálico
- `frames/check_p01_mesa.png` — gancho, plongée da mesa
