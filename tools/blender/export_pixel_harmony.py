"""Batch shadow casters and export the authored sample through Blender MCP."""
import bpy,json
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Pixel_Cavern_Coast'];bpy.context.window.scene=scene
assert scene['revision'] in ('pixel-cavern-vegetation-harmony-9','pixel-cavern-vegetation-harmony-10','pixel-cavern-vegetation-harmony-11')
groups={}
for o in list(scene.objects):
    if not o.get('pixel_cavern') or not o.name.startswith('Shadow_'):continue
    parts=o.name.split('_')
    key=('Shadow_BambooMass_'+parts[3]) if o.name.startswith(('Shadow_BambooMass_Leaves_','Shadow_BambooMass_Spray_')) else '_'.join(parts[:4])
    groups.setdefault(key,[]).append(o)
for name,items in groups.items():
    if len(items)>1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in items:o.hide_set(False);o.select_set(True)
        bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join()
    items[0].name=name
objects=[o for o in scene.objects if o.type=='MESH' and o.get('pixel_cavern')]
weighted=[o for o in objects if o.get('wind_data_layout')]
missing=[o.name for o in weighted if len(o.data.uv_layers)<2 or not o.data.color_attributes]
assert not missing,missing
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
out=root/'assets/pixel_cavern_coast'
bpy.data.libraries.write(str(out/'pixel_cavern_coast.blend'),{scene},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(out/'pixel_cavern_coast.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_normals=True,export_texcoords=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=False)
data={'revision':scene['revision'],'objects':len(objects),'weighted_meshes':len(weighted),'shadow_meshes':len(groups),'missing_weights':missing,'source':'Blender MCP, current new sample only'}
(out/'design.json').write_text(json.dumps(data,indent=2),encoding='utf-8');(root/'artifacts/pixel-vegetation-harmony-review/export-check.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps(data))
