import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
scene.objects['Fish_Underwater_Swimmer_00'].location=Vector((6.4,-1.6,-2.92))
scene.objects['Fish_Underwater_Swimmer_03'].location.z=-2.8
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';m=json.loads(p.read_text());m['revision']='Layered multi-crown distant ridges and bridge underwater life'
review='../../artifacts/cinematic-coast-review/README.md'
if review not in m.setdefault('source_manifests',[]):m['source_manifests'].append(review)
p.write_text(json.dumps(m,indent=2),encoding='utf-8')
