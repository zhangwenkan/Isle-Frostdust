"""Save only this newly authored scene and dependencies; Blender MCP."""
import bpy,json,os
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Pixel_Cavern_Coast']
assert scene['revision']=='pixel-cavern-review-7'
path=root/'assets/pixel_cavern_coast/pixel_cavern_coast.blend'
temporary=path.with_name('pixel_cavern_isolation_check.blend')
bpy.data.libraries.write(str(temporary),{scene},fake_user=True,compress=True)
with bpy.data.libraries.load(str(temporary),link=False) as (data_from,data_to):
    scenes=list(data_from.scenes)
os.replace(temporary,path)
result={'saved_scenes':scenes,'only_new_scene':scenes==['Pixel_Cavern_Coast'],'source_bytes':path.stat().st_size}
(root/'artifacts/pixel-cavern-coast-review/source-isolation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert result['only_new_scene']
print(json.dumps(result))
