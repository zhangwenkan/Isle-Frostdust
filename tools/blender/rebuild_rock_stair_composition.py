"""Hand-composed plane cuts, stair notch and interlocking rock feet, via MCP.

Primary rocks use individually specified fracture planes, never ring profiles.
This first pass saves a grey authoring preview before surface painting/export.
"""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
import array
from mathutils.bvhtree import BVHTree
R=ROOT/'artifacts/rock-stair-composition-review';R.mkdir(exist_ok=True)
assert not LAYOUT['reference_cape'].get('rock_stair_composition'), 'Already built: inspect and refine existing pass.'
COL=bpy.data.collections.new('55_Rock_Stair_Composition');SCENE.collection.children.link(COL)
ARCH=bpy.data.collections.new('90_Before_Rock_Stair_Composition');SCENE.collection.children.link(ARCH)
state={'collection':COL.name,'archive':ARCH.name,'created':[],'replaced':[],'retired':[],'rock_roles':{},'scope':'Rock/stair/platform sample. No passage or motion tests.'}
LAYOUT['reference_cape']['rock_stair_composition']=state

def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def keep(o):
    if o.name in state['replaced']:return
    cp=o.copy();cp.data=o.data.copy();cp.name='Composition_Before_'+o.name;ARCH.objects.link(cp);cp.hide_set(True);cp.hide_render=True;state['replaced'].append(o.name)
def retire(o):
    state['retired'].append(o.name)
    for c in list(o.users_collection):c.objects.unlink(o)
    ARCH.objects.link(o);o.hide_set(True);o.hide_render=True
def adopt(name,new):
    old=SCENE.objects.get(name)
    if old:
        keep(old);old.data=new.data;bpy.data.objects.remove(new,do_unlink=True);return old
    new.name=name;state['created'].append(name);return new
