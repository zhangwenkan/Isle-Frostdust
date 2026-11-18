"""Refine the existing walking bench, banks and rocks through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/near-mid-depth-review'
assert not LAYOUT['forest_extension'].get('near_mid_depth'),'Already authored: inspect before making another pass.'
COL=bpy.data.collections.new('48_Near_Middle_Depth');SCENE.collection.children.link(COL)
ARCH=bpy.data.collections.new('90_Before_Near_Middle_Depth');SCENE.collection.children.link(ARCH);ARCH.hide_render=True
changed=[]
def keep(ob):
    saved=ob.copy();saved.data=ob.data.copy();saved.name='NearMid_Before_'+ob.name;ARCH.objects.link(saved);saved.hide_render=True;saved.hide_set(True)
    COL.objects.link(ob);changed.append(ob.name)

route=[A[k] for k in ['forest_west_entry','forest_west_gate','forest_west_light','forest_west_mid','forest_west_shade','forest_west_end']]
def center_y(x):
    for a,b in zip(route,route[1:]):
        if min(a.x,b.x)<=x<=max(a.x,b.x):
            return a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x)
    return route[-1].y if x<route[-1].x else route[0].y
def extent(x):return sm(-55,-46,x)*(1-sm(-20,-14.5,x))
def rim(x):return 1.10+.15*math.sin((x+37)*.34)+.07*math.sin((x+21)*.67)
def terrain_delta(x,y):
    w=extent(x)
    if w==0:return 0.0
    d=center_y(x)-y
    # The original foot corridor stays untouched. One irregular earth edge
    # descends to a lower, connected grass bank rather than separate pillars.
    drop=.36+.12*math.exp(-((x+33)/6.2)**2)+.10*math.exp(-((x+23)/4.5)**2)
    front=-drop*sm(rim(x)-.12,rim(x)+.24,d)-.23*sm(3.2,5.9,d)
    shoulder=.22*math.exp(-((y-(7.3+.5*math.sin((x+35)*.18)))/1.0)**2)*math.exp(-((x+33)/11)**2)
    lower=-.19*sm(6.1,6.7,d)*math.exp(-((x+33)/8.5)**2)
    rear=.24*sm(.85,1.55,-d)*(1-sm(2.1,3.2,-d))
    return w*(front+shoulder+lower+rear)

floors=['WALK_Forest_Ground','WALK_Forest_NearSlope']
for name in floors:
    ob=SCENE.objects[name];keep(ob);me=ob.data
    if name=='WALK_Forest_Ground':
        bm=bmesh.new();bm.from_mesh(me)
        edges=[e for e in bm.edges if extent((e.verts[0].co.x+e.verts[1].co.x)*.5)>.05 and
               abs(center_y((e.verts[0].co.x+e.verts[1].co.x)*.5)-(e.verts[0].co.y+e.verts[1].co.y)*.5-rim((e.verts[0].co.x+e.verts[1].co.x)*.5))<.6]
        bmesh.ops.subdivide_edges(bm,edges=edges,cuts=2,use_grid_fill=True)
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    for v in me.vertices:v.co.z+=terrain_delta(v.co.x,v.co.y)
    me.update()
    if name=='WALK_Forest_Ground':
        soil_slot=len(me.materials);me.materials.append(MATS['soil'])
        for p in me.polygons:
            c=p.center;d=center_y(c.x)-c.y
            cut=extent(c.x)>.15 and .7<d<1.65 and abs(p.normal.z)<.78
            if cut:
                p.material_index=soil_slot;p.use_smooth=False
                for li in p.loop_indices:
                    co=me.vertices[me.loops[li].vertex_index].co;me.uv_layers[0].data[li].uv=(co.x*.30,co.z*.55)

newtrees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in [SCENE.objects[n] for n in floors]]
def ground(x,y):
    hits=[tree.ray_cast(Vector((x,y,35)),Vector((0,0,-1)))[0] for tree in newtrees]
    vals=[h.z for h in hits if h is not None];assert vals,(x,y,'outside imported forest ground')
    return max(vals)
def components(me):
    adjacent=[[] for _ in me.vertices]
    for e in me.edges:
        a,b=e.vertices;adjacent[a].append(b);adjacent[b].append(a)
    seen=set()
    for start in range(len(me.vertices)):
        if start in seen:continue
        group=[];stack=[start];seen.add(start)
        while stack:
            v=stack.pop();group.append(v)
            for other in adjacent[v]:
                if other not in seen:seen.add(other);stack.append(other)
        yield group
for name in ['Forest_Grass_Banks','Forest_Grass_Understory','Forest_Grass_NearPatches','WALK_Forest_Paving']:
    ob=SCENE.objects[name];keep(ob)
    for group in components(ob.data):
        points=[ob.data.vertices[i].co for i in group];bottom=min(p.z for p in points)
        roots=[p for p in points if p.z<bottom+.025];root=sum(roots,Vector())/len(roots)
        dz=terrain_delta(root.x,root.y)
        for i in group:ob.data.vertices[i].co.z+=dz
    ob.data.update()
skirt=SCENE.objects['Forest_Near_Closed_Skirt'];keep(skirt)
for v in skirt.data.vertices:v.co.z+=terrain_delta(v.co.x,v.co.y)
skirt.data.update()

# Four deliberate cut-rock profiles. They replace the existing flat stones,
# stay embedded in the revised bank, and retain all existing paint materials.
rock_specs=[
    ('Forest_Rock_00',-19.35,15.12,2.15,1.48,1.04,-.12,[.66,.87,.95,.82,.74,.62,.58,.61]),
    ('Forest_Rock_02',-29.5,10.18,2.10,1.42,.91,.22,[.62,.79,.94,.81,.72,.62,.56,.59]),
    ('Forest_Rock_03',-35.95,15.20,2.35,1.58,1.15,-.27,[.73,.88,.97,.89,.67,.58,.56,.64]),
    ('Forest_Rock_04',-42.2,16.25,2.72,1.76,1.22,.15,[.68,.83,.96,.90,.78,.62,.57,.62]),
]
rock_report=[]
outline=[(-1,-.35),(-.62,-.87),(.51,-.74),(1,-.17),(.75,.73),(.08,1),(-.81,.62),(-1,.12)]
for name,x,y,width,depth,h,angle,heights in rock_specs:
    original=SCENE.objects[name];keep(original)
    base=ground(x,y);cs=math.cos(angle);sn=math.sin(angle)
    def point(px,py,z):return Vector((x+px*width*.5*cs-py*depth*.5*sn,y+px*width*.5*sn+py*depth*.5*cs,z))
    lower=[point(px,py,0) for px,py in outline]
    for p in lower:p.z=ground(p.x,p.y)-.24
    upper=[point(px*.88+.045,py*.82+.03,base+h*heights[i]-.06) for i,(px,py) in enumerate(outline)]
    builder=Mesh(name+'_Cut')
    for i in range(8):builder.part([lower[i],lower[(i+1)%8],upper[(i+1)%8],upper[i]],[(0,1,2,3)],['rock_b','rock_c','rock_a','rock_b','rock_c','rock_b','rock_a','rock_b'][i])
    top=upper+[point(-.17,-.07,base+h-.06),point(.16,.34,base+h*.84-.06)]
    builder.part(top,[(0,1,8),(1,2,3,8),(3,4,9,8),(4,5,9),(5,6,7,9),(7,0,8,9)],'rock_top')
    builder.part(lower,[tuple(reversed(t)) for t in tri(lower)],'rock_c')
    built=builder.build();original.data=built.data;bpy.data.objects.remove(built,do_unlink=True)
    original['near_mid_cut']='embedded cut stone with uneven sloping top and steep visible sides'
    rock_report.append({'name':name,'center':[x,y,base],'width':width,'depth':depth,'height':h,'embed':.24,'top_planes':6})

# Move the existing three near culms and their own attached leaf cards.
# No extra row is created; original UV2 wind weights and random seeds remain.
wind=LAYOUT['forest_extension']['layer_roles']['wind_bindings'];root_changes=[]
for index,(x,y) in enumerate([(-45.5,5.0),(-33.0,4.8),(-22.8,6.1)]):
    name='Forest_Bamboo_Role_Front_%02d'%index
    old=Vector(wind[name]['root']);old=Vector((old.x,-old.z,old.y))
    new=Vector((x,y,ground(x,y)-.025));shift=new-old
    for ob_name in [name,'Forest_Bamboo_Role_FrontLeaf_%02d'%index]:
        ob=SCENE.objects[ob_name];keep(ob)
        for v in ob.data.vertices:v.co+=shift
        ob.data.update();wind[ob_name]['root']=[new.x,new.z,-new.y]
    root_changes.append({'object':name,'before':list(old),'after':list(new),'shift':list(shift)})

LAYOUT['forest_extension']['near_mid_depth']={'collection':COL.name,'changed_objects':changed,'foot_corridor':'Original route and center heights retained','rocks':rock_report,'near_culms':root_changes,'intent':'Readable walking bench, attached banks, cut-rock volume and close foreground parallax'}
(REVIEW/'author-pass1.json').write_text(json.dumps(LAYOUT['forest_extension']['near_mid_depth'],indent=2),encoding='utf-8')
export('near-middle-depth')
