"""Build one rock shelf, descending stairs and beach through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/reference-cape-review';TEX=OUT/'reference_cape'
assert not LAYOUT.get('reference_cape'),'Cape exists: inspect and refine instead of repeating initial authoring.'
partial=bpy.data.collections.get('49_Reference_Cape')
if partial:
    assert not partial.objects,'Partial build contains geometry; inspect rather than clear it.'
    bpy.data.collections.remove(partial)
COL=bpy.data.collections.new('49_Reference_Cape');SCENE.collection.children.link(COL)
def material(key,color=(1,1,1,1),image=None,rough=.90):
    m=bpy.data.materials.new('RC_'+key);m.use_nodes=True;m.diffuse_color=color
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=rough
    if image:
        im=bpy.data.images.load(str(TEX/(image+'.png')),check_existing=True);im.pack()
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    MATS[key]=m;return m
material('cape_side',image='rock_side');material('cape_top',image='rock_top')
material('cape_platform',image='platform');material('cape_tread',image='tread')
material('cape_sand',image='sand_unique');material('cape_wood',image='wood')
material('cape_char',(.085,.065,.045,1));material('cape_log_end',(.32,.21,.10,1))
material('cape_ring',(.25,.245,.205,1));material('cape_leaf',(.19,.27,.12,1))
material('cape_water',(.20,.37,.35,1));material('cape_fire',(1,.30,.035,1));material('cape_smoke',(.30,.28,.26,1))
old=SCENE.objects['WALK_Forest_Ground']
tree=BVHTree.FromPolygons([v.co for v in old.data.vertices],[list(p.vertices) for p in old.data.polygons])
def old_height(x,y):
    hit=tree.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
    if hit is None:hit=tree.find_nearest(Vector((x,y,6.28)))[0]
    assert hit,(x,y)
    return hit.z
def anchor(name,x,y,z):
    LAYOUT['anchors'][name]=[x,z,-y];A[name]=Vector((x,y,z))
def edge(a,b):LAYOUT['edges'].append([a,b])
anchor('forest_cape_approach',-52.2,13.7,old_height(-52.2,13.7));edge('forest_west_end','forest_cape_approach')
anchor('forest_cape_exit',-60.90,13.7,old_height(-60.90,13.7));edge('forest_cape_approach','forest_cape_exit')
anchor('cape_neck',-65.0,13.2,5.58);edge('forest_cape_exit','cape_neck')
anchor('cape_entry',-68.9,12.2,4.55);edge('cape_neck','cape_entry')
anchor('cape_center',-74.4,11.5,4.55);edge('cape_entry','cape_center')
anchor('cape_stair_top',-74.20,8.45,4.55);edge('cape_center','cape_stair_top')
anchor('cape_stair_bottom',-73.10,-2.5,.15);edge('cape_stair_top','cape_stair_bottom')
anchor('cape_sand',-75.8,-5.1,.12);edge('cape_stair_bottom','cape_sand')
anchor('cape_shore_end',-80.0,-3.3,.10);edge('cape_sand','cape_shore_end')
# A broad attached neck descends gently to the single shelf. There is no
# separate upper terrace or staircase between bamboo path and rock shelf.
def neck_center(t):return Vector((-60.90-8.45*t,13.7-1.5*t))
vs=[];uv=[];fs=[];NX=48;NY=12
for j in range(NY+1):
    s=(j/NY-.5)*2
    for i in range(NX+1):
        t=i/NX;c=neck_center(t);width=5.5-2.3*sm(0,.65,t)+.65*sm(.65,1,t)
        x=c.x;y=c.y+s*width
        h=(6.28*(1-sm(.04,1,t))+4.55*sm(.04,1,t))+.10*s*s*(1-t)
        if t<.06:
            h=old_height(x,y)*(1-sm(0,.06,t))+h*sm(0,.06,t)
        vs.append((x,y,h));uv.append((t,(s+1)*.5))
for j in range(NY):
    for i in range(NX):
        k=j*(NX+1)+i;fs.extend([(k,k+1,k+NX+2),(k,k+NX+2,k+NX+1)])
b=Mesh('WALK_Cape_Neck');b.part(vs,fs,'cape_top',uv);b.build(smooth=True)
neck_wall=Mesh('Cape_Neck_Rockside')
for row in [0,NY]:
    for i in range(NX):
        a=Vector(vs[row*(NX+1)+i]);b=Vector(vs[row*(NX+1)+i+1])
        neck_wall.part([a,b,(b.x,b.y+.05,-.45),(a.x,a.y+.05,-.45)],[(0,1,2,3)],'cape_side')
neck_wall.build()
outline=[(-68.2,9.4),(-71.5,6.6),(-72.83,6.22),(-73.05,8.57),(-75.35,8.33),(-75.10,6.20),(-78.1,5.95),(-81.3,7.0),(-83.0,9.8),(-82.4,13.0),(-80.0,15.1),(-76.5,15.9),(-72.2,15.0),(-69.2,14.0),(-68.0,12.3)]
pts=[Vector((x,y,4.55)) for x,y in outline]
b=Mesh('WALK_Cape_Platform');b.part(pts,tri(pts),'cape_platform',[((p.x+84)/17,(p.y-5)/13) for p in pts]);b.build()
core=Mesh('Cape_Attached_Cliff_Core')
for p,q in zip(pts,pts[1:]+pts[:1]):
    core.part([p-Vector((0,0,.05)),q-Vector((0,0,.05)),(q.x+.08,q.y+.08,-.65),(p.x+.08,p.y+.08,-.65)],[(0,1,2,3)],'cape_side')
core.build()
shape=[(-1,-.32),(-.82,-.78),(-.18,-1),(.63,-.84),(1,-.30),(.93,.48),(.46,.96),(-.39,.87),(-.93,.43)]
def cut_rock(name,x,y,width,depth,bottom,height,angle=0,lean=(.12,-.10),top_scale=.87):
    b=Mesh(name);cs=math.cos(angle);sn=math.sin(angle);rings=[]
    for j,(factor,z,shift) in enumerate([(1.02,bottom,(0,0)),(.98,bottom+height*.40,(-lean[0]*.35,-lean[1]*.35)),(top_scale,bottom+height,lean)]):
        ring=[]
        for i,(px,py) in enumerate(shape):
            phase=int(abs(x*1.3+y*.7))%9
            profile=[.96,.87,.94,.81,.90,.98,.84,.95,.90]
            f=factor*(1.0+.04*math.sin(i*1.65+phase))
            dx=px*width*.5*f+shift[0];dy=py*depth*.5*f+shift[1]
            zz=bottom+height*profile[(i+phase)%9] if j==2 else z+.04*math.sin(i*1.9)
            ring.append(Vector((x+dx*cs-dy*sn,y+dx*sn+dy*cs,zz)))
        rings.append(ring)
    for j in range(2):
        for i in range(len(shape)):
            q=(i+1)%len(shape)
            b.part([rings[j][i],rings[j][q],rings[j+1][q],rings[j+1][i]],[(0,1,2,3)],'cape_side')
    center=sum(rings[2],Vector())/len(shape)
    top=rings[2]+[center+Vector((-width*.14,-depth*.12,height*.06)),center+Vector((width*.13,depth*.13,-height*.02))]
    b.part(top,[(0,1,2,9),(2,3,4,10,9),(4,5,6,10),(6,7,8,0,9,10)],'cape_top')
    b.part(rings[0],[tuple(reversed(t)) for t in tri(rings[0])],'cape_side')
    return b.build()
rocks=[]
specs=[(-81.1,8.5,4.0,3.2,-.45,4.9,.12),(-81.0,12.8,4.2,3.7,-.55,5.0,-.14),(-83.0,10.7,2.45,2.6,-.65,3.6,.20),(-78.6,5.8,4.1,3.0,-.45,4.88,-.11),(-76.5,3.2,2.7,3.1,-.50,3.42,.17),(-75.6,-.30,2.0,2.2,-.42,1.95,.14),(-71.7,4.0,3.05,4.3,-.48,4.96,-.14),(-68.8,8.4,3.35,4.0,-.47,5.28,.15),(-69.6,15.9,3.3,3.0,-.45,6.30,-.21),(-78.0,16.0,4.1,2.9,-.42,5.6,.09)]
for i,s in enumerate(specs):rocks.append(cut_rock('Cape_Cliff_Mass_%02d'%i,*s).name)
# A single narrow stair notch through the front of the shelf, with irregular
# block joints and an actual filled support below every tread.
top=A['cape_stair_top'];bottom=A['cape_stair_bottom'];axis=(bottom-top);axis.z=0;length=axis.length;axis.normalize();side=Vector((-axis.y,axis.x,0))
stairs=Mesh('WALK_Cape_Stairs');steps=22;width=2.16
def box(builder,center,dx,dy,dz,material,angle=0):
    c=Vector(center);ax=Vector((math.cos(angle),math.sin(angle),0))*dx*.5;ay=Vector((-math.sin(angle),math.cos(angle),0))*dy*.5
    p=[c-ax-ay,c+ax-ay,c+ax+ay,c-ax+ay];vs=p+[v+Vector((0,0,dz)) for v in p]
    builder.part(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material,[(0,0),(1,0),(1,1),(0,1)]*2)
angle=math.atan2(axis.y,axis.x)
for i in range(steps):
    height=top.z-(top.z-bottom.z)*i/steps
    center=top+axis*(length*(i+.5)/steps)
    split=[-.5,-.18,.21,.5] if i%2==0 else [-.5,-.04,.5]
    for left,right in zip(split,split[1:]):
        c=center+side*((left+right)*width*.5);c.z=height-.19
        box(stairs,c,length/steps+.006,(right-left)*width-.009,.19,'cape_tread',angle)
stairs.build()
support=Mesh('Cape_Stair_Support')
for i in range(steps):
    h=top.z-(top.z-bottom.z)*i/steps-.20;c=top+axis*(length*(i+.5)/steps);c.z=-.45
    box(support,c,length/steps+.006,width-.08,max(.05,h+.45),'cape_side',angle)
support.build()
# Broad sand cove. Both sand and swash carriers are authored in Blender.
BACK=[(-84,1.5),(-81,-.1),(-77,-1.5),(-73,-1.55),(-69,.5),(-66,2.4)]
FRONT=[(-84,-3.0),(-81,-5.5),(-77,-7.65),(-73,-8.0),(-68.8,-5.8),(-65,-1.8)]
def curve(points,t):
    f=min(.999999,max(0,t))*(len(points)-1);i=int(f);u=f-i
    p0=Vector(points[max(0,i-1)]);p1=Vector(points[i]);p2=Vector(points[min(len(points)-1,i+1)]);p3=Vector(points[min(len(points)-1,i+2)])
    return .5*(2*p1+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u)
vs=[];uv=[];shore=[];fs=[];NX=80;NY=36;maxv=1.35;arc=[0.]
for i in range(1,NX+1):arc.append(arc[-1]+(curve(FRONT,i/NX)-curve(FRONT,(i-1)/NX)).length)
for j in range(NY+1):
    v=j/NY*maxv
    for i in range(NX+1):
        u=i/NX;a=curve(BACK,u);f=curve(FRONT,u);p=a+(f-a)*v
        z=.145-.032*sm(.2,.8,v)-.30*sm(.74,1.03,v)-.46*sm(1.03,1.35,v)
        vs.append(Vector((p.x,p.y,z)));uv.append((u,1-v/maxv));shore.append((arc[i],1.-(v-1)*(f-a).length))
for j in range(NY):
    for i in range(NX):
        k=j*(NX+1)+i;fs.extend([(k,k+1,k+NX+2),(k,k+NX+2,k+NX+1)])
for name,points,matkey in [('WALK_Cape_Sand',vs,'cape_sand'),('Cape_Swash_Film',[Vector((p.x,p.y,max(p.z,-.18)+.010)) for p in vs],'cape_water')]:
    b=Mesh(name);b.part(points,fs,matkey,uv);ob=b.build(smooth=True)
    for p in ob.data.polygons:
        for li in p.loop_indices:ob.data.uv_layers[1].data[li].uv=shore[ob.data.loops[li].vertex_index]
# Low rocks at the feet, attached to the cliff toe rather than peppered over
# the open sand. The beach's middle remains readable and walkable.
for i,s in enumerate([(-82.0,1.0,2.4,2.0,-.35,1.1,.18),(-79.0,.20,1.8,1.7,-.32,1.0,-.25),(-69.2,-.1,2.2,2.0,-.36,1.32,.17),(-67.5,1.5,2.1,1.7,-.35,1.6,.22)]):cut_rock('Cape_Cliff_Toe_%02d'%i,*s)
# Campfire and timber seat. Their components have separate editable meshes.
fire=Vector((-76.0,13.1,4.57))
for i in range(10):
    a=i*math.tau/10;center=fire+Vector((math.cos(a)*.68,math.sin(a)*.57,0))
    ob=cut_rock('Cape_Fire_Ring_%02d'%i,center.x,center.y,.32,.25,4.51,.27,a,top_scale=.82)
    for p in ob.data.polygons:p.material_index=0
    ob.data.materials.clear();ob.data.materials.append(MATS['cape_ring'])
for i,(x,y,a) in enumerate([(-.22,-.10,.5),(.22,.04,-.7),(-.02,.22,1.8),(.03,-.22,-.2),(.06,.02,.8)]):
    b=Mesh('Cape_Fire_Log_%02d'%i);c=fire+Vector((x,y,.11+(i%2)*.05));d=Vector((math.cos(a),math.sin(a),.17))
    tube(b,[c-d*.43,c+d*.43],[.115,.09],'cape_wood',sides=9);b.build()
seat=Mesh('Cape_Timber_Seat');c=Vector((-72.2,13.5,4.85));d=Vector((1,.13,0)).normalized()
tube(seat,[c-d*.96,c+d*.96],[.29,.25],'cape_wood',sides=12);seat.build()
caps=Mesh('Cape_Timber_Endgrain')
for sign in [-1,1]:
    center=c+d*(.969*sign);verts=[center+Vector((-.13*math.cos(i*math.tau/12),math.cos(i*math.tau/12),math.sin(i*math.tau/12)))*(.265 if sign==1 else .30) for i in range(12)]
    caps.part(verts,tri(verts),'cape_log_end',[(.5+.49*math.cos(i*math.tau/12),.5+.49*math.sin(i*math.tau/12)) for i in range(12)])
caps.build()
for i in range(6):
    a=i*math.pi/3;b=Mesh('Cape_Flame_%02d'%i);side=Vector((math.cos(a),math.sin(a),0))*.40
    pts=[fire-side,fire+side,fire+side+Vector((0,0,1.10)),fire-side+Vector((0,0,1.10))]
    b.part(pts,[(0,1,2,3)],'cape_fire',[(0,0),(1,0),(1,1),(0,1)]);b.build()
for i in range(3):
    a=i*math.pi/3;b=Mesh('Cape_Smoke_%02d'%i);side=Vector((math.cos(a),math.sin(a),0))*.50
    base=fire+Vector((0,0,.9));b.part([base-side,base+side,base+side+Vector((0,0,3.1)),base-side+Vector((0,0,3.1))],[(0,1,2,3)],'cape_smoke',[(0,0),(1,0),(1,1),(0,1)]);b.build()
for i in range(7):
    b=Mesh('Cape_Ember_%02d'%i);s=.027;b.part([fire+Vector((-s,0,0)),fire+Vector((s,0,0)),fire+Vector((s,0,s*2)),fire+Vector((-s,0,s*2))],[(0,1,2,3)],'cape_fire',[(0,0),(1,0),(1,1),(0,1)]);b.build()
# A small number of attached plants, using the existing colored leaf method.
grass=Mesh('Cape_Shore_Grass')
sites=[(-81.9,13.7,4.85),(-79.4,15.45,4.65),(-70.1,14.45,4.7),(-68.6,10.0,4.7),(-82.1,1.1,.20),(-80.9,-.7,.15),(-69.2,-.8,.16),(-67.5,.8,.24)]
for k,(x,y,z) in enumerate(sites):
    for i in range(11):
        a=i*2.399+k*.63;root=Vector((x+math.cos(a)*.24,y+math.sin(a)*.21,z));tip=root+Vector((math.cos(a)*.17,math.sin(a)*.16,.22+(i%4)*.08));side=Vector((-math.sin(a),math.cos(a),0))*.055
        grass.part([root-side,root+side,tip],[(0,1,2)],'cape_leaf',[(0,0),(1,0),(.5,1)],weights=[0,0,1])
grass.build()
# A separate sky carrier and deliberately grouped sea rocks. Far water stays
# a dynamic physical surface; the reference is not pasted across the scene.
sky=Mesh('Cape_Sky_Backdrop');sky.part([(-210,185,-35),(40,185,-35),(40,185,110),(-210,185,110)],[(0,1,2,3)],'cape_top',[(0,0),(1,0),(1,1),(0,1)]);sky.build()
islets=[]
for group,(x,y,w,d,h) in enumerate([(-112,92,15,11,9),(-89,124,6,6,11),(-63,151,12,11,7),(-75,95,4.5,5,13)]):
    for i,(dx,dy,s) in enumerate([(-.30,-.03,.65),(.13,.12,1),(.42,-.10,.57)]):
        ob=cut_rock('Cape_Distant_Islet_%02d_%02d'%(group,i),x+dx*w,y+dy*d,w*s*.75,d*s,-.7,h*s,(-.15+.17*i),lean=(.7,-.2),top_scale=.64)
        islets.append(ob.name)
LAYOUT['reference_cape']={'collection':COL.name,'reference':'artifacts/reference-cape-review/reference/user-cape.png','connection':'forest_west_end via existing west forest floor and one continuous gently descending neck','single_shelf_height':4.55,'sea_level':-.18,'stairs':{'top':'cape_stair_top','bottom':'cape_stair_bottom','steps':steps,'width':width},'fire_center':[fire.x,fire.z,-fire.y],'seat_center':[c.x,c.z,-c.y],'shoreline':[[curve(FRONT,i/31).x,-curve(FRONT,i/31).y] for i in range(32)],'cliff_masses':rocks,'distant_islets':islets,'new_anchors':[k for k in LAYOUT['anchors'] if k.startswith('cape_') or k.startswith('forest_cape_')],'bounds':[-84,-60.9,-9,18],'role':'walkable rock shelf, stair notch, sandy cove, live campfire and open sea'}
(REVIEW/'author-build.json').write_text(json.dumps(LAYOUT['reference_cape'],indent=2),encoding='utf-8')
export('reference-cape-initial')
