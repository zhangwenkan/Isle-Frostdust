import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Island_Refined']
def tree(name):
    o=scene.objects[name];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
old=tree('RoadBaseline_Fish_West_Continuous_Land');new=tree('Fish_West_Continuous_Land');report=[]
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if not ('Bamboo' in ob.name or ob.name.startswith('Campfire_') or ob.name.startswith('InkSample_Rock_')):continue
    gaps=[]
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co
        if p.x>-12.5:continue
        a=old.ray_cast(Vector((p.x,p.y,25)),Vector((0,0,-1)))[0]
        b=new.ray_cast(Vector((p.x,p.y,25)),Vector((0,0,-1)))[0]
        if a and b and -.12<p.z-a.z<.12:gaps.append(b.z-a.z)
    if gaps:report.append({'object':ob.name,'contact_points':len(gaps),'max_ground_change_m':max(abs(v) for v in gaps)})
(ROOT/'artifacts/cape-road-alignment-review/neighbor-ground-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
