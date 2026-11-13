"""Compose western exposed bedrock in Blender via MCP; never build geometry in Godot."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/stone-spatial-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()

def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
archive=collection('90_Before_Stone_Spatial_Refine')
sample=collection('28_Colored_Ink_Sample')
land=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
def surface(x,y):
    hit,n,_,_=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
    assert hit is not None,(x,y)
    return hit.z,n

def baseline(name):
    saved=bpy.data.objects.get('SpatialBaseline_'+name)
    if saved is not None:return saved
    ob=scene.objects[name]
    saved=ob.copy();saved.data=ob.data.copy();saved.name='SpatialBaseline_'+name
    archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    return saved

def retire(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True

# The spacing is intentionally unequal: a quiet western exposure, a main
# split ledge in the steep middle slope, then one lower shoulder at its exit.
# The main ledge's small piece overlaps its downhill foot, rather than forming
# a second freestanding decorative pair.
designs=[
    dict(name='InkSample_Rock_00',source='Fish_Ground_Rock_00_Body',center=(-17.8,1.10),size=(1.92,1.25,1.08),bury=.78,angle=-7,dip=-.12,role='Low western bedrock exposure, in front of bamboo roots'),
    dict(name='InkSample_Rock_02',source='InkSample_Rock_02',center=(-11.35,2.05),size=(3.02,2.02,1.65),bury=1.12,angle=-8,dip=-.24,role='Primary exposed ledge, uphill side embedded'),
    dict(name='InkSample_Rock_03',source='InkSample_Rock_03',center=(-10.05,1.64),size=(1.20,1.18,.98),bury=.82,angle=-12,dip=-.24,role='Attached downhill toe of primary ledge'),
    dict(name='InkSample_Rock_04',source='InkSample_Rock_04',center=(-6.45,1.95),size=(1.96,1.58,1.20),bury=.94,angle=-10,dip=-.22,role='Low downhill shoulder; open grass slope continues toward bridge'),
]
reports=[]
for d in designs:
    src=baseline(d['source'])
    pts=[src.matrix_world@v.co for v in src.data.vertices]
    lo=Vector([min(p[a] for p in pts) for a in range(3)])
    hi=Vector([max(p[a] for p in pts) for a in range(3)])
    ob=scene.objects.get(d['name'])
    if ob is None:
        ob=bpy.data.objects.new(d['name'],src.data.copy());sample.objects.link(ob)
    else:ob.data=src.data.copy()
    ob.parent=None;ob.matrix_world=Matrix.Identity(4)
    me=ob.data;me.name='Embedded_'+d['name'];cx,cy=d['center'];w,depth,h=d['size']
    ground,n=surface(cx,cy);angle=math.radians(d['angle'])
    slope_y=min(.32,max(.12,-n.y/n.z*.40))
    for v,p in zip(me.vertices,pts):
        u=(p.x-lo.x)/(hi.x-lo.x)-.5
        q=(p.y-lo.y)/(hi.y-lo.y)-.5
        t=(p.z-lo.z)/(hi.z-lo.z)
        dx=u*w;dy=q*depth
        x=cx+dx*math.cos(angle)-dy*math.sin(angle)
        y=cy+dx*math.sin(angle)+dy*math.cos(angle)
        # A shared dipping stone plane cuts through the soil surface. Only
        # buried foot vertices conform to the land; exposed faces stay rigid.
        z=ground-d['bury']+t*h+d['dip']*(x-cx)+slope_y*(y-cy)
        local_ground,_=surface(x,y)
        if t<.42:z=min(z,local_ground-.20-(.42-t)*.12)
        v.co=(x,y,z)
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    edges=[e for e in bm.edges if e.is_boundary]
    if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    me.materials.clear();me.materials.append(bpy.data.materials['InkSample_Rock_'+str(1 if d['name'].endswith('03') else 0)])
    if d['name'].endswith('00'):
        uv=me.uv_layers.active or me.uv_layers.new(name='StructurePainting')
        for loop in me.loops:
            v=me.vertices[loop.vertex_index].co
            uv.data[loop.index].uv=((v.x-cx)/w+.5,(v.z-ground+d['bury']-d['dip']*(v.x-cx))/h)
    for p in me.polygons:p.use_smooth=True
    bpy.context.view_layer.objects.active=ob
    modifier=ob.modifiers.new('Broad plane normals','WEIGHTED_NORMAL');modifier.weight=35
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    ob['source_role']=d['role'];ob['spatial_design']='Western embedded bedrock, 2026-11-08'
    ob.hide_set(False);ob.hide_render=False
    reports.append({**d,'ground_at_center':ground,'upper_plane_cross_slope':slope_y})

retired=['Fish_Ground_Rock_%02d_Body'%i for i in [0,1,6,9,10,11]]+['InkSample_Rock_05']
for name in retired:retire(scene.objects[name])
(OUT/'blender-authoring.json').write_text(json.dumps({'before_western_rock_count':10,'after_western_rock_count':4,'group_count':3,'designs':reports,'retired_objects':retired},ensure_ascii=False,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
manifest_path=ROOT/'assets/island_blender/asset_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['revision']='Western stone arrangement: 10 separate stones reduced to 4 embedded stones in 3 unequal bedrock groups'
reference='../../artifacts/stone-spatial-review/README.md'
if reference not in manifest['source_manifests']:manifest['source_manifests'].append(reference)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('STONE_SPATIAL_EXPORTED',len(designs),'stones, 3 groups')
