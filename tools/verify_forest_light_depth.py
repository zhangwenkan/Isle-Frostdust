"""Read GLBs to verify protected meshes and route/camera/wind metadata."""
import ast,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/forest-light-depth-review'
tree=ast.parse((ROOT/'tools/audit_west_forest_glb.py').read_text(encoding='utf-8'))
ns={};exec('import json,struct,hashlib',ns)
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name=='load':exec(compile(ast.Module(body=[n],type_ignores=[]),'read_glb','exec'),ns)
before=ns['load'](OUT/'before/layered_island.glb');after=ns['load'](ROOT/'assets/layered_island/layered_island.glb')
old=json.loads((OUT/'before/layout.json').read_text(encoding='utf-8'));new=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
report={'protected_objects':len(before),'unexpected_changes':[n for n in before if before[n]!=after.get(n)],'new_objects':sorted(set(after)-set(before)),
        'routes_camera_unchanged':all(old[k]==new[k] for k in ['anchors','edges','camera']),
        'forest_existing_metadata_unchanged':all(v==new['forest_extension']['layer_roles'][k] for k,v in old['forest_extension']['layer_roles'].items())}
(OUT/'geometry-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report));assert not report['unexpected_changes'];assert report['routes_camera_unchanged'];assert report['forest_existing_metadata_unchanged']
assert len(report['new_objects'])==6 and all(n.startswith('Forest_Sunray_') for n in report['new_objects'])
