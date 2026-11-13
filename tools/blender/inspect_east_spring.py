import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘')
s=bpy.context.scene
out={'file':bpy.data.filepath,'scene':s.name,'objects':[]}
for o in s.objects:
 if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if hi[0]>20 and lo[0]<42 and lo[1]<12 and hi[1]>-12:
  out['objects'].append({'name':o.name,'min':lo,'max':hi,'materials':[m.name for m in o.data.materials if m],'collections':[c.name for c in o.users_collection]})
o=s.objects['Fish_East_Continuous_Land']
out['east_land_vertices']=[list(o.matrix_world@v.co) for v in o.data.vertices if (o.matrix_world@v.co).x>22]
(R/'artifacts/east-spring-review/east-before.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='east_land_vertices'}))
