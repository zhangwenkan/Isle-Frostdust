"""Fix winding of a disposable reconstruction input, never the reference."""
import bpy,bmesh,json
s=bpy.data.scenes['Tripo_Reference_Reconstruction_20261119'];bpy.context.window.scene=s;o=s.objects['Replica_Coast_Quad_Control']
assert len(o.data.polygons)==49746
bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table()
signs={};conflicts=set()
def direction(f,e):
    l=next(l for l in f.loops if l.edge==e)
    return 1 if l.vert==e.verts[0] else -1
for root in bm.faces:
    if root in signs:continue
    signs[root]=1;todo=[root]
    while todo:
        f=todo.pop()
        for e in f.edges:
            if not e.is_manifold:continue
            q=e.link_faces[1] if e.link_faces[0]==f else e.link_faces[0]
            expected=-signs[f]*direction(f,e)*direction(q,e)
            if q not in signs:signs[q]=expected;todo.append(q)
            elif signs[q]!=expected:conflicts.add(e)
for f,sgn in signs.items():
    if sgn<0:f.normal_flip()
bm.normal_update()
print('Orientability conflicts:',len(conflicts),'remaining winding conflicts:',sum(e.is_manifold and not e.is_contiguous for e in bm.edges))
if conflicts:
    # A non-orientable coincident join is cut only in the disposable input.
    # Coordinates and silhouette are unchanged; surface patches remain.
    bmesh.ops.split_edges(bm,edges=list(conflicts),use_verts=False)
    bm.normal_update()
print('After surface join repair:',sum(e.is_manifold and not e.is_contiguous for e in bm.edges))
bm.to_mesh(o.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
print('Surface retopology:',bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=False,use_preserve_sharp=True,use_preserve_boundary=True,preserve_attributes=False,smooth_normals=True,mode='FACES',target_faces=11000,seed=0))
print('Faces',len(o.data.polygons),'quads',sum(len(p.vertices)==4 for p in o.data.polygons))
