OUTLINE=[(-18.9,-1.7),(-18,-3.5),(-15.6,-4.4),(-12,-4.9),(-8,-4.6),(-4,-3.8),(-.6,-2.7),(3.5,-1.7),(4.8,-.1),(4.1,1.6),(1.7,2.7),(-2.5,3.4),(-6.5,3.6),(-10.2,3.3),(-14,2.6),(-17.3,1.8),(-18.9,.8)]
EAST=[(14,.1),(15.1,-2.3),(18.5,-3.4),(23,-3),(26.5,-.8),(26,3),(22,4.2),(18,3.4),(15,2)]

def inside(x,z,outline):
    yes=False
    for i,a in enumerate(outline):
        b=outline[(i+1)%len(outline)]
        if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]: yes=not yes
    return yes

def terrain_island(outline,name):
    boundary=[]
    for i,a in enumerate(outline):
        b=outline[(i+1)%len(outline)]
        n=max(2,int(math.dist(a,b)/.42))
        for j in range(n):
            t=j/n; boundary.append((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t))
    top=mesh(name+'_Grass_Soil',[(x,height(x,z),z) for x,z in outline],[tuple(range(len(outline)))],['grass'],'01_Terrain')
    bm=bmesh.new();bm.from_mesh(top.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=8,use_grid_fill=True)
    for v in bm.verts:
        x,z=v.co.x,-v.co.y
        v.co.z=height(x,z)+.035*math.sin(x*3+z*2)*min(1,abs(z-path_z(x)))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(top.data);bm.free()
    uv=top.data.uv_layers.active
    for p in top.data.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            co=top.data.vertices[top.data.loops[li].vertex_index].co
            uv.data[li].uv=(co.x*.18,co.y*.18)
    center=Vector((sum(x for x,z in outline)/len(outline),sum(z for x,z in outline)/len(outline)))
    v=[];f=[];mi=[];steps=9; count=len(boundary)
    for k in range(steps):
        frac=k/(steps-1)
        for i,(x,z) in enumerate(boundary):
            radial=(Vector((x,z))-center).normalized()
            # Steep fracture faces, undercut middle, and a widened tidal foot.
            off=[0,.05,.22,-.08,-.26,-.18,.02,.36,.75][k]
            fracture=.13*math.sin(i*.66)+.08*math.sin(i*2.1+k*.7)
            q=Vector((x,z))+radial*(off+fracture)
            y=(1-frac)*height(x,z)+frac*(WATER-.8)
            if k not in (0,8):y+=.10*math.sin(i*.38+k*1.7)
            v.append((q.x,y,q.y))
    for k in range(steps-1):
        for i in range(count):
            j=(i+1)%count;f.append((k*count+i,k*count+j,(k+1)*count+j,(k+1)*count+i))
            mi.append(2 if k>=6 else (3 if k==0 else (1 if (i//5+k)%7==0 else 0)))
    cliff=mesh(name+'_Stratified_Sea_Cliff',v,f,['rock','rock_dark','wet_rock','earth'],'02_Cliff_Strata',mi)
    bevel(cliff,.035,2)
    # Geologic seams track the actual cliff profile rather than random spots.
    seams=Batch()
    for k in [2,4,6]:
        for i in range(0,count-3,4):
            if boundary[i][1]<-1.2:continue
            pts=[Vector(v[k*count+j])+Vector((0,.025,.035)) for j in range(i,min(i+5,count))]
            tube(seams,pts,[.018]*len(pts),5,0)
    seams.finish(name+'_Sedimentary_Seams',['rock_dark'],'02_Cliff_Strata')
    # Pebble shore, saturated algae and thin foam ribbon are separately editable.
    foam=Batch();shore=Batch()
    for i,(x,z) in enumerate(boundary):
        j=(i+1)%count; nx,nz=boundary[j]
        r=(Vector((x,z))-center).normalized();nr=(Vector((nx,nz))-center).normalized()
        foam.add([(x+r.x*.55,WATER+.035,z+r.y*.55),(nx+nr.x*.55,WATER+.035,nz+nr.y*.55),
                  (nx+nr.x*1.8,WATER+.035,nz+nr.y*1.8),(x+r.x*1.8,WATER+.035,z+r.y*1.8)],[(0,1,2,3)])
    ob=foam.finish(name+'_ShoreFoam',['foam'],'08_Sea_Reefs')
    uv=ob.data.uv_layers.active
    for p in ob.data.polygons:
        u=p.index/count
        for li,coords in zip(p.loop_indices,[(u,0),(u+1/count,0),(u+1/count,1),(u,1)]):uv.data[li].uv=coords

def sculpt_rock(name,pos,size,col='03_Weathered_Rocks',wet=False,seed=0):
    rr=random.Random(379+seed)
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
    for v in bm.verts:
        q=v.co.copy(); a=math.atan2(q.y,q.x)
        deform=1+.09*math.sin(a*5+seed)+.055*math.sin(q.z*9+a*2)
        q.x*=deform; q.y*=deform
        q.x+=.20*q.z+.05*math.sin(q.z*12)
        q.z=min(q.z,.77+.08*q.x)
        q.z=max(q.z,-.77)
        # Map local Blender axes to x / depth / elevation.
        v.co=(q.x*size[0],q.y*size[2],q.z*size[1])
    me=bpy.data.meshes.new(name+'_Sculpt');bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);COL[col].objects.link(ob);ob.location=G(pos)
    for key in (['wet_rock','rock_dark','rock'] if wet else ['rock','rock_light','rock_dark']):me.materials.append(MAT[key])
    for p in me.polygons:
        p.material_index=1 if p.normal.z>.6 else (2 if p.normal.z<-.1 else 0)
    bevel(ob,.035,2)
    uv=ob.data.uv_layers.new(name='RockUV')
    for p in ob.data.polygons:
        for li in p.loop_indices:
            co=ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv.data[li].uv=((co.x+co.y*.4)*.25,co.z*.25)
    if not wet:
        moss=Batch()
        for p in me.polygons:
            if p.normal.z>.62 and rr.random()<.65:
                vs=[]
                for idx in p.vertices:
                    q=ob.matrix_world @ me.vertices[idx].co
                    vs.append((q.x,q.z+.025,-q.y))
                moss.add(vs,[tuple(range(len(vs)))],rr.randrange(2))
        if moss.v:moss.finish(name+'_Crown_Lichen',['moss','moss_light'],col)
    return ob

terrain_island(OUTLINE,'West_Island')
terrain_island(EAST,'East_Island')

for start,end,name in [(-18.3,4.5,'West'),(14,24.5,'East')]:
    b=Batch(); x=start
    while x<end-.001:
        nx=min(x+.22,end);wa=.62+.07*math.sin(x*1.7);wb=.62+.07*math.sin(nx*1.7)
        vs=[]
        for xx,zz in [(x,path_z(x)-wa),(nx,path_z(nx)-wb),(nx,path_z(nx)+wb),(x,path_z(x)+wa)]:vs.append((xx,height(xx,zz)+.042,zz))
        b.add(vs,[(0,1,2,3)]);x=nx
    b.finish(name+'_Eroded_Walking_Trail',['path'],'01_Terrain',True)

for i,(x,z,sx,sy,sz) in enumerate([
    (-17,-2.1,1.5,1.0,1.0),(-13.2,-2.4,1.9,1.6,1.3),(-11.6,-3,1.1,1.3,.9),
    (-8.5,-3.1,1.6,1.3,1.1),(-5.6,-2.7,1.65,1.8,1.25),(-3.9,-2.5,.9,1.1,.9),
    (-.3,-1.5,1.15,1.3,.85),(1.5,-.9,.7,.75,.65),(19,-2.6,1.9,1.4,1.3),(22.2,-2.3,1.6,1.4,1.0),
]):sculpt_rock('Granite_Outcrop_%02d'%i,(x,height(x,z)+sy*.3,z),(sx,sy,sz),seed=i)

# Exposed angular strata embedded in the front face of the island.
for i in range(35):
    x=-18+i*.65
    z=2.5+math.sin((x+13)*.17)*.7
    if not inside(x,z-.4,OUTLINE):continue
    y=height(x,z)-R.uniform(1.4,3.4)
    sculpt_rock('Cliff_Ledged_Slab_%02d'%i,(x,y,z),(.65+R.random()*.45,.35+R.random()*.4,.48),'02_Cliff_Strata',seed=200+i)

for i,(x,z,sx,sy) in enumerate([(-16.5,5.7,1.6,1.1),(-13.8,7.2,.7,.5),(-8.7,5.8,1.4,1.1),(-6.1,7.1,.65,.5),(-1.8,5.4,1,.7),(7.7,1.6,1.15,1.2),(10.8,-1.4,.85,.8),(11.6,4,1.5,1.2),(17.3,5.4,1,.8),(-21,.2,.9,.8)]):
    sculpt_rock('Tidal_Reef_%02d'%i,(x,WATER+sy*.25,z),(sx,sy,sx*.75),'08_Sea_Reefs',True,seed=300+i)
    vs=[];fs=[]
    for j in range(33):
        a=j*math.tau/32
        for r in [1,1.65]:vs.append((x+math.cos(a)*sx*r,WATER+.045,z+math.sin(a)*sx*.75*r))
    for j in range(32):fs.append((j*2,(j+1)*2,(j+1)*2+1,j*2+1))
    ob=mesh('ReefFoam_%02d'%i,vs,fs,['foam'],'08_Sea_Reefs')
    for p in ob.data.polygons:
        for li,c in zip(p.loop_indices,[(p.index/32,0),((p.index+1)/32,0),((p.index+1)/32,1),(p.index/32,1)]):ob.data.uv_layers.active.data[li].uv=c

# Broad low distant islands, with no foreground-style speckle.
for i,(x,z,sx,sy) in enumerate([(-33,-65,9,2.3),(-25,-69,5,1.2),(31,-80,11,2.7),(42,-84,6,1.8)]):
    ob=sculpt_rock('Hazy_Islet_%02d'%i,(x,WATER,z),(sx,sy,4),'09_Distant_Isles',seed=400+i)
    ob.data.materials.clear();ob.data.materials.append(MAT['distant'])
    for p in ob.data.polygons:p.material_index=0
mesh('Open_Sea',[(-210,WATER,100),(210,WATER,100),(210,WATER,-130),(-210,WATER,-130)],[(0,1,2,3)],['ocean'],'11_Sea_Surface')
save()
print('Detailed stratified terrain, original UVs, trail, lichen, sea stacks and wave ribbons saved.')
