"""Read-only verification in the live Blender source via MCP."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/pixel-bamboo-west-review'
scene=bpy.data.scenes['Island_Refined']
def sig(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
    for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
    for uv in o.data.uv_layers:
        for d in uv.data:h.update(str(tuple(d.uv)).encode())
    h.update(str(o.matrix_world).encode());return h.hexdigest()
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
old=json.loads((O/'baseline-objects.json').read_text(encoding='utf-8'))
keep=[r for r in old if not r['name'].startswith('ForestVisibility_')]
changed=[r['name'] for r in keep if sig(scene.objects[r['name']])!=r['signature']]
assert not changed,changed
assert not [o for o in active if o.name.startswith(('ForestVisibility_','ValleyDepth_'))]
bamboos=[o for o in active if o.name.startswith('PixelBamboo_')]
floor=scene.objects['PixelForest_Low_Floor']
ft=BVHTree.FromPolygons([floor.matrix_world@v.co for v in floor.data.vertices],[tuple(p.vertices) for p in floor.data.polygons])
roots=[];weights=[]
for o in bamboos:
    assert len(o.data.uv_layers)==2
    uv=o.data.uv_layers[1]
    weight={l.vertex_index:uv.data[l.index].uv.x for l in o.data.loops}
    gaps=[];unsupported=[]
    for v in o.data.vertices:
        if weight[v.index]>.001:continue
        p=o.matrix_world@v.co
        h=ft.ray_cast(Vector((p.x,p.y,50)),Vector((0,0,-1)))[0]
        if h:gaps.append(p.z-h.z)
        else:unsupported.append(v.index)
    roots.append(dict(name=o.name,min_gap=min(gaps) if gaps else None,max_gap=max(gaps) if gaps else None,unsupported_bottom_vertices=len(unsupported)))
    weights.append(dict(name=o.name,min=min(weight.values()),max=max(weight.values())))
assert all(w['min']<.001 and w['max']>.99 for w in weights)
report=dict(preserved_original_meshes=len(keep),unexpected_geometry_changes=changed,active_bamboo_cards=len(bamboos),legacy_valley_exported=False,wind_uv=weights,root_contact=roots,root_note='Bottom mesh vertices; alpha silhouette may begin slightly above its mesh bounds.')
(O/'geometry-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PRESERVED',len(keep),'BAMBOO',len(bamboos),'ROOT_GAP_RANGE',min(r['min_gap'] for r in roots if r['min_gap'] is not None),max(r['max_gap'] for r in roots if r['max_gap'] is not None),'UNSUPPORTED',sum(r['unsupported_bottom_vertices'] for r in roots))
