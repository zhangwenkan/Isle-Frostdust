"""Re-import only the new GLB in isolated verification scene via Blender MCP."""
import bpy,json
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');source=bpy.context.scene
assert source.name=='Fresh_Pixel_Cape'
audit=bpy.data.scenes.new('Fresh_Export_Audit');bpy.context.window.scene=audit
bpy.ops.import_scene.gltf(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.glb'))
meshes=[o for o in audit.objects if o.type=='MESH']
result={'source_scene':source.name,'revision':source['revision'],'reimported_meshes':len(meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),'materials':sorted(set(m.name for o in meshes for m in o.data.materials)),'missing_uv':[o.name for o in meshes if not o.data.uv_layers and 'Overlay' not in o.name],'foreign_objects':[o.name for o in audit.objects if o.name in ['Cube','Camera','Light']]}
for o in meshes:o.data.calc_loop_triangles()
result['triangles']=sum(len(o.data.loop_triangles) for o in meshes)
(root/'artifacts/cape-stone-steps-clarity-review/reimport-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for o in list(audit.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.window.scene=source;bpy.data.scenes.remove(audit)
print(json.dumps(result,ensure_ascii=False))
