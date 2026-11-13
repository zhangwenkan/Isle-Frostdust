"""Through Blender MCP: preserve the open scene before the requested rollback."""
import bpy, json
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
out=ROOT/'artifacts/wuxia-style-review/rollback'
report={'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,
        'marker_objects':[ob.name for ob in bpy.data.objects if ob.name.startswith('Wuxia_Tingchao')]}
bpy.ops.wm.save_as_mainfile(filepath=str(out/'rejected-state/open-scene.blend'),copy=True)
(out/'snapshot.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('WUXIA_ROLLBACK_SNAPSHOT_OK',json.dumps(report))
