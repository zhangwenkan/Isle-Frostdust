import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-junction-refine-review'
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
data=[]
for o in s.objects:
 if o.type=='MESH' and (o.name.startswith(('Original_Coast_Rock','Integrated_Coast_Rock')) or o.name in ['Fish_West_Continuous_Land','IntegrationBaseline_Land']):
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  data.append(dict(name=o.name,bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],materials=[m.name for m in o.data.materials],uvs=[l.name for l in o.data.uv_layers]))
land=s.objects['Fish_West_Continuous_Land'];bi=[i*26 for i in range(101)]+[2600+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
(O/'current-inspection.json').write_text(json.dumps({'objects':data,'boundary':[list(land.matrix_world@land.data.vertices[i].co) for i in bi]},indent=2),encoding='utf8')
print('PROJECT',bpy.data.filepath,'SCENE',s.name)
print(json.dumps([d for d in data if d['name'].startswith('Original_')]))
