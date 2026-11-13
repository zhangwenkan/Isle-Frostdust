"""Extend the existing authored brush palette. Texture painting only."""
from pathlib import Path
import math,random,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];O=R/'assets/full_island_ink';O.mkdir(exist_ok=True)

def curve(a,b,c):
    return [((1-t)**2*a[0]+2*(1-t)*t*b[0]+t*t*c[0],(1-t)**2*a[1]+2*(1-t)*t*b[1]+t*t*c[1]) for t in np.linspace(0,1,18)]

def brush(d,points,width,color):
    left=[];right=[]
    for i,p in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx=b[0]-a[0];dy=b[1]-a[1];n=max(.001,math.hypot(dx,dy));t=i/(len(points)-1)
        w=width*(.22+.78*math.sin(math.pi*t)**.65)*(1-.80*t)
        left.append((p[0]-dy/n*w,p[1]+dx/n*w));right.append((p[0]+dy/n*w,p[1]-dx/n*w))
    d.polygon(left+right[::-1],fill=color)

def paint_ground(name,extent,size,road_enabled,seed):
    rng=random.Random(seed);xmin,xmax,zmin,zmax=extent;W,H=size
    xx=np.linspace(xmin,xmax,W,dtype=np.float32)[None,:];zz=np.linspace(zmin,zmax,H,dtype=np.float32)[:,None]
    path=np.where((xx>=4.5)&(xx<=14),.25,.4+np.sin(xx*.25)*.44)
    edge=.12*np.sin(xx*2.3+zz*3.2)+.065*np.sin(xx*5.7-zz*4.1)+.045*np.sin(xx*12.4+zz*7.8)
    road=np.clip((.82+edge-np.abs(zz-path))/.32,0,1) if road_enabled else np.zeros((H,W),np.float32)
    road=road*road*(3-2*road)
    wash=(np.sin(xx*.6+zz*.8)+.55*np.cos(xx*1.2-zz*.45)+.3*np.sin(xx*2.4+zz*1.8))/1.85
    grass=np.array([111,137,90])+wash[:,:,None]*np.array([10,9,8])
    dirt=np.array([165,151,119])+(np.sin(xx*.9+zz*.6)*2.5+np.cos(xx*2+zz*.9)*1.3)[:,:,None]
    im=Image.fromarray(np.uint8(np.clip(grass*(1-road[:,:,None])+dirt*road[:,:,None],0,255))).convert('RGBA')
    layer=Image.new('RGBA',size);d=ImageDraw.Draw(layer)
    sx=W/(xmax-xmin);sy=H/(zmax-zmin);scale=(sx+sy)/(118.15+109.71)
    def screen(x,z):return ((x-xmin)*sx,(z-zmin)*sy)
    def pathz(x):return .25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
    area=(xmax-xmin)*(zmax-zmin)
    for i in range(round(210*area/364)):
        x=rng.uniform(xmin,xmax);z=rng.uniform(zmin,zmax)
        if road_enabled and abs(z-pathz(x))<.85:continue
        u,v=screen(x,z);rx=rng.uniform(28,95)*scale;ry=rng.uniform(12,39)*scale
        d.ellipse((u-rx,v-ry,u+rx,v+ry),fill=rng.choice([(43,78,64,19),(137,151,104,23),(59,100,80,24)]))
    im=Image.alpha_composite(im,layer.filter(ImageFilter.GaussianBlur(9*scale)))
    layer=Image.new('RGBA',size);d=ImageDraw.Draw(layer);count=0
    for i in range(round(7800*area/364)):
        x=rng.uniform(xmin,xmax);z=rng.uniform(zmin,zmax);dist=abs(z-pathz(x))
        if road_enabled and dist<.58:continue
        weight=.84 if road_enabled and dist<1.25 else .38+.28*math.sin(x*.85+z*.90)*math.cos(x*.32-z*1.1)
        if rng.random()>weight:continue
        u,v=screen(x,z);length=rng.uniform(8,27)*scale;lean=rng.uniform(-9,9)*scale
        for j in range(rng.randint(2,7)):
            a=(u+rng.uniform(-9,9)*scale,v+rng.uniform(-2,4)*scale)
            side=(j-2)*rng.uniform(2.5,4.8)*scale+lean
            brush(d,curve(a,(a[0]+side*.23,a[1]-length*.56),(a[0]+side,a[1]-length*rng.uniform(.6,1.1))),rng.uniform(1.1,2.5)*scale,rng.choice([(52,79,47,58),(70,96,53,80),(158,168,106,85),(83,111,65,73)]))
        count+=1
    if road_enabled:
        for i in range(round(85*(xmax-xmin)/26)):
            x=rng.uniform(xmin,xmax);z=pathz(x)+rng.uniform(-.42,.42);u,v=screen(x,z)
            brush(d,curve((u,v),(u+9*scale,v-scale),(u+22*scale,v+rng.uniform(-3,3)*scale)),1.4*scale,(104,100,79,36))
    Image.alpha_composite(im,layer).convert('RGB').save(O/(name+'.png'))
    layer.save(O/(name+'-strokes.png'))
    return {'name':name,'extent_xz':extent,'size':size,'grass_groups':count,'road':road_enabled}

reports=[paint_ground('east_ground',[-1,29,-7,7],(3584,1536),True,11829),
         paint_ground('valley_turf',[-37,7,-44,0],(4096,4096),False,11830)]

# Broad rock washes carry the same pigment as the current western rocks.
# No crack web, dry-brush flecks or repeated edge outlines are restored.
S=1024;y,x=np.mgrid[0:S,0:S].astype(np.float32)/S
wash=3*np.sin(x*math.tau)*np.cos(y*math.tau)+1.8*np.sin((x+y)*math.tau)
data=np.array([142,153,146])+wash[:,:,None]*np.array([1,.9,.85])
im=Image.fromarray(np.uint8(data)).convert('RGBA');layer=Image.new('RGBA',(S,S));d=ImageDraw.Draw(layer)
for pts,w,c in [([(185,110),(224,245),(288,360),(302,510)],47,(83,111,98,27)),
                 ([(560,270),(627,320),(670,430),(725,540)],65,(172,168,137,24)),
                 ([(367,716),(464,699),(529,734),(588,747)],24,(80,105,94,22))]:
    brush(d,pts,w,c)
Image.alpha_composite(im,layer.filter(ImageFilter.GaussianBlur(8))).convert('RGB').save(O/'cliff_wash.png')
(O/'painting-layout.json').write_text(json.dumps({'ground':reports,'rock_base_srgb':[142,153,146],
 'source':'Original editable pressure strokes and broad washes, extending the existing sample palette. No AI image generation or reference pixels.',
 'rock_scratch_count':0},ensure_ascii=False,indent=2),encoding='utf-8')
print('FULL_INK_PAINT',reports)
