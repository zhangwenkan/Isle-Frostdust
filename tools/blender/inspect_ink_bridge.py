"""Read-only inspection in the live Blender MCP scene."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/ink-bridge-review';O.mkdir(exist_ok=True)
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
report={'file':bpy.data.filepath,'objects':[],'materials':{}}
for o in bpy.data.scenes['Island_Refined'].objects:
    if not o.name.startswith('Bridge_') or any(c.name.startswith('90_') for c in o.users_collection):continue
    me=o.data;me.calc_loop_triangles();points=[o.matrix_world@v.co for v in me.vertices]
    report['objects'].append({'name':o.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),
        'materials':[m.name for m in me.materials if m],'min':[min(p[k] for p in points) for k in range(3)],
        'max':[max(p[k] for p in points) for k in range(3)],'modifiers':[m.name for m in o.modifiers],
        'smooth_faces':sum(p.use_smooth for p in me.polygons)})
    for m in me.materials:
        if not m or m.name in report['materials']:continue
        bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        report['materials'][m.name]={'diffuse':list(m.diffuse_color),'roughness':float(bs.inputs['Roughness'].default_value) if bs else None,
            'textures':[{'node':n.name,'file':n.image.filepath,'size':list(n.image.size)} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []}
(O/'bridge-before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('BRIDGE_INSPECT',len(report['objects']),sum(o['triangles'] for o in report['objects']),report['materials'])
