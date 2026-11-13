import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘')
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
def active(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
out=[]
for o in s.objects:
 if not active(o):continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if lo[0]>-18:continue
 out.append({'name':o.name,'min':lo,'max':hi,'v':len(o.data.vertices),'f':len(o.data.polygons),'mat':[m.name for m in o.data.materials],'collections':[c.name for c in o.users_collection]})
land=s.objects['Fish_West_Continuous_Land']
profile=[]
for i in range(101):
 row=[land.matrix_world@v.co for v in land.data.vertices[i*26:i*26+26]]
 if min(p.x for p in row)>-17:continue
 profile.append({'i':i,'front':list(row[-1]),'back':list(row[0]),'path':list(min(row,key=lambda p:abs(p.y+.25)))})
report={'file':bpy.data.filepath,'objects':out,'land_profile':profile}
(R/'artifacts/shallow-cape-review/baseline-inspect.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
