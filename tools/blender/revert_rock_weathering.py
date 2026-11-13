"""Restore the accepted rock meshes through Blender MCP after rejected weathering."""
import bpy, json
from pathlib import Path

ROOT = Path('D:/自己做着玩的/孤屿霜尘')
REVIEW = ROOT / 'artifacts/rock-weathering-review'
assert Path(bpy.data.filepath).resolve() == (ROOT / 'assets/island_blender/nameless_island.blend').resolve()
scene = bpy.data.scenes['Island_Refined']
bpy.context.window.scene = scene
names = ['InkSample_Rock_%02d' % i for i in [0, 2, 3, 4]]
assert all('PlaneBaseline_' + name in bpy.data.objects for name in names)
archive = bpy.data.collections.get('90_Rejected_Rock_Weathering') or bpy.data.collections.new('90_Rejected_Rock_Weathering')
if archive.name not in scene.collection.children:
    scene.collection.children.link(archive)
reports = []
for name in names:
    ob = scene.objects[name]
    baseline = bpy.data.objects['PlaneBaseline_' + name]
    saved_name = 'RejectedWeathering_' + name
    if saved_name not in bpy.data.objects:
        rejected = ob.copy()
        rejected.data = ob.data.copy()
        rejected.name = saved_name
        archive.objects.link(rejected)
        rejected.hide_set(True)
        rejected.hide_render = True
    ob.data = baseline.data.copy()
    for key in list(ob.keys()):
        del ob[key]
    for key in baseline.keys():
        ob[key] = baseline[key]
    reports.append({'object': name, 'vertices': len(ob.data.vertices), 'faces': len(ob.data.polygons),
                    'restored_from': baseline.name})
# Keep the quiet pigment without painted pale edge accents. Mesh, UV and
# normals are restored exactly; this pass does not claim to fix hard lighting.
mat = bpy.data.materials['InkSample_Rock_Angular']
tex = next(n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE')
tex.image = bpy.data.images.load(str(ROOT / 'assets/colored_ink_sample/rock_weathered_base.png'), check_existing=True)
tex.image.reload()
exec(compile((ROOT / 'tools/blender/fish_export.py').read_text(encoding='utf-8'), 'fish_export.py', 'exec'))
p = ROOT / 'assets/island_blender/asset_manifest.json'
m = json.loads(p.read_text(encoding='utf-8'))
m['revision'] = 'Rejected localized weathering removed; previous four rock meshes restored exactly, pale painted edges remain removed. Hard plane transitions unresolved.'
p.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf-8')
(REVIEW / 'rollback-authoring.json').write_text(json.dumps({'rocks': reports, 'hard_boundary_issue_resolved': False}, ensure_ascii=False, indent=2), encoding='utf-8')
print('ROCK_WEATHERING_REVERTED')
