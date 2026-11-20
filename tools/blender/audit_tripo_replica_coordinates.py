"""Read-only audit through Blender MCP, before continuing the saved replica."""
import bpy,json
from mathutils import Vector
for sn in ['Tripo_Coast_Processing_20261119','Tripo_Measured_Profile_Rebuild_20261119']:
    s=bpy.data.scenes.get(sn)
    if not s:
        print('Missing scene',sn);continue
    rows=[]
    for o in s.objects:
        if o.type!='MESH' or o.name.startswith('DiagnosticFloor'):continue
        local=[v.co for v in o.data.vertices]
        world=[o.matrix_world@v for v in local]
        rows.append({'name':o.name,'matrix':[list(r) for r in o.matrix_world],
         'local_bounds':[[min(v[k] for v in local) for k in range(3)],[max(v[k] for v in local) for k in range(3)]],
         'world_bounds':[[min(v[k] for v in world) for k in range(3)],[max(v[k] for v in world) for k in range(3)]],
         'vertices':len(local),'faces':len(o.data.polygons)})
    print(json.dumps({'scene':sn,'objects':rows},ensure_ascii=False))
