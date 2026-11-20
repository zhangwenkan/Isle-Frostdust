"""Broad geological facets and selected weathered fracture relief, no noise fill."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
T=Path(__file__).resolve().parents[1]/'assets/layered_island/strict_coast';N=1024
im=Image.open(T/'rock_faces.png').convert('RGB');height=Image.new('L',(N,N),145);d=ImageDraw.Draw(im);hd=ImageDraw.Draw(height)
facets=[([(0,0),(300,0),(257,201),(70,290),(0,220)],(156,143,119),170),([(300,0),(609,0),(585,220),(431,300),(257,201)],(127,128,114),155),
        ([(609,0),(1024,0),(1024,197),(813,295),(585,220)],(145,139,119),161), ([(0,220),(70,290),(307,269),(350,498),(125,580),(0,452)],(109,114,104),123),
        ([(70,290),(257,201),(431,300),(522,450),(350,498),(307,269)],(169,152,124),170), ([(431,300),(585,220),(813,295),(796,471),(621,568),(522,450)],(139,138,119),150),
        ([(813,295),(1024,197),(1024,484),(880,611),(796,471)],(118,124,111),132), ([(0,452),(125,580),(307,593),(271,805),(89,859),(0,759)],(146,139,118),160),
        ([(125,580),(350,498),(522,450),(621,568),(578,717),(307,593)],(134,135,117),146), ([(307,593),(578,717),(619,890),(398,1024),(221,1024),(271,805)],(114,121,108),129),
        ([(621,568),(796,471),(880,611),(1024,484),(1024,780),(840,871),(578,717)],(156,145,121),164), ([(619,890),(578,717),(840,871),(1024,780),(1024,1024),(398,1024)],(130,131,113),144),
        ([(0,759),(89,859),(271,805),(221,1024),(0,1024)],(162,149,122),163)]
for poly,color,h in facets:
    d.polygon(poly,fill=color);hd.polygon(poly,fill=h)
    # Uneven weathered edge follows the actual plane's leading joint.
    edge=poly[:3];d.line(edge,fill=tuple(max(0,c-37) for c in color),width=7,joint='curve');hd.line(edge,fill=95,width=7,joint='curve')
    d.line([(x+6,y+4) for x,y in edge],fill=tuple(min(255,c+17) for c in color),width=4,joint='curve')
for pts in [[(209,331),(227,409),(213,458),(277,488)],[(702,45),(697,131),(736,186)],[(39,604),(70,667),(62,733)],[(679,777),(733,805),(755,855)]]:
    d.line(pts,fill=(92,101,91),width=5);hd.line(pts,fill=93,width=5)
im=im.filter(ImageFilter.GaussianBlur(.65));im.save(T/'rock_faces.png')
arr=np.asarray(height.filter(ImageFilter.GaussianBlur(2)),dtype=float)/255;dy,dx=np.gradient(arr)
n=np.dstack((-dx*9,-dy*9,np.ones_like(dx)));n/=np.linalg.norm(n,axis=2)[:,:,None];Image.fromarray(np.uint8((n*.5+.5)*255)).save(T/'rock_normal.png')
print('STRICT_ROCK_STRUCTURE_DONE')
