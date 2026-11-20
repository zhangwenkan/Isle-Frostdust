"""Registered 2D surface painting from the existing forest and rock images."""
from pathlib import Path
import numpy as np,json
from PIL import Image
R=Path(__file__).resolve().parents[1]
O=R/'assets/layered_island/rocky_terminus';O.mkdir(exist_ok=True)
src=np.load(R/'artifacts/cape-forest-continuity-review/forest_uv_source.npz')
W,H=1024,1536;xmin,xmax,ymin,ymax=-68.,-50.,4.,35.
X,Y=np.meshgrid(np.linspace(xmin,xmax,W),np.linspace(ymax,ymin,H))
UV=np.full((H,W,2),np.nan,dtype=np.float32);Z=np.full((H,W),-100.,dtype=np.float32)
for co,uv in zip(src['positions'],src['uv']):
    x0=max(0,int(np.floor((co[:,0].min()-xmin)/(xmax-xmin)*(W-1))));x1=min(W-1,int(np.ceil((co[:,0].max()-xmin)/(xmax-xmin)*(W-1))))
    y0=max(0,int(np.floor((ymax-co[:,1].max())/(ymax-ymin)*(H-1))));y1=min(H-1,int(np.ceil((ymax-co[:,1].min())/(ymax-ymin)*(H-1))))
    if x1<x0 or y1<y0:continue
    px=X[y0:y1+1,x0:x1+1];py=Y[y0:y1+1,x0:x1+1];a,b,c=co
    den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-8:continue
    l0=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den
    l1=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den;l2=1-l0-l1
    z=l0*a[2]+l1*b[2]+l2*c[2];region=Z[y0:y1+1,x0:x1+1]
    mask=(l0>=-1e-5)&(l1>=-1e-5)&(l2>=-1e-5)&(z>region)
    val=l0[...,None]*uv[0]+l1[...,None]*uv[1]+l2[...,None]*uv[2]
    UV[y0:y1+1,x0:x1+1][mask]=val[mask];region[mask]=z[mask]
valid=[]
for j in range(H):
    ids=np.flatnonzero(np.isfinite(UV[j,:,0]))
    if len(ids)<2:continue
    valid.append(j);left=ids[0]
    for axis in range(2):
        UV[j,:left,axis]=np.interp(2*left-np.arange(left),ids,UV[j,ids,axis])
        vals=UV[j,:,axis];good=np.flatnonzero(np.isfinite(vals));UV[j,:,axis]=np.interp(np.arange(W),good,vals[good])
for j in range(H):
    if not np.isfinite(UV[j,0,0]):UV[j]=UV[min(valid,key=lambda k:abs(k-j))]
def sample(path,u,v,repeat=False):
    im=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)/255.
    u=np.mod(u,1) if repeat else np.clip(u,0,1);v=np.mod(v,1) if repeat else np.clip(v,0,1)
    xx=u*(im.shape[1]-1);yy=v*(im.shape[0]-1);i=np.floor(xx).astype(int);j=np.floor(yy).astype(int)
    a=(xx-i)[...,None];b=(yy-j)[...,None];ii=np.minimum(i+1,im.shape[1]-1);jj=np.minimum(j+1,im.shape[0]-1)
    return (im[j,i]*(1-a)+im[j,ii]*a)*(1-b)+(im[jj,i]*(1-a)+im[jj,ii]*a)*b
def sm(a,b,v):
    t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
forest=sample(R/'assets/layered_island/forest_extension/forest_floor.png',UV[...,0],1-UV[...,1],True)
stone=sample(R/'assets/layered_island/reference_cape/platform.png',(X+68)/14,(19-Y)/13)*.93
rad=np.sqrt(((X+65.0)/2.55)**2+((Y-12.0)/3.1)**2)
rock=1-sm(.74,1.10,rad+.055*np.sin(Y*1.6+X*.4))
for cx,cy,rx,ry,strength in [(-62.4,13.25,2.3,1.0,.82),(-63.5,16.6,1.7,1.2,.65),(-60.3,8.0,2.1,1.5,.88)]:
    rock=np.maximum(rock,np.exp(-((X-cx)/rx)**4-((Y-cy)/ry)**4)*strength)
road=np.exp(-((Y-(13.7-.9*sm(-59,-64,X)))/1.14)**4)
soil=stone*.68+np.array([.35,.31,.22])*.32
rockcolor=stone*(1-road[...,None]*.16)+soil*road[...,None]*.16
rock*=1-sm(-55,-52,X)
color=forest*(1-rock[...,None])+rockcolor*rock[...,None]
contact=np.exp(-((X+64.85)/.74)**2-((Y-13.05)/.67)**2)*.27
color*=1-contact[...,None]
Image.fromarray(np.clip(color*255,0,255).astype('uint8')).save(O/'floor.png')
(O/'SOURCE.json').write_text(json.dumps({'bounds':[xmin,ymin,xmax-xmin,ymax-ymin],'sources':['forest_extension/forest_floor.png','reference_cape/platform.png'],'registration':'Preserved original Blender UV triangles; reflected nearest west strip into new ground','shapes':'One compact camp opening, a path finger and root/near exposed rock groups. No added fine noise.','model_geometry_changed_by_this_script':False},indent=2),encoding='utf8')
print('Painted compact registered floor',W,H)
