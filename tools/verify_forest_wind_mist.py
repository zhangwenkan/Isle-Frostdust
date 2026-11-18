"""Read the GLB and compare unrelated meshes, routes, camera and preserved wind X."""
import ast,json,struct,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/forest-wind-mist-review'
tree=ast.parse((ROOT/'tools/audit_west_forest_glb.py').read_text(encoding='utf-8'))
ns={};exec('import json,struct,hashlib',ns)
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name=='load':exec(compile(ast.Module(body=[n],type_ignores=[]),'read_glb','exec'),ns)
before=ns['load'](OUT/'before/layered_island.glb');after=ns['load'](ROOT/'assets/layered_island/layered_island.glb')
changed=set(json.loads((OUT/'blender-refine.json').read_text(encoding='utf-8'))['changed_existing'])
protected=set(before)-changed
def wind_x(path):
    data=path.read_bytes();length,_=struct.unpack_from('<II',data,12)
    doc=json.loads(data[20:20+length]);offset=20+length
    length,_=struct.unpack_from('<II',data,offset);binary=data[offset+8:offset+8+length]
    result={}
    for node in doc['nodes']:
        if 'mesh' not in node or 'Leaf' not in node.get('name',''):continue
        parts=[]
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            a=doc['accessors'][primitive['attributes']['TEXCOORD_1']]
            view=doc['bufferViews'][a['bufferView']]
            assert a['componentType']==5126 and a['type']=='VEC2'
            start=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',8)
            parts.append(hashlib.sha256(b''.join(binary[start+i*stride:start+i*stride+4] for i in range(a['count']))).hexdigest())
        result[node['name']]=parts
    return result
old_x=wind_x(OUT/'before/layered_island.glb');new_x=wind_x(ROOT/'assets/layered_island/layered_island.glb')
old=json.loads((OUT/'before/layout.json').read_text(encoding='utf-8'));new=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
report={'protected_objects':len(protected),'unexpected_changes':[n for n in protected if before[n]!=after.get(n)],'new_objects':sorted(set(after)-set(before)),
        'routes_camera_unchanged':all(old[k]==new[k] for k in ['anchors','edges','camera']),
        'leaf_positions_normals_preserved':all(all([p[k] for p in before[n]['parts']] == [p[k] for p in after[n]['parts']] for k in ['POSITION','NORMAL','TEXCOORD_0']) for n in changed if 'Leaf' in n),
        'leaf_wind_x_preserved':old_x==new_x}
(OUT/'geometry-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report));assert not report['unexpected_changes'];assert report['routes_camera_unchanged']
assert report['leaf_positions_normals_preserved'];assert report['leaf_wind_x_preserved']
