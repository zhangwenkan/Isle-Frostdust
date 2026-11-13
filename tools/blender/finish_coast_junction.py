import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/coast_junction';O=R/'artifacts/coast-junction-refine-review'
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s;ob=s.objects['Junction_Coast_Sample'];mat=bpy.data.materials['Junction_Coast_Painted']
bs=mat.node_tree.nodes.get('Principled BSDF');tx=mat.node_tree.nodes.get('JunctionPaint') or mat.node_tree.nodes.new('ShaderNodeTexImage');tx.name='JunctionPaint'
tx.image=bpy.data.images.load(str(A/'junction_paint.png'),check_existing=True);tx.image.reload();mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
image=bpy.data.images.get('JunctionContact') or bpy.data.images.new('JunctionContact',width=2048,height=1024,alpha=False)
image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color'
bpy.ops.object.select_all(action='DESELECT')
objects=list(bpy.data.collections['38_Coast_Junction_Sample'].objects)
for item in objects:
 item.select_set(True);item.hide_set(False);item.data.uv_layers.active_index=1;item.data.uv_layers[1].active_render=True
 for m in item.data.materials:
  node=m.node_tree.nodes.get('JunctionContactBake') or m.node_tree.nodes.new('ShaderNodeTexImage');node.name='JunctionContactBake';node.image=image;m.node_tree.nodes.active=node
bpy.context.view_layer.objects.active=ob
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=.85,island_margin=.006,area_weight=.8,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
engine=s.render.engine;samples=s.cycles.samples;s.render.engine='CYCLES';s.cycles.samples=32;s.render.bake.use_clear=True;s.render.bake.margin=4
bpy.ops.object.bake(type='AO')
image.filepath_raw=str(A/'junction_contact.png');image.file_format='PNG';image.save()
for item in objects:item.data.uv_layers.active_index=0;item.data.uv_layers[0].active_render=True
s.render.engine=engine;s.cycles.samples=samples
bpy.data.libraries.write(str(A/'coast_junction.blend'),{bpy.data.collections['38_Coast_Junction_Sample']},path_remap='ABSOLUTE',fake_user=True,compress=True)
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('JUNCTION_EXPORTED_WITH_CONTACT')
