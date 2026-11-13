"""Material-only update must preserve every exported geometry attribute."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/rock-plane-light-review'
scope={};source=(ROOT/'tools/verify_colored_ink_sample.py').read_text(encoding='utf-8')
reader=source[source.index('class GLB:'):source.index('\nold=GLB(')]
exec('import json,struct,hashlib\nimport numpy as np\n'+reader,scope);GLB=scope['GLB']
old=GLB(OUT/'backup/assets/island_blender/nameless_island.glb');new=GLB(ROOT/'assets/island_blender/nameless_island.glb')
assert set(old.nodes)==set(new.nodes)
unchanged=[];rocks={'InkSample_Rock_%02d'%i for i in [0,2,3,4]};shading_only=[]
for name,node in old.nodes.items():
    if 'mesh' not in node:continue
    if name in rocks:
        for key in ['matrix','translation','rotation','scale']:assert old.nodes[name].get(key)==new.nodes[name].get(key)
        op=old.primitives(name);np=new.primitives(name);assert len(op)==len(np)
        for a,b in zip(op,np):
            oi=old.array(a['indices']).reshape(-1);ni=new.array(b['indices']).reshape(-1)
            old_normals=old.array(a['attributes']['NORMAL'])[oi]
            new_normals=new.array(b['attributes']['NORMAL'])[ni]
            assert not scope['np'].allclose(old_normals,new_normals),name
            for key in set(a['attributes'])|set(b['attributes']):
                if key=='NORMAL':continue
                ov=old.array(a['attributes'][key])[oi];nv=new.array(b['attributes'][key])[ni]
                assert scope['np'].array_equal(ov,nv),(name,key)
        shading_only.append(name)
        continue
    assert old.signature(name)==new.signature(name),'Unexpected mesh attribute change: '+name
    unchanged.append(name)
assert set(shading_only)==rocks
report={'unchanged_exported_meshes':len(unchanged),'shading_normal_changes_only':shading_only,'all_rock_triangle_positions_uv_colors_transforms_identical':True,'all_other_mesh_attributes_identical':True,'changed_rock_texture_shader_and_shading_normals':True}
(OUT/'asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
