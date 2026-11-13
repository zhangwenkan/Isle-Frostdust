"""Bake contact on the actual integrated mass, only via Blender MCP."""
import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/original_coastal_rock';O=R/'artifacts/coast-integration-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
objects=list(bpy.data.collections['37_Integrated_Coastal_Mass'].objects)
assert len(objects)==19
mat=bpy.data.materials['Integrated_Coast_Painted'];bs=mat.node_tree.nodes.get('Principled BSDF');tx=mat.node_tree.nodes['IntegratedPaint'];tx.image=bpy.data.images.load(str(A/'integrated_coast_paint.png'),check_existing=True);tx.image.reload();mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:
    ob.hide_set(False);ob.select_set(True)
    if not ob.data.uv_layers.get('IntegratedContactUV'):ob.data.uv_layers.new(name='IntegratedContactUV')
    ob.data.uv_layers.active_index=ob.data.uv_layers.find('IntegratedContactUV');ob.data.uv_layers['IntegratedContactUV'].active_render=True
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=.85,island_margin=.004,area_weight=.8,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
image=bpy.data.images.get('IntegratedCoastContact') or bpy.data.images.new('IntegratedCoastContact',width=4096,height=2048,alpha=False)
image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color'
node=mat.node_tree.nodes.get('IntegratedContactBake') or mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='IntegratedContactBake';node.image=image;mat.node_tree.nodes.active=node
engine=s.render.engine;samples=s.cycles.samples;s.render.engine='CYCLES';s.cycles.samples=64
s.render.bake.use_clear=False;s.render.bake.margin=6;s.render.bake.target='IMAGE_TEXTURES';bpy.ops.object.bake(type='AO')
image.filepath_raw=str(A/'integrated_coast_contact.png');image.file_format='PNG';image.save()
for ob in objects:
    ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
s.render.engine=engine;s.cycles.samples=samples
bpy.data.libraries.write(str(A/'integrated_coastal_mass.blend'),{bpy.data.collections['37_Integrated_Coastal_Mass']},path_remap='ABSOLUTE',fake_user=True,compress=True)
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('INTEGRATED_CONTACT_READY')
