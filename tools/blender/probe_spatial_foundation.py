import bpy,json,os
from pathlib import Path
scene=bpy.data.scenes['Layered_Island_20261116']
r={'pid':os.getpid(),'filepath':bpy.data.filepath,'objects':[]}
for o in scene.objects:
    if o.type=='MESH' and (o.name.startswith(('Land','Cave','Bamboo','Foreground','WALK_','SUPPORT_'))):
        points=[o.matrix_world@v.co for v in o.data.vertices]
        r['objects'].append({'name':o.name,'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'collections':[c.name for c in o.users_collection]})
Path('D:/自己做着玩的/孤屿霜尘/artifacts/spatial-foundation-review/probe.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({'pid':r['pid'],'filepath':r['filepath'],'objects':len(r['objects'])}))
