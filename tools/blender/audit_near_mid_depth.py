"""Read Blender grounding, retained wind UVs and walking corridor after polish."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/near-mid-depth-review'
scene=bpy.data.scenes['Layered_Island_20261116'];layout=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/layered_island/layered_island.blend').resolve()
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
ground=tree(scene.objects['WALK_Forest_Ground']);near=tree(scene.objects['WALK_Forest_NearSlope'])
before=tree(scene.objects['NearMid_Before_WALK_Forest_Ground'])
left=tree(scene.objects['WALK_Left_Ground'])
def floor(x,y):
    hits=[t.ray_cast(Vector((x,y,35)),Vector((0,0,-1)))[0] for t in [ground,near]]
    return max(h.z for h in hits if h is not None)
max_error=0.;center_error=0.;route_samples=0
for a,b in layout['forest_extension']['new_edges']:
    va,vb=layout['anchors'][a],layout['anchors'][b]
    for i in range(51):
        x=va[0]+(vb[0]-va[0])*i/50;y=-(va[2]+(vb[2]-va[2])*i/50)
        for dy in [-.55,0,.55]:
            ray=Vector((x,y+dy,35));h=ground.ray_cast(ray,Vector((0,0,-1)))[0];old=before.ray_cast(ray,Vector((0,0,-1)))[0]
            shared=left.ray_cast(ray,Vector((0,0,-1)))[0]
            if shared:
                if not h or shared.z>h.z:h=shared
                if not old or shared.z>old.z:old=shared
            assert h and old,(a,b,i,dy,'missing author corridor')
            max_error=max(max_error,abs(h.z-old.z));route_samples+=1
            if dy==0:center_error=max(center_error,abs(h.z-old.z))
wind=[];failures=[]
for name,record in layout['forest_extension']['layer_roles']['wind_bindings'].items():
    ob=scene.objects[name];uv=ob.data.uv_layers[1]
    if 'Role_Front' in name:
        old=scene.objects['NearMid_Before_'+name]
        assert len(uv.data)==len(old.data.uv_layers[1].data)
        if any((a.uv-b.uv).length>1e-7 for a,b in zip(uv.data,old.data.uv_layers[1].data)):failures.append('Changed wind UV '+name)
    if 'Leaves' in name or 'FrontLeaf' in name:continue
    root=Vector((record['root'][0],-record['root'][2],record['root'][1]))
    base=[loop.index for loop in ob.data.loops if abs(ob.data.vertices[loop.vertex_index].co.z-root.z)<.045]
    weight=max([uv.data[i].uv.x for i in base],default=0)
    wind.append({'name':name,'root_wind_max':weight})
    if weight>1e-6:failures.append('Moving root '+name)
    if 'Role_Front' in name and abs(root.z+.025-floor(root.x,root.y))>.004:failures.append('Foreground root not planted '+name)
rocks=[]
for record in layout['forest_extension']['near_mid_depth']['rocks']:
    ob=scene.objects[record['name']]
    embed=[floor(v.co.x,v.co.y)-v.co.z for v in ob.data.vertices if floor(v.co.x,v.co.y)-v.co.z>.12]
    if not embed:failures.append('Unembedded rock '+ob.name)
    rocks.append({'name':ob.name,'embedded_vertices':len(embed),'min_embed':min(embed,default=0)})
mesh_check=[]
for ob in bpy.data.collections['48_Near_Middle_Depth'].objects:
    if ob.type!='MESH':continue
    bad=[p.index for p in ob.data.polygons if p.area<1e-10 or not all(math.isfinite(c) for c in p.normal)]
    if bad:failures.append('Degenerate face '+ob.name)
    mesh_check.append({'name':ob.name,'faces':len(ob.data.polygons),'uv_layers':len(ob.data.uv_layers),'bad_faces':bad})
if max_error>.015 or center_error>.002:failures.append('Changed walking corridor height')
# Read back the restored painting registration from the saved source.
old_mesh=scene.objects['NearMid_Before_WALK_Forest_Ground'].data
new_mesh=scene.objects['WALK_Forest_Ground'].data
uv_tree=BVHTree.FromPolygons([v.co for v in old_mesh.vertices],[list(p.vertices) for p in old_mesh.polygons])
expected_uv={};fallbacks=0
for vertex in new_mesh.vertices:
    co=vertex.co
    hit,normal,index,distance=uv_tree.ray_cast(Vector((co.x,co.y,40)),Vector((0,0,-1)))
    if index is None:
        hit,normal,index,distance=uv_tree.find_nearest(co);fallbacks+=1
    face=old_mesh.polygons[index]
    points=[Vector((old_mesh.vertices[i].co.x,old_mesh.vertices[i].co.y,0)) for i in face.vertices]
    values=[Vector((*old_mesh.uv_layers[0].data[i].uv,0)) for i in face.loop_indices]
    expected_uv[vertex.index]=barycentric_transform(Vector((co.x,co.y,0)),*points,*values).xy
uv_error=max((new_mesh.uv_layers[0].data[loop.index].uv-expected_uv[loop.vertex_index]).length for loop in new_mesh.loops)
if uv_error>2e-6:failures.append('Ground painting registration differs from original UV')
uv_report={'checked_loops':len(new_mesh.loops),'max_uv_difference':uv_error,'boundary_fallbacks':fallbacks,'restoration_record':layout['forest_extension']['near_mid_depth'].get('uv_restore')}
report={'source_file':bpy.data.filepath,'layout_revision':layout['revision'],'ground_uv_restoration':uv_report,'route_samples':route_samples,'max_corridor_height_change_m':max_error,'max_centerline_height_change_m':center_error,'wind_roots':wind,'rocks':rocks,'meshes':mesh_check,'failures':failures}
(OUT/'blender-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'route_samples':route_samples,'max_corridor_height_change_m':max_error,'max_centerline_height_change_m':center_error,'max_ground_uv_difference':uv_error,'roots':len(wind),'meshes':len(mesh_check),'failures':failures}))
assert not failures
