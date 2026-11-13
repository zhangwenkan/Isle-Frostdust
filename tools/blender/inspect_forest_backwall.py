import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-backwall-review';O.mkdir(exist_ok=True)
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
floor=s.objects['PixelForest_Low_Floor'];tree=BVHTree.FromPolygons([floor.matrix_world@v.co for v in floor.data.vertices],[tuple(p.vertices) for p in floor.data.polygons])
objects=[]
for ob in s.objects:
 if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
 if ob.name.startswith(('PixelBamboo_','ForestLightShaft_','InkSample_Rock_')) or ob==floor:
  pts=[ob.matrix_world@v.co for v in ob.data.vertices]
  objects.append({'name':ob.name,'root':list(ob.get('root_godot',[])),'layer':ob.get('pixel_bamboo_layer',None),'location':list(ob.location),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'materials':[m.name for m in ob.data.materials]})
rows=[]
for x in [-25,-23,-21,-19,-17,-15,-12,-8,-4,0,2,3]:
 row={'x':x,'hits':[]}
 for depth in [1,2,3,4,5,6,7,8,10,12,15,18,20,22]:
  p=tree.ray_cast(Vector((x,depth,30)),Vector((0,0,-1)))[0]
  row['hits'].append([depth,p.z if p else None])
 rows.append(row)
data={'file':bpy.data.filepath,'objects':objects,'floor_samples':rows}
(O/'inspection.json').write_text(json.dumps(data,indent=2),encoding='utf8')
print('FOREST_BACKWALL_INSPECTED',len(objects))
