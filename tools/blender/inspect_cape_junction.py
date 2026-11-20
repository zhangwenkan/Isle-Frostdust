"""Read actual cape junction boundaries through Blender MCP; no edits."""
import bpy,json
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘')
out={}
for name in ['WALK_Forest_NearSlope','WALK_Cape_Neck','Cape_Connection_Shoulder']:
    ob=bpy.data.objects[name];me=ob.data;counts={}
    for p in me.polygons:
        for a,b in zip(p.vertices,list(p.vertices)[1:]+list(p.vertices)[:1]):
            key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
    edges=[e for e,c in counts.items() if c==1]
    verts=sorted(set(i for e in edges for i in e))
    out[name]={'bounds':[[min(v.co[k] for v in me.vertices),max(v.co[k] for v in me.vertices)] for k in range(3)],'west_boundary':[list(me.vertices[i].co) for i in verts if me.vertices[i].co.x<-60.8]}
(root/'artifacts/reference-cape-review/junction-boundaries.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:{'bounds':v['bounds'],'west_boundary':v['west_boundary'][:24]} for k,v in out.items()}))
