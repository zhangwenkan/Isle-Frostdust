"""Paint structural albedo and a unique grass/path map; no 3D generation here."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,math,random,json,hashlib
R=Path(__file__).resolve().parents[1];OUT=R/'assets/layered_island/left_finish_textures'
layout=json.loads((R/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
rng=random.Random(1691)
def save(name,im):im.save(OUT/(name+'.png'))
def poly(d,pts,col):d.polygon(pts,fill=col)
# Four variants have distinct long joints, intermittent dry-brush shoulders and
# broad quiet planes. A whole face owns its UV; they are not cracks per triangle.
for k in range(4):
 im=Image.new('RGB',(512,512),(108+k*3,111+k*2,96+k));d=ImageDraw.Draw(im)
 paths=[[(30+19*k,0),(112+11*k,132),(168+16*k,159),(224+9*k,361)],[(395-17*k,70),(335-12*k,210),(286+4*k,276),(387+9*k,456)]]
 for j,pts in enumerate(paths):
  poly(d,[(x-35,y) for x,y in pts]+list(reversed([(x+48,y) for x,y in pts])),(97+k*3,102+k*2,89+k))
  poly(d,pts+list(reversed([(x+26,y) for x,y in pts])),(119+k*3,122+k*2,105+k))
  for a,b in zip(pts,pts[1:]):
   ax,ay=a;bx,by=b;start=(ax+(bx-ax)*.17,ay+(by-ay)*.17);end=(ax+(bx-ax)*.72,ay+(by-ay)*.72)
   d.line([start,end],fill=(82+k*3,86+k*2,76+k),width=2)
 # Three brush fields, confined to natural fracture shoulders.
 for cx,cy,wx,hy in [(213,90,84,30),(240,340,112,35),(451,208,62,44)]:
  for j in range(8):
   yy=cy+j*3;xx=cx+int(8*math.sin(j*1.7+k))
   d.line((xx-wx//2,yy,xx+wx//2-4*j,yy+2),fill=(113+k*3,116+k*2,100+k),width=2)
 save('rock_'+chr(97+k),im)
# Face-top and slab stone have quiet mineral colour plus selective flaked edges.
for name,base in [('rock_top',(121,126,104)),('paving',(139,133,111)),('tread',(140,138,117)),('soil',(109,108,76))]:
 im=Image.new('RGB',(256,256),base);d=ImageDraw.Draw(im)
 for pts,delta in [([(0,0),(160,0),(188,39),(70,83),(0,55)],7), ([(149,96),(255,70),(255,163),(216,181),(163,139)],-6), ([(0,172),(98,181),(154,235),(105,255),(0,255)],-4)]:
  d.polygon(pts,fill=tuple(c+delta for c in base))
 if name in ['paving','tread']:
  d.line([(8,14),(76,10),(110,15)],fill=tuple(c+15 for c in base),width=3)
  d.line([(199,6),(192,26),(209,35)],fill=tuple(c-22 for c in base),width=2)
  d.line([(13,205),(28,192),(53,198)],fill=tuple(c-16 for c in base),width=2)
 save(name,im)
# Sand broad tonal sweeps are intentionally close in value.
im=Image.new('RGB',(512,512),(165,149,115));d=ImageDraw.Draw(im)
for j in range(14):
 y=15+j*36;points=[(x,y+10*math.sin(x/155+j*.37)) for x in range(-100,620,16)]
 d.line(points,fill=(167+j%3,151+j%3,117+j%3),width=8+j%3*3)
save('sand',im.filter(ImageFilter.GaussianBlur(8)))
# Unique ground map in Blender XY: x -20..2, y -4..17. Raster top is +Y.
N=1536;x=np.linspace(-20,2,N);y=np.linspace(17,-4,N);X,Y=np.meshgrid(x,y)
dist=np.full((N,N),100.,dtype=np.float32)
for ei in [2,3,7,8,9,10,11,12]:
 a,b=[layout['anchors'][k] for k in layout['edges'][ei]];ax,ay=a[0],-a[2];bx,by=b[0],-b[2]
 vx,vy=bx-ax,by-ay;t=np.clip(((X-ax)*vx+(Y-ay)*vy)/(vx*vx+vy*vy),0,1)
 dist=np.minimum(dist,np.hypot(X-ax-vx*t,Y-ay-vy*t))
edge=.06*np.sin(X*3.7+Y*2.1)+.04*np.sin(Y*6.3-X*4.2)
path=1-np.clip((dist+edge-.51)/.60,0,1);path=path*path*(3-2*path)
tone=2*np.sin(X*.54+Y*.28)+2.2*np.sin(Y*.92-X*.24)
grass=np.stack([80+tone,99+tone,56+tone],axis=-1);earth=np.array([117,112,80])
arr=grass*(1-path[...,None])+earth*path[...,None]
outline=json.loads((R/'artifacts/left-finish-review/shore-and-outline.json').read_text())['outline']
boundary=np.full((N,N),100.,dtype=np.float32)
for a,b in zip(outline,outline[1:]+outline[:1]):
 ax,ay=a;bx,by=b;vx,vy=bx-ax,by-ay;t=np.clip(((X-ax)*vx+(Y-ay)*vy)/(vx*vx+vy*vy),0,1)
 boundary=np.minimum(boundary,np.hypot(X-ax-vx*t,Y-ay-vy*t))
width=.21+.13*np.sin(X*1.67+Y*.82)+.09*np.sin(Y*3.4-X*2.1)
edge_bare=np.clip((width-boundary)/np.maximum(width,.03),0,1)
arr=arr*(1-edge_bare[...,None])+(np.array([122,122,95])+tone[...,None])*edge_bare[...,None]
im=Image.fromarray(np.uint8(np.clip(arr,0,255)));d=ImageDraw.Draw(im)
def px(x,y):return ((x+20)/22*(N-1),(17-y)/21*(N-1))
# Grouped strokes with an open middle, not full-coverage stipple.
for _ in range(820):
 xx=rng.uniform(-19,1);yy=rng.uniform(-3,16);cx,cy=px(xx,yy);ix=int(cx);iy=int(cy)
 if dist[iy,ix]<.62:continue
 base=np.array(im.getpixel((ix,iy)))
 for j in range(rng.randint(3,7)):
  sx=cx+rng.uniform(-13,13);sy=cy+rng.uniform(-6,6);L=rng.uniform(5,12)
  c=tuple(np.clip(base+np.array([13,15,7])*(1 if j%3 else -1),0,255).astype(int))
  d.line([(sx,sy),(sx+L*.3,sy-L*.22),(sx+L,sy-L*.3)],fill=c,width=2)
save('ground_unique',im)
# Recover only controlled brush variation from the supplied painting; broad
# lights and recognisable repeated shapes stay out of the replacement maps.
source=Image.open(R/'assets/layered_island/textures/land.png').convert('RGB')
boxes=[(280,965,413,1083),(343,977,454,1086),(59,969,137,1068),(803,960,847,1048)]
for k,box in enumerate(boxes):
 name='rock_'+chr(97+k);base=Image.open(OUT/(name+'.png')).convert('RGB')
 detail=source.crop(box).convert('L').resize(base.size,Image.Resampling.BICUBIC)
 ar=np.asarray(detail,dtype=float);blur=np.asarray(detail.filter(ImageFilter.GaussianBlur(22)),dtype=float)
 delta=np.clip((ar-blur)*.34,-14,14)
 arr=np.asarray(base,dtype=float)+delta[...,None]
 save(name,Image.fromarray(np.uint8(np.clip(arr,0,255))))
manifest={'method':'Authored restrained fracture planes and intermittent structure strokes; unique top map follows actual path in XY. Rock maps add a limited high-pass brush layer from the supplied land painting; grass is newly painted. Source crop bounds retained in this script.','maps':['rock_a','rock_b','rock_c','rock_d','rock_top','soil','paving','tread','sand','ground_unique'],'ground_mapping':{'x':[-20,2],'y':[-4,17]},'hashes':{}}
for n in manifest['maps']:manifest['hashes'][n]=hashlib.sha256((OUT/(n+'.png')).read_bytes()).hexdigest()
(OUT/'REFINED_SOURCE.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Painted structural materials and unique ground/path map')
