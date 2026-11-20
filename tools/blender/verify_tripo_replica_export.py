"""Static GLB readback in an isolated Blender scene, via MCP; no game tests."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/tripo_replica';O=R/'artifacts/tripo-replica-review'
base=bpy.data.scenes['Tripo_Surface_Measurement_Rebuild_20261119'];old=bpy.context.window.scene
SN='Tripo_Replica_GLB_Static_Readback_20261119'
assert not bpy.data.scenes.get(SN),'Read existing static verification.'
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
bpy.ops.import_scene.gltf(filepath=str(A/'tripo_replica_review.glb'))
meshes=[o for o in s.objects if o.type=='MESH'];assert len(meshes)==2
for ob in base.objects:
    if ob.type in {'CAMERA','LIGHT'} or (ob.type=='MESH' and ob.name.startswith('DiagnosticFloor')):
        cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.filepath=str(O/'review-glb-readback.png');bpy.ops.render.render(write_still=True)
report={'meshes':len(meshes),'materials':[[m.name for m in o.data.materials] for o in meshes],
 'bounds':{o.name:[list(o.dimensions),[list(row) for row in o.matrix_world]] for o in meshes},
 'scope':'Isolated Blender static export readback only; no Godot integration, passage or motion tests.'}
(O/'glb-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old;print(json.dumps(report,ensure_ascii=False))
