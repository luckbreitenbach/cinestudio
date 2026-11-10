# Fitas da Serra · Ep. 01 · Opções de áudio (vozes TTS + SFX)
**Data da pesquisa:** 09/11/2026 (America/Sao_Paulo)  
**Episódio:** "A Figueira" (~92s, found footage VHS, só som diegético — sem trilha musical)  
**Roteiro:** `/workspace/cinestudio/03-roteiros/fitas-da-serra-ep01.md`  
**Decisão do Lucas (atualização):** todas as vozes sintéticas (TTS). Sem dublagem humana.  
**Regra:** nenhum serviço pago foi assinado, comprado ou cadastrado nesta pesquisa. Piper (open-source) foi instalado só para teste local.

---

## 0. Volume de fala do Ep. 01 (contagem do roteiro)

| Personagem | Papel | Chars (aprox.) | Bytes UTF-8 |
|---|---|---:|---:|
| Marta | mulher, 38, repórter TV | 178 | 185 |
| Tião | homem, 52, grave, mineiro, off | 55 | 56 |
| Dudu | homem jovem, rápido/nervoso | 61 | 63 |
| Benedito | idoso, rouco, sussurro | 91 | 94 |
| **Total** | | **385** | **398** |

O episódio inteiro cabe com folga em qualquer cota gratuita ou no plano Starter da ElevenLabs (~30k créditos).

---

## 1. VOZES (TTS sintético)

### 1.1 O que já existe neste computador (testado em 09/11/2026)

