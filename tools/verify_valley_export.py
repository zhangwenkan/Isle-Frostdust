"""Compare untouched Blender export objects by accessor bytes and transforms."""
import ast,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
code=ast.parse((ROOT/'tools/audit_west_forest_glb.py').read_text(encoding='utf-8'))
namespace={}
exec('import json,struct,hashlib',namespace)
for node in code.body:
    if isinstance(node,ast.FunctionDef) and node.name=='load':
        exec(compile(ast.Module(body=[node],type_ignores=[]),'read_only_glb','exec'),namespace)
load=namespace['load']
out=ROOT/'artifacts/forest-valley-enclosure-review'
before=load(out/'before/layered_island.glb')
after=load(ROOT/'assets/layered_island/layered_island.glb')
changed_names={'Forest_Back_Ground'}|{n for n in before if n.startswith('Forest_Bamboo_DeepRow_')}
protected=set(before)-changed_names
report={'protected_objects':len(protected),'unexpected_changes':[n for n in sorted(protected) if before[n]!=after.get(n)],
        'archived':[n for n in sorted(changed_names) if n not in after],
        'new':[n for n in after if n not in before]}
(out/'geometry-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'protected_objects':report['protected_objects'],'unexpected_changes':report['unexpected_changes'],'new_objects':len(report['new'])}))
assert not report['unexpected_changes']
