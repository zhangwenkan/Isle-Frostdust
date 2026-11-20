import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Tripo_Grit_Textured_Delivery_20261119'];o=s.objects['Grit_Delivery_Rocks'];me=o.data
parent=list(range(len(me.vertices)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for e in me.edges:
 a,b=map(find,e.vertices)
 if a!=b:parent[b]=a
cs={}
for v in me.vertices:cs.setdefault(find(v.index),[]).append(v.index)
rep=[]
for ids in sorted(cs.values(),key=len,reverse=True)[:45]:
 ps=[o.matrix_world@me.vertices[i].co for i in ids];rep.append({'count':len(ids),'first':ids[0],'bounds':[[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]})
(r/'artifacts/coast-structure-recovery/tripo-components.json').write_text(json.dumps(rep,indent=2),encoding='utf8')
# Load strict baseline, keeping all current scenes intact.
with bpy.data.libraries.load(str(r/'artifacts/rock-stair-composition-review/before/layered_island.blend'),link=False) as (a,b):b.scenes=['Layered_Island_20261116']
s=b.scenes[0];s.name='Coast_Recovery_Strict_Baseline_20261120'
print(json.dumps(rep))
print('BASE',s.name,[(o.name,len(o.data.vertices)) for o in s.objects if o.type=='MESH' and o.name.startswith(('WALK_Forest_Ground','Cape_Terminus','WALK_Cape_Stairs'))])

