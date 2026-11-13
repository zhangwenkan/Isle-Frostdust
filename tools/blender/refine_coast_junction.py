"""An authored front-coast sample. Run ONLY inside Blender via Blender MCP."""
import bpy,bmesh,json,math,hashlib,bisect
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-junction-refine-review';A=R/'assets/coast_junction'
A.mkdir(exist_ok=True)
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
X0=-23.;X1=-5.
# x, outward crown, turf retreat, shoulder elevation, shoulder projection, foot projection
# Two clefts separate three unequal broad faces; a low shoulder grows out of their base.
knots=[(-23,.05,0,.1,.15,.05),(-22.2,.18,.15,.15,.28,.13),
 (-21.1,.43,.72,.35,.55,.24),(-19.2,.39,1.04,.18,.48,.22),
 (-18.25,.05,.48,-.12,.12,-.06),(-17.85,-.24,.20,-.40,-.22,-.18),
 (-17.42,-.08,.44,.20,.28,.04),(-16.7,.36,.96,.67,1.12,.48),
 (-15.1,.50,1.12,.76,1.26,.63),(-13.65,.28,.65,.47,.92,.51),
 (-12.8,-.05,.22,-.12,.10,-.08),(-12.4,-.24,.12,-.46,-.12,-.13),
 (-11.95,.04,.52,-.26,.50,.22),(-10.7,.58,1.17,-.30,.98,.63),
 (-8.9,.62,.87,-.57,.91,.47),(-7.1,.31,.37,-.34,.57,.20),
 (-5.7,.12,.12,.05,.27,.07),(-5,.02,0,.1,.13,.04)]
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def envelope(x):return smooth(X0,X0+.8,x)*(1-smooth(X1-.8,X1,x))
def design(x):
 j=max(0,min(len(knots)-2,bisect.bisect_right([k[0] for k in knots],x)-1));a,b=knots[j:j+2];t=(x-a[0])/(b[0]-a[0]);return [a[k]*(1-t)+b[k]*t for k in range(1,6)]
