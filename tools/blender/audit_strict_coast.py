"""Read only source audit: preserved geometry, support, roots and UV2 wind."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
import array,hashlib
fail=[]
def fp(o):
    m=o.data;a=array.array('f',[0])*len(m.vertices)*3;m.vertices.foreach_get('co',a);b=array.array('i',[0])*len(m.loops);m.loops.foreach_get('vertex_index',b);h=hashlib.sha256(a.tobytes()+b.tobytes())
    for u in m.uv_layers:
        c=array.array('f',[0])*len(u.data)*2;u.data.foreach_get('uv',c);h.update(c.tobytes())
    return {'hash':h.hexdigest(),'matrix':[list(r) for r in o.matrix_world]}
before=json.loads((R/'before/object-state.json').read_text(encoding='utf8'));exclude=set(state['changed']+state['retired']);protected=0
for name,v in before.items():
    if name in exclude:continue
    o=SCENE.objects.get(name)
    if not o or not live(o) or fp(o)!=v:fail.append({'type':'protected','name':name})
    else:protected+=1
wt=[tree(o) for o in SCENE.objects if live(o) and o.name.startswith('WALK_')];rt=[tree(SCENE.objects[n]) for n in state['rocks']];ft=ground_tree()
def high(t,x,y):return max([h for h in [sample(q,x,y) for q in t] if h is not None],default=None)
route=0;blocked=[]
for ka,kb in LAYOUT['edges']:
    if not ka.startswith(('cape','forest_cape')) and not kb.startswith(('cape','forest_cape')):continue
    a=A[ka];b=A[kb]
    for i in range(81):
        p=a.lerp(b,i/80);h=high(wt,p.x,p.y);rh=high(rt,p.x,p.y);route+=1
        if h is None:fail.append({'type':'route','edge':[ka,kb],'i':i})
        if h is not None and rh is not None and rh>h+.09:blocked.append({'edge':[ka,kb],'i':i,'height':rh-h})
if blocked:fail.append({'type':'rock blocks route','count':len(blocked),'first':blocked[:10]})
roots=[];wind=[]
for row in state['plants']:
    p=Vector(row['root']);h=high([ft]+rt,p.x,p.y);error=abs(p.z-h-.012);roots.append(error)
    if error>.006:fail.append({'type':'root','name':row['name'],'error':error})
    o=SCENE.objects[row['name']];uv=o.data.uv_layers[1]
    weights=[1-uv.data[l].uv.y for l in range(len(uv.data))];wind.append([o.name,min(weights),max(weights)])
    if min(weights)>.002 or max(weights)<.9:fail.append({'type':'wind range','name':o.name})
meshstats=[]
grass_errors=[]
for name in ['Forest_Strict_Grass','Forest_Strict_Understory']:
    o=SCENE.objects[name]
    for start in range(0,len(o.data.vertices),15):
        p=(o.data.vertices[start].co+o.data.vertices[start+2].co)*.5;h=high([ft]+rt,p.x,p.y)
        if h is None:fail.append({'type':'small plant missing substrate','name':name})
        else:grass_errors.append(abs(p.z-h-.008))
if max(grass_errors,default=0)>.009:fail.append({'type':'small plant contact','error':max(grass_errors)})
for o in COL.objects:
    if not live(o):continue
    bad=sum(not all(math.isfinite(c) for c in v.co) for v in o.data.vertices);zero=sum(p.area<1e-10 for p in o.data.polygons)
    if bad or zero:fail.append({'type':'mesh','name':o.name,'nonfinite':bad,'zero':zero})
    meshstats.append([o.name,len(o.data.vertices),len(o.data.polygons)])
report={'revision':LAYOUT['revision'],'protected_objects':protected,'route_samples':route,'bamboo_roots':len(roots),'root_max_error':max(roots,default=0),'small_plant_roots':len(grass_errors),'small_plant_max_error':max(grass_errors,default=0),'wind_ranges':wind,'meshes':meshstats,'failures':fail}
(R/'blender-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['wind_ranges','meshes']}))
