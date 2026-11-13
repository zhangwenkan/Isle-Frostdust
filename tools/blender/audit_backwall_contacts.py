from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘')
AUDIT_OUTPUT=R/'artifacts/forest-backwall-review'
AUDIT_PHASE='backwall'
exec(compile((R/'tools/blender/audit_forest_rock_roots.py').read_text(encoding='utf8'),'audit_forest_rock_roots.py','exec'))
assert all(not r['intersecting_stems'] for r in report)
