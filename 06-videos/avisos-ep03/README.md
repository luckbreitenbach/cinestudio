# AVISOS À POPULAÇÃO · Aviso nº 3 · "Sirene" (guia)

Montagem completa com voz guia sintética local (Kokoro). **Não publicado.**

## Saídas

| Arquivo | Papel |
|---|---|
| `avisos-ep03_master_guia.mp4` | Master 1080×1920, 30 fps, 68,0 s |
| `avisos-ep03_tiktok_guia.mp4` | Export TikTok |
| `avisos-ep03_reels_guia.mp4` | Export Reels |
| `avisos-ep03_shorts_guia.mp4` | Export Shorts |
| `stems/` | Ambiente, chiado AM, SFX, voz seca, voz com filtro, mix |
| `stems/voz_guia/` | Falas avulsas (`*_dry.wav` e `*_filt.wav`) |
| `audio/` | SFX isolados (vinheta, clique, dial, sino, sirene) |
| `frames/check_*.png` | Quadros de checagem |
| `remix_with_voice.sh` | Troca a faixa de voz sem remontar a imagem |
| `work/video_film_subs_silent.mp4` | Imagem + legendas, sem áudio (entrada do remix) |

## Voz guia

- **Osvaldo:** Kokoro `pm_alex`, filtro AM (300–3400 Hz; no estúdio, p9, um pouco mais aberto: 220–4200 Hz). **"Quem é Teresa?"** (`osv_7`) usa filtro *off-mic* (sala curta, low-pass, nível mais baixo): ele está afastado do microfone, intrigado, sem pânico.
- **Interferência:** Kokoro `pf_dora`, filtro abafado (450–2200 Hz). Entra **no meio** do boletim (lista de nomes) e de novo no fim ("Aviso número quatro." / "Correção.").
- Licença do modelo e do voicepack: **Apache-2.0**. O treino do Kokoro inclui Koniwa (CC BY 3.0) e SIWIS (CC BY 4.0) — atribuição exigida. Arquivos em `fonts/licenses/` (Apache-2.0-Kokoro.txt, MIT-kokoro-onnx.txt). Registrado em `../licencas-audio.csv`.
- **Atempo nunca acima de 1,1×.** Quase todas as falas cabem na velocidade nativa 0,86–0,94, várias no raw sem atempo. Dois atempos:
  - `osv_2a` "Boa noite, Vila Aurora." — 1,033×.
  - `int_1` "Lurdes Ventura." — speed nativo no teto (1,08) + **atempo 1,10×** (o único no limite). A fala natural não cabia no 1,00 s entre as legendas 0:44 e 0:45; o in foi deslocado para **43,921 s** (desvio de −79 ms em relação à tabela 44,00) para terminar exatamente em 45,00, sem invadir "Joaquim Sales." e sem cortar palavras. A legenda acompanhou o in (desvio voz/legenda = 1 ms).

Outros deslocamentos dentro do respiro (legendas alinhadas à voz):

- `osv_1a`+`osv_1b` são **uma só frase**. A tabela pedia a segunda metade às 4,00 s, o que abriria um buraco de 1,3 s no meio da frase. `osv_1b` entra às **2,905 s** (vírgula de 0,22 s); `osv_1c` às **5,999 s**, com a pausa de 1,0 s do roteiro (a tabela pedia 7,00).
- `osv_2c`, `osv_6a`, `int_3`, `int_4`, `int_5` usam o raw natural (sem atempo): havia folga no intervalo. A pausa após `osv_6a` ficou em ~0,50 s (roteiro 0,6 s); a pausa após `int_4` em ~0,42 s (roteiro 0,6 s). `int_3` termina às 47,942 s (folga de ~58 ms antes do corte do p8).

## Sincronia voz / legenda

Desvio = início da fala − início da legenda correspondente. Teto ~100 ms. Nenhuma fala invade a cartela seguinte nem o plano seguinte. Máximo observado: **5 ms**.

