from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/angular-rock-review'
scope={};source=(ROOT/'tools/verify_colored_ink_sample.py').read_text(encoding='utf-8')
reader=source[source.index('class GLB:'):source.index('\nold=GLB(')]
exec('import json,struct,hashlib\nimport numpy as np\n'+reader,scope);GLB=scope['GLB']
old=GLB(OUT/'backup/assets/island_blender/nameless_island.glb');new=GLB(ROOT/'assets/island_blender/nameless_island.glb')
assert set(old.nodes)==set(new.nodes)
changed={'InkSample_Rock_%02d'%i for i in [0,2,3,4]};unchanged=[]
for name,node in old.nodes.items():
    if name in changed or 'mesh' not in node:continue
    assert old.signature(name)==new.signature(name),'Unexpected change: '+name
    unchanged.append(name)
for name in changed:assert old.signature(name)!=new.signature(name)
for name in ['InkSample_Path_Grass','Fish_West_Continuous_Land','InkSample_Bamboo_03']:assert name in unchanged
old_points=scope['np'].concatenate([old.array(p['attributes']['POSITION']) for p in old.primitives('InkSample_Rock_02')])
new_points=scope['np'].concatenate([new.array(p['attributes']['POSITION']) for p in new.primitives('InkSample_Rock_02')])
old_width=float(scope['np'].ptp(old_points[:,0]));new_width=float(scope['np'].ptp(new_points[:,0]))
assert new_width<old_width*.70,(old_width,new_width)
report={'reshaped_nodes':sorted(changed),'unchanged_exported_meshes':len(unchanged),'main_width_before':old_width,'main_width_after':new_width,'main_width_reduction_percent':100*(1-new_width/old_width),'terrain_bridge_bamboo_grass_mountain_geometry_uv_unchanged':True}
(OUT/'asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
