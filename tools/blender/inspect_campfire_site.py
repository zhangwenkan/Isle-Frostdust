import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];land=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
sites=[]
for x,z in [(-22.6,-.4),(-22.5,0),(-22.5,.3),(-22.3,-.2),(-22.0,-.45),(-22.8,.2)]:
    p,n,_,_=tree.ray_cast(Vector((x,-z,20)),Vector((0,0,-1)))
    sites.append({'godot':[x,p.z,z],'normal_blender':list(n)})
(ROOT/'artifacts/cape-campfire-review/site-probes.json').write_text(json.dumps(sites,indent=2),encoding='utf-8')
print(json.dumps(sites))
