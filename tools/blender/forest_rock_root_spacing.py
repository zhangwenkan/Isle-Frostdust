"""Seat three existing rocks in soil gaps between bamboo rows, via Blender MCP."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

R=Path('D:/自己做着玩的/孤屿霜尘')
O=R/'artifacts/forest-rock-root-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath)==R/'assets/island_blender/nameless_island.blend'
names=['InkSample_Rock_02','InkSample_Rock_03','InkSample_Rock_04']
def active():
    return [ob for ob in scene.objects if ob.type=='MESH' and not any(c.name.startswith('90_') for c in ob.users_collection)]
def signature(ob):
    h=hashlib.sha256()
    for v in ob.data.vertices:h.update(str(tuple(v.co)).encode())
    for p in ob.data.polygons:h.update(str(tuple(p.vertices)).encode())
    for uv in ob.data.uv_layers:
        for d in uv.data:h.update(str(tuple(d.uv)).encode())
    h.update(str(ob.matrix_world).encode())
    return h.hexdigest()
before={ob.name:signature(ob) for ob in active() if ob.name not in names}
arc=bpy.data.collections.get('90_Before_Forest_Root_Spacing') or bpy.data.collections.new('90_Before_Forest_Root_Spacing')
if arc.name not in scene.collection.children:scene.collection.children.link(arc)
arc.hide_render=True
floor=scene.objects['PixelForest_Low_Floor']
ft=BVHTree.FromPolygons([floor.matrix_world@v.co for v in floor.data.vertices],[tuple(p.vertices) for p in floor.data.polygons])
def ground(x,y):
    hit=ft.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))[0]
    assert hit is not None,(x,y)
    return hit.z
report=[]
for name,x,z,width,depth,height,angle in [
    ('InkSample_Rock_02',-11.10,-6.25,1.90,1.30,.82,-.18),
    ('InkSample_Rock_03',-9.25,-6.05,.95,.82,.55,.36),
    ('InkSample_Rock_04',-4.70,-6.65,1.65,1.15,.66,-.42),
]:
    ob=scene.objects[name]
    if not bpy.data.objects.get('RootSpacingBaseline_'+name):
        copy=ob.copy();copy.data=ob.data.copy();copy.name='RootSpacingBaseline_'+name
        arc.objects.link(copy);copy.hide_render=True;copy.hide_set(True)
    source=bpy.data.objects['ForestRockBaseline_'+name]
    ob.data=source.data.copy()
    pts=[source.matrix_world@v.co for v in ob.data.vertices]
    lo=Vector([min(p[i] for p in pts) for i in range(3)])
    hi=Vector([max(p[i] for p in pts) for i in range(3)])
    ob.matrix_world=Matrix.Identity(4);rot=Matrix.Rotation(angle,4,'Z')
    ground_center=ground(x,-z);embed=.24
    for v,p in zip(ob.data.vertices,pts):
        rel=rot@Vector((((p.x-lo.x)/(hi.x-lo.x)-.5)*width,((p.y-lo.y)/(hi.y-lo.y)-.5)*depth,0))
        q=(p.z-lo.z)/(hi.z-lo.z)
        h=ground(x+rel.x,-z+rel.y)
        v.co=(x+rel.x,-z+rel.y,(h-embed)*(1-q)+(ground_center+height-embed)*q)
    me=ob.data;me.update();me.normals_split_custom_set([(0,0,0)]*len(me.loops))
    me.materials.clear();me.materials.append(bpy.data.materials['ForestRock_Moss'])
    while len(me.uv_layers)>1:me.uv_layers.remove(me.uv_layers[-1])
    uv2=me.uv_layers.new(name='ForestRockHeight')
    for p in me.polygons:
        p.material_index=0;p.use_smooth=False
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv2.data[li].uv=(max(0,min(1,(v.z-ground_center+embed)/height)),0)
    ob['forest_rock_pocket']=True
    ob['root_spacing_revision']='2026-11-09: between bamboo rows, opaque root audit'
    report.append(dict(name=name,center_godot=[x,ground_center,z],width=width,depth=depth,exposed_height=height-embed))

assert all(before[ob.name]==signature(ob) for ob in active() if ob.name not in names)
(O/'placement.json').write_text(json.dumps(dict(rocks=report,preserved_meshes=len(before)),indent=2),encoding='utf8')
AUDIT_PHASE='after'
exec(compile((R/'tools/blender/audit_forest_rock_roots.py').read_text(encoding='utf8'),'audit_forest_rock_roots.py','exec'))
assert all(not item['intersecting_stems'] for item in report),'Opaque bamboo still inside rock'
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('FOREST_ROCK_ROOT_SPACING_EXPORTED')
