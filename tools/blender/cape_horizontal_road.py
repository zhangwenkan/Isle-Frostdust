"""Blender MCP: shape a level opening tread aligned with the side-view actor.
Keep the cape rim, campfire and other scene assets; conform affected grass roots.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/cape-road-alignment-review'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
profile={};exec(compile((ROOT/'tools/cape_road_profile.py').read_text(encoding='utf-8'),'cape_road_profile.py','exec'),profile)
route=profile['route'];height=profile['deform_height'];old_height=profile['old_height']
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def active():return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def digest(ob):
    m=ob.data
    return hashlib.sha256(json.dumps({'v':[list(v.co) for v in m.vertices],'p':[list(p.vertices) for p in m.polygons],'n':[list(n.vector) for n in m.corner_normals],'uv':[[list(d.uv) for d in u.data] for u in m.uv_layers],'matrix':[list(r) for r in ob.matrix_world]}).encode()).hexdigest()
before_file=OUT/'geometry-before.json'
if not before_file.exists():before_file.write_text(json.dumps({o.name:digest(o) for o in active()},indent=2),encoding='utf-8')
before=json.loads(before_file.read_text(encoding='utf-8'))
archive=bpy.data.collections.get('90_Before_Cape_Horizontal_Road')
if archive is None:
    archive=bpy.data.collections.new('90_Before_Cape_Horizontal_Road');scene.collection.children.link(archive)
archive.hide_render=True
def baseline(ob):
    name='RoadBaseline_'+ob.name;saved=bpy.data.objects.get(name)
    if saved is None:
        saved=ob.copy();saved.data=ob.data.copy();saved.name=name;archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    return saved
land=scene.objects['Fish_West_Continuous_Land'];saved=baseline(land)
land.data=saved.data.copy();me=land.data;inverse=land.matrix_world.inverted()
old_normals=[n.vector.copy() for n in me.corner_normals]
old_tree=BVHTree.FromPolygons([saved.matrix_world@v.co for v in saved.data.vertices],[tuple(p.vertices) for p in saved.data.polygons])
top_ids={i for p in me.polygons if p.material_index==0 for i in p.vertices}
changed_ids=set();largest=0.
for v in me.vertices:
    world=land.matrix_world@v.co
    if world.x>=-12.5:continue
    hit=old_tree.ray_cast(Vector((world.x,world.y,25)),Vector((0,0,-1)))[0]
    if hit is None:continue
    weight=1. if v.index in top_ids else 1-profile['smooth'](.05,1.0,hit.z-world.z)
    dz=(height(world.x,-world.y,hit.z)-hit.z)*weight
    if abs(dz)<1e-7:continue
    world.z+=dz;v.co=inverse@world;changed_ids.add(v.index);largest=max(largest,abs(dz))
me.normals_split_custom_set([(0.,0.,0.)]*len(me.loops));me.update()
new_normals=[n.vector.copy() for n in me.corner_normals]
normals=[]
for p in me.polygons:
    change=any(i in changed_ids for i in p.vertices)
    for li in p.loop_indices:
        normal=new_normals[li] if change else old_normals[li]
        if change and p.material_index==1:normal=normal.lerp(p.normal,.64).normalized()
        normals.append(tuple(normal))
me.normals_split_custom_set(normals);me.update()
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])

grass_reports=[]
for ob in active():
    if not (ob.name.startswith('Coast_Low_Grass_') or ob.name=='InkSample_Path_Grass'):continue
    if min((ob.matrix_world@v.co).x for v in ob.data.vertices)>-12.5:continue
    saved=baseline(ob);ob.data=saved.data.copy();inv=ob.matrix_world.inverted();n=4 if ob.name=='InkSample_Path_Grass' else 8
    moves=[];clearance=[]
    for start in range(0,len(ob.data.vertices),n):
        ids=list(range(start,min(start+n,len(ob.data.vertices))))
        points=[ob.matrix_world@ob.data.vertices[i].co for i in ids]
        root=points[0] if n==4 else (points[0]+points[1])*.5
        oldhit=old_tree.ray_cast(Vector((root.x,root.y,25)),Vector((0,0,-1)))[0]
        newhit=tree.ray_cast(Vector((root.x,root.y,25)),Vector((0,0,-1)))[0]
        if oldhit is None or newhit is None:continue
        dz=newhit.z-oldhit.z
        # Relocate only blades crossed by the new tread to its outer grass shoulder.
        dx=0.;dy=0.
        z=-root.y;relative=z-route(root.x)
        if -23.2<root.x<-12.8 and abs(relative)<profile['road_half_width'](root.x)+.12:
            side=1 if relative>=0 else -1
            target_z=route(root.x)+side*(profile['road_half_width'](root.x)+.16+.08*math.sin(start*.21))
            dy=-target_z-root.y
            shifted=tree.ray_cast(Vector((root.x,root.y+dy,25)),Vector((0,0,-1)))[0]
            if shifted:dz=shifted.z-oldhit.z
        if abs(dz)+abs(dy)<1e-7:continue
        shift=Vector((0,dy,dz))
        for idx,p in zip(ids,points):ob.data.vertices[idx].co=inv@(p+shift)
        moves.append(list(shift));clearance.append(root.z+dz-newhit.z if dy==0 else root.z+dz-shifted.z)
    ob.data.update()
    grass_reports.append({'name':ob.name,'moved_blades':len(moves),'max_vertical_shift':max([abs(s[2]) for s in moves],default=0),'max_horizontal_shift':max([abs(s[1]) for s in moves],default=0),'root_clearance_min_max':[min(clearance,default=0),max(clearance,default=0)]})

samples=[]
for i in range(84):
    x=-20.7+i*.1
    for offset in [-.55,0,.55]:
        z=route(x)+offset;p=tree.ray_cast(Vector((x,-z,25)),Vector((0,0,-1)))[0]
        assert p is not None,('route outside land',x,z)
        runtime=height(x,z,old_height(x,z));samples.append({'x':x,'offset':offset,'error_m':runtime-p.z})
worst=max(samples,key=lambda s:abs(s['error_m']))
# Add soft contact UVs to the existing Blender-authored footprint disc.
# Runtime may orient/scale this imported asset; no new geometry is made in Godot.
shadow=scene.objects['ContactShadow'];saved=baseline(shadow);shadow.data=saved.data.copy()
uv=shadow.data.uv_layers[0] if shadow.data.uv_layers else shadow.data.uv_layers.new(name='ContactUV')
uv.name='ContactUV'
coords=[v.co.copy() for v in shadow.data.vertices]
lo=[min(p[a] for p in coords) for a in range(3)];hi=[max(p[a] for p in coords) for a in range(3)]
axes=sorted(range(3),key=lambda a:hi[a]-lo[a],reverse=True)[:2]
for loop in shadow.data.loops:
    p=shadow.data.vertices[loop.vertex_index].co
    uv.data[loop.index].uv=tuple((p[a]-lo[a])/(hi[a]-lo[a]) for a in axes)
shadow.data.update()
after={o.name:digest(o) for o in active()};changed=[n for n in before if n in after and before[n]!=after[n]]
assert all(n in ['Fish_West_Continuous_Land','ContactShadow','InkSample_Path_Grass'] or n.startswith('Coast_Low_Grass_') for n in changed),changed
report={'changed_meshes':changed,'unchanged_meshes':len(before)-len(changed),'changed_terrain_vertices':len(changed_ids),'max_terrain_height_change':largest,'grass':grass_reports,'walk_samples':len(samples),'worst_walk_surface_error':worst,'profile':{'start':profile['START'],'start_z':profile['START_Z'],'start_height':profile['START_Y'],'join':[-18.5,-12.5],'opening_direction_xz':[9,-5]},'campfire_unchanged':all(before[n]==after[n] for n in before if n.startswith('Campfire_'))}
(OUT/'blender-authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert abs(worst['error_m'])<.10,worst
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
print('HORIZONTAL_CAPE_ROAD_EXPORTED',json.dumps(report))
