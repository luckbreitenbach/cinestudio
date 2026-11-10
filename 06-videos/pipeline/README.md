# Pipeline VHS — Fitas da Serra · Ep. 01

Editor do Cinestudio AI. Aplica textura VHS 9:16 (1080×1920), overlays de câmera, efeitos de corte, cartelas, legendas queimadas e exporta para TikTok, Instagram Reels e YouTube Shorts.

## Estrutura

```
06-videos/pipeline/
├── README.md
├── LICENCAS.md
├── fonts/                 # VT323 + Share Tech Mono (OFL) + DejaVu; licenças em fonts/licenses/
├── config/
│   ├── planos.json        # hora inicial + modo REC/PLAY por plano
│   ├── export-presets.json
│   ├── legendas-ep01.ass  # legendas do episódio completo
│   └── legendas-preview.ass
├── scripts/
│   ├── vhs_pipeline.py    # orquestrador principal
│   ├── build_preview.sh
│   └── export_platforms.sh
├── assets/cartelas/       # cartelas geradas (azul / pretas / FX)
├── test-clips/            # lavfi (só para teste)
├── preview/               # master + 3 exports + frames de verificação
└── exports/               # cópias das exportações
```

## Dependências

- ffmpeg 7.1+ com libx264, libass, drawtext, chromashift, noise, geq
- Python 3.11+
- Fontes em `fonts/` (já incluídas com arquivos de licença)

## Uso rápido

### Preview de teste (clipes lavfi)

```bash
cd /workspace/cinestudio/06-videos/pipeline
./scripts/build_preview.sh
# ou: python3 scripts/vhs_pipeline.py preview
```

Saídas: `preview/preview-teste_master.mp4`, `preview/preview-teste_{tiktok,reels,shorts}.mp4`, frames em `preview/frames/`.

### Aplicar VHS + OSD a um clipe real

```bash
python3 scripts/vhs_pipeline.py apply \
  -i /workspace/cinestudio/05-cenas/fitas-da-serra-ep01/plano-03.mp4 \
  -o /tmp/plano-03_vhs.mp4 \
  --start-tc 17:42:00 \
  --mode REC \
  --date "AGO 14 1994"
```

Parâmetros:
- `--start-tc` — hora inicial do plano (`HH:MM:SS`); o relógio corre com o tempo do clipe
- `--mode` — `REC` ou `PLAY`
- `--date` — rótulo da data no OSD (padrão `AGO 14 1994`)
- `--strength` — intensidade do look VHS (0.2–2.0, padrão 1.0)
- `--duration` — cortar saída em N segundos (opcional)

Cartelas de emissora usam look suave (`soft_look`) para não esmagar o azul VHS.

### Gerar cartelas e FX

```bash
python3 scripts/vhs_pipeline.py cartelas
```

### Exportar master para as 3 plataformas

```bash
./scripts/export_platforms.sh preview/preview-teste_master.mp4 preview-teste
# ou: python3 scripts/vhs_pipeline.py export -i MASTER.mp4 --stem fitas-da-serra-ep01
```

## Trocar clipes de teste pelos reais

1. Direção gera os planos em `/workspace/cinestudio/05-cenas/fitas-da-serra-ep01/` com nomes alinhados a `config/planos.json` (`plano-01.mp4` … `plano-13.mp4`).
2. Para cada plano, rode `apply` com o `inicio_timecode` e `modo` do JSON.
3. Monte a timeline (concat) na ordem do roteiro, inserindo:
   - `fx-glitch-tracking` entre gancho → cartela azul
   - cartela azul (plano 2)
   - `rewind` antes do plano 9 (playback)
   - tela azul VHS antes das cartelas finais
   - cartelas pretas finais (textos do roteiro)
4. Queime `config/legendas-ep01.ass` (ASS com `fontsdir=fonts/`).
5. Exporte com `export`.

O `planos.json` é a fonte de verdade para hora/modo; o preview atual monta uma versão enxuta (~20s) só para validar o look.

## Look VHS (filtros)

- Escala/pad 1080×1920 · 30 fps · yuv420p
- Saturação baixa, contraste ↑, pretos esmagados (`eq` + `curves`)
- Chroma bleed (`chromashift` + reforço de Cr nos vermelhos via `geq`)
- Grão forte (`noise`)
- Wobble leve (`crop` animado com seno)
- Linhas de tracking periódicas (`geq`)
- Vinheta leve
- OSD: `REC ●` / `▶ PLAY` (canto superior esquerdo) e `AGO 14 1994 HH:MM:SS` (canto inferior direito)
  - Texto: **VT323** (OFL)
  - Símbolos ● e ▶: **DejaVu Sans** (licença livre) — VT323 não tem esses glifos

## Legendas

Preferência do Lucas: **frases curtas, discretas e cinematográficas** (não palavra a palavra; não texto gigante). Branco com caixa preta semitransparente (`BorderStyle=3`), fonte ~36px, no máximo **2 linhas**, posicionadas acima da faixa do timestamp (`MarginV=300` em 1920 de altura).

## Zonas seguras de UI (9:16)

Documentadas em `config/export-presets.json`:

| Região | px (aprox.) | Motivo |
|--------|-------------|--------|
| Topo | 180 | username / botões |
| Base | 280 | legendas nativas / CTA |
| Laterais | 60 | UI lateral (Reels/Shorts) |

OSD: REC/PLAY em y≈144 (abaixo do topo seguro); timestamp em y≈h−96 (acima da base segura); legendas queimadas acima do timestamp.

### Duração

- Episódio alvo: **92s** (janela 85–95s)
- TikTok: até ~180s (recomendado 15–60)
- Reels: até **90s**
- Shorts: até ~180s (recomendado 15–60)

## Presets de exportação

Todos: H.264 High, yuv420p, 1080×1920, 30 fps, AAC 48 kHz, `+faststart`.

| Plataforma | Bitrate vídeo | Áudio |
|------------|---------------|-------|
| TikTok     | 6M (max 8M)   | 192k  |
| Reels      | 5M (max 7M)   | 160k  |
| Shorts     | 8M (max 10M)  | 192k  |

## Áudio

Sem trilha de terceiros. Hiss/chiado VHS gerado com `anoisesrc` (lavfi) e registrado em `../licencas-audio.csv` como *gerado localmente*.

## Não fazer

- Não publicar, comprar nem assinar nada por este pipeline
- Não usar fontes/assets sem licença adequada (evitar VCR OSD Mono e similares)
