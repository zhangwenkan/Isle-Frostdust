"""Author a restrained brush palette for the western sample, without source-game imagery.

Brush paths, palette and distribution are editable here. This paints texture maps only;
all geometry and UV authoring is performed separately inside Blender through MCP.
"""
from pathlib import Path
import math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/colored_ink_sample'
OUT.mkdir(parents=True,exist_ok=True)
rng=random.Random(11826)

def bezier(a,b,c,n=24):
    return [((1-t)**2*a[0]+2*(1-t)*t*b[0]+t*t*c[0],(1-t)**2*a[1]+2*(1-t)*t*b[1]+t*t*c[1]) for t in np.linspace(0,1,n)]

def brush(draw,points,width,fill):
    # Tapered pressure stroke with broad belly and a lifted, pointed end.
    left=[];right=[]
    for i,p in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx,dy=b[0]-a[0],b[1]-a[1];length=max(.001,math.hypot(dx,dy))
        t=i/(len(points)-1);w=width*(.22+.78*math.sin(math.pi*t)**.65)*(1-.80*t)
        left.append((p[0]-dy/length*w,p[1]+dx/length*w));right.append((p[0]+dy/length*w,p[1]-dx/length*w))
    draw.polygon(left+right[::-1],fill=fill)

W,H=3072,1536
xx=np.linspace(-20,6,W,dtype=np.float32)[None,:]
zz=np.linspace(-7,7,H,dtype=np.float32)[:,None]
path=.4+np.sin(xx*.25)*.44
edge=.12*np.sin(xx*2.3+zz*3.2)+.065*np.sin(xx*5.7-zz*4.1)+.045*np.sin(xx*12.4+zz*7.8)
road=np.clip((.82+edge-np.abs(zz-path))/.32,0,1)
road=road*road*(3-2*road)
wash=(np.sin(xx*.6+zz*.8)+.55*np.cos(xx*1.2-zz*.45)+.3*np.sin(xx*2.4+zz*1.8))/1.85
grass=np.zeros((H,W,3),np.float32)+[111,137,90]
grass+=wash[:,:,None]*np.array([10,9,8])
dirt=np.zeros_like(grass)+[165,151,119]
dirt+=(np.sin(xx*.9+zz*.6)*2.5+np.cos(xx*2.0+zz*.9)*1.3)[:,:,None]
paint=Image.fromarray(np.uint8(np.clip(grass*(1-road[:,:,None])+dirt*road[:,:,None],0,255))).convert('RGBA')
strokes=Image.new('RGBA',(W,H));d=ImageDraw.Draw(strokes)
def screen(x,z):return ((x+20)/26*W,(z+7)/14*H)

# Broad transparent leaf/grass washes. Avoid granular, uniform full-surface noise.
for i in range(210):
    x=rng.uniform(-20,6);z=rng.uniform(-7,7)
    if abs(z-(.4+math.sin(x*.25)*.44))<.85:continue
    u,v=screen(x,z);sx=rng.uniform(28,95);sy=rng.uniform(12,39)
    hue=rng.choice([(43,78,64,19),(137,151,104,23),(59,100,80,24)])
    d.ellipse((u-sx,v-sy,u+sx,v+sy),fill=hue)
paint=Image.alpha_composite(paint,strokes.filter(ImageFilter.GaussianBlur(9)))
strokes=Image.new('RGBA',(W,H));d=ImageDraw.Draw(strokes)
count=0
for i in range(7800):
    x=rng.uniform(-20,6);z=rng.uniform(-7,7);dist=abs(z-(.4+math.sin(x*.25)*.44))
    if dist<.58:continue
    # Clumps gather around the path and in loose bands, leaving calm patches.
    weight=.84 if dist<1.25 else .38+.28*math.sin(x*.85+z*.90)*math.cos(x*.32-z*1.1)
    if rng.random()>weight:continue
    u,v=screen(x,z);length=rng.uniform(8,27);lean=rng.uniform(-9,9)
    for j in range(rng.randint(2,7)):
        a=(u+rng.uniform(-9,9),v+rng.uniform(-2,4))
        side=(j-2)*rng.uniform(2.5,4.8)+lean
        c=(a[0]+side,a[1]-length*rng.uniform(.6,1.1))
        b=(a[0]+side*.23,a[1]-length*.56)
        pigment=rng.choice([(52,79,47,58),(70,96,53,80),(158,168,106,85),(83,111,65,73)])
        brush(d,bezier(a,b,c),rng.uniform(1.1,2.5),pigment)
    count+=1
