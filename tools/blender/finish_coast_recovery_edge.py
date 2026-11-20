"""Reuse sparse source grass clumps at the actual recovered terrain edge, MCP."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
assert not s.objects.get('Recovery_Forest_Strict_RecoveryGrass_00')
original=bpy.data.scenes['Coast_Recovery_Original_Readonly_20261120'];source=original.objects['Left_Grass_Clusters'];ground=s.objects['Recovery_WALK_Forest_Ground'];tree=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(f.vertices) for f in ground.data.polygons])
coords=[(-70.8,11.1),(-70.15,12.0),(-69.9,13.7),(-69.5,10.0),(-68.5,9.3),(-66.9,8.6),(-65.4,8.2),(-64.6,9.5),(-62.05,9.5),(-67.7,15.0),(-68.6,15.8),(-62.5,15.0)]
for i,(x,y) in enumerate(coords):
 hit=tree.ray_cast(Vector((x,y,20)),Vector((0,0,-1)))[0]
 if hit is None:continue
 o=source.copy();o.data=source.data.copy();o.name='Recovery_Forest_Strict_RecoveryGrass_%02d'%i;s.collection.objects.link(o)
 bm=bmesh.new();bm.from_mesh(o.data);remove=[v for v in bm.verts if abs(v.co.x+13.5)>1.0 or abs(v.co.y+.7)>1.0];bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free()
 z=min(v.co.z for v in o.data.vertices);rot=Matrix.Rotation(i*1.63,3,'Z');scale=.82+(i%3)*.08
 for v in o.data.vertices:v.co=hit+rot@(Vector((v.co.x+13.5,v.co.y+.7,(v.co.z-z)))*scale)-Vector((0,0,.018))
 o.data.update();o.hide_render=False;o.hide_set(False)
# Remove remaining sample prop fragments on the back of the cropped local face.
o=s.objects['Recovery_Cape_Inset_West'];bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if (lambda p:p.z>.343 and p.y>-.11 and p.x>-.28)(f.calc_center_median())],context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()
for im in bpy.data.images:
 if 'coast_recovery/core_wash' in im.filepath.replace('\\','/'):
  if im.packed_file:im.unpack(method='REMOVE')
  im.reload();im.pack()
# Pack the registered floor in the editable source using an explicit UV channel.
g=ground;uv=g.data.uv_layers.get('RecoveryFloor') or g.data.uv_layers.new(name='RecoveryFloor')
for p in g.data.polygons:
 for li in p.loop_indices:
  v=g.data.vertices[g.data.loops[li].vertex_index].co;uv.data[li].uv=((v.x+72.5)/23,(v.y-4)/31)
for i,mat in enumerate(list(g.data.materials)):
 mat=mat.copy();g.data.materials[i]=mat
 tex=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'),None)
 if tex:
  tex.image=bpy.data.images.load(str(A/'cape_floor.png'),check_existing=True);tex.image.pack();coord=mat.node_tree.nodes.new('ShaderNodeUVMap');coord.uv_map='RecoveryFloor';mat.node_tree.links.new(coord.outputs['UV'],tex.inputs['Vector'])
report=json.loads((A/'assembly.json').read_text());report['revision']='coast-structure-recovery-8';report['reused_grass_clumps']=len(coords);report['source_floor_uv']='RecoveryFloor';s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=g
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL_LOCAL_REFINEMENT',len(s.objects))
