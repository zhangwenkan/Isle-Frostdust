import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-visibility-review';O.mkdir(exist_ok=True,parents=True)
scene=bpy.data.scenes['Island_Refined']
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
report={'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'objects':[],'land_samples':[]}
for o in active:
    if not any(s in o.name for s in ['Bamboo','ValleyDepth','West_Continuous','InkSample_Rock','Grass','Fern']):continue
    pts=[o.matrix_world@Vector(p) for p in o.bound_box];pts=[(p.x,p.z,-p.y) for p in pts]
    report['objects'].append({'name':o.name,'min':[round(min(p[a] for p in pts),2) for a in range(3)],'max':[round(max(p[a] for p in pts),2) for a in range(3)],'mats':[m.name for m in o.data.materials if m],'roots':json.loads(o.get('root_positions_godot','[]')),'uv':[u.name for u in o.data.uv_layers]})
o=scene.objects['Fish_West_Continuous_Land'];tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
for x in [-18,-15,-12,-9,-6,-3,0,3]:
    row={'x':x,'heights':{}}
    for z in [1,0,-1,-2,-3,-4,-5,-6,-7,-8,-10]:
        p=tree.ray_cast(Vector((x,-z,40)),Vector((0,0,-1)))[0]
        row['heights'][z]=round(p.z,3) if p else None
    report['land_samples'].append(row)
(O/'scene-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PROBE',report['file'],report['dirty'],len(report['objects']))
