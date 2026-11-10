# Fitas da Serra · Ep. 01 · "A Figueira" — entrega de edição

## Saídas

| Arquivo | Uso |
|---------|-----|
| `fitas-da-serra-ep01_master.mp4` | Master 1080×1920 30fps H.264 High + AAC 48k (~92s) |
| `fitas-da-serra-ep01_tiktok.mp4` | Export TikTok |
| `fitas-da-serra-ep01_reels.mp4` | Export Instagram Reels |
| `fitas-da-serra-ep01_shorts.mp4` | Export YouTube Shorts |
| `stems/stem_ambiente_sfx.wav` | Stem ambiente + SFX (sem vozes) |
| `stems/stem_voz_placeholder.wav` | Silêncio com a mesma duração — substituir pela voz |
| `voice_timeline.json` | In/out de cada fala + metadados |
| `voice_timeline.edl` | EDL simples das falas |
| `remix_with_voice.sh` | Remixa vídeo+ambiente+voz sem remontar |
| `frames/check_*.png` | Frames de QC |
| `work/assemble_ep01.py` | Script da montagem |

Pipeline VHS reutilizado: `/workspace/cinestudio/06-videos/pipeline/`.

## Remix com voz

```bash
# Padrão: usa stem_voz_guia_piper.wav e gera master_com_voz
./remix_with_voice.sh

# Ou passe a faixa final (WaveNet/dublagem) e o nome de saída
./remix_with_voice.sh stems/stem_voz_final.wav fitas-da-serra-ep01_master_com_voz.mp4
```

O script mistura `stem_ambiente_sfx.wav` + voz com **ducking leve** do ambiente (sidechain) sobre o vídeo já legendado (`-c:v copy`). Timings em `voice_timeline.json`. Não sobrescreve os masters sem voz.

## Correções aplicadas nesta entrega

- **Plano 07:** fonte `alternativas/plano-07-v1-rosto-visivel.mp4`; rasgo/mancha gerado localmente cobrindo o rosto (rastreado pelo retângulo da foto); texto lápis **Benedito · 1931** (Patrick Hand, OFL).
- **Plano 06:** mancha humanóide na casca suavizada/escurecida (máscara elíptica + blur).
- **Plano 10:** sombras levantadas (gamma/curves) para a silhueta.
- **Plano 11:** exposição equalizada ao plano 10.
- Upscale lanczos 720×1280 → 1080×1920, 24→30 fps.

## Áudio

Só SFX CC0 (Freesound + BigSoundBank) listados em `04-prompts/fitas-da-serra-ep01-audio-opcoes.md`, mais hiss lavfi. Sem BBC. Masters sem voz (`*_master.mp4`, `*_tiktok.mp4`, etc.) permanecem só com ambiente+SFX + legendas. Registro: `../licencas-audio.csv`.

## Voz guia Piper (provisória)

Faixa guia gerada com **piper-tts** local (`bible/audio-tests/piper-venv`) e modelos CC0:

| Personagem | Modelo | Notas de guia |
|---|---|---|
| Marta | `pt_BR-jeff-medium` | voz masculina com pitch ↑ (~+3,5 semitons) — só guia |
| Tião | `pt_BR-cadu-medium` | grave, mais lento |
| Dudu | `pt_BR-jeff-medium` | mais rápido |
| Benedito | `pt_BR-cadu-medium` | pitch ↓, lento, leve aspereza |

Arquivos:
- `stems/stem_voz_guia_piper.wav` — faixa completa 48 kHz mono (~92,1 s)
- `stems/voz_guia/<id>.wav` — cada fala isolada (já com filtro de mic VHS)
- `fitas-da-serra-ep01_master_guia.mp4` + `_tiktok_guia` / `_reels_guia` / `_shorts_guia`
- Script de geração: `work/generate_voz_guia_piper.py`
- Relatório de encaixe/loudness: `work/voz_guia_report.json`

Filtro de mic VHS aplicado na voz: band-pass ~200–4500 Hz, compressão leve, saturação suave, eco curto de room. Mix com ducking leve do ambiente (`remix_with_voice.sh`).

### Trocar depois pela Google WaveNet (ou dublagem)

1. Gere as falas WaveNet (ou humanas) com os mesmos textos/timings de `voice_timeline.json`.
2. Salve cada clip em `stems/voz_guia/` (ou monte uma faixa 48 kHz da mesma duração).
3. Substitua `stems/stem_voz_guia_piper.wav` pela nova faixa (mesmo sample rate/duração).
4. Rode sem remontar o vídeo:

```bash
./remix_with_voice.sh stems/stem_voz_final.wav fitas-da-serra-ep01_master_com_voz.mp4
```

5. Reexporte TikTok/Reels/Shorts a partir do novo master com voz. Os arquivos `*_guia*` e o stem Piper podem ser arquivados.

Licenças dos modelos: MODEL_CARD local em `bible/audio-tests/voices/MODEL_CARD_{cadu,jeff}.md` e Hugging Face `rhasspy/piper-voices` — **CC0**. Runtime piper-tts é GPL-3.0-or-later (só a ferramenta; os WAV gerados a partir de modelos CC0 seguem o dataset CC0).
