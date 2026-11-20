"""Read local terrain boundary and assets through the existing Blender MCP."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review'
s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];result={'scene':s.name,'objects':[]}
for ob in s.objects:
    if ob.type!='MESH':continue
    row={'name':ob.name,'vertices':len(ob.data.vertices),'materials':[m.name if m else None for m in ob.data.materials]}
    if ob.name.startswith('GameJoin_') and ('Ground' in ob.name or 'Bedrock' in ob.name):
        bm=bmesh.new();bm.from_mesh(ob.data)
        row['boundary']=[[list(ob.matrix_world@v.co) for v in e.verts] for e in bm.edges if e.is_boundary and any(-63<v.co.x<-52 and v.co.y<16 for v in e.verts)]
        bm.free()
    result['objects'].append(row)
result['sand_objects']=[{'name':ob.name,'scene':[sc.name for sc in ob.users_scene],'bounds':[list(ob.matrix_world@Vector(v)) for v in ob.bound_box]} for ob in bpy.data.objects if ob.type=='MESH' and 'Sand' in ob.name and not '.' in ob.name]
result['scenes']=[sc.name for sc in bpy.data.scenes]
(O/'join-source.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({'objects':[(r['name'],r['vertices'],len(r.get('boundary',[]))) for r in result['objects']],'sand_names':[r['name'] for r in result['sand_objects']],'file':str(O/'join-source.json')}))
