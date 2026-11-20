import bpy,bmesh,json
s=bpy.data.scenes['Tripo_Reference_Reconstruction_20261119'];o=s.objects['Replica_Coast_Quad_Control']
bm=bmesh.new();bm.from_mesh(o.data)
print(json.dumps({'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'quads':sum(len(p.vertices)==4 for p in o.data.polygons),
 'nonmanifold':sum(not e.is_manifold for e in bm.edges),'revision':s['revision'],'is_job_running':bpy.app.is_job_running('OBJECT_BAKE')}))
bm.free()
