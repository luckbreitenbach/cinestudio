# Vozes de IA grátis para falas e narração (pt-BR, uso comercial) · 9 nov 2026

**Pedido:** Lucas, 9 nov 2026: "procure fontes grátis de voz com ia para falas e narracao".
**Critério:** grátis **e** com direito de uso **comercial** em vídeos monetizados.
**Data de checagem de todos os links:** 2026-11-09 (America/Sao_Paulo).
**Máquina (Shell, 9/11):** 8 vCPU, 16 GB de RAM (cerca de 4 GB livres no momento), **sem GPU**, 119 GB livres em disco.

> ⚠️ **Correção importante:** o plano anterior era usar a "faixa grátis do Google **ou Azure**". O **Azure F0 (grátis) NÃO dá direito comercial.** Os Microsoft Product Terms dizem: "For Customers of the paid tier TTS Service only, Customer may use the audio output ... including for commercial purposes". Moderadores da Microsoft confirmaram que é preciso usar S0, que é pago. Fontes: https://learn.microsoft.com/en-us/answers/questions/5805156/ (mar/2026) e https://learn.microsoft.com/en-us/answers/questions/6045956/ (22 out 2026). **Azure F0 está fora.**

---

## 1. Tabela resumo

| Fonte | Custo / limite grátis | Vozes pt-BR | Expressividade | Comercial? | Conta/cartão | Roda na nossa máquina? |
|---|---|---|---|---|---|---|
| **Gemini API TTS** (gemini-3.8-flash-tts / flash-lite-tts) | Nível grátis: **"Free of charge"** na entrada e na saída, com limites de taxa no AI Studio (valores exatos **não verificados**) | O idioma "Portuguese" consta como suportado. Vozes pré-prontas multilíngues; sotaque BR por instrução (**precisa testar**) | **Alta**: estilo, tom e ritmo por instrução e tags; **multi-speaker (2 vozes por chamada)** | **Sim, com condições**: "Google won't claim ownership" do conteúdo gerado. No nível grátis, o Google **usa prompts e áudios para treinar**. Na EEA/UK, só nível pago | Conta Google e chave do AI Studio; **sem cartão** no nível grátis | Nuvem (API) |
| **Google Cloud TTS** Chirp 3 HD | **1 mi de caracteres/mês grátis**, depois US$30 por 1 mi | **30 vozes** pt-BR-Chirp3-HD-* | Boa/natural, mas **sem SSML, rate ou pitch** | **Sim**: o áudio é "Customer Data" (resumo de busca; termos completos não lidos) | Conta Google Cloud **com faturamento e cartão** | Nuvem |
| Google Cloud TTS WaveNet / Neural2 | WaveNet: 4 mi/mês grátis · Neural2: 1 mi/mês grátis | WaveNet A–E, Neural2 A–C | Média, com SSML | Sim (idem) | Cartão | Nuvem |
| **Amazon Polly** | Generative: 100 mil caracteres/mês e Neural: 1 mi/mês, **nos primeiros 12 meses**. Standard: 5 mi/mês | Generative: **Camila, Carolina, Leo**. Neural: Camila, Vitória, Thiago | Generative boa | Provável (termos da AWS **não lidos** nesta rodada) | Conta AWS e cartão | Nuvem |
| IBM Text to Speech Lite | 10 mil caracteres/mês | Isabela, Camila, Lucas (Natural/Expressive) | Média | **Não verificado** | Conta IBM Cloud | Nuvem |
| Azure Speech F0 | 0,5 mi caracteres/mês | Francisca, Antonio, Thalita (+HD) | Alta | **NÃO** (só no nível pago) | Cartão | Nuvem |
| ElevenLabs Free | 10 mil créditos/mês | Muitas | Muito alta | **NÃO**: "cannot be used for any commercial purpose", exige "elevenlabs.io" no título, e o áudio gerado no free **nunca** vira comercial | Conta | Nuvem |
| Fish Audio Free | n/d | Sim | Alta | **NÃO** (só uso pessoal, não comercial) | Conta | Nuvem |
| Murf Free | Trial de 10 min, sem download | Sim | Alta | **NÃO** | Conta | Nuvem |
| PlayHT | — | — | — | **Encerrado** (comprado pela Meta em jul/2025, fechado no fim de 2025) | — | — |
| CapCut TTS | Grátis no app | Sim | Média | **Arriscado**: só materiais "Dual Use" marcados como comerciais, e mesmo assim só para fins **promocionais e publicitários**. Proíbe editar o material fora do CapCut. A versão lida é a dos EUA | Conta | App |
| TikTok TTS (no app) | Grátis | Sim | Baixa | Só dentro do TikTok. Uso externo **não autorizado** (fonte secundária) | — | App |
| Edge "Ler em voz alta" / edge-tts | Grátis | Sim (as do Azure) | Alta | **NÃO** há concessão comercial; a Microsoft indica usar o Azure | — | — |
| **Kokoro-82M** (local) | **Grátis, ilimitado** | **3**: pf_dora (F), pm_alex (M), pm_santa (M) | Média, mais "chapada"; sem clonagem | **Sim**: pesos **Apache-2.0** | Nenhuma | **Sim, CPU**: cerca de 1–2 s por frase de 5 s (**testado**) |
| **Piper** (local, já instalado) | Grátis, ilimitado | faber, cadu, jeff (datasets **CC0**); edresson (CC BY 4.0, exige atribuição) | Baixa–média | **Sim**: o dataset das vozes é CC0. O motor piper1-gpl é GPL-3.0, o que não afeta o áudio gerado | Nenhuma | **Sim, CPU** (testado) |
| **Chatterbox Multilingual v3, pacote pt-br** | Grátis | Clonagem a partir de uma referência (usar voz **sintética** como referência) | **Alta**; o pt-br tem CER de 0,35% segundo a Resemble | **Sim**: **MIT**. Todo áudio leva marca d'água PerTh. **Sem manutenção desde ago/2026** | Nenhuma | **Não na prática**: o checkpoint T3 tem 2,1 GB em fp32, o que pede GPU ou bem mais RAM livre. Não testado |
| Qwen3-TTS (0.6B/1.7B) | Grátis | Português suportado, mas **sem falante nativo pt** nos presets (os 9 timbres são zh/en/ja/ko). Daria para clonar ou desenhar a voz | Alta (instruções de emoção) | **Sim**: Apache-2.0 | Nenhuma | Pesado para CPU com 4 GB livres (~0,9 B parâmetros). Não testado |
| Coqui XTTS-v2 | Grátis | Sim | Alta | **NÃO**: CPML "allows only non-commercial use of a machine learning model and its outputs". A Coqui fechou e não há como comprar licença | — | — |
| F5-TTS (inclui fine-tune pt-br) | Grátis | Sim | Alta | **NÃO**: os pesos são CC-BY-NC-4.0 | — | — |
| Fish Speech / OpenAudio S1-mini / S2 Pro | Grátis | Sim | Muito alta | **NÃO**: CC-BY-NC-SA ou Fish Audio Research License | — | — |
| VibeVoice (Microsoft) | Grátis | **Sem pt** (só en/zh) | — | Só para pesquisa | — | — |
| MeloTTS, Bark | Grátis | **Não verificado nesta rodada** | — | Código MIT (não confirmado de novo) | — | — |

