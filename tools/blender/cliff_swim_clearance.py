"""Blender MCP: retain nearby clear swimming lanes after the cliff sculpt."""
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
code=(ROOT/'tools/blender/cinematic_safe_swim_routes.py').read_text(encoding='utf-8')
code=code.replace("['Rock','Reef','Crag','Continuous_Land']","['Rock','Reef','Crag','Continuous_Land','Cliff_Fractures']")
code=code.replace("originals=[(6.4,1.6,-2.92),(8.4,1.42,-3.68),(11.0,-1.72,-3.42),(13.0,.55,-2.8)]","originals=[(6.0,2.5,-2.92),(8.5,.5,-3.656361),(11.0,-2.5,-3.42),(12.0,.5,-2.8)]")
code=code.replace('artifacts/cinematic-coast-review/swim-placement.json','artifacts/cliff-form-review/swim-placement.json')
exec(compile(code,'cliff_swim_clearance','exec'))
