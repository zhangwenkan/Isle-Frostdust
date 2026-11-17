"""Finish grass clumps and root weights; refresh the final painted albedo maps."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
ground=SCENE.objects['WALK_Left_Ground'];tree=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
if not SCENE.objects.get('Left_Grass_Clusters'):
    clumps=Mesh('Left_Grass_Clusters')
    centers=[(-13.5,-.7),(-11.5,-.4),(-9.7,-.8),(-7.5,-.35),(-6.25,.2),(-2.3,.0),(-1.35,1.0),(-6.1,2.4),(-7.0,3.9),(-8.75,4.7),(-10.5,6.9),(-12.3,8.4),(-13.9,10.2),(-12.4,12.7),(-15.2,4.2),(-16.0,7.1),(-17.1,10.6)]
    for ci,(cx,cy) in enumerate(centers):
        for j in range(4):
            phase=ci*.71+j*2.4;x=cx+math.cos(phase)*(.13+j*.035);y=cy+math.sin(phase)*(.13+j*.035)
            if route_at(x,y)[0]<.74:continue
            hit=tree.ray_cast(Vector((x,y,25)),Vector((0,0,-1)))
            if hit[0] is None:continue
            z=hit[0].z-.008
            for k in range(6):
                angle=k*2.4+ci*.5;dx=math.cos(angle);dy=math.sin(angle);h=[.23,.37,.28,.34,.21,.31][(k+ci)%6];w=.034+.012*(k%3)
                base=Vector((x+dx*.05,y+dy*.05,z));tip=base+Vector((dx*h*.35,dy*h*.35,h));mid=base.lerp(tip,.45)+Vector((0,0,.025));side=Vector((-dy,dx,0))*w
                vs=[base,mid-side,tip,mid+side,mid+Vector((0,0,.018))]
                uv=[(.5,0),(0,.45),(.5,1),(1,.45),(.5,.45)]
                tone=[.95,1.09,1.0,.88][(ci+k)%4]
                clumps.part(vs,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'grass_blade',uv,[0,.45,1,.45,.45],[(tone,tone,tone,1)]*5)
    clumps.build()
for ob in COL.objects:
    if ob.name.startswith('Left_Grass'):
        for p in ob.data.polygons:
            for li in p.loop_indices:ob.data.uv_layers[1].data[li].uv=(ob.data.uv_layers[0].data[li].uv.y,0)
for im in bpy.data.images:
    if 'left_finish_textures' in bpy.path.abspath(im.filepath):
        if im.packed_file:im.unpack(method='REMOVE')
        im.reload();im.pack()
export('ground-finish')
