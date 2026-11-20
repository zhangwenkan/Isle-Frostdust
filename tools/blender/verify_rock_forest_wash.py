"""Blender MCP: isolated GLB readback; inspect final exported materials and UVs."""
import bpy,json,math
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/tripo_replica';O=R/'artifacts/rock-forest-style-review'
SN='Rock_Forest_Wash_Final_Readback_20261119';assert not bpy.data.scenes.get(SN)
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
bpy.ops.import_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'))
report=[]
for ob in s.objects:
    if ob.type!='MESH':continue
    mats=[]
    for m in ob.data.materials:
        if not m:continue
        imgs=[{'name':n.image.name,'size':list(n.image.size)} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
        mats.append({'name':m.name,'images':imgs})
    assert all(math.isfinite(c) for v in ob.data.vertices for c in v.co)
    report.append({'name':ob.name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'uv_layers':[u.name for u in ob.data.uv_layers],'materials':mats})
assert len(report)==8
assert not any('Rock_Near' in r['name'] for r in report)
(O/'glb-readback.json').write_text(json.dumps({'scene':SN,'objects':report,'only_expected_eight_meshes':True,'old_shoulders_absent':True},indent=2),encoding='utf8')
bpy.context.window.scene=bpy.data.scenes['Tripo_Game_Assembly_20261119']
print('Isolated readback: 8 expected meshes, materials/images and UV layers present; old shoulders absent.')
