"""Read saved western terrain and projected coastline before cape authoring."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Layered_Island_20261116']
bpy.context.window.scene=scene
names=['WALK_Forest_Ground','WALK_Forest_NearSlope','Forest_Near_Closed_Skirt','Sea_Surface']
trees=[];report={'source':bpy.data.filepath,'objects':[],'samples':[]}
for name in names:
    ob=scene.objects[name]
    vertices=[ob.matrix_world@v.co for v in ob.data.vertices]
    report['objects'].append({'name':name,'bounds':[[min(v[k] for v in vertices),max(v[k] for v in vertices)] for k in range(3)],'matrix':list(map(list,ob.matrix_world))})
    if name.startswith('WALK_'):trees.append((name,BVHTree.FromPolygons(vertices,[list(p.vertices) for p in ob.data.polygons])))
for x in [-43.4,-48,-52,-56,-59,-61,-63,-66]:
    for y in [11.8,13.7,15.0]:
        hits=[(name,tree.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]) for name,tree in trees]
        hits=[(name,list(hit)) for name,hit in hits if hit is not None]
        report['samples'].append({'x':x,'y':y,'hits':hits})
(root/'artifacts/reference-cape-review/site-before.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
