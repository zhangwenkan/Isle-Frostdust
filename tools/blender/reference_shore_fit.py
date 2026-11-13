"""Local study fit of attributed Wandering Sword shore assets. Run via Blender MCP."""
import bpy,bmesh,json,math,bisect,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/reference-shore-fit';O.mkdir(exist_ok=True)
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
D=json.loads((S/'scene-manifest.json').read_text(encoding='utf8'))
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def sig(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for layer in o.data.uv_layers:
  for uv in layer.data:h.update(str(tuple(uv.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={ob.name:sig(ob) for ob in active() if not ob.name.startswith('WS_Reference_Shore_')}
arc=bpy.data.collections.get('90_Before_Reference_Shore_Study') or bpy.data.collections.new('90_Before_Reference_Shore_Study')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True
def baseline(ob):
 name='ReferenceShoreBaseline_'+ob.name;b=bpy.data.objects.get(name)
 if b is None:
  b=ob.copy();b.data=ob.data.copy();b.name=name;arc.objects.link(b);b.hide_set(True);b.hide_render=True
 return b
land=s.objects['Fish_West_Continuous_Land'];base=baseline(land)
col=bpy.data.collections.get('35_Reference_Shore_Study') or bpy.data.collections.new('35_Reference_Shore_Study')
if col.name not in s.collection.children:s.collection.children.link(col)
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
boundary=[i*26 for i in range(101)]+[2600+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
top=[base.matrix_world@v.co for v in list(base.data.vertices)[:2626]];perimeter=[top[i] for i in boundary];lengths=[0.]
from mathutils.bvhtree import BVHTree
turf_tree=BVHTree.FromPolygons(top,[tuple(p.vertices) for p in base.data.polygons if p.material_index==0])
for j in range(250):lengths.append(lengths[-1]+(perimeter[(j+1)%250]-perimeter[j]).length)
total=lengths[-1]
def at(u):
 u=u%total;j=min(249,bisect.bisect_right(lengths,u)-1);f=(u-lengths[j])/(lengths[j+1]-lengths[j]);p=perimeter[j].lerp(perimeter[(j+1)%250],f)
 # Corner normals follow the perimeter instead of projecting the whole asset off a straight wall.
 prev=perimeter[(j+1)%250]-perimeter[(j-1)%250];nxt=perimeter[(j+2)%250]-perimeter[j]
 tangent=prev.lerp(nxt,f);return p,Vector((-tangent.y,tangent.x,0)).normalized()
sources={}
mat=bpy.data.materials.get('Reference_WS_Shore_Rock') or bpy.data.materials.new('Reference_WS_Shore_Rock');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
for name in ['SM_XYNJiangnan017','SM_XYNJiangnan018','SM_XYNJiangnan001','SM_XYNJiangnan014']:
 e=next(v for k,v in D['meshes'].items() if k.endswith('/'+name+'.uasset'))
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=e['gltf']);added=set(bpy.data.objects)-old;ob=next(o for o in added if o.type=='MESH')
 ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4);sources[name]=ob.data.copy()
 for o in added:bpy.data.objects.remove(o,do_unlink=True)
 if name=='SM_XYNJiangnan017':
  texture=str(R/'assets/reference_shore/T_XuanyaNew001.png')
  tex=mat.node_tree.nodes.get('OriginalShoreTexture') or mat.node_tree.nodes.new('ShaderNodeTexImage');tex.name='OriginalShoreTexture';tex.image=bpy.data.images.load(texture,check_existing=True);mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
mat['source_game']='Wandering Sword / 逸剑风云决';mat['usage']='Attributed local reference study, not original project art'
# Backing closes the turf body, while foreground rock shoulders determine the visible cliff.
verts=[p.copy() for p in top];polys=[p for p in base.data.polygons if p.material_index==0];faces=[tuple(p.vertices) for p in polys]
mats=[0]*len(faces);uvs=[tuple(base.data.uv_layers.active.data[j].uv) for p in polys for j in p.loop_indices]
previous=boundary
for zoffset,inset in [(.10,.02),(.40,.38),(5.6,.50)]:
 current=[]
 for j,p in enumerate(perimeter):
  q,n=at(lengths[j]);q-=n*inset;q.z=p.z-zoffset;current.append(len(verts));verts.append(q)
 for j in range(250):
  k=(j+1)%250;faces.append((previous[j],previous[k],current[k],current[j]));mats.append(1);uvs.extend([(0,0)]*4)
 previous=current
faces.append(tuple(reversed(previous)));mats.append(1);uvs.extend([(0,0)]*250)
recess=bpy.data.materials.get('Reference_Shore_Recess') or bpy.data.materials.new('Reference_Shore_Recess');recess.use_nodes=True
bs=recess.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.13,.16,.12,1);bs.inputs['Roughness'].default_value=1
me=bpy.data.meshes.new('West_Shore_Recessed_Core');me.from_pydata(verts,[],faces);me.materials.append(base.data.materials[0]);me.materials.append(recess);me.update()
uv=me.uv_layers.new(name='CoastUV');uv.data.foreach_set('uv',[v for pair in uvs for v in pair])
if base.data.color_attributes:
 ca=me.color_attributes.new(name='LandscapeColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',[v for i in range(len(verts)) for v in (tuple(base.data.color_attributes['LandscapeColor'].data[i].color) if i<2626 else (.3,.32,.27,1))])
for p,m in zip(me.polygons,mats):p.material_index=m;p.use_smooth=m==0
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-10],context='FACES_ONLY');bm.to_mesh(me);bm.free();land.data=me;land.matrix_world.identity()
# Broad overlapping masses, not narrow isolated pillars. Their upper surfaces stay under the turf.
widths=[5.6,4.0,5.3,4.6,6.1,4.2,5.8,4.8,5.3,4.1,5.7,4.6,5.9,4.4,5.2,4.8,5.5,4.5,5.0]
factor=total/sum(w*.52 for w in widths);cursor=0.;placements=[]
for i,w in enumerate(widths):
 w*=factor;center=cursor+w*.26;cursor+=w*.52
 name=['SM_XYNJiangnan017','SM_XYNJiangnan018','SM_XYNJiangnan017','SM_XYNJiangnan018','SM_XYNJiangnan017'][i%5]
 mesh=sources[name].copy();rot=Matrix.Rotation([.0,.13,-.18,.24,-.12,.09][i%6],4,'Z');mesh.transform(rot)
 lo=Vector([min(v.co[j] for v in mesh.vertices) for j in range(3)]);hi=Vector([max(v.co[j] for v in mesh.vertices) for j in range(3)])
 depth=[3.5,2.8,3.2,3.8,2.9][i%5];height=[5.3,5.7,5.1,5.6][i%4]
 for v in mesh.vertices:
  u=(v.co.x-lo.x)/(hi.x-lo.x);out=(hi.y-v.co.y)/(hi.y-lo.y)
  p,n=at(center+(u-.5)*w)
  q=p+n*((out-.83)*depth)
  q.z=p.z-.015-pow((hi.z-v.co.z)/(hi.z-lo.z),1.55)*height
  # Existing grass/path covers the interior: prevent embedded tops from breaking through.
  support=turf_tree.ray_cast(Vector((q.x,q.y,40)),Vector((0,0,-1)))[0]
  if support:q.z=min(q.z,support.z-.055)
  v.co=q
 mesh.materials.clear();mesh.materials.append(mat)
 for poly in mesh.polygons:poly.material_index=0
 # Recalculate the source normals after fitting the island curvature, keep UV islands intact.
 # Mapping source +Y inward across the clockwise island perimeter mirrors the basis.
 # Reverse winding as well as recalculating normals, so normal back-face culling is valid.
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 if mesh.has_custom_normals:mesh.normals_split_custom_set([(0,0,0)]*len(mesh.loops))
 mesh.update();ob=bpy.data.objects.new('WS_Reference_Shore_%02d'%i,mesh);col.objects.link(ob)
 ob['source_game']='Wandering Sword';ob['source_mesh']=name;ob['local_reference_study']=True
 placements.append(dict(name=ob.name,source=name,center_s=center,width=w,depth=depth,height=height))
