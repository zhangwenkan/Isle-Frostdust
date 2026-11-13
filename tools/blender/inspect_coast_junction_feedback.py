"""Read-only inspection of the active island, executed through Blender MCP."""
import bpy, json
from pathlib import Path
R = Path('D:/自己做着玩的/孤屿霜尘')
O = R / 'artifacts/coast-junction-study-20261111'
O.mkdir(exist_ok=True)
report = {'file': bpy.data.filepath, 'active_scene': bpy.context.scene.name,
          'scenes': {s.name: len(s.objects) for s in bpy.data.scenes}}
scene = bpy.data.scenes.get('Island_Refined')
if scene:
    report['coast_objects'] = [{
        'name': o.name, 'vertices': len(o.data.vertices),
        'faces': len(o.data.polygons),
        'collections': [c.name for c in o.users_collection],
        'uv_layers': [u.name for u in o.data.uv_layers],
        'materials': [m.name if m else None for m in o.data.materials],
    } for o in scene.objects if o.type == 'MESH' and o.name.startswith('Integrated_Coast_')]
(O / 'blender-inspection.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(report, ensure_ascii=False))