| id | in voz | in legenda | desvio | out voz | ok? |
|---|---:|---:|---:|---:|---|
| osv_1a | 0,000 | 0,00 | 0 ms | 2,685 | sim |
| osv_1b | 2,905 | 2,90 | +5 ms | 4,999 | sim (frase contínua; tabela pedia 4,00) |
| osv_1c | 5,999 | 6,00 | −1 ms | 8,648 | sim (pausa 1,0 s; tabela pedia 7,00) |
| osv_2a | 12,000 | 12,00 | 0 ms | 13,710 | sim |
| osv_2b | 14,100 | (suprimida: a cartela já mostra o aviso) | — | 16,408 | — |
| osv_2c | 16,808 | (suprimida, idem) | — | 17,797 | — |
| osv_3a | 19,000 | 19,00 | 0 ms | 22,243 | sim |
| osv_3b | 24,000 | 24,00 | 0 ms | 25,136 | sim |
| osv_3c | 26,000 | 26,00 | 0 ms | 28,706 | sim |
| osv_4a | 31,000 | 31,00 | 0 ms | 35,340 | sim |
| osv_4b | 37,000 | 37,00 | 0 ms | 39,410 | sim |
| osv_4c | 40,000 | 40,00 | 0 ms | 41,460 | sim |
| int_1 | 43,921 | 43,92 | +1 ms | 45,000 | sim |
| int_2 | 45,000 | 45,00 | 0 ms | 46,266 | sim |
| int_3 | 47,000 | 47,00 | 0 ms | 47,942 | sim (58 ms antes do p8) |
| osv_5a | 48,000 | 48,00 | 0 ms | 49,138 | sim |
| osv_5b | 51,000 | 51,00 | 0 ms | 53,451 | sim |
| osv_6a | 55,000 | 55,00 | 0 ms | 57,502 | sim |
| osv_6b | 58,000 | 58,00 | 0 ms | 59,766 | sim |
| int_4 | 62,000 | 62,00 | 0 ms | 63,583 | sim |
| int_5 | 64,000 | 64,00 | 0 ms | 64,938 | sim |
| osv_7 | 65,000 | 65,00 | 0 ms | 66,298 | sim (antes do corte em 67,00) |

A legenda "Aviso à população número três. Número três." foi **suprimida** durante a cartela, que já traz "AVISO À POPULAÇÃO Nº 3". "Boa noite, Vila Aurora." ficou à esquerda do carimbo "LEIA COM ATENÇÃO" (estilo Cartela: Alignment 1, MarginL 90, MarginR 540, MarginV 430) e **não cruza o carimbo**. Confirmado no frame `check_leg_cartela_boa_noite.png`.

## Áudio / loudness

- Alvo: ≈ **−14 LUFS** integrados, teto **−1 dBTP**.
- Medição EBU R 128 (`ebur128=peak=true`) no master: **I = −14,3 LUFS**, **TP = −13,9 dBTP**, **LRA = 7,0 LU**.
- Normalização: atenuação prévia do mix quente + duas passagens `loudnorm` linear + atenuação residual de −1,65 dB. O true peak ficou folgado (o material, depois da voz comprimida, não é picudo); o integrado é que limita.
- **Sirene** (arquivo-assinatura da série, o mesmo de `06-videos/avisos-shared/sirene-barragem.wav`): entra em **1:01** sobre o plano 10, grave e ao longe mas audível ("toca de verdade"). **Corte seco em 1:07**, no corte para o plano 11. O p11 é silêncio absoluto (voz, chiado, ambiente e SFX zerados; medição ebur128 com FTPK −inf a partir de 67,2 s).
- **Sino curto do relógio** em **0:37,15** (entrada do p6).
- Assobio de dial em 0:43,00; chiado sobe na interferência do meio (43–48) e de novo com a sirene (61–67), voltando ao normal no intervalo. Vinheta de vibrafone + clique de projetor em 0:11.
- Todo o SFX foi sintetizado localmente (numpy), exceto a sirene, reutilizada do arquivo-assinatura (também gerado localmente no nº 2). Registrado em `../licencas-audio.csv`. Sem música de terceiros.

## Imagem

