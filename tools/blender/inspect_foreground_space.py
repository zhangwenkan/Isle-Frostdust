"""Inspect the actual Blender scene before the foreground composition pass."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/foreground-space-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
report={'filepath':bpy.data.filepath,'dirty':bpy.data.is_dirty,'objects':[]}
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    points=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    report['objects'].append({'name':ob.name,'vertices':len(ob.data.vertices),'collections':[c.name for c in ob.users_collection],'bounds':[[round(min(p[k] for p in points),3),round(max(p[k] for p in points),3)] for k in range(3)],'materials':[m.name if m else None for m in ob.data.materials],'uv':[u.name for u in ob.data.uv_layers]})
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'backup/live-session.blend'),copy=True)
(OUT/'inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'filepath':report['filepath'],'dirty':report['dirty'],'objects':len(report['objects'])}))
