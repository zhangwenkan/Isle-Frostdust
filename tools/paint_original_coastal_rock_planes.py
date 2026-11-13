"""Original plane-aware mineral painting, with no reference-game or photo pixels."""
from pathlib import Path
from PIL import Image, ImageDraw
import random, math, json
R=Path(__file__).resolve().parents[1]; A=R/'assets/original_coastal_rock'
design=json.loads((A/'geometry-design.json').read_text(encoding='utf8'))
W,H=1024,512
atlas=Image.new('RGB',(W*4,H*4)); tops=Image.new('RGB',(1024,1024)); spec=[]
def tint(c,d): return tuple(max(0,min(255,round(c[k]+d[k]))) for k in range(3))
def blend(a,b,t): return tuple(round(a[k]*(1-t)+b[k]*t) for k in range(3))
for i in range(16):
    rng=random.Random(8123+i*97)
    block=design['modules'][min(i//3,4)][i%3]
    profile=design['profiles'][block[-1]]
    lengths=[0.0]
    for j in range(len(profile)):
        x,y=profile[j]; xx,yy=profile[(j+1)%len(profile)]
        lengths.append(lengths[-1]+math.hypot(xx-x,yy-y))
    bounds=[v/lengths[-1] for v in lengths]
    delta=[-3,3,0,5,-2,1,-4,2][i%8]; base=(177+delta,145+delta,121+delta)
    im=Image.new('RGB',(W,H),base); d=ImageDraw.Draw(im)
    seam=[.36,.57,.43,.61,.29,.49,.38,.54,.66,.42,.59,.33,.47,.63,.36][i%15]
    for j in range(len(profile)):
        left=round((.007+.986*bounds[j])*W); right=round((.007+.986*bounds[j+1])*W); width=right-left
        shade=[-7,4,9,-2,-12,1,7,-6,-3][(j+i)%9]; tone=tint(base,(shade,shade,shade*.9))
        d.rectangle((left,0,right,H),fill=tone)
        yy=round((seam+(.10 if j%3==0 else -.04))*H); shift=round(width*.27)*(-1 if i%3==1 else 1)
        d.polygon([(left,yy+shift),(right,yy-shift),(right,H),(left,H)],fill=blend(tone,(113,106,104),.21))
        # Subordinate angular pigment fields leave broad quiet planes.
        for n in range(3):
            x=left+width*rng.uniform(.07,.62); y=H*rng.uniform(.06,.90)
            w=width*rng.uniform(.26,.61); h=H*rng.uniform(.05,.14); value=rng.choice([-8,-5,5,8])
            d.polygon([(x,y),(min(right,x+w*.65),y-h*.14),(min(right,x+w),y+h*.55),
                       (x+w*.28,y+h),(x-width*.04,y+h*.69)],fill=tint(tone,(value,value*.9,value*.8)))
        # Selected short oblique joints: tapered shadow with a broken bright upper edge.
        if (j+i)%4!=0:
            x0=left+width*(.03 if j%2 else .14); x1=right-width*(.04 if j%3 else .26)
            y0=H*(seam+(.06 if j%2 else -.06)); slope=[-.11,.045,-.06,.09,.02][(i+j)%5]*H
            points=[(x0,y0),(x0+(x1-x0)*.32,y0+slope*.25-3),(x0+(x1-x0)*.69,y0+slope*.65+2),(x1,y0+slope)]
            d.line([(x,y-4) for x,y in points[:3]],fill=tint(tone,(21,18,14)),width=5)
            d.polygon(points+[(x1-3,y0+slope+2),(points[2][0]-3,points[2][1]+7),(points[1][0],points[1][1]+5),(x0+3,y0+2)],fill=blend(tone,(73,65,67),.58))
            d.line(points,fill=blend(tone,(77,63,63),.73),width=2)
            if (i+j)%3==0:
                px,py=points[2]
                d.line([(px,py),(px-width*.08,py-H*.06),(px+width*.07,py-H*.14)],fill=blend(tone,(78,67,66),.60),width=3)
        if j in [1,3,6,8]:
            y0=H*(.09+.07*((i+j)%4)); y1=y0+H*(.17+.03*(j%3))
            d.polygon([(left+2,y0),(left+width*.09,y0+12),(left+width*.06,y1),(left+1,y1+8)],fill=blend(tone,(91,83,83),.32))
        # Grouped dry strokes are large enough to be visible at gameplay distance.
        for n in range(3):
            x=left+width*(.18+.24*n); y=H*(.16+.23*((n+j+i)%3))
            for q in range(3+(n%2)):
                xx=x+width*rng.uniform(-.06,.10); yy=y+rng.uniform(-10,10); ln=width*rng.uniform(.05,.18)
                d.line([(xx,yy),(min(right-2,xx+ln),yy-2)],fill=tint(tone,rng.choice([(-15,-13,-10),(18,15,10),(-10,-9,-7)])),width=2+(q%2))
    px=im.load()
    for y in range(H):
        t=max(0,(y/H-.62)/.38)*.20
        if t:
            for x in range(W): px[x,y]=blend(px[x,y],(105,105,106),t)
    atlas.paste(im,((i%4)*W,(i//4)*H))
    top=Image.new('RGB',(256,256),(184+delta,157+delta,129+delta)); td=ImageDraw.Draw(top)
    for n in range(12):
        x=rng.randint(-15,220); y=rng.randint(-15,220); w=rng.randint(25,85); h=rng.randint(12,45)
        c=tint((184+delta,157+delta,129+delta),(rng.choice([-11,-6,7]),)*3)
        td.polygon([(x,y),(x+w*.7,y-7),(x+w,y+h*.6),(x+w*.3,y+h),(x-4,y+h*.5)],fill=c)
    for pts in [[(24,180),(71,156),(112,165),(152,132)],[(152,132),(160,90),(187,61)]]:
        td.line([(x,y-2) for x,y in pts],fill=(200+delta,176+delta,148+delta),width=3)
        td.line(pts,fill=(125+delta,111+delta,104+delta),width=3)
    tops.paste(top,((i%4)*256,(i//4)*256));spec.append(dict(id=i,seam=seam,face_boundaries=bounds))
atlas.save(A/'warm_rock_sides.png'); tops.save(A/'warm_rock_tops.png')
(A/'paint-design.json').write_text(json.dumps(spec,indent=2),encoding='utf8')
(A/'SOURCE.md').write_text('Original project coast assets. Geometry: new explicit profiles authored through Blender MCP. Texture: tools/paint_original_coastal_rock_planes.py, using only our own profile/UV design. Contact shading: Blender AO bake of those original modules. No Wandering Sword geometry, UVs, textures, or photo texture pixels are used. Sea of Stars screenshot is a visual reference only; no pixels were sampled or copied. The artwork is script-authored, not described as human hand-painted. Poly Haven candidates in artifacts were researched but are not incorporated.\n',encoding='utf8')
print('ORIGINAL_PLANE_PAINT',atlas.size,tops.size)