Look Super-8/16 mm do `film_pipeline.py` (sépia-oliva corrigido, o mesmo do nº 2, sem magenta): grain, poeira, weave de projetor, flicker, vinheta. 1080×1920, 30 fps, upscale lanczos.

Ajustes da Direção:

- **p5:** crop/zoom de 10%, **sem espelhar**, com leve viés à direita para preservar a torre da sirene.
- **p6:** as silhuetas no bruto eram minúsculas e quase não se liam (QC). Apliquei **zoom 1,3×** centrado no coreto, com um pequeno viés à esquerda para manter o relógio no quadro. Uma silhueta de pé passa a ler-se através do coreto; ainda é pequena no telemóvel.
- **p8:** faixa de luz amarela sob a porta escurecida de leve nos últimos 2,5 s (média da faixa caiu ~16%; o máximo, ~19%). As sombras dos pés/pernas continuam legíveis.
- **p3:** "Rua das Paineiras, 41" composto (PT Serif creme) na faixa inferior da fachada, acima do muro e da zona de legenda. Lift leve de dia para o grade filme não murchar o céu (o plano já era diurno).
- **p2:** cartela oficial nº 3 com entrada de slide e tremor de projetor.
- **p7:** "AM 870" em letterpress no mostrador, com tracking (150/150 frames com detecção do dial).
- **p10–p11:** sirene sobre o 10, corte seco no 11 (flash de fim de rolo, silêncio, sem legenda).

Fontes: PT Serif e Oswald, OFL (cópias das licenças em `fonts/licenses/`).

## Remix da voz

```bash
./remix_with_voice.sh                         # usa stems/stem_voz_guia_kokoro.wav
./remix_with_voice.sh stems/stem_voz_final.wav avisos-ep03_master_com_voz.mp4
./remix_with_voice.sh stems/stem_voz_dry.wav  avisos-ep03_master_com_voz.mp4 --am
```

O script foi testado com a voz guia e completa sem erro. Ele aplica ducking e um `loudnorm` de uma passagem. **Depois da troca, confira o true peak** (o AAC pode estourar o teto; o master final desta pasta foi normalizado em duas passagens + trim, I=−14,3 / TP=−13,9). Se o pico passar de −1 dBTP, atenue o WAV e remuxe com `-c:v copy`.

## Pontos fracos (honestos)

- No p6, mesmo com zoom 1,3×, só uma silhueta (talvez uma segunda, muito ténue) se lê através do coreto; no telemóvel continua discreta. Não inventámos figuras.
- As sombras do p8, como o QC já notava, lembram mais pernas projetadas do que apenas a sombra de dois pés na faixa.
- No p3, leite e jornais estão na calçada, do lado de fora do muro (não na soleira), com sacos/fardos — ressalva do QC, não alterámos o bruto.
- A legenda de duas linhas no p3 assenta sobre as garrafas; lê-se, mas o contraste não é o ideal.
- `int_1` ("Lurdes Ventura.") é a fala mais apertada: speed 1,08 + atempo 1,10, no teto do que combinámos como natural.
- O true peak do master (−13,9 dBTP) está muito abaixo do teto; não dá para subir o nível sem passar de −14 LUFS (o material é denso, não picudo).

## Melhores frames de checagem

- `frames/check_leg_cartela_boa_noite.png` — legenda à esquerda do carimbo, sem cruzar
- `frames/check_p03_fachada_41.png` — endereço na fachada, acima das legendas
- `frames/check_p05_barragem_zoom.png` — zoom 10%, torre no lugar, sem espelho
- `frames/check_p06_silhuetas_zoom.png` — zoom 1,3×, silhueta no coreto, relógio no quadro
- `frames/check_p07_am870.png` — AM 870 no mostrador
- `frames/check_p08_faixa_luz_fim.png` — faixa um pouco mais baixa, sombras legíveis
- `frames/check_p10_represa_sirene.png` — callback das luzes debaixo d'água
- `frames/check_leg_quem_e_teresa.png` — "Quem é Teresa?" no p10
- `frames/check_p01_rua_chao.png` — gancho, câmera rente ao asfalto molhado
- `frames/check_p11_flash.png` — fim de rolo, silêncio
