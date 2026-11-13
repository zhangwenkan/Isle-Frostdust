"""Compare final GLB to the task backup, including terrain and wind attributes."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];O=R/'artifacts/full-island-ink-review'
scope={};source=(R/'tools/verify_colored_ink_sample.py').read_text(encoding='utf-8')
exec('import json,struct,hashlib\nimport numpy as np\n'+source[source.index('class GLB:'):source.index('\nold=GLB(')],scope)
GLB=scope['GLB'];old=GLB(O/'backup/assets/island_blender/nameless_island.glb');new=GLB(R/'assets/island_blender/nameless_island.glb')
assert set(old.nodes)==set(new.nodes),'Unexpected exported node addition/removal'
expected={'Fish_Ground_Rock_%02d_Body'%i for i in [7,8]}|{'Coast_Low_Grass_%02d.003'%i for i in range(11,19)}|{'Depth_Bamboo_Main_%02d'%i for i in range(7,11)}
changed=[];unchanged=[];wind={};float_roundtrips=[]
def equivalent(name):
    if old.signature(name)==new.signature(name):return True
    if len(old.primitives(name))!=len(new.primitives(name)):return False
    for a,b in zip(old.primitives(name),new.primitives(name)):
        if a['attributes'].keys()!=b['attributes'].keys():return False
        for k in a['attributes']:
            if not np.array_equal(old.array(a['attributes'][k]),new.array(b['attributes'][k])):return False
        if not np.array_equal(old.array(a['indices']),new.array(b['indices'])):return False
    delta=0.
    for k in ['matrix','translation','rotation','scale']:
        a=old.nodes[name].get(k);b=new.nodes[name].get(k)
        if (a is None)!=(b is None):return False
        if a is not None:
            d=float(np.max(np.abs(np.array(a)-np.array(b))));delta=max(delta,d)
            if d>1e-6:return False
    float_roundtrips.append({'object':name,'max_transform_component_delta':delta,'mesh_attributes_exact':True})
    return True
for name,node in old.nodes.items():
    if 'mesh' not in node:continue
    if equivalent(name):unchanged.append(name)
    else:changed.append(name)
    for p in new.primitives(name):
        for k,i in p['attributes'].items():assert np.isfinite(new.array(i)).all(),(name,k)
    if name.startswith(('Coast_Low_Grass_','Depth_Bamboo_Main_','ForestVisibility_')) or name=='InkSample_Path_Grass':
        for p in new.primitives(name):
            mat=new.doc['materials'][p['material']]['name']
            if mat not in ['InkSample_Grass','InkSample_Bamboo_Stem','InkSample_Bamboo_Leaf']:continue
            assert 'TEXCOORD_1' in p['attributes'],(name,mat)
            a=new.array(p['attributes']['TEXCOORD_1'])[:,0]
            assert a.min()>=0 and a.max()<=1.001
            w=wind.setdefault(name,{'fixed_vertices':0,'moving_vertices':0})
            w['fixed_vertices']+=int(np.count_nonzero(a<.001));w['moving_vertices']+=int(np.count_nonzero(a>.1))
assert set(changed)==expected,(set(changed)-expected,expected-set(changed))
assert all(d['fixed_vertices']>0 and d['moving_vertices']>0 for d in wind.values())
for name in new.nodes:
    assert not name.startswith(('FullInkBaseline_','RoundBaseline_','PlaneBaseline_'))
mesh_geometry_preserved={n:old.signature(n)==new.signature(n) for n in unchanged}
report={'exported_meshes':len(changed)+len(unchanged),'changed_meshes':changed,'unchanged_meshes':len(unchanged),
 'terrain_bridge_mountains_water_geometry_unchanged':all(n in unchanged for n in old.nodes if n.startswith(('Fish_West_Continuous','Fish_East_Continuous','Bridge_','Mist_Ridge_','ForestVisibility_Creek'))),
 'wind':wind,'all_attributes_finite':True,'node_set_unchanged':True,'transform_float_roundtrips':float_roundtrips}
(O/'asset-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='wind'},ensure_ascii=False));print('Wind meshes',len(wind))
