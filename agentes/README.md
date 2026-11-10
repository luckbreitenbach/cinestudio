# Equipe do CINESTUDIO AI

O CINESTUDIO AI é um estúdio de curtas cinematográficos originais feitos com IA, pensados para TikTok, Reels e Shorts. A equipe é formada por um diretor e cinco especialistas.

Esses especialistas **não são programas com código próprio**. Cada um é um assistente configurado por **instruções em texto** (o prompt de sistema de cada papel). O que existe neste repositório é o resultado do trabalho deles — roteiros, bíblias, prompts, referências e ferramentas de edição — e, nesta pasta, a descrição de como a equipe se organiza.

## Fluxo de produção

O diretor (Cinestudio AI) coordena a fila e fala com o responsável pelo estúdio. O trabalho passa, nesta ordem:

1. **Pesquisa** levanta formatos e tendências, com fonte e data, e registra em `01-tendencias/`.
2. **Roteiro** transforma a ideia aprovada em história original, bíblia, narração cronometrada e storyboard em `03-roteiros/` e `bible/`.
3. **Direção** define estética, gera referências fixas e escreve e gera os clipes a partir de `04-prompts/` e `05-cenas/`.
4. **Edição** monta o episódio vertical 9:16 com ffmpeg e Python, aplica o look, as legendas, o áudio e exporta as versões de plataforma em `06-videos/`.
5. **Análise** coleta métricas reais das publicações e registra em `07-resultados/`, para orientar os próximos episódios.

Nada é publicado, comprado ou assinado sem autorização explícita do responsável.

```
Pesquisa → Roteiro → Direção → Edição → Análise
                 ↑
           Cinestudio AI (diretor)
```

## Quem lê e quem escreve em cada pasta

| Pasta | Quem lê | Quem escreve | O que fica no Git |
|---|---|---|---|
| `01-tendencias/` | Diretor, Roteiro, Análise | Pesquisa | Relatórios com fonte e data |
| `02-ideias-aprovadas/` | Roteiro, Direção | Diretor (depois da aprovação) | Conceito aprovado |
| `03-roteiros/` | Direção, Edição | Roteiro | Roteiro, diálogos, storyboard, legendas |
| `04-prompts/` | Edição, Diretor | Direção (e relatórios de voz da equipe) | Prompts finais e pesquisa de vozes |
| `05-cenas/` | Edição | Direção | Só a estrutura das pastas; os clipes `.mp4` não entram no Git |
| `06-videos/` | Análise, Diretor | Edição | Scripts, presets, fontes, licenças e README de cada episódio; masters, stems e frames ficam de fora |
| `07-resultados/` | Diretor, Roteiro, Pesquisa | Análise | Planilha e relatórios de métricas (quando houver coleta) |
| `bible/` | Toda a equipe | Roteiro (cânone) e Direção (estética e referências) | Bíblias, estética, cartelas, stills de referência e ferramentas |
| `agentes/` | Toda a equipe | Diretor | Esta documentação |

## Regras do estúdio

Valem para todos os papéis:

- Nunca inventar dados de tendências nem métricas. Toda afirmação factual cita fonte e data da pesquisa ou da coleta.
- Não copiar histórias ou vídeos de outros criadores. Usar tendências só como inspiração de **formato**.
- Preservar a consistência dos personagens e dos cenários (bíblia, estética e imagens de referência fixas).
- Não publicar nada sem aprovação explícita do responsável.
- Não comprar serviços nem fazer assinaturas sem autorização.
- Usar apenas músicas, imagens, vozes, efeitos e fontes com direitos de uso adequados, e registrar a licença.
- Antes de iniciar uma produção paga, apresentar o custo estimado e esperar autorização.
- Não afirmar que uma tarefa foi executada se ela ainda não foi realizada.

## Lições técnicas da produção

- Ritmo de fala em torno de **2,2 palavras por segundo**, com pausas escritas no roteiro; gerar frase a frase e montar depois.
- Evitar planos que dependam da orientação exata de um objeto ou de uma sequência precisa de pequenos eventos (o gerador costuma inverter isso).
- Texto na tela (cartela, número de casa, "AM 870", legendas) entra **na edição**, nunca gerado dentro da imagem.
- Clipes gerados em **720×1280** (9:16), com imagens de referência fixas da `bible/`. A edição amplia para **1080×1920** a 30 fps.
- Loudness alvo: **−14 LUFS** integrados, teto **−1 dBTP**.
- Faixas de voz ficam em stems separados, para trocar a voz depois sem remontar a imagem (`remix_with_voice.sh`).

## Como recriar fora do Grok Bot

Hoje esses papéis rodam como assistentes especializados no ambiente Grok Bot, configurados por texto — não há um executável de cada agente neste repositório. A mesma equipe pode ser recriada em outro lugar, porque o que define cada papel são as instruções.

Para montar um fluxo equivalente:

1. **Texto (LLM).** Use o prompt de sistema de cada arquivo desta pasta (`diretor.md`, `pesquisa.md`, `roteiro.md`, `direcao.md`, `edicao.md`, `analise.md`) em qualquer API de modelo de linguagem, ou orquestre a fila num fluxo (por exemplo n8n, um script ou outro orquestrador). O diretor recebe o pedido, chama o próximo especialista e devolve o resultado ao responsável.
2. **Imagem e vídeo.** A geração das cenas é um passo à parte do texto. É preciso um gerador que aceite imagem de referência, formato vertical 9:16 e durações inteiras em segundos. No estúdio, isso é feito com as ferramentas nativas de imagem e vídeo do ambiente (uso incluso do plano), a 720×1280 quando há referência. Fora dele, use o gerador que você tiver, mantendo as mesmas referências da `bible/` e os prompts de `04-prompts/`.
3. **Voz (TTS).** A voz-guia dos Avisos é o **Kokoro** rodando localmente (modelo Apache-2.0; o empacotador kokoro-onnx é MIT; o treino inclui Koniwa CC BY 3.0 e SIWIS CC BY 4.0, com atribuição). Osvaldo usa `pm_alex`; a interferência usa `pf_dora`. Em Fitas da Serra, a guia usa Piper pt_BR (`cadu` e `jeff`, dataset CC0). Qualquer TTS com direito comercial adequado pode substituir a guia depois, via `remix_with_voice.sh`.
4. **Edição.** A montagem já está neste repositório e não depende do Grok Bot: Python + ffmpeg. Os presets estão em `06-videos/pipeline/scripts/film_pipeline.py` (look Super-8/16 mm dos Avisos) e `06-videos/pipeline/scripts/vhs_pipeline.py` (look VHS de Fitas da Serra). Cartelas: `bible/avisos-a-populacao/tools/compor_cartela.py`. Still estático virando clipe: `bible/avisos-a-populacao/tools/still_para_filme.sh`.

O que este repositório **não** versiona: vídeos montados, clipes de cena, WAV, masters, stems e modelos `.onnx`. Quem for recriar o fluxo precisa gerar ou copiar essa mídia à parte.

## Arquivos desta pasta

- [diretor.md](diretor.md) — Cinestudio AI, diretor do estúdio
- [pesquisa.md](pesquisa.md) — Cinestudio Pesquisa
- [roteiro.md](roteiro.md) — Cinestudio Roteiro
- [direcao.md](direcao.md) — Cinestudio Direção (direção visual)
- [edicao.md](edicao.md) — Cinestudio Edição
- [analise.md](analise.md) — Cinestudio Análise
