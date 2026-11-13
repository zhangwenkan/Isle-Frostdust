import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Island_Refined']
def bvh(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
land=bvh(scene.objects['Fish_West_Continuous_Land']);out=[]
for ob in scene.objects:
    if not ob.name.startswith('InkSample_Rock_'):continue
    tree=bvh(ob);pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    lx,hx=min(p.x for p in pts),max(p.x for p in pts);ly,hy=min(p.y for p in pts),max(p.y for p in pts)
    distances=[];clearances=[]
    for ix in range(1,20):
        for iy in range(1,20):
            x=lx+(hx-lx)*ix/20;y=ly+(hy-ly)*iy/20
            p=tree.ray_cast(Vector((x,y,-10)),Vector((0,0,1)))[0]
            g=land.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
            if p is not None and g is not None:distances.append(p.z-g.z)
    bm=bmesh.new();bm.from_mesh(ob.data)
    nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
    path_gap=min(p.y+.4+math.sin(p.x*.25)*.44 for p in pts)
    assert nonmanifold==0 and volume>0,(ob.name,nonmanifold,volume)
    assert sum(d<=0 for d in distances)/len(distances)>.90,ob.name
    assert path_gap>.65,(ob.name,path_gap)
    out.append({'object':ob.name,'sample_count':len(distances),'below_ground_samples':sum(d<=0 for d in distances),'max_bottom_gap':max(distances),'min_bottom_gap':min(distances),'bounds':[lx,hx,ly,hy],'nonmanifold_edges':nonmanifold,'signed_volume':volume,'minimum_distance_behind_path_center':path_gap})
(ROOT/'artifacts/colored-ink-sample-review/contact-inspection.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out))