| Item | Status | Licença verificada | Qualidade (teste honesto) |
|---|---|---|---|
| **ffmpeg** | Instalado | LGPL/GPL (binário do sistema) | Edição/mix OK |
| **piper-tts 1.8.0** | Instalado em `/workspace/cinestudio/bible/audio-tests/piper-venv` | Runtime: **GPL-3.0-or-later** (PyPI) | — |
| **pt_BR-cadu-medium** | Baixado + amostra gerada | MODEL_CARD: dataset **CC0**; finetune do base `rdh` (**CC0**) — [MODEL_CARD](https://huggingface.co/rhasspy/piper-voices/blob/main/pt/pt_BR/cadu/medium/MODEL_CARD) | Intelligível, plano, robótico; sem emoção/idade/sotaque |
| **pt_BR-jeff-medium** | Baixado + amostra gerada | Idem, **CC0** — [MODEL_CARD](https://huggingface.co/rhasspy/piper-voices/blob/main/pt/pt_BR/jeff/medium/MODEL_CARD) | Idem |
| **pt_BR-faber-medium** | NÃO usado | Dataset CC0, mas finetune do inglês **Lessac** (termos de pesquisa) — risco comercial | Evitar para publicação monetizada |
| **OpenVoiceOS Miro/Dii (pt-BR)** | NÃO usado | Vozes de pessoas reais; **uso comercial exige contato com TigreGotico Lda** ([Miro](https://huggingface.co/OpenVoiceOS/pipertts_pt-BR_miro), [Dii](https://huggingface.co/OpenVoiceOS/pipertts_pt-BR_dii)) | — |
| **espeak-ng / Coqui XTTS** | Não instalados | espeak-ng: GPL; Coqui/XTTS: modelos com licenças próprias (muitas restringem comercial) | Não testados |

**Amostras geradas (só teste):**
- `/workspace/cinestudio/bible/audio-tests/piper-cadu-sample.wav` — "Em Capela do Sereno, dizem que a terra recusou um homem." (~3,78s)
- `/workspace/cinestudio/bible/audio-tests/piper-jeff-sample.wav` — "Meia hora." (~1,09s)
- Notas: `/workspace/cinestudio/bible/audio-tests/README-qualidade.md`

**Conclusão Piper:** útil só para rascunho de timing. Só há vozes masculinas CC0 no pacote oficial rhasspy pt-BR → **não cobre Marta**. Qualidade insuficiente para found footage cinematográfico.

---

### 1.2 Serviços pagos / cloud com pt-BR (preços oficiais, 09/11/2026)

Nada abaixo foi assinado. Preços lidos nas páginas oficiais ou documentação oficial na data.

#### A) ElevenLabs — [elevenlabs.io/pricing](https://elevenlabs.io/pricing) (lido 09/11/2026)

| Plano | Preço | Créditos/mês | Uso comercial | Notas |
|---|---|---|---|---|
| Free | US$ 0 | 10k | **Sem** "Commercial License" na tabela do plano Free | ~10 min TTS na UI |
| **Starter** | **US$ 6/mês** (promo 1º mês US$ 1 em alguns banners) | 30k | **Sim — "Commercial License"** listado no plano | Instant Voice Cloning |
| Creator | US$ 22/mês (1º mês US$ 11) | 121k | Sim | Professional Voice Cloning |
| Pro | US$ 99/mês | 600k | Sim | — |

- API (página API): Multilingual/v4 ≈ **US$ 0,08 / 1.000 chars**; Flash/Turbo ≈ **US$ 0,04 / 1.000 chars** ([elevenlabs.io/pricing/api](https://elevenlabs.io/pricing/api)).
- pt-BR: Multilingual v2 e Eleven v4 listam Português / Português (Brasil) na documentação.
- **Adequação ao Ep. 01:** 385 chars cabem no Starter com sobra enorme. Melhor opção de qualidade + emoção + 4 personagens distintos (Voice Design / biblioteca).
- **Custo estimado só deste episódio no Starter:** praticamente o mínimo do plano (US$ 6/mês se mantiver a assinatura; ou cancelar após o ciclo). Não dá para gerar comercialmente no Free.

#### B) Fish Audio — [fish.audio/plan/](https://fish.audio/plan/) + [docs pricing](https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits) (lido 09/11/2026)

| Oferta | Preço | Comercial? | Notas |
|---|---|---|---|
| Free (UI) | US$ 0 · 8k créditos/mês · até ~7 min | **Contraditório:** o card do Free cita "Commercial use", mas a FAQ da mesma página diz que Free é só pessoal/não-comercial | **Não confiar no Free para TikTok/IG/YT monetizado** |
| Plus | US$ 15/mês (US$ 11/mês no anual) | Sim ("Commercial use allowed") | ~200 min; Voice Design |
| Pro | US$ 100/mês (US$ 75/mês no anual) | Sim | — |
| API `s2.1-pro` | **US$ 15 / 1M UTF-8 bytes** | Sim (pago) | Pay-as-you-go, sem mensalidade mínima |
| API `s2.1-pro-free` | US$ 0 até **30/11/2026** | Restrições: sem SLA; dados podem treinar modelo; produtos > US$ 1M ARR devem contatar | Arriscado para publicação comercial "limpa" |
| API `drama-3` | US$ 50 / 1M bytes (promo US$ 10 até 30/11/2026) | Pago | Foco em performance dramática |

- pt-BR: modelo multilíngue (docs/blog citam Português entre 80+ idiomas).
- Ep. 01 ≈ 398 bytes UTF-8 → custo API pago ≈ **desprezível** (frações de centavo), mas exige crédito/conta.

#### C) Azure Speech (Neural) — [azure.microsoft.com/.../speech](https://azure.microsoft.com/en-us/pricing/details/speech/) + Q&A Microsoft

| Item | Valor | Fonte / data |
|---|---|---|
| Free F0 | **0,5 milhão** de chars neurais/mês | Página Azure (09/11/2026) |
| Neural padrão (lista East US) | **US$ 15 / 1M chars** | Citado na doc de quotas Microsoft e em [OndaLabs 17/10/2026](https://ondalabs.app/blog/azure-ai-speech-tts) / [VoiceCost 09/11/2026](https://voicecost.net/vendors/azure.html). A página Azure pública mascara `$` sem login. |
| Neural HD | ~US$ 22 / 1M chars (East US) | OndaLabs 17/10/2026 |
| Uso comercial do áudio gerado | Sim, com recurso **pago/billed** (Pay-as-you-go); sem royalty por reprodução | [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/460557/microsoft-azure-text-to-speech-commercial-usage) (funcionário Microsoft) |

- Vozes pt-BR prebuilt (ex.: Francisca, Antonio — nomes históricos da plataforma; confirmar lista atual no portal).
- Bom para Marta/Tião com SSML; menos "atuação" que ElevenLabs/Fish Drama.
- Exige conta Azure + upgrade para billed se for uso comercial conforme a resposta oficial acima.

#### D) Google Cloud Text-to-Speech — [cloud.google.com/text-to-speech/pricing](https://cloud.google.com/text-to-speech/pricing) (lido 09/11/2026)

| Modelo | Free/mês | Depois |
|---|---|---|
| WaveNet / Standard | 0–4M chars | **US$ 4 / 1M chars** |
| Neural2 / Polyglot | 0–1M chars | **US$ 16 / 1M chars** |
| Chirp 3 HD | 0–1M chars | **US$ 30 / 1M chars** |
| Studio | 0–1M chars | **US$ 160 / 1M chars** |
| Gemini TTS (vários) | — | tokens (ex. Flash TTS input US$ 0,50–1,00 / 1M text tokens) |

- Precisa habilitar billing no GCP (mesmo com free tier).
- Ep. 01 cabe no free WaveNet/Neural2.
- Qualidade sólida, menos expressiva que ElevenLabs para terror diegético.

---

### 1.3 Mapeamento sugerido personagem → TTS

| Personagem | Piper (rascunho) | Produção recomendada |
|---|---|---|
| Marta (♀ 38, TV) | ❌ sem voz feminina CC0 | ElevenLabs Voice Design / biblioteca pt-BR feminina adulta; ou Azure Francisca + SSML |
| Tião (♂ 52, mineiro off) | cadu/jeff (rascunho) | ElevenLabs masculino grave + direção "calmo, mineiro"; ou Azure Antonio |
| Dudu (♂ jovem, nervoso) | ❌ qualidade baixa | ElevenLabs jovem + tags de urgência |
| Benedito (idoso, rouco) | ❌ | ElevenLabs/Fish com estilo sussurro/rouquidão; processar com EQ + chiado VHS na edição |

---

## 2. EFEITOS SONOROS (SFX)

### 2.1 Fontes e licenças (verificadas 09/11/2026)

| Fonte | Licença | Comercial TikTok/IG/YT monetizado? | Atribuição | Observação |
|---|---|---|---|---|
| **Freesound CC0** | Creative Commons 0 | **Sim** | Não obrigatória | Só usar sons cuja página mostre o texto CC0 ("You can copy, modify… commercial purposes…") |
| **Pixabay Sound Effects** | [Pixabay Content License](https://pixabay.com/service/license-summary/) | **Sim** (não redistribuir o SFX sozinho/standalone) | Não obrigatória | Livre para modificar e embutir no vídeo |
| **BigSoundBank (La Sonothèque)** | **CC0** declarado na página de cada som | **Sim** | Não obrigatória | Confirmei nas páginas individuais |
| **Sonniss #GameAudioGDC** | [EULA v2.0, vigente 27/08/2026](https://sonniss.com/gdc-bundle-license/) | **Sim** (sync em vídeos/jogos; sem atribuição) | Não | Proíbe revender como biblioteca e **proíbe treinar IA** com os sons. Download gratuito do bundle. |
| **BBC Sound Effects (RemArc)** | RemArc: **só não-comercial / educação / pesquisa**; comercial via Pro Sound Effects (pago) | **NÃO** no free RemArc | Crédito BBC se usar RemArc | [Licensing](https://sound-effects.bbcrewind.co.uk/licensing) + FAQ BBC. **Não usar** no Ep. 01 sem compra PSE. |

---

### 2.2 Candidatos verificados por necessidade (URLs + licença)

Só listo o que a página confirmou CC0 / Pixabay Content License / BigSoundBank CC0 nesta data. Não baixei os arquivos ainda (só pesquisa).

| Necessidade | Candidato 1 | Licença | Candidato 2 | Licença |
|---|---|---|---|---|
| **Cigarras / insetos BR** | [Freesound 414411 — Mineiros Brasil selva dusk chorus (samwd)](https://freesound.org/people/samwd/sounds/414411/) | **CC0** (texto comercial na página) | Pixabay search [cicadas](https://pixabay.com/sound-effects/search/cicadas/) | Pixabay Content License |
| **Vento nas folhas** | [Freesound 751473 — Soft Wind in the Trees (Borgory)](https://freesound.org/people/Borgory/sounds/751473/) | **CC0** | — | — |
| **Passos em folhas secas** | [Freesound 635875 — Stepping on dry leaves (Wax_vibe)](https://freesound.org/people/Wax_vibe/sounds/635875/) | **CC0** | [Pixabay — Person walking in leaves](https://pixabay.com/sound-effects/film-special-effects-person-walking-in-leaves-47817/) | Pixabay Content License |
| **Respiração rascante** | [Freesound 151206 — Female Breathing heavily (OwlStorm)](https://freesound.org/people/OwlStorm/sounds/151206/) — autor declara **CC0** na descrição | **CC0** | Processar com pitch/EQ na edição para o gancho "seco" | — |
| **Estalo de galho** | [Freesound 434555 — Branches being snapped (KieranKeegan)](https://freesound.org/people/KieranKeegan/sounds/434555/) | **CC0** | — | — |
| **Motor / playback VHS / camcorder** | [BigSoundBank 2691 — VCR: VHS playback](https://bigsoundbank.com/vcr-vhs-playback-s2691.html) | **CC0** | [Freesound 750857 — VCR fast rewinding (LukaCafuka)](https://freesound.org/people/LukaCafuka/sounds/750857/) | **CC0** |
| **Clique REC / botão** | [BigSoundBank — Electric switch](https://bigsoundbank.com/electric-switch-s0026.html) | **CC0** (site) | [BigSoundBank — Electric switch #2](https://bigsoundbank.com/electric-switch-2-s0052.html) | **CC0** |
| **Rebobinar / chiado VHS** | Freesound 750857 (acima) | **CC0** | Alternativa com **atribuição**: [Tape hiss loop — heyheytheree](https://freesound.org/people/heyheytheree/sounds/873064/) = **CC BY 4.0** (crédito obrigatório) | Preferir CC0 puro |
| **Grilos / noite** | Usar 414411 (dusk) + vento 751473; ou Pixabay search "crickets" | CC0 / Pixabay | — | — |
| **Corrida no mato** | Camada: passos 635875 + galhos 434555 (+ respiração 151206) | CC0 | Lacuna: um take único "running through woods" (ex. jone_oost 366711) **não teve CC0 confirmado na página** nesta rodada — **não usar** até verificar | — |
| **Queda da câmera no chão** | [BigSoundBank 235 — Iron bar falls #2](https://bigsoundbank.com/iron-bar-falls-2-s0235.html) + folhas 635875 (camada) | **CC0** | Não é câmera literal; processar (EQ + folhas) na edição | — |
| **Cascos de cavalo (gancho Fita 02)** | [Freesound 843303 — Coconut Horse Walking (BorzSounds)](https://freesound.org/people/BorzSounds/sounds/843303/) — texto CC0 na página | **CC0** | [Pixabay — Horse Walking (Universfield)](https://pixabay.com/sound-effects/nature-horse-walking-123782/) | Pixabay Content License |
| **Corrente** | [Freesound 670853 — horse steps and chain (bruno.auzet)](https://freesound.org/people/bruno.auzet/sounds/670853/) | **CC0** | [BigSoundBank 359 — Heavy chain](https://bigsoundbank.com/sound-359-heavy-chain.html) | **CC0** |

**Sonniss GDC:** fonte complementar gratuita e comercial-safe para preencher lacunas (queda, mato, etc.), desde que o download seja do site oficial e se respeite a proibição de treinar IA. Catálogo muda por ano; escolher sons após baixar o bundle 2026 em [gdc.sonniss.com](https://gdc.sonniss.com/).

**BBC RemArc:** descartado para este episódio (não-comercial).

---

## 3. Recomendação (caminho mais barato e seguro)

### SFX → **custo US$ 0**
Montar o banco do Ep. 01 só com **Freesound CC0 + BigSoundBank CC0 + Pixabay**. Opcional: Sonniss GDC. **Não usar BBC RemArc.**  
Estimativa: 0 reais / 0 dólares.

### Vozes → escolher um dos três

| Prioridade | Caminho | Custo para o Ep. 01 | Qualidade esperada | Risco de licença |
|---|---|---|---|---|
| **1 — Recomendado** | **ElevenLabs Starter** (Commercial License) + 4 vozes distintas | **US$ 6/mês** (ou promo 1º mês se ainda válida) | Melhor para terror diegético / emoção | Baixo (plano pago com comercial explícito) |
| **2 — Quase grátis** | **Google WaveNet** (free 4M chars) ou **Azure Neural** (F0 0,5M + recurso billed p/ comercial) | Conta cloud; episódio ≈ US$ 0 de uso | Boa, menos "atuação" | Médio (setup billing; seguir Product Terms) |
| **3 — Só rascunho** | **Piper cadu/jeff** local | US$ 0 | Ruim para final; sem Marta | Baixo (CC0 nas vozes), mas qualidade insuficiente |

**Caminho recomendado ao Lucas:**  
1. Aprovar **ElevenLabs Starter** (ou Google/Azure se quiser zero/quase zero custo e aceitar menos emoção).  
2. Eu (ou Edição) baixo só os SFX CC0/Pixabay listados, com cópia da URL+licença na pasta `bible/audio/`.  
3. Gerar as 4 vozes; processar com textura VHS (chiado, banda estreita) no ffmpeg.  
4. Antes de qualquer assinatura: apresentar de novo o custo exato e esperar autorização (regra do estúdio).

**Nada foi publicado, comprado ou assinado nesta pesquisa.**

---

## 4. Arquivos desta rodada

| Caminho | Conteúdo |
|---|---|
| `/workspace/cinestudio/04-prompts/fitas-da-serra-ep01-audio-opcoes.md` | Este relatório |
| `/workspace/cinestudio/bible/audio-tests/piper-cadu-sample.wav` | Amostra Piper cadu |
| `/workspace/cinestudio/bible/audio-tests/piper-jeff-sample.wav` | Amostra Piper jeff |
| `/workspace/cinestudio/bible/audio-tests/README-qualidade.md` | Avaliação de qualidade |
| `/workspace/cinestudio/bible/audio-tests/voices/` | Modelos ONNX Piper (CC0) + MODEL_CARD |

---

## 5. Fontes principais (data 09/11/2026)

- ElevenLabs Pricing: https://elevenlabs.io/pricing  
- ElevenLabs API Pricing: https://elevenlabs.io/pricing/api  
- Fish Audio Plans: https://fish.audio/plan/  
- Fish Audio API Pricing: https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits  
- Google Cloud TTS Pricing: https://cloud.google.com/text-to-speech/pricing  
- Azure Speech Pricing: https://azure.microsoft.com/en-us/pricing/details/speech/  
- Azure commercial Q&A: https://learn.microsoft.com/en-us/answers/questions/460557/microsoft-azure-text-to-speech-commercial-usage  
- Piper MODEL_CARD cadu/jeff: huggingface.co/rhasspy/piper-voices  
- Pixabay Content License: https://pixabay.com/service/license-summary/  
- Sonniss GDC License v2.0: https://sonniss.com/gdc-bundle-license/  
- BBC Sound Effects Licensing: https://sound-effects.bbcrewind.co.uk/licensing  
