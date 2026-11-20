"""Paint only project-owned raster surfaces. No model geometry is produced."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,runpy
R=Path(__file__).resolve().parents[1];O=R/'assets/layered_island/rocky_terminus'
def atlas(name,base,side=False):
    im=Image.new('RGB',(1024,1024),base);d=ImageDraw.Draw(im)
    # Four deliberately different broad planes; restrained, broken structural brush.
    for j in range(2):
        for i in range(2):
            x=i*512;y=j*512;k=j*2+i
            d.polygon([(x,y+140+k*23),(x+280,y+34),(x+512,y+180),(x+512,y+512),(x,y+512)],fill=tuple(max(0,c-10-k*2) for c in base))
            d.polygon([(x+16,y+22),(x+492,y+28),(x+396,y+210),(x+135,y+155)],fill=tuple(min(255,c+10) for c in base))
            strokes=[[(x+30,y+345),(x+150,y+313),(x+275,y+350)],[(x+351,y+197),(x+405,y+287),(x+450,y+314)]]
            if side:strokes=[[(x+28,y+215),(x+162,y+192),(x+271,y+207)],[(x+309,y+380),(x+404,y+357),(x+487,y+365)]]
            for p in strokes:
                d.line(p,fill=tuple(max(0,c-26) for c in base),width=5)
                q=[(a,b-4) for a,b in p[:2]];d.line(q,fill=tuple(min(255,c+13) for c in base),width=3)
            # A few broad translucent-looking wash marks, no grain/noise fill.
            for n in range(5):
                xx=x+49+n*79;yy=y+430-(n%3)*31
                d.line([(xx,yy),(xx+38,yy-8),(xx+62,yy-2)],fill=tuple(max(0,c-6) for c in base),width=9)
    im.save(O/(name+'.png'))
atlas('rock_planes_top',(157,150,124));atlas('rock_planes_side',(116,112,96),True)
p=runpy.run_path(str(R/'tools/paint_rocky_terminus.py'))
X,Y=p['X'],p['Y'];W,H=p['W'],p['H'];forest=p['forest'];sm=p['sm']
def px(x,y):return ((x+68)/18*(W-1),(35-y)/31*(H-1))
mask=Image.new('L',(W,H));d=ImageDraw.Draw(mask)
outline=[(-68,8),(-66.5,7.3),(-64.8,8.5),(-62.3,8.6),(-60.6,8.3),(-59.3,9.4),(-60.0,10.9),(-59.0,12.6),(-57.8,13.5),(-58.7,14.3),(-60.6,14.2),(-61.5,15.6),(-63.0,15.1),(-64.3,16.0),(-65.6,15.8),(-68,14.9)]
d.polygon([px(x,y) for x,y in outline],fill=255)
for x,y,rx,ry in [(-64.3,17.0,1.5,1.2),(-61.7,17.2,1.8,1.0),(-59.0,16.8,1.6,.8),(-58.8,8.0,1.8,1.1)]:
    a=px(x-rx,y+ry);b=px(x+rx,y-ry);d.ellipse([a,b],fill=230)
mask=mask.filter(ImageFilter.GaussianBlur(5));m=np.asarray(mask)/255.
stone=Image.new('RGB',(W,H),(150,142,115));d=ImageDraw.Draw(stone)
# Large interlocking camp planes, matching the route and natural shelf.
patches=[([(-68,11.2),(-65.9,10.8),(-64.2,11.9),(-63.8,14.2),(-66,15.8),(-68,14.0)],(158,149,122)),([(-65.9,8),(-63.8,8.2),(-62.2,10.1),(-64.2,11.9),(-65.9,10.8)],(137,133,111)),([(-64.2,11.9),(-62.2,10.1),(-60.6,11.6),(-60.5,14.8),(-63.8,14.2)],(148,144,121)),([(-62.2,10.1),(-61.9,8),(-58.5,8),(-59.3,10.8),(-60.6,11.6)],(139,136,111))]
for pts,col in patches:d.polygon([px(x,y) for x,y in pts],fill=col)
for pts in [[(-65.9,10.8),(-64.7,11.45),(-64.2,11.9)],[(-63.8,14.2),(-63.95,13.4)],[(-62.2,10.1),(-61.4,10.8)],[(-63.8,8.2),(-63.2,9.0)]]:
    d.line([px(x,y) for x,y in pts],fill=(103,103,88),width=3)
    d.line([px(x,y+.025) for x,y in pts[:2]],fill=(173,164,132),width=2)
stone=np.asarray(stone,dtype=float)/255.
color=forest*(1-m[...,None])+stone*m[...,None]
# Keep soil on the route as it runs into rock, avoid a separate brown carpet.
road=np.exp(-((Y-(13.7-.9*sm(-59,-64,X)))/.8)**4)*(1-sm(-61,-59,X))
color=color*(1-road[...,None]*.045)
fire=np.exp(-((X+64.85)/.5)**2-((Y-13.05)/.45)**2)
color*=1-fire[...,None]*.15
Image.fromarray(np.clip(color*255,0,255).astype('uint8')).save(O/'floor.png')
Image.fromarray((m*255).astype('uint8')).save(O/'exposed_rock_mask.png')
(O/'rework-source.json').write_text(json.dumps({'date':'2026-11-19','paint':'own broad watercolor planes and selective broken structure strokes','geometry_generated':False,'floor_bounds':[-68,4,18,31],'east_registration':'Original forest raster/UV unchanged beyond blend boundary','reference':'forest-rocky-terminus-study/reference/user-forest-coast.png'},indent=2),encoding='utf8')
print('Painted rocky forest terminus surfaces')
