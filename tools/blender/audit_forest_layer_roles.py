"""Read current author geometry through Blender MCP, without mutations."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Layered_Island_20261116']
rows=[]
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if not any(c.name in ['43_West_Forest','44_Valley_Forest_Backdrop'] for c in ob.users_collection):continue
    points=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    rows.append({'name':ob.name,'collections':[c.name for c in ob.users_collection],
                 'min':[min(p[k] for p in points) for k in range(3)],'max':[max(p[k] for p in points) for k in range(3)],
                 'materials':[m.name for m in ob.data.materials]})
(root/'artifacts/forest-layer-role-review/current-author-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({'live_target_objects':len(rows),'scene':scene.name}))
