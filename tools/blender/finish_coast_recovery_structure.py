"""Shared corner closure and crop burial correction, Blender MCP only."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
terrain=s.objects['Recovery_WALK_Forest_Ground'];bm=bmesh.new();bm.from_mesh(terrain.data)
edges=[e for e in bm.edges if e.is_boundary and max(v.co.x for v in e.verts)<-53.99 and min(v.co.x for v in e.verts)<-54.01];normal={}
for e in edges:
 p,q=[v.co for v in e.verts];delta=q-p;out=Vector((delta.y,-delta.x,0)).normalized()
 if out.dot((p+q)*.5-e.link_faces[0].calc_center_median())<0:out=-out
 for v in e.verts:normal[v]=normal.get(v,Vector())+out
verts=[];idx={};uv=[];faces=[]
for v,out in normal.items():
 out.normalize()
 for k,(f,w) in enumerate([(1,0),(.7,.10),(.3,.20),(0,.14)]):
  q=v.co+out*w;q.z=-.42+(v.co.z+.42)*f;idx[v,k]=len(verts);verts.append(tuple(q));uv.append((v.co.x*.12,1-f))
for e in edges:
 a,b=e.verts
 for k in range(3):faces.append((idx[a,k],idx[b,k],idx[b,k+1],idx[a,k+1]))
me=bpy.data.meshes.new('Recovery_Closed_Shared_Edge_Core');me.from_pydata(verts,[],faces);me.update();me.materials.append(bpy.data.materials['Recovery_Face_Stone']);core=s.objects['Recovery_Cape_Terminus_Bedrock'];core.data=me
u=me.uv_layers.new(name='UVMap')
for p in me.polygons:
 for li in p.loop_indices:u.data[li].uv=uv[me.loops[li].vertex_index]
bm.free()
source=bpy.data.scenes['Tripo_Grit_Textured_Delivery_20261119'].objects['Grit_Delivery_Rocks'];P=Matrix(json.loads((R/'assets/layered_island/tripo_replica/game_assembly.json').read_text())['placement_matrix']);mat=bpy.data.materials['Recovery_Inset_Stone']
specs=[('West',[(Vector((1,-.287,0)), -.027),((0,1,0),.075),((0,0,1),.385)],(-.80,.55,-.06)),('StairRight',[(Vector((-1,.287,0)),-.123),((1,0,0),.32),((0,1,0),-.065),((0,0,1),.373)],(.10,.20,-.15))]
for name,planes,delta in specs:
 o=s.objects['Recovery_Cape_Inset_'+name];o.data=source.data.copy();bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=0],context='FACES')
 for n,d in planes:
  n=Vector(n);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=n*d/n.length_squared,plane_no=n,dist=.000001,clear_outer=True)
 # Remove small isolated remnants left by the sample prop boundary.
 unseen=set(bm.verts)
 while unseen:
  seed=unseen.pop();component={seed};stack=[seed]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    other=e.other_vert(v)
    if other in unseen:unseen.remove(other);component.add(other);stack.append(other)
  if len(component)<180:bmesh.ops.delete(bm,geom=list(component),context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();o.data.materials.clear();o.data.materials.append(mat)
 for f in o.data.polygons:f.material_index=0
 o.matrix_world=Matrix.Translation(Vector(delta))@P@source.matrix_world
report=json.loads((A/'assembly.json').read_text());report['revision']='continuous-cape-shared-boundary-5';s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=core
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('SHARED_CORE_AND_BURIED_FACES')
