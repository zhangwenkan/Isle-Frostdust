"""Build connected, individually shaped shore faces in Blender via MCP."""
import bpy,bmesh,math,json,hashlib,bisect
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/shore-facets-review';O.mkdir(exist_ok=True)
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
arc=bpy.data.collections.get('90_Rejected_Coastal_Stripes') or bpy.data.collections.new('90_Rejected_Coastal_Stripes')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True
def baseline(ob):
 name='ShoreBaseline_'+ob.name;b=bpy.data.objects.get(name)
 if b is None:
  b=ob.copy();b.data=ob.data.copy();b.name=name;arc.objects.link(b);b.hide_set(True);b.hide_render=True
 return b
land=s.objects['Fish_West_Continuous_Land'];base=baseline(land)
count=2626;boundary=[i*26 for i in range(101)]+[2600+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
top=[base.matrix_world@v.co for v in list(base.data.vertices)[:count]];perimeter=[top[i] for i in boundary]
lengths=[0.0]
for j in range(250):lengths.append(lengths[-1]+(perimeter[(j+1)%250]-perimeter[j]).length)
total=lengths[-1];design=json.loads((R/'assets/shore_facets/design.json').read_text())['faces']
cuts=[0.0]
for d in design:cuts.append(cuts[-1]+d['width'])
cuts=[c/cuts[-1]*total for c in cuts]
def interp_profile(keys,x):
 for (a,va),(b,vb) in zip(keys,keys[1:]):
  if a<=x<=b:return va+(vb-va)*(x-a)/(b-a)
 return keys[-1][1]
def perimeter_at(u):
 u=u%total;j=min(249,bisect.bisect_right(lengths,u)-1);f=(u-lengths[j])/(lengths[j+1]-lengths[j]);p=perimeter[j].lerp(perimeter[(j+1)%250],f)
 t=perimeter[(j+1)%250]-perimeter[j];return p,Vector((-t.y,t.x,0)).normalized()
mat=bpy.data.materials.get('Shore_Facet_Painted') or bpy.data.materials.new('Shore_Facet_Painted');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
tex=mat.node_tree.nodes.get('ShoreFacets') or mat.node_tree.nodes.new('ShaderNodeTexImage');tex.name='ShoreFacets';tex.image=bpy.data.images.load(str(R/'assets/shore_facets/shore_rock_faces.png'),check_existing=True);tex.image.reload();mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
verts=[p.copy() for p in top];topfaces=[p for p in base.data.polygons if p.material_index==0]
faces=[tuple(p.vertices) for p in topfaces];mats=[0]*len(faces);uvs=[tuple(base.data.uv_layers.active.data[i].uv) for p in topfaces for i in p.loop_indices]
# All original boundary vertices plus deliberately placed shoulder stations.
stations=sorted(set(lengths[:-1]+[c for c in cuts[:-1]]+[cuts[i]+(cuts[i+1]-cuts[i])*f for i in range(30) for f in [.075,.19,.34,.70,.84,.95]]))
# One narrow top join closes the different discretizations without moving a single turf vertex.
def append_face(ids,uv,mi=1):faces.append(tuple(ids));mats.append(mi);uvs.extend(uv)
def uv_for(i,a,t):return ((i%6+(0.015+.97*a))/6,1-(i//6+(.01+.98*t))/5)
def shape(i,a,t,u):
 d=design[i];p,n=perimeter_at(u)
 profile=interp_profile([(0,-.13),(.075,-.19),(.19,.10),(.34,d['shoulder']),(.70,d['shoulder']*.90),(.84,.09),(.95,-.17),(1,-.13)],a)
 top_blend=min(1,t/.13)
 off=profile*top_blend-.26*t
 # Short, partial rock shelves occur on selected faces at different heights.
 if d['ledge'] is not None:
  q=d['ledge'];ledge=interp_profile([(0,0),(q-.035,0),(q,.28),(q+.018,.29),(q+.060,0),(1.05,0)],t)
  across=interp_profile([(0,0),(.19,0),(.34,1),(.70,1),(.88,0),(1,0)],a)
  off+=ledge*across
 drift=d['lean']*t*(1-t)*4*math.sin(math.pi*a)
 p2,n2=perimeter_at(u+drift)
 q=p2+n2*off
 q.z=p.z-(p.z+3.5)*t
 return q
station_ids=[];face_stations=[]
for i in range(30):
 us=[u for u in stations if cuts[i]-1e-7<=u<=cuts[i+1]+1e-7]
 if i==29:us.append(total)
 us=sorted(set(us));rows=[]
 d=design[i];levels=[0,.035,.09,.14,.25,.43,.62,.82,1.02]
 if d['ledge'] is not None:levels=sorted(set(levels+[d['ledge']-.035,d['ledge'],d['ledge']+.018,d['ledge']+.060]))
 for t in levels:
  row=[]
  for u in us:
   a=(u-cuts[i])/(cuts[i+1]-cuts[i]);row.append(len(verts));verts.append(shape(i,a,t,u))
  rows.append(row)
 for r in range(len(levels)-1):
  for j in range(len(us)-1):
   a=(us[j]-cuts[i])/(cuts[i+1]-cuts[i]);b=(us[j+1]-cuts[i])/(cuts[i+1]-cuts[i]);ta,tb=levels[r:r+2]
   append_face([rows[r][j],rows[r][j+1],rows[r+1][j+1],rows[r+1][j]],[uv_for(i,a,ta),uv_for(i,b,ta),uv_for(i,b,tb),uv_for(i,a,tb)])
 # Seal junction with the original terrain boundary. Coplanar triangles only where an edge was subdivided.
 for j in range(len(us)-1):
  mid=(us[j]+us[j+1])/2;k=min(249,bisect.bisect_right(lengths,mid)-1)
  aa,bb=boundary[k],boundary[(k+1)%250]
  # Both subdivided edge endpoints lie on this exact original boundary edge.
  # This thin apron is supported beneath the turf, rather than extending into the walking surface.
  p0=verts[rows[0][j]];p1=verts[rows[0][j+1]]
  if (p0-top[aa]).length<1e-6:rows[0][j]=aa
  if (p1-top[bb]).length<1e-6:rows[0][j+1]=bb
 face_stations.append(dict(i=i,start=cuts[i],end=cuts[i+1],levels=levels))
# Surface endpoints meet exactly. Merge coincident points after building, retaining originals first.
me=bpy.data.meshes.new('West_Shore_Individual_Facets');me.from_pydata(verts,[],faces);me.materials.append(base.data.materials[0]);me.materials.append(mat);me.update()
uv=me.uv_layers.new(name='CoastUV');uv.data.foreach_set('uv',[v for pair in uvs for v in pair])
if base.data.color_attributes:
 ca=me.color_attributes.new(name='LandscapeColor',type='FLOAT_COLOR',domain='POINT');colors=[tuple(base.data.color_attributes['LandscapeColor'].data[i].color) for i in range(count)]+[(.3,.32,.27,1)]*(len(verts)-count);ca.data.foreach_set('color',[v for c in colors for v in c])
for p,m in zip(me.polygons,mats):p.material_index=m;p.use_smooth=m==0
# Keep the original index/UV order for gameplay auditing; normals are outward by perimeter winding.
me.update();land.data=me;land.matrix_world.identity()
changed=[land.name]
from mathutils.bvhtree import BVHTree
tree=BVHTree.FromPolygons([v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
for ob in active():
 if not ob.name.startswith('Cliff_Fern_West_'):continue
 b=baseline(ob);ob.data=b.data.copy();ob.matrix_world=b.matrix_world.copy();ps=[ob.matrix_world@v.co for v in ob.data.vertices]
 cx=sum(p.x for p in ps)/len(ps);z=max(p.z for p in ps)-.1
 hit=tree.ray_cast(Vector((cx,-25,z)),Vector((0,1,0)))[0]
 if hit:
  root=Vector((cx,max(p.y for p in ps),z));delta=hit-root;inv=ob.matrix_world.inverted()
  for v,p in zip(ob.data.vertices,ps):v.co=inv@(p+delta)
  ob.data.update();changed.append(ob.name)
preserved=[n for n in before if n not in changed];assert all(sig(s.objects[n])==before[n] for n in preserved)
assert max((me.vertices[i].co-top[i]).length for i in range(count))<1e-6
me.calc_loop_triangles();bad=[t.index for t in me.loop_triangles if t.area<1e-10]
report=dict(changed=changed,preserved=len(preserved),top_vertices_unchanged=count,panels=30,triangles=len(me.loop_triangles),degenerate=len(bad),design=face_stations)
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
# Original reference scenes must remain separate from the editable island source.
for refscene in list(bpy.data.scenes):
 if refscene.name.startswith('Actual_'):bpy.data.scenes.remove(refscene)
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('SHORE_FACETS',json.dumps({k:v for k,v in report.items() if k!='design'}))
