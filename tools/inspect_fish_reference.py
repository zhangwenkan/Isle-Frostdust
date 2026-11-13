"""Read supplied Unity reference data; never modify the reference installation."""
from pathlib import Path
import UnityPy,json,numpy as np
from functools import lru_cache
ROOT=Path('D:/steam/steamapps/common/I Just Wanted to Fish Demo')
OUT=Path('artifacts/fish-style-review')
env=UnityPy.load(str(ROOT/'I Just Wanted to Fish_Data/sharedassets1.assets'))
materials={}
for obj in env.objects:
 if obj.type.name!='Material':continue
 m=obj.read()
 if not m.m_Name.startswith(('M_Tree_A','M_Tree_B','M_Rock','M_Terrain','M_Grass','M_Bush')):continue
 entry={'textures':{},'floats':{},'colors':{}}
 for key,val in m.m_SavedProperties.m_TexEnvs:
  if val.m_Texture.path_id:
   try:entry['textures'][key]=val.m_Texture.read().m_Name
   except:entry['textures'][key]=str(val.m_Texture.path_id)
 for key,val in m.m_SavedProperties.m_Floats:
  if any(s in key for s in ['Smooth','NormalScale','Alpha','Leaf','Wind']):entry['floats'][key]=val
 for key,val in m.m_SavedProperties.m_Colors:
  if key in ['_BaseColor','_Color']:entry['colors'][key]=[val.r,val.g,val.b,val.a]
 materials[m.m_Name]=entry
(OUT/'reference-materials.json').write_text(json.dumps(materials,indent=2),encoding='utf-8')
print('material bindings',len(materials),flush=True)
env=UnityPy.load(str(ROOT/'I Just Wanted to Fish_Data/level1'))
trans={};go={};render={}
for obj in env.objects:
 t=obj.type.name
 if t=='GameObject':go[obj.path_id]=obj.read().m_Name
 elif t=='Transform':trans[obj.path_id]=obj.read()
 elif t=='MeshRenderer':
  d=obj.read();render[d.m_GameObject.path_id]=d
def xyz(v):return [v.x,v.y,v.z]
@lru_cache(None)
def world(pid):
 t=trans[pid];q=t.m_LocalRotation;x,y,z,w=q.x,q.y,q.z,q.w
 rot=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
 m=np.eye(4);m[:3,:3]=rot@np.diag(xyz(t.m_LocalScale));m[:3,3]=xyz(t.m_LocalPosition)
 return world(t.m_Father.path_id)@m if t.m_Father.path_id in trans else m
records=[]
for pid,t in trans.items():
 name=go.get(t.m_GameObject.path_id,'')
 if not name.startswith(('Tree_A','Tree_B','Rock_','Boulder','Terrain','GrassTufts')):continue
 m=world(pid)
 rec={'name':name,'position':m[:3,3].tolist(),'scale':np.linalg.norm(m[:3,:3],axis=0).tolist(),'matrix':m.tolist()}
 r=render.get(t.m_GameObject.path_id)
 if r:
  rec['materials']=[]
  for ptr in r.m_Materials:
   try:rec['materials'].append(ptr.read().m_Name)
   except:rec['materials'].append(str(ptr.path_id))
 records.append(rec)
(OUT/'reference-placement.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('placement records',len(records),flush=True)
for kind in ['Tree_A','Tree_B','Rock_A','Boulder_A']:
 print(kind,[r for r in records if r['name']==kind][:2])
