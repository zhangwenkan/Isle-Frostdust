import bpy,json
from mathutils import Vector
names=['Open_Sea','Fish_West_Continuous_Land','Fish_East_Continuous_Land']
for ob in bpy.context.scene.objects:
 if ob.name in names or any(s in ob.name.lower() for s in ['seabed','sea_floor','underwater','shallow']):
  pts=[ob.matrix_world@Vector(c) for c in ob.bound_box];print(ob.name,[(round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)) for i in range(3)])
