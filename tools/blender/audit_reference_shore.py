"""Check source fit against the unchanged turf, UVs, and actual visible front normals."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Island_Refined'];land=s.objects['Fish_West_Continuous_Land'];base=s.objects['ReferenceShoreBaseline_Fish_West_Continuous_Land']
err=max((land.matrix_world@land.data.vertices[i].co-base.matrix_world@base.data.vertices[i].co).length for i in range(2626));assert err<1e-6
a=[p for p in land.data.polygons if p.material_index==0];b=[p for p in base.data.polygons if p.material_index==0];assert len(a)==len(b)
uv_error=0.
for p,q in zip(a,b):
 assert tuple(p.vertices)==tuple(q.vertices)
 for i,j in zip(p.loop_indices,q.loop_indices):uv_error=max(uv_error,(land.data.uv_layers.active.data[i].uv-base.data.uv_layers.active.data[j].uv).length)
assert uv_error<1e-7
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices[:2626]],[tuple(p.vertices) for p in a])
penetrations=[];samples=0;allverts=[];allfaces=[]
for ob in s.objects:
 if not ob.name.startswith('WS_Reference_Shore_'):continue
 me=ob.data;me.calc_loop_triangles();points=[ob.matrix_world@v.co for v in me.vertices]
 off=len(allverts);allverts.extend(points);allfaces.extend([tuple(off+j for j in p.vertices) for p in me.polygons])
 for p in points+[sum((points[j] for j in t.vertices),Vector())/3 for t in me.loop_triangles]:
  if p.z<1.4:continue
  h=tree.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
  if h:
   samples+=1
   if p.z>h.z-.005:penetrations.append([ob.name,list(p),h.z])
assert not penetrations,penetrations[:8]
rocktree=BVHTree.FromPolygons(allverts,allfaces);hits=0;inverted=[]
for i in range(60):
 x=-29+i*.55
 for z in [1.2,.4,-.5,-1.4]:
  p,n,idx,dist=rocktree.ray_cast(Vector((x,-25,z)),Vector((0,1,0)))
  if p:
   hits+=1
   if n.y>.03:inverted.append([x,z,list(n)])
assert not inverted,inverted[:10]
out=dict(top_vertices_unchanged=2626,max_vertex_error=err,top_faces_unchanged=len(a),max_uv_error=uv_error,rock_samples_under_turf=samples,turf_penetrations=len(penetrations),visible_front_normals=hits,inverted_front_normals=len(inverted))
(R/'artifacts/reference-shore-fit/audit.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('REFERENCE_SHORE_AUDIT',json.dumps(out))
