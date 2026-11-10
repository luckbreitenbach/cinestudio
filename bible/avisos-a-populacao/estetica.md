# AVISOS À POPULAÇÃO · Estética visual (Direção visual)

**Versão 1 · 09/11/2026 · base:** bíblia da série (seção 6) + estética base do Cinestudio (`bible/estetica-base.md`, noir dramático).

## Conceito
Material de arquivo institucional falso de Vila Aurora (1979–1987): filme Super-8 e 16 mm de propaganda municipal, slides de projetor e fotos de jornal da Prefeitura. **Nunca VHS de câmera** (isso é de "Fitas da Serra"). O otimismo oficial dos anos 70 por cima de algo que ninguém nomeia: tudo limpo, organizado e vazio demais.

## Paleta
- Base **sépia-esverdeada desbotada**: creme amarelado nas altas, verde-oliva/verde-garrafa nos médios, pretos lavados puxando pro verde-escuro.
- Uma única cor de destaque por plano (regra noir do canal): âmbar do poste/janela, verde do azulejo, vermelho do carimbo, mostrador âmbar do rádio.
- Saturação baixa. Nada de azul limpo, nada de cores digitais vivas.

## Luz (onde entra o noir)
- Dia/entardecer (planos institucionais: aérea, praça): luz natural chapada e fria de filme de prefeitura, céu lavado. O noir aparece nas sombras longas do fim de tarde.
- Noite e interiores (mesa, cozinha, rua, rádio, represa, fachada): **uma fonte só e dura** (janela, poste, mostrador, luar), contraluz, pretos profundos ocupando boa parte do quadro, silhuetas recortadas contra a luz.
- Pretos "lavados" do filme (não pretos digitais puros): o noir vem do contraste e da composição, a textura vem do filme.

## Textura de filme (de leve, nunca VHS)
- Grão de filme, poeira, arranhões finos, leve *gate weave* (tremor do quadro), vinheta suave/circular, um ou outro quadro que pula.
- Proibido: linhas de varredura, *tracking*, sangramento de cor de fita, timestamp, REC, OSD, overlays de câmera.
- Textura forte (queima, flash, perfuração) só nos planos de "defeito" (9 e 11); o resto é tratado na edição.

## Enquadramentos
- Vertical 9:16, câmera institucional: **plano fixo em tripé**, zooms lentos de filme (push-in), pans lentos. Nada de câmera na mão nervosa.
- Composição simétrica e frontal, de cartão-postal municipal, que "dá errado" por um detalhe (cadeira virada, figura de pé, luzes na água).
- Use batentes, janelas, postes e sombras pra enquadrar dentro do 9:16.
- Objetos como protagonistas: mesa posta, cadeira, rádio de mesa, poste, relógio da praça, louça, a represa.

## Regras fixas
1. **Nenhum rosto visível.** Pessoas só de costas, fora de foco, cortadas no pescoço, ao longe ou como silhuetas atrás de vidro fosco.
2. **Nenhuma Visita inteira, nítida e iluminada.** No máximo silhueta atrás de vidro fosco, lugar a mais, cadeira mexida, pegada molhada.
3. **Nenhum texto gerado na imagem** (placas, números de casa, mostrador do rádio sem números legíveis, sem legenda/marca d'água). Cartela, "870", "41" e legendas entram na edição.
4. Cidade vazia demais: ruas sem carros, praça sem gente, varal parado sem vento.
5. Arquitetura canônica: casas iguais, térreas, telhado de fibrocimento, muros baixos, ruas arborizadas (paineiras, ipês), postes de luz amarela; represa lisa no fim das ruas que descem; torre da rádio no morro.
6. Tudo original: nada de *Angel Engine*, *Greetings from Atomville*, *Latent Places* ou "Fitas da Serra".

## Prefixo de prompt (vídeo)
"1970s–1980s Brazilian municipal archival film footage, vertical 9:16, faded sepia-green color, Super-8 / 16mm film grain, light dust and scratches, slight gate weave, soft vignette, hard single-source light and deep shadows (film noir), empty planned small town, no visible faces, no text, no letters, no numbers, no watermark."

## Referências fixas (esta pasta)
- `cartela-aviso-01-base.png` (sem texto) e `cartela-aviso-01.png` (1080x1920, texto composto por `tools/compor_cartela.py` em Pillow com fontes livres: Courier Prime, Noto Serif Display Condensed e Oswald no carimbo).
- `ref-rua-das-paineiras.png`, `ref-cozinha-azulejo-verde.png` (cenário: azulejo, toalha e luz; ATENÇÃO: a cadeira não saiu virada para a parede, então ainda falta uma ref fiel da cadeira-assinatura), `ref-represa.png`, `ref-radio-am870.png` (sem números legíveis; o "870" entra na edição).

## Referências adicionadas no Aviso 2/3 (10/11/2026)
- `ref-estudio-radio-cardiga.png`: estúdio da Rádio Municipal (microfone cromado de mesa, console sem rótulos, lâmpada vermelha simples, paredes de espuma). Osvaldo SEMPRE de costas, de cardigã marrom e cabelo grisalho curto. A cabeça foi desfocada e escurecida em Pillow pra não mostrar orelha nem bochecha; a bruta está em `alternativas/`. Lição: em vídeo, o modelo tende a virar a cabeça dele de perfil. Prefira enquadrar com a cabeça fora do quadro ou só ombro e cardigã.
- `ref-barragem-torre-sirene.png`: barragem de concreto em contraluz, com torre treliçada e sirene de cornetas (a v1, que saiu como antena parabólica, está em `alternativas/`).
- `ref-hall-sombra-pes.png`: hall visto de dentro, porta escura, faixa de luz sob a porta e a sombra de dois pés parados.
- `ref-fachada-41-dia.png`: fachada da casa dos Moraes de dia, com cortina de renda e muro baixo com portão. O "41" entra na edição.
- Auxiliares: `aux-radio-cozinha.png` (o rádio na prateleira da cozinha de azulejo), `aux-ep02-desenho-geladeira.png` e `aux-praca-frame-ep01p04.png`.
- Ferramenta: `tools/still_para_filme.sh` transforma um still num clipe de arquivo (grão, gate weave, flicker, vinheta e chiado AM sintetizado). Use para planos de elemento estático.
