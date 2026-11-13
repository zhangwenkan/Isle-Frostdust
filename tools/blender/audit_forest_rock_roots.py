"""Read actual opaque lower bamboo pixels against rock solids in Blender MCP."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np

R = Path('D:/自己做着玩的/孤屿霜尘')
O = Path(globals().get('AUDIT_OUTPUT',R/'artifacts/forest-rock-root-review'))
O.mkdir(exist_ok=True)
scene = bpy.data.scenes['Island_Refined']
bpy.context.window.scene = scene
assert Path(bpy.data.filepath) == R/'assets/island_blender/nameless_island.blend'

def tree(ob):
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices], [tuple(p.vertices) for p in ob.data.polygons])

floor_tree = tree(scene.objects['PixelForest_Low_Floor'])
def ground(x,y):
    hit = floor_tree.ray_cast(Vector((x,y,40)), Vector((0,0,-1)))[0]
    return hit.z if hit else None

atlas = {}
samples = []
roots = []
for ob in scene.objects:
    if not ob.name.startswith('PixelBamboo_') or any(c.name.startswith('90_') for c in ob.users_collection):
        continue
    mat = ob.data.materials[0]
    tex = next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and '_color' in n.image.name)
    if tex.name not in atlas:
        w,h = tex.size
        a = np.empty(w*h*4,dtype=np.float32)
        tex.pixels.foreach_get(a)
        atlas[tex.name]=(a.reshape(h,w,4)[:,:,3],w,h)
    alpha,w,h = atlas[tex.name]
    # Carriers are authored as an 8 x 30 grid. Sample alpha runs in the
    # lower part of the artwork, including multiple stems per cluster.
    assert len(ob.data.vertices)==9*31, ob.name
    local_grid = [v.co.copy() for v in ob.data.vertices]
    for py in range(2, min(h,int(h*.27)), 5):
        xs = np.flatnonzero(alpha[py]>.65)
        if len(xs)==0: continue
        runs=np.split(xs,np.where(np.diff(xs)>1)[0]+1)
        for run in runs:
            if len(run)<2: continue
            # Center and near-edges catch thick/leaning stems, ignoring
            # transparent parts of the rectangular mesh carrier.
            for px in [run[0]+.2*(run[-1]-run[0]),float(run.mean()),run[-1]-.2*(run[-1]-run[0])]:
                u=(px+.5)/w;v=(py+.5)/h
                gx=u*8;gy=v*30;i=min(7,int(gx));j=min(29,int(gy));fx=gx-i;fy=gy-j
                a=local_grid[j*9+i];b=local_grid[j*9+i+1];c=local_grid[(j+1)*9+i+1];d=local_grid[(j+1)*9+i]
                local=a*(1-fx)*(1-fy)+b*fx*(1-fy)+c*fx*fy+d*(1-fx)*fy
                p=ob.matrix_world@local;g=ground(p.x,p.y)
                if g is not None and -.10<p.z-g<1.15:
                    samples.append((ob.name,p.copy(),p.z-g))
                    if -.07<p.z-g<.16: roots.append((ob.name,p.copy()))

report=[]
for name in ['InkSample_Rock_02','InkSample_Rock_03','InkSample_Rock_04']:
    ob=scene.objects[name];rt=tree(ob);pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    top=max(p.z for p in pts)+1;bottom=min(p.z for p in pts)-1
    collisions={}
    for stem,p,height in samples:
        hit=rt.ray_cast(Vector((p.x,p.y,top)),Vector((0,0,-1)))[0]
        low=rt.ray_cast(Vector((p.x,p.y,bottom)),Vector((0,0,1)))[0] if hit else None
        if hit and low and low.z+.008<p.z<hit.z-.008:
            if stem not in collisions: collisions[stem]=dict(samples=0,example_godot=[p.x,p.z,-p.y],max_depth=0)
            collisions[stem]['samples']+=1
            collisions[stem]['max_depth']=max(collisions[stem]['max_depth'],hit.z-p.z)
    report.append(dict(rock=name,bounds_blender=[list(map(min,zip(*pts))),list(map(max,zip(*pts)))],intersecting_stems=collisions))
phase=globals().get('AUDIT_PHASE','before')
(O/(phase+'-root-audit.json')).write_text(json.dumps(dict(opaque_lower_stem_samples=len(samples),root_samples=len(roots),rocks=report),indent=2),encoding='utf8')
(O/'opaque-root-points.json').write_text(json.dumps([dict(object=n,point_blender=list(p)) for n,p in roots]),encoding='utf8')
print('ROOT_AUDIT',phase,json.dumps(report))
