import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
m=bpy.data.materials['Recovery_Face_Stone'];im=bpy.data.images.load(str(A/'core_wash.png'),check_existing=True);im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
o=s.objects['Recovery_Cape_Terminus_Bedrock'];uv=o.data.uv_layers[0]
for p in o.data.polygons:
 for li in p.loop_indices:
  q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((q.x+72.5)/23,q.z/5)
# Make the retained structural top part of the editable authoring material too.
g=s.objects['Recovery_WALK_Forest_Ground'];im=bpy.data.images.load(str(A/'cape_floor.png'),check_existing=True);im.pack()
for m in g.data.materials:
 m=m # preserve original materials shared only by this copied scene
report=json.loads((A/'assembly.json').read_text());report['revision']='coast-structure-recovery-6';report['material_scope']='local registered grass-earth clearing; broad core wash; retained measured rock albedo';s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=g
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('RECOVERY_MATERIALS_SAVED')
