"""Sculpt the wide foreground into the continuous forest coast using Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
rc=LAYOUT['reference_cape'];rw=rc['rocky_terminus']['reference_rework'];assert not rw.get('near_bank_shaped')
ground=SCENE.objects['WALK_Forest_Ground']
def tree(o):return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
old=tree(ground)
def fh(t,x,y):
    p=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
    return p.z if p else t.find_nearest(Vector((x,y,6)))[0].z
def drop(x,y):
    # Three broad changes of pitch flow diagonally under the road. They are
    # non-walkable bank relief, not a new path, stair or extra upper platform.
    f=sm(-54,-57,x)*sm(-64.3,-61.7,x)
    s=y+.28*(x+60)
    return f*(.50*(1-sm(10,12,s))+.78*(1-sm(8.2,9.7,s))+.78*(1-sm(5.5,7.1,s)))
for v in ground.data.vertices:v.co.z-=drop(v.co.x,v.co.y)
ground.data.update()
wall=SCENE.objects['Cape_Terminus_Bedrock']
for v in wall.data.vertices:
    p=v.co;upper=fh(old,p.x,p.y);amount=drop(p.x,p.y);weight=max(0,min(1,(p.z+.65)/(upper+.65)));p.z-=amount*weight
wall.data.update();ft=tree(ground)
# Maintain a buried foot for the sloping near-side exposures.
for row in rw['rocks']:
    if row['name'].endswith(('Near_Shoulder','Near_Return')):
        ob=SCENE.objects[row['name']];x=row['x'];y=row['y'];dz=min(0,fh(ft,x,y)-.30-row['base'])
        for v in ob.data.vertices:v.co.z+=dz
        ob.data.update();row['base']+=dz
# The corresponding stone drawing becomes grass/soil lower down, rather than
# a solid stone rim on top of a flat green mesa.
trees=[ft]+[tree(SCENE.objects[n]) for n in rc['cliff_masses']]
def support(x,y):
    hits=[t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0] for t in trees]
    return max([p.z for p in hits if p],default=fh(ft,x,y))
g=SCENE.objects['Forest_Grass_Terminus']
for start in range(0,len(g.data.vertices),5):
    p=(g.data.vertices[start].co+g.data.vertices[start+1].co)*.5;dz=support(p.x,p.y)+.012-p.z
    for k in range(5):g.data.vertices[start+k].co.z+=dz
g.data.update()
fern=SCENE.objects['Forest_Grass_Terminus_Ferns'];group=5*(6*5+4*2*4)
for i,(x,y,z) in enumerate(rw['fern_settled']['roots']):
    newz=support(x,y)+.012;dz=newz-z
    for k in range(group):fern.data.vertices[i*group+k].co.z+=dz
    rw['fern_settled']['roots'][i][2]=newz
fern.data.update()
rw['near_bank_shaped']={'maximum_lowering':2.06,'scope':'Near-side bank only, x<-54 and y<12; road/camp/stair stay one walking level','geometry':'Actual Blender through MCP, original outline and UV kept'}
export('reference-forest-coast-bank-review')
