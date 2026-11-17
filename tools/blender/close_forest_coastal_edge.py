"""Close the newly exposed coastal edge at the original upper path, in Blender."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/bamboo-west-extension-review';COL=bpy.data.collections['43_West_Forest']
assert not SCENE.objects.get('Forest_Coastal_Closure')
ob=SCENE.objects['WALK_Forest_Ground'];bvh=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
edge=[(-1.25,3.26),(1.2,7.5),(.5,15),(-4,24)]
b=Mesh('Forest_Coastal_Closure')
for i,(p,q) in enumerate(zip(edge,edge[1:])):
    n=max(3,round((Vector(q)-Vector(p)).length/1.5))
    for j in range(n):
        a=Vector(p).lerp(Vector(q),j/n);c=Vector(p).lerp(Vector(q),(j+1)/n)
        points=[]
        for v in [a,c]:
            inward=Vector((-.04,.015));hit=bvh.ray_cast(Vector((v.x+inward.x,v.y+inward.y,30)),Vector((0,0,-1)))[0]
            if hit is None:
                nearest=bvh.find_nearest(Vector((v.x,v.y,5)));z=nearest[0].z
            else:z=hit.z
            points.append((v.x,v.y,z))
        for ring in range(3):
            top=1-ring/3;bottom=1-(ring+1)/3
            vs=[]
            for point,f in [(points[0],top),(points[1],top),(points[1],bottom),(points[0],bottom)]:
                x,y,z=point;vs.append((x+(1-f)*.22,y-(1-f)*.08,-.5+(z+.5)*f))
            b.part(vs,[(0,1,2,3)],['rock_a','rock_b','rock_c'][(j+i)%3],[(j*.48,top),(j*.48+.48,top),(j*.48+.48,bottom),(j*.48,bottom)])
b.build();export('west-forest-coastal-closure')
