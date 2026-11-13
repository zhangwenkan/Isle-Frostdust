import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/west-cape-extension-review';O.mkdir(exist_ok=True)
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
report={'file':bpy.data.filepath,'objects':[],'sections':[]}
for o in s.objects:
 if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if lo[0]<-13 and hi[2]>-2 and (hi[0]<6 or o.name in ['Fish_West_Continuous_Land','PixelForest_Low_Floor','Open_Sea']):
  report['objects'].append({'name':o.name,'bounds':[lo,hi],'verts':len(pts),'materials':[m.name for m in o.data.materials]})
land=s.objects['Fish_West_Continuous_Land'];top={i for p in land.data.polygons if p.material_index==0 for i in p.vertices}
for x in [-19,-18,-17,-16,-15,-14,-13,-12]:
 pts=[land.matrix_world@land.data.vertices[i].co for i in top if abs((land.matrix_world@land.data.vertices[i].co).x-x)<.25]
 report['sections'].append({'x':x,'points':[[round(p.x,3),round(-p.y,3),round(p.z,3)] for p in pts]})
(O/'inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('WEST_EXTENSION_INSPECTION',len(report['objects']))
