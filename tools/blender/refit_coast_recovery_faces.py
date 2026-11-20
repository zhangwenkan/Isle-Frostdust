"""Refit measured faces along the source stair boundary; remove failed crops."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';O=R/'artifacts/coast-structure-recovery';s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
for key in ['Recovery_Cape_Inset_West','Recovery_Cape_Inset_StairRight']:
 old=s.objects[key];s.collection.objects.unlink(old);old.name+='RejectedCrop';old.hide_render=True
source=bpy.data.scenes['Tripo_Grit_Textured_Delivery_20261119'].objects['Grit_Delivery_Rocks'];P=Matrix(json.loads((R/'assets/layered_island/tripo_replica/game_assembly.json').read_text())['placement_matrix']);mat=bpy.data.materials['Recovery_Inset_Stone']
specs=[('West',[(Vector((1,-.287,0)), -.027),((0,1,0),.075),((0,0,1),.385)],(-1.70,.65,-.04)),('StairRight',[(Vector((-1,.287,0)),-.123),((1,0,0),.32),((0,1,0),-.065),((0,0,1),.373)],(.78,-.45,-.01))]
for name,planes,delta in specs:
 o=source.copy();o.data=source.data.copy();o.name='Recovery_Cape_Inset_'+name;o['game_name']='Cape_Inset_'+name;s.collection.objects.link(o);o.hide_render=False;o.hide_set(False)
 bm=bmesh.new();bm.from_mesh(o.data)
 for n,d in planes:
  n=Vector(n);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=n*d/n.length_squared,plane_no=n,dist=.000001,clear_outer=True)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();o.data.materials.clear();o.data.materials.append(mat)
 for f in o.data.polygons:f.material_index=0
 o.matrix_world=Matrix.Translation(Vector(delta))@P@source.matrix_world
# Stone colours approach the same value as the inserted faces.
for key,color in [('Recovery_Face_Stone',(.19,.207,.177)),('Recovery_Tread_Stone',(.31,.33,.279)),('Recovery_Edge_Stone',(.24,.26,.214))]:
 m=bpy.data.materials[key];m.diffuse_color=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
# The original stair notches had small gaps; move only the adjacent buried wall
# edge to the actual restored curb. No new isolated patch stones.
core=s.objects['Recovery_Cape_Terminus_Bedrock'];axis=Vector((-.8,4.8,0)).normalized();side=Vector((axis.y,-axis.x,0));origin=Vector((-62.5,4,0))
for v in core.data.vertices:
 p=v.co;rel=p-origin;t=rel.dot(axis);w=rel.dot(side)
 if 2.3<t<5.1 and 1.02<abs(w)<1.5:v.co-=side*(1 if w>0 else -1)*.10
core.data.update()
report=json.loads((A/'assembly.json').read_text());report['revision']='continuous-platform-original-stair-local-rocks-3';report['local_rocks_source']='Grit_Delivery_Rocks, clipped along measured stair flanks, two embedded partial exposures';s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=core
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('REFITTED_LOCAL_FACES')
