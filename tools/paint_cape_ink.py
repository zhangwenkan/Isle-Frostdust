"""Extend the existing western grass/soil brush language to the opening cape.

Texture painting only; vegetation UV/shape changes are authored in Blender MCP.
Reuse the sample's palette, world density, pressure brush and wash proportions.
The old sample and every rock texture remain untouched.
"""
from pathlib import Path
import math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from cape_road_profile import route,road_half_width

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/west_cape'
W,H=1792,1312
rng=random.Random(11826)

def bezier(a,b,c,n=24):
    return [((1-t)**2*a[0]+2*(1-t)*t*b[0]+t*t*c[0],(1-t)**2*a[1]+2*(1-t)*t*b[1]+t*t*c[1]) for t in np.linspace(0,1,n)]

def brush(draw,points,width,fill):
    left=[];right=[]
    for i,p in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx,dy=b[0]-a[0],b[1]-a[1];length=max(.001,math.hypot(dx,dy))
        t=i/(len(points)-1);w=width*(.22+.78*math.sin(math.pi*t)**.65)*(1-.80*t)
        left.append((p[0]-dy/length*w,p[1]+dx/length*w));right.append((p[0]+dy/length*w,p[1]-dx/length*w))
    draw.polygon(left+right[::-1],fill=fill)

def screen(x,z):return ((x+26)/15*W,(z+6)/12*H)
def fade(x):
    t=np.clip((x+24.5)/2.2,0,1);return t*t*(3-2*t)

xx=np.linspace(-26,-11,W,dtype=np.float32)[None,:]
zz=np.linspace(-6,6,H,dtype=np.float32)[:,None]
path=np.array([route(float(x)) for x in xx[0]],dtype=np.float32)[None,:]
width=np.array([road_half_width(float(x)) for x in xx[0]],dtype=np.float32)[None,:]
edge=.12*np.sin(xx*2.3+zz*3.2)+.065*np.sin(xx*5.7-zz*4.1)+.045*np.sin(xx*12.4+zz*7.8)
road=np.clip((width+edge-np.abs(zz-path))/.32,0,1)
road=road*road*(3-2*road)*fade(xx)
wash=(np.sin(xx*.6+zz*.8)+.55*np.cos(xx*1.2-zz*.45)+.3*np.sin(xx*2.4+zz*1.8))/1.85
grass=np.zeros((H,W,3),np.float32)+[111,137,90]
grass+=wash[:,:,None]*np.array([10,9,8])
dirt=np.zeros_like(grass)+[165,151,119]
dirt+=(np.sin(xx*.9+zz*.6)*2.5+np.cos(xx*2+zz*.9)*1.3)[:,:,None]
paint=Image.fromarray(np.uint8(np.clip(grass*(1-road[:,:,None])+dirt*road[:,:,None],0,255))).convert('RGBA')
layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
for i in range(round(210*180/364)):
    x=rng.uniform(-26,-11);z=rng.uniform(-6,6)
    if abs(z-route(x))<road_half_width(x) and fade(x)>.4:continue
    u,v=screen(x,z);sx=rng.uniform(28,95);sy=rng.uniform(12,39)
    d.ellipse((u-sx,v-sy,u+sx,v+sy),fill=rng.choice([(43,78,64,19),(137,151,104,23),(59,100,80,24)]))
paint=Image.alpha_composite(paint,layer.filter(ImageFilter.GaussianBlur(9)))
layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer);count=0
for i in range(round(7800*180/364)):
    x=rng.uniform(-26,-11);z=rng.uniform(-6,6);dist=abs(z-route(x));width=road_half_width(x)
    if dist<width-.24 and rng.random()<fade(x):continue
    weight=.84 if width-.24<dist<width+.43 else .38+.28*math.sin(x*.85+z*.90)*math.cos(x*.32-z*1.1)
    if rng.random()>weight:continue
    u,v=screen(x,z);length=rng.uniform(8,27);lean=rng.uniform(-9,9)
    for j in range(rng.randint(2,7)):
        a=(u+rng.uniform(-9,9),v+rng.uniform(-2,4));side=(j-2)*rng.uniform(2.5,4.8)+lean
        c=(a[0]+side,a[1]-length*rng.uniform(.6,1.1));b=(a[0]+side*.23,a[1]-length*.56)
        brush(d,bezier(a,b,c),rng.uniform(1.1,2.5),rng.choice([(52,79,47,58),(70,96,53,80),(158,168,106,85),(83,111,65,73)]))
    count+=1
for i in range(40):
    x=rng.uniform(-23,-11);z=route(x)+rng.uniform(-.42,.42)
    u,v=screen(x,z);brush(d,bezier((u,v),(u+9,v-1),(u+22,v+rng.uniform(-3,3))),1.4,(104,100,79,round(36*fade(x))))
Image.alpha_composite(paint,layer).convert('RGB').save(OUT/'cape_turf.png')
layer.save(OUT/'cape_ink_strokes.png')
Image.fromarray(np.uint8(road*255)).save(OUT/'cape_ink_path_mask.png')
(OUT/'cape-ink-palette.json').write_text(json.dumps({'ground_extent_godot_xz':[-26,-11,-6,6],'grass_base_srgb':[111,137,90],'path_base_srgb':[165,151,119],'grass_clumps':count,'reference':'assets/colored_ink_sample/ground_brush_color.png','source':'Same editable pressure strokes and world-scale density as tools/paint_colored_ink_sample.py; no rock texture changes.'},indent=2),encoding='utf-8')
print('Painted cape using western sample palette:',count,'grass clumps')
