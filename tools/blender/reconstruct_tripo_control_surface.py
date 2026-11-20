"""Reference-constrained topology reconstruction, executed in Blender via MCP.

This is NOT independent from-reference-free sculpting. The Tripo surface is
used for volume measurement and fitting. Output has a newly reconstructed
control topology and stored multires detail, never the original face/UV data.
Do not promote this alone to a general independent rock-generation workflow.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/tripo-replica-review';OUT.mkdir(exist_ok=True)
ASSET=ROOT/'assets/layered_island/tripo_replica';ASSET.mkdir(exist_ok=True)
old=bpy.context.window.scene
ref=bpy.data.scenes['Tripo_Coast_Processing_20261119'].objects['Tripo_Coast_Original_Surface']
NAME='Tripo_Reference_Reconstruction_20261119';assert not bpy.data.scenes.get(NAME),'Inspect existing reconstruction.'
s=bpy.data.scenes.new(NAME);bpy.context.window.scene=s
author=bpy.data.collections.new('Tripo_Replica_Authored');s.collection.children.link(author)
guides=bpy.data.collections.new('Tripo_Replica_Hidden_Reference');s.collection.children.link(guides)
review=bpy.data.collections.new('Tripo_Replica_Review_Only');s.collection.children.link(review)
# The guide is a preserved hidden original, not selected for export.
guide=ref.copy();guide.data=ref.data.copy();guide.name='REFERENCE_Tripo_Surface_Not_Exported';guides.objects.link(guide)
guide.hide_render=True
o=bpy.data.objects.new('Replica_Coast_Control_Surface',ref.data.copy());author.objects.link(o)
bpy.context.view_layer.objects.active=o;o.select_set(True)
# Voxel reconstruction removes the original triangles/UV and makes a new
# connected quad control surface from the measured volume.
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000002)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
rem=o.modifiers.new('Measured volume control retopology','REMESH');rem.mode='VOXEL';rem.voxel_size=.014
rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
for uv in list(o.data.uv_layers):o.data.uv_layers.remove(uv)
control_faces=len(o.data.polygons);control_vertices=len(o.data.vertices)
mr=o.modifiers.new('Reconstructed surface detail','MULTIRES')
bpy.ops.object.multires_subdivide(modifier=mr.name,mode='SIMPLE')
bpy.ops.object.multires_subdivide(modifier=mr.name,mode='SIMPLE')
mr.levels=2;mr.sculpt_levels=2;mr.render_levels=2
dg=bpy.context.evaluated_depsgraph_get()
high=bpy.data.objects.new('Temporary_Sampled_Detail',bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg))
author.objects.link(high)
# Fit the newly created samples to the original surface. No source vertex,
# face index or original UV is transferred.
bm=bmesh.new();bm.from_mesh(ref.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000002)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));tree=BVHTree.FromBMesh(bm);bm.free()
distances=[]
for v in high.data.vertices:
    hit,normal,index,d=tree.find_nearest(v.co)
    if hit is not None:
        v.co=hit;distances.append(d)
high.data.update()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);high.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.multires_reshape(modifier=mr.name)
bpy.data.objects.remove(high,do_unlink=True)
for p in o.data.polygons:p.use_smooth=True
o['method']='New voxel control topology + simple subdivision + reference-sampled multires reshape.'
o['reference_required_for_this_reconstruction']=True
o['original_uv_or_texture_reused']=False
s['revision']='reference-constrained-reconstruction-1'
clay=bpy.data.materials.new('Replica_Neutral_Clay');clay.use_nodes=True
clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.36,.38,.38,1)
clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.88
o.data.materials.clear();o.data.materials.append(clay)
for p in o.data.polygons:p.material_index=0
# Comparison reference gets the exact same neutral material, losing the
# original texture advantage. Both views share camera and lights.
refview=ref.copy();refview.data=ref.data.copy();refview.name='Review_Tripo_Gray_Only';review.objects.link(refview)
refview.data.materials.clear();refview.data.materials.append(clay)
for p in refview.data.polygons:p.material_index=0
base=bpy.data.scenes['Tripo_Rock_Stair_Diagnostic_20261119']
for obj in base.objects:
    if obj.type in {'CAMERA','LIGHT'} or obj.name=='DiagnosticFloor':
        cp=obj.copy();cp.data=obj.data.copy();review.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
cam=s.camera;cam.data.ortho_scale=1.43;center=Vector((0,0,.21))
for angle in [0,35]:
    a=math.radians(angle);cam.location=center+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05))
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    o.hide_render=False;refview.hide_render=True
    s.render.filepath=str(OUT/('replica-gray-'+str(angle)+'.png'));bpy.ops.render.render(write_still=True)
    o.hide_render=True;refview.hide_render=False
    s.render.filepath=str(OUT/('reference-gray-'+str(angle)+'.png'));bpy.ops.render.render(write_still=True)
o.hide_render=False;refview.hide_render=True;guide.hide_render=True
bpy.data.libraries.write(str(ASSET/'tripo_reference_replica.blend'),{s},fake_user=True,compress=True)
report={'scene':s.name,'revision':s['revision'],'method':o['method'],
 'scope':'Reference-constrained reconstruction sample. No main-game changes, passage or motion tests.',
 'control_vertices':control_vertices,'control_faces':control_faces,'detail_levels':2,
 'fitted_samples':len(distances),'fitting_distance_max':max(distances),'fitting_distance_mean':sum(distances)/len(distances),
 'original_faces_or_uv_exported':False,'original_texture_reused':False,
 'source_reference':'C:/Users/51440/Downloads/bccfc00f-d7ae-4bae-abab-5cc7e8c254e6.glb',
 'limitations':['This pass uses the Tripo mesh to measure and fit the surface. It does not demonstrate reference-free sculpting or a general reusable geological workflow.',
 'The reference merged static camp objects and thin/back defects remain part of this first faithful comparison.'],
 'status':'Pending visual comparison and user evaluation; workflow has not been created.'}
(OUT/'reconstruction-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old
print(json.dumps(report,ensure_ascii=False))
