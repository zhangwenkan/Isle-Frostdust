import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review';s=bpy.data.scenes['Tripo_Game_Assembly_20261119']
result={}
for name in ['GameJoin_WALK_Forest_Ground','GameJoin_Cape_Terminus_Bedrock']:
    ob=s.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    result[name]=[[list(ob.matrix_world@v.co) for v in e.verts] for e in bm.edges if e.is_boundary and all(-62<v.co.x<-52 and v.co.y<14.6 for v in e.verts)]
    bm.free()
with bpy.data.libraries.load(str(R/'assets/layered_island/layered_island.blend'),link=False) as (available,loaded):loaded.objects=['WALK_Cape_Sand']
sand=loaded.objects[0];vs=[sand.matrix_world@v.co for v in sand.data.vertices];tree=BVHTree.FromPolygons(vs,[list(p.vertices) for p in sand.data.polygons])
result['sand']={'name':sand.name,'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'samples':[]}
for y in [2,4,6,8,10,12]:
    row=[]
    for x in [-62,-61,-60,-59,-58,-57,-56,-55,-54]:
        hit=tree.ray_cast(Vector((x,y,10)),Vector((0,0,-1)),20);row.append(round(hit[0].z,3) if hit[0] else None)
    result['sand']['samples'].append({'y':y,'heights':row})
(O/'boundary-welded.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('Boundary and sand sampled; no game geometry changed.')
