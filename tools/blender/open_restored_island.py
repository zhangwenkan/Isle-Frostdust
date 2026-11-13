"""Through Blender MCP: reload the user's restored source and verify marker removal."""
import bpy, json
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
target=ROOT/'assets/island_blender/nameless_island.blend'
if Path(bpy.data.filepath).resolve()!=target.resolve() or any(ob.name.startswith('Wuxia_Tingchao') for ob in bpy.data.objects):
    bpy.ops.wm.open_mainfile(filepath=str(target))
scene=bpy.data.scenes['Island_Refined']
# open_mainfile invalidates the callback's previous window context.
for manager in bpy.data.window_managers:
    for window in manager.windows:
        window.scene=scene
markers=[ob.name for ob in bpy.data.objects if ob.name.startswith('Wuxia_Tingchao')]
assert not markers, markers
assert 'Open_Sea' in scene.objects
report={'file':bpy.data.filepath,'scene':scene.name,'marker_objects':markers,
        'scene_objects':len(scene.objects),'ocean_dimensions_blender':list(scene.objects['Open_Sea'].dimensions)}
(ROOT/'artifacts/wuxia-style-review/rollback/blender-restored.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('WUXIA_ROLLBACK_BLENDER_OK',json.dumps(report))
