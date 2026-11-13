import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/cape-broad-notch-review';O.mkdir(parents=True,exist_ok=True)
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
o=bpy.data.objects['CapeHookBaseline_Fish_West_Continuous_Land']
rows=[]
for i in range(101):
 ps=[o.matrix_world@o.data.vertices[i*26+j].co for j in range(26)]
 if min(p.x for p in ps)>-17:continue
 rows.append({'i':i,'start':list(ps[0]),'mid':list(ps[13]),'end':list(ps[-1])})
report={'rows':rows,'verts':len(o.data.vertices),'polygons':len(o.data.polygons),'materials':[m.name for m in o.data.materials]}
(O/'inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
