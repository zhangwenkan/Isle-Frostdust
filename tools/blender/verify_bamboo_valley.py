"""Read-only source validation through Blender MCP."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/bamboo-valley-review'
scene=bpy.data.scenes['Island_Refined'];collection=bpy.data.collections['30_West_Bamboo_Valley']
ob=scene.objects['InkValley_Connected_Terraces'];me=ob.data
bm=bmesh.new();bm.from_mesh(me)
boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
assert boundary==0 and nonmanifold==0,(boundary,nonmanifold)
assert all(p.area>1e-7 for p in me.polygons)
tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
roots=[]
for bamboo in collection.objects:
    if not bamboo.name.startswith('InkValley_Bamboo_'):continue
    assert len(bamboo.data.uv_layers)==2
    assert bamboo.data.uv_layers[1].name=='WindWeight'
    for r in json.loads(bamboo['root_positions_godot']):
        p=Vector((r[0],-r[2],r[1]));hit=tree.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
        assert hit is not None
        nearest=min((bamboo.matrix_world@v.co-p).length for v in bamboo.data.vertices)
        assert nearest<.12,(bamboo.name,nearest)
        assert abs((hit.z-p.z)-.07)<.0001
        roots.append({'object':bamboo.name,'embed':hit.z-p.z,'closest_mesh_vertex':nearest})
report={'terrain_boundary_edges':boundary,'terrain_nonmanifold_edges':nonmanifold,'zero_area_faces':0,'bamboo_root_count':len(roots),'max_bamboo_root_mesh_distance':max(r['closest_mesh_vertex'] for r in roots),'bamboo_wind_uv2_retained':True,'source_file':bpy.data.filepath,'saved':not bpy.data.is_dirty}
(OUT/'asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
