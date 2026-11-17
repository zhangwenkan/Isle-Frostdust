"""Material UVs, fitted sand/rock contact and broken cliff lips via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
for im in bpy.data.images:
    if 'left_finish_textures' in bpy.path.abspath(im.filepath):
        im.unpack(method='REMOVE') if im.packed_file else None
        im.reload();im.pack()
ground=SCENE.objects['WALK_Left_Ground'];gm=mat('ground_unique')
ground.data.materials[4]=gm
for p in ground.data.polygons:
    if p.material_index==4:
        p.use_smooth=True
        for li in p.loop_indices:
            co=ground.data.vertices[ground.data.loops[li].vertex_index].co
            ground.data.uv_layers[0].data[li].uv=((co.x+20)/22,(co.y+4)/21)
# Upper side planes get joints that run down their own faces, rather than
# unrelated repeated image fragments. Preserve the existing cut outline.
for ob in COL.objects:
    if not ob.name.startswith(('Left_Rock','WALK_Left_Ground')):continue
    if ob==ground:
        for p in ob.data.polygons:
            if p.material_index==4:continue
            for li in p.loop_indices:
                co=ob.data.vertices[ob.data.loops[li].vertex_index].co
                ob.data.uv_layers[0].data[li].uv=((co.y if abs(p.normal.x)>.65 else co.x)*.31,co.z*.28)
# Sand reaches under the rock toes and lower stair. Only the seaward perimeter
# descends through the tide; the inland edge is not a second wet shoreline.
old=SCENE.objects['WALK_Left_Beach'];bpy.data.objects.remove(old,do_unlink=True)
outline=[(-16.0,-1.35),(-13.4,-1.6),(-10.5,-2.0),(-7.7,-1.50),(-5.1,-2.05),(-3.6,-.8),(-1.75,-1.50),(-1.12,-3.65),(-2.27,-5.66),(-4.43,-6.73),(-7.02,-7.50),(-9.43,-7.17),(-11.42,-6.53),(-13.1,-5.15),(-14.65,-3.85)]
center=Vector((-7.65,-4.25));n=len(outline);vs=[]
for ring,s in enumerate([0,.58,.86,1.,1.04]):
    for i,(x,y) in enumerate(outline):
        p=center+(Vector((x,y))-center)*s
        inland=i<=6
        z=.148+.009*math.sin(p.x*.9+p.y*.4)
        if not inland:z-=[0,.0,.02,.245,.64][ring]
        vs.append((p.x,p.y,z))
fs=[]
for ring in range(4):
    for i in range(n):j=(i+1)%n;fs.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i))
b=Mesh('WALK_Left_Beach');b.part(vs,fs,'sand',[(p[0]*.105,p[1]*.14) for p in vs]);ob=b.build(smooth=True)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
# A few small, connected broken shoulders at the cliff/sand join.
# Their positions are designed around the existing main masses, not scattered.
for idx,(cx,cy,z,sx,sy) in enumerate([(-13.4,-2.85,.36,.75,.50),(-11.35,-3.15,.24,.64,.45),(-7.9,-2.38,.42,.55,.41),(-2.82,-1.97,.36,.64,.47)]):
 b=Mesh('Left_Rock_ShoreChip_%02d'%idx)
 pts=[(-1,-.4),(-.45,-.95),(.62,-.71),(1,.12),(.52,.78),(-.64,.64)]
 low=[(cx+x*sx,cy+y*sy,-.15) for x,y in pts]
 high=[(cx+x*sx*.91,cy+y*sy*.86,z+(.04 if j in [0,1,5] else -.07)) for j,(x,y) in enumerate(pts)]
 b.part(low+high,[(j,(j+1)%6,(j+1)%6+6,j+6) for j in range(6)],'rock_b')
 b.part(high,tri(high),'rock_top');b.part(low,[tuple(reversed(t)) for t in tri(low)],'rock_c');b.build()
# The foam curve follows the sea-facing edge only; close far inside solid rock.
shore=outline[6:]+outline[:7];lengths=[0.]
for p,q in zip(shore,shore[1:]):lengths.append(lengths[-1]+(Vector(q)-Vector(p)).length)
coast=[]
for i in range(32):
 s=lengths[-1]*i/31;k=next((j for j in range(len(lengths)-1) if lengths[j+1]>=s),len(shore)-2)
 p=Vector(shore[k]).lerp(Vector(shore[k+1]),(s-lengths[k])/(lengths[k+1]-lengths[k]));coast.append([p.x,-p.y])
LAYOUT['shoreline']=coast
export('materials-shore')
