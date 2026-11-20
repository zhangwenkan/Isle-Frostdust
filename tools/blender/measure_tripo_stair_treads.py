"""Read actual tread height landmarks via Blender MCP."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.scenes['Tripo_Coast_Processing_20261119'].objects['Tripo_Coast_Original_Surface']
bm=bmesh.new();bm.from_mesh(o.data);tree=BVHTree.FromBMesh(bm);bm.free()
rows=[]
for j in range(61):
    y=-.455+j*.0045;zs=[]
    for x in [-.052,-.026,0,.026,.052]:
        h,n,i,d=tree.ray_cast(Vector((x,y,.40)),Vector((0,0,-1)),.42)
        zs.append(round(h.z,5) if h is not None else None)
    rows.append({'y':round(y,5),'z':zs})
p=Path('D:/自己做着玩的/孤屿霜尘/artifacts/tripo-replica-review/stair-height-landmarks.json')
p.write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows))
