"""Clean stone pigment with two structural edge accents; no surface scratches."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/colored_ink_sample'
S=512;atlas=Image.new('RGB',(S*4,S*4))
base=np.array([142,153,146],dtype=float)
def stroke(draw,points,width,color):
    left=[];right=[]
    for i,(x,y) in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx,dy=b[0]-a[0],b[1]-a[1];n=max(.01,math.hypot(dx,dy))
        t=i/(len(points)-1);w=width*(.08+.92*math.sin(math.pi*t)**.8)
        left.append((x-dy/n*w,y+dx/n*w));right.append((x+dy/n*w,y-dx/n*w))
    draw.polygon(left+right[::-1],fill=color)
for k in range(16):
    y,x=np.mgrid[0:S,0:S].astype(float)/S
    # Same pigment across faces: illumination, not arbitrary tile values,
    # establishes the large planes. Only a faint broad pigment wash remains.
    wash=1.4*np.exp(-((x-.32)**2/.18+(y-.35)**2/.22))-1.1*np.exp(-((x-.72)**2/.20+(y-.68)**2/.24))
    foot=3.0*np.clip((y-.72)/.24,0,1) if k<9 else 0
    tile=Image.fromarray(np.uint8(np.clip(base+wash[:,:,None]-np.asarray(foot)[...,None],0,255))).convert('RGBA')
    marks=Image.new('RGBA',(S,S));d=ImageDraw.Draw(marks)
    if k==2:
        stroke(d,[(43,27),(85,29),(132,27),(185,30),(222,28)],3.6,(199,203,183,125))
        stroke(d,[(27,31),(30,66),(28,101),(29,121)],2.3,(193,198,179,85))
    if k==4:
        stroke(d,[(289,29),(329,27),(370,30),(399,29)],2.6,(195,201,181,86))
    # The only dark accent is a short buried-foot contact, not a perimeter.
    if k==3:
        stroke(d,[(296,469),(329,467),(356,470)],1.4,(83,104,91,58))
    tile=Image.alpha_composite(tile,marks.filter(ImageFilter.GaussianBlur(.65)))
    atlas.paste(tile.convert('RGB'),((k%4)*S,(k//4)*S))
atlas.save(OUT/'rock_plane_values.png')
(OUT/'rock_plane_values.json').write_text(json.dumps({'base_srgb':[142,153,146],'surface_scratch_count':0,'strategy':'Shared pigment; shape-normal illumination, two selected pale edge accents and one foot contact','source':'Original authored texture, no reference pixels'},indent=2),encoding='utf-8')
print(OUT/'rock_plane_values.png')
