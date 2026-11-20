import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];report={}
for name in ['Recovery_WALK_Forest_Ground','Recovery_Cape_Terminus_Bedrock']:
 o=s.objects[name];data=[]
 for v in o.data.vertices:
  p=v.co
  if -65<p.x<-61 and 3<p.y<10:data.append([round(k,3) for k in p])
 report[name]=data[:150]
(r/'artifacts/coast-structure-recovery/notch-vertices.json').write_text(json.dumps(report,indent=2))
print(report)
