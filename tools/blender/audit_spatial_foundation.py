"""Read-only audit of live meshes and saved source paths through Blender MCP."""
import bpy,bmesh,json,hashlib
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Layered_Island_20261116']
r={'objects':[],'issues':[],'textures':[]}
images=set()
for o in scene.objects:
    if o.type!='MESH' or any(c.name.startswith('90_') for c in o.users_collection):continue
    me=o.data;me.calc_loop_triangles()
    row={'name':o.name,'triangles':len(me.loop_triangles),'uv':[u.name for u in me.uv_layers],'invalid_normals':sum(p.normal.length<.5 for p in me.polygons)}
    if row['invalid_normals']:r['issues'].append(o.name+': invalid normal')
    if not me.uv_layers:r['issues'].append(o.name+': no UV')
    if o.name in ['Space_Continuous_Cliff','WALK_Space_Stairs'] or o.name.startswith('Space_Rock'):
        bm=bmesh.new();bm.from_mesh(me);row['boundary_edges']=sum(e.is_boundary for e in bm.edges);bm.free()
        if row['boundary_edges']:r['issues'].append(o.name+': open volume')
    if o.name.startswith(('Space_Bamboo','Space_Grass')):
        if len(me.uv_layers)<2:r['issues'].append(o.name+': missing wind weights')
        else:
            w=[p.uv.x for p in me.uv_layers[1].data];row['wind_range']=[min(w),max(w)]
    for mat in me.materials:
        if mat and mat.use_nodes:
            images.update(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
    r['objects'].append(row)
for im in images:
    exists=bool(im.packed_file) or Path(bpy.path.abspath(im.filepath)).is_file()
    r['textures'].append({'name':im.name,'available':exists})
    if not exists:r['issues'].append('Missing texture '+im.name)
r['meshes']=len(r['objects']);r['triangles']=sum(o['triangles'] for o in r['objects'])
(root/'artifacts/spatial-foundation-review/blender-audit.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({k:r[k] for k in ['meshes','triangles','issues']}))
