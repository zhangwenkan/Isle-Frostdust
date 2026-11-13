"""Bend the outer cape behind the horizontal walk, using the live Blender MCP scene."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/cape-hook-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def sig(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={o.name:sig(o) for o in active()}
archive=bpy.data.collections.get('90_Before_Cape_Hook') or bpy.data.collections.new('90_Before_Cape_Hook')
if archive.name not in s.collection.children:s.collection.children.link(archive)
archive.hide_render=True
def base(o):
 b=bpy.data.objects.get('CapeHookBaseline_'+o.name)
 if b is None:
  b=o.copy();b.data=o.data.copy();b.name='CapeHookBaseline_'+o.name;archive.objects.link(b);b.hide_set(True);b.hide_render=True
 return b
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def bend(x):return 4.2*(1-smooth(-28.0,-24.5,x))
def deform(p):
 shoulder=.9*math.exp(-((p.x+26.9)/1.1)**2)*smooth(-.2,2.,p.y)
 cove=.7*math.exp(-((p.x+24.3)/.9)**2)*smooth(.5,2.5,p.y)
 width=1+.65*(1-smooth(-26.,-24.5,p.x))
 outward=1.2*(1-smooth(-28.0,-24.5,p.x))
 return Vector((p.x-outward,p.y*width+bend(p.x)+shoulder-cove,p.z))
changed=[]
for o in list(active()):
 land=o.name=='Fish_West_Continuous_Land'
 cliff=o.name=='Cliff_Fractures_West' or o.name.startswith('Cliff_Fern_West_')
 grass=o.name.startswith('Coast_Low_Grass_') or o.name=='InkSample_Path_Grass'
 if not(land or cliff or grass):continue
 if min((o.matrix_world@v.co).x for v in o.data.vertices)>-22.0:continue
 b=base(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();inv=o.matrix_world.inverted()
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 if grass:
  stride=4 if o.name=='InkSample_Path_Grass' else 8
  for start in range(0,len(pts),stride):
   root=pts[start] if stride==4 else (pts[start]+pts[start+1])*.5
   delta=deform(root)-root
   for j in range(start,min(start+stride,len(pts))):o.data.vertices[j].co=inv@(pts[j]+delta)
 elif o.name.startswith('Cliff_Fern_'):
  center=sum(pts,Vector())/len(pts);delta=deform(center)-center
  for v,p in zip(o.data.vertices,pts):v.co=inv@(p+delta)
 else:
  for v,p in zip(o.data.vertices,pts):v.co=inv@deform(p)
 if land or cliff:o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops))
 o.data.update();changed.append(o.name)
land=s.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
def hit(x,y):return tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
fire_center=Vector((-27.5,3.65,1.86));fire_scale=1.7
old_center=Vector((-26.5,.06,1.86));fire_points=[]
for o in list(active()):
 if not o.name.startswith('Campfire_'):continue
 b=base(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=fire_center+(o.matrix_world@v.co-old_center)*fire_scale
  v.co=inv@p;fire_points.append(p)
 o.data.update();changed.append(o.name)
support=[]
for p in fire_points:
 q=hit(p.x,p.y);assert q is not None and q.z>1.8,('Fire beyond turf',list(p),list(q) if q else None)
 support.append(p.z-q.z)
route=[]
for i in range(541):
 x=-24.2+i*.05
 for z in [-.65,-.30,.25,.80,1.15]:
  p=hit(x,-z);assert p is not None,(x,z)
  route.append(abs(p.z-1.86))
assert max(route)<.025
preserved=[o.name for o in active() if o.name in before and o.name not in changed]
assert all(sig(s.objects[n])==before[n] for n in preserved)
land.data.calc_loop_triangles()
degenerate=sum(t.area<1e-9 for t in land.data.loop_triangles)
baseline_land=base(land);baseline_land.data.calc_loop_triangles()
inverted=sum(t.normal.z<=0 for t in land.data.loop_triangles if land.data.polygons[t.polygon_index].material_index==0)
baseline_inverted=sum(t.normal.z<=0 for t in baseline_land.data.loop_triangles if baseline_land.data.polygons[t.polygon_index].material_index==0)
assert inverted==baseline_inverted and not degenerate,(inverted,baseline_inverted,degenerate)
report={'changed':changed,'preserved_meshes':len(preserved),'rearward_bend_m':4.2,'outer_width_added_m':1.2,'fire_center_godot':[fire_center.x,fire_center.z,-fire_center.y],'fire_scale':fire_scale,'fire_width_m':max(p.x for p in fire_points)-min(p.x for p in fire_points),'fire_min_support_m':min(support),'fire_nearest_depth_to_walk_edge_m':min(p.y for p in fire_points)-.30,'route_samples':len(route),'max_route_error_m':max(route),'non_upward_turf_triangles_before':baseline_inverted,'non_upward_turf_triangles_after':inverted,'degenerate_triangles':degenerate}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('CAPE_HOOK_AUTHORED',json.dumps(report))
