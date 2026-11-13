import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Island_Refined']
def bvh(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
land=bvh(scene.objects['Fish_West_Continuous_Land']);out=[]
for ob in scene.objects:
    if not ob.name.startswith('InkSample_Rock_') or any(c.name.startswith('90_') for c in ob.users_collection):continue
    tree=bvh(ob);pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    lx,hx=min(p.x for p in pts),max(p.x for p in pts);ly,hy=min(p.y for p in pts),max(p.y for p in pts)
    distances=[];heights=[]
    for ix in range(1,32):
        for iy in range(1,32):
            x=lx+(hx-lx)*ix/32;y=ly+(hy-ly)*iy/32
            p=tree.ray_cast(Vector((x,y,-10)),Vector((0,0,1)))[0]
            top=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
            g=land.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
            if p is not None and g is not None:
                distances.append(p.z-g.z)
                heights.append(top.z-g.z)
    bm=bmesh.new();bm.from_mesh(ob.data)
    nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
    path_gap=min(p.y+.4+math.sin(p.x*.25)*.44 for p in pts)
    embedded=sum(d<=0 for d in distances)/len(distances)
    assert nonmanifold==0 and volume>0,(ob.name,nonmanifold,volume)
    assert path_gap>.90,(ob.name,path_gap)
    assert max(heights)>.15,ob.name
    out.append({'object':ob.name,'sample_count':len(distances),'embedded_fraction':embedded,'max_bottom_gap':max(distances),'max_exposed_height':max(heights),'bounds':[lx,hx,ly,hy],'nonmanifold_edges':nonmanifold,'signed_volume':volume,'minimum_distance_behind_path_center':path_gap,'clearance_beyond_walkable_strip':path_gap-.55})
assert len(out)==4,len(out)
(ROOT/'artifacts/stone-spatial-review/contact-inspection.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out))
for item in out:assert item['embedded_fraction']>.98,(item['object'],item['embedded_fraction'])
