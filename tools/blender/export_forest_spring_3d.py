import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/forest_spring_3d'
bpy.context.window.scene=bpy.data.scenes['Forest_Spring_Volumetric']
bpy.ops.object.select_all(action='DESELECT')
col=bpy.data.collections['40_Forest_Spring_3D']
for ob in col.objects:ob.select_set(True)
bpy.data.libraries.write(str(A/'forest_spring.blend'),{bpy.context.scene},path_remap='ABSOLUTE',fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'forest_spring.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_extras=True)
print('EXPORTED_ONLY',bpy.context.scene.name,len(col.objects))
