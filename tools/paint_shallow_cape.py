"""Paint sparse stone planes into the UV face atlas authored in Blender."""
import json,random,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];A=R/'assets/shallow_cape'
data=json.loads((R/'artifacts/shallow-cape-review/authoring.json').read_text(encoding='utf8'))
N=128;atlas=Image.new('RGB',(N*16,N*16),(93,97,91))
for f in data['atlas']:
 rng=random.Random(1100+f['rock']*57+f['face']*7)
 base=(111,115,99) if f['top'] else (88,94,92)
 if f['bottom']:base=(67,74,74)
 dv=[-2,3,0,-1,2,-2,1,0,2,-1,0,1,0][f['rock']]
 base=tuple(c+dv for c in base)
 tile=Image.new('RGB',(N,N),base);dr=ImageDraw.Draw(tile)
 # Broad mineral washes leave most of each plane quiet. No fine grain overlay.
 for j in range(3 if f['top'] else 2):
  x=rng.randrange(10,90);y=rng.randrange(12,95);w=rng.randrange(29,66);h=rng.randrange(12,29)
  polygon=[(x,y),(x+w*.34,y-3),(x+w*.58,y+2),(x+w,y-1),(x+w-8,y+h*.58),(x+w*.48,y+h),(x+6,y+h-4)]
  delta=([7,-5,4][j] if f['top'] else [5,-4][j]);c=tuple(max(0,min(255,v+delta)) for v in base)
  if f['top'] and j==0:c=(base[0]+9,base[1]+6,base[2]-1)
  dr.polygon(polygon,fill=c)
 # A few angled strokes reveal the largest planes; avoid tracing every face perimeter.
 if not f['bottom'] and f['face']%3==1:
  x=18+rng.randrange(12);y=31+rng.randrange(43);w=36+rng.randrange(28)
  poly=[(x,y),(x+w*.32,y+4),(x+w*.60,y+3),(x+w,y+12),(x+w-2,y+14),(x+w*.55,y+6),(x+w*.24,y+7)]
  dr.polygon(poly,fill=tuple(max(0,v-19) for v in base))
  dr.line([(x+w*.3,y+9),(x+w*.59,y+8),(x+w*.76,y+11)],fill=tuple(v+5 for v in base),width=1)
 # Wide, broken darker patches at selected corners, not a uniform black outline.
 if f['top'] and f['rock'] in [0,1,2,4,7]:
  dr.polygon([(17,88),(35,81),(51,84),(67,101),(58,111),(33,102)],fill=tuple(v-13 for v in base))
 tile=tile.filter(ImageFilter.GaussianBlur(.35))
 atlas.paste(tile,((f['tile']%16)*N,(f['tile']//16)*N))
atlas.save(A/'slab_paint.png')
W,H=1040,880
surface=Image.new('RGBA',(W,H),(111,115,99,255));dr=ImageDraw.Draw(surface)
def point(x,z):return ((x+32)/13*W,(z+5.5)/11*H)
def poly(coords,color):dr.polygon([point(x,z) for x,z in coords],fill=color)
# The crown is largely bare stone; small mineral planes share the slabs' restrained palette.
poly([(-30.3,-2.8),(-28.9,-4.6),(-27,-4.7),(-26.1,-2.9),(-27.6,-1.1),(-29.7,-.5)],(118,119,102,255))
poly([(-30.5,.3),(-29.2,1.0),(-27.4,2.9),(-26.5,3.8),(-28.9,4.4),(-30.7,2.3)],(102,109,98,255))
poly([(-26.7,-.8),(-25,-1.4),(-23.9,.4),(-24.5,2.8),(-26.5,2.3),(-27.6,.8)],(115,119,104,255))
poly([(-29.9,2.7),(-28.2,2.4),(-27.5,3.1),(-28.9,3.5)],(124,125,105,255))
# Selected broken creases; none crosses the character's entire floor as a ruler line.
for line in [[(-29.8,-.3),(-28.9,-.68),(-28.3,-1.8)], [(-28.8,2.6),(-28,1.8),(-27.6,1.1)], [(-25.9,-1.2),(-25.0,-.8),(-24.6,.2)], [(-27.7,2.55),(-26.7,2.22),(-26.1,2.7)]]:
 dr.line([point(x,z) for x,z in line],fill=(74,85,83,255),width=3)
# Grass retreats inland along an uneven boundary with a few shallow lobes.
mask=Image.new('L',(W,H));mp=mask.load()
for j in range(H):
 z=j/H*11-5.5
 boundary=-23.55+.30*math.sin(z*1.25)+.15*math.sin(z*3.2+.7)+(.95 if z>2.25 else 0)
 for i in range(W):
  x=i/W*13-32;t=max(0,min(1,(boundary+.20-x)/.40));mp[i,j]=round(255*t*t*(3-2*t))
surface.putalpha(mask);surface.save(A/'cape_surface.png')
print('Painted',len(data['atlas']),'face panels into',A/'slab_paint.png')
