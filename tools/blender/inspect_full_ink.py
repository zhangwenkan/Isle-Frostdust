"""Read the live Blender source for the full-island material extension."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/full-island-ink-review';O.mkdir(exist_ok=True)
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
rows=[]
for o in bpy.data.scenes['Island_Refined'].objects:
    if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    rows.append({'name':o.name,'materials':[m.name for m in o.data.materials if m],
      'min':[min(v[k] for v in pts) for k in range(3)],'max':[max(v[k] for v in pts) for k in range(3)],
      'verts':len(o.data.vertices),'uv':[u.name for u in o.data.uv_layers],
      'colors':[c.name for c in o.data.color_attributes]})
(O/'inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('Inventory',len(rows),'meshes',bpy.data.filepath)
