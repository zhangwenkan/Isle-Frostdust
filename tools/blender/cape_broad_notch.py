"""Blender MCP authoring: broad chamfered cape with a rear sea notch."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/cape-broad-notch-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def sig(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={o.name:sig(o) for o in active()}
arc=bpy.data.collections.get('90_Rejected_Narrow_Cape') or bpy.data.collections.new('90_Rejected_Narrow_Cape')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True
def archive(o):
 name='BroadCapeBaseline_'+o.name
 if bpy.data.objects.get(name) is None:
  b=o.copy();b.data=o.data.copy();b.name=name;arc.objects.link(b);b.hide_set(True);b.hide_render=True
land=s.objects['Fish_West_Continuous_Land'];archive(land)
base=bpy.data.objects['CapeHookBaseline_'+land.name]
land.data=base.data.copy();land.matrix_world=base.matrix_world.copy();me=land.data;inv=land.matrix_world.inverted()
old=[base.matrix_world@v.co for v in base.data.vertices]
assert len(old)==7126
xs=[-30.0,-29.5,-28.8,-28.0,-27.1,-26.1,-25.2,-24.3,-23.3,-21.6,old[260].x]
rears=[2.0,3.1,3.75,4.2,4.6,4.1,1.45,1.0,2.0,3.0,old[260].y]
fronts=[-1.4,-2.6,-3.1,-3.7,-3.95,-3.9,-3.75,-3.6,-3.55,-3.7,old[285].y]
def smooth(a,b,x):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def mapped_y(row,y):
 rear=old[row*26].y;front=old[row*26+25].y
 if row<=6:return fronts[row]+(y-front)/(rear-front)*(rears[row]-fronts[row])
 # Preserve the whole walking corridor, including shoe overshoot margins.
 if y>.7:return .7+(y-.7)/(rear-.7)*(rears[row]-.7)
 if y< -1.2:return -1.2+(y+1.2)/(front+1.2)*(fronts[row]+1.2)
 return y
for row in range(10):
 for j in range(26):
  idx=row*26+j;p=old[idx]
  y=rears[row]+(fronts[row]-rears[row])*j/25. if row<=6 else mapped_y(row,p.y)
  q=Vector((xs[row],y,p.z))
  # The fire clearing and lane stay level; just the outer grass lip falls away.
  edge=abs(j-12.5)/12.5
  q.z=1.86-.06*smooth(.80,1.,edge)*smooth(3,7,row)
  me.vertices[idx].co=inv@q
# Reorient the attached shell using its original offsets and the new shoreline.
boundary=[i*26 for i in range(101)]+[100*26+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
assert len(boundary)==250
newtop=[land.matrix_world@v.co for v in me.vertices[:2626]]
def outward(points,j):
 v=points[boundary[(j+1)%250]]-points[boundary[(j-1)%250]]
 return Vector((-v.y,v.x,0)).normalized()
for j,idx in enumerate(boundary):
 if idx>=260:continue
 oldn=outward(old,j);newn=outward(newtop,j)
 for ring in range(18):
  k=2626+ring*250+j;delta=old[k]-old[idx]
  inherited=newtop[idx]+newn*delta.dot(oldn);inherited.z=newtop[idx].z+delta.z
  fractions=[.018,.055,.105,.16,.23,.29,.34,.40,.46,.52,.59,.65,.71,.78,.85,.92,1.,1.14]
  offsets=[.025,.045,.05,.02,-.08,-.16,-.15,-.12,-.16,-.22,-.25,-.27,-.32,-.36,-.40,-.45,-.48,-.60]
  q=newtop[idx]+newn*offsets[ring];q.z=newtop[idx].z*(1-fractions[ring])-3.35*fractions[ring]
  q=q.lerp(inherited,smooth(-24.,-19.2,newtop[idx].x))
  me.vertices[k].co=inv@q
for p in me.polygons:
 if p.material_index==1 and any((land.matrix_world@me.vertices[i].co).x<-19.2 for i in p.vertices):p.use_smooth=False
# The inherited seabed cap is a 250-vertex ngon. Straight new cut faces leave
# collinear cap corners; triangulate the cap and drop only zero-area pieces.
bm=bmesh.new();bm.from_mesh(me)
bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
empty=[f for f in bm.faces if f.calc_area()<1e-10]
if empty:bmesh.ops.delete(bm,geom=empty,context='FACES_ONLY')
bm.to_mesh(me);bm.free()
me.normals_split_custom_set([(0,0,0)]*len(me.loops));me.update()
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def hit(x,y):return tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
changed=[land.name];fire_center=Vector((-27.35,2.15,1.86));old_fire=Vector((-26.5,.06,1.86));firepts=[]
for o in active():
 if not o.name.startswith('Campfire_'):continue
 archive(o);b=bpy.data.objects['CapeHookBaseline_'+o.name];o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();oi=o.matrix_world.inverted()
 for v in o.data.vertices:
  q=fire_center+(o.matrix_world@v.co-old_fire)*1.7
  v.co=oi@q;firepts.append(q)
 o.data.update();changed.append(o.name)
for p in firepts:
 h=hit(p.x,p.y);assert h is not None and abs(h.z-1.86)<.025,('fire support',list(p),list(h) if h else None)
# Restore the little grass group to the unbent source and fit its roots to turf.
grass=s.objects['Coast_Low_Grass_00.003'];archive(grass);b=bpy.data.objects['CapeHookBaseline_'+grass.name]
grass.data=b.data.copy();grass.matrix_world=b.matrix_world.copy();gi=grass.matrix_world.inverted()
grass_contacts=[]
for start in range(0,len(grass.data.vertices),8):
 vs=list(grass.data.vertices)[start:start+8];pts=[grass.matrix_world@v.co for v in vs];root=(pts[0]+pts[1])*.5
 row=next((i for i in range(10) if old[(i+1)*26+13].x>=root.x),9)
 f=max(0,min(1,(root.x-old[row*26+13].x)/(old[(row+1)*26+13].x-old[row*26+13].x)))
 x=xs[row]*(1-f)+xs[row+1]*f;y=mapped_y(row,root.y)*(1-f)+mapped_y(row+1,root.y)*f
 h=hit(x,y);assert h is not None
 delta=Vector((x-root.x,y-root.y,h.z-.025-root.z))
 for v,p in zip(vs,pts):v.co=gi@(p+delta)
 grass_contacts.append(delta.z)
grass.data.update();changed.append(grass.name)
route=[]
for i in range(541):
 x=-24.2+i*.05
 for z in [-.65,-.30,.25,.80,1.15]:
  p=hit(x,-z);assert p is not None,(x,z)
  route.append(abs(p.z-1.86))
assert max(route)<.025
preserved=[o.name for o in active() if o.name not in changed]
assert all(sig(s.objects[n])==before[n] for n in preserved)
me.calc_loop_triangles();degenerate=sum(t.area<1e-9 for t in me.loop_triangles)
upward=sum(t.normal.z<=0 for t in me.loop_triangles if all(i<2626 for i in t.vertices) and max((land.matrix_world@me.vertices[i].co).x for i in t.vertices)<-19.2)
assert not degenerate and not upward,(degenerate,upward)
for x,y in [(-24.3,1.8),(-24.8,2.7),(-25.2,3.3)]:
 h=hit(x,y);assert h is None or h.z<0,('notch must open to sea',x,y,h)
report={'changed':changed,'preserved_meshes':len(preserved),'profile_blender':[{'x':x,'rear_y':a,'front_y':b} for x,a,b in zip(xs,rears,fronts)],'min_connection_width_m':rears[7]-fronts[7],'notch_depth_m':max(rears)-rears[7],'fire_center_godot':[fire_center.x,fire_center.z,-fire_center.y],'fire_scale':1.7,'fire_nearest_depth_to_walk_edge_m':min(p.y for p in firepts)-.30,'route_samples':len(route),'max_route_error_m':max(route),'degenerate_triangles':degenerate,'non_upward_new_top_triangles':upward,'grass_groups':len(grass_contacts),'notch_water_open':True}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('BROAD_NOTCHED_CAPE',json.dumps(report))
