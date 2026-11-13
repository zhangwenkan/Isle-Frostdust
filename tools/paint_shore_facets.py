"""Original face-specific rock washes. No reference pixels are copied."""
from pathlib import Path
import json,math,random
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];A=R/'assets/shore_facets';A.mkdir(exist_ok=True)
W,H=224,448;COLS,ROWS=6,5
widths=[3.2,2.1,4.4,2.65,1.8,3.6,2.8,4.1,2.0,3.4,2.3,3.8,2.55,3.1,2.2,4.0,2.7,3.5,2.1,3.9,2.5,3.2,1.9,3.7,2.8,4.1,2.4,3.3,2.65,3.4]
design=[];atlas=Image.new('RGB',(W*COLS,H*ROWS))
for i in range(30):
 r=random.Random(2011+i*131)
 shoulder=[.22,.38,.31,.48,.18,.35,.25][i%7]
 ledge=([.34,.46,.57][i%3] if i%4 in [0,1] else None)
 d=dict(id=i,width=widths[i],shoulder=shoulder,ledge=ledge,lean=[-.18,.27,-.32,.13,.36,-.25][i%6],moss_depth=[.11,.07,.16,.09,.13][i%5])
 design.append(d)
 shift=[-5,0,5,-2,3,-4][i%6];base=(105+shift,108+shift,91+shift)
 im=Image.new('RGB',(W,H),base);dr=ImageDraw.Draw(im)
 def poly(points,col):dr.polygon([(int(x*W),int(y*H)) for x,y in points],fill=col)
 # Whole mineral planes, aligned to the authored shoulder and recess.
 poly([(0,0),(.14,0),(.19,.34),(.13,.69),(.17,1),(0,1)],(62+shift,72+shift,65+shift))
 poly([(.14,0),(.30,0),(.35,.24),(.29,.58),(.36,1),(.17,1),(.13,.69),(.19,.34)],(124+shift,128+shift,105+shift))
 poly([(.72,0),(1,0),(1,1),(.80,1),(.85,.73),(.76,.43)],(78+shift,87+shift,75+shift))
 poly([(.34,.08),(.67,.05),(.76,.43),(.70,.75),(.79,1),(.36,1),(.29,.58),(.35,.24)],(110+shift,113+shift,96+shift))
 # A few broad translucent-looking brush planes; no scattered speckle field.
 for j in range(11):
  x=r.uniform(.22,.78);y=r.uniform(.10,.86);ww=r.uniform(.035,.13);hh=r.uniform(.05,.23)
  value=r.choice([-9,-5,5,8]);c=tuple(max(0,v+value) for v in base)
  poly([(x,y),(x+ww*.7,y-.014),(x+ww,y+hh*.3),(x+ww*.72,y+hh),(x+.008,y+hh*.81)],c)
 # Sparse tapered vertical grain follows the planes; ends remain broken.
 for j in range(9):
  x=r.uniform(.20,.82);y=r.uniform(.12,.76);ln=r.uniform(.07,.20)
  c=tuple(v-14 for v in base)
  poly([(x,y),(x+.012,y+.035),(x-.006,y+ln),(x-.014,y+ln*.78)],c)
  if j%3==0:poly([(x+.016,y+.02),(x+.024,y+.02),(x+.012,y+ln*.7)],tuple(v+14 for v in base))
 # A local shelf has a broad upward facing mineral edge, never a full-width stripe.
 if ledge is not None:
  y=ledge;poly([(.24,y-.025),(.65,y-.040),(.83,y+.015),(.75,y+.062),(.38,y+.047)],(142+shift,144+shift,117+shift))
  poly([(.38,y+.047),(.75,y+.062),(.83,y+.015),(.77,y+.087),(.43,y+.077)],(67+shift,78+shift,67+shift))
  dr.line([(int(W*x),int(H*y0)) for x,y0 in [(.29,y-.019),(.49,y-.031),(.64,y-.025)]],fill=(162+shift,161+shift,130+shift),width=2)
 # Two selective clefts; alternate orientations rather than repeat decorative zigzags.
 if i%3==0:
  points=[(.56,.04),(.51,.19),(.54,.25),(.46,.36)]
 else:points=[(.68,.56),(.63,.67),(.65,.72),(.59,.84)]
 dr.line([(int(x*W),int(y*H)) for x,y in points],fill=(63+shift,75+shift,65+shift),width=2)
 # Turf overlaps stone in connected irregular tongues at the actual top edge.
 depth=d['moss_depth'];edge=[(0,0),(1,0),(1,depth*.4)]
 for j in range(12,-1,-1):edge.append((j/12,depth*(.55+.45*r.random())))
 poly(edge,(91+shift,105+shift,61+shift))
 for j in range(8):
  x=r.uniform(.02,.96);y=r.uniform(.004,depth*.68)
  poly([(x,y),(x+.025,y),(x+.035,y+.024),(x+.01,y+.038)],(112+shift,124+shift,76+shift))
 # Lower stone is mildly cooler; do not paint a hard waterline into the atlas.
 pix=im.load()
 for yy in range(H):
  q=max(0,(yy/H-.65)/.35)*.12
  for xx in range(W):
   c=pix[xx,yy];pix[xx,yy]=tuple(int(c[k]*(1-q)+[61,77,71][k]*q) for k in range(3))
 atlas.paste(im,((i%COLS)*W,(i//COLS)*H))
atlas.save(A/'shore_rock_faces.png')
(A/'design.json').write_text(json.dumps(dict(tile=[W,H],grid=[COLS,ROWS],faces=design),indent=2),encoding='utf8')
(A/'SOURCE.md').write_text('Original project texture, authored by tools/paint_shore_facets.py. Structure informed by inspection of Wandering Sword shore meshes; no pixels or mesh data copied from that game. Face-specific color planes, short ledges, restrained vertical grain and turf overlap. Not hand-painted by a human artist.\n',encoding='utf8')
print('PAINTED',atlas.size)
