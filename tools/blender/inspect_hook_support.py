import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['Island_Refined'];o=s.objects['Fish_West_Continuous_Land']
t=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
old=Vector((-26.5,.06,1.86));pts=[]
for o in s.objects:
 if not o.name.startswith('CapeHookBaseline_Campfire_'):continue
 pts += [(o.matrix_world@v.co-old)*1.7 for v in o.data.vertices]
scores=[]
best=[]
for ix in range(17):
 for iy in range(17):
  x=-27.2+ix*.12;y=3.0+iy*.16
  hits=[t.ray_cast(Vector((x+p.x,y+p.y,20)),Vector((0,0,-1)))[0] for p in pts]
  if all(p is not None for p in hits):scores.append([x,y,min(p.z for p in hits),max(p.z for p in hits)])
  best.append([sum(p is not None for p in hits),x,y])
print('SUPPORTED_CENTERS',json.dumps(scores))
print('BEST',json.dumps(sorted(best,reverse=True)[:10]),'POINTS',len(pts))
