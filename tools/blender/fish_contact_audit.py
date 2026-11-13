import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
ground={}
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
 ob=bpy.data.objects[name];ground[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
def ray(x,z):
 hits=[b.ray_cast(Vector((x,-z,30)),Vector((0,0,-1))) for b in ground.values()]
 return max((p.z for p,n,i,d in hits if p is not None),default=None)
def path_z(x):return .25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
def height(x,z):
 if x>10:return 1.15+math.sin(x*.37)*.18+max(0,-z)*.16
 return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.10+max(0,-z-.3)*.23
path=[]
for a,b in [(-18,4.1),(14.7,23.7)]:
 for i in range(80):
  x=a+(b-a)*i/79;z=path_z(x);y=ray(x,z)
  path.append({'x':x,'model_y':y,'game_y':height(x,z),'error':abs(y-height(x,z)) if y is not None else 100})
max_error=max(x['error'] for x in path)
roots=[]
for ob in scene.objects:
 if ob.name.startswith('Fish_Tree_') and ob.name.endswith('Bark'):
  x,z=ob.location.x,-ob.location.y;y=ray(x,z)
  roots.append({'name':ob.name,'root_origin_y':ob.location.z,'terrain_y':y,'origin_above_terrain':ob.location.z-y})
old=[ob.name for ob in scene.objects if ob.name.startswith(('Pine_','Sample_','Bamboo_','Granite_'))]
report={'walk_samples':len(path),'max_path_height_error_m':max_error,'roots':roots,'old_natural_objects':old,'details':path}
(ROOT/'artifacts/fish-style-review/contact-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert max_error<.035,(max_error,'path mismatch')
assert len(roots)==8 and all(x['origin_above_terrain']<.035 for x in roots)
assert not old,old
print('CONTACT_PASS',len(path),'path samples; max gap',max_error,'m; all 8 tree origins meet the terrain; old trees removed')
