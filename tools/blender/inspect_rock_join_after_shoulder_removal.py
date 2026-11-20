"""Read existing slope edges and bedrock after shoulder removal via Blender MCP."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-game-integration-review/shoulder-removal'
s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];rows=[]
for name in ['GameJoin_WALK_Forest_Ground','GameJoin_Cape_Terminus_Bedrock']:
    ob=s.objects[name];me=ob.data;vs=[ob.matrix_world@v.co for v in me.vertices]
    tree=BVHTree.FromPolygons(vs,[list(p.vertices) for p in me.polygons])
    samples=[]
    for y in [4,6,8,10,12,14,15,16]:
        row=[]
        for x in [-62,-61,-60,-59.8,-59,-58,-57,-56]:
            hit=tree.ray_cast(Vector((x,y,12)),Vector((0,0,-1)),20)
            row.append(round(hit[0].z,3) if hit[0] else None)
        samples.append({'y':y,'heights':row})
    rows.append({'name':name,'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'x_columns':[-62,-61,-60,-59.8,-59,-58,-57,-56],'samples':samples})
(O/'join-inspection.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows))
