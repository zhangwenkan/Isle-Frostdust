"""Read GLB exports to verify unrelated geometry, UV and matrices are preserved."""
import ast,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tree=ast.parse((ROOT/'tools/audit_west_forest_glb.py').read_text(encoding='utf-8'))
namespace={};exec('import json,struct,hashlib',namespace)
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name=='load':exec(compile(ast.Module(body=[n],type_ignores=[]),'read_only_glb','exec'),namespace)
load=namespace['load'];out=ROOT/'artifacts/forest-layer-role-review'
before=load(out/'before/layered_island.glb');after=load(ROOT/'assets/layered_island/layered_island.glb')
archived=set(json.loads((out/'build-report.json').read_text(encoding='utf-8'))['archived'])
protected=set(before)-archived
old_layout=json.loads((out/'before/layout.json').read_text(encoding='utf-8'))
new_layout=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
report={'protected_objects':len(protected),'unexpected_changes':[n for n in sorted(protected) if before[n]!=after.get(n)],'archived':[n for n in sorted(archived) if n not in after],'new':[n for n in after if n not in before],
        'routes_and_camera_unchanged':all(old_layout[k]==new_layout[k] for k in ['anchors','edges','camera'])}
(out/'geometry-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'protected':len(protected),'unexpected_changes':report['unexpected_changes'],'new':len(report['new']),'archived':len(report['archived'])}))
assert not report['unexpected_changes']
assert report['routes_and_camera_unchanged']
