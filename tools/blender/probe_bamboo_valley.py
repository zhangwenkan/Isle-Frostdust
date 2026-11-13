"""Read current authored coast through Blender MCP, without changing the scene."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/bamboo-valley-review';OUT.mkdir(exist_ok=True,parents=True)
scene=bpy.data.scenes.get('Island_Refined')
result={'filepath':bpy.data.filepath,'dirty':bpy.data.is_dirty,'scene':bpy.context.scene.name,'objects':[]}
if scene:
    for o in scene.objects:
        if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
        if not any(s in o.name for s in ['West','Bamboo','InkSample','Bridge','Grass','Rock']):continue
        pts=[o.matrix_world@Vector(p) for p in o.bound_box]
        pts=[(p.x,p.z,-p.y) for p in pts]
        result['objects'].append({'name':o.name,'min':[min(p[a] for p in pts) for a in range(3)],'max':[max(p[a] for p in pts) for a in range(3)],'materials':[m.name if m else '' for m in o.data.materials]})
(OUT/'scene-probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
