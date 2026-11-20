"""Unify rock feet and the connected cape shoulder through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/reference-cape-review';COL=bpy.data.collections['49_Reference_Cape']
assert not LAYOUT['reference_cape'].get('rock_polish')
for key in ['cape_side','cape_top','cape_platform','cape_tread','cape_sand']:
    MATS[key]=[m for m in bpy.data.materials if m.name.startswith('RC_'+key)][-1]
source=ast.parse((ROOT/'tools/blender/build_reference_cape.py').read_text(encoding='utf-8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name=='cut_rock':exec(compile(ast.Module(body=[node],type_ignores=[]),'rock_factory','exec'))
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='shape' for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'rock_shape','exec'))
specs=[(-81.0,8.6,5.15,4.0,-.45,5.22,.12),(-81.0,12.9,5.1,4.3,-.55,5.33,-.14),(-83.1,10.7,3.3,3.9,-.65,4.15,.20),(-78.55,5.8,5.0,4.0,-.45,5.13,-.11),(-76.9,3.5,3.45,3.75,-.50,3.85,.17),(-75.85,.00,2.65,2.9,-.42,2.45,.14),(-71.25,4.1,3.25,4.8,-.48,5.12,-.14),(-68.45,8.6,4.2,4.8,-.47,5.55,.15),(-69.6,15.9,3.8,3.6,-.45,6.0,-.21),(-78.0,16.0,4.8,3.4,-.42,5.78,.09)]
for i,s in enumerate(specs):
    ob=SCENE.objects['Cape_Cliff_Mass_%02d'%i];new=cut_rock(ob.name+'_Polish',*s,lean=(.24,-.20),top_scale=.94)
    ob.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
# Break the outer shelf's equal-height edge while keeping the core activity
# band flat. Subdivision creates editable top relief rather than a fake rim.
ob=SCENE.objects['WALK_Cape_Platform'];me=ob.data
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=5,use_grid_fill=True);bmesh.ops.triangulate(bm,faces=list(bm.faces))
routes=[(A[a],A[b]) for a,b in [['cape_entry','cape_center'],['cape_center','cape_stair_top']]]
def route_distance(x,y):
    q=Vector((x,y));best=100
    for a,b in routes:
        v=b.xy-a.xy;t=max(0,min(1,(q-a.xy).dot(v)/v.length_squared));best=min(best,(q-(a.xy+v*t)).length)
    return best
for v in bm.verts:
    d=route_distance(v.co.x,v.co.y)
    v.co.z=4.55-sm(1.9,4.5,d)*(.14+.045*math.sin(v.co.x*.61+v.co.y*.49))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
for p in me.polygons:
    for li in p.loop_indices:
        co=me.vertices[me.loops[li].vertex_index].co;me.uv_layers[0].data[li].uv=((co.x+84)/17,(co.y-5)/13)
platform=BVHTree.FromPolygons([v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
core=SCENE.objects['Cape_Attached_Cliff_Core']
for v in core.data.vertices:
    if v.co.z>3:
        h=platform.find_nearest(Vector((v.co.x,v.co.y,4.5)))[0];v.co.z=h.z-.018
core.data.update()
# Connect the visible near-side old slope to the cape neck with one fitted
# rock/earth shoulder, closing the first build's open wedge at the junction.
old_surfaces=[SCENE.objects[n] for n in ['WALK_Forest_Ground','WALK_Forest_NearSlope']]
trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in old_surfaces]
def old_height(x,y):
    hits=[t.ray_cast(Vector((x,y,35)),Vector((0,0,-1)))[0] for t in trees];hits=[h.z for h in hits if h is not None]
    return max(hits) if hits else 5.5
vs=[];uv=[];fs=[];NX=32;NY=20
for j in range(NY+1):
    y=3.0+8.8*j/NY
    for i in range(NX+1):
        x=-59.6-9*i/NX;t=i/NX
        back=6.15*(1-sm(0,1,t))+4.40*sm(0,1,t)
        z=1.15+(back-1.15)*sm(3.0,11.5,y)+.10*math.sin(x*.45+y*.27)
        z=old_height(x,y)*(1-sm(0,.21,t))+z*sm(0,.21,t)
        vs.append((x,y,z));uv.append((i/NX,j/NY))
for j in range(NY):
    for i in range(NX):
        k=j*(NX+1)+i;fs.extend([(k,k+1,k+NX+2),(k,k+NX+2,k+NX+1)])
b=Mesh('Cape_Connection_Shoulder');b.part(vs,fs,'cape_top',uv);b.build(smooth=True)
# Give the sea enough extent for the newly opened western view. Only this
# existing four-vertex carrier changes; water shading remains Godot's role.
sea=SCENE.objects['Sea_Surface']
for v in sea.data.vertices:
    v.co.x=-450 if v.co.x<0 else 450
    v.co.y=-100 if v.co.y<0 else 500
sea.data.update()
archive=bpy.data.collections.new('90_Reference_Cape_Initial_Sky_Card');SCENE.collection.children.link(archive)
sky=SCENE.objects.get('Cape_Sky_Backdrop')
if sky:
    for c in list(sky.users_collection):c.objects.unlink(sky)
    archive.objects.link(sky);sky.hide_set(True);sky.hide_render=True
# Low broken silhouettes, a distant stack and a pale rear island group.
far_specs=[(-123,103,16,11,7.9),(-114,104,17,13,9.3),(-106,101,13,10,6.2),(-98,154,4.8,6.5,7.4),(-96,155,5.0,6.2,10.4),(-93,155,4.0,5.6,6.8),(-72,185,13,10,4.9),(-62,186,17,12,6.0),(-54,185,12,9,4.3),(-79,117,4.3,5.2,5.8),(-76,118,5.3,6.0,7.4),(-73,117,3.6,4.8,4.8)]
for name,s in zip(LAYOUT['reference_cape']['distant_islets'],far_specs):
    old=SCENE.objects[name];x,y,w,d,h=s;new=cut_rock(name+'_Polish',x,y,w,d,-.6,h,lean=(.30,-.20),top_scale=.70)
    old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
LAYOUT['reference_cape']['rock_polish']={'larger_interlocking_cliff_masses':True,'unequal_outer_shelf_edge':True,'connected_near_shoulder':True,'sea_carrier_expanded':[-450,450,-100,500],'sky':'Godot sky shader, initial card archived','distant_silhouettes':'low ridges, a far stack and a pale rear island'}
export('reference-cape-polish')
