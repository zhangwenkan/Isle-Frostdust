import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined']
report={'filepath':bpy.data.filepath,'dirty':bpy.data.is_dirty,'objects':[]}
for ob in scene.objects:
    if ob.name not in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land'] and not ob.name.startswith('Depth_Foreground_Crag'):continue
    corners=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    mats=[m.name if m else None for m in ob.data.materials]
    report['objects'].append({'name':ob.name,'verts':len(ob.data.vertices),'faces':len(ob.data.polygons),'bounds':[[min(v[k] for v in corners),max(v[k] for v in corners)] for k in range(3)],'materials':mats,'face_counts':{mats[i]:sum(p.material_index==i for p in ob.data.polygons) for i in range(len(mats))},'attributes':[(a.name,a.domain,a.data_type) for a in ob.data.attributes],'matrix':[list(row) for row in ob.matrix_world]})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'artifacts/cliff-form-review/backup/live-session.blend'),copy=True)
(ROOT/'artifacts/cliff-form-review/inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
