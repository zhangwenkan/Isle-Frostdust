"""Full left terrain, articulated rock masses and shoreline via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
assert COL is None,'Left finish already exists; refine it instead'
COL=bpy.data.collections.new('41_Left_Finish');SCENE.collection.children.link(COL)
archive=bpy.data.collections.new('90_Before_Left_Finish');SCENE.collection.children.link(archive)
protected={};retired=[]
for ob in list(SCENE.objects):
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    replace=(any(c.name=='40_Spatial_Foundation' for c in ob.users_collection) and ob.name!='Space_Cave_Lining') or ob.name=='Land_Relief' or (ob.name.startswith('WALK_Route_') and int(ob.name[-2:]) in [0,2,3,7,8,9,10,11,12])
    if replace:
        retired.append(ob.name)
        for c in list(ob.users_collection):c.objects.unlink(ob)
        archive.objects.link(ob);ob.name='Before_Left_'+ob.name;ob.hide_render=True;ob.hide_set(True)
    else:
        blob=repr(([(tuple(v.co)) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[[tuple(d.uv) for d in uv.data] for uv in ob.data.uv_layers],list(map(tuple,ob.matrix_world)))).encode()
        protected[ob.name]=hashlib.sha256(blob).hexdigest()
(REVIEW/'protected-geometry.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
(REVIEW/'retired-objects.json').write_text(json.dumps(retired,indent=2),encoding='utf-8')

outline=[(-17.2,-1.0),(-15.2,-2.05),(-12.5,-2.0),(-10,-2.6),(-8.1,-2.3),(-6.7,-1.8),(-5.75,-.30),(-3.80,-.30),(-3.2,-1.23),(-1.22,-.78),(.72,.7),(.75,2.38),(-1.25,3.26),(-3.1,4.18),(-4.5,5.8),(-6.3,7.4),(-7.9,9.4),(-9.6,10.1),(-10.0,12.4),(-12.4,14.3),(-15.6,15.1),(-18,13.2),(-18.6,9.9),(-18.1,6.2),(-18.5,2.7)]
# A watertight volume with a properly subdivided top. Side rings follow the
# designed ground, not a triangulated plane cutting through a separate grass cap.
vs=[];fs=[];mi=[];n=len(outline)
for ring,f in enumerate([0,.17,.57,.83,1.]):
    for i,(x,y) in enumerate(outline):
        tangent=Vector(outline[(i+1)%n])-Vector(outline[(i-1)%n]);outward=Vector((tangent.y,-tangent.x)).normalized()
        spread=[.11,.22,.10,.015,0][ring]
        if 5<=i<=8:spread=0
        z=-.65+(height(x,y)+.65)*f
        vs.append((x+outward.x*spread,y+outward.y*spread,z))
for ring in range(4):
    for i in range(n):
        j=(i+1)%n;fs.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i));mi.append(i%4)
fs.extend([tuple(reversed(t)) for t in tri(vs[:n])]);mi.extend([2]*(n-2))
for t in tri(vs[4*n:]):fs.append(tuple(4*n+i for i in t));mi.append(4)
me=bpy.data.meshes.new('WALK_Left_Ground');me.from_pydata(vs,[],fs);me.update()
for m in [MATS['rock_a'],MATS['rock_b'],MATS['rock_c'],MATS['rock_d'],MATS['grass']]:me.materials.append(m)
for p,i in zip(me.polygons,mi):p.material_index=i
bm=bmesh.new();bm.from_mesh(me)
topfaces=[f for f in bm.faces if f.material_index==4];edges=set(e for f in topfaces for e in f.edges)
bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=13,use_grid_fill=True)
for v in {v for f in bm.faces if f.material_index==4 for v in f.verts}:v.co.z=height(v.co.x,v.co.y)
bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if f.material_index==4])
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
ob=bpy.data.objects.new('WALK_Left_Ground',me);COL.objects.link(ob)
uv=me.uv_layers.new(name='UVMap');wind=me.uv_layers.new(name='Wind')
for p in me.polygons:
    for li in p.loop_indices:
        co=me.vertices[me.loops[li].vertex_index].co
        uv.data[li].uv=(co.x*.31,co.y*.31) if p.material_index==4 else ((co.y if abs(p.normal.x)>abs(p.normal.y) else co.x)*.28,co.z*.29)

# Each exposed rock has its own authored outline, cap break and leaning face.
# Rock feet are broad, partly embedded and lower than the continuous ledge.
rocks=[
('WestShoulder',(-15.20,-1.95),[(-1.30,-.22),(-.65,-.87),(.36,-.90),(1.20,-.25),(.91,.79),(-.92,.85)],2.28,(-.21,.18),[.15,-.04,-.23,.03,.21,.11]),
('FrontMass',(-12.25,-2.30),[(-1.38,-.45),(-.68,-.98),(.62,-.76),(1.48,-.05),(.85,.78),(-.75,.63)],2.76,(.24,.08),[-.12,-.20,.07,.20,.16,-.05]),
('LowShelf',(-10.27,-3.00),[(-1.14,-.58),(-.18,-.83),(.91,-.47),(1.16,.51),(.13,.91),(-.97,.37)],1.06,(-.08,-.09),[.09,-.04,-.16,.17,.18,.04]),
('StairLeftWall',(-7.40,-1.84),[(-1.13,-.32),(-.40,-.81),(.65,-.65),(1.10,.33),(.39,.84),(-1.05,.54)],2.47,(-.18,.20),[-.15,.11,-.03,.13,.22,.10]),
('StairLeftFoot',(-7.05,-2.74),[(-.87,-.48),(-.14,-.65),(.73,-.14),(.62,.58),(-.56,.66)],.82,(.12,.1),[.08,-.10,-.02,.16,.06]),
('StairRightMass',(-2.45,-1.04),[(-1.11,-.30),(-.61,-.86),(.43,-.87),(1.35,-.07),(.70,.86),(-.70,.78)],2.57,(.13,.14),[.14,.03,-.25,-.03,.14,.2]),
('RightLowFoot',(-1.43,-1.65),[(-.87,-.40),(-.05,-.65),(.95,-.18),(.83,.46),(-.43,.70)],1.18,(-.15,.04),[-.14,.09,.16,.06,-.06]),
('WestMidLedge',(-17.90,4.70),[(-.85,-1.17),(.65,-1.01),(1.1,-.11),(.92,1.08),(-.73,.98),(-1.05,.03)],3.42,(.18,-.12),[.04,.13,.0,-.15,.20,.12]),
('UpperWestFace',(-17.7,9.1),[(-.94,-1.21),(.56,-1.03),(1.06,-.17),(.66,1.18),(-.65,1.06),(-1.11,.17)],4.93,(.15,-.16),[-.10,.11,.21,-.01,.15,.10])]
for idx,(name,(cx,cy),plan,h,lean,dz) in enumerate(rocks):
    vs=[];count=len(plan)
    for ring in range(4):
        scale=[.90,1.02,.96,.79][ring]
        for i,(x,y) in enumerate(plan):
            xx=cx+x*scale+lean[0]*ring/3;yy=cy+y*scale+lean[1]*ring/3
            z=[-.44,h*.24,h*.80,h][ring]
            if ring==3:z+=dz[i]
            if ring==2:z+=dz[i]*.38
            vs.append((xx,yy,z))
    b=Mesh('Left_Rock_'+name)
    for ring in range(3):
        for i in range(count):
            j=(i+1)%count;ids=[ring*count+i,ring*count+j,(ring+1)*count+j,(ring+1)*count+i]
            points=[vs[k] for k in ids]
            # Full-height continuous side UV; no reset at each triangle.
            uv=[(0,ring/3),(1,ring/3),(1,(ring+1)/3),(0,(ring+1)/3)]
            b.part(points,[(0,1,2,3)],['rock_a','rock_b','rock_c','rock_d'][(i+idx)%4],uv)
    top=vs[3*count:];b.part(top,tri(top),'rock_top',[(p[0]*.39,p[1]*.39) for p in top])
    b.part(vs[:count],[tuple(reversed(t)) for t in tri(vs[:count])],'rock_c')
    b.build()

# Sand has a broad resting area, bank slope and a wet perimeter below the tide.
beach=[(-14.7,-2.6),(-12.5,-3.0),(-10.8,-3.5),(-8.8,-3.1),(-6.5,-3.18),(-5.45,-3.24),(-4.1,-3.0),(-3.0,-2.3),(-1.90,-2.9),(-1.35,-4.25),(-2.27,-5.66),(-4.43,-6.73),(-7.02,-7.50),(-9.43,-7.17),(-11.42,-6.53),(-13.1,-5.15),(-14.65,-3.85)]
if sum(beach[i][0]*beach[(i+1)%len(beach)][1]-beach[(i+1)%len(beach)][0]*beach[i][1] for i in range(len(beach)))<0:beach.reverse()
center=Vector((-7.65,-4.76));vs=[];n=len(beach)
for ring,s in enumerate([0, .70,1.,1.065]):
    for x,y in beach:
        p=center+(Vector((x,y))-center)*s
        z=[.15,.10,-.075,-.54][ring]
        if ring<2:z+=.018*math.sin(p.x*.9+p.y*.3)
        vs.append((p.x,p.y,z))
fs=[]
for ring in range(3):
    for i in range(n):j=(i+1)%n;fs.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i))
# Remove coincident central fan vertices before export.
b=Mesh('WALK_Left_Beach');b.part(vs,fs,'sand',[(p[0]*.14,p[1]*.21) for p in vs]);beach_ob=b.build(smooth=True)
bm=bmesh.new();bm.from_mesh(beach_ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(beach_ob.data);bm.free()
shore=beach+[beach[0]];lengths=[0.]
for p,q in zip(shore,shore[1:]):lengths.append(lengths[-1]+(Vector(p)-Vector(q)).length)
coast=[]
for i in range(32):
    s=lengths[-1]*i/31;k=next((j for j in range(len(lengths)-1) if lengths[j+1]>=s),len(shore)-2);p=Vector(shore[k]).lerp(Vector(shore[k+1]),(s-lengths[k])/(lengths[k+1]-lengths[k]));coast.append([p.x,-p.y])
LAYOUT['shoreline']=coast;LAYOUT['left_finish']={'collection':COL.name,'retired':retired,'scope':'full left beach, cliffs, terraces, stairs, upper path and bamboo'}
(REVIEW/'shore-and-outline.json').write_text(json.dumps({'outline':outline,'beach':beach},indent=2),encoding='utf-8')
print('GLTF COLOR OPTIONS',[k for k in bpy.ops.export_scene.gltf.get_rna_type().properties.keys() if 'color' in k])
export('terrain')
