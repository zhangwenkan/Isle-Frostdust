"""Beach profile, submerged sand and a separate swash film via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
REVIEW=ROOT/'artifacts/beach-swash-review';TEX=OUT/'beach_swatch'
assert not bpy.data.collections.get('42_Beach_Swash'),'Refine current beach; do not rerun initial build'
old=SCENE.objects['WALK_Left_Beach'];protected={}
for ob in SCENE.objects:
    if ob.type!='MESH' or ob==old or any(c.name.startswith('90_') for c in ob.users_collection):continue
    blob=repr(([(tuple(v.co)) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[[tuple(d.uv) for d in uv.data] for uv in ob.data.uv_layers],list(map(tuple,ob.matrix_world)))).encode()
    protected[ob.name]=hashlib.sha256(blob).hexdigest()
(REVIEW/'protected-geometry.json').write_text(json.dumps(protected,indent=2))
archive=bpy.data.collections.new('90_Before_Beach_Swash');SCENE.collection.children.link(archive)
for c in list(old.users_collection):c.objects.unlink(old)
archive.objects.link(old);old.name='Before_Swash_Beach';old.hide_set(True);old.hide_render=True
COL=bpy.data.collections.new('42_Beach_Swash');SCENE.collection.children.link(COL)
mat('sand_albedo');mat('beach_pebble',(.20,.22,.18,1));mat('swash',(.22,.40,.39,1))
BACK=[(-16.0,-1.30),(-13.6,-1.45),(-11.3,-1.9),(-9.3,-1.4),(-7.4,-1.5),(-5.45,-2.05),(-3.2,-.90),(-1.25,-1.75)]
FRONT=[(-15.9,-3.25),(-13.55,-4.80),(-11.35,-6.20),(-9.30,-6.94),(-7.2,-7.12),(-4.94,-6.60),(-2.55,-5.37),(-.93,-3.51)]
def curve(points,t):
    f=max(0,min(.999999,t))*(len(points)-1);i=int(f);u=f-i
    p0=Vector(points[max(0,i-1)]);p1=Vector(points[i]);p2=Vector(points[min(len(points)-1,i+1)]);p3=Vector(points[min(len(points)-1,i+2)])
    return .5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u)
def beach_point(u,v):
    back=curve(BACK,u);front=curve(FRONT,u);delta=front-back;length=delta.length
    # Meandering sand edge and subtle broad deposits, not a flat slab with a rim.
    undulate=(.09*math.sin(u*19.0)+.04*math.sin(u*41.0))*(sm(.65,1.,v))
    p=back+delta*v+delta.normalized()*undulate
    z=.148+.018*math.sin(p.x*.81+p.y*.39)*sm(.35,.8,v)
    z-=.045*sm(.48,.82,v)+.30*sm(.72,1.08,v)+.83*sm(1.02,1.45,v)
    # The existing beach-to-stair approach remains a shallow, supported surface.
    d,rh,idx,t=route_at(p.x,p.y)
    if idx==0:z=z*sm(.48,.95,d)+(.148+.006*math.sin(p.x))* (1.-sm(.48,.95,d))
    return Vector((p.x,p.y,z)),length
NX=100;NV=48;MAXV=1.45
vs=[];uv=[];coord=[];fs=[];arc=[0.]
for i in range(1,NX+1):arc.append(arc[-1]+(curve(FRONT,i/NX)-curve(FRONT,(i-1)/NX)).length)
for j in range(NV+1):
    v=MAXV*j/NV
    for i in range(NX+1):
        u=i/NX;p,length=beach_point(u,v);vs.append(p);uv.append((u,1-v/MAXV));coord.append((arc[i],(v-1)*length))
for j in range(NV):
    for i in range(NX):
        k=j*(NX+1)+i;fs.extend([(k,k+NX+2,k+1),(k,k+NX+1,k+NX+2)])
b=Mesh('WALK_Left_Beach');b.part(vs,fs,'sand_albedo',uv);sand=b.build(smooth=True)
for p in sand.data.polygons:
    for li in p.loop_indices:sand.data.uv_layers[1].data[li].uv=(coord[sand.data.loops[li].vertex_index][0],1.-coord[sand.data.loops[li].vertex_index][1])
# Author the film on the physical sand and mean sea level, keeping it separate
# from the opaque substrate so future 2D-style water can use the same UV2 field.
film_vs=[Vector((p.x,p.y,max(p.z,-.18)+.009)) for p in vs]
b=Mesh('Beach_Swash_Film');b.part(film_vs,fs,'swash',uv);film=b.build(smooth=True)
for p in film.data.polygons:
    for li in p.loop_indices:film.data.uv_layers[1].data[li].uv=(coord[film.data.loops[li].vertex_index][0],1.-coord[film.data.loops[li].vertex_index][1])
sand['shore_v_compensated']=True;film['shore_v_compensated']=True
# Three distinct little stones in the supplied composition. Their volume and
# contact shadows belong to geometry, not frozen painted pebble silhouettes.
for idx,(u,v,size,rotation) in enumerate([(.35,.43,.25,.2),(.41,.40,.19,-.35),(.46,.32,.12,.7)]):
    p,_=beach_point(u,v);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=p)
    ob=bpy.context.object;ob.name='Left_Beach_Pebble_%02d'%idx
    for c in list(ob.users_collection):c.objects.unlink(ob)
    COL.objects.link(ob)
    ob.scale=(size,size*.73,size*.47);ob.rotation_euler.z=rotation;ob.location.z+=size*.20
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(MATS['beach_pebble'])
    for poly in ob.data.polygons:poly.use_smooth=False
    ob.data.uv_layers.new(name='UVMap');ob.data.uv_layers.new(name='Wind')
coast=[]
for i in range(32):
    p,_=beach_point(i/31,1.);coast.append([p.x,-p.y])
LAYOUT['shoreline']=coast
LAYOUT['beach_swatch']={'collection':COL.name,'shore_coordinates':'UV2.x alongshore metres, UV2.y signed offshore metres','maximum_v':MAXV,'sea_level':-.18,'bounds':{'x':[-18,2],'z':[.5,12]},'water_decision':'Near-shore demonstration only; final ocean technique not selected'}
(REVIEW/'profile.json').write_text(json.dumps({'back':BACK,'front':FRONT,'grid':[NX,NV],'maximum_v':MAXV,'coastline':coast},indent=2))
export('beach-swash')
