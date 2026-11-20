"""Reference-surface reconstruction study, exclusively executed via Blender MCP.

The supplied thin/nonorientable surface is a measurement input. A disposable
thickened shell makes a new voxel control topology. It is not independent
sculpting and must never be reported as such. No original textures or UVs.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
SN='Tripo_Surface_Measurement_Rebuild_20261119'
assert not bpy.data.scenes.get(SN),'Do not repeat this completed shell reconstruction.'
old=bpy.context.window.scene;s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
col=bpy.data.collections.new('Replica_New_Surface_Topology');s.collection.children.link(col)
rev=bpy.data.collections.new('Replica_Surface_Review_Only');s.collection.children.link(rev)
ref=bpy.data.scenes['Tripo_Coast_Processing_20261119'].objects['Tripo_Coast_Original_Surface']
o=bpy.data.objects.new('Replica_Surface_Control',ref.data.copy());col.objects.link(o)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000002);bm.to_mesh(o.data);bm.free()
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
sol=o.modifiers.new('Disposable measured thin-surface support','SOLIDIFY');sol.thickness=.008;sol.offset=0;sol.use_even_offset=False
sol.solidify_mode='NON_MANIFOLD';bpy.ops.object.modifier_apply(modifier=sol.name)
rem=o.modifiers.new('New measured shell topology','REMESH');rem.mode='VOXEL';rem.voxel_size=.0025;rem.use_smooth_shade=True;rem.use_remove_disconnected=False
bpy.ops.object.modifier_apply(modifier=rem.name)
for uv in list(o.data.uv_layers):o.data.uv_layers.remove(uv)
o.data.materials.clear();o.data.materials.append(bpy.data.materials['Replica_Neutral_Clay'])
for p in o.data.polygons:p.material_index=0;p.use_smooth=True
s['revision']='thick-surface-new-topology-1'
base=bpy.data.scenes['Tripo_Reference_Reconstruction_20261119']
for ob in base.objects:
    if ob.type in {'CAMERA','LIGHT'} or (ob.type=='MESH' and ob.name.startswith('DiagnosticFloor')):
        cp=ob.copy();cp.data=ob.data.copy();rev.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
cam=s.camera;cam.data.ortho_scale=1.43;target=Vector((0,0,.21))
bpy.data.libraries.write(str(A/'tripo_surface_measurement_replica.blend'),{s},fake_user=True,compress=True)
for angle in [0,35]:
    a=math.radians(angle);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(O/('shell-replica-gray-%s.png'%angle));bpy.ops.render.render(write_still=True)
report={'scene':SN,'revision':s['revision'],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'method':__doc__,
 'voxel_size':.0025,'support_shell_thickness':.008,'source_faces':len(ref.data.polygons),'source_vertices':len(ref.data.vertices),
 'source_uv_or_texture_reused':False,'status':'Surface measurement replica; independent sculpting not demonstrated.'}
(O/'shell-reconstruction-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old;print(json.dumps(report,ensure_ascii=False))
