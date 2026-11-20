"""Edit the existing registered floor painting; no model generation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,random,math
R=Path(__file__).resolve().parents[1];A=R/'assets/layered_island/tripo_replica/textures_wash';A.mkdir(exist_ok=True)
rng=random.Random(191119)
src=Image.open(R/'assets/layered_island/strict_coast/floor.png').convert('RGB');w,h=src.size
orig=np.asarray(src,dtype=np.float32);soft=np.asarray(src.filter(ImageFilter.GaussianBlur(2.8)),dtype=np.float32)
yy,xx=np.mgrid[0:h,0:w];X=xx/(w-1)*18-68;Y=(1-yy/(h-1))*31+4
local=np.clip((X+61)/1.2,0,1)*np.clip((-51.5-X)/2.0,0,1)*np.clip((Y-5)/2,0,1)*np.clip((20-Y)/4,0,1)
base=orig*(1-local[...,None])+(orig*.5+soft*.5)*local[...,None]
def point(x,y):return ((x+68)/18*w,(1-(y-4)/31)*h)
def overlay_polygon(points,color,alpha,blur=0):
    global base
    mask=Image.new('L',(w,h));d=ImageDraw.Draw(mask);d.polygon([point(*p) for p in points],fill=int(alpha*255))
    if blur:mask=mask.filter(ImageFilter.GaussianBlur(blur))
    a=np.asarray(mask,dtype=np.float32)/255*local
    base=base*(1-a[...,None])+np.array(color)*a[...,None]
# Irregular muted green/ochre pools along the slope, separated by quiet grass.
for cx,cy,sx,sy,c,a in [(-58.8,10.8,1.2,1.2,(104,109,67),.26),(-56.9,8.8,1.5,1.2,(92,99,59),.25),(-55.1,7.6,1.6,.9,(100,105,66),.19),(-57.4,15.1,1.1,1.3,(64,81,45),.28),(-54.2,12.0,1.5,.8,(96,105,60),.18)]:
    pts=[(cx+math.cos(i*math.tau/13)*sx*rng.uniform(.68,1.1),cy+math.sin(i*math.tau/13)*sy*rng.uniform(.72,1.1)) for i in range(13)]
    overlay_polygon(pts,c,a,5)
# Broken soil wisps at the grass/route boundary. Existing route stays registered.
for i in range(26):
    x=rng.uniform(-60.1,-52.6);y=13.1+.10*(x+57)+rng.choice([-1,1])*rng.uniform(.35,.75)
    dx=rng.uniform(.13,.38);dy=rng.uniform(.04,.13)
    overlay_polygon([(x-dx,y),(x,y-dy),(x+dx*.7,y+.02),(x+dx*.2,y+dy)],(113,116,77),rng.uniform(.18,.32),1.2)
# Small groups of tapered grass brush strokes; no blanket noise or repeated bands.
im=Image.fromarray(np.uint8(np.clip(base,0,255))).convert('RGBA');paint=Image.new('RGBA',(w,h));draw=ImageDraw.Draw(paint)
for cx,cy in [(-59.0,11.0),(-58.3,12.0),(-57.8,9.4),(-56.8,10.6),(-55.7,7.8),(-55.0,9.6),(-54.2,11.8),(-56.9,15.0),(-54.7,14.8)]:
    for k in range(rng.randint(9,15)):
        x=cx+rng.uniform(-.52,.52);y=cy+rng.uniform(-.34,.34);dx=rng.uniform(.07,.22);dy=rng.uniform(.10,.28)
        color=rng.choice([(120,130,75,75),(50,70,38,70),(137,138,85,62)])
        draw.polygon([point(x-.018,y),point(x+dx*.32,y+dy*.65),point(x+dx,y+dy),point(x+.018,y+.02)],fill=color)
im=Image.alpha_composite(im,paint).convert('RGB');im.save(A/'forest_floor_wash.png')
# A quiet soil/stone painting for the newly exposed continuous slope body.
bw,bh=1024,1024;bank=Image.new('RGB',(bw,bh),(105,111,80));paint=Image.new('RGBA',(bw,bh));d=ImageDraw.Draw(paint)
for cx,cy,sx,sy,c in [(170,250,210,220,(140,137,101,70)),(510,550,280,270,(76,92,76,75)),(850,320,220,260,(132,130,91,65)),(290,820,240,170,(126,119,87,50))]:
    pts=[(cx+math.cos(i*math.tau/11)*sx*rng.uniform(.6,1.15),cy+math.sin(i*math.tau/11)*sy*rng.uniform(.6,1.1)) for i in range(11)];d.polygon(pts,fill=c)
bank=Image.alpha_composite(bank.convert('RGBA'),paint.filter(ImageFilter.GaussianBlur(7)))
d=ImageDraw.Draw(bank)
for i in range(30):
    x=rng.randint(0,bw);y=rng.randint(120,bh);length=rng.randint(30,115)
    d.line([(x,y),(x+length*.4,y-8),(x+length,y-21)],fill=(76,88,69,255),width=rng.choice([1,2,3]))
bank.convert('RGB').save(A/'forest_bank_wash.png')
print('Local floor and bank paintings saved.')
