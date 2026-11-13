def pine(index,x,z,h,lean):
    rr=random.Random(718+index)
    base=Vector((x,height(x,z),z));wood=Batch();ridges=Batch();needles=Batch()
    def trunk(f):return base+Vector((lean*f*f+.17*math.sin(f*5),h*f,.13*math.sin(f*4)))
    pts=[trunk(j/10) for j in range(11)]
    tube(wood,pts,[h*.047*(1-j/11)**.8+.015 for j in range(11)],12)
    # Raised bark ribs and branching roots make the base read as a tree.
    for k in range(11):
        a=k*math.tau/11
        pts=[trunk(j/10)+Vector((math.cos(a)*h*.047*(1-j/11)**.8,0,math.sin(a)*h*.047*(1-j/11)**.8)) for j in range(9)]
        tube(ridges,pts,[.013]*9,4,k%2)
    for j in range(7):
        a=j*math.tau/7+rr.random()*.3
        endpoint=base+Vector((math.cos(a)*rr.uniform(.5,.95),0,math.sin(a)*rr.uniform(.5,.9)))
        endpoint.y=height(endpoint.x,endpoint.z)+.03
        tube(wood,[base+Vector((0,.35,0)),base.lerp(endpoint,.5)+Vector((0,.10,0)),endpoint],[.15,.10,.015],9)
    for j in range(15):
        f=.36+j*.042
        a=j*2.399+index*.4
        origin=trunk(f)
        length=(1-f)*h*.83+.33
        d=Vector((math.cos(a),.12,math.sin(a)*.70))
        end=origin+d*length+Vector((.18,.12,0))
        bend=origin.lerp(end,.48)-Vector((0,.12,0))
        tube(wood,[origin,bend,end],[.10*(1-f)+.02,.046,.01],8)
        for k in range(5):
            ff=.4+k*.14
            branch=origin.lerp(end,ff)
            side=Vector((-d.z,0,d.x)).normalized()*(.34 if k%2 else -.34)
            twig=branch+side+Vector((0,.16,0))
            tube(wood,[branch,twig],[.024,.007],6)
            for cluster in range(3):
                center=twig+Vector((rr.uniform(-.24,.24),rr.uniform(-.08,.12),rr.uniform(-.24,.24)))
                # Actual interlocking needle fans, with three-dimensional volume.
                for n in range(28):
                    angle=rr.uniform(0,math.tau);rad=rr.uniform(.03,.32)
                    start=center+Vector((math.cos(angle)*rad,rr.uniform(-.07,.07),math.sin(angle)*rad))
                    tip=start+Vector((math.cos(angle)*rr.uniform(.13,.27),rr.uniform(.04,.14),math.sin(angle)*rr.uniform(.13,.27)))
                    idx=rr.choices([0,1,2,3],[12,42,34,12])[0]
                    leaf(needles,start,tip,rr.uniform(.022,.045),.012,idx)
    wood.finish(f'Pine_{index:02d}_Twisted_Trunk_Roots',['bark'],'04_Pine_Trees',True)
    ridges.finish(f'Pine_{index:02d}_Bark_Ridges',['bark_light','bark_dark'],'04_Pine_Trees')
    needles.finish(f'Pine_{index:02d}_Needle_Boughs',['pine_dark','pine','pine_light','pine_tip'],'04_Pine_Trees')

for i,config in enumerate([(-15.5,-2,4.9,-.75),(-10.5,-3.3,6.0,.65),(-7.4,-3.8,4.0,-.45),(-1.8,-1.9,4.8,.75),(18.5,-1.7,5.8,-.65),(22.3,-1,4.6,.6)]):pine(i,*config)

def bamboo(index,x,z,count):
    rr=random.Random(913+index);stems=Batch();nodes=Batch();leaves=Batch();twigs=Batch()
    for i in range(count):
        xx=x+rr.uniform(-.75,.75);zz=z+rr.uniform(-.5,.5);base=Vector((xx,height(xx,zz),zz))
        h=rr.uniform(2.8,4.4);lean=Vector((rr.uniform(-.35,.35),0,rr.uniform(-.15,.15)))
        for j in range(9):
            a=base+Vector((0,h*j/9,0))+lean*(j/9)**2
            b=base+Vector((0,h*(j+1)/9,0))+lean*((j+1)/9)**2
            tube(stems,[a,b],[.045,.041],10,i%2)
            tube(nodes,[b-Vector((0,.022,0)),b+Vector((0,.018,0))],[.054,.050],12)
            if j>=4:
                for side in [-1,1]:
                    end=b+Vector((side*rr.uniform(.35,.65),.20,rr.uniform(-.2,.2)))
                    tube(twigs,[b,end],[.012,.003],6)
                    for k in range(7):
                        start=b.lerp(end,.2+k*.11)
                        tip=start+Vector((side*rr.uniform(.16,.32),rr.uniform(-.22,-.04),(-1 if k%2 else 1)*rr.uniform(.1,.22)))
                        leaf(leaves,start,tip,.026,.025,k%3)
    stems.finish(f'Bamboo_{index}_Segmented_Culms',['bamboo','bamboo_light'],'05_Bamboo',True)
    nodes.finish(f'Bamboo_{index}_Raised_Nodes',['bamboo_node'],'05_Bamboo',True)
    twigs.finish(f'Bamboo_{index}_Fine_Twigs',['bamboo'],'05_Bamboo',True)
    leaves.finish(f'Bamboo_{index}_Lanceolate_Leaves',['leaf_dark','leaf','leaf_tip'],'05_Bamboo')

