import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.scenes['Layered_Island_20261116'].objects['Land_Relief']
t=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
rows=[]
for x in [-16,-14.5,-13,-11.5,-10,-8.5,-7,-5.5,-4]:
    for y in [8.0,9.5,11.0,12.5]:
        hit=t.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
        if hit[0] is not None:rows.append([x,y,round(hit[0].z,2)])
print(json.dumps(rows))
