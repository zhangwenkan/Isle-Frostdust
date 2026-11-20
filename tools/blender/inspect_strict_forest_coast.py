import bpy,json,array,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/strict-forest-coast-review';O.mkdir(exist_ok=True)
S=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=S
def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def fp(o):
    m=o.data;a=array.array('f',[0])*len(m.vertices)*3;m.vertices.foreach_get('co',a);b=array.array('i',[0])*len(m.loops);m.loops.foreach_get('vertex_index',b);h=hashlib.sha256(a.tobytes()+b.tobytes())
    for u in m.uv_layers:
        c=array.array('f',[0])*len(u.data)*2;u.data.foreach_get('uv',c);h.update(c.tobytes())
    return {'hash':h.hexdigest(),'matrix':[list(r) for r in o.matrix_world]}
objects=[]
for o in S.objects:
    if not live(o):continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box];bounds=[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)]
    if bounds[0][0]<-47 and bounds[0][1]>-90:
        objects.append({'name':o.name,'bounds':bounds,'collections':[c.name for c in o.users_collection],'materials':[m.name for m in o.data.materials],'verts':len(o.data.vertices)})
(O/'inspection.json').write_text(json.dumps(objects,indent=2),encoding='utf8')
if not (O/'before/object-state.json').exists():
    (O/'before/object-state.json').write_text(json.dumps({o.name:fp(o) for o in S.objects if live(o)},indent=2),encoding='utf8')
print(json.dumps({'scene':S.name,'objects':len(objects),'file':bpy.data.filepath,'targets':[(r['name'],r['bounds']) for r in objects if r['name'].startswith(('WALK_Cape','Cape_Swash','Cape_Terminus'))]}))