bamboo(0,-4.4,-2.5,10);bamboo(1,16.5,-1.1,8)

def fern(index,x,z,size,col='06_Ferns_Grass',y=None):
    rr=random.Random(573+index);b=Batch();stems=Batch();base=Vector((x,height(x,z)+.035 if y is None else y,z))
    for j in range(8):
        a=j*math.tau/8+rr.random()*.3;length=size*rr.uniform(.65,1)
        d=Vector((math.cos(a),0,math.sin(a)));side=Vector((-d.z,0,d.x))
        def frond(t):return base+d*length*t+Vector((0,size*(.08+.72*math.sin(t*math.pi*.80)),0))
        pts=[frond(k/12) for k in range(13)]
        tube(stems,pts,[.012*(1-k/15)*size for k in range(13)],5)
        for k in range(1,13):
            t=k/13; start=frond(t);span=size*.18*math.sin(t*math.pi)**.7
            for sign in [-1,1]:
                end=start+side*span*sign+d*size*.11+Vector((0,-.035,0))
                leaf(b,start,end,size*.022,.015,(j+k)%3)
                # Each pinna has a distinct pointed silhouette.
    b.finish(f'Fern_{index:03d}_Divided_Fronds',['leaf_dark','leaf','leaf_tip'],col)
    stems.finish(f'Fern_{index:03d}_Rachis',['bamboo_light'],col)

for i in range(52):
    x=R.uniform(-18.2,24);z=R.uniform(-3.7,3.1)
    outline=OUTLINE if x<5 else EAST
    if not inside(x,z,outline) or abs(z-path_z(x))<.92:continue
    fern(i,x,z,R.uniform(.45,.95))

# Vegetation is built in local patches for culling and separate editing.
for patch in range(18):
    grass=Batch();seed_heads=Batch();rr=random.Random(1823+patch)
    lo=-18.6+patch*2.5;hi=lo+2.5
    for tuft in range(25):
        x=rr.uniform(lo,hi);z=rr.uniform(-4,3.5);outline=OUTLINE if x<5 else EAST
        if not inside(x,z,outline) or abs(z-path_z(x))<.8:continue
        y=height(x,z)+.015
        for j in range(rr.randint(6,12)):
            a=rr.uniform(0,math.tau);h=rr.uniform(.12,.42)
            start=Vector((x+rr.uniform(-.07,.07),y,z+rr.uniform(-.07,.07)))
            tip=start+Vector((math.cos(a)*h*.45,h,math.sin(a)*h*.45))
            mid=start.lerp(tip,.5)+Vector((0,.05,0))
            leaf(grass,start,tip,rr.uniform(.010,.024),.02,rr.randrange(3))
            if j%11==0:
                tube(seed_heads,[tip-Vector((0,.04,0)),tip+Vector((0,.055,0))],[.013,.004],5)
    if grass.v:grass.finish(f'Wild_Grass_Patch_{patch:02d}',['grass_dark','grass_mid','grass_tip'],'06_Ferns_Grass')
    if seed_heads.v:seed_heads.finish(f'Wild_Seed_Heads_{patch:02d}',['dry_grass'],'06_Ferns_Grass')

# Curved fronds and a small rock bank frame only the extreme foreground.
for side in [-1,1]:
    sculpt_rock('Foreground_Bank_'+str(side),(side*15,-3.8,21),(5,2,3),'10_Foreground',seed=600+side)
    for j in range(5):fern(100+j+(10 if side==1 else 0),side*(12.7+j*.8),21+j*.5,2.1,'10_Foreground',y=-.3+j*.12)
save()
print('Six individually branched pines, true needle fans, jointed bamboo, divided fern fronds and grass patches saved.')
