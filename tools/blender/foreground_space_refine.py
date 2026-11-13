"""Blender MCP: continuous near terrain and an open coast foreground."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/foreground-space-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene

def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c

archive=collection('90_Rejected_Foreground_Pillars')
retired=[]
for ob in list(scene.objects):
    if not ob.name.startswith(('Depth_Foreground_Crag_','Depth_Bamboo_Fore_')):continue
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True;retired.append(ob.name)

def clamp(v):return max(0.,min(1.,v))
def smooth(a,b,v):
    t=clamp((v-a)/(b-a));return t*t*(3-2*t)
def path_z(x):return .25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44

terrain_names=['Fish_West_Continuous_Land','Fish_East_Continuous_Land']
baselines={}
for ob in list(scene.objects):
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if ob.name not in terrain_names and not ob.name.startswith(('Cliff_Fractures_','Cliff_Fern_','Fish_Ground_Rock_','Coast_Low_Grass_')):continue
    key=ob.name+'_Before_Foreground_Space'
    base=bpy.data.meshes.get(key)
    if base is None:base=ob.data.copy();base.name=key;base.use_fake_user=True
    baselines[ob.name]=base

edges={}
for name in terrain_names:
    n=52 if 'East' in name else 100;base=baselines[name]
    edges['East' in name]=[(base.vertices[i*26+25].co.x,-base.vertices[i*26+25].co.y) for i in range(n+1)]
def edge(x,east):
    pts=edges[east]
    for a,b in zip(pts,pts[1:]):
        if a[0]<=x<=b[0]:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
    return pts[0][1] if x<pts[0][0] else pts[-1][1]

def reshape(p):
    x,z,y=p.x,-p.y,p.z;east=x>10;pz=path_z(x)
    t=smooth(pz+.75,max(pz+.9,edge(x,east)),z)
    # Shaping fades before both abutments and below the water, preserving the
    # walk strip, bridge joints and underwater routes. Broad unequal shoulders
    # continue through the turf, cliff shell and its embedded fracture faces.
    ends=(smooth(14.8,17.0,x)*(1-smooth(24.8,26.5,x))) if east else (smooth(-19.0,-17.0,x)*(1-smooth(.8,4.1,x)))
    shoreline=smooth(-2.15,-.55,y)
    breadth=(.45+.18*math.cos((x-20)*.66)) if east else (.70+.30*math.cos((x+7.5)*.55)+.12*math.sin(x*.93))
    dz=breadth*t*ends*shoreline
    lower=(.23 if east else .34)*t*t*ends*shoreline
    p.y-=dz;p.z-=lower
    return p

reports=[]
for name,base in baselines.items():
    ob=scene.objects[name];me=base.copy();me.name=name+'_Near_Slope';ob.data=me
    largest=0.
    rigid_shift=None
    if name.startswith('Fish_Ground_Rock_'):
        points=[ob.matrix_world@v.co for v in base.vertices]
        center=sum(points,Vector())/len(points);center.z=min(p.z for p in points)
        rigid_shift=reshape(center.copy())-center
    for v,b in zip(me.vertices,base.vertices):
        world=ob.matrix_world@b.co
        target=world+rigid_shift if rigid_shift is not None else reshape(world.copy())
        v.co=ob.matrix_world.inverted()@target
        largest=max(largest,(v.co-b.co).length)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    report={'name':name,'max_vertex_move':largest}
    if name in terrain_names:
        count=(53 if 'East' in name else 101)*26
        walking=[i for i in range(count) if 11<=i%26<=15]
        delta=max((me.vertices[i].co-base.vertices[i].co).length for i in walking)
        assert delta<1e-6
        report['walk_vertices']=len(walking);report['max_walk_delta']=delta
    reports.append(report)

# Compare-and-remove: the two trial clumps crowded the endpoint and crossed
# the actor. The existing main grove supplies foliage at the screen edges.
near=collection('27_Near_Terrain_Bamboo')
for ob in list(near.objects):bpy.data.objects.remove(ob,do_unlink=True)
roots_report=[]

(OUT/'authoring.json').write_text(json.dumps({'archived':retired,'terrain_and_attached_props':reports,'bamboo':roots_report},indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
manifest_path=ROOT/'assets/island_blender/asset_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['revision']='Open foreground with continuous near slopes; layered distant ridges and underwater life retained'
review_source='../../artifacts/foreground-space-review/README.md'
if review_source not in manifest['source_manifests']:manifest['source_manifests'].append(review_source)
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('FOREGROUND_SPACE_EXPORTED',len(retired),'archived;',len(roots_report),'sparse bamboo groups')