### Fontes (todas checadas em 2026-11-09)
- Preços do Google Cloud TTS: https://cloud.google.com/text-to-speech/pricing
- Vozes do Google (lista pt-BR extraída por curl): https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types
- Preços da Gemini API (TTS grátis no Free Tier): https://ai.google.dev/gemini-api/docs/pricing
- Termos da Gemini API ("Use of Generated Content" e "Unpaid Services"): https://ai.google.dev/gemini-api/terms
- Geração de voz no Gemini (multi-speaker, idiomas): https://ai.google.dev/gemini-api/docs/speech-generation
- Preços do Azure (F0 com 0,5 mi): https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/
- Azure F0 sem direito comercial: links do aviso no topo + Product Terms https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure/MCA
- Preços do Polly: https://aws.amazon.com/polly/pricing/ · Vozes: https://docs.aws.amazon.com/polly/latest/dg/available-voices.html
- ElevenLabs: https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform
- Fish Audio, planos: https://fish.audio/plan/ · S1-mini: https://huggingface.co/fishaudio/s1-mini
- Murf/PlayHT: https://aicomparison.ai/murf-ai-vs-playht/ e https://help.murf.ai/is-murf-free-to-use (fontes secundárias)
- Licença de materiais do CapCut (atualizada em 22 jan 2026): https://www.capcut.com/clause/material-license-agreement
- Edge/edge-tts: https://learn.microsoft.com/en-us/answers/questions/5925556/
- TikTok TTS: https://thetechtips.blog/is-tiktok-text-to-speech-copyright-guide (fonte secundária, **fraca**)
- IBM: https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-voices
- Comparação de licenças de modelos abertos (Cartesia, 9 out 2026): https://www.cartesia.ai/learn/open-source-tts
- Kokoro: https://github.com/hexgrad/kokoro · https://huggingface.co/hexgrad/Kokoro-82M
- Chatterbox v3 (10 jun 2026, aviso de aposentadoria em ago/2026): https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages · pacote pt-br: https://huggingface.co/ResembleAI/Chatterbox-Multilingual-pt-br (licença MIT pela tag do HF; o corpo do card não repete)
- Qwen3-TTS: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
- XTTS: https://huggingface.co/coqui/XTTS-v2/raw/main/LICENSE.txt
- F5-TTS: https://github.com/SWivid/F5-TTS/discussions/997 · https://huggingface.co/firstpixel/F5-TTS-pt-br
- Piper pt_BR (MODEL_CARD de cada voz): https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR

