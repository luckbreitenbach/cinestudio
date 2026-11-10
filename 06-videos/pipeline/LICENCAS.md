# Licenças — pipeline VHS Ep. 01

Todos os assets abaixo são livres para uso comercial conforme suas licenças. Cópias locais dos textos de licença estão em `fonts/`.

## Fontes

| Asset | Autor | URL | Licença | Uso |
|-------|-------|-----|---------|-----|
| **VT323** Regular | Peter Hull / The VT323 Project Authors | https://github.com/google/fonts/tree/main/ofl/vt323 · https://fonts.google.com/specimen/VT323 | SIL OFL 1.1 (`fonts/licenses/OFL-VT323.txt`) | Texto do OSD (`REC`, `PLAY`, timestamp, cartelas) |
| **Share Tech Mono** Regular | Carrois Apostrophe | https://github.com/google/fonts/tree/main/ofl/sharetechmono · https://fonts.google.com/specimen/Share+Tech+Mono | SIL OFL 1.1 (`fonts/licenses/OFL-ShareTechMono.txt`) | Alternativa mono OFL (disponível; pipeline padrão usa VT323) |
| **DejaVu Sans** | DejaVu Fonts authors (Bitstream Vera derivatives) | https://dejavu-fonts.github.io/ · pacote Debian `fonts-dejavu-core` | Licença DejaVu / Bitstream Vera (`fonts/licenses/LICENSE-DejaVu.txt`) | Glifos **●** e **▶** (fallback; VT323/Share Tech Mono não os incluem) e corpo das legendas ASS |
| Press Start 2P (OFL baixado, **não usado** no render) | CodeMan38 | https://github.com/google/fonts/tree/main/ofl/pressstart2p | SIL OFL 1.1 (`fonts/licenses/OFL-PressStart2P.txt`) | Reservado; não entra no preview |

**Não usadas (licença ambígua / proibidas pelo brief):** VCR OSD Mono e similares.

## Áudio

| Asset | Tipo | Origem | Licença |
|-------|------|--------|---------|
| Hiss / chiado VHS | `anoisesrc` (pink/brown/white) via lavfi do ffmpeg | Gerado localmente neste box | Domínio próprio do projeto / gerado localmente — ver `../licencas-audio.csv` |

Nenhuma música ou SFX de terceiros.

## Vídeo de teste

Clipes em `test-clips/` gerados com filtros lavfi do ffmpeg (`testsrc2`, `color`, `drawgrid`). Não são conteúdo final.

## Cartelas e FX

Textos das cartelas vêm do roteiro original do Cinestudio (`03-roteiros/fitas-da-serra-ep01.md`). Efeitos (glitch, rewind, tela azul) são filtros ffmpeg aplicados a fontes lavfi ou aos clipes do projeto.


| **Patrick Hand** Regular | Patrick Wagesreither | https://fonts.google.com/specimen/Patrick+Hand · OFL em `fonts/licenses/OFL-PatrickHand.txt` | SIL OFL 1.1 | Texto lápis «Benedito · 1931» no plano 07 |
| **Caveat** (Variable) | Pablo Impallari / The Caveat Project Authors | https://fonts.google.com/specimen/Caveat · OFL em `fonts/licenses/OFL-Caveat.txt` | SIL OFL 1.1 | Alternativa manuscrita OFL (disponível) |
