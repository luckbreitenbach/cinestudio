# Testes de TTS locais — Fitas da Serra Ep.01
Data: 09/11/2026 (America/Sao_Paulo)

## Ambiente
- Computador do bot: Python 3.13.5, ffmpeg instalado
- TTS instalado para teste: piper-tts 1.8.0 em /workspace/cinestudio/bible/audio-tests/piper-venv
- Vozes baixadas: pt_BR-cadu-medium e pt_BR-jeff-medium (rhasspy/piper-voices)

## Amostras geradas
1. piper-cadu-sample.wav — "Em Capela do Sereno, dizem que a terra recusou um homem." (~3,78s, 22,05 kHz mono PCM)
2. piper-jeff-sample.wav — "Meia hora." (~1,09s, 22,05 kHz mono PCM)

## Avaliação honesta de qualidade
- Inteligível em pt-BR.
- Entrega plana, robótica, sem controle de emoção, idade, sotaque mineiro ou sussurro.
- Só vozes masculinas oficiais CC0 (cadu/jeff); não há voz feminina pt-BR CC0 no pacote rhasspy para Marta.
- Adequado só para rascunho de timing/legendas. NÃO recomendado como áudio final cinematográfico de found footage.

## Licenças (verificadas 09/11/2026)
- Runtime piper-tts: GPL-3.0-or-later (PyPI/metadata upstream).
- MODEL_CARD cadu e jeff: dataset CC0; finetune a partir do base rdh (CC0). URLs: huggingface.co/rhasspy/piper-voices
