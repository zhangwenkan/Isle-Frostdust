import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined']
land=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
out={'objects':[],'terrain_sections':[]}
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if 'Rock' not in ob.name:continue
    pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    out['objects'].append({'name':ob.name,'collections':[c.name for c in ob.users_collection],'bounds':[[min(p[a] for p in pts),max(p[a] for p in pts)] for a in range(3)],'vertices':len(pts)})
for x in [-18,-17,-16,-13,-12,-11,-10,-9,-6,-5,-4,-3]:
    for y in [.8,1.2,1.6,2.0,2.4,2.8,3.2]:
        hit,n,_,_=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
        if hit is not None:out['terrain_sections'].append({'x':x,'y':y,'height':hit.z,'normal':list(n)})
(ROOT/'artifacts/stone-spatial-review/before-inspection.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out))
