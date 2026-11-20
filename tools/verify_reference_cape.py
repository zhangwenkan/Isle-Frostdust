"""Read GLB preservation and source files; performs no model generation."""
import ast,json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/reference-cape-review'
source=ast.parse((ROOT/'tools/audit_west_forest_glb.py').read_text(encoding='utf-8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name=='load':exec(compile(ast.Module(body=[node],type_ignores=[]),'read_glb','exec'))
old=load(OUT/'before/layered_island.glb');new=load(ROOT/'assets/layered_island/layered_island.glb')
changes=[n for n in old if old[n]!=new.get(n)]
before=json.loads((OUT/'before/layout.json').read_text());after=json.loads((ROOT/'assets/layered_island/layout.json').read_text())
protected=json.loads((OUT/'before/protected-hashes.json').read_text());file_changes=[n for n,h in protected.items() if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
report={'original_objects':len(old),'protected_objects':len(old)-1,'original_changed':changes,'new_objects':sorted(set(new)-set(old)),'original_anchors_preserved':all(after['anchors'][k]==v for k,v in before['anchors'].items()),'original_edges_preserved':after['edges'][:len(before['edges'])]==before['edges'],'original_camera_metadata_preserved':before['camera']==after['camera'],'wind_metadata_preserved':before['forest_extension']==after['forest_extension'],'protected_file_changes':file_changes,'protected_files':len(protected)}
(OUT/'geometry-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert changes==['Sea_Surface'],changes
assert not file_changes and all(report[k] for k in ['original_anchors_preserved','original_edges_preserved','original_camera_metadata_preserved','wind_metadata_preserved'])
assert all(n.startswith(('Cape_','WALK_Cape_')) for n in report['new_objects'])
print(json.dumps({k:v for k,v in report.items() if k!='new_objects'}))