def sig(o):
 h=hashlib.sha256();h.update(str(o.matrix_world).encode())
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 return h.hexdigest()
def active(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
arc=bpy.data.collections.get('90_Before_Junction_Sample')
if not arc:
 arc=bpy.data.collections.new('90_Before_Junction_Sample');s.collection.children.link(arc);arc.hide_render=True
 for o in list(s.objects):
  if active(o) and (o.name.startswith('Integrated_Coast_') or o.name=='Fish_West_Continuous_Land'):
   b=o.copy();b.data=o.data.copy();b.name='JunctionBaseline_'+o.name;arc.objects.link(b);b.hide_render=True;b.hide_set(True)
col=bpy.data.collections.get('38_Coast_Junction_Sample')
if not col:col=bpy.data.collections.new('38_Coast_Junction_Sample');s.collection.children.link(col)
for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
land=s.objects['Fish_West_Continuous_Land'];base=bpy.data.objects['JunctionBaseline_'+land.name]
land.data=base.data.copy()
others={o.name:sig(o) for o in s.objects if active(o) and o.name!=land.name and not o.name.startswith('Integrated_Coast_')}
for o in list(s.objects):
 if o.name.startswith('Integrated_Coast_') and active(o):
  old=bpy.data.objects['JunctionBaseline_'+o.name];o.data=old.data.copy()
original_pts=[base.matrix_world@v.co for v in base.data.vertices]
front=sorted([original_pts[i*26+25] for i in range(101)],key=lambda p:p.x)
def boundary(x,points=front):
 xs=[p.x for p in points];j=max(0,min(len(points)-2,bisect.bisect_right(xs,x)-1));a,b=points[j:j+2];t=(x-a.x)/max(1e-8,b.x-a.x);return a.lerp(b,t)
changed=[];protected=[]
for v in land.data.vertices[:2626]:
 q=base.matrix_world@v.co
 if not X0<q.x<X1 or q.y>-.25-1.55:protected.append(v.index);continue
 p=boundary(q.x);dist=q.y-p.y
 if dist<-.02 or dist>1.4:protected.append(v.index);continue
 retreat=design(q.x)[1]*envelope(q.x)
 w=(1-smooth(0,1.4,dist))*smooth(1.55,2.0,abs(q.y+.25))
 v.co.y+=retreat*w
 if retreat*w>1e-7:changed.append(v.index)
 else:protected.append(v.index)
newfront=sorted([land.matrix_world@land.data.vertices[i*26+25].co for i in range(101)],key=lambda p:p.x)
# Side rings become an interior closing core, behind the deliberately visible faces.
for v in land.data.vertices[2626:]:
 q=base.matrix_world@v.co
 if X0<q.x<X1 and q.y<-.25-1.55:
  v.co.y+=1.35*envelope(q.x)
  if q.z>1.2:v.co.z-=.25*envelope(q.x)
edge=land.data.uv_layers['CoastEdgeBlend']
for loop in land.data.loops:
 q=land.matrix_world@land.data.vertices[loop.vertex_index].co
 if X0<q.x<X1 and q.y< -1.8:
  p=boundary(q.x,newfront);d=max(0,q.y-p.y)
  edge.data[loop.index].uv=((1-smooth(0,.24+.19*design(q.x)[1],d))*envelope(q.x),(q.x-X0)/(X1-X0))
# Read current outside profile only for the two end joins; the sample itself is authored.
sv=[];sf=[]
# Recover the original readable faces with their own per-face UVs. The new mesh
# is an INNER support and a crown junction; it must never average over relief.
reliefs=[]
for ri in range(11,16):
 source=bpy.data.objects['Original_Coast_Rock_%02d'%ri]
 child=source.copy();child.data=source.data.copy();child.name='Junction_Relief_%02d'%ri
 col.objects.link(child);child.hide_render=False;child.hide_set(False)
 bm=bmesh.new();bm.from_mesh(child.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(X0,0,0),plane_no=(1,0,0),clear_inner=True)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(X1,0,0),plane_no=(1,0,0),clear_outer=True)
 bm.to_mesh(child.data);bm.free();child.data.update();reliefs.append(child)
 for index,m in enumerate(child.data.materials):
  name=m.name.replace('Original_Coast_Stone_','Junction_Relief_')
  newmat=bpy.data.materials.get(name)
  if not newmat:newmat=m.copy();newmat.name=name
  child.data.materials[index]=newmat
 offset=len(sv);sv.extend([child.matrix_world@v.co for v in child.data.vertices]);sf.extend([tuple(i+offset for i in f.vertices) for f in child.data.polygons])
tree=BVHTree.FromPolygons(sv,sf)
trimmed=[]
for ob in list(s.objects):
 if not active(ob) or not ob.name.startswith('Integrated_Coast_'):continue
 if not any(X0<v.co.x<X1 and v.co.y<0 for v in ob.data.vertices):continue
 bm=bmesh.new();bm.from_mesh(ob.data)
 for x in [X0,X1]:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(x,0,0),plane_no=(1,0,0))
 remove=[f for f in bm.faces if X0+1e-5<f.calc_center_median().x<X1-1e-5 and f.calc_center_median().y<-.8]
 bmesh.ops.delete(bm,geom=remove,context='FACES')
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
 bm.to_mesh(ob.data);bm.free();ob.data.update();trimmed.append(ob.name)
