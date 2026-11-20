"""Remove only the derived first bake scene after detecting lost material slots."""
import bpy,json
from pathlib import Path
O=Path('D:/自己做着玩的/孤屿霜尘/artifacts/tripo-replica-review')
s=bpy.data.scenes['Tripo_Textured_Delivery_20261119']
assert s['revision']=='authored-textures-baked-5'
report=json.loads((O/'material-bake-status.json').read_text(encoding='utf8'))
report['validation_failure']='Clearing material slots reset polygon assignments. First baked maps do not preserve wood/fire regions; superseded, not delivered.'
(O/'material-bake-first-rejected.json').write_text(json.dumps(report,indent=2),encoding='utf8')
bpy.context.window.scene=bpy.data.scenes['Tripo_Authored_Material_Sample_20261119']
for ob in list(s.objects):
    assert len(ob.users_scene)==1
    bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.scenes.remove(s)
print('Removed only rejected derived bake scene; authored source and gray source retained.')
