import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/cape-hook-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
objects=[]
for o in s.objects:
 if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 if min(p.x for p in pts)>-19:continue
 if o.name.startswith('Campfire_') or o.name in ['Fish_West_Continuous_Land','Cliff_Fractures_West'] or o.name.startswith('Coast_Low_Grass_'):
  objects.append({'name':o.name,'vertices':len(pts),'materials':[m.name for m in o.data.materials], 'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]})
land=s.objects['Fish_West_Continuous_Land']
ids={i for p in land.data.polygons if p.material_index==0 for i in p.vertices}
pts=[land.matrix_world@land.data.vertices[i].co for i in ids]
sections=[]
for x in [-28,-27,-26,-25,-24,-23,-22,-21,-20,-19]:
 row=[p for p in pts if abs(p.x-x)<.45]
 sections.append({'x':x,'count':len(row),'y_bounds':[min(p.y for p in row),max(p.y for p in row)] if row else []})
report={'objects':objects,'sections':sections,'top_points':[list(p) for p in pts if p.x<-19]}
(O/'inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='top_points'}))