def simple_mat(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.88
    return m
GRAY=simple_mat('StrictCoast_Composition_Gray',(.33,.34,.34))

top=Vector((-63.3,8.8,3.8564));bottom=Vector((-62.5,4.0,.15));direction=bottom-top;direction.z=0;run=direction.length;direction.normalize();side=Vector((-direction.y,direction.x,0));WIDTH=2.25

def clip(bm,point,normal):
    res=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
    edges=[e for e in res['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
    if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))

def solid_from_cuts(name,center,size,angle,cuts,role,notch=None,wear=.06):
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
    for normal,distance in cuts:
        n=Vector(normal);clip(bm,n*distance/n.length_squared,n)
    w,d,h=size;c=Vector(center);cs=math.cos(angle);sn=math.sin(angle)
    for v in bm.verts:
        x=v.co.x*w*.5;y=v.co.y*d*.5;z=(v.co.z+1)*h*.5
        v.co=Vector((c.x+x*cs-y*sn,c.y+x*sn+y*cs,c.z+z))
    if notch=='left':clip(bm,top-side*(WIDTH*.5+.055),side)
    elif notch=='right':clip(bm,top+side*(WIDTH*.5+.055),-side)
    # Actual shared-edge topology. Wear is deliberately selective and varies
    # by edge orientation/position; no identical bevel ring around every rock.
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    edges=[e for e in bm.edges if e.is_manifold and e.calc_face_angle()>.46 and (e.verts[0].co.z+e.verts[1].co.z)*.5>c.z+.22]
    if edges:bmesh.ops.bevel(bm,geom=edges,offset=wear,segments=2,affect='EDGES',clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.update();me.materials.append(GRAY)
    o=bpy.data.objects.new(name,me);COL.objects.link(o)
    for p in me.polygons:p.use_smooth=False
    o=adopt(name,o);state['rock_roles'][o.name]=role;return o

# Each large stone has its own designed plane intersections and shoulder.
# Left rear wraps the camp; front principal slab has a slanted broken roof.
specs=[
 ('Sea_West',(-66.7,12.2,.45),(3.8,4.0,3.65),.08,[((-.22,.09,1),.83),((-1,-.1,.11),.9),((1,.28,.18),.97),((-.2,-1,.16),.86),((-.8,.65,.22),1.08),((.75,-.9,.48),1.16),((-.55,-.8,-.35),1.22)],'rear sea shoulder',None,.085),
 ('Sea_Front',(-66.05,8.45,.78),(3.95,3.4,3.30),-.10,[((.20,-.12,1),.84),((-.09,-1,.22),.91),((-1,.13,-.16),.94),((1,.12,.07),.90),((-.8,-.65,.27),1.10),((.85,-.7,.50),1.12),((-.65,.8,.34),1.12),((.2,.3,-1),.90)],'principal left fractured block','left',.09),
 ('Stair_Left',(-65.25,5.95,.10),(3.0,2.65,2.68),.13,[((-.25,.13,1),.87),((-.05,-1,.12),.91),((-.85,-.7,.4),1.01),((.8,-.6,.35),1.12),((-1,.25,-.10),.9),((.75,.75,.3),1.22)],'left lower shoulder','left',.055),
 ('Stair_Right',(-60.65,8.60,.72),(4.00,3.9,3.25),.09,[((-.18,.16,1),.85),((.18,-1,.16),.89),((1,.2,-.1),.92),((-.85,-.6,.30),1.09),((.90,-.75,.53),1.13),((.70,.8,.19),1.22),((.25,.0,-1),.94)],'principal right counterweight','right',.08),
 ('Root_West',(-64.1,16.75,3.53),(3.55,2.8,1.75),-.11,[((.22,.07,1),.83),((-.8,-.7,.26),1.08),((.85,-.6,.40),1.08),((-.85,.75,.16),1.17),((1,.03,.12),.94)],'embedded high rooted shoulder',None,.065),
 ('Root_Mid',(-60.95,16.9,3.43),(2.75,2.50,1.25),.18,[((-.25,-.11,1),.85),((-.8,-.7,.19),1.08),((.8,.7,.36),1.12),((.13,-1,.04),.94),((1,-.15,.20),.95)],'low rooted companion',None,.04),
 ('Root_East',(-58.35,17.1,3.45),(2.90,2.45,1.17),-.21,[((.18,.17,1),.80),((-1,.02,.12),.90),((.8,-.7,.28),1.06),((-.6,-.8,.41),1.10),((.8,.75,-.12),1.13)],'far rooted shelf',None,.05),
 ('Toe_West',(-67.35,6.00,-.05),(2.15,2.15,1.5),-.27,[((-.27,.18,1),.78),((-.8,-.7,.2),1.01),((.8,-.65,.33),1.08),((-1,.04,-.1),.86),((.55,.8,.45),1.02)],'outer supporting foot',None,.055),
 ('Toe_West_Inset',(-65.70,3.90,-.03),(2.5,2.2,1.78),.14,[((.24,-.09,1),.85),((-.8,-.6,.35),1.05),((.8,-.75,.19),1.05),((.75,.8,.40),1.17),((-.15,-1,-.05),.9)],'left foot beside lower stairs','left',.065),
 ('Toe_Right',(-60.65,4.6,-.02),(3.00,2.55,1.95),-.19,[((-.21,.09,1),.81),((.05,-1,.15),.88),((.8,-.6,.30),1.09),((-.7,-.85,.32),1.11),((1,.22,-.2),.91),((.8,.7,.25),1.17)],'right lower stair enclosure','right',.06),
 ('Toe_Right_Low',(-60.80,2.65,-.05),(1.90,1.70,.9),.23,[((.26,-.19,1),.81),((-.8,-.7,.20),1.02),((.75,-.85,.18),1.08),((1,.18,.07),.86),((.75,.65,.35),1.13)],'subordinate sand foot','right',.045),
 ('Near_Upper',(-58.6,5.85,.40),(4.1,3.80,2.93),-.16,[((.18,.11,1),.86),((-.14,-1,.14),.88),((1,.22,-.10),.9),((-.7,-.8,.19),1.12),((.85,-.7,.48),1.13),((.8,.75,.19),1.15)],'broad right bank shoulder',None,.075),
 ('Near_Lower',(-56.70,3.70,.10),(3.85,3.75,2.35),.16,[((-.19,-.16,1),.83),((.13,-1,.07),.92),((1,.05,-.12),.94),((-.8,-.7,.34),1.10),((.8,-.75,.42),1.05),((.8,.8,.12),1.14)],'lower overlapping bank ledge',None,.065),
 ('Near_Seam',(-54.90,2.65,.05),(3.0,3.7,2.88),-.12,[((.16,.15,1),.84),((-.1,-1,.08),.9),((1,-.04,.10),.94),((-.7,-.8,.35),1.06),((.75,-.75,.25),1.14)],'bank return into original slope',None,.055)
]
new_rocks=[]
for suffix,center,size,angle,cuts,role,notch,wear in specs:new_rocks.append(solid_from_cuts('Cape_Strict_Rock_'+suffix,center,size,angle,cuts,role,notch,wear))
for n in ['Cape_Strict_Rock_Root_Embedded','Cape_Strict_Attached_Exposure_0','Cape_Strict_Attached_Exposure_1','Cape_Strict_Attached_Exposure_2','Cape_Strict_Near_Ledges','Cape_Strict_Near_Ledge_Moss']:
    if SCENE.objects.get(n) and live(SCENE.objects[n]):retire(SCENE.objects[n])

# One narrow incision in each principal face: true shallow wedge geometry,
# not a repeated decorative fracture on every stone.
def incision(o,offset,length,width):
    face=max([p for p in o.data.polygons if p.normal.y<-.68 and p.area>.3],key=lambda p:p.area,default=None)
    if not face:return
    normal=face.normal.normalized();center=face.center+Vector(offset);along=normal.cross(Vector((0,0,1))).normalized();along=(along+Vector((0,0,-.28))).normalized();across=normal.cross(along).normalized()
    pts=[]
    for t,w in [(-.5,width),(.5,width*.6)]:
        base=center+along*length*t
        pts.extend([base+across*w+normal*.035,base-across*w+normal*.035,base-normal*.095])
    me=bpy.data.meshes.new('Composition_Fracture_Cutter');me.from_pydata(pts,[],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);me.update()
    cut=bpy.data.objects.new(me.name,me);COL.objects.link(cut)
    bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('Authored shallow fracture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True);bpy.data.meshes.remove(me)
for suffix,offset,length,width in [('Sea_Front',(-.20,0,.12),1.45,.09),('Stair_Right',(.12,0,-.13),1.25,.075)]:incision(SCENE.objects['Cape_Strict_Rock_'+suffix],offset,length,width)

# Recede the old straight near edge into the new bank. The walked route,
# camp and rear bamboo roots are all outside this y<9.8 envelope.
def deform(p):
    q=p.copy();wx=sm(-62.0,-60.5,p.x)*(1-sm(-54.6,-53.8,p.x));wy=1-sm(5.0,9.8,p.y);weight=wx*wy
    if weight:
        q.y+=.65*weight;q.z-=.64*weight*sm(.7,2.9,p.z)
    return q
for name in ['WALK_Forest_Ground','Cape_Terminus_Bedrock']:
    o=SCENE.objects[name];keep(o)
    for v in o.data.vertices:v.co=deform(v.co)
    o.data.update()
# The old long wall withdraws behind the new blocks, rather than remaining
# the visible facade between separate decorative stones.
wall=SCENE.objects['Cape_Terminus_Bedrock']
for v in wall.data.vertices:
    p=v.co
    if p.x>-62 and p.y<9.2:p.y+=.25*(1-sm(7.3,9.2,p.y))
wall.data.update()
for name in ['Forest_Strict_Grass','Forest_Strict_Understory','Forest_Strict_Flowers']:
    o=SCENE.objects.get(name)
    if not o:continue
    keep(o)
    for v in o.data.vertices:v.co=deform(v.co)
    o.data.update()

# Treads are hand-specified stone joints, with complete supporting geometry
# integrated in the exported model. No new upper stairs or route are added.
stairs=Mesh('Composition_Stair_Treads');support=Mesh('Composition_Stair_Core');N=16
patterns=[[-.5,-.13,.5],[-.5,.05,.5],[-.5,-.26,.21,.5],[-.5,-.03,.5],[-.5,-.19,.30,.5],[-.5,.16,.5],[-.5,-.22,.16,.5],[-.5,.04,.5],[-.5,-.15,.5],[-.5,-.28,.19,.5],[-.5,.11,.5],[-.5,-.08,.5],[-.5,-.21,.26,.5],[-.5,.02,.5],[-.5,-.12,.5],[-.5,.19,.5]]
depths=[.012,-.008,.004,.016,-.004,.009,-.011,.003,.010,-.006,.012,-.005,.004,.014,-.007,.0]
for i in range(N):
    c=top+direction*(run*i/N);z=top.z-(top.z-bottom.z)*i/N;depth=run/N+.024
    cuts=patterns[i]
    for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
        aa=a*WIDTH+.006;bb=b*WIDTH-.006;chip=.027 if (i+j)%4==0 else .014
        poly=[c+side*(aa+chip)-direction*(.009+depths[i]),c+side*(bb-chip*.5)-direction*(.009+depths[i]),c+side*bb+direction*.025,c+side*bb+direction*(depth-.018),c+side*(bb-.02)+direction*depth,c+side*(aa+.024)+direction*depth,c+side*aa+direction*(depth-.026),c+side*aa+direction*.024]
        for p in poly:p.z=z
        low=[p-Vector((0,0,.29)) for p in poly]
        stairs.part(poly,tri(poly),GRAY)
        for k in range(8):n=(k+1)%8;stairs.part([low[k],low[n],poly[n],poly[k]],[(0,1,2,3)],GRAY)
        stairs.part(low,[tuple(reversed(t)) for t in tri(low)],GRAY)
    poly=[c-side*WIDTH*.5-direction*.023,c+side*WIDTH*.5-direction*.023,c+side*WIDTH*.5+direction*(depth+.02),c-side*WIDTH*.5+direction*(depth+.02)]
    for p in poly:p.z=z-.06
    low=[Vector((p.x,p.y,-.45)) for p in poly];support.part(poly,[(0,1,2,3)],GRAY)
    for k in range(4):n=(k+1)%4;support.part([low[k],low[n],poly[n],poly[k]],[(0,1,2,3)],GRAY)
    support.part(low,[(3,2,1,0)],GRAY)
for old,builder in [('WALK_Cape_Stairs',stairs),('Cape_Stair_Support',support)]:
    ob=builder.build();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if old=='WALK_Cape_Stairs':
        edges=[e for e in bm.edges if e.is_manifold and e.calc_face_angle()>.65]
        bmesh.ops.bevel(bm,geom=edges,offset=.012,segments=2,affect='EDGES',clamp_overlap=True)
    bm.to_mesh(ob.data);bm.free();ob.data.update();adopt(old,ob)

state['rocks']=[o.name for o in new_rocks];state['stairs']={'steps':N,'width':WIDTH,'run':run,'top':list(top),'bottom':list(bottom),'joins':'explicit varied stone patterns'}
LAYOUT['reference_cape']['cliff_masses']=state['rocks'];LAYOUT['reference_cape']['strict_reference']['rocks']=state['rocks']
state['stage']='grey geometry, before face paintings';LAYOUT['revision']='left-finish-rock-stair-composition-grey'
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
(R/'grey-layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2),encoding='utf8')
bpy.data.libraries.write(str(R/'grey-authoring.blend'),{SCENE},fake_user=True,compress=True)

# Neutral authoring view of the actual new assembly, independent of game fog.
diagnostic=bpy.data.scenes.new('Rock_Stair_Composition_Grey_20261119');original=bpy.context.window.scene;bpy.context.window.scene=diagnostic
try:
    for o in new_rocks+[SCENE.objects['WALK_Cape_Stairs'],SCENE.objects['Cape_Stair_Support'],SCENE.objects['WALK_Forest_Ground']]:
        cp=o.copy();cp.data=o.data.copy();cp.name='Grey_'+o.name;diagnostic.collection.objects.link(cp);cp.hide_render=False;cp.hide_set(False);cp.data.materials.clear();cp.data.materials.append(GRAY)
        for p in cp.data.polygons:p.material_index=0
        if o.name=='WALK_Forest_Ground':
            bm=bmesh.new();bm.from_mesh(cp.data)
            for point,normal in [((-69,0,0),(-1,0,0)),((-54,0,0),(1,0,0)),((0,0,0),(0,-1,0)),((0,19,0),(0,1,0))]:
                bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,clear_outer=True)
            bm.to_mesh(cp.data);bm.free()
    diagnostic.render.engine='CYCLES';diagnostic.cycles.samples=20;diagnostic.cycles.use_denoising=True;diagnostic.render.resolution_x=1280;diagnostic.render.resolution_y=900;diagnostic.render.resolution_percentage=100;diagnostic.render.image_settings.file_format='PNG';diagnostic.view_settings.view_transform='AgX';diagnostic.view_settings.exposure=.1
    world=bpy.data.worlds.new('CompositionGreyWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.22,.23,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;diagnostic.world=world
    for key,power,pos,size in [('Key',3200,(-75,-1,20),12),('Fill',1200,(-50,-3,12),12),('Rim',1500,(-59,22,18),10)]:
        d=bpy.data.lights.new('CompositionGrey'+key,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(d.name,d);diagnostic.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((-62,9,2))-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('CompositionGreyCamera');cam=bpy.data.objects.new(d.name,d);diagnostic.collection.objects.link(cam);diagnostic.camera=cam;d.type='ORTHO';d.ortho_scale=20
    target=Vector((-61.8,9.3,2.4))
    for angle in [0,28]:
        a=math.radians(angle);cam.location=target+Vector((math.sin(a)*30,-math.cos(a)*30,15));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();diagnostic.render.filepath=str(R/('grey-'+str(angle)+'.png'));bpy.ops.render.render(write_still=True)
finally:bpy.context.window.scene=original
print(json.dumps({'stage':state['stage'],'rocks':len(new_rocks),'grey_preview':['grey-0.png','grey-28.png'],'saved':str(R/'grey-authoring.blend')}))
