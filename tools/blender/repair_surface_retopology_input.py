import bpy,bmesh,json
s=bpy.data.scenes['Tripo_Reference_Reconstruction_20261119'];bpy.context.window.scene=s;o=s.objects['Replica_Coast_Quad_Control']
assert s['revision']=='reference-constrained-reconstruction-1' and len(o.data.polygons)==49746
bm=bmesh.new();bm.from_mesh(o.data)
bad=[f for f in bm.faces if f.calc_area()<1e-12]
print('Zero-area faces:',len(bad))
if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
bmesh.ops.dissolve_degenerate(bm,dist=.0000001,edges=list(bm.edges))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
print(json.dumps({'faces':len(bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'normal_conflicts':sum(e.is_manifold and not e.is_contiguous for e in bm.edges)}))
bm.to_mesh(o.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
print('QuadriFlow:',bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=False,use_preserve_sharp=False,use_preserve_boundary=False,preserve_attributes=False,smooth_normals=True,mode='FACES',target_faces=11000,seed=0))
print('Result faces:',len(o.data.polygons),'quads:',sum(len(p.vertices)==4 for p in o.data.polygons))
