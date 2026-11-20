"""Replace failed voxel study with surface QuadriFlow reconstruction via MCP.
Reference-guided reconstruction is recorded accurately, not independent sculpt.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/tripo-replica-review';ASSET=ROOT/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Reference_Reconstruction_20261119'];old=bpy.context.window.scene;bpy.context.window.scene=s
assert s['revision']=='reference-constrained-reconstruction-1','Inspect current completed revision.'
failed=s.objects['Replica_Coast_Control_Surface'];archive=bpy.data.collections.new('90_Failed_Voxel_Reconstruction');s.collection.children.link(archive)
for c in list(failed.users_collection):c.objects.unlink(failed)
archive.objects.link(failed);failed.hide_render=True;failed.hide_set(True)
ref=s.objects['REFERENCE_Tripo_Surface_Not_Exported']
author=bpy.data.collections['Tripo_Replica_Authored']
o=bpy.data.objects.new('Replica_Coast_Quad_Control',ref.data.copy());author.objects.link(o)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000002)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=False,use_preserve_sharp=True,use_preserve_boundary=True,
 preserve_attributes=False,smooth_normals=True,mode='FACES',target_faces=11000,seed=0)
assert len(o.data.polygons)!=len(ref.data.polygons) and sum(len(p.vertices)==4 for p in o.data.polygons)>.85*len(o.data.polygons), 'Surface retopology failed; do not call unchanged import a replica.'
for uv in list(o.data.uv_layers):o.data.uv_layers.remove(uv)
o.data.materials.clear();o.data.materials.append(bpy.data.materials['Replica_Neutral_Clay'])
for p in o.data.polygons:p.use_smooth=True;p.material_index=0
control_faces=len(o.data.polygons);control_vertices=len(o.data.vertices)
mr=o.modifiers.new('Reference reconstructed surface detail','MULTIRES')
bpy.ops.object.multires_subdivide(modifier=mr.name,mode='SIMPLE');bpy.ops.object.multires_subdivide(modifier=mr.name,mode='SIMPLE')
mr.levels=2;mr.sculpt_levels=2;mr.render_levels=2
dg=bpy.context.evaluated_depsgraph_get();high=bpy.data.objects.new('Temporary_Surface_Samples',bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg));author.objects.link(high)
bm=bmesh.new();bm.from_mesh(ref.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000002);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));tree=BVHTree.FromBMesh(bm);bm.free()
dist=[]
for v in high.data.vertices:
    hit,n,index,d=tree.find_nearest(v.co)
    if hit is not None:v.co=hit;dist.append(d)
high.data.update();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);high.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.multires_reshape(modifier=mr.name);bpy.data.objects.remove(high,do_unlink=True)
o['method']='Surface QuadriFlow control topology, simple subdivision and reference-sampled multires shape.'
o['source_geometry_measurement']=True;o['original_texture_or_uv_reused']=False
s['revision']='surface-quad-reference-reconstruction-2'
refview=s.objects['Review_Tripo_Gray_Only'];refview.hide_render=True
cam=s.camera;center=Vector((0,0,.21))
for angle in [0,35]:
    a=math.radians(angle);cam.location=center+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(OUT/('surface-replica-gray-'+str(angle)+'.png'));bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(ASSET/'tripo_reference_replica.blend'),{s},fake_user=True,compress=True)
report={'scene':s.name,'revision':s['revision'],'method':o['method'],'control_vertices':control_vertices,
 'control_faces':control_faces,'sculpt_detail_levels':2,'fitted_samples':len(dist),'mean_sample_fitting_distance':sum(dist)/len(dist),
 'original_face_topology_or_uv_reused':False,'original_texture_reused':False,
 'scope':'New surface control topology and detail sample, constrained by the supplied Tripo mesh. Main game unchanged.',
 'limitations':['This is reference-guided retopology and surface reconstruction, not proof of independent from-scratch geological sculpting.',
 'Static fire/log components and reference back defects remain in this faithful comparison.'],
 'status':'Pending visual comparison and user evaluation. General workflow not established.'}
(OUT/'surface-reconstruction-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old;print(json.dumps(report,ensure_ascii=False))
