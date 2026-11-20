import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path('D:/自己做着玩的/孤屿霜尘');result={'scenes':[s.name for s in bpy.data.scenes]}
s=bpy.data.scenes.get('Layered_Island_20261116');result['main']=[]
if s:
 for o in s.objects:
  if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
  if any(k in o.name for k in ['Front','Cliff','Bedrock','Cape','Forest_Ground','Left_Finish']):
   vs=[o.matrix_world@Vector(v) for v in o.bound_box]
   result['main'].append({'name':o.name,'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'verts':len(o.data.vertices),'mats':[m.name for m in o.data.materials if m],'collections':[c.name for c in o.users_collection]})
(r/'artifacts/coast-structure-recovery/scene-inventory.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result))
