"""Expose structural crown slabs while preserving the actual actor/fire support."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
land=s.objects['Fish_West_Continuous_Land'];rocks=list(bpy.data.collections['39_Shallow_Rock_Cape'].objects)
vv=[];ff=[]
for ob in rocks:
 offset=len(vv);vv.extend([ob.matrix_world@v.co for v in ob.data.vertices]);ff.extend([tuple(i+offset for i in p.vertices) for p in ob.data.polygons])
tree=BVHTree.FromPolygons(vv,ff)
def distance(p,a,b):
 d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-t*d).length
bm=bmesh.new();bm.from_mesh(land.data)
# Retain the continuous walking roof. Removing it opened unintended holes between slabs.
removed=[]
# Seat all free roof edges against the actual rock below, leaving no wafer overhang.
edges=[e for e in bm.edges if len(e.link_faces)==1 and e.link_faces[0].material_index==0]
border={v for e in edges for v in e.verts}
seated=0
for v in border:
 q=v.co
 if q.x>=-23.2 or (q.x>-25.0 and abs(q.y+.25)<1.0):continue
 if ((q.x+27.35)/1.25)**2+((q.y-2.15)/.96)**2<1:continue
 hit=tree.ray_cast(Vector((q.x,q.y,12)),Vector((0,0,-1)))[0]
 if hit is not None and abs(hit.z-q.z)<.8:v.co.z=hit.z+.004;seated+=1
bm.to_mesh(land.data);bm.free();land.data.update()
print('EXPOSED_CROWNS',len(removed),'faces; SEATED_RIM',seated)
exec(compile((R/'tools/blender/shallow_cape_contacts.py').read_text(encoding='utf8'),'shallow_cape_contacts.py','exec'))
