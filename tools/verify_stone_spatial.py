"""Check that rock rearrangement preserves all unrelated exported attributes."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/stone-spatial-review'
# Reuse only the GLB reader; the earlier sample's top-level assertions apply
# to its own archived revision, not this task's different change set.
scope={}
source=(ROOT/'tools/verify_colored_ink_sample.py').read_text(encoding='utf-8')
reader=source[source.index('class GLB:'):source.index('\nold=GLB(')]
exec('import json,struct,hashlib\nimport numpy as np\n'+reader,scope)
GLB=scope['GLB']
old=GLB(OUT/'backup/assets/island_blender/nameless_island.glb')
new=GLB(ROOT/'assets/island_blender/nameless_island.glb')
expected={'Fish_Ground_Rock_%02d_Body'%i for i in [0,1,6,9,10,11]}|{'InkSample_Rock_05'}
removed=set(old.nodes)-set(new.nodes)
assert removed==expected,removed^expected
assert set(new.nodes)-set(old.nodes)=={'InkSample_Rock_00'}
changed={'InkSample_Rock_%02d'%i for i in [2,3,4]}
unchanged=[]
for name,node in old.nodes.items():
    if name in removed or name in changed or 'mesh' not in node:continue
    assert old.signature(name)==new.signature(name),'Unexpected geometry/UV/normal/color change: '+name
    unchanged.append(name)
assert 'InkSample_Path_Grass' in unchanged
for name in ['InkSample_Bamboo_%02d'%i for i in [3,4,5]]:assert name in unchanged
report={'removed_nodes':sorted(removed),'new_nodes':['InkSample_Rock_00'],'reshaped_nodes':sorted(changed),'unchanged_exported_meshes':len(unchanged),'terrain_bridge_bamboo_grass_mountain_geometry_and_uv_unchanged':True,'before_western_rocks':10,'after_western_rocks':4}
(OUT/'asset-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
