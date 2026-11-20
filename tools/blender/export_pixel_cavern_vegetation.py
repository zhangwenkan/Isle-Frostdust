"""Export and inspect completed living plants through Blender MCP."""
import bpy,json
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');out=root/'assets/pixel_cavern_coast'
scene=bpy.data.scenes['Pixel_Cavern_Coast'];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-living-vegetation-8'
objects=[o for o in scene.objects if o.type=='MESH' and o.get('pixel_cavern')]
live=[o for o in objects if o.name.startswith(('Live','Bamboo_Stem','Bamboo_Branches','Plant_Fern','Plant_Edge_Shrub','Plant_Foreground','Plant_Cliff_Creeper'))]
missing=[o.name for o in live if len(o.data.uv_layers)<2 or not o.data.color_attributes]
assert not missing,missing
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.gltf(filepath=str(out/'pixel_cavern_coast.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_normals=True,export_texcoords=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False)
bpy.data.libraries.write(str(out/'pixel_cavern_coast.blend'),{scene},fake_user=True,compress=True)
data={'revision':scene['revision'],'objects':len(objects),'weighted_meshes':len(live),'missing_weights':missing,'source':'Blender MCP, new sample only','imported_geometry':[]}
(out/'design.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
(root/'artifacts/pixel-vegetation-review/export-check.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data))
