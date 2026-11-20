import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.data.scenes['Pixel_Cavern_Coast'];bpy.context.window.scene=s
rows=[]
for o in s.objects:
    if not o.get('pixel_cavern') or not o.name.startswith(('LiveBamboo','LiveCanopy','LiveGrass','Bamboo_Stem','Bamboo_Branch','Grass_','Shadow_')):continue
    ps=[o.matrix_world@Vector(q) for q in o.bound_box]
    lo=[min(q[i] for q in ps) for i in range(3)];hi=[max(q[i] for q in ps) for i in range(3)]
    rows.append({'name':o.name,'lo':lo,'hi':hi,'verts':len(o.data.vertices),'materials':[m.name for m in o.data.materials]})
p=Path('D:/自己做着玩的/孤屿霜尘/artifacts/pixel-vegetation-harmony-review/scene-inspection.json')
p.write_text(json.dumps({'revision':s.get('revision'),'objects':rows},indent=2),encoding='utf-8')
print(json.dumps({'revision':s.get('revision'),'inspected':len(rows),'sample':rows[:5]}))
