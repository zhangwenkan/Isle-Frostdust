"""Reuse the complete swim-volume audit against the new cliff surfaces."""
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
code=(ROOT/'tools/blender/cinematic_validate_life.py').read_text(encoding='utf-8')
code=code.replace("['Rock','Reef','Crag','Continuous_Land']","['Rock','Reef','Crag','Continuous_Land','Cliff_Fractures']")
code=code.replace('artifacts/cinematic-coast-review/swim-clearance.json','artifacts/cliff-form-review/swim-clearance.json')
exec(compile(code,'cliff_validate_swimming','exec'))
