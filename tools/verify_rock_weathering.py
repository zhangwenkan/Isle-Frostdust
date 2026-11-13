"""Confirm only four rocks changed and the broad footprint stays within tolerance."""
from pathlib import Path
import json,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/rock-weathering-review'
scope={};source=(ROOT/'tools/verify_colored_ink_sample.py').read_text(encoding='utf-8')
reader=source[source.index('class GLB:'):source.index('\nold=GLB(')]
exec('import json,struct,hashlib\nimport numpy as np\n'+reader,scope);GLB=scope['GLB']
old=GLB(OUT/'backup/assets/island_blender/nameless_island.glb');new=GLB(ROOT/'assets/island_blender/nameless_island.glb')
assert set(old.nodes)==set(new.nodes)
rocks={'InkSample_Rock_%02d'%i for i in [0,2,3,4]};unchanged=[];details=[]
for name,node in old.nodes.items():
    if 'mesh' not in node:continue
    if name not in rocks:
        assert old.signature(name)==new.signature(name),'Unexpected change: '+name
        unchanged.append(name);continue
    for key in ['matrix','translation','rotation','scale']:assert old.nodes[name].get(key)==new.nodes[name].get(key)
    a=np.concatenate([old.array(p['attributes']['POSITION']) for p in old.primitives(name)])
    b=np.concatenate([new.array(p['attributes']['POSITION']) for p in new.primitives(name)])
    delta=max(float(np.max(abs(a.min(0)-b.min(0)))),float(np.max(abs(a.max(0)-b.max(0)))))
    assert delta<.065,(name,delta)
    for p in new.primitives(name):
        for k,i in p['attributes'].items():assert np.isfinite(new.array(i)).all(),(name,k)
        color=new.array(p['attributes']['COLOR_0']);assert color[:,:3].min()>.9,(name,color.min())
    details.append({'object':name,'max_bbox_delta_m':delta})
report={'only_four_rocks_changed':True,'unchanged_exported_meshes':len(unchanged),'transforms_unchanged':True,'rock_details':details}
(OUT/'asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
