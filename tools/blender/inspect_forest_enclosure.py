import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-enclosure-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
active=[o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
report=[]
for o in active:
 p=[o.matrix_world@v.co for v in o.data.vertices]
 lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 if lo[0]<4.5 and hi[0]>-25 and hi[2]>0 and not o.name.startswith('PixelBamboo_'):
  report.append(dict(name=o.name,bounds_blender=[lo,hi],vertices=len(p),materials=[m.name for m in o.data.materials],parent=o.parent.name if o.parent else None))
samples={}
for name in ['Fish_West_Continuous_Land','PixelForest_Low_Floor']:
 o=s.objects[name];t=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
 samples[name]=[]
 for x in [-18,-17.5,-15.2,-14,-12,-11,-9,-6,-3,0,2.5,4.2]:
  row=[x]
  for z in [3,2,.4,-1.7,-4,-8,-12]:
   h=t.ray_cast(Vector((x,-z,30)),Vector((0,0,-1)))[0];row.append(round(h.z,3) if h else None)
  samples[name].append(row)
(O/'scene-inspection.json').write_text(json.dumps(dict(file=bpy.data.filepath,objects=report,samples_x_z3_2_p4_n1p7_n4_n8_n12=samples),indent=2),encoding='utf8')
print('INSPECTED',len(report),'objects',json.dumps(samples))
