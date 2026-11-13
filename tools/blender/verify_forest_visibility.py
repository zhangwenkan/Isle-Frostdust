"""Read-only checks in Blender MCP for the revised creek-side composition."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-visibility-review'
scene=bpy.data.scenes['Island_Refined']
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
    for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
    for uv in o.data.uv_layers:
        for d in uv.data:h.update(str(tuple(d.uv)).encode())
    h.update(str(o.matrix_world).encode());return h.hexdigest()
before=json.loads((O/'baseline-signatures.json').read_text());after={o.name:signature(o) for o in active}
changes=[name for name in before if name in after and before[name]!=after[name]]
unchanged=[name for name in before if name in after and before[name]==after[name]]
archived=[name for name in before if name not in after]
auth=json.loads((O/'authoring.json').read_text())
unexpected=set(changes)-set(auth['changed_originals'])
assert not unexpected,unexpected
ground=[o for o in active if o.name in ['Fish_West_Continuous_Land','ForestVisibility_Near_Bank','ForestVisibility_Opposite_Rock_Slope']]
trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in ground]
def ground_at(x,z):
    hits=[t.ray_cast(Vector((x,-z,60)),Vector((0,0,-1)))[0] for t in trees]
    return max((p.z for p in hits if p is not None),default=None)
roots=[];mesh_checks=[]
for ob in active:
    if not ob.name.startswith('ForestVisibility'):continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    check={'object':ob.name,'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'uv':[u.name for u in ob.data.uv_layers]}
    bm.free();mesh_checks.append(check)
    assert check['zero_area_faces']==0,check
    open_surface=ob.name in ['ForestVisibility_Creek','ForestVisibility_Creek_Waterfall','ForestVisibility_Creek_Foam']
    if not open_surface and not any(k in ob.name for k in ['Bamboo','Grass']):assert check['non_manifold_edges']==0,check
    if 'Bamboo' not in ob.name:continue
    assert len(ob.data.uv_layers)>=2,ob.name
    for x,y,z in json.loads(ob['root_positions_godot']):
        actual=ground_at(x,z);assert actual is not None,ob.name
        nearest=min((ob.matrix_world@v.co-Vector((x,-z,y))).length for v in ob.data.vertices)
        root={'object':ob.name,'support_offset':y-actual,'nearest_vertex':nearest}
        assert abs(root['support_offset']+.06)<.02,root
        assert nearest<.15,root
        roots.append(root)
profile={};exec(compile((R/'tools/cape_compact_profile.py').read_text(encoding='utf-8'),'compact','exec'),profile)
route={};exec(compile((R/'tools/cape_road_profile.py').read_text(encoding='utf-8'),'route','exec'),route)
def smooth(a,b,v):
    t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
walk=[]
for i in range(194):
    x=-15.2+i*.10;sx=profile['source_x'](x);z=route['route'](sx)
    for dz in [-.48,0,.48]:
        pz=z+dz;y=route['deform_height'](sx,pz,route['old_height'](sx,pz))
        y-=max(0,y-1.5)*.4*smooth(-15.1,-12.2,x)*(1-smooth(.5,4,x))
        actual=ground_at(x,pz)
        assert actual is not None,(x,pz)
        walk.append(abs(actual-y))
assert max(walk)<.14,max(walk)
water=scene.objects['ForestVisibility_Creek'];water_points=[water.matrix_world@v.co for v in water.data.vertices]
fall=scene.objects['ForestVisibility_Creek_Waterfall'];fall_points=[fall.matrix_world@v.co for v in fall.data.vertices]
water_tree=BVHTree.FromPolygons(water_points,[tuple(p.vertices) for p in water.data.polygons])
bridge_top=max((o.matrix_world@v.co).z for o in active if o.name.startswith('Bridge_Plank_') for v in o.data.vertices)
assert min(p.z for p in water_points)>bridge_top+.30,(min(p.z for p in water_points),bridge_top)
height_comparison=[]
for x in [-15.2,-14.2,-12.8,-11.0,-6.8,-2.5,1.5]:
    source_x=profile['source_x'](x);path_z=route['route'](source_x)
    ground_y=ground_at(x,path_z)
    hits=[water_tree.ray_cast(Vector((x,-z,60)),Vector((0,0,-1)))[0] for z in [-4.5-i*.10 for i in range(85)]]
    water_y=max(p.z for p in hits if p is not None)
    assert water_y>ground_y+.10,(x,water_y,ground_y)
    height_comparison.append({'x':x,'water_y':water_y,'path_y':ground_y,'difference':water_y-ground_y})
assert abs(max(p.z for p in fall_points)-min(p.z for p in water_points))<.04
assert abs(min(p.z for p in fall_points)-.035)<.015
waterfall_report={'creek_y_range':[min(p.z for p in water_points),max(p.z for p in water_points)],'bridge_top_y':bridge_top,'fall_y_range':[min(p.z for p in fall_points),max(p.z for p in fall_points)],'water_above_foreground_path':height_comparison}
result={'unchanged_originals':len(unchanged),'changed_originals':changes,'archived':archived,'new_meshes':mesh_checks,'roots':roots,'walking_samples':len(walk),'max_walk_height_error_m':max(walk),'root_support_offset_range':[min(r['support_offset'] for r in roots),max(r['support_offset'] for r in roots)],'waterfall':waterfall_report}
(O/'asset-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('FOREST_VERIFIED',len(unchanged),'unchanged',len(changes),'changed','max path error',max(walk),'roots',len(roots))
