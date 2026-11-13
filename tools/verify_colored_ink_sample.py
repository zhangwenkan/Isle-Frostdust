"""Compare authored GLBs and validate the sample's geometry/UV preservation."""
from pathlib import Path
import json, struct, hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/colored-ink-sample-review'

class GLB:
    def __init__(self,path):
        with path.open('rb') as f:
            f.read(12);n,t=struct.unpack('<II',f.read(8));self.doc=json.loads(f.read(n))
            n,t=struct.unpack('<II',f.read(8));self.bin=f.read(n)
        self.nodes={n.get('name'):n for n in self.doc['nodes']}
    def array(self,index):
        a=self.doc['accessors'][index];v=self.doc['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2'}[a['componentType']]
        size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        offset=v.get('byteOffset',0)+a.get('byteOffset',0)
        stride=v.get('byteStride',np.dtype(dtype).itemsize*size)
        return np.ndarray((a['count'],size),dtype=dtype,buffer=self.bin,offset=offset,strides=(stride,np.dtype(dtype).itemsize)).copy()
    def primitives(self,name):return self.doc['meshes'][self.nodes[name]['mesh']]['primitives']
    def signature(self,name):
        h=hashlib.sha256()
        node=self.nodes[name]
        for key in ['matrix','translation','rotation','scale']:h.update(json.dumps(node.get(key)).encode())
        for p in self.primitives(name):
            for key,index in sorted(p['attributes'].items()):h.update(key.encode());h.update(self.array(index).tobytes())
            h.update(self.array(p['indices']).tobytes())
        return h.hexdigest()

old=GLB(OUT/'backup/assets/island_blender/nameless_island.glb')
new=GLB(ROOT/'assets/island_blender/nameless_island.glb')
removed=set(old.nodes)-set(new.nodes)
expected={'Fish_Ground_Rock_%02d_Body'%i for i in [2,3,4,5]}|{'Depth_Bamboo_Main_%02d'%i for i in [3,4,5]}
expected|={n for n in old.nodes if any(n.startswith('Coast_Low_Grass_%02d.'%i) for i in range(4,11))}
assert removed==expected,removed^expected
unchanged=[]
for name,node in old.nodes.items():
    if name in removed or 'mesh' not in node:continue
    assert old.signature(name)==new.signature(name),f'Unexpected geometry change: {name}'
    unchanged.append(name)
wind={}
for name in ['InkSample_Bamboo_%02d'%i for i in [3,4,5]]+['InkSample_Path_Grass']:
    data=[]
    for p in new.primitives(name):
        weights=new.array(p['attributes']['TEXCOORD_1'])[:,0]
        assert np.all(np.isfinite(weights)) and weights.min()>=0 and weights.max()<=1.001
        data.append({'material':new.doc['materials'][p['material']]['name'],'weight_min':float(weights.min()),'weight_max':float(weights.max()),'fixed_vertices':int(np.count_nonzero(weights<.001))})
    assert sum(p['fixed_vertices'] for p in data)>0
    wind[name]=data
for name in [n for n in new.nodes if n.startswith('InkSample_Rock_')]:
    for p in new.primitives(name):
        assert np.isfinite(new.array(p['attributes']['TEXCOORD_0'])).all()
        assert np.isfinite(new.array(p['attributes']['NORMAL'])).all()
report={'expected_archived_nodes':sorted(expected),'new_sample_nodes':sorted(set(new.nodes)-set(old.nodes)),'unchanged_geometry_nodes':len(unchanged),'terrain_and_bridge_identical':all(n in unchanged for n in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land','Bridge_Plank_00']),'wind_weight_ranges':wind}
(OUT/'asset-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
