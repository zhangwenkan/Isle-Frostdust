"""Read back delivered GLB in isolated scene through MCP."""
import bpy,json
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');author=bpy.data.scenes['Pixel_Cavern_Coast']
audit=bpy.data.scenes.new('PCC_Harmony_Export_Check');bpy.context.window.scene=audit
bpy.ops.import_scene.gltf(filepath=str(root/'assets/pixel_cavern_coast/pixel_cavern_coast.glb'))
objects=[o for o in audit.objects if o.type=='MESH'];living=[o for o in objects if o.name.startswith('Live')]
for ob in objects:ob.data.calc_loop_triangles()
result={'meshes':len(objects),'triangles':sum(len(o.data.loop_triangles) for o in objects),'live_meshes':len(living),'missing_uv2':[o.name for o in living if len(o.data.uv_layers)<2],'missing_color':[o.name for o in living if not o.data.color_attributes],'archived_exported':[o.name for o in objects if o.name.startswith(('Foliage_Tree_','Plant_Vine_Leaves_','Shadow_Foliage_','Plant_Grass_Patch_'))]}
assert not result['missing_uv2'] and not result['missing_color'] and not result['archived_exported']
(root/'artifacts/pixel-vegetation-harmony-review/reimport-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for ob in list(audit.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.window.scene=author;bpy.data.scenes.remove(audit)
print(json.dumps(result))

