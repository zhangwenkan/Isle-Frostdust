"""Rebuild the visible forest coast relief, executed exclusively via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
R=ROOT/'artifacts/forest-rocky-terminus-rework';rc=LAYOUT['reference_cape'];data=rc['rocky_terminus']
assert not data.get('reference_rework'),'This pass was executed; inspect before refining.'
COL=bpy.data.collections.new('53_Reference_Forest_Coast_Relief');SCENE.collection.children.link(COL)
archive=bpy.data.collections.new('90_Before_Reference_Forest_Coast_Relief');SCENE.collection.children.link(archive)
changed=[];retired=[]
def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def keep(o):
    cp=o.copy();cp.data=o.data.copy();cp.name='Relief_Before_'+o.name;archive.objects.link(cp);cp.hide_set(True);cp.hide_render=True;changed.append(o.name)
def retire(o):
    retired.append(o.name)
    for c in list(o.users_collection):c.objects.unlink(o)
    archive.objects.link(o);o.hide_set(True);o.hide_render=True
def replace(o,new):o.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def sample(t,x,y):
    p=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0];return p.z if p else None
ground=SCENE.objects['WALK_Forest_Ground'];keep(ground)
# Low changes within the existing outline; the route and exact eastern seam stay fixed.
for v in ground.data.vertices:
    p=v.co
    if p.x>=-54:continue
    f=sm(-54,-57,p.x)
    p.z+=f*.32*sm(14.6,16.9,p.y)*(1-sm(18.8,22,p.y))
    p.z+=f*.08*(1-sm(-61,-58,p.x))*math.exp(-((p.y-11.1)/3.1)**2)
ground.data.update();ft=tree(ground)
def fh(x,y):
    z=sample(ft,x,y)
    if z is None:z=ft.find_nearest(Vector((x,y,6)))[0].z
    return z
def rockmat(key,image):
    m=bpy.data.materials.new('ForestCoast_'+key);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.95
    im=bpy.data.images.load(str(OUT/'rocky_terminus'/image),check_existing=True);im.reload();im.pack()
    n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
    MATS[key]=m;return m
rockmat('relief_top','rock_planes_top.png');rockmat('relief_side','rock_planes_side.png')
for o in list(SCENE.objects):
    if live(o) and (o.name in data.get('retired_objects',[]) or o.name.startswith('Cape_Terminus_Root_') or o.name=='Cape_Terminus_Near_Exposure'):retire(o)

# The entire coast remains one connected base. Unequal fracture stations and
# ledge heights form volume, rather than two immense straight faces.
border=[Vector(p) for p in data['outline']]
for p in border:p.z=fh(p.x,p.y)
b=Mesh('Cape_Terminus_Bedrock_Structured')
stations=[];skip=[]
for idx,(p,q) in enumerate(zip(border,border[1:])):
    if p.y>8.7 and q.y>8.7 and p.x<-64 and q.x>-63:skip.append(idx)
    n=Vector((q.y-p.y,p.x-q.x,0)).normalized()
    for k in range(3):
        t=k/3;v=p.lerp(q,t)
        stations.append((v,n,idx,k))
stations.append((border[-1],stations[-1][1],len(border)-2,3))
heights=[0,.055,.19,.43,.69,1.]
rings=[]
for j,h in enumerate(heights):
    row=[]
    for i,(p,n,seg,k) in enumerate(stations):
        if j==0:z=p.z;off=0
        elif j==1:z=p.z-.23-.04*(seg%3);off=.15+.06*(seg%2)
        else:
            z=p.z*(1-h)+(-.65)*h
            if j<5:z+=.10*math.sin(seg*1.1+k*.8+j*.9)
            off=[0,0,.24,.40,.30,.35][j]+.08*math.sin(seg*1.3+k*1.7+j)
        row.append(Vector((p.x+n.x*off,p.y+n.y*off,z)))
    rings.append(row)
for j in range(5):
    for i in range(len(stations)-1):
        p,n,seg,k=stations[i]
        if seg in skip:continue
        # UV coordinates give large brush planes per fractured face, no micro grain.
        tile=(seg+j)%4;u0=(tile%2)*.5;v0=(tile//2)*.5
        uv=[(u0+.03,v0+.04),(u0+.46,v0+.02),(u0+.47,v0+.46),(u0+.04,v0+.47)]
        b.part([rings[j][i],rings[j][i+1],rings[j+1][i+1],rings[j+1][i]],[(0,1,2,3)],'relief_top' if j==0 else 'relief_side',uv)
wall=SCENE.objects['Cape_Terminus_Bedrock'];keep(wall);replace(wall,b.build())

# Jointed blocks: clipped corners, inclined cap planes, true near-vertical cuts.
shape=[(-1,-.42),(-.70,-.94),(.16,-1),(.79,-.67),(1,.13),(.56,.92),(-.38,.84),(-.98,.31)]
rocks=[];rockspec=[]
def block(name,x,y,w,d,base,h,angle,lean,tilt,variant=0):
    b=Mesh(name);cs=math.cos(angle);sn=math.sin(angle);rings=[]
    for j,(factor,z) in enumerate([(1.03,base),(.99,base+h-.18),(.85,base+h)]):
        row=[]
        for i,(px,py) in enumerate(shape):
            dx=px*w*.5*factor+lean[0]*j*.5;dy=py*d*.5*factor+lean[1]*j*.5
            zz=z+(tilt[0]*px+tilt[1]*py if j else 0)
            row.append(Vector((x+dx*cs-dy*sn,y+dx*sn+dy*cs,zz)))
        rings.append(row)
    tile=variant%4;u=(tile%2)*.5;v=(tile//2)*.5
    for j in range(2):
        for i in range(8):
            q=(i+1)%8
            b.part([rings[j][i],rings[j][q],rings[j+1][q],rings[j+1][i]],[(0,1,2,3)],'relief_side' if j==0 else 'relief_top',[(u+.03,v+.04),(u+.47,v+.04),(u+.47,v+.47),(u+.03,v+.47)])
    center=sum(rings[2],Vector())/8
    top=rings[2]+[center+Vector((-w*.12,-d*.06,.07)),center+Vector((w*.16,d*.06,-.035))]
    uv=[(u+.06+(p.x-x+w*.5)/w*.39,v+.05+(p.y-y+d*.5)/d*.39) for p in top]
    b.part(top,[(0,1,2,8),(2,3,4,9,8),(4,5,6,9),(6,7,0,8,9)],'relief_top',uv)
    b.part(rings[0],[tuple(reversed(t)) for t in tri(rings[0])],'relief_side')
    ob=b.build();rocks.append(ob);rockspec.append(dict(name=name,x=x,y=y,w=w,d=d,base=base,height=h));return ob

# Rear bedding runs from the cliff into bamboo roots, in three linked shoulders.
specs=[('Root_West',-64.5,16.6,3.1,2.3,5.60,1.70,-.20,(.10,-.06),(.13,-.17)),
       ('Root_Middle',-61.8,16.9,3.0,2.0,5.65,1.40,.12,(-.13,-.05),(-.15,-.12)),
       ('Root_East',-59.1,16.55,2.7,1.8,5.80,1.15,-.15,(.06,.08),(.11,-.09)),
       ('Root_Low',-61.0,15.65,1.5,1.15,6.15,.66,.30,(.03,-.05),(.05,-.06)),
       ('Stair_West',-65.1,8.65,2.1,1.55,4.65,1.78,-.18,(.08,.12),(-.08,.12)),
       ('Stair_East',-61.9,8.35,2.4,1.75,4.70,1.95,.18,(-.12,.10),(.13,.10)),
       ('Near_Shoulder',-59.4,7.4,2.7,1.95,4.65,1.75,-.24,(.09,.16),(-.14,.08)),
       ('Near_Return',-56.9,5.5,2.5,1.85,4.35,1.35,.18,(-.07,.12),(.09,.06)),
       ('Coast_West',-66.9,11.7,1.8,2.25,4.45,1.87,.13,(.14,.02),(-.08,.08))]
for i,s in enumerate(specs):block('Cape_Terminus_'+s[0],*s[1:],variant=i)
rt=[tree(o) for o in rocks]
def support(x,y):
    return max([z for z in [sample(ft,x,y)]+[sample(t,x,y) for t in rt] if z is not None],default=fh(x,y))

# A few irregular paving pieces lead through soil directly onto the exposed rock.
paving=Mesh('Cape_Terminus_Path_Pieces')
for i in range(21):
    x=-60.7+(i//3)*.82;y=13.65+[-.52,.09,.59][i%3]+.12*math.sin(i*1.2)
    w=[.38,.51,.44,.62][i%4];d=[.36,.43,.32][i%3]
    pts=[(x+px*w*.5,y+py*d*.5) for px,py in shape]
    z=fh(x,y)+.018
    paving.part([(a,bb,z+.005*px) for (a,bb),(px,py) in zip(pts,shape)],tri([Vector((a,bb,z)) for a,bb in pts]),'relief_top',[(.5+(a-x)/w*.36,.5+(bb-y)/d*.36) for a,bb in pts])
paving.build()

# Original plants preserve UV2 and seeds. Move only within the revised contact area.
roles=LAYOUT['forest_extension']['layer_roles'];bindings=roles['wind_bindings'];moved_bamboo=[]
for num in [0,1,2,30,31]:
    name='Forest_Bamboo_Role_Main_%02d'%num
    bind=bindings[name];old=Vector((bind['root'][0],-bind['root'][2],bind['root'][1]))
    new=old.copy();new.z=support(new.x,new.y)+.012;delta=new-old
    for label in ['Main','Leaves']:
        ob=SCENE.objects['Forest_Bamboo_Role_%s_%02d'%(label,num)];keep(ob)
        for p in ob.data.vertices:p.co+=delta
        ob.data.update();bindings[ob.name]['root']=[new.x,new.z,-new.y];moved_bamboo.append(ob.name)
new_bamboo=[]
for num,x,y,scale,angle in [(32,-64.0,18.0,.82,.35),(33,-62.6,18.55,.88,-.25),(34,-60.9,18.25,.80,.60),(35,-60.05,17.45,.86,-.45)]:
    srcnum=(num-32)%2;src=bindings['Forest_Bamboo_Role_Main_%02d'%srcnum]
    root=Vector((src['root'][0],-src['root'][2],src['root'][1]));new=Vector((x,y,support(x,y)+.012));cs=math.cos(angle);sn=math.sin(angle)
    for label in ['Main','Leaves']:
        ob=SCENE.objects['Forest_Bamboo_Role_%s_%02d'%(label,srcnum)];cp=ob.copy();cp.data=ob.data.copy();cp.name='Forest_Bamboo_Role_%s_%02d'%(label,num);COL.objects.link(cp)
        for v in cp.data.vertices:
            p=v.co-root;v.co=new+Vector((p.x*cs-p.y*sn,p.x*sn+p.y*cs,p.z*scale))
        cp.data.update();cp.hide_set(False);cp.hide_render=False
        bindings[cp.name]={'root':[new.x,new.z,-new.y],'height':src['height']*scale,'seed':928+num*9.31,'amplitude':.58}
        LAYOUT['forest_extension']['groves'].append({'name':cp.name,'band':'role_main'});new_bamboo.append(cp.name)

# Grass and low fern groups belong to rock/soil margins; quiet camp/path stays open.
grass=Mesh('Forest_Grass_Terminus_Groups');roots=[]
centers=[(-65.5,15.7),(-64.8,17.6),(-63.0,17.9),(-61.8,17.8),(-60.2,16.1),(-58.1,16.2),(-57.1,15.2),
         (-61.0,14.7),(-59.6,14.9),(-58.0,14.7),(-57.0,14.8),(-55.6,14.85),
         (-60.7,10.8),(-59.2,10.3),(-58.2,9.2),(-57.1,8.7),(-55.9,8.0),(-60.7,7.6),(-58.6,6.9),(-56.9,6.0),(-65.8,10.5)]
for i,(x,y) in enumerate(centers):
    for j in range(13):
        a=j*2.4+i*.37;rad=.10+.055*(j%5);cx=x+math.cos(a)*rad;cy=y+math.sin(a)*rad;z=support(cx,cy)+.012
        h=.24+.065*(j%4);direction=Vector((math.cos(a),math.sin(a),0));side=Vector((-direction.y,direction.x,0));root=Vector((cx,cy,z));mid=root+direction*.07+Vector((0,0,h*.63));tip=root+direction*.22+Vector((0,0,h))
        col=[(.73,.89,.55,1),(.86,.94,.63,1),(1.08,1.10,.73,1)][j%3]
        grass.part([root-side*.035,root+side*.035,mid+side*.023,mid-side*.023,tip],[(0,1,2,3),(3,2,4)],'grass_blade',weights=[0,0,.55,.55,1],colors=[col]*5);roots.append([cx,cy,z])
keep(SCENE.objects['Forest_Grass_Terminus']);replace(SCENE.objects['Forest_Grass_Terminus'],grass.build())
ferns=Mesh('Forest_Grass_Terminus_Ferns')
for i,(x,y) in enumerate([(-65.0,15.8),(-63.1,15.9),(-60.3,16.2),(-58.35,16.4),(-59.4,8.5),(-57.7,7.8),(-61.0,10.6)]):
    z=support(x,y)+.015;root=Vector((x,y,z))
    for j in range(5):
        a=j*math.tau/5+i*.61;direction=Vector((math.cos(a),math.sin(a),0));side=Vector((-direction.y,direction.x,0));length=.48+.12*(j%3)
        for k in range(4):
            t=(k+1)/5;c=root+direction*length*t+Vector((0,0,.34*math.sin(t*math.pi*.7)))
            w=.15*(1-t*.65)
            for sign in [-1,1]:
                end=c+side*w*sign+direction*.13+Vector((0,0,-.03));mid=(c+end)*.5+Vector((0,0,.025))
                ferns.part([c,mid-direction*.042,end,mid+direction*.043],[(0,1,2),(0,2,3)],'grass_blade',weights=[t*.4,t*.65,t,t*.65],colors=[(.84,1.02,.65,1)]*4)
ferns.build()

# Refit fire and seat to the natural stone shelf, keeping original animation.
for key,prefixes,extra in [('fire_center',('Cape_Fire_','Cape_Flame_','Cape_Smoke_','Cape_Ember_'),.02),('seat_center',('Cape_Timber_',),.30)]:
    p=rc[key];newz=fh(p[0],-p[2])+extra;dz=newz-p[1]
    for o in SCENE.objects:
        if live(o) and o.name.startswith(prefixes):
            keep(o)
            for v in o.data.vertices:v.co.z+=dz
            o.data.update()
    p[1]=newz
for name in ['forest_cape_exit','cape_neck','cape_entry','cape_center']:p=LAYOUT['anchors'][name];p[1]=fh(p[0],-p[2])
for m in ground.data.materials:
    if m and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image and 'rocky_terminus/floor.png' in n.image.filepath.replace('\\','/'):
                n.image.reload();n.image.pack()
rc['cliff_masses']=[o.name for o in rocks]
data['reference_rework']={'date':'2026-11-19','collection':COL.name,'archive':archive.name,'changed':changed,'retired':retired,'root_bamboo':moved_bamboo+new_bamboo,'rocks':rockspec,'grass_roots':roots,'coast_stations':len(stations),'coast_courses':5,'scope':'Existing outline, compact forest terminus; structural relief and registered paint','art_status':'must inspect actual game views; not reference acceptance'}
(R/'author-pass.json').write_text(json.dumps(data['reference_rework'],indent=2),encoding='utf8')
export('reference-forest-coast-relief-pass1')
