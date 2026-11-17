"""Read-only audit of the authored scene, called through Blender MCP."""
import bpy, json
from pathlib import Path
root = Path('D:/自己做着玩的/孤屿霜尘')
scene = bpy.data.scenes['Layered_Island_20261116']
report = {'scene': scene.name, 'objects': [], 'issues': []}
for ob in scene.objects:
    if ob.type != 'MESH':
        continue
    me = ob.data
    me.calc_loop_triangles()
    zero_normals = sum(p.normal.length < .5 for p in me.polygons)
    row = {'name': ob.name, 'vertices': len(me.vertices), 'triangles': len(me.loop_triangles),
           'uv_layers': [uv.name for uv in me.uv_layers], 'invalid_face_normals': zero_normals,
           'materials': [m.name if m else None for m in me.materials]}
    if len(me.uv_layers) > 1:
        weights = [uv.uv.x for uv in me.uv_layers[1].data]
        row['uv2_weight_range'] = [min(weights), max(weights)] if weights else []
    if zero_normals:
        report['issues'].append(ob.name + ': invalid face normals')
    if not me.uv_layers:
        report['issues'].append(ob.name + ': missing UV')
    report['objects'].append(row)
report['mesh_count'] = len(report['objects'])
report['triangles'] = sum(row['triangles'] for row in report['objects'])
report['images'] = []
images = set()
for ob in scene.objects:
    if ob.type == 'MESH':
        for mat in ob.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        images.add(node.image)
for im in images:
    report['images'].append({'name': im.name, 'packed': bool(im.packed_file), 'size': list(im.size)})
    if not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file():
        report['issues'].append('Missing texture: ' + im.name)
path = root / 'artifacts/layered-island-build/blender-audit.json'
path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ['mesh_count', 'triangles', 'issues']}))
