"""Seat full palm trunk base caps below the actual sloping ground, via Blender MCP."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
ground=[]
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
    ob=scene.objects[name];ground.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
def terrain(p):
    hits=[b.ray_cast(Vector((p.x,p.y,30)),Vector((0,0,-1))) for b in ground]
    return max((q.z for q,n,i,d in hits if q is not None),default=p.z)
report=[]
for ob in list(scene.objects):
    if not ob.name.startswith('Coast_Palm_') or not ob.name.endswith('_Body'):continue
    base=[p for p in ob.data.polygons if p.center.z<.35 and p.normal.z<-.35]
    ids=set(v for p in base for v in p.vertices)
    if not ids:ids={v.index for v in ob.data.vertices if v.co.z<min(q.co.z for q in ob.data.vertices)+.15}
    points=[ob.matrix_world@ob.data.vertices[i].co for i in ids]
    clearance=max(p.z-terrain(p) for p in points)
    drop=max(0,clearance+.035)
    prefix=ob.name.rsplit('_',1)[0]
    for part in scene.objects:
        if part.name.startswith(prefix+'_'):part.location.z-=drop
    ob['root_burial']=float(ob.get('root_burial',.035))+drop
    report.append({'name':ob.name,'cap_vertices':len(ids),'previous_highest_cap_clearance':clearance,'lowered_by':drop,'burial':ob['root_burial']})
bpy.context.view_layer.update()
(ROOT/'artifacts/palm-style-review/root-seating.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/island_blender/nameless_island.blend'))
print('PALM_ROOT_SEATING',json.dumps(report))
