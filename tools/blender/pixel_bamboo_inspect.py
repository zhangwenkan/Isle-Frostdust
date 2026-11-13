import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘')
O=R/'artifacts/pixel-bamboo-west-review'
target=R/'assets/island_blender/nameless_island.blend'
if Path(bpy.data.filepath)!=target:
    if bpy.data.is_dirty:
        bpy.ops.wm.save_as_mainfile(filepath=str(O/'backup/previous-open-session.blend'),copy=True)
    bpy.ops.wm.open_mainfile(filepath=str(target))
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def sig(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
    for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
    for uv in o.data.uv_layers:
        for d in uv.data:h.update(str(tuple(d.uv)).encode())
    h.update(str(o.matrix_world).encode());return h.hexdigest()
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
report=[]
for o in active:
    ps=[o.matrix_world@Vector(p) for p in o.bound_box]
    report.append(dict(name=o.name,collections=[c.name for c in o.users_collection],min=[min(p[i] for p in ps) for i in range(3)],max=[max(p[i] for p in ps) for i in range(3)],verts=len(o.data.vertices),materials=[m.name for m in o.data.materials if m],signature=sig(o)))
(O/'baseline-objects.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
land=scene.objects['Fish_West_Continuous_Land']
t=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
samples=[]
for x in [-22,-18,-15,-12,-9,-6,-3,0,2,4]:
    row=[]
    for z in [2,0,-1,-2,-3,-4,-5,-6,-8,-10]:
        p=t.ray_cast(Vector((x,-z,50)),Vector((0,0,-1)))[0]
        row.append([z,round(p.z,3) if p else None])
    samples.append([x,row])
(O/'baseline-ground.json').write_text(json.dumps(samples,indent=2),encoding='utf-8')
print('MAIN_SCENE',bpy.data.filepath,len(active))
print('BAMBOO',[(o['name'],o['min'],o['max']) for o in report if 'Bamboo' in o['name'] and not o['name'].startswith('ForestVisibility')])
print('GROUND',samples)
