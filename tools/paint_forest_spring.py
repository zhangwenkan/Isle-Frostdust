"""Component paintings for the forest spring. No reference-image pixels used.
Raster brush work only; all model geometry is authored inside Blender via MCP.
"""
from pathlib import Path
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
R=Path(__file__).resolve().parents[1]; A=R/'assets/forest_spring_3d'; A.mkdir(exist_ok=True)
r=random.Random(2411)

def save(im,name):im.save(A/name)
def blend(a,b,t):return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))

# Eight face-specific washes: stone fronts/top faces have separate UV allocations.
im=Image.new('RGB',(1024,512));d=ImageDraw.Draw(im)
for tile in range(8):
 ox=(tile%4)*256;oy=(tile//4)*256
 base=[(114,109,98),(122,121,108),(98,101,98),(117,113,103),(160,154,129),(143,149,125),(149,148,131),(131,141,118)][tile]
 d.rectangle((ox,oy,ox+255,oy+255),fill=base)
 for j in range(10):
  x=r.randrange(245);y=r.randrange(242);w=r.randrange(15,90);h=r.randrange(8,44)
  c=blend(base,(168,166,138) if j%3 else (48,66,68),r.uniform(.045,.10))
  d.polygon([(ox+x,oy+y),(ox+x+w*.8,oy+y-5),(ox+x+w,oy+y+h*.5),(ox+x+w*.55,oy+y+h),(ox+x-10,oy+y+h*.7)],fill=c)
 # Interrupted edge strokes; no uniform outline or crack network.
 for j in range(4):
  x=r.randrange(18,185);y=r.randrange(25,227);ln=r.randrange(22,70)
  points=[(ox+x,oy+y),(ox+x+ln*.55,oy+y-4),(ox+x+ln,oy+y-2)]
  d.line(points,fill=blend(base,(38,55,55),.28),width=2)
  if j%2:d.line([(x,y-2) for x,y in points],fill=blend(base,(190,183,152),.19),width=1)
 # Local moss enters from the top, leaves stone edges bare elsewhere.
 for j in range(4):
  x=r.randrange(15,245);y=r.randrange(4,35 if tile<4 else 95)
  d.polygon([(ox+x,oy+y),(ox+x+17,oy+y-5),(ox+x+26,oy+y+7),(ox+x+14,oy+y+18),(ox+x-6,oy+y+12)],fill=blend(base,(80,108,68),.26))
save(im,'spring_stone_faces.png')

im=Image.new('RGB',(256,512),(101,88,68));d=ImageDraw.Draw(im)
for j in range(13):
 x=j*21+r.randrange(-6,6)
 points=[(x+math.sin(k*.67+j)*10,k*32) for k in range(18)]
 d.line(points,fill=(85+r.randrange(12),78+r.randrange(10),61+r.randrange(9)),width=r.randrange(3,7))
 if j%3:d.line([(x+3,y) for x,y in points[2:10]],fill=(120,104,78),width=2)
for j in range(8):
 x=r.randrange(256);y=r.randrange(512)
 d.arc((x-11,y-30,x+11,y+30),45,290,fill=(63,64,53),width=3)
save(im,'spring_bark.png')

# Four alpha-cutout leafy sprays, with broad grouped values and an open edge.
im=Image.new('RGBA',(512,512));d=ImageDraw.Draw(im)
for tile in range(4):
 ox=tile%2*256;oy=tile//2*256
 clusters=[(126,125,67),(75,150,49),(179,143,52),(140,75,48),(63,90,39),(203,94,36)]
 for cx,cy,rad in clusters:
  poly=[]
  for k in range(28):
   angle=k*math.tau/28;rr=rad*(.81+.12*math.sin(k*2.31+tile))
   poly.append((ox+cx+math.cos(angle)*rr,oy+cy+math.sin(angle)*rr))
  d.polygon(poly,fill=blend((31,58,46),(63,93,56),max(0,(170-cy)/150))+(255,))
  for j in range(95):
   a=r.random()*math.tau;rr=rad*math.sqrt(r.random());x=ox+cx+math.cos(a)*rr;y=oy+cy+math.sin(a)*rr
   sz=r.randrange(3,10);lit=max(0,min(1,(180-(y-oy))/150))
   c=blend((33,61,47),(101,122,70),lit*.52+r.random()*.10)+(255,)
   d.polygon([(x-sz,y),(x-sz*.6,y-sz*.55),(x+sz*.3,y-sz*.65),(x+sz,y-sz*.12),(x+sz*.7,y+sz*.5),(x-sz*.15,y+sz*.65)],fill=c)
   if j%6==0:d.line([(x-sz*.5,y),(x+sz*.5,y-sz*.18)],fill=blend(c,(138,149,89),.18)+(255,),width=1)
save(im,'spring_leaf_sprays.png')

# Grouped short grass and long bank sedge, each with clear alpha margins.
im=Image.new('RGBA',(512,256));d=ImageDraw.Draw(im)
for tile in range(4):
 ox=tile*128
 for j in range(21 if tile<2 else 12):
  bx=ox+r.uniform(40,85);by=r.uniform(221,248);tx=bx+r.uniform(-52,52);ty=r.uniform(45,190) if tile<2 else r.uniform(6,160)
  width=r.uniform(3,7);c=blend((51,83,51),(139,153,87),r.random()*.8)+(255,)
  d.polygon([(bx-width,by),(bx+(tx-bx)*.47-width*.5,(by+ty)*.53),(tx,ty),(bx+(tx-bx)*.6+width*.3,(by+ty)*.53),(bx+width,by)],fill=c)
save(im,'spring_grass.png')

# Registered terrain painting. Coordinates correspond to Blender's X/Z UVs.
W=1536;H=1024
x=np.linspace(23.5,45,W)[None,:];z=np.linspace(-14,7,H)[:,None]
t=np.clip((x-24.2)/(29-24.2),0,1);t=t*t*(3-2*t)
path=(.4+math.sin(24.2*.25)*.44)*(1-t)+2.1*t
t2=np.clip((x-29)/5,0,1);t2=t2*t2*(3-2*t2);path=path+(1.4-2.1)*t2
dist=np.abs(z-path)
broad=(np.sin(x*1.13+np.sin(z*.64))*np.sin(z*1.39-x*.28))
shadow=np.clip((-z-2)/11,0,1)*.35+np.exp(-((x-29.5)/2.4)**2-((z+2)/4)**2)*.24
base=np.zeros((H,W,3),dtype=np.float32)+np.array([94,117,76])
base+=broad[:,:,None]*np.array([3,5,3]);base*=1-shadow[:,:,None]
trail=np.clip((.86+np.sin(x*1.4+z)*.1-dist)/.28,0,1)
base=base*(1-trail[:,:,None])+np.array([151,140,107])*trail[:,:,None]
end=np.clip((x-34.0)/1.1,0,1);end=end*end*(3-2*end)
base=base*(1-(trail*end)[:,:,None])+np.array([92,113,73])*(trail*end)[:,:,None]
q=np.sqrt(((x-35.45)/(3.45*1.22))**2+((z+2.6)/(2.35*1.12))**2)
wet=np.clip((1.23-q)/.28,0,1)
base=base*(1-wet[:,:,None])+np.array([65,92,73])*wet[:,:,None]
im=Image.fromarray(np.clip(base,0,255).astype('uint8'));d=ImageDraw.Draw(im)
for j in range(5500):
 px=r.randrange(W);py=r.randrange(H);wx=23.5+21.5*px/W;wz=-14+21*py/H
 col=im.getpixel((px,py));bright=r.choice([-1,1]);c=tuple(max(0,min(255,v+bright*r.randrange(3,12))) for v in col)
 sz=r.randrange(2,8)
 d.polygon([(px,py),(px+sz*2,py-2),(px+sz,py+3),(px-2,py+2)],fill=c)
save(im,'spring_floor.png')

# Hanging moss: a few broad lobes, matching the field-grass palette.
im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im)
for i in range(13):
 x=18+i*18;bottom=75+int(100*math.sin(i*.65)**2)
 col=blend((55,79,43),(99,117,65),r.random()*.7)+(255,)
 d.polygon([(x-16,7),(x+15,5),(x+17,bottom*.43),(x+7,bottom),(x-2,bottom+12),(x-11,bottom*.68)],fill=col)
 for j in range(7):
  y=r.uniform(14,bottom);xx=x+r.uniform(-10,10)
  d.ellipse((xx-4,y-3,xx+5,y+4),fill=blend(col,(129,141,80),.16)+(255,))
save(im,'spring_moss.png')
print('Spring component paintings written; reference screenshot never read.')
