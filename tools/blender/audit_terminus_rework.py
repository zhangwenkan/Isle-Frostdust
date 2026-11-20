"""Read only: protected source, actual contact and foreground clearance."""
import bpy,json,array,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-rocky-terminus-rework';S=bpy.data.scenes['Layered_Island_20261116']
L=json.loads((R/'assets/layered_island/layout.json').read_text(encoding='utf8'));rw=L['reference_cape']['rocky_terminus']['reference_rework'];fail=[]
def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def fp(o):
    m=o.data;a=array.array('f',[0])*len(m.vertices)*3;m.vertices.foreach_get('co',a);b=array.array('i',[0])*len(m.loops);m.loops.foreach_get('vertex_index',b);h=hashlib.sha256(a.tobytes()+b.tobytes())
    for u in m.uv_layers:
        c=array.array('f',[0])*len(u.data)*2;u.data.foreach_get('uv',c);h.update(c.tobytes())
    return dict(hash=h.hexdigest(),matrix=[list(r) for r in o.matrix_world])
before=json.loads((O/'before/object-state.json').read_text(encoding='utf8'));exclude=set(rw['changed']+rw['retired']);protected=0
for name,state in before.items():
    if name in exclude:continue
    ob=S.objects.get(name)
    if not ob or not live(ob) or fp(ob)!=state:fail.append({'type':'protected','name':name})
    else:protected+=1
def records(o):
    out=set()
    for li,l in enumerate(o.data.loops):
        p=o.data.vertices[l.vertex_index].co
        if p.x<-53.99999:continue
        r=[round(c,5) for c in p]
        for u in o.data.uv_layers:r.extend(round(c,5) for c in u.data[li].uv)
        out.add(tuple(r))
    return out
old=records(S.objects['Relief_Before_WALK_Forest_Ground']);now=records(S.objects['WALK_Forest_Ground']);missing=len(old-now)
if missing:fail.append({'type':'east position/UV','count':missing})
def tree(o):return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
walk=[tree(o) for o in S.objects if live(o) and o.name.startswith('WALK_')]
rock=[tree(S.objects[n]) for n in L['reference_cape']['cliff_masses']]
def sample(t,x,y):
    p=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0];return p.z if p else None
def support(x,y,trees=walk):return max([z for z in [sample(t,x,y) for t in trees] if z is not None],default=None)
route=0;blocked=[]
for a,b in L['edges']:
    if not a.startswith(('cape','forest_cape')) and not b.startswith(('cape','forest_cape')):continue
    p=Vector(L['anchors'][a]);q=Vector(L['anchors'][b])
    for i in range(81):
        v=p.lerp(q,i/80);h=support(v.x,-v.z);route+=1
        if h is None:fail.append({'type':'route missing','edge':[a,b],'t':i/80})
        rh=support(v.x,-v.z,rock)
        if rh is not None and h is not None and rh>h+.08:blocked.append({'edge':[a,b],'t':i/80,'height':rh-h})
if blocked:fail.append({'type':'rock over route','count':len(blocked),'first':blocked[:5]})
ft=tree(S.objects['WALK_Forest_Ground']);roots=[]
for name in rw['root_bamboo']:
    bind=L['forest_extension']['layer_roles']['wind_bindings'][name];p=bind['root'];h=support(p[0],-p[2],[ft]+rock);e=abs(p[1]-h-.012);roots.append(e)
    if e>.006:fail.append({'type':'plant support','name':name,'error':e})
g=S.objects['Forest_Grass_Terminus'];gr=[]
for start in range(0,len(g.data.vertices),5):
    p=(g.data.vertices[start].co+g.data.vertices[start+1].co)*.5;h=support(p.x,p.y,[ft]+rock)
    if h is None:fail.append({'type':'grass missing support','point':list(p)})
    else:gr.append(abs(p.z-h-.012))
if max(gr,default=0)>.006:fail.append({'type':'grass root center','error':max(gr)})
meshes=[]
for ob in S.objects:
    if not live(ob) or not (ob.name.startswith('Cape_Terminus_') or ob.name.startswith('Forest_Grass_Terminus')):continue
    bad=sum(not all(math.isfinite(c) for c in v.co) for v in ob.data.vertices);uvbad=sum(not all(math.isfinite(c) for c in p.uv) for u in ob.data.uv_layers for p in u.data);zero=sum(p.area<1e-10 for p in ob.data.polygons)
    if bad or uvbad or zero:fail.append({'type':'mesh data','name':ob.name,'nonfinite':bad+uvbad,'zero_faces':zero})
    meshes.append({'name':ob.name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons)})
report={'revision':L['revision'],'protected_objects':protected,'eastern_records':len(old),'missing_eastern_records':missing,'route_samples':route,'bamboo_root_max_error':max(roots,default=0),'grass_root_max_error':max(gr,default=0),'meshes':meshes,'failures':fail}
(O/'blender-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='meshes'}))
