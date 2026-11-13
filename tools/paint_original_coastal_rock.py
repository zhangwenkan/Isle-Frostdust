"""Original warm limestone paint, with bounded mineral strokes and selective seams.
No game texture or reference pixels are read. Sea of Stars informs the color hierarchy.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import random,math,json
R=Path(__file__).resolve().parents[1];A=R/'assets/original_coastal_rock';A.mkdir(exist_ok=True)
W,H=1024,512;atlas=Image.new('RGB',(4096,2048));tops=Image.new('RGB',(1024,1024));spec=[]
for i in range(16):
 r=random.Random(5321+i*79);delta=[-4,3,0,6,-2,4,-5,1][i%8]
 base=(181+delta,158+delta,128+delta);im=Image.new('RGB',(W,H),base);dr=ImageDraw.Draw(im)
 # Wide pigment planes, subtle enough that actual lighting remains dominant.
 for j in range(10):
  x=j/10;lean=[.012,-.018,.025,-.01,.018][(j+i)%5]
  value=[-7,2,5,-3,0,4,-5,3,-1,1][(j+i)%10]
  c=(base[0]+value,base[1]+value,base[2]+int(value*.5))
  pts=[(x*W,0),((x+.1)*W,0),((x+.1+lean)*W,H),((x+lean)*W,H)]
  dr.polygon(pts,fill=c)
 # Mineral washes have ragged polygon boundaries and large quiet areas.
 for j in range(26):
  x=r.uniform(0,1);y=r.uniform(.03,.96);w=r.uniform(.025,.09);h=r.uniform(.035,.15)
  v=r.choice([-12,-8,-5,5,7,10]);c=(base[0]+v,base[1]+v,base[2]+int(v*.7))
  dr.polygon([(int(xx*W),int(yy*H)) for xx,yy in [(x,y),(x+w*.7,y-h*.12),(x+w,y+h*.3),(x+w*.84,y+h*.7),(x+w*.30,y+h),(x-.004,y+h*.55)]],fill=c)
 # A few grain groups use compact broken marks, not random full-surface speckling.
 for j in range(18):
  x=r.uniform(.02,.98);y=r.uniform(.08,.92)
  for k in range(r.randint(3,7)):
   xx=x+r.uniform(-.025,.025);yy=y+r.uniform(-.025,.025);ln=r.uniform(.003,.013)
   v=r.choice([-15,-10,10,15]);dr.line([(int(xx*W),int(yy*H)),(int((xx+ln)*W),int((yy-.003)*H))],fill=(base[0]+v,base[1]+v,base[2]+int(v*.6)),width=1 if k%3 else 2)
 # Front-facing strata run only across part of one rock, stop at fracture boundaries.
 seam_y=[.38,.57,.47,.29,.63,.42,.52,.34][i%8]
 ranges=[(.07,.31),(.14,.38),(.22,.43),(.03,.26)][i%4]
 x0,x1=ranges;points=[]
 for j in range(9):
  x=x0+(x1-x0)*j/8;y=seam_y+[.0,.018,.01,.032,.015,-.003,.013,-.005,.008][(j+i)%9]
  points.append((int(x*W),int(y*H)))
 if i%4!=2:
  dr.line([(x,y-3) for x,y in points[:-1]],fill=(205+delta,181+delta,143+delta),width=3)
  dr.line(points,fill=(119+delta,108+delta,100+delta),width=2)
  dr.line([(x,y+3) for x,y in points[2:6]],fill=(147+delta,128+delta,110+delta),width=3)
 # Fine diagonal cleft on one part of the mineral plane; no full-height black division.
 x=.13+.07*(i%4);y=.07+.05*(i%3)
 pts=[(x,y),(x-.009,y+.09),(x+.008,y+.16),(x-.007,y+.24)]
 dr.line([(int(a*W),int(b*H)) for a,b in pts],fill=(124+delta,113+delta,105+delta),width=2)
 dr.line([(int(a*W)+2,int(b*H)) for a,b in pts[:3]],fill=(201+delta,177+delta,144+delta),width=1)
 # Gentle change toward cooler, damp lower stone, with no baked hard waterline.
 px=im.load()
 for y in range(H):
  q=max(0,(y/H-.60)/.4)*.13
  for x in range(W):
   c=px[x,y];px[x,y]=tuple(round(c[k]*(1-q)+[124,123,120][k]*q) for k in range(3))
 atlas.paste(im,((i%4)*W,(i//4)*H))
 top=Image.new('RGB',(256,256),(197+delta,178+delta,145+delta));td=ImageDraw.Draw(top)
 for j in range(16):
  x=r.randint(0,255);y=r.randint(0,255);ww=r.randint(15,65);hh=r.randint(8,35);v=r.choice([-9,-5,4,7]);td.polygon([(x,y),(x+ww,y-5),(x+ww+6,y+hh),(x+8,y+hh+8)],fill=(197+delta+v,178+delta+v,145+delta+v))
 td.line([(20,175),(62,153),(110,162),(145,137)],fill=(145+delta,133+delta,118+delta),width=2)
 td.line([(145,137),(159,89),(179,64)],fill=(151+delta,139+delta,122+delta),width=2)
 tops.paste(top,((i%4)*256,(i//4)*256));spec.append(dict(id=i,seam=seam_y,range=ranges))
atlas.save(A/'warm_rock_sides.png');tops.save(A/'warm_rock_tops.png')
(A/'paint-design.json').write_text(json.dumps(spec,indent=2),encoding='utf8')
(A/'SOURCE.md').write_text('Original project assets. Geometry is authored from new profiles through Blender MCP; textures are created by tools/paint_original_coastal_rock.py. No Wandering Sword geometry, UVs, or texture pixels are used. Sea of Stars screenshot is a visual reference only; no image pixels are sampled or copied. This is script-authored artwork, not human hand-painted work.\n',encoding='utf8')
print('ORIGINAL_ROCK_TEXTURES',atlas.size,tops.size)
