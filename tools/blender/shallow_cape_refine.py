"""Low interlocking cape, authored ONLY in Blender through Blender MCP."""
import bpy,bmesh,json,math,hashlib
from mathutils.bvhtree import BVHTree
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/shallow-cape-review';A=R/'assets/shallow_cape'
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def active(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def sig(o):
 h=hashlib.sha256();h.update(str(o.matrix_world).encode())
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 return h.hexdigest()
arc=bpy.data.collections.get('90_Before_Shallow_Cape')
if not arc:
 arc=bpy.data.collections.new('90_Before_Shallow_Cape');s.collection.children.link(arc);arc.hide_render=True
col=bpy.data.collections.get('39_Shallow_Rock_Cape')
if not col:col=bpy.data.collections.new('39_Shallow_Rock_Cape');s.collection.children.link(col)
for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
for b in list(arc.objects):
 if not b.name.startswith('ShallowBaseline_'):continue
 name=b.name.removeprefix('ShallowBaseline_');ob=bpy.data.objects.get(name)
 if not ob:continue
 ob.data=b.data.copy();ob.matrix_world=b.matrix_world.copy()
 if arc in ob.users_collection:
  arc.objects.unlink(ob)
  target='37_Integrated_Coastal_Mass' if name.startswith('Integrated_') else '38_Coast_Junction_Sample'
  bpy.data.collections[target].objects.link(ob)
 ob.hide_set(False);ob.hide_render=False
before={o.name:sig(o) for o in s.objects if active(o)}
changed=[]
def baseline(o):
 name='ShallowBaseline_'+o.name
 b=bpy.data.objects.get(name)
 if not b:
  b=o.copy();b.data=o.data.copy();b.name=name;arc.objects.link(b);b.hide_set(True);b.hide_render=True
 o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();changed.append(o.name)
 return b
DROP=2.31
def weight(x,y):
 # The walking ramp eases up over seven metres. The rear blend ends before bamboo roots.
 return (1-smooth(-23,-16,x))*(1-smooth(.60,1.30,y))+(1-smooth(-23,-19.25,x))*smooth(.60,1.30,y)
def fall(p):return DROP*weight(p.x,p.y)*max(0,min(1,(p.z+3.6)/5.46))
land=s.objects['Fish_West_Continuous_Land'];lb=baseline(land)
old=[lb.matrix_world@v.co for v in lb.data.vertices];iv=land.matrix_world.inverted()
for v,p in zip(land.data.vertices,old):
 q=p.copy();q.z-=fall(p)
 # Turf pulls away from exposed crown slabs. The lane and fire clearing stay supported.
 edge=(1-smooth(-23,-21.7,p.x))
 if v.index<2626 and p.y< -1.25:
  q.y+=.73*edge*smooth(-1.25,-3.2,p.y)
 if v.index<2626 and p.x< -28.8:q.x+=.38*smooth(-28.8,-30.3,p.x)
 v.co=iv@q
uv2=land.data.uv_layers.get('CoastEdgeBlend')
if uv2:
 for l in land.data.loops:
  if (land.matrix_world@land.data.vertices[l.vertex_index].co).x< -21.6:uv2.data[l.index].uv=(0,0)
# Hide only the old cape's side faces behind the new structural slabs.
bm=bmesh.new();bm.from_mesh(land.data)
for x in [-22.1]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(x,0,0),plane_no=(1,0,0))
# Remove the exposed old side band, including its soil-colored rim. New rock closes it.
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==1 and f.calc_center_median().x< -22.1],context='FACES')
bm.to_mesh(land.data);bm.free();land.data.update()
landtree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons if p.material_index==0])
# The inherited wall remains outside the cape. It follows the connecting ramp only.
trimmed=[]
for ob in list(s.objects):
 if not active(ob) or not (ob.name.startswith('Integrated_Coast_') or ob.name.startswith('Junction_')):continue
 if min(((ob.matrix_world@v.co).x for v in ob.data.vertices),default=100)>=-16:continue
 baseline(ob);inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:
  q=ob.matrix_world@v.co;q.z-=fall(q);v.co=inv@q
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=inv@Vector((-22.1,0,0)),plane_no=(1,0,0),clear_inner=True)
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
 bm.to_mesh(ob.data);bm.free();ob.data.update();trimmed.append(ob.name)
 if not ob.data.polygons:
  for c in list(ob.users_collection):c.objects.unlink(ob)
  arc.objects.link(ob);ob.hide_set(True);ob.hide_render=True
