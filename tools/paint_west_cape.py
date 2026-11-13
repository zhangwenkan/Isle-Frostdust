"""A world-scaled cape turf painting: broad color, grouped grass and a fading footpath."""
from pathlib import Path
import random, math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/west_cape'
OUT.mkdir(exist_ok=True)
W,H=1536,768
yy,xx=np.mgrid[0:H,0:W];x=-26+xx/W*15;z=-6+yy/H*12
path=.4+np.sin(x*.25)*.44
field=.55*np.sin(x*.42+z*.55)+.3*np.cos(x*.75-z*.41)
rgb=np.zeros((H,W,3))+np.array([105,119,65])+field[:,:,None]*np.array([7,7,4])
light=np.exp(-((x+21)/3.6)**2-((z+.1)/2.8)**2)
rgb+=light[:,:,None]*np.array([17,14,7])
img=Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert('RGBA')
marks=Image.new('RGBA',(W,H));d=ImageDraw.Draw(marks);rng=random.Random(212)
for i in range(920):
    px=rng.uniform(-25.5,-10.5);pz=rng.uniform(-5.8,5.8)
    if abs(pz-(.4+math.sin(px*.25)*.44))<.48:continue
    u=(px+26)/15*W;v=(pz+6)/12*H
    shade=rng.choice([(160,162,103,62),(71,91,48,60),(139,146,79,75)])
    for k in range(rng.randint(2,4)):
        sx=u+k*rng.uniform(3,7);sy=v+k*rng.uniform(-2,2)
        length=rng.uniform(5,12)
        d.line([(sx,sy),(sx+length*.4,sy-3),(sx+length,sy-5)],fill=shade,width=2)
img=Image.alpha_composite(img,marks)
arr=np.array(img.convert('RGB')).astype(float)
edge=.46+.065*np.sin(x*2.2)+.045*np.sin(x*4.7+z*.8)
path_w=np.clip((edge+.24-abs(z-path))/.24,0,1)
path_w=path_w*path_w*(3-2*path_w)
# No pale trail ending abruptly on the cliff lip; footprints taper into turf.
fade=np.clip((x+23.4)/3.2,0,1);fade=fade*fade*(3-2*fade)
path_w*=fade*.81
soil=np.array([159,143,103])+np.sin(x*.8+z*.5)[:,:,None]*np.array([3,3,2])
arr=arr*(1-path_w[:,:,None])+soil*path_w[:,:,None]
Image.fromarray(np.uint8(np.clip(arr,0,255))).save(OUT/'cape_turf.png')
print(OUT/'cape_turf.png')
