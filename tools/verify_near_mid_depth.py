"""Read exported geometry and protected files; no modeling outside Blender."""
import ast,hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/near-mid-depth-review'
source=ast.parse((ROOT/'tools/audit_west_forest_glb.py').read_text(encoding='utf-8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name=='load':exec(compile(ast.Module(body=[node],type_ignores=[]),'read_glb','exec'))
before=load(OUT/'before/layered_island.glb');after=load(ROOT/'assets/layered_island/layered_island.glb')
old=json.loads((OUT/'before/layout.json').read_text(encoding='utf-8'));new=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
allowed=set(new['forest_extension']['near_mid_depth']['changed_objects'])
unexpected=[name for name in before if name not in allowed and before[name]!=after.get(name)]
protected=json.loads((OUT/'before/protected-hashes.json').read_text(encoding='utf-8'))
file_changes=[name for name,digest in protected.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
bindings=old['forest_extension']['layer_roles']['wind_bindings']
wind=[]
for name,row in bindings.items():
    current=new['forest_extension']['layer_roles']['wind_bindings'][name]
    if name not in allowed and row!=current:wind.append(name)
    if name in allowed and any(row[k]!=current[k] for k in row if k!='root'):wind.append(name)
report={'original_objects':len(before),'protected_objects':len(before)-len(allowed),'unexpected_geometry_changes':unexpected,
        'expected_changed_objects':sorted(allowed),'new_objects':sorted(set(after)-set(before)),
        'route_anchors_and_edges_preserved':all(old[k]==new[k] for k in ['anchors','edges']),
        'base_camera_metadata_preserved':old['camera']==new['camera'],'wind_metadata_failures':wind,
        'protected_files':len(protected),'protected_file_changes':file_changes}
(OUT/'geometry-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not unexpected and not file_changes and not wind
assert report['route_anchors_and_edges_preserved'] and report['base_camera_metadata_preserved']
assert len(report['new_objects'])==4 and all(n.startswith('Forest_Eroded_Bank_') for n in report['new_objects'])
print(json.dumps({k:v for k,v in report.items() if k!='expected_changed_objects'}))
