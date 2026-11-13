"""Read-only GLB comparison and normal/UV/triangle checks."""
from pathlib import Path
import json,struct,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'artifacts/coast-junction-refine-review'
# Reuse the established GLB reader only, without executing its old task assertions.
reader=(R/'tools/verify_original_coast_assets.py').read_text(encoding='utf8')
exec(reader[reader.index('def read(path):'):reader.index('old=read(')])
old=read(O/'backup/nameless_island.glb');new=read(R/'assets/island_blender/nameless_island.glb')
report=json.loads((O/'authoring.json').read_text(encoding='utf8'))
changed=set(report['trimmed_old_meshes']+['Fish_West_Continuous_Land'])
unchanged=[n for n in old[2] if n not in changed]
for n in unchanged:
 assert old[2][n]==new[2].get(n),n
 for key in ['matrix','translation','rotation','scale']:assert old[1][n].get(key)==new[1][n].get(key),(n,key)
triangles=0;bad=[];normal_stats={}
for name in [n for n in new[2] if n in changed or n.startswith('Junction_')]:
 for p in new[0]['meshes'][new[1][name]['mesh']]['primitives']:
  v=new[3](p['attributes']['POSITION']);idx=new[3](p['indices']).reshape(-1,3);norm=new[3](p['attributes']['NORMAL'])
  assert np.isfinite(v).all() and np.isfinite(norm).all()
  cr=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]])
  areas=np.linalg.norm(cr,axis=1)*.5
  if name.startswith('Junction_'):
   assert (areas>1e-10).all(),name
   for key in ['TEXCOORD_0','TEXCOORD_1']:
    uvcheck=new[3](p['attributes'][key]);assert np.isfinite(uvcheck).all() and (uvcheck>=-1e-6).all() and (uvcheck<=1.000001).all(),name
  if name=='Junction_Coast_Sample':
   assert (areas>1e-9).all()
   for key in ['TEXCOORD_0','TEXCOORD_1']:
    uv=new[3](p['attributes'][key]);assert np.isfinite(uv).all() and (uv>=-1e-6).all() and (uv<=1.000001).all()
   uv=new[3](p['attributes']['TEXCOORD_0']);centers=uv[idx].mean(axis=1)
   top=cr[centers[:,1]<.179];front=cr[(centers[:,1]>.23)&(centers[:,1]<.53)]
   normal_stats={'top_up_positive':bool((top[:,1]>0).all()),'main_faces_toward_front':bool((front[:,2]>0).all())}
  elif name.startswith('Integrated_') and (areas<1e-10).any():bad.append((name,int((areas<1e-10).sum())))
  triangles+=len(idx)
assert normal_stats['top_up_positive'],normal_stats
assert normal_stats['main_faces_toward_front'],normal_stats
assert not any(n.startswith(('WS_Reference_Shore_','Cliff_Fern_')) for n in new[2])
result={'unchanged_exported_meshes':len(unchanged),'normals':normal_stats,'checked_triangles':triangles,'tiny_trim_triangles':bad,
 'sample_uv_finite_in_range':True,'sample_no_degenerate_triangles':True,'hanging_ferns_and_borrowed_coast_absent':True,
 'grass_edge_max_error_m':report['grass_edge_max_error_m'],'protected_turf_vertices':report['protected_turf_vertices'],
 'turf_vertices_changed':report['turf_vertices_changed']}
(O/'asset-verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
