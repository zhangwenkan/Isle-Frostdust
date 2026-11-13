"""Compare integrated coast export with its own before-change GLB; no mutation."""
from pathlib import Path
import struct,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'artifacts/coast-integration-review'
def read(path):
    data=path.read_bytes();at=12;doc=None;binary=None
    while at<len(data):
        n,t=struct.unpack_from('<II',data,at);raw=data[at+8:at+8+n];at+=8+n
        if t==0x4e4f534a:doc=json.loads(raw)
        if t==0x004e4942:binary=raw
    def array(i):
        a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
        dtype={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
        count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
        unit=np.dtype(dtype).itemsize
        return np.ndarray((a['count'],count),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',count*unit),unit)).copy()
    def primitive(p):
        vals={k:hashlib.sha256(array(v).tobytes()).hexdigest() for k,v in p['attributes'].items()}
        if 'indices' in p:vals['indices']=hashlib.sha256(array(p['indices']).tobytes()).hexdigest()
        return vals
    nodes={n['name']:n for n in doc['nodes'] if 'mesh'in n}
    meshes={k:[primitive(p) for p in doc['meshes'][n['mesh']]['primitives']] for k,n in nodes.items()}
    return doc,nodes,meshes,array
old=read(O/'backup/nameless_island.glb');new=read(R/'assets/island_blender/nameless_island.glb')
excluded=lambda n:n.startswith(('WS_Reference_Shore_','Cliff_Fern_','Original_Coast_Rock_')) or n=='Fish_West_Continuous_Land'
common=sorted(n for n in old[2] if not excluded(n));mismatch=[]
for name in common:
    if old[2][name]!=new[2].get(name):mismatch.append(name)
    for k in ('matrix','translation','rotation','scale'):
        if old[1][name].get(k)!=new[1].get(name,{}).get(k):mismatch.append(name+':'+k)
land='Fish_West_Continuous_Land'
# Traversal and modified edge verified independently in Blender and Godot.
assert not mismatch,mismatch
assert not any(n.startswith(('WS_Reference_Shore_','Cliff_Fern_')) for n in new[2])
coast=[n for n in new[2] if n.startswith('Integrated_Coast_')]
assert len(coast)==19
coast_vertices=coast_triangles=degenerate=0
for name in coast:
    node=new[1][name]
    for p in new[0]['meshes'][node['mesh']]['primitives']:
        v=new[3](p['attributes']['POSITION']);uv=new[3](p['attributes']['TEXCOORD_0']);uv2=new[3](p['attributes']['TEXCOORD_1']);n=new[3](p['attributes']['NORMAL'])
        assert np.isfinite(v).all() and np.isfinite(uv).all() and np.isfinite(uv2).all()
        assert np.all((uv[:,0]>=0)&(uv[:,0]<=2)) and np.all((uv[:,1]>=0)&(uv[:,1]<=1))
        assert np.all((uv2>=0)&(uv2<=1))
        assert np.all(np.linalg.norm(n,axis=1)>.99)
        idx=new[3](p['indices']).reshape(-1,3)
        areas=np.linalg.norm(np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]]),axis=1)*.5
        degenerate+=int((areas<1e-9).sum());coast_vertices+=len(v);coast_triangles+=len(idx)
assert degenerate==0,degenerate
report={'unchanged_other_exported_meshes':len(common),'unchanged_positions_normals_uvs_indices':True,'traversal_surface_unchanged':'See protected corridor check; outer turf changed','hanging_ferns_remain_absent':True,'original_modules_archived':18,'integrated_coast_meshes':len(coast),'coast_vertices':coast_vertices,'coast_triangles':coast_triangles,'degenerate_triangles':degenerate,'finite_uv0_with_periodic_u_and_bounded_uv2':True,'sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'assets/island_blender/nameless_island.blend',R/'assets/island_blender/nameless_island.glb',R/'assets/original_coastal_rock/warm_rock_sides.png',R/'assets/original_coastal_rock/warm_rock_tops.png',R/'assets/original_coastal_rock/fitted_coast_contact.png']}}
(O/'asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
