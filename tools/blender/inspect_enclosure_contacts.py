import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Island_Refined']
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
land=tree(s.objects['Fish_West_Continuous_Land']);floor=tree(s.objects['PixelForest_Low_Floor'])
def height(t,x,y):
 p=t.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
 return p.z if p else None
rows=[]
for ob in s.objects:
 if not ob.name.startswith('ForestForeground_'):continue
 pts=[ob.matrix_world@v.co for v in ob.data.vertices]
 rows.append({'name':ob.name,'bottom_grid':[[p.x,p.y,p.z,height(land,p.x,p.y)] for p in pts[:9]],'root_meta':list(ob.get('root_godot',[]))})
overlap=[]
for x in [-17,-15,-11,-6,-1,2]:
 for y in [1.5,2.5,4,5.5]:
  a=height(land,x,y);b=height(floor,x,y)
  overlap.append({'x':x,'blender_y':y,'land':a,'floor':b,'gap':None if a is None or b is None else b-a})
print(json.dumps({'foreground':rows,'overlap':overlap}))
print('SINGLE_SOURCES',[(o.name,o.data.materials[0].name) for o in s.objects if o.name.startswith('PixelBamboo_L0_')])
(R/'artifacts/forest-enclosure-review/terrain-contact-inspection.json').write_text(json.dumps({'foreground':rows,'overlap':overlap},indent=2),encoding='utf8')
