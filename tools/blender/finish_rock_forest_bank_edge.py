"""Blender MCP: soften local end contact and eliminate empty ground face slots."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review';s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];bpy.context.window.scene=s
assert not s.get('bank_edge_finished')
g=s.objects['GameJoin_WALK_Forest_Ground'];missing=[]
for p in g.data.polygons:
    if g.data.materials[p.material_index] is None:missing.append(p.index);p.material_index=0
# Smooth only the bank's eastern join toward the retained terrain, so its top
# does not end as a visible straight slab. Positions outside the local addon stay.
original=bpy.data.scenes['Tripo_Game_Assembly_20261119'].objects['GameJoin_WALK_Forest_Ground']
tree=BVHTree.FromPolygons([v.co for v in original.data.vertices],[list(p.vertices) for p in original.data.polygons])
ob=s.objects['Forest_Bank_Continuous_Core'];nchanged=0
for v in ob.data.vertices:
    x,y,z=v.co
    if x>-54.35:
        hit=tree.ray_cast(Vector((x,y,12)),Vector((0,0,-1)),20)
        if hit[0]:
            f=max(0,min(1,(x+54.35)/.9));v.co.z=z*(1-f)+(hit[0].z-.018)*f;nchanged+=1
ob.data.update();s['bank_edge_finished']=True
(O/'bank-edge-finish.json').write_text(json.dumps({'unassigned_ground_faces_fixed':len(missing),'east_contact_vertices':nchanged},indent=2),encoding='utf8');print('Ground face materials repaired:',len(missing),'bank edge points:',nchanged)