# Move existing cold fire and small cape grass with their support, preserving their shapes/UVs.
for ob in list(s.objects):
 if not active(ob):continue
 if ob.name.startswith('Campfire_'):
  baseline(ob);inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   q=ob.matrix_world@v.co;q.z-=DROP;v.co=inv@q
 elif ob.name in ['Coast_Low_Grass_00.003','Coast_Low_Grass_01.003']:
  baseline(ob);inv=ob.matrix_world.inverted()
  for start in range(0,len(ob.data.vertices),8):
   vs=list(ob.data.vertices)[start:start+8];p=[ob.matrix_world@v.co for v in vs];root=(p[0]+p[1])*.5
   dz=DROP*weight(root.x,root.y)
   for v,q in zip(vs,p):q.z-=dz;v.co=inv@q
# Wide submerged apron in the EXISTING seabed, without a separate visible disc or new coastline.
bed=s.objects['Fish_Seabed'];baseline(bed);bi=bed.matrix_world.inverted()
shore=[Vector(p) for p in [(-30.2,1.8,0),(-29.8,-1.7,0),(-28.7,-3.25,0),(-26.6,-3.9,0),(-23,-3.7,0),(-21,-3.4,0),(-23,2.1,0),(-24.4,1.15,0),(-25.2,1.5,0),(-26,4.0,0),(-27.1,4.5,0),(-28.9,3.7,0)]]
def distance2d(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared));return (p-a-v*t).length
for v in bed.data.vertices:
 q=bed.matrix_world@v.co
 if not (-48<q.x<-17 and -23<q.y<23):continue
 p=Vector((q.x,q.y,0));d=min(distance2d(p,a,shore[(j+1)%len(shore)]) for j,a in enumerate(shore))
 w=1-smooth(-22,-17,q.x)
 target=-2.72-.18*d-.105*d*d+.035*math.sin(q.x*.81+q.y*.39)
 q.z=max(q.z,q.z*(1-w)+target*w);v.co=bi@q
bed.data.normals_split_custom_set([(0,0,0)]*len(bed.data.loops))
for f in bed.data.polygons:f.use_smooth=True
bed.data.update()
# Explicit silhouettes: broad upper seats, opposing slanted slabs, and three unequal tidal feet.
# Each outline is designed for its place in the cape, not copied from a random rock generator.
specs=[
 ('West_Crown',[(-30.9,-1.75),(-30.55,1.25),(-29.7,2.85),(-28.4,3.15),(-28.15,1.0),(-28.65,-1.45),(-29.65,-2.15)],-.55,2.08,(.12,-.05),(.22,.12)),
 ('Main_Oblique',[(-30.3,-2.0),(-29.55,-3.7),(-28.0,-4.15),(-26.3,-3.8),(-26.6,-1.5),(-28.4,-1.4)],-.65,2.12,(.085,.13),(.48,.25)),
 ('Counter_Slab',[(-27.75,-2.35),(-27.0,-4.35),(-24.7,-4.25),(-23.05,-3.5),(-23.4,-1.9),(-25.8,-1.8)],-.80,1.76,(-.13,.10),(-.32,.12)),
 ('Ramp_Shoulder',[(-23.8,-2.0),(-23.1,-3.65),(-21.45,-3.85),(-20.8,-2.8),(-21.1,-1.8),(-22.6,-1.5)],-.53,2.26,(.05,.14),(-.20,.18)),
 ('Rear_Crown',[(-30.0,1.4),(-29.4,3.75),(-27.15,4.75),(-25.9,4.05),(-26.05,2.2),(-28.0,1.15)],-.55,2.00,(.015,-.02),(.0,-.15)),
 ('Notch_Slab',[(-26.3,1.45),(-26.0,3.9),(-25.3,3.20),(-24.65,1.55),(-24.0,.68),(-25.1,.40)],-.77,1.98,(-.11,-.09),(-.20,-.25)),
 ('Low_West_Buttress',[(-31.5,-2.25),(-30.45,-3.65),(-28.65,-4.25),(-28.1,-3.6),(-29.05,-2.60),(-30.45,-1.60)],-1.35,1.28,(.11,.09),(.10,.22)),
 ('Front_Tilted_Foot',[(-28.0,-3.65),(-27.5,-4.9),(-26.25,-5.22),(-24.85,-4.55),(-25.25,-3.4),(-26.7,-3.16)],-1.31,1.42,(-.22,.10),(.32,.08)),
 ('East_Low_Foot',[(-24.6,-3.35),(-24.35,-4.5),(-22.5,-4.75),(-21.5,-4.0),(-22.1,-3.30),(-23.1,-3.1)],-1.70,1.08,(.14,-.12),(-.18,.14)),
 ('West_Waterline',[(-32,-.40),(-31.75,1.20),(-30.6,1.9),(-29.95,1.08),(-30.3,-.70),(-31.3,-1.10)],-1.65,1.30,(.05,-.13),(.12,0)),
 ('Nose_Wash',[(-32.2,-2.3),(-31.4,-3.1),(-30.55,-2.9),(-30.35,-1.5),(-31.25,-1.2)],-1.98,.85,(.15,.13),(.12,.03)),
 ('Rear_Water_Step',[(-29.0,3.20),(-28.6,4.75),(-26.55,5.25),(-25.25,4.5),(-25.9,3.5),(-27.5,3.1)],-1.44,1.42,(.02,-.09),(.2,-.25)),
 ('Central_Backbone',[(-29.2,-.8),(-28.55,-1.85),(-26.4,-2.10),(-24.75,-1.1),(-24.7,.7),(-26.0,1.8),(-28.6,1.55)],-.44,2.26,(-.045,.055),(.22,.12))]
