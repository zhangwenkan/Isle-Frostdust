"""Paint a shared stone/soil/grass field using existing images and UV data."""
from pathlib import Path
import numpy as np,json,sys
from PIL import Image
R=Path(__file__).resolve().parents[1];TIP='tip' in sys.argv
O=R/('assets/layered_island/forest_tip_extension' if TIP else 'assets/layered_island/cape_forest_transition');O.mkdir(exist_ok=True)
src=np.load(R/'artifacts/cape-forest-continuity-review/forest_uv_source.npz')
W=1152;H=1536;xmin=-74.;xmax=-50.;ymin=-5.;ymax=28.
if TIP:W=1536;H=1792;xmin=-84.;ymax=35.
xs=np.linspace(xmin,xmax,W);ys=np.linspace(ymax,ymin,H);X,Y=np.meshgrid(xs,ys)
UV=np.full((H,W,2),np.nan,dtype=np.float32);Z=np.full((H,W),-100.,dtype=np.float32)
for co,uv in zip(src['positions'],src['uv']):
    x0=max(0,int(np.floor((co[:,0].min()-xmin)/(xmax-xmin)*(W-1))));x1=min(W-1,int(np.ceil((co[:,0].max()-xmin)/(xmax-xmin)*(W-1))))
    y0=max(0,int(np.floor((ymax-co[:,1].max())/(ymax-ymin)*(H-1))));y1=min(H-1,int(np.ceil((ymax-co[:,1].min())/(ymax-ymin)*(H-1))))
    if x1<x0 or y1<y0:continue
    px=X[y0:y1+1,x0:x1+1];py=Y[y0:y1+1,x0:x1+1]
    a,b,c=co;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-8:continue
    l0=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den
    l1=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den;l2=1-l0-l1
    zz=l0*a[2]+l1*b[2]+l2*c[2];region=Z[y0:y1+1,x0:x1+1]
    mask=(l0>=-1e-5)&(l1>=-1e-5)&(l2>=-1e-5)&(zz>region)
    val=l0[...,None]*uv[0]+l1[...,None]*uv[1]+l2[...,None]*uv[2]
    UV[y0:y1+1,x0:x1+1][mask]=val[mask];region[mask]=zz[mask]
# Continue the registered western painting into new land, extrapolating the
# nearest valid strip's UV direction. This is material data, not new geometry.
valid_rows=[]
for j in range(H):
    ids=np.flatnonzero(np.isfinite(UV[j,:,0]))
    if len(ids)<2:continue
    valid_rows.append(j);left=int(ids[0]);right=int(ids[-1]);next_id=int(ids[min(len(ids)-1,24)])
    if left>0:
        if TIP:
            # This is a unique painted atlas, not a seamless tiling texture.
            # Continue the nearest original strip by reflection; extrapolated
            # negative U would wrap onto the opposite edge and form a stripe.
            for axis in range(2):
                UV[j,:left,axis]=np.interp(2*left-np.arange(left),ids,UV[j,ids,axis])
        else:
            slope=(UV[j,next_id]-UV[j,left])/(next_id-left)
            UV[j,:left]=UV[j,left]+(np.arange(left)-left)[:,None]*slope
    if right<W-1:UV[j,right+1:]=UV[j,right]
    for axis in range(2):
        vals=UV[j,:,axis];good=np.flatnonzero(np.isfinite(vals));UV[j,:,axis]=np.interp(np.arange(W),good,vals[good])
for j in range(H):
    if not np.isfinite(UV[j,0,0]):UV[j]=UV[min(valid_rows,key=lambda k:abs(k-j))]
def sample(path,u,v,repeat=False):
    im=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)/255.
    if repeat:u=np.mod(u,1);v=np.mod(v,1)
    else:u=np.clip(u,0,1);v=np.clip(v,0,1)
    xx=u*(im.shape[1]-1);yy=v*(im.shape[0]-1);i=np.floor(xx).astype(int);j=np.floor(yy).astype(int)
    a=(xx-i)[...,None];b=(yy-j)[...,None];ii=np.minimum(i+1,im.shape[1]-1);jj=np.minimum(j+1,im.shape[0]-1)
    return ((im[j,i]*(1-a)+im[j,ii]*a)*(1-b)+(im[jj,i]*(1-a)+im[jj,ii]*a)*b)
forest=sample(R/'assets/layered_island/forest_extension/forest_floor.png',UV[...,0],1-UV[...,1],True)
stone=sample(R/'assets/layered_island/reference_cape/platform.png',(X+84)/17,(18-Y)/13)*.93
def sm(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
edge=X+.75*np.sin(Y*.32+.7)+.35*np.sin(Y*.67-1.2)
grass=sm(-70.,-55.,edge)
# Several broad, connected incursions follow the bank. No fine random noise.
for cx,cy,rx,ry,strength in [(-68.9,16.4,2.1,2.6,.26),(-65.5,9.4,2.8,2.5,.22),(-62.3,18.2,2.6,3.0,.17)]:
    grass+=np.exp(-((X-cx)/rx)**2-((Y-cy)/ry)**2)*strength*(1-grass)
center=13.7-1.5*sm(-61.,-69.,X)
road=np.exp(-((Y-center)/1.15)**4)*(1-sm(-61.,-54.5,X))
grass*=1-road*.56*sm(-71.,-68.,X)
grass=np.clip(grass,0,1)
# Soil joins the rock/grass palette along the continuing activity band.
soil=stone*.62+np.array([.38,.34,.24])*.38
rocksoil=stone*(1-(road*.35)[...,None])+soil*(road*.35)[...,None]
color=rocksoil*(1-grass[...,None])+forest*grass[...,None]
if TIP:
    stone=sample(R/'assets/layered_island/reference_cape/platform.png',(X+84)/17,(18-Y)/13)*.93
    grass=sm(-80.0,-73.0,X+.55*np.sin(Y*.38+.8))
    front=(1-sm(7.0,10.0,Y))*(1-sm(-72.0,-67.0,X))*.56
    grass*=1-front
    grass+=np.exp(-((X+78.7)/1.5)**2-((Y-16.0)/2.4)**2)*.22*(1-grass)
    color=stone*(1-grass[...,None])+forest*grass[...,None]
    contact=np.exp(-((X+79.0)/.76)**2-((Y-12.8)/.67)**2)*.37
    color=color*(1-contact[...,None])
Image.fromarray(np.clip(color*255,0,255).astype('uint8')).save(O/('tip_floor.png' if TIP else 'continuity_floor.png'))
(O/'SOURCE.json').write_text(json.dumps({'date':'2026-11-19','bounds':[xmin,ymin,xmax-xmin,ymax-ymin],'source_images':['forest_extension/forest_floor.png','reference_cape/platform.png'],'registration':'Existing Blender UV triangles rasterized; nearest original strip mirrored into new land, avoiding unique atlas wrap' if TIP else 'Existing Blender UV triangles rasterized; western UV direction continued','painting':'Broad irregular grass/soil/stone groups and a continuous walking strip; no added noise, AI images or geometry'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Shared registered floor painting created',W,H)
