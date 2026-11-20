"""Extend the existing forest floor into a rocky tip; Blender MCP authoring only."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast
from mathutils.bvhtree import BVHTree
O=ROOT/'artifacts/forest-tip-extension-review';assert not LAYOUT['reference_cape'].get('forest_tip_extension')
COL=bpy.data.collections.new('51_Forest_Tip_Extension');SCENE.collection.children.link(COL)
archive=bpy.data.collections.new('90_Before_Forest_Tip_Extension');SCENE.collection.children.link(archive)
def keep(ob):
    saved=ob.copy();saved.data=ob.data.copy();saved.name='Tip_Before_'+ob.name;archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
def archive_object(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True
edges=json.loads((O/'attachment-edges.json').read_text(encoding='utf-8'))
g=[Vector(p) for p in edges['WALK_Forest_Ground']];near=[Vector(p) for p in edges['WALK_Forest_NearSlope']]
def profile(points,y):
    if y<=points[0].y:return points[0].z
    for a,b in zip(points,points[1:]):
        if a.y<=y<=b.y:return a.z+(b.z-a.z)*(y-a.y)/(b.y-a.y)
    return points[-1].z
cap=[Vector((0,y,z)) for y,z in [(-3,4.75),(3,5.6),(6,6.12),(10,6.28),(14,6.28),(17,6.20),(19,5.55),(23,4.1),(27.5,3.0)]]
def top(x,y):
    old=profile(g,y) if y>8.08 else profile(near,y)
    return old*(1-sm(-64,-78,x))+profile(cap,y)*sm(-64,-78,x)
outer=[(-64.2,27.5,3.0),(-67.5,24.0,3.95),(-71.0,21.0,4.95),(-76.5,18.6,5.75),(-80.0,17.0,6.2),(-82.4,13.0,6.28),(-83.0,9.8,6.27),(-81.3,7.0,6.20),(-78.1,5.95,6.14),(-75.10,6.20,6.16),(-75.35,8.33,6.28),(-73.05,8.57,6.28),(-72.83,6.22,6.16),(-71.5,6.6,6.15),(-68.2,4.8,5.95),(-65.5,2.7,5.35)]
outline=g+[Vector(p) for p in outer]+near
pins={tuple(round(c,5) for c in p):p.z for p in outline}
MATS['tip_floor']=SCENE.objects['WALK_Forest_Ground'].data.materials[0]
b=Mesh('Forest_Tip_Joined_Patch');b.part(outline,tri(outline),'tip_floor',[((p.x+50)/54,(p.y+4)/40) for p in outline]);patch=b.build(True)
bm=bmesh.new();bm.from_mesh(patch.data)
bmesh.ops.subdivide_edges(bm,edges=[e for e in bm.edges if len(e.link_faces)==2],cuts=16,use_grid_fill=True)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
for v in bm.verts:
    if tuple(round(c,5) for c in v.co) not in pins:v.co.z=top(v.co.x,v.co.y)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(patch.data);bm.free();patch.data.update()
for p in patch.data.polygons:
    p.use_smooth=True
    for li in p.loop_indices:
        co=patch.data.vertices[patch.data.loops[li].vertex_index].co;patch.data.uv_layers[0].data[li].uv=((co.x+50)/54,(co.y+4)/40)
ground=SCENE.objects['WALK_Forest_Ground'];slope=SCENE.objects['WALK_Forest_NearSlope'];keep(ground);keep(slope)
bpy.ops.object.select_all(action='DESELECT')
for ob in [ground,slope,patch]:ob.hide_set(False);ob.select_set(True)
bpy.context.view_layer.objects.active=ground;bpy.ops.object.join()
bm=bmesh.new();bm.from_mesh(ground.data)
candidates=[v for v in bm.verts if v.co.x<-60.8]
bmesh.ops.remove_doubles(bm,verts=candidates,dist=.003)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free();ground.data.update()
for p in ground.data.polygons:p.use_smooth=True
floor=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
def floor_height(x,y):
    hit=floor.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
    assert hit is not None,(x,y)
    return hit.z
retired=['WALK_Cape_Neck','Cape_Neck_Rockside','WALK_Cape_Platform','Cape_Connection_Shoulder','Cape_Connection_Closed_Skirt']
for name in retired:archive_object(SCENE.objects[name])
# A continuous closed rocky body follows the new outer terrain, not a separate
# terrace attached to its edge. The existing exposed rock groups provide folds.
MATS['cape_side']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_side')][-1]
wall=Mesh('Cape_Tip_Continuous_Bedrock')
border=[g[-1]]+[Vector(p) for p in outer]+[near[0]]
for i,(p,q) in enumerate(zip(border,border[1:])):
    offset=Vector((q.y-p.y,p.x-q.x,0)).normalized()*(.12+.06*(i%3))
    midp=Vector((p.x,p.y,2.2))+offset;midq=Vector((q.x,q.y,2.2))+offset
    wall.part([p,q,midq,midp],[(0,1,2,3)],'cape_side')
    wall.part([midp,midq,(midq.x,midq.y,-.7),(midp.x,midp.y,-.7)],[(0,1,2,3)],'cape_side')
wall.build()
core=SCENE.objects['Cape_Attached_Cliff_Core'];keep(core)
for v in core.data.vertices:
    if v.co.z>3:
        hit=floor.find_nearest(Vector((v.co.x,v.co.y,6.25)))[0];v.co.z=hit.z-.025
core.data.update()
for name in LAYOUT['reference_cape']['cliff_masses']:
    ob=SCENE.objects[name];keep(ob);lo=min(v.co.z for v in ob.data.vertices);hi=max(v.co.z for v in ob.data.vertices)
    target=6.62 if name.endswith('_03') else 6.28
    for v in ob.data.vertices:v.co.z=lo+(v.co.z-lo)*(target-lo)/(hi-lo)
    ob.data.update()
# Move the existing campfire and seat onto the exposed outer rock crown.
old_fire=Vector((-76.0,13.1,4.57));new_fire=Vector((-79.0,12.8,floor_height(-79.0,12.8)+.02));delta=new_fire-old_fire
for ob in list(SCENE.objects):
    if ob.type=='MESH' and not any(c.name.startswith('90_') for c in ob.users_collection) and ob.name.startswith(('Cape_Fire_','Cape_Flame_','Cape_Smoke_','Cape_Ember_')):
        keep(ob)
        for v in ob.data.vertices:v.co+=delta
        ob.data.update()
old_seat=Vector((-72.2,13.5,4.85));new_seat=Vector((-76.0,13.5,floor_height(-76.0,13.5)+.30));delta_seat=new_seat-old_seat
for name in ['Cape_Timber_Seat','Cape_Timber_Endgrain']:
    ob=SCENE.objects[name];keep(ob)
    for v in ob.data.vertices:v.co+=delta_seat
    ob.data.update()
# Rebuild the descending stair flight to the retained sand level, with the
# same notch and width. There is no staircase between forest and rocky tip.
source=ast.parse((ROOT/'tools/blender/build_reference_cape.py').read_text(encoding='utf-8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name=='box':exec(compile(ast.Module(body=[node],type_ignores=[]),'tip_step_boxes','exec'))
MATS['cape_tread']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_tread')][-1]
step_top=Vector((-74.20,8.45,6.28));step_bottom=Vector((-73.10,-2.5,.15));axis=step_bottom-step_top;axis.z=0;length=axis.length;axis.normalize();side=Vector((-axis.y,axis.x,0));angle=math.atan2(axis.y,axis.x);steps=30;width=2.16
for name,is_support in [('WALK_Cape_Stairs',False),('Cape_Stair_Support',True)]:
    old=SCENE.objects[name];keep(old);b=Mesh(name+'_Tip_Height')
    for i in range(steps):
        h=step_top.z-(step_top.z-step_bottom.z)*i/steps;c=step_top+axis*(length*(i+.5)/steps)
        if is_support:
            c.z=-.45;box(b,c,length/steps+.006,width-.08,h-.20+.45,'cape_side',angle)
        else:
            split=[-.5,-.18,.21,.5] if i%2==0 else [-.5,-.04,.5]
            for l,r in zip(split,split[1:]):
                p=c+side*((l+r)*width*.5);p.z=h-.19
                box(b,p,length/steps+.006,(r-l)*width-.009,.19,'cape_tread',angle)
    new=b.build();old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
plants=SCENE.objects['Cape_Shore_Grass'];keep(plants);me=plants.data
for p in me.polygons:
    roots=[me.loops[li].vertex_index for li in p.loop_indices if me.uv_layers[1].data[li].uv.x<.01];assert len(roots)==2
    root=(me.vertices[roots[0]].co+me.vertices[roots[1]].co)/2
    hit=floor.ray_cast(Vector((root.x,root.y,40)),Vector((0,0,-1)))[0]
    if hit:
        for i in p.vertices:me.vertices[i].co.z+=hit.z+.014-root.z
me.update()
for name in ['forest_cape_exit','cape_neck','cape_entry']:
    a=LAYOUT['anchors'][name];a[1]=floor_height(a[0],-a[2])
LAYOUT['anchors']['cape_center']=[-77.0,floor_height(-77.0,12.8),-12.8]
LAYOUT['anchors']['cape_stair_top']=[step_top.x,step_top.z,-step_top.y]
rc=LAYOUT['reference_cape'];rc['fire_center']=[new_fire.x,new_fire.z,-new_fire.y];rc['seat_center']=[new_seat.x,new_seat.z,-new_seat.y];rc['single_shelf_height']=6.28;rc['stairs']['steps']=steps
rc['forest_tip_extension']={'date':'2026-11-19','one_joined_floor':'WALK_Forest_Ground','joined_source_meshes':['WALK_Forest_Ground','WALK_Forest_NearSlope','new tip patch'],'attachment_vertices':len(g)+len(near),'weld_distance':.003,'walking_height_continues_original_grass':True,'independent_ramp_retired':retired,'original_forest_restored':True,'floor_bounds':[-84,-5,34,40],'steps_to_sand':steps,'fire_at_rock_crown':True}
(O/'author-report.json').write_text(json.dumps(rc['forest_tip_extension'],ensure_ascii=False,indent=2),encoding='utf-8')
export('forest-ground-extends-rocky-tip')
