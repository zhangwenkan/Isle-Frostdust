"""Compare opaque terrain coverage from the exact Godot gameplay cameras."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-backwall-review'
phase=globals().get('AUDIT_PHASE','review')
s=bpy.data.scenes['Island_Refined']
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
trees={'before':tree(bpy.data.objects['BackwallBaseline_PixelForest_Low_Floor']),'after':tree(s.objects['PixelForest_Low_Floor'])}
data=json.loads((O/(phase+'-camera-rays.json')).read_text(encoding='utf8'));report=[]
for shot in data:
 row={'hero_x':shot['hero_x'],'rays':len(shot['rays'])}
 for stage,t in trees.items():
  total=0;center=0;ncenter=0
  for ray in shot['rays']:
   a=ray['origin'];b=ray['direction'];o=Vector((a[0],-a[2],a[1]));d=Vector((b[0],-b[2],b[1]))
   p=t.ray_cast(o,d,70)[0];blocked=p is not None
   total+=int(blocked)
   if 256<=ray['screen'][0]<=1024:
    ncenter+=1;center+=int(blocked)
  row[stage]={'solid_terrain_coverage':total/len(shot['rays']),'center_coverage':center/ncenter}
 report.append(row)
floor=s.objects['PixelForest_Low_Floor'];floor.data.calc_loop_triangles()
inverted=0;degenerate=0
for t in floor.data.loop_triangles:
 ps=[floor.matrix_world@floor.data.vertices[i].co for i in t.vertices]
 n=(ps[1]-ps[0]).cross(ps[2]-ps[0])
 if t.material_index in [0,2] and n.z<-.000001:inverted+=1
 if n.length<1e-9:degenerate+=1
result={'camera_coverage':report,'note':'Screen x5%-95%, y4%-59%; opaque forest terrain only, alpha bamboo excluded. Coverage is geometric support, not an art approval.','degenerate_triangles':degenerate,'negative_top_orientation_count':inverted}
(O/(phase+'-coverage.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
print('BACKWALL_COVERAGE',json.dumps(result))
