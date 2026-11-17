"""Individual cut slabs, step foundations and curb pieces in Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
assert not SCENE.objects.get('WALK_Left_Stairs_00')
def slab(b,c,right,forward,w,d,h,top,variant=0):
    c=Vector(c);right=Vector(right);forward=Vector(forward);cut=[.035,.054,.043,.062][variant%4]
    plan=[(-w/2+cut,-d/2),(w/2-cut*.5,-d/2),(w/2,-d/2+cut),(w/2,d/2-cut*.7),(w/2-cut,d/2),(-w/2+cut*.6,d/2),(-w/2,d/2-cut),(-w/2,-d/2+cut*.6)]
    vs=[]
    for ring in range(3):
        for x,y in plan:
            factor=1 if ring<2 else .97
            vs.append(c+right*x*factor+forward*y*factor+Vector((0,0,[-h,-.022,0][ring])))
    for ring in range(2):
        for i in range(8):
            j=(i+1)%8;ids=[ring*8+i,ring*8+j,(ring+1)*8+j,(ring+1)*8+i]
            b.part([vs[k] for k in ids],[(0,1,2,3)],'rock_b' if ring==0 else top,[(0,0),(1,0),(1,1),(0,1)])
    points=vs[16:];b.part(points,tri(points),top,[((x+w/2)/w,(y+d/2)/d) for x,y in plan])
    b.part(vs[:8],[tuple(reversed(t)) for t in tri(vs[:8])],'rock_c')
flights=[('stair_bottom','stair_top',15,2.04),('forest_turn','forest_step1',4,1.67),('forest_mid','forest_step2',7,1.70),('forest_landing','forest_end',6,1.65)]
step_counts=[]
for idx,(ka,kb,n,width) in enumerate(flights):
    a=A[ka];z=A[kb];delta=z-a;forward=Vector((delta.x,delta.y,0)).normalized();right=Vector((forward.y,-forward.x,0));length=Vector((delta.x,delta.y,0)).length;tread=length/n;rise=delta.z/n
    b=Mesh('WALK_Left_Stairs_%02d'%idx)
    # The foundation is below slab level, with a complete sawtooth side profile.
    profile=[a-Vector((0,0,.22))]
    for j in range(n):
        p=a+forward*(j*tread);p.z=a.z+(j+1)*rise-.06;profile.extend([p.copy(),p+forward*tread])
    tail=z.copy();tail.z=a.z-.22;profile.append(tail)
    pn=len(profile);vs=[p+right*side*width*.5 for side in [-1,1] for p in profile]
    fs=[(j,(j+1)%pn,(j+1)%pn+pn,j+pn) for j in range(pn)]
    local=[((p-a).dot(forward),p.z,0) for p in profile]
    for t in tri(local):fs.append(tuple(reversed(t)));fs.append(tuple(pn+i for i in t))
    b.part(vs,fs,'rock_b')
    for j in range(n):
        pieces=3 if j%3==1 else 2;offsets=[0]
        widths=[width/pieces]*pieces
        if pieces==2:widths=[width*(.46 if j%2 else .55),0];widths[1]=width-widths[0]
        x=-width/2
        for k,w in enumerate(widths):
            c=a+forward*((j+.5)*tread)+right*(x+w*.5);c.z=a.z+(j+1)*rise+.014
            slab(b,c,right,forward,w-.018,tread-.012,.105,'tread' if (j+k)%3 else 'paving',j+k);x+=w
    # Short fitted curb stones follow the pitch. The outer edge has a bevel.
    group=3 if idx==0 else 2
    for sign in [-1,1]:
        for start in range(0,n,group):
            end=min(n,start+group);p=a+forward*(start*tread)+right*sign*(width*.5+.075);q=a+forward*(end*tread)+right*sign*(width*.5+.075)
            p.z=a.z+start*rise+.15;q.z=a.z+end*rise+.15
            vs=[]
            for down in [.0,-.24]:
                for point,along in [(p,forward*.012),(q,-forward*.012)]:
                    for side in [-1,1]:vs.append(point+along+right*side*.085+Vector((0,0,down)))
            b.part(vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(2,3,7,6),(0,2,6,4)],'rock_a')
    b.build();step_counts.append({'name':b.name,'steps':n,'slab_count':sum(3 if j%3==1 else 2 for j in range(n))})
road=Mesh('WALK_Left_Paving')
for ei in [2,3,7,9,11]:
    ka,kb=LAYOUT['edges'][ei];a=A[ka];b=A[kb];v=b-a;forward=Vector((v.x,v.y,0)).normalized();right=Vector((forward.y,-forward.x,0));length=Vector((v.x,v.y,0)).length
    count=max(1,int(length/.66))
    for j in range(count):
        t=(j+.5)/count;c=a.lerp(b,t);c.z+=.025
        for k,off in enumerate([-.31,.30]):
            along=(.095 if (j+k)%2 else -.07)
            p=c+right*off+forward*along
            slab(road,p,right,forward,.59 if k==0 else .57,length/count*.78,.070,'paving',j+ei+k)
road.build()
(REVIEW/'stonework.json').write_text(json.dumps(step_counts,indent=2),encoding='utf-8')
export('stonework')
