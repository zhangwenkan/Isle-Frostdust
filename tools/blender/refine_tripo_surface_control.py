"""Clean the disposable shell, make new control topology, fit measured detail.
All bpy operations run in the connected Blender via MCP. Reference-dependent.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Surface_Measurement_Rebuild_20261119'];old=bpy.context.window.scene;bpy.context.window.scene=s
assert s['revision']=='thick-surface-new-topology-1','Inspect completed fitted reconstruction.'
ref=bpy.data.scenes['Tripo_Coast_Processing_20261119'].objects['Tripo_Coast_Original_Surface']
bm=bmesh.new();bm.from_mesh(ref.data);tree=BVHTree.FromBMesh(bm);bm.free()
o=s.objects['Replica_Surface_Control']
bm=bmesh.new();bm.from_mesh(o.data)
bad=[]
for v in bm.verts:
    h,n,i,d=tree.find_nearest(v.co)
    if h is None or d>.013:bad.append(v)
bmesh.ops.delete(bm,geom=bad,context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
dec=o.modifiers.new('Reconstructed control topology reduction','DECIMATE');dec.ratio=.026;dec.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier=dec.name)
control_faces=len(o.data.polygons);control_vertices=len(o.data.vertices)
mr=o.modifiers.new('Reference-measured editable sculpt detail','MULTIRES')
for _ in range(2):bpy.ops.object.multires_subdivide(modifier=mr.name,mode='SIMPLE')
mr.levels=2;mr.sculpt_levels=2;mr.render_levels=2
dg=bpy.context.evaluated_depsgraph_get();high=bpy.data.objects.new('TEMP_detail_measurement',bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg));s.collection.objects.link(high)
dist=[]
for v in high.data.vertices:
    h,n,i,d=tree.find_nearest(v.co)
    if h is not None:v.co=h;dist.append(d)
high.data.update();high.select_set(True);o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.multires_reshape(modifier=mr.name);bpy.data.objects.remove(high,do_unlink=True)
for p in o.data.polygons:p.use_smooth=True
o['method']='New thickened-shell voxel topology, collapsed control topology, and measured multires shape.'
o['reference_dependent']=True;o['source_faces_uv_texture_reused']=False
s['revision']='new-control-measured-detail-2'
cam=s.camera;target=Vector((0,0,.21))
for angle in [0,35]:
    a=math.radians(angle);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(O/('control-replica-gray-%s.png'%angle));bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(A/'tripo_surface_measurement_replica.blend'),{s},fake_user=True,compress=True)
report={'scene':s.name,'revision':s['revision'],'control_faces':control_faces,'control_vertices':control_vertices,
 'removed_spike_vertices':len(bad),'detail_samples':len(dist),'fitting_distance_max':max(dist),'fitting_distance_mean':sum(dist)/len(dist),
 'method':o['method'],'source_faces_uv_texture_reused':False,'independent_sculpting_demonstrated':False,
 'status':'Actual static replica, pending visual inspection and user evaluation. Not an approved workflow.'}
(O/'control-reconstruction-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old;print(json.dumps(report,ensure_ascii=False))
