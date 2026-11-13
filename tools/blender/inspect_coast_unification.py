import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-unification-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
rows=[]
for o in s.objects:
 if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
 if not (o.name.startswith(('PixelForest','Cliff_','Fish_West','InkIsland','Coast_Low','ForestForeground','InkSample_Rock'))):continue
 ps=[o.matrix_world@v.co for v in o.data.vertices]
 rows.append({'name':o.name,'vertices':len(ps),'polygons':len(o.data.polygons),'bounds':[[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]],'materials':[m.name for m in o.data.materials],'uvs':[uv.name for uv in o.data.uv_layers]})
o=s.objects['Fish_West_Continuous_Land'];ps=[o.matrix_world@v.co for v in o.data.vertices]
land=[{'i':i,'rear':list(ps[i*26]),'front':list(ps[i*26+25])} for i in range(101)]
floor=s.objects['PixelForest_Low_Floor'];pts=[floor.matrix_world@v.co for v in floor.data.vertices]
floorrows=[]
for d in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]:
 group=[p for p in pts if d<=p.y<d+1]
 if group:floorrows.append({'depth':d,'xmin':min(p.x for p in group),'xmax':max(p.x for p in group),'zmax':max(p.z for p in group)})
(O/'inspection.json').write_text(json.dumps({'objects':rows,'land_rows':land,'floor_rows':floorrows},indent=2),encoding='utf8')
print(json.dumps({'objects':rows,'floor_rows':floorrows}))
