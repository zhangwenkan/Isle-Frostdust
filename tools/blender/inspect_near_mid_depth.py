"""Read current Blender author geometry for the near/middle forest pass."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/near-mid-depth-review'
scene=bpy.data.scenes['Layered_Island_20261116']
live=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
rows=[]
for ob in live:
    if not (ob.name.startswith(('Forest_','WALK_Forest_')) and not any(n in ob.name for n in ['Bamboo_Role_Main','Bamboo_Role_Leaves','Paint_','Mist_','Sunray_'])):continue
    pts=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    rows.append({'name':ob.name,'min':[min(p[k] for p in pts) for k in range(3)],'max':[max(p[k] for p in pts) for k in range(3)],'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'materials':[m.name for m in ob.data.materials],'collections':[c.name for c in ob.users_collection]})
profiles=[]
for name in ['WALK_Forest_Ground','WALK_Forest_NearSlope']:
    ob=scene.objects[name];tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
    for x in [-43,-37,-32,-27,-21,-17]:
        vals=[]
        for y in [2,4,6,8,9,10,11,11.5,12,12.5,13,13.5,14,15,16,18]:
            hit=tree.ray_cast(Vector((x,y,35)),Vector((0,0,-1)))[0]
            vals.append([y,round(hit.z,4) if hit else None])
        profiles.append({'object':name,'x':x,'heights':vals})
report={'scene':scene.name,'file':bpy.data.filepath,'live_count':len(live),'objects':rows,'profiles':profiles}
(OUT/'author-before.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'scene':scene.name,'live_count':len(live),'target_objects':len(rows),'objects':[r['name'] for r in rows]}))