mat=bpy.data.materials.get('ShallowCape_Stone') or bpy.data.materials.new('ShallowCape_Stone');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.28,.30,.27,1);bs.inputs['Roughness'].default_value=1
atlas=[];tile=0;objects=[]
for idx,(name,poly,zt,h,tilt,lean) in enumerate(specs):
 center=Vector((sum(p[0] for p in poly)/len(poly),sum(p[1] for p in poly)/len(poly)))
 top=[];middle=[];bottom=[]
 for j,(x,y) in enumerate(poly):
  rise=DROP*smooth(-23,-16,x)*(1-smooth(-21.2,-20.4,x)) if idx==3 else 0
  z=zt+(x-center.x)*tilt[0]+(y-center.y)*tilt[1]+rise
  # One uneven broad fold on the top, not regular bevel bands.
  z+=.045*max(0,(x-center.x)*(.8 if idx%2 else -.8)+(y-center.y)*.35)
  hit=landtree.ray_cast(Vector((x,y,20)),Vector((0,0,-1)))[0]
  if hit is not None:z=min(z,hit.z-.035)
  top.append((x,y,z))
  f=[.89,.96,.92,1.02,.90,.95,.88][(j+idx)%7]
  bottom.append((center.x+(x-center.x)*f+lean[0],center.y+(y-center.y)*f+lean[1],z-h))
  ratio=[.29,.42,.23,.58,.66,.34,.49][(j+idx)%7]
  bow=[.04,-.015,.06,-.025,.035,.08,-.03][(j+idx*2)%7]
  middle.append((x+(bottom[-1][0]-x)*ratio+(x-center.x)*bow,y+(bottom[-1][1]-y)*ratio+(y-center.y)*bow,z-h*ratio))
 n=len(poly);verts=top+middle+bottom
 faces=[tuple(range(n))]+[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(2) for j in range(n)]+[tuple(reversed(range(n*2,n*3)))]
 me=bpy.data.meshes.new('ShallowCape_'+name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 uv=me.uv_layers.new(name='FacePainting');uv2=me.uv_layers.new(name='ContactUV')
 for f in me.polygons:
  pts=[me.vertices[v].co for v in f.vertices];normal=f.normal;edge=(pts[1]-pts[0]).normalized();up=normal.cross(edge).normalized()
  pu=[(p.dot(edge),p.dot(up)) for p in pts];mi=[min(p[k] for p in pu) for k in range(2)];ma=[max(p[k] for p in pu) for k in range(2)]
  xy=[(.07+.86*(p[0]-mi[0])/max(1e-6,ma[0]-mi[0]),.07+.86*(p[1]-mi[1])/max(1e-6,ma[1]-mi[1])) for p in pu]
  cell=(tile%16,tile//16)
  for li,p in zip(f.loop_indices,xy):uv.data[li].uv=((cell[0]+p[0])/16,1-(cell[1]+p[1])/16)
  atlas.append({'tile':tile,'rock':idx,'face':f.index,'top':normal.z>.60,'bottom':normal.z<-.65,'polygon':xy,'size':[ma[k]-mi[k] for k in range(2)]})
  tile+=1;f.use_smooth=False
 ob=bpy.data.objects.new('ShallowCape_'+name,me);col.objects.link(ob);objects.append(ob)
 ob['authoring']='Hand-set cape slab footprint and slanted planes; created inside Blender MCP 2026-11-12'
 if (A/'slab_paint.png').exists():
  tx=mat.node_tree.nodes.get('SlabPaint') or mat.node_tree.nodes.new('ShaderNodeTexImage');tx.name='SlabPaint';tx.image=bpy.data.images.load(str(A/'slab_paint.png'),check_existing=True);tx.image.reload();mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
preserved=[o.name for o in s.objects if active(o) and o.name in before and o.name not in changed]
assert all(sig(s.objects[n])==before[n] for n in preserved)
report={'drop_m':DROP,'water_y':-2.1,'cape_ground_y':-.45,'above_water_m':1.65,'changed':changed,'preserved_meshes':len(preserved),'trimmed':trimmed,'rock_objects':[o.name for o in objects],'atlas':atlas,'walk_ramp_x':[-23,-16],'bamboo_meshes_unchanged':True}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/island_blender/nameless_island.blend'))
print('SHALLOW_CAPE_AUTHORED',len(objects),'slabs;',len(preserved),'other meshes preserved;',tile,'paint panels')
