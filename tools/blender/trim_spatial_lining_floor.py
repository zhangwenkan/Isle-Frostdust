"""Remove the redundant underside which was showing through the old cave landing."""
import bpy,bmesh
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');out=root/'assets/layered_island'
scene=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=scene
ob=scene.objects['Space_Cave_Lining'];bm=bmesh.new();bm.from_mesh(ob.data)
floors=[f for f in bm.faces if abs(f.normal.z)>.98 and f.calc_center_median().z<3.0]
assert len(floors)==1,len(floors)
bmesh.ops.delete(bm,geom=floors,context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update()
bpy.data.libraries.write(str(out/'layered_island.blend'),{scene},fake_user=True,compress=True)
live=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
bpy.ops.object.select_all(action='DESELECT')
for o in live:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(out/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
print('Removed redundant cave lining floor; walk surfaces retained')
