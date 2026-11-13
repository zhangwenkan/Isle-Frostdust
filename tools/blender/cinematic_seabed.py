import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ob=bpy.data.objects['Fish_Seabed']; tree=BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get())
for x in [5.5,7.0,8.5,10,11.5,13]:
 print(x,[(z,round(tree.ray_cast(Vector((x,-z,5)),Vector((0,0,-1)))[0].z,2)) for z in [-3,0,2,4,6]])
