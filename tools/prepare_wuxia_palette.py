"""Reversible image palette edits and an original brush-lettered island marker."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
out = ROOT/'assets/wuxia_coast'
out.mkdir(exist_ok=True)
source = ROOT/'assets/island_blender/palm_study/Island_Ground_Study.png'
im = Image.open(source).convert('RGB')
a = np.asarray(im).astype(float)/255
luma = (a*np.array([.2126,.7152,.0722])).sum(axis=2,keepdims=True)
green = np.clip((a[:,:,1:2]-a[:,:,0:1])/.14,0,1)*np.clip((a[:,:,1:2]-a[:,:,2:3])/.10,0,1)
muted = luma*.40+a*.60
muted *= np.array([.94,.96,.91])
# Keep the established painted ground variation, but shift lime toward moss.
muted = muted*(1-green*.18)+np.array([.28,.34,.24])*green*.18
Image.fromarray(np.uint8(np.clip(muted*255,0,255))).save(out/'Moss_Ground.png')

# Quiet long grain, deliberately no pixel noise/cracks.
w,h=256,512
x,y=np.meshgrid(np.arange(w)/w,np.arange(h)/h)
grain=np.sin((x+.012*np.sin(y*6.0))*54)*.018+np.sin((x+.008*np.sin(y*9))*123)*.009
tone=np.array([.38,.325,.26])[None,None,:]+grain[:,:,None]
Image.fromarray(np.uint8(np.clip(tone*255,0,255))).save(out/'Old_Timber.png')

plaque=Image.new('RGB',(256,512),'#92968a')
draw=ImageDraw.Draw(plaque)
font=ImageFont.truetype('C:/Windows/Fonts/simkai.ttf',142)
for ch,cy in [('听',38),('潮',218)]:
    draw.text((128,cy),ch,font=font,anchor='mt',fill='#353f39',stroke_width=0)
small=ImageFont.truetype('C:/Windows/Fonts/simkai.ttf',24)
draw.rounded_rectangle((185,421,224,469),radius=2,fill='#824c3d')
draw.text((204,444),'屿',font=small,anchor='mm',fill='#c5bba2')
plaque.save(out/'Tingchao_Stone.png')
print('Prepared moss ground, quiet timber and original Tingchao marker lettering')