# Ferns attach to the resulting outer surface; their original leaf meshes are preserved.
from mathutils.bvhtree import BVHTree
tv=[];tf=[]
for ob in [land]+list(col.objects):
 off=len(tv);tv.extend([ob.matrix_world@v.co for v in ob.data.vertices]);tf.extend([tuple(off+j for j in p.vertices) for p in ob.data.polygons])
tree=BVHTree.FromPolygons(tv,tf);changed=[land.name]
for ob in active():
 if not ob.name.startswith('Cliff_Fern_West_'):continue
 b=baseline(ob);ob.data=b.data.copy();ob.matrix_world=b.matrix_world.copy();ps=[ob.matrix_world@v.co for v in ob.data.vertices];cx=sum(p.x for p in ps)/len(ps);z=max(p.z for p in ps)-.1
 hit=tree.ray_cast(Vector((cx,-25,z)),Vector((0,1,0)))[0]
 if hit:
  delta=hit-Vector((cx,max(p.y for p in ps),z));inv=ob.matrix_world.inverted()
  for v,p in zip(ob.data.vertices,ps):v.co=inv@(p+delta)
  ob.data.update();changed.append(ob.name)
assert max((land.data.vertices[i].co-top[i]).length for i in range(2626))<1e-6
preserved=[n for n in before if n not in changed];assert all(sig(s.objects[n])==before[n] for n in preserved)
(O/'authoring.json').write_text(json.dumps(dict(placements=placements,preserved=len(preserved),changed=changed,top_vertices_unchanged=2626,source_texture=texture,source_library=str(S)),ensure_ascii=False,indent=2),encoding='utf8')
for refscene in list(bpy.data.scenes):
 if refscene.name.startswith('Actual_'):bpy.data.scenes.remove(refscene)
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('REFERENCE_SHORE_FIT',len(placements),'preserved',len(preserved))
