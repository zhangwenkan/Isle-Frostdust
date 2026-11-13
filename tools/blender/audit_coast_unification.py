import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-unification-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
land=s.objects['Fish_West_Continuous_Land'];base=bpy.data.objects['UnifiedBaseline_'+land.name]
top_error=max((land.matrix_world@land.data.vertices[i].co-base.matrix_world@base.data.vertices[i].co).length for i in range(2626))
t=tree(land);samples=[]
for i in range(541):
 x=-24.2+i*.05
 for z in [-.65,-.3,.25,.80,1.15]:
  hit=t.ray_cast(Vector((x,-z,30)),Vector((0,0,-1)))[0]
  assert hit is not None,(x,z);samples.append(abs(hit.z-1.86))
assert max(samples)<.025
floor=s.objects['PixelForest_Low_Floor'];ft=tree(floor);roots=[];outside=[]
for ob in s.objects:
 if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
 if ob.name.startswith('PixelBamboo_'):
  r=ob['root_godot'];p=ft.ray_cast(Vector((r[0],-r[2],40)),Vector((0,0,-1)))[0];assert p is not None,ob.name
  roots.append(abs(p.z-r[1]-.035))
 ps=[ob.matrix_world@v.co for v in ob.data.vertices]
 if not ps:continue
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 if lo[0]<-5 and hi[0]>-10 and lo[1]<-4 and hi[2]<2.2 and 'Land' not in ob.name:outside.append({'name':ob.name,'bounds':[lo,hi]})
uv_error=0
for p in land.data.polygons:
 if p.material_index:continue
 # Top loop UV lookup, tolerant of any face winding changes after normal recalculation.
 old=base.data.polygons[p.index]
 olduv={base.data.loops[i].vertex_index:base.data.uv_layers.active.data[i].uv.copy() for i in old.loop_indices}
 for i in p.loop_indices:uv_error=max(uv_error,(land.data.uv_layers.active.data[i].uv-olduv[land.data.loops[i].vertex_index]).length)
report={'top_vertex_error':top_error,'top_uv_error':uv_error,'route_samples':len(samples),'max_route_error':max(samples),'bamboo_roots':len(roots),'max_root_offset_error':max(roots),'near_water_objects':outside}
report['rock_centers']={name:list(sum([s.objects[name].matrix_world@v.co for v in s.objects[name].data.vertices],Vector())/len(s.objects[name].data.vertices)) for name in ['InkSample_Rock_02','InkSample_Rock_03','InkSample_Rock_04']}
(O/'mesh-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
AUDIT_OUTPUT=O;AUDIT_PHASE='unified'
exec(compile((R/'tools/blender/audit_forest_rock_roots.py').read_text(encoding='utf8'),'audit_forest_rock_roots.py','exec'))
assert all(not r['intersecting_stems'] for r in report)
