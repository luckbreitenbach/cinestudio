#!/usr/bin/env python3
"""Compõe a cartela 'AVISO À POPULAÇÃO Nº X' sobre cartela-aviso-01-base.png (1080x1920).
Uso: python3 compor_cartela.py [numero] [texto_carimbo] [saida]
Fontes livres (SIL OFL): Courier Prime, Noto Serif Display (Condensed), Oswald."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
G="/usr/share/fonts/truetype/sand-box/google/"
num = sys.argv[1] if len(sys.argv)>1 else "1"
stamp = sys.argv[2] if len(sys.argv)>2 else "LEIA COM\nATENÇÃO"
out = sys.argv[3] if len(sys.argv)>3 else "/workspace/cinestudio/bible/avisos-a-populacao/cartela-aviso-01.png"
base=Image.open("/workspace/cinestudio/bible/avisos-a-populacao/cartela-aviso-01-base.png").convert("RGB").resize((1080,1920))
W,H=base.size; rng=np.random.default_rng(7)
GREEN=(38,66,44); RED=(176,40,46)
def ink(layer, strength=0.82, speck=0.22):
    """textura de impressão: alpha com falhas e variação"""
    a=np.array(layer.split()[-1]).astype(float)/255
    n=rng.random(a.shape); n=np.array(Image.fromarray((n*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255
    a=a*np.clip(strength+(n-0.5)*1.4,0,1); a[rng.random(a.shape)<speck*0.05]=0
    layer.putalpha(Image.fromarray((a*255).astype('uint8'))); return layer
def text_layer(lines, font, fill, y0, spacing=0, cx=W//2):
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L); y=y0
    for t in lines:
        b=d.textbbox((0,0),t,font=font); w=b[2]-b[0]
        d.text((cx-w//2-b[0],y-b[1]),t,font=font,fill=fill); y+=(b[3]-b[1])+spacing
    return L,y
img=base.convert("RGBA")
# 1. cabeçalho máquina de escrever
f1=ImageFont.truetype(G+"Courier Prime/CourierPrime-Bold.ttf",40)
L,y=text_layer(["PREFEITURA MUNICIPAL","DE VILA AURORA"],f1,GREEN+(255,),725,spacing=14,cx=538)
img=Image.alpha_composite(img,ink(L))
# 2. linha fina
L=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(L).line((250,y+34,826,y+34),fill=GREEN+(255,),width=3)
img=Image.alpha_composite(img,ink(L,0.9)); y+=64
# 3. título serifado condensado
ft=ImageFont.truetype(G+"Noto Serif Display/NotoSerifDisplay-VariableFont_wdth,wght.ttf",150)
ft.set_variation_by_axes([800,62])
L,y=text_layer(["AVISO À","POPULAÇÃO"],ft,GREEN+(255,),y,spacing=28,cx=538)
fn=ImageFont.truetype(G+"Noto Serif Display/NotoSerifDisplay-VariableFont_wdth,wght.ttf",180); fn.set_variation_by_axes([800,62])
L2,y=text_layer([f"Nº {num}"],fn,GREEN+(255,),y+30,cx=538)
img=Image.alpha_composite(img,ink(L)); img=Image.alpha_composite(img,ink(L2))
# 4. rodapé
f3=ImageFont.truetype(G+"Courier Prime/CourierPrime-Bold.ttf",36)
L,_=text_layer(["RÁDIO MUNICIPAL · AM 870 · 1987"],f3,GREEN+(255,),1790,cx=540)
img=Image.alpha_composite(img,ink(L))
# 5. carimbo vermelho dentro da moldura (centro ~ (772,1557), girado ~9°)
fs=ImageFont.truetype(G+"Oswald/Oswald-VariableFont_wght.ttf",74); fs.set_variation_by_name("Bold")
S=Image.new("RGBA",(520,300),(0,0,0,0)); d=ImageDraw.Draw(S); yy=52
for t in stamp.split("\n"):
    b=d.textbbox((0,0),t,font=fs); w=b[2]-b[0]; d.text((260-w//2-b[0],yy-b[1]),t,font=fs,fill=RED+(235,)); yy+=(b[3]-b[1])+24
S=ink(S,0.78,0.5).rotate(9.1,resample=Image.BICUBIC,expand=True)
img.alpha_composite(S,(772-S.width//2,1557-S.height//2))
img.convert("RGB").save(out); print(out,img.size)
