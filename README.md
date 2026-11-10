# CINESTUDIO AI

Estúdio de curtas cinematográficos originais feitos com IA, pensados para TikTok, Reels e Shorts.

Este repositório reúne roteiros, bíblias de série, prompts, ferramentas de edição, fontes e referências estáticas. Os vídeos montados, os clipes de cena e o áudio pesado (WAV, masters, stems e modelos de voz) não estão versionados aqui.

## Estrutura

- `01-tendencias/` — levantamentos de formato, com fonte e data da pesquisa
- `02-ideias-aprovadas/` — conceitos aprovados para produção
- `03-roteiros/` — roteiros dos episódios
- `04-prompts/` — prompts de geração e pesquisas de voz
- `05-cenas/` — pasta dos clipes gerados (os vídeos ficam fora do repositório)
- `06-videos/` — scripts de montagem, presets, fontes, registros de licença e pastas de episódio (exportações e stems ficam de fora)
- `07-resultados/` — métricas de publicação, quando houver coleta
- `bible/` — bíblias, estética, referências visuais e amostras curtas de voz

## Séries neste repositório

- **Avisos à População** — terror analógico de serviço público, vertical 9:16
- **Fitas da Serra** — found footage com estética VHS

## Vozes, fontes e licenças

As falas e a narração usam vozes sintéticas. A voz-guia dos Avisos é o Kokoro (Apache-2.0; o empacotador kokoro-onnx é MIT). A voz-guia de Fitas da Serra usa Piper pt_BR (modelos cadu e jeff, dataset CC0). As fontes do projeto estão acompanhadas das licenças OFL (e da licença da DejaVu, onde ela é usada). O registro está em `06-videos/licencas-audio.csv` e nas pastas `fonts/licenses/`.

Amostras curtas de voz em MP3 (menores que 2 MB) e alguns efeitos sonoros leves foram mantidos. Os arquivos `.onnx` e os WAV de trabalho não entram neste repositório.
