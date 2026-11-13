import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined']
bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve(),bpy.data.filepath
report=[]
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if ob.name.startswith(('Fish_Ground_Rock_','Depth_Bamboo_Main_','Coast_Low_Grass_')) or ob.name=='Fish_West_Continuous_Land':
        points=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        report.append({'name':ob.name,'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)],'verts':len(ob.data.vertices),'uv':[l.name for l in ob.data.uv_layers],'material':[m.name for m in ob.data.materials],'root_positions':ob.get('root_positions_godot','')})
out=ROOT/'artifacts/colored-ink-sample-review'
out.mkdir(parents=True,exist_ok=True)
(out/'source-objects.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'backup/session-before.blend'),copy=True)
print(json.dumps(report,ensure_ascii=False))