# Include original turf stations so the shared grass/rock boundary is exact.
xs=sorted(set([k[0] for k in knots]+[p.x for p in newfront if X0<p.x<X1]))
rows=[0,.18,.22,.53,.58,.91,1.]
verts=[];uvs=[]
for x in xs:
 crown,retreat,sh,proj,foot=design(x);p=boundary(x);g=boundary(x,newfront);e=envelope(x)
 # Top slopes out from thin soil. The middle shoulder thickens downward into bedrock.
 # Crown height drops into the joints rather than staying an equal-height rim.
 joint_a=math.exp(-((x+17.85)/.62)**2);joint_b=math.exp(-((x+12.4)/.68)**2)
 crown_drop=.09+.10*retreat+.37*joint_a+.30*joint_b
 lip_z=p.z-crown_drop
 shoulder=smooth(-17.8,-16.65,x)*(1-smooth(-14.1,-12.9,x))
 bevel=.018+.018*(.5+.5*math.sin(x*1.8))
 # Away from the single low shoulder these rows lie on one steep main face.
 face_r3=crown*(1-(lip_z-sh-.12)/(lip_z+2.65))+foot*((lip_z-sh-.12)/(lip_z+2.65))
 face_r4=crown*(1-(lip_z-sh+.11)/(lip_z+2.65))+foot*((lip_z-sh+.11)/(lip_z+2.65))
 r3=face_r3*(1-shoulder)+(crown*.76+.03)*shoulder
 r4=face_r4*(1-shoulder)+proj*shoulder
 levels=[(g.y,g.z),(p.y-crown,lip_z),(p.y-crown-.009,lip_z-bevel),
         (p.y-r3,sh+.12),(p.y-r4,sh-.11),
         (p.y-foot,-2.65),(p.y-foot+.19,-4.10)]
 for ri,(y,z) in enumerate(levels):
  if ri>0:
   hit=tree.ray_cast(Vector((x,-12,z)),Vector((0,1,0)),20)[0]
   if hit is not None:y=hit.y+(.045 if ri==1 else .24)
   else:y=p.y+.38
   if ri==1:y=min(y,g.y-.035)
  lean=(.31*joint_a-.34*joint_b+.12*math.sin(x*.58))*e
  shift=lean*[0,0,.06,.61,.66,1.,1.][ri]
  verts.append((x+shift,y,z));uvs.append(((x-X0)/(X1-X0),1-rows[ri]))
faces=[]
for i in range(len(xs)-1):
 for j in range(6):faces.append((i*7+j,i*7+j+1,(i+1)*7+j+1,(i+1)*7+j))
me=bpy.data.meshes.new('Junction_Authored_Connected_Faces');me.from_pydata(verts,[],faces);me.update()
uv=me.uv_layers.new(name='AuthoredFacePaint')
for l in me.loops:uv.data[l.index].uv=uvs[l.vertex_index]
uv2=me.uv_layers.new(name='JunctionContactUV')
for l in me.loops:uv2.data[l.index].uv=uvs[l.vertex_index]
# Face orientation consistently outward. A slight threshold smooths only coplanar samples.
# Open terrain strip: retain explicit, consistent winding. Volume-based recalc
# is ambiguous for an open strip and can invert the crown independently.
for p in me.polygons:p.use_smooth=False
mat=bpy.data.materials.get('Junction_Coast_Painted') or bpy.data.materials.new('Junction_Coast_Painted');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1;bs.inputs['Base Color'].default_value=(.35,.31,.23,1)
if (A/'junction_paint.png').exists():
 tx=mat.node_tree.nodes.get('JunctionPaint') or mat.node_tree.nodes.new('ShaderNodeTexImage');tx.name='JunctionPaint';tx.image=bpy.data.images.load(str(A/'junction_paint.png'),check_existing=True);tx.image.reload();mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
me.materials.append(mat);ob=bpy.data.objects.new('Junction_Coast_Sample',me);col.objects.link(ob)
ob['authoring']='Explicit crown/cleft/shoulder profiles made through Blender MCP. No reference-game geometry.'
# Verify the exact grass-edge join, protected road and all unrelated meshes.
assert all((land.data.vertices[i].co-base.data.vertices[i].co).length==0 for i in protected)
assert all(sig(s.objects[n])==h for n,h in others.items())
err=max((Vector(verts[i*7])-boundary(x,newfront)).length for i,x in enumerate(xs))
assert err<1e-5
report={'x_range':[X0,X1],'knots':knots,'rows':rows,'stations':xs,'vertices':verts,'turf_vertices_changed':len(changed),
 'protected_turf_vertices':len(protected),'unrelated_meshes_unchanged':len(others),'trimmed_old_meshes':trimmed,'grass_edge_max_error_m':err,
 'surface_source':'Five existing self-authored relief modules with original face UVs; new crown junction and recessed inner support, not an exterior smoothing shell',
 'relief_meshes':[o.name for o in reliefs],'geometry_authoring':'Blender MCP'}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
# Save source now. Export is a later step after paint and contact inspection.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/island_blender/nameless_island.blend'))
print('JUNCTION_SAMPLE_AUTHORED',len(xs),'stations',len(changed),'turf vertices;',len(others),'unrelated meshes unchanged; edge error',err)
