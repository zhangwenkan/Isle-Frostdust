"""Continuous paint using the previously attributed original/CC0 coastal palette."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'assets/original_coastal_rock';O=R/'artifacts/coast-integration-review'
info=json.loads((O/'integration-authoring.json').read_text(encoding='utf8'));length=info['perimeter_m']
W,H=8192,1024;original=Image.open(A/'warm_rock_sides.png').convert('RGB');tiles=[]
for i in range(15):
    tile=original.crop(((i%4)*1024+88,(i//4)*512,(i%4)*1024+478,(i//4+1)*512)).resize((700,H),Image.Resampling.BICUBIC)
    tiles.append(np.array(tile,dtype=np.float32))
out=np.zeros((H,W,4),dtype=np.uint8);v=np.arange(H)/float(H-1);s=np.arange(W)/float(W-1)*length
for x,u in enumerate(s):
    f=u/6.7;i=int(math.floor(f));t=f-i
    left=tiles[(i*7+3)%15][:,min(699,int(t*699))]
    # Long shared pigment fields span the former stone boundaries.
    if t<.12:
        previous=tiles[((i-1)*7+3)%15][:,min(699,int((.88+t)*699))]
        q=t/.12;q=q*q*(3-2*q);left=previous*(1-q)+left*q
    out[:,x,:3]=np.uint8(np.clip(left,0,255))
    patch=.22+.64*(.5+.5*math.sin(u*.63+1.7))**3
    depth=.018+.12*(1-patch)*(.5+.5*math.sin(u*.83+.8))
    # This is a material blend mask, not alpha transparency.
    threshold=depth/5.6
    q=np.clip((v-(threshold-.006))/.019,0,1);q=q*q*(3-2*q)
    out[:,x,3]=np.uint8((1-q)*(1-patch)*255)
Image.fromarray(out).save(A/'integrated_coast_paint.png')
if not (A/'integrated_coast_contact.png').exists():Image.new('L',(4096,1024),255).save(A/'integrated_coast_contact.png')
print('INTEGRATED_PAINT',length,W,H)
