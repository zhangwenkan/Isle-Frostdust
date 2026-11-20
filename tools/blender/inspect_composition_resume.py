"""Read-only inspection of the interrupted MCP authoring session."""
import bpy,json
from pathlib import Path
r=Path('D:/自己做着玩的/孤屿霜尘/artifacts/rock-stair-composition-review')
s=bpy.data.scenes.get('Layered_Island_20261116')
assert s and bpy.data.collections.get('55_Rock_Stair_Composition')
names=['WALK_Forest_Ground','Cape_Terminus_Bedrock','WALK_Cape_Stairs','Cape_Strict_Rock_Sea_Front','Cape_Strict_Rock_Near_Upper']
rows=[]
for name in names:
 o=s.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices]
 rows.append({'name':name,'vertices':len(vs),'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'materials':[m.name if m else None for m in o.data.materials],'matrix':[list(row) for row in o.matrix_world]})
report={'file':bpy.data.filepath,'active_scene':bpy.context.scene.name,'target_scene':s.name,'objects':rows}
(r/'resume-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
