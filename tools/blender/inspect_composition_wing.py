"""Locate the rendered wing on the actual Blender ground mesh, read only."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.scenes['Layered_Island_20261116'].objects['WALK_Forest_Ground'];me=o.data
t=BVHTree.FromPolygons([v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
loc,n,i,d=t.find_nearest(Vector((-54.849754,.98184,2.545206)))
rows=[]
for p in me.polygons:
 if any(v in p.vertices for v in me.polygons[i].vertices):
  rows.append({'index':p.index,'center':list(p.center),'normal':list(p.normal),'area':p.area,'vertices':[list(me.vertices[v].co) for v in p.vertices]})
r=Path('D:/自己做着玩的/孤屿霜尘/artifacts/rock-stair-composition-review')
(r/'wing-source-faces.json').write_text(json.dumps({'hit_face':i,'rows':rows},indent=2),encoding='utf8')
print(json.dumps({'hit_face':i,'rows':rows}))
