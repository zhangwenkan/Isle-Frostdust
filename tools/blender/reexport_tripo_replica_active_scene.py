"""Correct Blender's multi-scene GLB export and perform static readback via MCP."""
import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/tripo_replica';O=R/'artifacts/tripo-replica-review'
base=bpy.data.scenes['Tripo_Surface_Measurement_Rebuild_20261119'];old=bpy.context.window.scene;bpy.context.window.scene=base
for o in base.objects:o.select_set(False)
for name in ['Replica_Measured_Rock_Surfaces','Replica_Authored_Diagonal_Staircase']:base.objects[name].select_set(True)
bpy.context.view_layer.objects.active=base.objects['Replica_Measured_Rock_Surfaces']
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_replica_review.glb'),export_format='GLB',use_selection=True,use_active_scene=True,
 export_materials='EXPORT',export_cameras=False,export_lights=False)
SN='Tripo_Replica_GLB_Static_Readback_Corrected_20261119';assert not bpy.data.scenes.get(SN)
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s;bpy.ops.import_scene.gltf(filepath=str(A/'tripo_replica_review.glb'))
meshes=[o for o in s.objects if o.type=='MESH'];assert len(meshes)==2,'The standalone GLB must contain just its two review meshes.'
for ob in base.objects:
    if ob.type in {'CAMERA','LIGHT'} or (ob.type=='MESH' and ob.name.startswith('DiagnosticFloor')):
        cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.filepath=str(O/'review-glb-readback.png');bpy.ops.render.render(write_still=True)
report={'meshes':len(meshes),'mesh_names':[o.name for o in meshes],'materials':[[m.name for m in o.data.materials] for o in meshes],
 'glb_bytes':(A/'tripo_replica_review.glb').stat().st_size,'scope':'Corrected active-scene-only export. Isolated Blender static readback, no game tests.'}
(O/'glb-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old;print(json.dumps(report,ensure_ascii=False))
