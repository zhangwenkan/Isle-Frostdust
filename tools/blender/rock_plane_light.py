"""Restore broad readable plane normals and clean pigment inside Blender MCP."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');REVIEW_DIR=ROOT/'artifacts/rock-plane-light-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
mat=bpy.data.materials['InkSample_Rock_Angular']
tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(ROOT/'assets/colored_ink_sample/rock_plane_values.png'),check_existing=True);tex.image.reload()
reports=[]
for index in [0,2,3,4]:
    ob=scene.objects['InkSample_Rock_%02d'%index]
    baseline=bpy.data.objects['HardNormalBaseline_'+ob.name]
    before_positions=[tuple(v.co) for v in ob.data.vertices]
    before_uv=[[tuple(d.uv) for d in l.data] for l in ob.data.uv_layers]
    ob.data=baseline.data.copy();me=ob.data
    average=[Vector((0,0,0)) for v in me.vertices]
    for p in me.polygons:
        for vi in p.vertices:average[vi]+=p.normal
    average=[n.normalized() for n in average]
    normals=[None]*len(me.loops)
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            vi=me.loops[li].vertex_index
            normals[li]=tuple(p.normal.lerp(average[vi],.16).normalized())
    me.normals_split_custom_set(normals);me.update()
    assert before_positions==[tuple(v.co) for v in me.vertices]
    assert before_uv==[[tuple(d.uv) for d in l.data] for l in me.uv_layers]
    reports.append({'object':ob.name,'normal_blend':.16,'positions_uv_unchanged':True,'vertices':len(me.vertices)})
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['revision']='Clean western rock planes: shared pigment, restrained plane lighting, selected pale edge accents; rejected scratches removed'
ref='../../artifacts/rock-plane-light-review/README.md'
if ref not in m['source_manifests']:m['source_manifests'].append(ref)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(REVIEW_DIR/'blender-authoring.json').write_text(json.dumps({'rocks':reports,'texture':tex.image.filepath,'geometry_preserved':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('ROCK_PLANE_LIGHT_EXPORTED')
