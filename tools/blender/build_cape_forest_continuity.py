"""Reshape one continuous forest mouth; execute only through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/cape-forest-continuity-review'
assert not LAYOUT['reference_cape'].get('forest_continuity'),'Already executed: inspect the saved revision.'
COL=bpy.data.collections.new('50_Cape_Forest_Continuity');SCENE.collection.children.link(COL)
archive=bpy.data.collections.new('90_Before_Cape_Forest_Continuity');SCENE.collection.children.link(archive)
changed=[]
def keep(ob):
    saved=ob.copy();saved.data=ob.data.copy();saved.name='Continuity_Before_'+ob.name;archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    changed.append(ob.name)
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
old_trees=[tree(SCENE.objects[n]) for n in ['WALK_Forest_Ground','WALK_Forest_NearSlope']]
old_neck=tree(SCENE.objects['WALK_Cape_Neck']);old_shoulder=tree(SCENE.objects['Cape_Connection_Shoulder'])
def center_y(x):return 13.7-1.5*sm(-61,-69,x)
def old_top(x,y):
    xx=max(-62.98,x)
    hits=[t.ray_cast(Vector((xx,y,40)),Vector((0,0,-1)))[0] for t in old_trees];hits=[h.z for h in hits if h is not None]
    if hits:return max(hits)
    return 6.28
def pure_height(x,y):
    road=4.55+1.73*sm(-70,-53.5,x)
    drop=.14*(1-sm(8,11.5,y))+.63*(1-sm(-3,8,y))
    return road+.020*(y-center_y(x))-drop
def new_top(x,y):
    old=old_top(x,y);w=(1-sm(-57,-53.5,x))*(1-sm(24,28,y))
    return old+(pure_height(x,y)-old)*w
def height_normal(x,y):
    e=.035;dx=(new_top(x+e,y)-new_top(x-e,y))/(2*e);dy=(new_top(x,y+e)-new_top(x,y-e))/(2*e)
    return Vector((-dx,-dy,1)).normalized()
def normals(ob,gate=True):
    me=ob.data;me.update();values=[]
    for p in me.polygons:
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            active=co.x<-53.5 and co.y<24 if gate else True
            values.append(tuple(height_normal(co.x,co.y)) if active else tuple(me.corner_normals[li].vector))
    me.normals_split_custom_set(values)
# Adjust the original mouth and its near bank together. Lower hidden surfaces
# by the same displacement, retaining their separation rather than creating
# two coincident sheets. Existing UV and wind data are kept verbatim.
for name in ['WALK_Forest_Ground','WALK_Forest_NearSlope']:
    ob=SCENE.objects[name];keep(ob)
    for v in ob.data.vertices:
        if v.co.x<-53.5 and v.co.y<28:v.co.z+=new_top(v.co.x,v.co.y)-old_top(v.co.x,v.co.y)
    for p in ob.data.polygons:
        if p.center.x<-53.5:p.use_smooth=True
    normals(ob)
ob=SCENE.objects['Forest_Near_Closed_Skirt'];keep(ob)
for v in ob.data.vertices:
    if v.co.x<-53.5:v.co.z+=(new_top(v.co.x,v.co.y)-old_top(v.co.x,v.co.y))*sm(-.15,3.2,v.co.z)
ob.data.update()
# The neck has the same height field and boundary normals as the old land.
ob=SCENE.objects['WALK_Cape_Neck'];keep(ob)
for v in ob.data.vertices:v.co.z=new_top(v.co.x,v.co.y)
for p in ob.data.polygons:p.use_smooth=True
normals(ob,False)
ob=SCENE.objects['Cape_Neck_Rockside'];keep(ob)
for v in ob.data.vertices:
    if v.co.z>3:v.co.z=new_top(v.co.x,v.co.y)-.010
ob.data.update()
# Smooth the near wedge into both terrain edges, with a rounded toe remaining
# below the walking bench. Its eastern boundary uses the same new height.
ob=SCENE.objects['Cape_Connection_Shoulder'];keep(ob)
NX=40;NY=56;assert len(ob.data.vertices)==(NX+1)*(NY+1)
for j in range(NY+1):
    s=j/NY
    for i in range(NX+1):
        t=i/NX;v=ob.data.vertices[j*(NX+1)+i]
        start_y=-2.92+(8.60+2.92)*s
        begin=new_top(-63.04,start_y)
        end=1.10+(4.45-1.10)*sm(0,.93,s)
        z=begin*(1-sm(0,1,t))+end*sm(0,1,t)
        upper=sm(.78,1,s)
        z=z*(1-upper)+new_top(v.co.x,v.co.y)*upper
        v.co.z=z
ob.data.update()
new_shoulder=tree(ob)
# Match the shared normal only at the upper and eastern joins. Inside the
# curved near wedge, retain its own slope normals.
me=ob.data;values=[]
for p in me.polygons:
    for li in p.loop_indices:
        co=me.vertices[me.loops[li].vertex_index].co
        values.append(tuple(height_normal(co.x,co.y)) if co.x>-63.12 or co.y>8.6 else tuple(me.corner_normals[li].vector))
me.normals_split_custom_set(values)
ob=SCENE.objects['Cape_Connection_Closed_Skirt'];keep(ob)
for v in ob.data.vertices:
    prior=old_shoulder.find_nearest(v.co)[0]
    if prior is not None and (prior.xy-v.co.xy).length<.015 and abs(prior.z-v.co.z)<.08:
        hit=new_shoulder.ray_cast(Vector((v.co.x,v.co.y,40)),Vector((0,0,-1)))[0]
        if hit is None:hit=new_shoulder.find_nearest(Vector((v.co.x,v.co.y,prior.z)))[0]
        if hit:v.co.z=hit.z
ob.data.update()
# Blend the inner rim of the existing rock shelf into the same shallow rise.
ob=SCENE.objects['WALK_Cape_Platform'];keep(ob)
for v in ob.data.vertices:
    w=sm(-71.0,-68.3,v.co.x)*sm(9.8,11.4,v.co.y)
    v.co.z+=(new_top(v.co.x,v.co.y)-v.co.z)*w
ob.data.update();platform=tree(ob)
ob=SCENE.objects['Cape_Attached_Cliff_Core'];keep(ob)
for v in ob.data.vertices:
    if v.co.z>3:
        hit=platform.find_nearest(Vector((v.co.x,v.co.y,4.55)))[0]
        if hit:v.co.z=hit.z-.027
ob.data.update()
new_floors=[tree(SCENE.objects[n]) for n in ['WALK_Forest_Ground','WALK_Forest_NearSlope','WALK_Cape_Neck','WALK_Cape_Platform']]
def actual_height(x,y):
    hits=[t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0] for t in new_floors];hits=[h.z for h in hits if h is not None]
    assert hits,(x,y)
    return max(hits)
# Existing roots are moved as coherent culm/leaf groups. The first two become
# a sparse, slightly lower entry; no additional full bamboo grove is added.
bindings=LAYOUT['forest_extension']['layer_roles']['wind_bindings'];root_report={}
for name,data in bindings.items():
    if data['root'][0]>=-52:continue
    ob=SCENE.objects[name];keep(ob);old=Vector((data['root'][0],-data['root'][2],data['root'][1]));new=old.copy();scale=1.0
    if name.endswith('_00'):new.x=-62.1;new.y=16.55;scale=.82
    elif name.endswith('_01'):new.x=-59.85;new.y=17.05;scale=.90
    new.z=actual_height(new.x,new.y)-.045
    for v in ob.data.vertices:v.co=new+(v.co-old)*scale
    ob.data.update();data['root']=[new.x,new.z,-new.y];data['height']*=scale
    root_report[name]={'before':list(old),'after':list(new),'scale':scale,'seed':data['seed'],'amplitude':data['amplitude']}
# Move only plants that already attach to the reshaped mouth; identify actual
# roots through their zero wind weight, preserving tip weight and whole blades.
ob=SCENE.objects['Cape_Shore_Grass'];keep(ob);me=ob.data
all_trees=new_floors+[new_shoulder]+[tree(o) for o in bpy.data.collections['49_Reference_Cape'].objects if o.type=='MESH' and o.name.startswith('Cape_Cliff_')]
for p in me.polygons:
    roots=[me.loops[li].vertex_index for li in p.loop_indices if me.uv_layers[1].data[li].uv.x<.01];assert len(roots)==2
    root=(me.vertices[roots[0]].co+me.vertices[roots[1]].co)/2
    if root.x<-71:continue
    hits=[t.ray_cast(Vector((root.x,root.y,40)),Vector((0,0,-1)))[0] for t in all_trees];hits=[h for h in hits if h is not None]
    if hits:
        delta=max(h.z for h in hits)+.014-root.z
        for i in p.vertices:me.vertices[i].co.z+=delta
me.update()
for name in ['forest_cape_exit','cape_neck','cape_entry']:
    a=LAYOUT['anchors'][name];a[1]=actual_height(a[0],-a[2]);A[name]=Vector((a[0],-a[2],a[1]))
LAYOUT['reference_cape']['forest_continuity']={'date':'2026-11-19','range':[-70,-53.5],'height_difference_spread_m':16.5,'world_floor_bounds':[-74,-5,24,33],'changed_meshes':changed,'archive':archive.name,'coherent_root_changes':root_report,'shared_height_and_normal_field':True,'forest_uv_preserved':True,'single_shelf_and_stairs_retained':True}
(REVIEW/'author-report.json').write_text(json.dumps(LAYOUT['reference_cape']['forest_continuity'],ensure_ascii=False,indent=2),encoding='utf-8')
export('cape-forest-continuity')
