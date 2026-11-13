"""Blend shading normals slightly, keeping all accepted rock vertex positions/UVs."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');REVIEW_DIR=ROOT/'artifacts/rock-wash-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
archive=bpy.data.collections.get('90_Before_Rock_Wash_Normals') or bpy.data.collections.new('90_Before_Rock_Wash_Normals')
if archive.name not in scene.collection.children:scene.collection.children.link(archive)
reports=[]
for index in [0,2,3,4]:
    ob=scene.objects['InkSample_Rock_%02d'%index]
    savedname='HardNormalBaseline_'+ob.name
    saved=bpy.data.objects.get(savedname)
    if saved is None:
        saved=ob.copy();saved.data=ob.data.copy();saved.name=savedname
        archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    ob.data=saved.data.copy();me=ob.data
    positions=[tuple(v.co) for v in me.vertices]
    uv_before=[[tuple(d.uv) for d in layer.data] for layer in me.uv_layers]
    average=[Vector((0,0,0)) for v in me.vertices]
    for p in me.polygons:
        for vi in p.vertices:average[vi]+=p.normal
    average=[n.normalized() for n in average]
    normals=[None]*len(me.loops)
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            vi=me.loops[li].vertex_index
            # Partial blending keeps the original angular silhouette while
            # broad painted light crosses the original plane boundaries.
            normals[li]=tuple(p.normal.lerp(average[vi],.55).normalized())
    me.normals_split_custom_set(normals);me.update()
    assert positions==[tuple(v.co) for v in me.vertices]
    assert uv_before==[[tuple(d.uv) for d in layer.data] for layer in me.uv_layers]
    reports.append({'object':ob.name,'custom_normal_blend':.55,'positions_uv_unchanged':True,'vertices':len(me.vertices)})
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
(REVIEW_DIR/'normal-authoring.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print('ROCK_WASH_NORMALS_EXPORTED; accepted positions and UVs retained')