# A few long, nearly dry marks along the trail; no gravel carpet.
for i in range(85):
    x=rng.uniform(-20,6);z=.4+math.sin(x*.25)*.44+rng.uniform(-.42,.42)
    u,v=screen(x,z)
    brush(d,bezier((u,v),(u+9,v-1),(u+22,v+rng.uniform(-3,3))),1.4,(104,100,79,36))
paint=Image.alpha_composite(paint,strokes)
paint.convert('RGB').save(OUT/'ground_brush_color.png')
strokes.save(OUT/'ground_brush_strokes.png')
Image.fromarray(np.uint8(road*255)).save(OUT/'ground_path_mask.png')

# Authored structural lines for the two leaning rock variants. Coordinates follow
# their frontal UV projection; these are stone folds, not random crack networks.
rock_paths=[
 [[(.12,.63),(.22,.59),(.29,.47),(.34,.38)],[(.31,.39),(.46,.35),(.62,.31),(.75,.21)],[(.72,.15),(.77,.28),(.72,.43),(.77,.58),(.69,.79)],[(.83,.28),(.88,.42),(.83,.57),(.87,.70)],[(.16,.81),(.28,.76),(.39,.66)],[(.45,.52),(.53,.48),(.61,.45)],[(.65,.72),(.61,.85),(.54,.94)]],
 [[(.08,.55),(.23,.48),(.39,.44),(.55,.33)],[(.64,.13),(.69,.30),(.64,.45),(.70,.63),(.66,.83)],[(.83,.33),(.79,.49),(.84,.68)],[(.22,.77),(.36,.67),(.48,.62)],[(.36,.31),(.44,.29),(.56,.23)]]
]
for variant,paths in enumerate(rock_paths):
    N=1024;y,x=np.mgrid[0:N,0:N].astype(np.float32)/N
    # Broad wash follows the rock face, with restrained color pooling on one side.
    value=np.sin(x*5+y*3)*4+np.cos(x*8-y*4)*3
    pooling=np.clip((x-.65)/.3,0,1)*13
    data=np.zeros((N,N,3),np.float32)+[143,151,137]
    data+=(value-pooling)[:,:,None]
    im=Image.fromarray(np.uint8(np.clip(data,0,255))).convert('RGBA')
    wash_layer=Image.new('RGBA',(N,N));wd=ImageDraw.Draw(wash_layer)
    for k in [0,2,3]:
        pts=[(u*N+9,v*N+10) for u,v in paths[k]]
        brush(wd,pts,27 if k==2 else 38,(57,79,64,37))
    im=Image.alpha_composite(im,wash_layer.filter(ImageFilter.GaussianBlur(6)))
    layer=Image.new('RGBA',(N,N));dr=ImageDraw.Draw(layer)
    for k,path in enumerate(paths):
        pts=[(u*N,v*N) for u,v in path]
        fine=[]
        for segment,(a,b) in enumerate(zip(pts,pts[1:])):
            fine.extend([(a[0]+(b[0]-a[0])*t+math.sin(t*math.pi*2+segment)*1.8,a[1]+(b[1]-a[1])*t+math.sin(t*math.pi)*2.0) for t in np.linspace(0,1,20)])
        brush(dr,fine,5.0 if k in [0,2] else 2.3,(33,45,37,230 if k in [0,2] else 180))
        # Diluted adjacent stroke, used only on two major structure marks.
        if k in [0,2]:brush(dr,[(u+7,v) for u,v in fine],6.0,(49,76,67,29))
    im=Image.alpha_composite(im,layer)
    im.convert('RGB').save(OUT/f'rock_brush_{variant}.png')
    layer.save(OUT/f'rock_lines_{variant}.png')

(OUT/'palette-and-layout.json').write_text(json.dumps({'ground_extent_godot_xz':[-20,6,-7,7],'grass_clumps':count,'grass_base_srgb':[111,137,90],'path_base_srgb':[165,151,119],'rock_base_srgb':[143,151,137],'rock_paths_uv':rock_paths,'source':'Original editable brush paths and composited color washes. No reference-game pixels used.'},indent=2),encoding='utf-8')
print('Painted ground, path edges and rock structure maps;',count,'grouped grass strokes')
