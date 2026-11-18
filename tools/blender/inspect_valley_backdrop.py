"""Read current forest dimensions through the live Blender MCP connection."""
import bpy,json
from mathutils import Vector
scene=bpy.data.scenes.get('Layered_Island_20261116')
assert scene is not None
names=['WALK_Forest_Ground','Forest_Back_Ground','Forest_Bamboo_33','Forest_Bamboo_Canopy_33','Forest_Bamboo_DeepRow_1_2_0','Forest_Bamboo_DeepRow_1_2_1']
rows=[]
for name in names:
    ob=scene.objects[name]
    pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    rows.append({'name':name,'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)],'vertices':len(ob.data.vertices),'materials':[m.name for m in ob.data.materials]})
print(json.dumps({'file':bpy.data.filepath,'scene':scene.name,'collections':[c.name for c in bpy.data.collections if c.name.startswith(('43_','44_'))],'objects':rows}))
