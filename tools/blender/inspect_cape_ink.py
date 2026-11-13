import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/cape-colored-ink-review'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];report={}
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if not (ob.name.startswith('Coast_Low_Grass_0') or ob.name in ['Fish_West_Continuous_Land','InkSample_Rock_00','InkSample_Path_Grass']):continue
    me=ob.data;points=[ob.matrix_world@v.co for v in me.vertices]
    mats=[]
    for m in me.materials:
        bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        mats.append({'name':m.name,'diffuse':list(m.diffuse_color),'base':list(bs.inputs['Base Color'].default_value) if bs else None,'nodes':[(n.type,n.name) for n in m.node_tree.nodes] if m.use_nodes else []})
    report[ob.name]={'bounds':[[min(p[a] for p in points) for a in range(3)],[max(p[a] for p in points) for a in range(3)]],'vertices':len(points),'faces':len(me.polygons),'materials':mats,'attributes':[(a.name,a.domain,a.data_type) for a in me.attributes], 'first_vertices':[list(v.co) for v in me.vertices[:18]],'uv_layers':[u.name for u in me.uv_layers]}
(OUT/'source-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
