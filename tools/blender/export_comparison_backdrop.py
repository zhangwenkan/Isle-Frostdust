"""Blender MCP: export only the existing ink mountain comparison layer."""
import bpy,json
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
out=ROOT/'assets/background_comparison';out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
objects=list(bpy.data.collections['30_Sumiro_Ink_Hills'].objects)
assert len(objects)==14
for ob in objects:ob.hide_set(False);ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'ink_mountains.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
(out/'source.json').write_text(json.dumps({'source':'Sumiro adapted hill layer, Blender MCP export','source_blend':'../../artifacts/background-comparison-review/rejected-full-ink/assets/island_blender/nameless_island.blend','objects':[o.name for o in objects],'provenance':'../sumiro/PROVENANCE.md'},indent=2),encoding='utf8')
print('COMPARISON_BACKDROP_EXPORTED',len(objects))
