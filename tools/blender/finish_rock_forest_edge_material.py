"""MCP: replace the exposed legacy gray test slot with muted bank pigment."""
import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review';s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];bpy.context.window.scene=s
g=s.objects['GameJoin_WALK_Forest_Ground'];report=[]
for i,m in enumerate(g.data.materials):
    if m and 'Composition_Gray' in m.name:
        cp=m.copy();cp.name='ForestBank_Former_Test_Faces';bs=next(n for n in cp.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.052,.072,.027,1);bs.inputs['Roughness'].default_value=.97;g.data.materials[i]=cp
        report.append({'slot':i,'old':m.name,'replacement':cp.name,'face_count':sum(p.material_index==i for p in g.data.polygons)})
(O/'legacy-gray-material-fix.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(report)
