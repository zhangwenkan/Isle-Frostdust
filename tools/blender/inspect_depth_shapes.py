import bpy,json
from mathutils import Vector
from pathlib import Path
data=[]
for ob in bpy.data.scenes['Island_Refined'].objects:
    if ob.name.startswith(('Fish_Ground_Rock','Fish_Tidal_Reef')):
        data.append({'name':ob.name,'dimensions':list(ob.dimensions),'materials':[m.name for m in ob.data.materials]})
print(json.dumps(data))
