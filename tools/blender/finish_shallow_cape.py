import bpy
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/shallow_cape'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
mat=bpy.data.materials['ShallowCape_Stone'];bs=mat.node_tree.nodes.get('Principled BSDF')
tx=mat.node_tree.nodes.get('SlabPaint') or mat.node_tree.nodes.new('ShaderNodeTexImage');tx.name='SlabPaint'
tx.image=bpy.data.images.load(str(A/'slab_paint.png'),check_existing=True);tx.image.reload();mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
objects=list(bpy.data.collections['39_Shallow_Rock_Cape'].objects)
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True);ob.data.uv_layers.active_index=1;ob.data.uv_layers[1].active_render=True
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=.86,island_margin=.008,area_weight=.8,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
im=bpy.data.images.get('ShallowCapeContact') or bpy.data.images.new('ShallowCapeContact',width=1024,height=1024,alpha=False)
im.generated_color=(1,1,1,1);im.colorspace_settings.name='Non-Color'
node=mat.node_tree.nodes.get('CapeContactBake') or mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='CapeContactBake';node.image=im;mat.node_tree.nodes.active=node
engine=s.render.engine;samples=s.cycles.samples;s.render.engine='CYCLES';s.cycles.samples=16;s.render.bake.use_clear=True;s.render.bake.margin=6
bpy.ops.object.bake(type='AO');im.filepath_raw=str(A/'slab_contact.png');im.file_format='PNG';im.save()
for ob in objects:ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
s.render.engine=engine;s.cycles.samples=samples
bpy.data.libraries.write(str(A/'shallow_cape.blend'),{bpy.data.collections['39_Shallow_Rock_Cape']},path_remap='ABSOLUTE',fake_user=True,compress=True)
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('SHALLOW_CAPE_EXPORTED')
