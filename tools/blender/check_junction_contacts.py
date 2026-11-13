"""Blender checks: actual ground, authored crown, and nearby plant roots."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-junction-refine-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
land=s.objects['Fish_West_Continuous_Land'];rock=s.objects['Junction_Coast_Sample']
verts=[];faces=[]
for ob in [land]+list(bpy.data.collections['38_Coast_Junction_Sample'].objects):
 offset=len(verts);verts.extend([ob.matrix_world@v.co for v in ob.data.vertices]);faces.extend([tuple(i+offset for i in f.vertices) for f in ob.data.polygons if ob!=land or f.material_index==0])
tree=BVHTree.FromPolygons(verts,faces)
base=bpy.data.objects['JunctionBaseline_Fish_West_Continuous_Land']
oldtree=BVHTree.FromPolygons([base.matrix_world@v.co for v in base.data.vertices],[tuple(f.vertices) for f in base.data.polygons if f.material_index==0])
roots=[]
for ob in s.objects:
 if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection) or not any('Grass' in m.name for m in ob.data.materials if m):continue
 # Each detached blade/card has its own root. Inspect connected components.
 adjacency=[[] for _ in ob.data.vertices]
 for edge in ob.data.edges:
  a,b=edge.vertices;adjacency[a].append(b);adjacency[b].append(a)
 remaining=set(range(len(adjacency)))
 while remaining:
  start=remaining.pop();group=[start];stack=[start]
  while stack:
   for i in adjacency[stack.pop()]:
    if i in remaining:remaining.remove(i);group.append(i);stack.append(i)
  pts=[ob.matrix_world@ob.data.vertices[i].co for i in group];minz=min(p.z for p in pts);low=[p for p in pts if p.z<minz+.025]
  root=sum(low,Vector())/len(low)
  if -23<root.x<-5 and root.y<-1.8:
   hit=tree.ray_cast(Vector((root.x,root.y,20)),Vector((0,0,-1)))[0]
   oldhit=oldtree.ray_cast(Vector((root.x,root.y,20)),Vector((0,0,-1)))[0]
   roots.append({'object':ob.name,'root':list(root),'height_gap':root.z-hit.z if hit else None,'support_change_m':hit.z-oldhit.z if hit and oldhit else None})
report={'roots':roots,'sample_faces':len(rock.data.polygons),'top_normals_up':all(p.normal.z>0 for p in rock.data.polygons if p.index%6==0)}
(O/'contacts-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
author=json.loads((O/'authoring.json').read_text(encoding='utf8'))
author['surface_source']='Five existing self-authored relief modules with original face UVs; new crown junction and recessed inner support, not an exterior smoothing shell'
author['relief_meshes']=[o.name for o in bpy.data.collections['38_Coast_Junction_Sample'].objects if o.name.startswith('Junction_Relief_')]
(O/'authoring.json').write_text(json.dumps(author,indent=2),encoding='utf8')
print('ROOTS',len(roots),'max support height change',max(abs(r['support_change_m']) for r in roots if r['support_change_m'] is not None),'top normals up',report['top_normals_up'])
