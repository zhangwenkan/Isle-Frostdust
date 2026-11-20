"""Fix visible sample defects inside the fresh scene through Blender MCP."""
import bpy,json
from pathlib import Path

root=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Fresh_Pixel_Cape']
bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-color-study-3'

# Keep the lower apron beneath the final tread and the side rock beneath
# the penultimate tread. These are newly authored objects from this sample.
for name,cap in [('Lower_Stair_Rock_Apron',.14),('Fresh_Lower_Stair_Side',.40)]:
    ob=bpy.data.objects[name]
    for v in ob.data.vertices:
        v.co.z=min(v.co.z,cap)

# Extend the authored preview sea so its far polygon edge is out of frame.
sea=bpy.data.objects['Sea_Surface']
for v in sea.data.vertices:
    v.co.x*=4
    v.co.y*=4

# Constant-color accents still receive simple editable UV coordinates.
for ob in scene.objects:
    if ob.type=='MESH' and not ob.data.uv_layers:
        uv=ob.data.uv_layers.new(name='UVMap')
        for i,loop in enumerate(ob.data.loops):
            p=ob.data.vertices[loop.vertex_index].co
            uv.data[i].uv=(p.x*.25,p.z*.25+p.y*.15)

scene['revision']='fresh-cape-color-study-4'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'source_scene':scene.name}))
