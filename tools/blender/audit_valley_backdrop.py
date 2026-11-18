"""Read normals, wind channels and live source bounds through Blender MCP."""
import bpy,json
from pathlib import Path
scene=bpy.data.scenes['Layered_Island_20261116']
collection=bpy.data.collections['44_Valley_Forest_Backdrop']
rows=[];bad=[]
for ob in collection.objects:
    if ob.type!='MESH':continue
    me=ob.data
    weights=[uv.uv.x for uv in me.uv_layers[1].data]
    row={'name':ob.name,'vertices':len(me.vertices),'faces':len(me.polygons),'uv_layers':len(me.uv_layers),'zero_area_faces':sum(p.area<1e-10 for p in me.polygons),'wind_min':min(weights),'wind_max':max(weights)}
    if row['zero_area_faces'] or row['uv_layers']!=2:bad.append(ob.name)
    rows.append(row)
report={'file':bpy.data.filepath,'scene':scene.name,'collection':collection.name,'objects':rows,'invalid':bad,'ground_downward_faces':sum(p.normal.z<0 for p in scene.objects['Forest_Valley_Ground'].data.polygons)}
Path('D:/自己做着玩的/孤屿霜尘/artifacts/forest-valley-enclosure-review/blender-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'objects':len(rows),'invalid':bad,'ground_downward_faces':report['ground_downward_faces']}))
