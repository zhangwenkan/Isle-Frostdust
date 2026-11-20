import bpy,json,array,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘')
S=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=S
def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def fp(o):
    m=o.data;a=array.array('f',[0])*len(m.vertices)*3;m.vertices.foreach_get('co',a)
    b=array.array('i',[0])*len(m.loops);m.loops.foreach_get('vertex_index',b)
    h=hashlib.sha256(a.tobytes()+b.tobytes())
    for u in m.uv_layers:
        c=array.array('f',[0])*len(u.data)*2;u.data.foreach_get('uv',c);h.update(c.tobytes())
    return dict(hash=h.hexdigest(),matrix=[list(r) for r in o.matrix_world])
O=R/'artifacts/forest-rocky-terminus-rework'
if not (O/'before/object-state.json').exists():(O/'before/object-state.json').write_text(json.dumps({o.name:fp(o) for o in S.objects if live(o)},indent=2),encoding='utf8')
g=S.objects['WALK_Forest_Ground'];t=BVHTree.FromPolygons([v.co for v in g.data.vertices],[list(p.vertices) for p in g.data.polygons])
hits={}
for x in [-67,-65,-63,-61,-59,-57,-54]:
    hits[x]=[]
    for y in [7,9,11,13,15,17,19,21,24]:
        p=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0];hits[x].append([y,p.z if p else None])
(O/'source-inspection.json').write_text(json.dumps({'file':bpy.data.filepath,'scene':S.name,'floor':hits,'materials':[(m.name,[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]) for m in bpy.data.materials if m.use_nodes and m.name.startswith(('ForestRole','RC_'))]},indent=2),encoding='utf8')
print(json.dumps({'scene':S.name,'floor':hits,'active_meshes':sum(live(o) for o in S.objects)}))
