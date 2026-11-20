"""Bamboo groves, ground cover, cave vines, trees. Blender MCP authoring."""
import bpy
from pathlib import Path
exec((Path('D:/自己做着玩的/孤屿霜尘/tools/blender/pixel_cavern_lib.py')).read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-landscape-1'
P=palette();bamboo=collection('07_Bamboo');green=collection('08_Undergrowth');trees=collection('09_Right_Trees');vines=collection('10_Cave_Vines')

def merge_objects(objects,name):
    active(objects[0])
    for ob in objects:ob.select_set(True)
    bpy.ops.object.join();ob=bpy.context.object;ob.name=name;return ob

# Bamboo groups leave the route open: a dark back wall, side lit middle stems,
# and a few framing stems. Height/lean belongs to the plant, not per-leaf noise.
positions=[]
for row,(y,xmin,xmax,count,z) in enumerate([(9.1,-17,-5.7,18,6.0),(5.1,-17,-4.3,15,4.47),(1.8,-17,-10.5,9,4.47),(-2.6,-17,-10.5,9,4.47)]):
    for i in range(count):
        x=xmin+(xmax-xmin)*(i+.25)/count+rng.uniform(-.25,.25)
        positions.append((x,y+rng.uniform(-.85,.85),z,row,i))
positions.extend([(-3.7,2.35,4.47,1,30),(-3.3,3.4,4.47,1,31),(-4.6,1.9,4.47,1,32),(-17.2,-7.5,.3,3,33),(-16.4,-8.1,.3,3,34),(-15.6,-7.3,.3,3,35)])
for k,(x,y,z,row,ix) in enumerate(positions):
    h=7.0+rng.uniform(-1.1,2.1)+(1 if row==0 else 0);lean=Vector((rng.uniform(-.65,.65),rng.uniform(-.3,.6),0));base=Vector((x,y,z-.08))
    stalkpts=[tuple(base+Vector((0,0,h*t))+lean*t*t) for t in [0,.25,.5,.75,1]]
    stem=tube('Bamboo_Stem_%02d'%k,stalkpts,.105,bamboo,P['bamboo_dark'] if row==0 else P['bamboo'],radii=[.105,.098,.083,.065,.036],sides=8)
    nodes=[]
    for j in range(1,int(h/.72)):
        t=j*.72/h;q=base+Vector((0,0,h*t))+lean*t*t
        nodes.append(tube('Bamboo_Node_temp',[q-Vector((0,0,.018)),q+Vector((0,0,.018))],.112-.060*t,bamboo,P['bamboo_node'],sides=8))
    merge_objects([stem]+nodes,'Bamboo_Stem_%02d'%k)
    leaves=[];branches=[]
    for j,t in enumerate([.43,.59,.74,.87,.97]):
        q=base+Vector((0,0,h*t))+lean*t*t
        angle=(k*.87+j*2.48)%math.tau;ln=1.8 if j in [1,2] else 1.25
        end=q+Vector((math.cos(angle),math.sin(angle),.16))*ln*.55
        branches.append(tube('Bamboo_Branch_temp',[q,end],.023,bamboo,P['bamboo'],radii=[.025,.009],sides=5))
        mats=[P['leaf_dark'],P['leaf']] if row==0 else [P['leaf'],P['leaf_lit']]
        leaves.append(leaf_group('Bamboo_Leaves_temp',end,angle,ln,bamboo,mats,k*8+j,fullness=14))
        leaves.append(leaf_group('Bamboo_Leaves_temp',q,angle+2.8,ln*.75,bamboo,mats,k*8+j+350,fullness=10))
    merge_objects(branches,'Bamboo_Branches_%02d'%k)
    merge_objects(leaves,'Bamboo_Leaves_%02d'%k)

# Grass is built in irregular patches of broader blades. Roots are held in a
# common upward-lighting field, avoiding black/white micro-shadow confetti.
def grass_patch(name,x,y,z,sx,sy,seed,count=40):
    r=random.Random(seed);vs=[];fs=[];ix=[]
    for i in range(count):
        a=r.random()*math.tau;rr=math.sqrt(r.random());xx=x+sx*math.cos(a)*rr;yy=y+sy*math.sin(a)*rr
        h=r.uniform(.12,.34);w=r.uniform(.023,.045);ang=r.random()*math.tau;d=Vector((math.cos(ang),math.sin(ang),0));p=Vector((-d.y,d.x,0));q=Vector((xx,yy,z));k=len(vs)
        vs.extend([tuple(q-p*w),tuple(q+p*w),tuple(q+d*.045+Vector((0,0,h*.63))+p*w*.6),tuple(q+d*.12+Vector((0,0,h))),tuple(q+d*.045+Vector((0,0,h*.63))-p*w*.6)])
        fs.append(tuple(range(k,k+5)));ix.append(1 if i%6==0 else 0)
    ob=mesh(name,vs,fs,green,[P['grass'],P['grass_light']],ix)
    ob.data.normals_split_custom_set([(0,0,1)]*len(ob.data.loops));return ob

patches=[(-15,-3.8,4.48,2.1,.55),(-11.7,-4.4,4.48,1.1,.45),(-9,-1.3,4.48,.36,1.7),(-5.4,-1.5,4.48,.4,1.7),(-3.7,-2.2,4.48,1.25,.45),(-2.6,2.4,4.48,.65,1),(-5.5,3.8,4.48,1.7,1),(-13,3,4.48,2,1.6),(-15,6.7,6.03,1.4,1.3),(-8.8,8,6.03,.9,.5),(-8.9,-8.7,.25,.4,.6),(-5.8,-8.0,.25,.3,.8),(-12.5,-6.3,.25,1.1,.4),(7,-1.2,4.47,.65,.8),(9,-2.5,4.47,1.2,.45),(13.5,-2,4.47,1.8,.6),(15.6,.1,4.47,1.2,1),(8.2,2.2,4.47,.5,.6),(14.8,3.1,4.5,.7,.6)]
for i,(x,y,z,sx,sy) in enumerate(patches):grass_patch('Plant_Grass_Patch_%02d'%i,x,y,z,sx,sy,300+i,80)
for i in range(28):
    x=rng.uniform(-16,-10);y=rng.uniform(-2,7)
    z=6.04 if y>5.8 else 4.48
    grass_patch('Plant_Forest_Cover_%02d'%i,x,y,z,.6,.55,500+i,35)

# Broad moss islands project onto actual new stone surfaces, not floating planes.
def moss_patch(ob,tag):
    coords=[v.co for v in ob.data.vertices];lo=Vector(tuple(min(v[a] for v in coords) for a in range(3)));hi=Vector(tuple(max(v[a] for v in coords) for a in range(3)));c=(lo+hi)*.5
    if hi.z<.3:return
    points=[];r=random.Random(tag)
    cx=c.x-(hi.x-lo.x)*.06;cy=c.y+(hi.y-lo.y)*.05
    for j in range(13):
        ang=j*math.tau/12;rad=.8+r.random()*.2
        points.append((cx+math.cos(ang)*(hi.x-lo.x)*.31*rad,cy+math.sin(ang)*(hi.y-lo.y)*.34*rad))
    vs=[]
    for x,y in [(cx,cy)]+points:
        hit,q,n,idx=ob.ray_cast(Vector((x,y,hi.z+2)),Vector((0,0,-1)))
        if not hit:return
        vs.append(tuple(q+Vector((0,0,.012))))
    mesh('Plant_Moss_'+ob.name,vs,[(0,j+1,j+2) for j in range(12)],green,[P['stone_moss']])
for i,ob in enumerate(list(scene.objects)):
    if ob.type=='MESH' and ob.name.startswith(('Rock_Cliff','Rock_Cave')):moss_patch(ob,i+122)

def fern(name,point,scale,seed):
    r=random.Random(seed);parts=[];o=Vector(point)
    for j in range(7):
        a=j*math.tau/7+r.uniform(-.12,.12);pts=[]
        for k in range(5):
            t=k/4;pts.append(o+Vector((math.cos(a)*t*scale,math.sin(a)*t*scale,(math.sin(t*2.4)*.52+.08)*scale)))
        parts.append(tube(name+'_rib',pts,.012*scale,green,P['fern'],sides=4))
        for k in range(1,5):parts.append(leaf_group(name+'_frond',pts[k],a,.40*scale*(1-k*.14),green,[P['fern'],P['leaf']],seed+j*11+k,fullness=6))
    return merge_objects(parts,name)
for i,(x,y,z,s) in enumerate([(-9.9,-3.8,4.5,.8),(-6,-2,4.5,.65),(-4,-2.7,4.5,.75),(-12,-1,4.5,1),(-14,2,4.5,1.1),(-10,4.8,4.5,.8),(-8.9,-7.1,.3,.75),(-5,-7,.3,.65),(7,-1,4.5,.8),(8,2.5,4.6,.7),(14.7,1.8,4.6,.95),(14,-2.6,4.5,.85),(16,1.0,4.5,1.05)]):fern('Plant_Fern_%02d'%i,(x,y,z),s,900+i)

# Vines originate in roof/root crevices and descend on either jamb; central
# dangling stems stop above the opening to preserve a readable dark entrance.
vine_specs=[(8.0,2.85,8.8,3.0),(8.65,2.7,9.45,2.2),(9.1,2.65,9.75,2.45),(10.05,2.6,10.0,2.0),(10.6,2.55,10.3,1.6),(12.6,2.6,10.2,2.4),(13.55,2.65,9.1,3.5),(14.15,2.6,8.3,3.0),(7.8,3.0,6.0,1.6),(14.9,2.8,5.3,2.4),(7.4,-1.8,4.4,3.0),(12.8,-3.3,4.3,3.8)]
for i,(x,y,z,length) in enumerate(vine_specs):
    pts=[]
    for k in range(10):
        t=k/9;pts.append(Vector((x+.15*math.sin(t*6+i),y-.08*math.sin(t*4),z-length*t)))
    tube('Root_Vine_%02d'%i,pts,.023,vines,P['root'],sides=5)
    vs=[];fs=[];ix=[]
    for j in range(14):
        t=(j+.3)/14;idx=min(8,int(t*9));q=pts[idx].lerp(pts[idx+1],t*9-idx);sign=-1 if j%2 else 1;ln=.24+rng.random()*.12;w=ln*.45;k=len(vs)
        end=q+Vector((sign*ln,-.035,-ln*.55));mid=q.lerp(end,.45)
        vs.extend([tuple(q),tuple(mid+Vector((0,-.06,w))),tuple(end),tuple(mid+Vector((0,.03,-w)))])
        fs.append((k,k+1,k+2,k+3));ix.append(j%4==0)
    ob=mesh('Plant_Vine_Leaves_%02d'%i,vs,fs,vines,[P['leaf'],P['leaf_lit']],ix)
    ob.data.normals_split_custom_set([(.0,-.65,.76)]*len(ob.data.loops))

# Right trees: trunks branch into asymmetric mounds of broad pixel-readable
# leaf plates; normals follow the crown volume rather than each tiny leaf.
def canopy(name,center,radius,seed):
    r=random.Random(seed);ctr=Vector(center);vs=[];fs=[];ix=[];normals=[]
    for i in range(180):
        a=r.random()*math.tau;u=r.uniform(-.8,1);rad=math.sqrt(1-u*u)
        q=ctr+Vector((math.cos(a)*rad*radius[0],math.sin(a)*rad*radius[1],u*radius[2]))
        normal=Vector(((q.x-ctr.x)/radius[0],(q.y-ctr.y)/radius[1],(q.z-ctr.z)/radius[2]+.30)).normalized()
        side=normal.cross(Vector((0,0,1)))
        if side.length<.1:side=Vector((1,0,0))
        side.normalize();up=side.cross(normal).normalized();size=r.uniform(.23,.39);k=len(vs)
        poly=[(-.8,-.45),(-.95,.18),(-.35,.75),(.30,.79),(.90,.2),(.60,-.65),(-.05,-.80)]
        vs.extend([tuple(q+(side*x+up*y)*size) for x,y in poly]);fs.append(tuple(range(k,k+7)));ix.append(1 if u>.4 and i%3==0 else 0)
        normals.extend([tuple(normal)]*7)
    ob=mesh(name,vs,fs,trees,[P['leaf_dark'],P['leaf']],ix)
    ob.data.normals_split_custom_set(normals)
    # Hidden inner volume supplies broad canopy shadows in the renderer.
    proxy=rock('Shadow_'+name,center,tuple(s*.80 for s in radius),trees,[P['leaf_dark']],seed)
    return ob
tree_specs=[(16.5,7.5,7.2,6.0),(16.7,2.0,4.5,7.4),(7.8,7.6,4.5,6.4),(14.1,9.3,8.7,5.1),(18,10,5,9)]
for i,(x,y,z,h) in enumerate(tree_specs):
    trunkpts=[(x,y,z),(x-.15,y+.1,z+h*.34),(x+.25,y+.1,z+h*.68),(x+.1,y,z+h*.92)]
    tube('Wood_Tree_%02d'%i,trunkpts,.25,trees,P['wood_dark'],radii=[.36,.28,.18,.08],sides=9)
    for j,(dx,dy,dz,sx,sy,sz) in enumerate([(-1,.0,.65,1.6,1.5,1.55),(1.1,.2,.75,1.9,1.6,1.6),(.0,-.2,.96,1.8,1.7,1.7),(.3,1.2,.82,1.7,1.6,1.6)]):
        c=(x+dx,y+dy,z+h*dz);tube('Wood_Tree_Branch_%d_%d'%(i,j),[(x,y,z+h*.5),c],.12,trees,P['wood_dark'],radii=[.13,.04],sides=6)
        canopy('Foliage_Tree_%d_%d'%(i,j),c,(sx,sy,sz),1400+i*20+j)

# Shore detail is grouped around the cliff foot; central sand remains quiet.
shore=collection('06_Shore')
for i,(x,y,s) in enumerate([(-10,-7.1,.4),(-9.5,-9,.17),(-12,-9.7,.16),(-4.5,-9,.35),(-15,-8,.24),(-13.4,-6.3,.5),(-5.6,-10.6,.25)]):rock('Rock_Shore_%02d'%i,(x,y,.27),(s,s*.8,s*.6),shore,[P['stone'],P['stone_light']],1600+i)
scene['revision']='pixel-cavern-foliage-2'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'pixel_cavern_coast.blend'))
print(json.dumps({'revision':scene['revision'],'objects':len(scene.objects),'bamboos':len(positions)}))
