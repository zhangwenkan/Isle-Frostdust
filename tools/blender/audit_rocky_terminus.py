"""Read-only audit of the integrated Blender source, UV, roots and route."""
import bpy,json,ast,array,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');R=ROOT/'artifacts/forest-rocky-terminus-review'
SCENE=bpy.data.scenes['Layered_Island_20261116'];LAYOUT=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf8'))
data=LAYOUT['reference_cape']['rocky_terminus'];failures=[]
def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
code=ast.parse((ROOT/'tools/blender/build_rocky_terminus.py').read_text(encoding='utf8'))
for f in code.body:
    if isinstance(f,ast.FunctionDef) and f.name=='fingerprint':exec(compile(ast.Module(body=[f],type_ignores=[]),'read-only-fingerprint','exec'))
before=json.loads((R/'before/object-state.json').read_text(encoding='utf8'))
excluded=set(data['changed_objects']+data['retired_objects']);protected=0
for name,state in before.items():
    if name in excluded:continue
    o=SCENE.objects.get(name)
    if not o or not live(o) or fingerprint(o)!=state:failures.append({'type':'protected object changed','name':name})
    else:protected+=1
meshes=[]
for o in SCENE.objects:
    if not live(o):continue
    if o.name in ['WALK_Forest_Ground','WALK_Cape_Stairs','WALK_Cape_Sand','Forest_Grass_Terminus'] or o.name.startswith('Cape_Terminus_'):
        bad=sum(not all(math.isfinite(c) for c in v.co) for v in o.data.vertices)
        uvbad=sum(not all(math.isfinite(c) for c in p.uv) for u in o.data.uv_layers for p in u.data)
        zero=sum(p.area<1e-10 for p in o.data.polygons)
        if bad or uvbad:failures.append({'type':'nonfinite mesh','name':o.name,'vertices':bad,'uv':uvbad})
        meshes.append({'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'tiny_area_faces':zero,'uv_layers':[u.name for u in o.data.uv_layers]})
ground=SCENE.objects['WALK_Forest_Ground']
names=[o.name for o in SCENE.objects if live(o) and o.name.startswith('WALK_')]
trees={n:BVHTree.FromPolygons([v.co for v in SCENE.objects[n].data.vertices],[list(p.vertices) for p in SCENE.objects[n].data.polygons]) for n in names}
def support(x,y):
    hits=[t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0] for t in trees.values()]
    return max([h.z for h in hits if h is not None],default=None)
route_samples=0
for edge in LAYOUT['edges']:
    a=Vector(LAYOUT['anchors'][edge[0]]);b=Vector(LAYOUT['anchors'][edge[1]])
    if not (edge[0].startswith(('forest','cape')) and edge[1].startswith(('forest','cape'))):continue
    for i in range(81):
        p=a.lerp(b,i/80);h=support(p.x,-p.z);route_samples+=1
        if h is None:failures.append({'type':'route missing support','edge':edge,'t':i/80})

# Preserve the registered painting and wind UV at every untouched eastern loop.
def uvrecords(o):
    result=set()
    for p in o.data.polygons:
        for li in p.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co
            if v.x<=-53.99999:continue
            record=[round(c,5) for c in v]
            for u in o.data.uv_layers:record.extend(round(c,5) for c in u.data[li].uv)
            result.add(tuple(record))
    return result
old=uvrecords(SCENE.objects['LongTip_Before_WALK_Forest_Ground']);now=uvrecords(ground)
missing=len(old-now)
if missing:failures.append({'type':'eastern vertex or UV changed','records':missing})
rocktrees=[BVHTree.FromPolygons([v.co for v in SCENE.objects[n].data.vertices],[list(p.vertices) for p in SCENE.objects[n].data.polygons]) for n in LAYOUT['reference_cape']['cliff_masses']]
def plant_support(x,y):
    hits=[t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0] for t in [trees['WALK_Forest_Ground']]+rocktrees]
    return max(h.z for h in hits if h is not None)
roots=[]
for name in data['new_bamboo']:
    binding=LAYOUT['forest_extension']['layer_roles']['wind_bindings'][name];p=binding['root'];error=abs(p[1]-plant_support(p[0],-p[2])-.012)
    roots.append({'name':name,'error':error})
    if error>.003:failures.append({'type':'bamboo root support','name':name,'error':error})
grass=SCENE.objects['Forest_Grass_Terminus'];errors=[]
uv=grass.data.uv_layers[1]
for li,loop in enumerate(grass.data.loops):
    if uv.data[li].uv.x>.001:continue
    p=grass.data.vertices[loop.vertex_index].co;errors.append(abs(p.z-plant_support(p.x,p.y)-.012))
if max(errors,default=0)>.08:failures.append({'type':'grass root support','max_error':max(errors)})
report={'revision':LAYOUT['revision'],'protected_objects':protected,'authorized_changed_objects':len(excluded),'eastern_uv_records':len(old),'missing_eastern_uv_records':missing,'route_samples':route_samples,'meshes':meshes,'new_bamboo_roots':roots,'grass_root_max_error':max(errors,default=0),'grass_root_samples':len(errors),'failures':failures}
(R/'blender-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','new_bamboo_roots','failures']}|{'failure_count':len(failures),'first_failures':failures[:3]}))
