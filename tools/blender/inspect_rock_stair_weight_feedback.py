"""Read-only geometry diagnosis via Blender MCP after user close-up feedback."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review/feedback-steps'
s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];report=[]
for name in ['WALK_Tripo_Rock_Surface','WALK_Tripo_Stairs']:
    ob=s.objects[name];me=ob.data;vs=[ob.matrix_world@v.co for v in me.vertices]
    row={'name':name,'vertices':len(vs),'faces':len(me.polygons),'smooth_faces':sum(p.use_smooth for p in me.polygons),'bounds_author_m':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]],'dimensions_author_m':[max(v[k] for v in vs)-min(v[k] for v in vs) for k in range(3)],'modifiers':[m.type for m in ob.modifiers]}
    if name.endswith('Stairs'):
        levels=sorted({round(v.co.z,4) for v in me.vertices})
        row['local_z_levels']=levels;row['normals']=[list(me.polygons[i].normal) for i in range(0,len(me.polygons),max(1,len(me.polygons)//20))]
    report.append(row)
(O/'geometry-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
