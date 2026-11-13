import bpy
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/original_coastal_rock'
col=bpy.data.collections['37_Integrated_Coastal_Mass']
for ob in col.objects:
    keep=ob.data.uv_layers[0].name
    for layer in list(ob.data.uv_layers):
        if layer.name not in [keep,'IntegratedContactUV']:ob.data.uv_layers.remove(layer)
    assert len(ob.data.uv_layers)==2
    assert ob.data.uv_layers[1].name=='IntegratedContactUV'
    ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
bpy.data.libraries.write(str(A/'integrated_coastal_mass.blend'),{col},path_remap='ABSOLUTE',fake_user=True,compress=True)
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
exec(compile((R/'tools/blender/verify_coastal_integration.py').read_text(encoding='utf8'),'verify_coastal_integration.py','exec'))
