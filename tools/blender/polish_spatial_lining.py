import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘');out=root/'assets/layered_island'
scene=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=scene
o=scene.objects['Space_Cave_Lining'];center=Vector((10.574,1.519,2.96))
arch=[(-1.6,-.55),(-1.7,1.85),(-1.25,3.25),(-.35,3.8),(.65,3.65),(1.65,2.2),(1.65,-.55)]
for j,depth in enumerate([1.55,4.1]):
    for i,(x,z) in enumerate(arch):o.data.vertices[j*7+i].co=center+Vector((x,depth,z))
o.data.update()
for im in bpy.data.images:
    if im.source=='FILE' and '/spatial_textures/' in im.filepath.replace('\\','/'):
        im.reload();im.pack()
live=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
bpy.data.libraries.write(str(out/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in live:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=scene.objects['Space_Continuous_Cliff']
bpy.ops.export_scene.gltf(filepath=str(out/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
print('Tunnel lining moved behind the entrance; surface brush contrast restored')
