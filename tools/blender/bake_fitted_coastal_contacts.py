"""Actual fitted-shore AO in a dedicated UV2, through Blender MCP."""
import bpy, json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/original_coastal_rock';O=R/'artifacts/original-shore-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
objects=sorted([o for o in s.objects if o.name.startswith('Original_Coast_Rock_') and not any(c.name.startswith('90_') for c in o.users_collection)],key=lambda o:o.name)
assert len(objects)==18
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:
    ob.hide_set(False);ob.select_set(True)
    if ob.data.uv_layers.get('CoastContactUV') is None:ob.data.uv_layers.new(name='CoastContactUV')
    ob.data.uv_layers.active_index=ob.data.uv_layers.find('CoastContactUV')
    ob.data.uv_layers['CoastContactUV'].active_render=True
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=.88,island_margin=.009,area_weight=.5,correct_aspect=True,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
image=bpy.data.images.get('FittedCoastContact') or bpy.data.images.new('FittedCoastContact',width=4096,height=2048,alpha=False)
image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color'
for ob in objects:
    for mat in ob.data.materials:
        node=mat.node_tree.nodes.get('FittedCoastContactBake') or mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.name='FittedCoastContactBake';node.image=image;mat.node_tree.nodes.active=node
engine=s.render.engine;samples=s.cycles.samples
s.render.engine='CYCLES';s.cycles.samples=96;s.render.bake.use_clear=False;s.render.bake.margin=8;s.render.bake.target='IMAGE_TEXTURES'
bpy.ops.object.bake(type='AO')
image.filepath_raw=str(A/'fitted_coast_contact.png');image.file_format='PNG';image.save()
for ob in objects:
    ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
s.render.engine=engine;s.cycles.samples=samples
(O/'fitted-contact-bake.json').write_text(json.dumps({'objects':len(objects),'uv_channel':'TEXCOORD_1 / UV2, coast objects only','resolution':[4096,2048],'samples':96,'basis':'actual fitted geometry and current island occluders'},indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('FITTED_CONTACT_BAKED')
