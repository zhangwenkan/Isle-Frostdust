"""Edge-color dilation for transparent Blender renders; no new geometry or AI art."""
from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib
R=Path(__file__).resolve().parents[1];A=R/'assets/bamboo_depth';O=R/'artifacts/bamboo-mist-depth-review'
status=json.loads((O/'bake-status.json').read_text(encoding='utf-8'));assert status['status']=='complete'
records=[]
for p in sorted(A.glob('*_*.png')):
    if not p.stem.endswith(('_normal','_color')):continue
    raw=O/'raw-bakes'/p.name;raw.parent.mkdir(exist_ok=True)
    image=np.array(Image.open(p).convert('RGBA'));Image.fromarray(image).save(raw)
    alpha=image[:,:,3].copy();mask=alpha>32
    valid=mask.copy()
    for step in range(12):
        expanded=valid.copy();rgb=image[:,:,:3].copy()
        for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]:
            neighbor=np.roll(valid,(dy,dx),(0,1))
            if dy>0:neighbor[:dy]=False
            elif dy<0:neighbor[dy:]=False
            if dx>0:neighbor[:,:dx]=False
            elif dx<0:neighbor[:,dx:]=False
            select=(~expanded)&neighbor
            moved=np.roll(image[:,:,:3],(dy,dx),(0,1));rgb[select]=moved[select];expanded|=select
        image[:,:,:3]=rgb;valid=expanded
    edge=valid&(~mask)
    assert np.array_equal(image[:,:,3],alpha)
    Image.fromarray(image).save(p)
    records.append(dict(file=p.name,size=[image.shape[1],image.shape[0]],opaque_pixels=int(mask.sum()),edge_pixels=int(edge.sum()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(A/'SOURCE.json').write_text(json.dumps(dict(source='Project eastern bamboo meshes; lowest complete branch fans removed and baked in Blender MCP',author='tools/blender/bake_depth_bamboo.py',processing='RGBA edge-color dilation only; original alpha unchanged',textures=records),indent=2),encoding='utf-8')
print('PREPARED',len(records),'transparent texture maps')
