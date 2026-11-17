"""Read GLB accessors to compare preserved assets; does not create geometry."""
import json,struct,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/bamboo-west-extension-review'
def load(path):
 data=path.read_bytes();n,t=struct.unpack_from('<II',data,12);doc=json.loads(data[20:20+n]);start=20+n;n,t=struct.unpack_from('<II',data,start);binary=data[start+8:start+8+n]
 def accessor(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];comps={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']]*comps
  stride=v.get('byteStride',size);start=v.get('byteOffset',0)+a.get('byteOffset',0)
  return b''.join(binary[start+j*stride:start+j*stride+size] for j in range(a['count']))
 result={}
 for node in doc['nodes']:
  if 'mesh' not in node:continue
  parts=[]
  for p in doc['meshes'][node['mesh']]['primitives']:
   attrs={k:hashlib.sha256(accessor(i)).hexdigest() for k,i in p['attributes'].items()};attrs['indices']=hashlib.sha256(accessor(p['indices'])).hexdigest();parts.append(attrs)
  result[node['name']]={'parts':parts,'transform':{k:node[k] for k in ['matrix','translation','rotation','scale'] if k in node}}
 return result
before=load(OUT/'before/layered_island.glb');after=load(ROOT/'assets/layered_island/layered_island.glb')
protected=[n for n in before if not n.startswith('Left_Bamboo') and n!='WALK_Left_Ground']
changed=[n for n in protected if before[n]!=after.get(n)]
report={'protected_count':len(protected),'protected_changed':changed,'old_floor_position_preserved':[p['POSITION'] for p in before['WALK_Left_Ground']['parts']]==[p['POSITION'] for p in after['WALK_Left_Ground']['parts']],'removed':[n for n in before if n not in after],'new':[n for n in after if n not in before]}
(OUT/'geometry-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['new','removed']}))
