"""Recompose the terminal forest as one rocky coast, executed via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
import ast,array
R=ROOT/'artifacts/forest-rocky-terminus-review'
assert not LAYOUT['reference_cape'].get('rocky_terminus'),'Already authored: inspect and refine, do not rerun.'
COL=bpy.data.collections.get('52_Forest_Rocky_Terminus')
if COL:assert not COL.objects,'Partial authoring beyond the seam cut; inspect before resuming.'
else:COL=bpy.data.collections.new('52_Forest_Rocky_Terminus');SCENE.collection.children.link(COL)
archive=bpy.data.collections.get('90_Rejected_Long_Forest_Tip')
if not archive:archive=bpy.data.collections.new('90_Rejected_Long_Forest_Tip');SCENE.collection.children.link(archive)
def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def fingerprint(o):
    me=o.data;vs=array.array('f',[0])*len(me.vertices)*3;me.vertices.foreach_get('co',vs)
    inds=array.array('i',[0])*len(me.loops);me.loops.foreach_get('vertex_index',inds)
    h=hashlib.sha256(vs.tobytes()+inds.tobytes())
    for uv in me.uv_layers:
        a=array.array('f',[0])*len(uv.data)*2;uv.data.foreach_get('uv',a);h.update(a.tobytes())
    return {'hash':h.hexdigest(),'matrix':[list(v) for v in o.matrix_world]}
if not (R/'before/object-state.json').exists():(R/'before/object-state.json').write_text(json.dumps({o.name:fingerprint(o) for o in SCENE.objects if live(o)}),encoding='utf8')
changed=[];retired=[]
def keep(o):
    if archive.objects.get('LongTip_Before_'+o.name):changed.append(o.name);return
    cp=o.copy();cp.data=o.data.copy();cp.name='LongTip_Before_'+o.name;archive.objects.link(cp);cp.hide_set(True);cp.hide_render=True;changed.append(o.name)
def retire(o):
    retired.append(o.name)
    for c in list(o.users_collection):c.objects.unlink(o)
    archive.objects.link(o);o.hide_set(True);o.hide_render=True
def shift(o,delta):
    keep(o)
    for v in o.data.vertices:v.co+=delta
    o.data.update()
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def sample(t,x,y,z=30):
    h=t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))[0]
    return h.z if h else None

# The replacement is based on the saved pre-extension forest, keeping all
# eastern geometry and UV. It cuts and rejoins one exact x=-54 boundary.
ground=SCENE.objects['WALK_Forest_Ground'];keep(ground)
ground.data=SCENE.objects['Tip_Before_WALK_Forest_Ground'].data.copy()
near=SCENE.objects['Tip_Before_WALK_Forest_NearSlope'].copy();near.data=near.data.copy();near.name='Terminus_Base_Near';COL.objects.link(near);near.hide_set(False);near.hide_render=False
bpy.ops.object.select_all(action='DESELECT')
for o in [ground,near]:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=ground;bpy.ops.object.join()
original=tree(ground)
bm=bmesh.new();bm.from_mesh(ground.data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=Vector((-54,0,0)),plane_no=Vector((1,0,0)))
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x<-54.00001],context='VERTS')
bm.to_mesh(ground.data);bm.free();ground.data.update()
seam=sorted({tuple(round(c,6) for c in v.co):v.co.copy() for v in ground.data.vertices if abs(v.co.x+54)<.00002}.values(),key=lambda p:p.y)
assert len(seam)>35 and seam[-1].y>27,'Unexpected actual forest boundary.'

def original_height(x,y):
    xx=max(-61.2399,x);h=sample(original,xx,y)
    if h is None:
        h=sample(original,max(-62.99,x),y)
    if h is None:
        h=original.find_nearest(Vector((xx,y,6.2)))[0].z
    return h
def floor_height(x,y):
    h=original_height(x,y)
    # Broad near-edge shoulder, then a clear cliff: no low connection ramp.
    target=6.26-.017*max(0,13.7-y)
    front=1-sm(10.0,13.0,y)
    return h+(target-h)*sm(-54,-59.5,x)*front
outer_xy=[(-60.8,27.5),(-62.8,24.5),(-64.4,22.0),(-65.3,18.5),(-66.0,16.0),
          (-66.9,13.6),(-67.35,10.9),(-66.6,8.8),(-64.6,7.6),
          (-64.4,8.82),(-62.2,8.82),(-62.15,6.9),(-59.8,5.8),(-56.5,1.4)]
border=[seam[-1]]+[Vector((x,y,floor_height(x,y))) for x,y in outer_xy]+[seam[0]]
outline=seam+border[1:-1]
builder=Mesh('Terminus_Joined_Floor');builder.part(outline,tri(outline),ground.data.materials[0],[((p.x+68)/18,(p.y-4)/31) for p in outline]);patch=builder.build(True)
bm=bmesh.new();bm.from_mesh(patch.data)
bmesh.ops.subdivide_edges(bm,edges=[e for e in bm.edges if len(e.link_faces)==2],cuts=18,use_grid_fill=True)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
pins={tuple(round(c,6) for c in p):p.z for p in outline}
for v in bm.verts:
    if tuple(round(c,6) for c in v.co) not in pins:v.co.z=floor_height(v.co.x,v.co.y)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(patch.data);bm.free();patch.data.update()
for p in patch.data.polygons:
    for li in p.loop_indices:
        v=patch.data.vertices[patch.data.loops[li].vertex_index].co
        patch.data.uv_layers[0].data[li].uv=((v.x+68)/18,(v.y-4)/31)
bpy.ops.object.select_all(action='DESELECT')
for o in [ground,patch]:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=ground;bpy.ops.object.join()
bm=bmesh.new();bm.from_mesh(ground.data);bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if abs(v.co.x+54)<.00003],dist=.00003);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free();ground.data.update()
floor=tree(ground)
def fh(x,y):
    h=sample(floor,x,y);assert h is not None,(x,y);return h

# Truncate only the old near skirt which belonged to the replaced endpoint.
skirt=SCENE.objects['Forest_Near_Closed_Skirt'];keep(skirt)
bm=bmesh.new();bm.from_mesh(skirt.data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=Vector((-54,0,0)),plane_no=Vector((1,0,0)))
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x<-54.00001],context='VERTS');bm.to_mesh(skirt.data);bm.free();skirt.data.update()
for o in list(SCENE.objects):
    if live(o) and o.name.startswith(('Cape_Cliff_','Cape_Tip_Continuous','Cape_Shore_Grass')):retire(o)
MATS['terminus_side']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_side')][-1]
MATS['terminus_top']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_top')][-1]
MATS['terminus_tread']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_tread')][-1]

# Continuous interlocking cliff planes share the terrain outline. The stair
# notch stays open; no separate ring of tall boulder columns is added.
wall=Mesh('Cape_Terminus_Bedrock')
for i,(p,q) in enumerate(zip(border,border[1:])):
    if p.y>8.7 and q.y>8.7 and p.x<-64 and q.x>-63:continue
    n=Vector((q.y-p.y,p.x-q.x,0)).normalized()
    p1=Vector((p.x,p.y,p.z*.48))+n*(.12 if i%3 else -.10)
    q1=Vector((q.x,q.y,q.z*.48))+n*(.10 if i%3 else -.07)
    wall.part([p,q,q1,p1],[(0,1,2,3)],'terminus_side')
    wall.part([p1,q1,(q1.x+.12*n.x,q1.y+.12*n.y,-.65),(p1.x+.12*n.x,p1.y+.12*n.y,-.65)],[(0,1,2,3)],'terminus_side')
wall.build()
def slab(name,xy,heights):
    b=Mesh(name);tops=[Vector((x,y,z)) for (x,y),z in zip(xy,heights)]
    bottoms=[Vector((p.x,p.y,fh(p.x,p.y)-.4)) for p in tops]
    for i,(p,q) in enumerate(zip(tops,tops[1:]+tops[:1])):
        j=(i+1)%len(tops);b.part([bottoms[i],bottoms[j],q,p],[(0,1,2,3)],'terminus_side')
    center=sum(tops,Vector())/len(tops);center.z+=.09
    b.part(tops+[center],[(i,(i+1)%len(tops),len(tops)) for i in range(len(tops))],'terminus_top')
    b.part(bottoms,[tuple(reversed(t)) for t in tri(bottoms)],'terminus_side');return b.build()
rock1=slab('Cape_Terminus_Root_Rock_West',[(-65.05,16.25),(-64.5,15.7),(-62.7,15.65),(-61.7,16.4),(-62.2,17.7),(-64.3,17.9)],[6.8,7.05,6.85,6.65,6.75,7.1])
rock2=slab('Cape_Terminus_Root_Rock_East',[(-60.4,16.4),(-59.2,16.05),(-57.9,16.5),(-58.1,17.8),(-59.7,18.0),(-60.8,17.3)],[6.7,6.5,6.4,6.75,6.55,6.6])
rock3=slab('Cape_Terminus_Near_Exposure',[(-60.8,6.95),(-59.5,6.6),(-57.8,7.25),(-58.5,8.4),(-60.4,8.5),(-61.0,7.8)],[6.18,6.08,6.0,6.34,6.3,6.1])
rocks=[rock1,rock2,rock3]
contact_trees=[tree(o) for o in [ground]+rocks]
def support(x,y):
    hs=[sample(t,x,y) for t in contact_trees];hs=[h for h in hs if h is not None];assert hs;return max(hs)

# Keep original leaf UV2 weights, roots and coherent wind bindings on reused
# planted culms. Only the two new endpoint plants are copied and repositioned.
roles=LAYOUT['forest_extension']['layer_roles'];new_bamboo=[]
for num,source,xyz,scale in [(30,0,(-65.1,17.7),.86),(31,1,(-62.05,17.6),.90)]:
    srcname='Forest_Bamboo_Role_Main_%02d'%source;binding=roles['wind_bindings'][srcname]
    srcroot=Vector((binding['root'][0],-binding['root'][2],binding['root'][1]))
    target=Vector((xyz[0],xyz[1],support(*xyz)+.012))
    for label in ['Main','Leaves']:
        old=SCENE.objects['Forest_Bamboo_Role_%s_%02d'%(label,source)]
        cp=old.copy();cp.data=old.data.copy();cp.name='Forest_Bamboo_Role_%s_%02d'%(label,num);COL.objects.link(cp)
        for v in cp.data.vertices:
            offset=v.co-srcroot;offset.z*=scale;v.co=target+offset
        cp.data.update();cp.hide_set(False);cp.hide_render=False
        roles['wind_bindings'][cp.name]={'root':[target.x,target.z,-target.y],'height':binding['height']*scale,'seed':470+num*13.47,'amplitude':.68}
        LAYOUT['forest_extension']['groves'].append({'name':cp.name,'band':'role_main'});new_bamboo.append(cp.name)

# Retain the fire and timber props, placing them on the common surface.
oldfire=Vector((LAYOUT['reference_cape']['fire_center'][0],-LAYOUT['reference_cape']['fire_center'][2],LAYOUT['reference_cape']['fire_center'][1]))
newfire=Vector((-64.85,13.05,fh(-64.85,13.05)+.02))
for o in list(SCENE.objects):
    if live(o) and o.name.startswith(('Cape_Fire_','Cape_Flame_','Cape_Smoke_','Cape_Ember_')):shift(o,newfire-oldfire)
oldseat=Vector((LAYOUT['reference_cape']['seat_center'][0],-LAYOUT['reference_cape']['seat_center'][2],LAYOUT['reference_cape']['seat_center'][1]))
newseat=Vector((-62.15,14.2,fh(-62.15,14.2)+.30))
for name in ['Cape_Timber_Seat','Cape_Timber_Endgrain']:shift(SCENE.objects[name],newseat-oldseat)

# Sand, swash and shoreline move with the compact coast, preserving source UV.
def sandx(x):return -63.8+(x+13.8+63.8)*.72
for name in ['WALK_Cape_Sand','Cape_Swash_Film']:
    o=SCENE.objects[name];keep(o)
    for v in o.data.vertices:v.co.x=sandx(v.co.x)
    o.data.update()
rc=LAYOUT['reference_cape'];rc['shoreline']=[[sandx(p[0]),p[1]] for p in rc['shoreline']]

# A narrow, single descending stair with original authored stone joints.
source=ast.parse((ROOT/'tools/blender/build_reference_cape.py').read_text(encoding='utf8'))
for n in source.body:
    if isinstance(n,ast.FunctionDef) and n.name=='box':exec(compile(ast.Module(body=[n],type_ignores=[]),'step-box','exec'))
top=Vector((-63.3,8.8,6.22));bottom=Vector((-62.2,-2.5,.15));axis=bottom-top;axis.z=0;length=axis.length;axis.normalize();side=Vector((-axis.y,axis.x,0));angle=math.atan2(axis.y,axis.x);steps=30;width=2.16
MATS['cape_tread']=MATS['terminus_tread'];MATS['cape_side']=MATS['terminus_side']
for name,supporting in [('WALK_Cape_Stairs',False),('Cape_Stair_Support',True)]:
    o=SCENE.objects[name];keep(o);b=Mesh(name+'_Compact')
    for i in range(steps):
        h=top.z-(top.z-bottom.z)*i/steps;c=top+axis*(length*(i+.5)/steps)
        if supporting:c.z=-.45;box(b,c,length/steps+.006,width-.08,h-.20+.45,'cape_side',angle)
        else:
            splits=[-.5,-.18,.21,.5] if i%2==0 else [-.5,-.04,.5]
            for l,r in zip(splits,splits[1:]):
                p=c+side*((l+r)*width*.5);p.z=h-.19;box(b,p,length/steps+.006,(r-l)*width-.009,.19,'cape_tread',angle)
    new=b.build();o.data=new.data;bpy.data.objects.remove(new,do_unlink=True)

# Sparse grouped grass only on contact edges, with fixed roots and weighted tips.
plants=Mesh('Forest_Grass_Terminus')
plant_roots=[]
for i,(x,y) in enumerate([(-65.6,15.6),(-65.0,16.2),(-64.8,17.3),(-64.0,18.3),(-62.4,16.1),(-61.8,15.8),(-60.6,16.8),(-59.4,16.4),(-58.3,17.3),(-62.0,11.2),(-60.9,10.8),(-60.6,8.3),(-59.3,8.2),(-58.2,9.0),(-57.6,12.0),(-58.8,15.1)]):
    z=support(x,y)+.012;plant_roots.append([x,y,z])
    for j,(dx,dy,h) in enumerate([(-.19,.04,.32),(.0,-.09,.42),(.21,.03,.28)]):
        cx=x+dx;cy=y+dy;zz=support(cx,cy)+.012;w=.10
        plants.part([(cx-w,cy,zz),(cx+w,cy,zz),(cx+.12*math.sin(i+j),cy+.06,zz+h)],[(0,1,2)],'grass_blade',weights=[0,0,1])
plants.build()

def anch(n,x,y,z=None):LAYOUT['anchors'][n]=[x,fh(x,y) if z is None else z,-y]
for n,x,y in [('forest_cape_exit',-57,13.7),('cape_neck',-59.6,13.65),('cape_entry',-61.4,13.4),('cape_center',-63.3,12.8)]:anch(n,x,y)
anch('cape_stair_top',top.x,top.y,top.z);anch('cape_stair_bottom',bottom.x,bottom.y,bottom.z);anch('cape_sand',-64.9,-5.1,.12);anch('cape_shore_end',-67.5,-3.3,.10)
rc['fire_center']=[newfire.x,newfire.z,-newfire.y];rc['seat_center']=[newseat.x,newseat.z,-newseat.y];rc['single_shelf_height']=6.22;rc['cliff_masses']=[o.name for o in rocks];rc['bounds']=[-68.5,-54,-8,34]
rc['rocky_terminus']={'date':'2026-11-19','collection':COL.name,'replacement_boundary_x':-54,'seam_vertices':len(seam),'old_extent_x':-83.0,'new_extent_x':-67.35,'floor_bounds':[-68,4,18,31],'camera_opening':[57,65],'archive':archive.name,'changed_objects':changed,'retired_objects':retired,'new_bamboo':new_bamboo,'grass_roots':plant_roots,'outline':[list(p) for p in border],'modeling':'Actual Blender via blender-mcp; no external mesh generation'}
(R/'author-pass1.json').write_text(json.dumps(rc['rocky_terminus'],indent=2),encoding='utf8')
export('forest-rocky-terminus-pass1')
