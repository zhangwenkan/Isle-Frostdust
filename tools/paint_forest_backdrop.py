"""Compose distant forest pigment from our Blender-baked bamboo, no new geometry."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,math,json
R=Path(__file__).resolve().parents[1];O=R/'assets/forest_backwall';O.mkdir(exist_ok=True)
W,H=3072,1434
y=np.linspace(0,1,H)[:,None,None]
top=np.array([38,58,48])[None,None,:];bottom=np.array([58,76,55])[None,None,:]
base=np.repeat(top*(1-y)+bottom*y,W,axis=1)
canvas=Image.fromarray(np.uint8(base)).convert('RGBA')
names=['slender_a','slender_b','cluster_a','slender_c','cluster_b']
sources={n:Image.open(R/'assets/bamboo_depth'/f'{n}_color.png').convert('RGBA') for n in names}
placements=[]
for layer,(spacing,height,root,tint,contrast) in enumerate([(1.30,8.6,1.1,(69,88,72),.20),(1.85,7.1,.1,(48,70,53),.32),(2.30,6.2,-1.6,(34,54,40),.38)]):
 for i in range(int(32/spacing)+2):
  x=-25+i*spacing+.24*math.sin(i*1.7+layer)
  h=height*(.9+.13*math.sin(i*1.41+layer*.8))
  n=names[(i+layer*2)%5];src=sources[n]
  pixels=np.asarray(src).astype(float);lum=pixels[:,:,:3].mean(axis=2)
  pixels[:,:,:3]=np.clip(np.array(tint)[None,None,:]*(1+contrast*(lum[:,:,None]/120-1)),0,255)
  im=Image.fromarray(np.uint8(pixels));pxh=int(h/14*H);pxw=int(pxh*src.width/src.height*.82)
  im=im.resize((pxw,pxh),Image.Resampling.LANCZOS)
  if i%3==0:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  px=int((x+24)/30*W-pxw*.5);py=int(H-(root+h-1.6)/14*H)
  canvas.alpha_composite(im,(px,py));placements.append({'layer':layer,'x':x,'height':h,'variant':n})
canvas=canvas.convert('RGB').filter(ImageFilter.GaussianBlur(.65))
canvas.save(O/'forest_backdrop.png')
(O/'source.json').write_text(json.dumps({'source':'Project bamboo_depth Blender-baked color atlases','mapping':{'x':[-24,6],'height':[1.6,15.6]},'placements':placements},indent=2),encoding='utf8')
print('Composed forest pigment',canvas.size)
