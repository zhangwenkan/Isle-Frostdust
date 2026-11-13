"""Read-only source checks, executed in Blender through MCP."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined']
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
ground=[o for o in active if o.name in ['Fish_West_Continuous_Land','ValleyDepth_Connected_Terrain']]
trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in ground]
roots=[];missing=[];meshes=[]
for ob in active:
    if ob.name.startswith('ValleyDepth_'):
        bm=bmesh.new();bm.from_mesh(ob.data)
        meshes.append({'name':ob.name,'vertices':len(bm.verts),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'uv_layers':[u.name for u in ob.data.uv_layers]})
        bm.free()
    if not ob.get('root_positions_godot'):continue
    if not (ob.name.startswith('ValleyDepth_') or ob.name in ['InkSample_Bamboo_03','Depth_Bamboo_Main_02']):continue
    for i,(x,y,z) in enumerate(json.loads(ob['root_positions_godot'])):
        hits=[t.ray_cast(Vector((x,-z,45)),Vector((0,0,-1)))[0] for t in trees]
        hits=[h for h in hits if h is not None]
        if not hits:missing.append([ob.name,i]);continue
        h=max(p.z for p in hits)
        roots.append({'object':ob.name,'root':i,'offset_m':y-h})
report={'source':bpy.data.filepath,'active_meshes':len(active),'meshes':meshes,'roots':roots,'missing_support':missing,'root_offset_min_m':min(r['offset_m'] for r in roots),'root_offset_max_m':max(r['offset_m'] for r in roots)}
(ROOT/'artifacts/valley-depth-review/asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','roots']}))
