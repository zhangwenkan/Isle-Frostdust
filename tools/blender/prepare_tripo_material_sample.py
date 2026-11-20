"""Isolated material sample and reference, executed only via Blender MCP."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘'); O=R/'artifacts/tripo-replica-review'
SN='Tripo_Authored_Material_Sample_20261119'
assert not bpy.data.scenes.get(SN), 'Already prepared; inspect instead of repeating.'
base=bpy.data.scenes['Tripo_Surface_Measurement_Rebuild_20261119']
s=bpy.data.scenes.new(SN); bpy.context.window.scene=s
for ob in base.objects:
    if ob.hide_render: continue
    cp=ob.copy(); cp.data=ob.data.copy(); s.collection.objects.link(cp)
    if ob.name=='Replica_Measured_Rock_Surfaces': cp.name='Textured_Measured_Rocks'
    elif ob.name=='Replica_Authored_Diagonal_Staircase': cp.name='Textured_Authored_Stairs'
    if cp.type=='CAMERA': s.camera=cp
s.world=base.world.copy(); s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.use_denoising=True
s.render.resolution_x=1200; s.render.resolution_y=960; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'
s['revision']='authored-material-prepared-1'
src=Path('C:/Users/51440/Downloads/bccfc00f-d7ae-4bae-abab-5cc7e8c254e6.glb')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='e51a58a5a6d60e8c2c3334d44a0509e16c6475ac73c2bed97051d74d05679bd2'
ref=bpy.data.scenes.new('Tripo_Material_Reference_20261119'); bpy.context.window.scene=ref
bpy.ops.import_scene.gltf(filepath=str(src)); ob=next(o for o in ref.objects if o.type=='MESH'); ob.name='Material_Reference_Original'
for o in s.objects:
    if o.type in {'LIGHT','CAMERA'}:
        cp=o.copy(); cp.data=o.data.copy(); ref.collection.objects.link(cp)
        if cp.type=='CAMERA': ref.camera=cp
ref.world=s.world; ref.render.engine='CYCLES'; ref.cycles.samples=16; ref.cycles.use_denoising=True
ref.render.resolution_x=1100;ref.render.resolution_y=1100;ref.render.resolution_percentage=100
ref.render.image_settings.file_format='PNG'; ref.view_settings.view_transform='AgX'; ref.view_settings.look=s.view_settings.look
ref.camera.location=(0,0,2);ref.camera.rotation_euler=(0,0,0);ref.camera.data.ortho_scale=1.13
ref.render.filepath=str(O/'material-reference-top.png');bpy.ops.render.render(write_still=True)
report={'sample_scene':s.name,'reference_scene':ref.name,'sample_meshes':[{'name':o.name,'faces':len(o.data.polygons),'matrix':[list(row) for row in o.matrix_world]} for o in s.objects if o.type=='MESH' and not o.name.startswith('Diagnostic')],
 'reference_high_bounds':[[min(v.co[k] for v in ob.data.vertices if v.co.z>.39) for k in range(3)],[max(v.co[k] for v in ob.data.vertices if v.co.z>.39) for k in range(3)]]}
(O/'material-prepared.json').write_text(json.dumps(report,indent=2),encoding='utf8')
bpy.context.window.scene=s
print(json.dumps(report))
