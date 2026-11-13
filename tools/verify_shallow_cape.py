"""Read-only exported scene/UV/triangle checks against the actual pre-edit GLB."""
from pathlib import Path
import struct,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'artifacts/shallow-cape-review'
src=(R/'tools/verify_original_coast_assets.py').read_text(encoding='utf8')
exec(src[src.index('def read(path):'):src.index('old=read(')])
old=read(O/'backup/nameless_island.glb');new=read(R/'assets/island_blender/nameless_island.glb')
def main_names(doc):
 names=set()
 def walk(i):
  n=doc['nodes'][i]
  if 'mesh' in n:names.add(n['name'])
  for c in n.get('children',[]):walk(c)
 for i in doc['scenes'][doc.get('scene',0)].get('nodes',[]):walk(i)
 return names
scope=json.loads((O/'authoring.json').read_text(encoding='utf8'));changed=set(scope['changed'])
before=main_names(old[0]);after=main_names(new[0]);unchanged=sorted(before-changed)
for n in unchanged:
 assert old[2][n]==new[2].get(n),n
 for k in ['matrix','translation','rotation','scale']:assert old[1][n].get(k)==new[1][n].get(k),(n,k)
count=0
for n in after:
 if not n.startswith('ShallowCape_'):continue
 for p in new[0]['meshes'][new[1][n]['mesh']]['primitives']:
  v=new[3](p['attributes']['POSITION']);idx=new[3](p['indices']).reshape(-1,3);norm=new[3](p['attributes']['NORMAL'])
  assert np.isfinite(v).all() and np.isfinite(norm).all()
  area=np.linalg.norm(np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]]),axis=1)*.5
  assert (area>1e-9).all(),n
  for k in ['TEXCOORD_0','TEXCOORD_1']:
   uv=new[3](p['attributes'][k]);assert np.isfinite(uv).all() and (uv>=0).all() and (uv<=1).all(),(n,k)
  count+=len(idx)
assert len(new[0]['scenes'])==1 and new[0]['scenes'][0]['name']=='Island_Refined'
assert not any(n.startswith(('WS_Reference','Cliff_Fern','SM_XYN','ShallowBaseline_')) for n in after)
out={'preserved_export_meshes':len(unchanged),'bamboo_meshes_unchanged':sum(n.startswith('PixelBamboo_') for n in unchanged),'new_rock_triangles':count,'new_rock_uv_finite_in_range':True,'new_rock_no_degenerate_triangles':True,'only_main_scene_exported':True,'removed_original_cape_meshes':sorted(before-after),'changed_meshes':sorted(changed)}
(O/'asset-verification.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
