import bpy,json
from mathutils import Vector
scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-reference-polish-2'
for ob in scene.objects:
    if ob.type!='MESH':continue
    if 'Bamboo_Leaf_Cluster' in ob.name:
        for p in ob.data.polygons:p.use_smooth=True
        c=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
        ns=[]
        for loop in ob.data.loops:
            q=ob.data.vertices[loop.vertex_index].co-c
            ns.append(tuple(Vector((q.x*.8,q.y*1.8-.20,q.z*2.4+.36)).normalized()))
        ob.data.normals_split_custom_set(ns)
    if 'Grass_Patch_Blades' in ob.name:
        for p in ob.data.polygons:p.use_smooth=True
        ob.data.normals_split_custom_set([(0,0,1)]*len(ob.data.loops))
print(json.dumps({'smoothed_cluster_normals':True,'revision':scene['revision']}))
