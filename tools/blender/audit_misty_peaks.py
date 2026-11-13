import bpy, json, math
from pathlib import Path

ROOT = Path('D:/自己做着玩的/孤屿霜尘')
OUT = ROOT / 'artifacts/misty-peaks-review'
scene = bpy.data.scenes['Island_Refined']
active = [o for o in scene.objects if o.type == 'MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
peak_collection = bpy.data.collections.get('21_Misty_Peak_Groups')
assert peak_collection is not None
peaks = [o for o in peak_collection.objects if o.type == 'MESH']
assert len(peaks) == 9
stats = []
for ob in peaks:
    invalid = sum(not all(math.isfinite(float(c)) for c in v.co) for v in ob.data.vertices)
    zero = sum(p.area < 1e-10 for p in ob.data.polygons)
    assert invalid == 0 and zero == 0
    stats.append({'name': ob.name, 'vertices': len(ob.data.vertices), 'faces': len(ob.data.polygons), 'invalid_vertices': invalid, 'zero_area_faces': zero})
assert not any(o.name == 'Depth_Mountain_Ranges' for o in active)
assert not any(o.name.startswith('Depth_Bamboo_Back') or o.name == 'Depth_Forest_Shore' for o in active)
report = {
    'scene': scene.name,
    'peak_collection': peak_collection.name,
    'peak_count': len(peaks),
    'active_mesh_objects': len(active),
    'stats': stats,
    'retired_continuous_mountains_active': False,
    'retired_distant_shore_active': False,
    'geometry_check': 'finite vertices and nonzero polygon areas',
}
(OUT / 'pass5-geometry-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('MISTY_PEAK_AUDIT', json.dumps(report))
