import bpy,json
from pathlib import Path
s=bpy.data.scenes['Island_Refined'];o=s.objects['Fish_West_Continuous_Land']
boundary=[i*26 for i in range(101)]+[2600+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
print('BOUNDARY',json.dumps([(i,tuple(o.matrix_world@o.data.vertices[boundary[i]].co)) for i in range(0,250,10)]))
print('LAND',len(o.data.vertices),len(o.data.polygons),[(m.name) for m in o.data.materials],[u.name for u in o.data.uv_layers])
print('ROCKS',json.dumps([(o.name,len(o.data.vertices),list(o.dimensions)) for o in s.objects if o.name.startswith('Original_Coast_Rock_')]))
