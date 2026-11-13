# Rebuild lichen in each rock's LOCAL coordinates, removing any transform ambiguity.
for col in ['02_Cliff_Strata','03_Weathered_Rocks','08_Sea_Reefs','10_Foreground']:
    for ob in list(COL[col].objects):
        if 'Lichen' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
    rocks=[ob for ob in COL[col].objects if ob.type=='MESH' and ('Sculpt' in ob.data.name or 'Buttress' in ob.name)]
    for idx,ob in enumerate(rocks):
        if col=='08_Sea_Reefs':continue
        b=Batch();rr=random.Random(idx+190)
        for p in ob.data.polygons:
            if p.normal.z<.65 or p.area<.02 or rr.random()>.50:continue
            center=p.center
            vs=[]
            for j in p.vertices:
                q=center.lerp(ob.data.vertices[j].co,.78)
                vs.append((q.x,q.z+.012,-q.y))
            b.add(vs,[tuple(range(len(vs)))],0)
        if b.v:
            moss=b.finish(ob.name+'_Crown_Lichen',['moss'],col)
            moss.matrix_world=ob.matrix_world.copy()

# Fine vertical fracture lines and mineral veins with deliberate placement.
cracks=Batch();veins=Batch();rr=random.Random(92)
for ob in list(COL['03_Weathered_Rocks'].objects):
    if 'Lichen' in ob.name:continue
    for p in ob.data.polygons:
        if p.normal.y>-.45 or p.area<.18 or rr.random()>.2:continue
        c=ob.matrix_world@p.center
        start=Vector((c.x,c.z,-c.y-.012))
        length=min(.65,math.sqrt(p.area)*.48)
        tube(cracks,[start+Vector((-.025,length*.3,0)),start,start+Vector((.06,-length*.6,.008))],[.010,.013,.004],5)
cracks.finish('Granite_Hairline_Fissures',['rock_dark'],'03_Weathered_Rocks')

# Ragged grass cap on the sea-facing cliff; roots hang below the soil line.
lip=Batch();roots=Batch();creepers=Batch();rr=random.Random(482)
for i,a in enumerate(OUTLINE):
    b=OUTLINE[(i+1)%len(OUTLINE)]
    if a[1]<1 or b[1]<.8:continue
    steps=max(2,int(math.dist(a,b)/.22))
    for j in range(steps):
        f=j/steps; nf=(j+1)/steps
        x=a[0]*(1-f)+b[0]*f;z=a[1]*(1-f)+b[1]*f
        nx=a[0]*(1-nf)+b[0]*nf;nz=a[1]*(1-nf)+b[1]*nf
        h=height(x,z);nh=height(nx,nz);drop=rr.uniform(.08,.25)
        lip.add([(x,h+.02,z),(nx,nh+.02,nz),(nx,nh-drop,nz+.02),(x,h-drop,z+.02)],[(0,1,2,3)],j%2)
        if j%2==0:
            start=Vector((x,h-.05,z+.04));end=start+Vector((rr.uniform(-.10,.10),-rr.uniform(.3,.65),.04))
            tube(roots,[start,start.lerp(end,.5)+Vector((.03,0,.03)),end],[.012,.008,.003],5)
        if j%6==0:
            start=Vector((x,h,z+.08));length=rr.uniform(.5,1.2)
            pts=[start+Vector((.07*math.sin(k),-k*length/8,.04*k)) for k in range(9)]
            tube(roots,pts,[.01]*9,5)
            for k in range(1,9):
                for side in [-1,1]:leaf(creepers,pts[k],pts[k]+Vector((side*.12,-.04,.05)),.045,.015,k%2)
lip.finish('Cliff_Ragged_Turf_Overhang',['grass','moss'],'01_Terrain')
roots.finish('Exposed_Cliff_Rootlets',['bark_dark'],'06_Ferns_Grass')
creepers.finish('Cliff_Trailing_Leaves',['leaf_dark','leaf'],'06_Ferns_Grass')

for j,(x,z) in enumerate([(-17.2,1.5),(-14,2.2),(-11,2.6),(-8,2.9),(-5,2.9),(-2,2.5),(.8,2.1)]):fern(200+j,x,z,.65)

# Softer, continuous stone faces retain creases; do not smooth the silhouettes away.
for col in ['02_Cliff_Strata','03_Weathered_Rocks','08_Sea_Reefs']:
    for ob in COL[col].objects:
        if ob.type!='MESH' or 'Lichen' in ob.name or 'Foam' in ob.name:continue
        if 'Sculpt' in ob.data.name:
            for p in ob.data.polygons:p.use_smooth=True

save()
print('Lichen transforms corrected; rock fissures, turf overhangs, exposed roots, trailing plants and coastal ferns added.')
