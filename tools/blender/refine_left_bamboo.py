"""Actual segmented culms, branches and folded lanceolate leaves via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
archive=bpy.data.collections.new('90_Left_Finish_SparseBamboo');SCENE.collection.children.link(archive)
for ob in list(COL.objects):
    if ob.name.startswith(('Left_Bamboo','Left_Grass')):
        COL.objects.unlink(ob);archive.objects.link(ob);ob.name='Sparse_'+ob.name;ob.hide_set(True);ob.hide_render=True
ground=SCENE.objects['WALK_Left_Ground'];tree=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
beach=SCENE.objects['WALK_Left_Beach'];beach_tree=BVHTree.FromPolygons([v.co for v in beach.data.vertices],[list(p.vertices) for p in beach.data.polygons])
def root_height(x,y,allow_beach=False):
    hit=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
    if hit[0] is None and allow_beach:hit=beach_tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
    return hit[0].z if hit[0] is not None else None
def leaf(builder,base,direction,length,width,roll,weight,tone=1.,material='leaf'):
    base=Vector(base);d=Vector(direction).normalized();side=d.cross(Vector((0,0,1)))
    if side.length<.1:side=Vector((1,0,0))
    side.normalize();normal=side.cross(d).normalized();side=side*math.cos(roll)+normal*math.sin(roll);normal=side.cross(d).normalized()
    points=[base,base+d*length*.28-side*width*.5,base+d*length*.65-side*width*.38,base+d*length+Vector((0,0,-length*.10)),base+d*length*.65+side*width*.38,base+d*length*.28+side*width*.5,base+d*length*.45+normal*width*.18]
    uv=[(.5,0),(0,.28),(.12,.65),(.5,1),(.88,.65),(1,.28),(.5,.45)]
    faces=[(i,(i+1)%6,6) for i in range(6)]
    colors=[(tone,tone,tone,1)]*7
    builder.part(points,faces,material,uv,[weight]*7,colors)

groves=[(-15.5,.30,9,7.10,1.32),(-12.9,2.2,8,7.70,1.30),(-9.5,1.40,7,6.80,1.05),(-1.40,2.1,5,6.40,.64),(-12.5,5.5,8,7.8,1.35),(-5.0,5.3,6,6.40,.66),(-15.6,8.8,9,7.50,1.42),(-8.0,8.8,6,6.80,.62),(-11.0,13.6,7,7.5,.86),(-15.7,13.0,8,7.9,1.26),(-17.5,4.5,6,7.3,.67),(-10.3,5.1,7,7.5,.85),(-12.8,10.6,6,7.3,.67),(-17.1,-1.7,5,6.3,.60),(-14.9,-3.2,5,6.0,.52),(-3.1,-1.5,3,5.3,.36)]
records=[];leaf_count=0;branch_count=0;culm_count=0
for gi,(cx,cy,count,h,radius) in enumerate(groves):
    b=Mesh('Left_Bamboo_%02d'%gi)
    for si in range(count):
        angle=si*2.399+gi*.71;rad=radius*(.20+.73*((si*3+2)%count)/max(1,count-1))
        x=cx+math.cos(angle)*rad;y=cy+math.sin(angle)*rad
        if route_at(x,y)[0]<.92:continue
        base_z=root_height(x,y,allow_beach=True)
        if base_z is None:continue
        H=h*[.91,1.04,.84,1.0,.96,1.08,.88][(si+gi)%7]
        R=[.098,.089,.104,.091,.078][(si+gi)%5];bend=Vector((math.cos(angle+.5),math.sin(angle+.5),0))*(.35+.12*(si%3));base=Vector((x,y,base_z-.025))
        def center(z):return base+Vector((0,0,z))+bend*(z/H)**1.75
        intervals=max(8,round(H/.57));zs=[];radii=[]
        for j in range(intervals+1):
            z=H*j/intervals;rr=R*(1-.46*j/intervals)
            for dz,f in [(-.019,1.03),(0,1.10),(.027,1.07),(.070,.95)]:
                if 0<=z+dz<=H:zs.append(z+dz);radii.append(rr*f)
        order=sorted(range(len(zs)),key=lambda i:zs[i]);zs=[zs[i] for i in order];radii=[radii[i] for i in order]
        tube(b,[center(z) for z in zs],radii,'culm',10,[(z/H)**1.8 for z in zs])
        # Small collars and narrow dark rims make nodes physical, not painted bands.
        for j in range(1,intervals):
            z=H*j/intervals;rr=R*(1-.46*j/intervals)
            tube(b,[center(z-.013),center(z+.017)],[rr*1.13,rr*1.11],'node',10,[(z/H)**1.8]*2)
        culm_count+=1;records.append({'grove':gi,'root':[x,y,base_z],'height':H})
        for k,j in enumerate(range(max(3,intervals//3),intervals,2)):
            z=H*j/intervals;phase=angle+k*2.25+gi*.44
            horizontal=Vector((math.cos(phase),math.sin(phase),0));length=[1.45,1.82,1.37,1.67][(k+si)%4]*(1-.20*j/intervals)
            start=center(z);elbow=start+horizontal*length*.48+Vector((0,0,.28));end=start+horizontal*length+Vector((0,0,.14))
            tube(b,[start,elbow,end],[R*.34,R*.19,.009],'branch',6,[(z/H)**1.8,(min(H,z+.28)/H)**1.8,(min(H,z+.14)/H)**1.8]);branch_count+=1
            for tw in [-1,0,1]:
                begin=elbow.lerp(end,.32 if tw else .76)
                theta=phase+tw*.72;axis=Vector((math.cos(theta),math.sin(theta),-.14));L=.84 if tw else 1.02;tip=begin+axis*L
                tube(b,[begin,tip],[.011,.004],'branch',5,[(z/H)**1.8]*2)
                for li in range(7):
                    t=.09+li*.13;p=begin.lerp(tip,t)
                    side=-1 if li%2 else 1
                    leaf_angle=theta+side*(.62+.10*((li+si)%3))
                    direct=Vector((math.cos(leaf_angle),math.sin(leaf_angle),[-.42,-.20,.05,-.33,-.10][(li+k)%5]))
                    ln=[.44,.58,.49,.62,.40][(li+si+k)%5];w=ln*(.21+.025*((li+gi)%3))
                    weight=(min(H,z+.20)/H)**1.8
                    leaf(b,p,direct,ln,w,(li%3-1)*.44+gi*.1,weight,[.92,1.08,1.0,.86,1.04][(si+li)%5]);leaf_count+=1
        # A light terminal spray keeps the top taper readable.
        for k in range(7):
            phase=angle+k*math.tau/7
            leaf(b,center(H-.16),Vector((math.cos(phase),math.sin(phase),.15-k*.045)),.48,.103,k*.19,1.,.98);leaf_count+=1
    ob=b.build()
    for p in ob.data.polygons:
        if ob.data.materials[p.material_index].name in ['LF_culm','LF_node','LF_branch']:p.use_smooth=True

# Broad, readable grass strokes grouped along path margins and soil/rock edges.
grass=Mesh('Left_Grass_Banks');centers=[]
outlines=json.loads((REVIEW/'shore-and-outline.json').read_text())['outline']
for ei,(p,q) in enumerate(zip(outlines,outlines[1:]+outlines[:1])):
    p=Vector(p);q=Vector(q);count=max(1,int((q-p).length/.60));edge=q-p;inside=Vector((-edge.y,edge.x)).normalized()*.18
    for j in range(count):centers.append((p.lerp(q,(j+.5)/count)+inside,ei+j))
for ei in [2,3,7,8,9,10,11,12]:
    ka,kb=LAYOUT['edges'][ei];a=A[ka];c=A[kb];v=Vector((c.x-a.x,c.y-a.y));side=Vector((-v.y,v.x)).normalized();count=max(1,int(v.length/.67))
    for j in range(count):
        p=Vector((a.x,a.y))+v*((j+.5)/count)
        for sign in [-1,1]:centers.append((p+side*sign*(.90+.08*((j+ei)%3)),j+ei))
accepted=[]
for i,(p,phase) in enumerate(centers):
    if route_at(p.x,p.y)[0]<.73:continue
    z=root_height(p.x,p.y)
    if z is None:continue
    accepted.append((p.x,p.y,z))
    for k in range(7):
        a=k*2.38+phase*.6;radius=.055*(k%3);dx=math.cos(a);dy=math.sin(a);base=Vector((p.x+dx*radius,p.y+dy*radius,z-.018))
        ln=[.24,.31,.19,.36,.26,.29,.22][(k+phase)%7]
        leaf(grass,base,Vector((dx*.22,dy*.22,1)),ln,.055 if k%2 else .045,a*.1,.78,[.89,1.03,.95,1.1][k%4],'grass_blade')
grass.build()
(REVIEW/'vegetation.json').write_text(json.dumps({'culms':culm_count,'primary_branches':branch_count,'geometric_leaves':leaf_count,'grass_tufts':len(accepted),'roots':records},indent=2),encoding='utf-8')
export('vegetation-refined')
