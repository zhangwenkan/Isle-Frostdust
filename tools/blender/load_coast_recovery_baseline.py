import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path('D:/自己做着玩的/孤屿霜尘')
with bpy.data.libraries.load(str(r/'assets/layered_island/layered_island.blend'),link=False) as (a,b):b.scenes=['Layered_Island_20261116']
s=b.scenes[0];s.name='Coast_Recovery_Original_Readonly_20261120'
res={'scene':s.name,'objects':[]}
for o in s.objects:
 if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
 if any(k in o.name for k in ['Left_Ground','Left_Stairs_00','Left_Rock','Cape','Forest_Ground']):
  ps=[o.matrix_world@Vector(v) for v in o.bound_box];res['objects'].append({'name':o.name,'bounds':[[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]],'verts':len(o.data.vertices),'mats':[m.name for m in o.data.materials if m]})
(r/'artifacts/coast-structure-recovery/original-inventory.json').write_text(json.dumps(res,indent=2),encoding='utf8')
print(json.dumps(res))
