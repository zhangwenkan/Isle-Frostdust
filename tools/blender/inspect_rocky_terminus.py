import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/自己做着玩的/孤屿霜尘')
out=root/'artifacts/forest-rocky-terminus-review';out.mkdir(exist_ok=True)
s=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=s
objects=[]
for o in s.objects:
    if o.type!='MESH':continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    bounds=[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)]
    archived=any(c.name.startswith('90_') for c in o.users_collection)
    if (bounds[0][0]<-50 and not archived) or o.name.startswith(('Tip_Before_WALK_Forest','Continuity_Before_WALK_Forest')):
        objects.append(dict(name=o.name,bounds=bounds,collections=[c.name for c in o.users_collection],archived=archived,materials=[m.name for m in o.data.materials],uv=[u.name for u in o.data.uv_layers],verts=len(o.data.vertices),polys=len(o.data.polygons)))
floors={}
for name in ['WALK_Forest_Ground','Tip_Before_WALK_Forest_Ground','Tip_Before_WALK_Forest_NearSlope']:
    o=s.objects.get(name)
    if not o:continue
    tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
    floors[name]={}
    for x in [-66,-63.04,-61.24,-60,-57,-54,-50]:
        floors[name][str(x)]=[]
        for y in [4,6,8,10,13.7,16.5,19,23,27,34]:
            h=tree.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))[0]
            floors[name][str(x)].append([y,h.z if h else None])
report={'filepath':bpy.data.filepath,'scene':s.name,'objects':objects,'floors':floors,'materials':{m.name:[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] for m in bpy.data.materials if m.use_nodes and m.name.startswith(('RC_','Forest_'))}}
(out/'inspect.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'scene':s.name,'file':bpy.data.filepath,'target_objects':len(objects),'report':str(out/'inspect.json')}))
