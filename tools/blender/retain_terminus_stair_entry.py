"""Restore the complete original stair approach, keep sculpted banks outside it."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
import ast
rc=LAYOUT['reference_cape'];rw=rc['rocky_terminus']['reference_rework'];assert not rw.get('stair_corridor_restored')
src=ast.parse((ROOT/'tools/blender/shape_terminus_near_bank.py').read_text(encoding='utf8'))
for n in src.body:
    if isinstance(n,ast.FunctionDef) and n.name=='drop':exec(compile(ast.Module(body=[n],type_ignores=[]),'bank-drop-field','exec'))
a=Vector(LAYOUT['anchors']['cape_center']);b=Vector(LAYOUT['anchors']['cape_stair_top']);aa=Vector((a.x,-a.z));bb=Vector((b.x,-b.z));axis=bb-aa
def restore(x,y):
    q=Vector((x,y))-aa;t=max(0,min(1,q.dot(axis)/axis.length_squared));dist=(q-axis*t).length
    return drop(x,y)*(1-sm(1.30,1.85,dist))
ground=SCENE.objects['WALK_Forest_Ground'];before=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
for v in ground.data.vertices:v.co.z+=restore(v.co.x,v.co.y)
ground.data.update()
wall=SCENE.objects['Cape_Terminus_Bedrock']
for v in wall.data.vertices:
    p=v.co;h=before.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
    if not h:h=before.find_nearest(Vector((p.x,p.y,6)))[0]
    f=max(0,min(1,(p.z+.65)/(h.z+.65)));p.z+=restore(p.x,p.y)*f
wall.data.update()
rw['stair_corridor_restored']={'radius':1.30,'falloff':1.85,'original_heights':'Added back the exact authored bank drop field within the route capsule','purpose':'Preserve the whole approach, not just its center anchor'}
export('reference-forest-coast-bank-corridor-review')
