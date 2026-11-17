"""Paint the connected woodland floor. Raster only; geometry is Blender-owned."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,random,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/layered_island/forest_extension';OUT.mkdir(exist_ok=True)
layout=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
# A shared map keeps the old / new floor seam continuous, 48 texels per metre.
W,H=2592,1920
x=np.linspace(-50,4,W,dtype=np.float32);y=np.linspace(36,-4,H,dtype=np.float32);X,Y=np.meshgrid(x,y)
dist=np.full((H,W),100.,np.float32)
for ka,kb in layout['edges']:
 if ka in ['beach','stair_bottom','bridge_left','bridge_right','cave_mouth']:continue
 a,b=[layout['anchors'][k] for k in (ka,kb)];ax,ay=a[0],-a[2];bx,by=b[0],-b[2]
 vx,vy=bx-ax,by-ay;t=np.clip(((X-ax)*vx+(Y-ay)*vy)/(vx*vx+vy*vy),0,1)
 dist=np.minimum(dist,np.hypot(X-ax-t*vx,Y-ay-t*vy))
edge=.065*np.sin(X*3.7+Y*2.1)+.04*np.sin(Y*6.3-X*4.2)
width=.8+.1*np.sin(X*.37)
path=1-np.clip((dist+edge-width)/.48,0,1);path*=path*(3-2*path)
tone=3*np.sin(X*.54+Y*.28)+2*np.sin(Y*.92-X*.24)
grass=np.stack([66+tone,85+tone,44+tone],axis=-1);earth=np.stack([151+tone,134+tone,86+tone],axis=-1)
arr=grass*(1-path[...,None])+earth*path[...,None]
im=Image.fromarray(np.uint8(np.clip(arr,0,255)));d=ImageDraw.Draw(im);rng=random.Random(161126)
def pixel(xx,yy):return ((xx+50)/54*(W-1),(36-yy)/40*(H-1))
# Brush groups run along the banks. The walking strip keeps quiet open areas.
for _ in range(3500):
 xx=rng.uniform(-49,3);yy=rng.uniform(-3,35);cx,cy=pixel(xx,yy);ix=int(cx);iy=int(cy)
 if dist[iy,ix]<1.05:continue
 base=np.array(im.getpixel((ix,iy)))
 for j in range(rng.randint(3,6)):
  sx=cx+rng.uniform(-10,10);sy=cy+rng.uniform(-5,5);L=rng.uniform(4,10)
  col=tuple(np.clip(base+np.array([10,13,5])*(1 if j%3 else -1),0,255).astype(int))
  d.line([(sx,sy),(sx+L*.25,sy-L*.3),(sx+L,sy-L*.4)],fill=col,width=2)
# Sparse fallen bamboo leaves accumulate at path sides; no all-over noise.
for i in range(280):
 xx=rng.uniform(-46,-13);yy=rng.uniform(10.5,15.8);cx,cy=pixel(xx,yy)
 if not .60<dist[int(cy),int(cx)]<1.48:continue
 ang=rng.uniform(0,math.tau);L=rng.uniform(3,7);dx,dy=math.cos(ang)*L,math.sin(ang)*L
 d.polygon([(cx-dx,cy-dy),(cx-dy*.18,cy+dx*.18),(cx+dx,cy+dy),(cx+dy*.18,cy-dx*.18)],fill=(105+i%8,108+i%7,61+i%4))
# Preserve the existing floor painting away from the new connection; feather
# only the upper western connection, keeping old stairs / path marks aligned.
old=Image.open(ROOT/'assets/layered_island/left_finish_textures/ground_unique.png').convert('RGB')
crop=im.crop((int(pixel(-20,17)[0]),int(pixel(-20,17)[1]),int(pixel(2,-4)[0]),H))
old=old.resize(crop.size,Image.Resampling.BILINEAR)
gx=np.linspace(-20,2,crop.width);gy=np.linspace(17,-4,crop.height);GX,GY=np.meshgrid(gx,gy)
blend=np.clip((GX+17.8)/3,0,1)*np.clip((14.8-GY)/2.8,0,1)
merged=np.asarray(old,dtype=float)*blend[...,None]+np.asarray(crop,dtype=float)*(1-blend[...,None])
im.paste(Image.fromarray(np.uint8(merged)),(int(pixel(-20,17)[0]),int(pixel(-20,17)[1])))
im.save(OUT/'forest_floor.png')
(OUT/'SOURCE.json').write_text(json.dumps({'floor':'New authored earth, grassy brush groups and sparse bamboo litter, blended with the existing self-painted ground at the original island. No third-party game assets.','mapping':{'x':[-50,4],'blender_y':[-4,36]},'size':[W,H]},indent=2),encoding='utf-8')
print('FOREST_FLOOR_SAVED',W,H)
