"""Keep world pivots in float UVs; GPU vertex colors are only 8-bit."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Pixel_Cavern_Coast'];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-living-vegetation-8'
count=0
for ob in scene.objects:
    if ob.type!='MESH' or not ob.get('pixel_cavern'):continue
    if ob.get('wind_data_layout')=='uv_xz_uv2_y_weight_color_leaf_phase':continue
    me=ob.data
    if len(me.uv_layers)<2 or not me.color_attributes:continue
    colors=me.color_attributes.get('WindPivot')
    if not colors:continue
    pivots=[Vector(c.color[:3])*64-Vector((32,32,32)) for c in colors.data]
    local=[c.color[3] for c in colors.data];phases=[0]*len(me.vertices)
    wind=me.uv_layers.get('Wind');uv0=me.uv_layers[0]
    for loop in me.loops:
        i=loop.vertex_index;weight,phase=wind.data[loop.index].uv[:];p=pivots[i]
        uv0.data[loop.index].uv=(p.x,1-p.z)
        wind.data[loop.index].uv=(p.y,1-weight);phases[i]=phase
    for i,c in enumerate(colors.data):c.color=(local[i],phases[i],0,1)
    ob['wind_data_layout']='uv_xz_uv2_y_weight_color_leaf_phase';count+=1
bpy.data.libraries.write(str(root/'assets/pixel_cavern_coast/pixel_cavern_coast.blend'),{scene},fake_user=True,compress=True)
print(json.dumps({'precision_pivots':count,'layout':'UV=root.xz UV2=root.y,weight COLOR.rg=tip,phase'}))
