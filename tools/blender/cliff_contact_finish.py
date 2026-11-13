"""Blender MCP: seat cliff plants and audit retained gameplay surfaces."""
import bpy,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
dg=bpy.context.evaluated_depsgraph_get()
rocks=[o for o in scene.objects if o.name.startswith('Cliff_Fractures_') or 'Continuous_Land' in o.name]
trees=[BVHTree.FromObject(o,dg) for o in rocks]
plants=[]
for ob in scene.objects:
    if not ob.name.startswith('Cliff_Fern_'):continue
    key=ob.name+'_Before_Contact'
    baseline=bpy.data.meshes.get(key)
    if baseline is None:baseline=ob.data.copy();baseline.name=key;baseline.use_fake_user=True
    ob.data=baseline.copy()
    uv=ob.data.uv_layers['WindWeight'];roots={l.vertex_index for l in ob.data.loops if uv.data[l.index].uv.x<.001}
    p=sum((ob.data.vertices[i].co for i in roots),Vector())/len(roots)
    east='East' in ob.name
    outward=Vector((p.x-(20.3 if east else -7.2),p.y,0)).normalized()
    # The front lip points toward negative Blender Y. The actual contact is
    # measured on the final fracture surfaces rather than on the retired shell.
    outward=Vector((outward.x*.22,-1,0)).normalized()
    hits=[t.ray_cast(p+outward*4,-outward,8)[0] for t in trees]
    hits=[h for h in hits if h is not None]
    if hits:
        hit=max(hits,key=lambda h:h.dot(outward));shift=hit-p+outward*.018
        for v in ob.data.vertices:v.co+=shift
        ob.data.update();plants.append({'name':ob.name,'root_offset_m':shift.length})
report={'plants':plants,'terrain':[],'walking_intrusions':[]}
for east in [False,True]:
    ob=scene.objects['Fish_East_Continuous_Land' if east else 'Fish_West_Continuous_Land']
    baseline=bpy.data.meshes[ob.name+'_Before_Cliff_Forms'];count=(53 if east else 101)*26
    delta=max((ob.data.vertices[i].co-baseline.vertices[i].co).length for i in range(count))
    report['terrain'].append({'name':ob.name,'top_vertices':count,'max_top_delta_m':delta})
    assert delta<1e-6
    for index in range(81):
        x=(14.5+9.2*index/80) if east else (-18+22.2*index/80)
        z=.25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
        y=(1.15+math.sin(x*.37)*.18+max(0,-z)*.16) if east else (1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.10+max(0,-z-.3)*.23)
        for offset in [-.52,0,.52]:
            for rock,tree in zip(rocks,trees):
                if not rock.name.startswith('Cliff_Fractures'):continue
                hit=tree.ray_cast(Vector((x,-z-offset,20)),Vector((0,0,-1)))[0]
                if hit is not None and hit.z>y+.08:report['walking_intrusions'].append({'x':x,'z':z+offset,'height_above_path':hit.z-y})
(ROOT/'artifacts/cliff-form-review/contact-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not report['walking_intrusions'],report['walking_intrusions']
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
print('CLIFF_CONTACT_VERIFIED',json.dumps(report))