---

## 2. Recomendações

### Narração
1. **Gemini 3.8 Flash TTS (nível grátis)**: o mais expressivo entre as opções grátis com uso comercial, controlado por instrução ("narre em tom sombrio, sussurrado, sotaque mineiro"). Não pede cartão. *Ressalvas:* os roteiros e áudios enviados podem ser usados pelo Google para treino, o que é aceitável porque o material será público de qualquer forma. Os limites diários não foram verificados. O sotaque brasileiro precisa de teste.
2. **Google Cloud Chirp 3 HD pt-BR**: 30 vozes e 1 mi de caracteres/mês grátis, o que dá para dezenas de episódios. *Ressalva:* exige faturamento ativo com cartão (a tarefa adiada de abrir o Google Cloud). Não tem controle de emoção por SSML.
3. **Kokoro (local) ou Piper faber/cadu (local)**: grátis para sempre, offline, sem conta e com licença limpa (Apache-2.0 / CC0). Qualidade inferior; serve como guia e reserva.

### Falas (diálogo)
1. **Gemini TTS multi-speaker**: 2 personagens por chamada, com estilo por fala. Para 3 ou mais personagens, gerar em mais de uma chamada.
2. **Google Chirp 3 HD**: uma voz diferente das 30 para cada personagem. Fácil manter a consistência, porque a mesma voz-ID vale para a temporada inteira.
3. **Amazon Polly Generative** (Camila, Carolina, Leo), grátis por 12 meses e com cartão; ou **Chatterbox pt-br** (MIT, clonagem expressiva) **se** um dia tivermos GPU. *Ressalva do Chatterbox:* usar como referência **apenas vozes sintéticas próprias** (nunca clonar pessoas reais), considerar a marca d'água e lembrar que o projeto não recebe mais manutenção.

### Não usar em vídeo monetizado
ElevenLabs Free, Azure F0, Fish Audio Free e os pesos abertos dele, Murf Free, XTTS-v2, F5-TTS, edge-tts, TikTok TTS fora do app e CapCut TTS (exceto anúncio com material "Dual Use").

### Boas práticas
- Indicar "vozes sintéticas geradas por IA" na descrição. A Microsoft exige isso, e TikTok e YouTube pedem rótulo de conteúdo realista feito com IA.
- Gerar o áudio final **no próprio plano que dá direito comercial**. Não dá para "regularizar" depois áudio feito em plano grátis (é a regra explícita do ElevenLabs e do Azure).
- Guardar em `bible/` o registro de qual serviço, voz e data gerou cada fala, como prova de licença.

---

## 3. Testes de áudio gerados nesta rodada
Pasta: `/workspace/cinestudio/bible/audio-tests/2026-11-09-nova-busca/` (WAV e MP3)
Frase usada: *"Ninguém sabe quem gravou esta fita. Mas todo mundo que assistiu até o fim... desapareceu."*
- `kokoro_pf_dora` (F), `kokoro_pm_alex` (M), `kokoro_pm_santa` (M): Kokoro-82M via kokoro-onnx, CPU, 0,8–2,1 s para gerar cerca de 5,5 s de áudio. Licença Apache-2.0.
- `piper_faber` (M, novo) e `piper_cadu` (M): Piper, para comparação. Dataset CC0.
- **Ainda não foram ouvidos.** Não tenho como julgar a pronúncia pelo ouvido; o Lucas precisa ouvir e comparar.
- Ambiente do Kokoro: `/workspace/tts-eval/kvenv` com modelo `/workspace/tts-eval/kokoro-v1.0.onnx` (325 MB) e vozes (28 MB).
- Gemini e Google Cloud **não foram testados**, porque exigem conta ou chave do Lucas.

## 4. Não verificado
- Limites diários e por minuto do nível grátis do Gemini TTS e qualidade do sotaque pt-BR.
- Termos de uso de saída da AWS (Polly) e da IBM (Lite).
- Suporte a pt em MeloTTS e Bark.
- Termos do CapCut para o Brasil (a versão lida é a dos EUA).
- O resumo de que no Google Cloud TTS "o áudio é Customer Data" veio de resultado de busca; os termos completos do Google Cloud não foram lidos.
