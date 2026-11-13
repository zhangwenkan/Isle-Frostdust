"""Validate imported bridge geometry and the unchanged surrounding GLB assets."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];O=R/'artifacts/ink-bridge-review'
s=(R/'tools/verify_colored_ink_sample.py').read_text(encoding='utf-8');ns={}
exec('import json,struct,hashlib\nimport numpy as np\n'+s[s.index('class GLB:'):s.index('\nold=GLB(')],ns)
GLB=ns['GLB'];old=GLB(O/'backup/assets/island_blender/nameless_island.glb');new=GLB(R/'assets/island_blender/nameless_island.glb')
removed=set(old.nodes)-set(new.nodes)
assert removed=={'Bridge_Plank_Grain_Grooves','Bridge_Wooden_Pegs'},removed
assert not set(new.nodes)-set(old.nodes)
unchanged=[];bridge=[];before_tri=0;after_tri=0
for name,node in old.nodes.items():
    if 'mesh' not in node:continue
    if not name.startswith('Bridge_'):
        assert old.signature(name)==new.signature(name),name
        unchanged.append(name);continue
    before_tri+=sum(len(old.array(p['indices']))//3 for p in old.primitives(name))
    if name in removed:continue
    for p in new.primitives(name):
        after_tri+=len(new.array(p['indices']))//3
        for k,v in p['attributes'].items():assert np.isfinite(new.array(v)).all(),(name,k)
        mat=new.doc['materials'][p['material']]['name'];assert mat.startswith('InkBridge_'),(name,mat)
        assert 'TEXCOORD_0' in p['attributes'],name
    if name.startswith('Bridge_Plank_'):
        a=np.concatenate([old.array(p['attributes']['POSITION']) for p in old.primitives(name)])
        b=np.concatenate([new.array(p['attributes']['POSITION']) for p in new.primitives(name)])
        assert abs(float(a[:,1].max()-b[:,1].max()))<1e-6
    bridge.append(name)
report={'unrelated_exported_meshes_identical':len(unchanged),'bridge_meshes':len(bridge),
 'archived_nodes':sorted(removed),'triangles_before':before_tri,'triangles_after':after_tri,
 'triangle_reduction_percent':100*(1-after_tri/before_tri),'all_bridge_surfaces_use_ink_materials':True,
 'attributes_finite':True,'plank_highest_points_preserved':True}
(O/'asset-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
