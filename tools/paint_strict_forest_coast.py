"""Project-owned surface paintings; this script never creates model geometry."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
R=Path(__file__).resolve().parents[1];T=R/'assets/layered_island/strict_coast';T.mkdir(exist_ok=True)
N=1024
yy,xx=np.mgrid[:N,:N];x=xx/N;y=yy/N
def save_field(name,base,patches):
    a=np.zeros((N,N,3),dtype=float)+base
    for cx,cy,rx,ry,c in patches:
        w=np.exp(-(((x-cx)/rx)**2+((y-cy)/ry)**2)*2)
        a=a*(1-w[:,:,None]*.48)+np.array(c)[None,None,:]*w[:,:,None]*.48
    im=Image.fromarray(np.uint8(np.clip(a,0,255)));im.save(T/name);return im
im=save_field('rock_faces.png',[128,123,103],[(.2,.2,.4,.2,[160,145,113]),(.7,.6,.5,.2,[94,101,87]),(.3,.8,.45,.25,[111,109,96]),(.75,.25,.22,.4,[151,140,114])])
d=ImageDraw.Draw(im)
for pts,w in [([(0,316),(154,328),(320,301),(415,333)],4), ([(518,260),(592,347),(574,407),(655,508)],5), ([(510,618),(384,670),(213,692),(117,754)],4), ([(924,660),(846,768),(857,830),(781,948)],5), ([(174,0),(206,139),(181,241)],3)]:
    d.line(pts,fill=(83,88,76),width=w,joint='curve');d.line([(a-4,b-3) for a,b in pts],fill=(163,149,118),width=2)
for pts in [[(20,465),(178,448),(310,472)],[(620,75),(817,96),(964,73)],[(493,883),(560,861),(711,874)]]:d.line(pts,fill=(142,133,108),width=3)
im.save(T/'rock_faces.png')
save_field('rock_caps.png',[158,146,118],[(.22,.25,.4,.3,[176,156,120]),(.65,.65,.4,.3,[128,129,104]),(.85,.1,.25,.2,[148,142,113])])
im=Image.open(T/'rock_caps.png');d=ImageDraw.Draw(im)
for pts in [[(110,92),(228,247),(242,301),(341,411)],[(799,187),(653,398),(560,424)],[(550,695),(712,676),(806,751)]]:
    d.line(pts,fill=(111,111,91),width=4);d.line([(a+4,b-2) for a,b in pts],fill=(181,163,125),width=2)
im.save(T/'rock_caps.png')
save_field('moss.png',[71,88,32],[(.1,.2,.4,.4,[109,124,46]),(.7,.5,.4,.3,[49,65,27]),(.4,.8,.4,.3,[84,100,34])])
# A leaf's light middle and dark edge follow its actual long axis.
leaf=np.zeros((256,128,3));u=np.linspace(-1,1,128)[None,:];v=np.linspace(0,1,256)[:,None]
for k,b in enumerate([61,91,26]):leaf[:,:,k]=b+(1-u*u)*(20 if k==1 else 9)+v*8
leaf[:,61:65,:]+=np.array([16,18,7]);Image.fromarray(np.uint8(leaf)).save(T/'leaf.png')
save_field('soil.png',[127,107,66],[(.2,.2,.4,.4,[144,122,74]),(.6,.6,.4,.3,[91,91,49]),(.85,.2,.2,.4,[134,115,67])])
s=np.zeros((N,N,3))+[188,159,109]
r=.8*np.sin(x*43+y*9)+.5*np.sin(y*63-x*8)
s+=r[:,:,None]*[1.1,1,.7];s+=y[:,:,None]*[-7,-6,-4]
Image.fromarray(np.uint8(s)).save(T/'sand.png')
# Paint only the terminus portion of the established registered ground map.
floor=Image.open(R/'assets/layered_island/rocky_terminus/floor.png').convert('RGB').resize((2048,2048));d=ImageDraw.Draw(floor)
def uv(px,py):return ((px+68)/18*2048,2048-(py-4)/31*2048)
def poly(points,color):d.polygon([uv(a,b) for a,b in points],fill=color)
poly([(-66.8,11),(-65.6,10),(-63.3,10.8),(-61.7,11.7),(-61.8,14.3),(-63.6,15.4),(-66.3,14.9)],(152,135,95))
poly([(-65.1,13.6),(-63.4,14.2),(-61.1,14.5),(-58.8,14.6),(-55.8,14.6),(-54,14.5),(-54,12.8),(-56.7,12.7),(-59.4,12.8),(-62,12.3)],(143,122,77))
# Broad grass islands and moss intrude into bare stone rather than a straight split.
for i,(cx,cy,rx,ry) in enumerate([(-61,15.5,1.4,.8),(-58.2,15.5,1.3,1),(-60.3,10.9,1.9,.9),(-56.5,11.7,1.8,1.2),(-64.8,16,1,.8),(-58,8.5,1.5,.7)]):
    p=[(cx+rx*np.cos(a)*(1+.10*np.sin(a*3)),cy+ry*np.sin(a)) for a in np.linspace(0,2*np.pi,15)]
    poly(p,[(71,91,31),(81,100,36),(64,85,31)][i%3])
floor.save(T/'floor.png')
(T/'SOURCE.json').write_text(json.dumps({'source':'Project-owned painted fields, selected fracture lines and leaf-axis shading. No reference pixels copied.','author':'tools/paint_strict_forest_coast.py','reference':'artifacts/forest-rocky-terminus-study/reference/user-forest-coast.png','geometry':'Produced separately inside Blender through blender-mcp'},ensure_ascii=False,indent=2),encoding='utf8')
print('STRICT_COAST_PAINT_DONE',T)
