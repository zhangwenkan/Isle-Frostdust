import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘')
print('FILE',bpy.data.filepath)
assert Path(bpy.data.filepath)==R/'assets/island_blender/nameless_island.blend'
scene=bpy.data.scenes['Island_Refined']
for name in ['Depth_Bamboo_Main_07','Depth_Bamboo_Main_08','InkSample_Bamboo_03']:
    o=scene.objects[name]
    print('OBJECT',name,len(o.data.vertices),dict(o.items()),'MATS',[(m.name,[(n.name,n.type) for n in m.node_tree.nodes]) for m in o.data.materials],'COLORS',[(c.name,c.domain) for c in o.data.color_attributes])
print('RENDER_ENGINES',scene.render.engine)
print('CYCLES_DEVICES',[(d.name,d.type) for d in bpy.context.preferences.addons['cycles'].preferences.devices])
