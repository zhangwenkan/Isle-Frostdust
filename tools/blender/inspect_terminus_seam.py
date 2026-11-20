import bpy,json
from pathlib import Path
o=bpy.data.scenes['Layered_Island_20261116'].objects['WALK_Forest_Ground']
v=[list(v.co) for v in o.data.vertices if abs(v.co.x+54)<.00003]
print(json.dumps({'count':len(v),'y_range':[min(p[1] for p in v),max(p[1] for p in v)],'points':sorted(v,key=lambda p:p[1])[::max(1,len(v)//8)]}))
