"""Withdraw the broad shoal experiment; retain low submerged rock feet."""
import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
bed=s.objects['Fish_Seabed'];base=bpy.data.objects['ShallowBaseline_Fish_Seabed'];bed.data=base.data.copy();bed.matrix_world=base.matrix_world.copy()
p=R/'artifacts/shallow-cape-review/authoring.json';report=json.loads(p.read_text(encoding='utf8'));report['changed']=[n for n in report['changed'] if n!='Fish_Seabed'];report['wide_shoal_withdrawn']=True;report['shallow_water_structure']='Submerged lower rock feet; original ocean and seabed retained';p.write_text(json.dumps(report,indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
