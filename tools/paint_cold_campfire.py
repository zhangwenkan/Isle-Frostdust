"""Quiet watercolor pigments and a few lengthwise charcoal strokes; textures only."""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/cape_campfire';OUT.mkdir(exist_ok=True)
W,H=1024,512
y,x=np.mgrid[0:H,0:W].astype(float);u=x/(W-1);v=y/(H-1)
# Wood side: broad brown surviving ends around a cool blackened middle.
end=np.clip((np.abs(u-.52)-.22)/.23,0,1);end=end*end*(3-2*end)
dark=np.array([43,49,44]);brown=np.array([78,70,57])
rgb=dark[None,None,:]*(1-end[:,:,None])+brown[None,None,:]*end[:,:,None]
wash=(np.sin(u*5+v*4)*2+np.cos(u*9-v*3)*1.5)[:,:,None]
rgb+=wash
# Broad ash dust along two exposed lengthwise flutes, never a noise carpet.
ash=(np.exp(-((v-.23-.025*np.sin(u*11))/.085)**2)*.46+np.exp(-((v-.74)/.11)**2)*.30)
ash*=np.clip(1-((u-.45)/.53)**4,0,1)
rgb=rgb*(1-ash[:,:,None])+np.array([145,146,132])*ash[:,:,None]
im=Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert('RGBA')
lines=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lines)
for a,b,row,alpha in [(.08,.38,.14,95),(.43,.80,.17,70),(.18,.60,.47,110),(.64,.94,.52,90),(.07,.31,.82,100),(.39,.73,.88,80)]:
    pts=[((a+(b-a)*t)*W,(row+.008*math.sin(t*3.8))*H) for t in np.linspace(0,1,32)]
    left=[];right=[]
    for i,(px,py) in enumerate(pts):
        width=3.0+3.8*math.sin(math.pi*i/(len(pts)-1))
        left.append((px,py-width));right.append((px,py+width))
    d.polygon(left+right[::-1],fill=(32,39,35,alpha))
Image.alpha_composite(im,lines).convert('RGB').save(OUT/'charred_wood.png')
lines.save(OUT/'charred_wood_strokes.png')
# Dry broken ends, a single interrupted growth curve and an off-center split.
N=256;yy,xx=np.mgrid[0:N,0:N].astype(float);rr=np.sqrt(((xx-125)/124)**2+((yy-132)/118)**2)
rgb=np.zeros((N,N,3))+[86,87,73];rgb+=(np.cos(rr*4)*3)[:,:,None]
endim=Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert('RGBA')
layer=Image.new('RGBA',(N,N));d=ImageDraw.Draw(layer)
d.arc((55,62,201,193),16,226,fill=(47,51,43,90),width=3)
d.line([(122,138),(144,157),(168,181)],fill=(36,43,37,125),width=4)
Image.alpha_composite(endim,layer).convert('RGB').save(OUT/'charred_end.png')
(OUT/'palette.json').write_text(json.dumps({'wood':[43,49,44],'surviving_wood':[78,70,57],'ash':[145,146,132],'source':'Original broad washes and sparse lengthwise strokes; follows cape colored-ink palette, no noisy grain.'},indent=2),encoding='utf-8')
print('Cold campfire pigments authored.')
