"""MCP static contact and geometry checks, not a full passage audit."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-cape-weight-review';s=bpy.data.scenes['Rock_Cape_Weight_Game_20261119'];bpy.context.window.scene=s
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
stairs=tree(s.objects['WALK_Tripo_Stairs']);sand=tree(s.objects['GameJoin_WALK_Cape_Sand']);rock=tree(s.objects['WALK_Tripo_Rock_Surface']);fit=json.loads((R/'assets/layered_island/tripo_replica/game_assembly.json').read_text())
rows=[]
for key in ['cape_stair_bottom','cape_stair_top','cape_center']:
    p=fit['sample_anchors'][key];pos=Vector((p[0],-p[2],12));row={'anchor':key,'authored':p}
    for label,tr in [('stairs',stairs),('sand',sand),('rock',rock)]:
        hit=tr.ray_cast(pos,Vector((0,0,-1)),30);row[label]=list(hit[0]) if hit[0] else None
    rows.append(row)
report={'static_contact':rows,'meshes':[{ 'name':o.name,'verts':len(o.data.vertices),'faces':len(o.data.polygons),'uv_layers':[u.name for u in o.data.uv_layers]} for o in s.objects if o.type=='MESH']}
(O/'contact-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(rows))
