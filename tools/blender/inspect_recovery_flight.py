import bpy,json
from mathutils import Vector
from pathlib import Path
s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];o=s.objects['Recovery_WALK_Cape_Stairs'];a=Vector((-62.5,4,.15));u=Vector((-.8,4.8,0)).normalized();v=Vector((u.y,-u.x,0));groups={}
for f in o.data.polygons:
 if f.normal.z>.9:
  p=o.matrix_world@f.center;groups.setdefault(round(p.z,3),[]).append([round((p-a).dot(u),3),round((p-a).dot(v),3)])
print(json.dumps(groups))
