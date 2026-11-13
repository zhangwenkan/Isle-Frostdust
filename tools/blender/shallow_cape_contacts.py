import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
land=s.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons if p.material_index==0])
fixed=0
for ob in s.objects:
 if not ob.type=='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
 if not ob.name.startswith(('Integrated_Coast_','Junction_')):continue
 if ob.name=='Integrated_Coast_Rock_02' and len(ob.data.polygons)<500:
  bm=bmesh.new();bm.from_mesh(ob.data)
  region=[f for f in bm.faces if f.calc_center_median().x< -19 and f.calc_area()>.04]
  edges={e for f in region for e in f.edges}
  if edges:bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=3,use_grid_fill=True)
  bm.to_mesh(ob.data);bm.free();ob.data.update()
 inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:
  q=ob.matrix_world@v.co
  if not q.x<-16:continue
  hit=tree.ray_cast(Vector((q.x,q.y,20)),Vector((0,0,-1)))[0]
  margin=.44 if ob.name=='Integrated_Coast_Rock_02' else .04
  if hit is not None and q.z>hit.z-margin:q.z=hit.z-margin;v.co=inv@q;fixed+=1
 ob.data.update()
print('LEGACY_RIM_VERTICES_BELOW_TERRAIN',fixed)
