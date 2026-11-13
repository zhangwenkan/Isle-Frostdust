"""Read-only Blender MCP checks for the new near-terrain composition."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/foreground-space-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
assert not any(o.name.startswith(('Depth_Foreground_Crag','Depth_Bamboo_Fore','Near_Bamboo_')) for o in active)
report={'active_meshes':len(active),'retired_foreground_exported':False,'terrain':[],'plants':[],'main_bamboo_missing_ground':[]}
lands=[scene.objects[n] for n in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']]
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
landtrees=[tree(o) for o in lands]
for ob in lands:
    base=bpy.data.meshes[ob.name+'_Before_Foreground_Space'];count=(53 if 'East' in ob.name else 101)*26
    indices=[i for i in range(count) if 11<=i%26<=15]
    delta=max((ob.data.vertices[i].co-base.vertices[i].co).length for i in indices)
    assert delta<1e-6
    report['terrain'].append({'name':ob.name,'walk_vertices':len(indices),'max_walk_delta_m':delta,'finite_vertices':all(math.isfinite(v) for p in ob.data.vertices for v in p.co)})
    assert report['terrain'][-1]['finite_vertices']
rocks=[tree(o) for o in active if o.name.startswith('Cliff_Fractures') or o in lands]
for ob in active:
    if ob.name.startswith('Cliff_Fern_'):
        uv=ob.data.uv_layers['WindWeight'];ids={l.vertex_index for l in ob.data.loops if uv.data[l.index].uv.x<.001}
        center=sum((ob.matrix_world@ob.data.vertices[i].co for i in ids),Vector())/len(ids)
        distances=[r.find_nearest(center)[3] for r in rocks]
        gap=min(d for d in distances if d is not None)
        report['plants'].append({'name':ob.name,'root_surface_gap_m':gap})
        assert gap<.12,(ob.name,gap)
    if ob.name.startswith('Depth_Bamboo_Main_'):
        for x,y,z in json.loads(ob['root_positions_godot']):
            hits=[t.ray_cast(Vector((x,-z,30)),Vector((0,0,-1)))[0] for t in landtrees]
            ys=[p.z for p in hits if p is not None]
            if not ys or y-max(ys)>.08:report['main_bamboo_missing_ground'].append([ob.name,x,y,z])
assert not report['main_bamboo_missing_ground']
(OUT/'contact-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
code=(ROOT/'tools/blender/cinematic_validate_life.py').read_text(encoding='utf-8')
code=code.replace("['Rock','Reef','Crag','Continuous_Land']","['Rock','Reef','Crag','Continuous_Land','Cliff_Fractures']")
code=code.replace('artifacts/cinematic-coast-review/swim-clearance.json','artifacts/foreground-space-review/swim-clearance.json')
exec(compile(code,'foreground_swim_audit','exec'))
swim=json.loads((OUT/'swim-clearance.json').read_text(encoding='utf-8'))
assert min(f['minimum_floor_clearance_m'] for f in swim['fish'])>.10
print('FOREGROUND_CONTACTS_VERIFIED',json.dumps(report))
