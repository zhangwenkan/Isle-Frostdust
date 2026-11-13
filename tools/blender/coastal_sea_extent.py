"""Run only through Blender MCP: extend the existing authored sea surface."""
import bpy, json
from pathlib import Path
ROOT = Path('D:/自己做着玩的/孤屿霜尘')
assert Path(bpy.data.filepath).resolve() == (ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene = bpy.data.scenes['Island_Refined']
bpy.context.window.scene = scene
sea = scene.objects['Open_Sea']
before = [(min(v.co[i] for v in sea.data.vertices), max(v.co[i] for v in sea.data.vertices)) for i in range(3)]
for v in sea.data.vertices:
    for axis in (0, 1):
        low, high = before[axis]
        v.co[axis] = -2400 + (v.co[axis]-low)/(high-low)*4800
sea.data.update()
sea['authoring_note'] = 'Existing ocean surface extended in Blender for a continuous atmospheric horizon; wave detail is shading.'
(ROOT/'artifacts/water-light-review/sea-authoring.json').write_text(json.dumps({'before_bounds_blender':before, 'after_xy':[-2400,2400], 'vertices':len(sea.data.vertices)}),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'), 'fish_export.py', 'exec'))
manifest_path = ROOT/'assets/island_blender/asset_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['revision'] = 'Palm coast preserved; Blender ocean extent enlarged for continuous horizon'
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('COASTAL_SEA_EXTENT_COMPLETE')
