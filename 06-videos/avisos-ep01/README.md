# AVISOS À POPULAÇÃO · Aviso nº 1 · "A cadeira virada" — entrega de edição

Episódio completo (~66 s), vertical 9:16, 1080×1920 30 fps, look Super-8/16 mm (não é VHS). Voz guia sintética local. Nada foi publicado.

## Saídas

| Arquivo | Uso |
|---------|-----|
| `avisos-ep01_master_guia.mp4` | Master com voz guia, legendas e look filme |
| `avisos-ep01_tiktok_guia.mp4` | Export TikTok |
| `avisos-ep01_reels_guia.mp4` | Export Instagram Reels |
| `avisos-ep01_shorts_guia.mp4` | Export YouTube Shorts |
| `stems/stem_voz_guia.wav` | Alias da faixa de voz com filtro AM (cópia de `stem_voz_guia_kokoro.wav`) |
| `stems/stem_voz_guia_kokoro.wav` | Faixa de voz (já com filtro AM) 48 kHz, 66 s |
| `stems/stem_voz_guia_dry.wav` | Voz sem filtro AM (para remaster) |
| `stems/voz_guia/` | Cada fala isolada (`*_dry.wav` + versão filtrada) |
| `stems/stem_ambiente.wav` | Ambiente dos clipes (p7 quase mudo, sem o murmúrio) |
| `stems/stem_am_chiado.wav` | Chiado AM + hum 60 Hz (gerado localmente) |
| `stems/stem_sfx_vinheta.wav` | Vinheta, cliques, clacs, rangido, assobio, queima |
| `remix_with_voice.sh` | Remixa vídeo legendado + stems + nova voz, sem remontar a imagem |
| `audio/` | SFX isolados (vinheta, clacs, projetor, rangido, assobio, queima, chiado AM) — gerados localmente |
| `frames/check_*.png` | Quadros de QC |
| `work/film_pipeline` / `../pipeline/scripts/film_pipeline.py` | Preset `film` (sépia-esverdeado, grão, tremor, flicker, vinheta — sem REC/timestamp) |

Cópias das plataformas também em `exports/`.

## Voz guia (provisória)

Testados: Kokoro `pm_santa`, `pm_alex` e (não usados) Piper `cadu` / `faber`.

- **Osvaldo:** Kokoro **`pm_alex`** (pt-BR), ritmo lento, filtro AM (300–3400 Hz, compressão, saturação). No plano 7 a voz passa por um filtro de alto-falante (mais fechado, ressonância de caixa). Escolhido por ser mais grave que `pm_santa` (f0 ~140 Hz vs ~178 Hz no trecho de teste).
- **Interferência:** Kokoro **`pf_dora`**, filtro mais abafado (450–2200 Hz) e atraso leve (~40 ms).

**Licenças (confirmadas localmente + páginas oficiais):**
- Modelo e voicepack Kokoro v1.0: **Apache-2.0** (`hexgrad/Kokoro-82M`; runtime `kokoro-onnx` é MIT). O treino do modelo inclui áudio **CC BY 3.0 Koniwa** e **CC BY 4.0 SIWIS** — atribuição no CSV.
- **Piper `faber` NÃO foi usado:** o MODEL_CARD diz fine-tune da voz inglesa *lessac*, cuja base Blizzard 2013 é licença **somente pesquisa / uso comercial proibido**.

### Trocar depois pelo Gemini / Google WaveNet

1. Gere as falas com os textos e timings de `work/voice_timeline_guia.json` (e o roteiro em `03-roteiros/avisos-ep01.md`).
2. Monte uma faixa 48 kHz da mesma duração (66 s), ou substitua os clips em `stems/voz_guia/`.
3. Remixe sem remontar o vídeo:

```bash
# se a faixa nova estiver "dry" (sem AM):
./remix_with_voice.sh stems/stem_voz_final.wav avisos-ep01_master_com_voz.mp4 --am

# se você já aplicou o filtro AM:
./remix_with_voice.sh stems/stem_voz_final.wav avisos-ep01_master_com_voz.mp4
```

## Legendas e fontes

Legendas em **PT Serif** (SIL OFL), creme com sombra, discretas, no máximo 2 linhas; interferência em itálico. Cartela oficial (`bible/avisos-a-populacao/cartela-aviso-01.png`) composta com Courier Prime, Noto Serif Display e Oswald (SIL OFL). "AM 870" no mostrador: Oswald Medium (OFL). Licenças em `fonts/licenses/`.

## Som

Sem música de terceiros. Vinheta de vibrafone (3 notas + tom de prefixo; no fim, desafinada e descendente) sintetizada neste computador. SFX de projetor, clacs, rangido, assobio de dial e queima também gerados localmente. Registro em `../licencas-audio.csv`.

## O que a edição corrige (sem gerar clipes novos)

- **p1:** janela escurecida (máscara de vidro + curvas), para não parecer dia.
- **p2:** cartela oficial com entrada de slide e tremor de projetor.
- **p4 e p10:** pulo de quadro reforçado na edição.
- **p5:** corte mais fechado na cadeira/azulejo e um giro sutil (~1,7°) a partir de ~4,4 s. A cadeira **continua de frente** (encosto no azulejo); isso só se resolve com clipe novo.
- **p6:** clacs em 2,0 s e 3,6 s do plano.
- **p7:** murmúrio da ferramenta removido; voz do Osvaldo no alto-falante; "AM 870" composto no mostrador, acompanhando o push-in.
- **p9:** cartela íntegra até 2 s; depois queima de película gerada em código.
- **p10:** grão extra na figura de pé / vidro, para casar com o filme.

Pipeline de look: `/workspace/cinestudio/06-videos/pipeline/scripts/film_pipeline.py`.


## Notas de QC (remontagem da cor e correções pontuais)

O look inicial do preset saiu magenta/arroxeado no material de origem. O master foi reexportado com uma correção sépia-esverdeada no concat; o áudio não foi remixado (mesmo loudness). O preset em `pipeline/scripts/film_pipeline.py` foi reforçado para rendições futuras.

Também refeitos só o que não convencia nos frames:

- **p7:** o detector do mostrador pegava o reflexo quente da prateleira no plano aberto; o "AM 870" agora acompanha o visor âmbar do início ao close.
- **p9:** queima com anel de brasa/carbonização (antes o buraco era branco demais).

`remix_with_voice.sh` foi corrigido (`asplit` na voz, para o duck e o mix). Teste a seco em `/tmp` concluído com 66 s, vídeo copy + AAC 192 k. Uso:

```bash
./remix_with_voice.sh stems/stem_voz_guia.wav avisos-ep01_master_com_voz.mp4
./remix_with_voice.sh stems/stem_voz_guia_dry.wav avisos-ep01_master_com_voz.mp4 --am
```

Nada foi publicado.
