"""Embed two retained measured rock faces into the continuous cape, via MCP."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';O=R/'artifacts/coast-structure-recovery'
s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
assert not s.objects.get('Recovery_Cape_Inset_West')
source=bpy.data.scenes['Tripo_Grit_Textured_Delivery_20261119'].objects['Grit_Delivery_Rocks']
P=Matrix(json.loads((R/'assets/layered_island/tripo_replica/game_assembly.json').read_text())['placement_matrix'])
m=bpy.data.materials.new('Recovery_Inset_Stone');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.94
im=bpy.data.images.load(str(R/'assets/layered_island/tripo_replica/textures_weight/weight_delivery_rocks_basecolor.png'),check_existing=True);im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
# Only local natural faces, without the Tripo camp, its stairs or entire platform.
specs=[('West',(-.51,-.06,-.39,.10,-.01,.335),(-2.1,1.2,.12)),('StairRight',(.115,.51,-.39,.08,-.01,.325),(-.05,-.25,.10))]
for name,limits,delta in specs:
 o=source.copy();o.data=source.data.copy();o.name='Recovery_Cape_Inset_'+name;o['game_name']='Cape_Inset_'+name;s.collection.objects.link(o);o.hide_render=False;o.hide_set(False)
 bm=bmesh.new();bm.from_mesh(o.data)
 for axis,low,high in [(0,limits[0],limits[1]),(1,limits[2],limits[3]),(2,limits[4],limits[5])]:
  for cut,sign in [(low,-1),(high,1)]:
   point=Vector((0,0,0));point[axis]=cut;normal=Vector((0,0,0));normal[axis]=sign
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,dist=.000001,clear_outer=True)
 # Crop boundaries lie buried inside the continuous supporting core.
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();o.data.materials.clear();o.data.materials.append(m)
 for f in o.data.polygons:f.material_index=0
 o.matrix_world=Matrix.Translation(Vector(delta))@P@source.matrix_world
# Close the small strips beside the recovered wider stair foundation with the
# existing bedrock, extending buried side vertices only, never the tread geometry.
core=s.objects['Recovery_Cape_Terminus_Bedrock'];axis=Vector((-.8,4.8,0)).normalized();side=Vector((axis.y,-axis.x,0));origin=Vector((-62.5,4,0))
for v in core.data.vertices:
 q=v.co;rel=q-origin;t=rel.dot(axis);w=rel.dot(side)
 if 1.7<t<5.3 and 1.10<abs(w)<1.70:
  v.co-=side*(1 if w>0 else -1)*.20
core.data.update()
report=json.loads((A/'assembly.json').read_text());report['revision']='continuous-platform-original-stair-local-rocks-2';report['local_rocks']=[{'name':n,'source_bounds':list(b),'placement_offset':list(d)} for n,b,d in specs];s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=core
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('LOCAL_ROCKS_EXPORTED')
