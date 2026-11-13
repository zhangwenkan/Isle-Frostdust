"""Build a collapsed, cold campfire in the actual Blender scene through MCP.

Low grouped charcoal, ash and five uneven perimeter stones. All new surfaces are
authored here, conformed to the existing ground; the old cape rock is archived.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/cape-campfire-review';ASSET=ROOT/'assets/cape_campfire'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
land=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])

def active():return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def digest(ob):
    me=ob.data
    data={'v':[list(v.co) for v in me.vertices],'p':[list(p.vertices) for p in me.polygons],
          'n':[list(n.vector) for n in me.corner_normals],'uv':[[list(d.uv) for d in u.data] for u in me.uv_layers],
          'matrix':[list(r) for r in ob.matrix_world]}
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
baseline_path=OUT/'geometry-before.json'
if not baseline_path.exists():baseline_path.write_text(json.dumps({o.name:digest(o) for o in active()},indent=2),encoding='utf-8')
before=json.loads(baseline_path.read_text(encoding='utf-8'))

archive=bpy.data.collections.get('90_Replaced_Cape_Rock_By_Campfire')
if archive is None:
    archive=bpy.data.collections.new('90_Replaced_Cape_Rock_By_Campfire');scene.collection.children.link(archive)
archive.hide_render=True
rock=scene.objects['InkSample_Rock_00']
if archive not in rock.users_collection:
    for c in list(rock.users_collection):c.objects.unlink(rock)
    archive.objects.link(rock)
rock.hide_render=True;rock.hide_set(True)
collection=bpy.data.collections.get('29_Cape_Cold_Campfire')
if collection is None:
    collection=bpy.data.collections.new('29_Cape_Cold_Campfire');scene.collection.children.link(collection)
for ob in list(collection.objects):bpy.data.objects.remove(ob,do_unlink=True)

cx,cz=-23.0,-.06;rotation=math.radians(-28)
U=Vector((math.cos(rotation),-math.sin(rotation),0));V=Vector((-math.sin(rotation),-math.cos(rotation),0))
def ground(x,y):
    p,n,_,_=tree.ray_cast(Vector((x,y,25)),Vector((0,0,-1)))
    assert p is not None,(x,y)
    return p.z
def point(u,v,h=0):
    xy=Vector((cx,-cz,0))+U*u+V*v
    return Vector((xy.x,xy.y,ground(xy.x,xy.y)+h))
center=point(0,0)
parent=bpy.data.objects.new('Cape_Cold_Campfire',None);collection.objects.link(parent);parent.location=center
parent['state']='Cold next-morning campfire: no fire, ember glow, smoke or light'
parent['sleeping_actor_relation']='Off the walking strip, upper-left of sleeping torso in opening view'

def linear(hex):
    c=[int(hex[i:i+2],16)/255 for i in [0,2,4]]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)+(1,)
def material(name,texture=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    nodes=m.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=1
    bs.inputs['Specular IOR Level'].default_value=0;output=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface'])
    if texture:
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ASSET/texture),check_existing=True);tex.image.reload()
        m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    else:
        attr=nodes.new('ShaderNodeVertexColor');attr.layer_name='CampfireColor';m.node_tree.links.new(attr.outputs['Color'],bs.inputs['Base Color'])
    return m
wood=material('InkCampfire_Charcoal','charred_wood.png');endmat=material('InkCampfire_BrokenEnd','charred_end.png')
stone=material('InkCampfire_Stone');ash=material('InkCampfire_Ash')
objects=[];contact=[]
def mesh(name,vertices,faces,mats,colors=None,uvs=None,indices=None):
    me=bpy.data.meshes.new(name);me.from_pydata([tuple(v-center) for v in vertices],[],faces);me.update()
    for m in mats:me.materials.append(m)
    if indices:
        for p,mi in zip(me.polygons,indices):p.material_index=mi
    if uvs:
        uv=me.uv_layers.new(name='CampfireBrushUV')
        for p,coords in zip(me.polygons,uvs):
            for li,coord in zip(p.loop_indices,coords):uv.data[li].uv=coord
    if colors:
        ca=me.color_attributes.new(name='CampfireColor',type='FLOAT_COLOR',domain='POINT')
        for d,c in zip(ca.data,colors):d.color=c
        me.color_attributes.active_color=ca;me.color_attributes.render_color_index=0
    # Face winding from authored rings is corrected without smoothing away planes.
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if name=='Campfire_Cold_Ashbed':
        bm.normal_update()
        if sum(f.normal.z for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();me.update()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob);ob.parent=parent
    objects.append(ob);return ob

# Ash is a restrained wash on the real terrain material, not a separate flat disc.
# Five incomplete, varied perimeter stones; no identical bead ring.
stone_specs=[(-163,.58,.43,.28,.20,.105),(-96,.57,.45,.22,.19,.080),(-28,.57,.48,.25,.20,.115),(48,.54,.46,.23,.19,.095),(143,.58,.40,.26,.18,.10)]
for k,(deg,ru,rv,sx,sy,h) in enumerate(stone_specs):
    t=math.radians(deg);u=ru*math.cos(t);v=rv*math.sin(t);theta=t+.3
    ring2=[(-.44,-.36),(.18,-.48),(.49,-.13),(.34,.39),(-.22,.46),(-.52,.10)]
    vv=[];cc=[]
    for level in range(3):
        for j,(a,b) in enumerate(ring2):
            scale=[.86,1.,.79][level]
            du=(a*math.cos(theta)*sx-b*math.sin(theta)*sy)*scale
            dv=(a*math.sin(theta)*sx+b*math.cos(theta)*sy)*scale
            z=[-.035,h*.30,h*(.92+.08*math.sin(j+k))][level]
            vv.append(point(u+du,v+dv,z));cc.append(linear(['67756c','7b8478','909584'][level]))
    ff=[tuple(reversed(range(6))),tuple(range(12,18))]
    for level in range(2):
        for j in range(6):ff.append((level*6+j,level*6+(j+1)%6,(level+1)*6+(j+1)%6,(level+1)*6+j))
    ob=mesh('Campfire_Hearth_Stone_%02d'%k,vv,ff,[stone],cc)
    contact.append({'object':ob.name,'ground_embed_m':.035})

# Low, collapsed pile: two grounded pieces support a cross piece, a short split
# and a detached burned end. Its long axis echoes the sleeping body and contour.
log_specs=[(0,-.16,.82,7,.079,0),(.015,.17,.75,-22,.080,0),(-.07,.01,.77,83,.066,.135),(.20,-.02,.48,42,.057,.12),(-.28,-.27,.24,-31,.044,0)]
for k,(u,v,length,angle,radius,lift) in enumerate(log_specs):
    a=math.radians(angle);axis=U*math.cos(a)+V*math.sin(a);side=Vector((-axis.y,axis.x,0));mid=point(u,v)
    vv=[];rings=[(-.5,.65),(-.33,1.0),(.02,.73),(.34,.96),(.5,.58)];S=8
    for ring,(along,rs) in enumerate(rings):
        xy=mid+axis*(length*along);cy=ground(xy.x,xy.y)+radius*.94+lift
        for j in range(S):
            t=2*math.pi*j/S+.10;shape=1+.065*math.sin(j*2.1+k)
            p=Vector((xy.x,xy.y,cy))+side*(math.cos(t)*radius*rs*shape)+Vector((0,0,math.sin(t)*radius*rs))
            if ring in [0,len(rings)-1]:p+=axis*(math.sin(j*2.7+k)*.014)
            vv.append(p)
    ff=[];uvs=[];mi=[]
    for ring in range(len(rings)-1):
        for j in range(S):
            nxt=(j+1)%S;ff.append((ring*S+j,ring*S+nxt,(ring+1)*S+nxt,(ring+1)*S+j));mi.append(0)
            uvs.append([(rings[ring][0]+.5,j/S),(rings[ring][0]+.5,(j+1)/S),(rings[ring+1][0]+.5,(j+1)/S),(rings[ring+1][0]+.5,j/S)])
    for ring in [0,len(rings)-1]:
        ids=list(range(ring*S,(ring+1)*S));ff.append(tuple(ids));mi.append(1)
        uvs.append([(.5+.46*math.cos(2*math.pi*j/S),.5+.46*math.sin(2*math.pi*j/S)) for j in range(S)])
    ob=mesh('Campfire_Charred_Log_%02d'%k,vv,ff,[wood,endmat],uvs=uvs,indices=mi)
    contact.append({'object':ob.name,'radius_m':radius,'support_lift_m':lift,'role':'grounded' if lift==0 else 'supported_by_lower_logs'})

# A few broad, low charcoal fragments provide the burned center's broken shape.
for k,(u,v,s) in enumerate([(-.23,.09,.10),(.21,.24,.085),(.05,-.32,.075),(-.30,-.02,.065)]):
    vv=[point(u-s*.7,v-s*.4,.016),point(u+s*.6,v-s*.5,.014),point(u+s*.8,v+s*.4,.015),point(u-s*.5,v+s*.6,.014),point(u-.08*s,v,.055)]
    mesh('Campfire_Coal_%02d'%k,vv,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],[ash],[linear('414a40')]*4+[linear('646b5d')])

after={o.name:digest(o) for o in active()};removed=sorted(set(before)-set(after));changed=[n for n in before if n in after and before[n]!=after[n]]
assert removed==['InkSample_Rock_00'],removed
assert not changed,changed
points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
# Update dependency graph before deriving world bounds of parented objects.
bpy.context.view_layer.update()
points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
report={'center_godot':[cx,center.z,cz],'orientation_godot_degrees':-28,'removed':removed,'other_meshes_unchanged':len(before)-1,'new_objects':[o.name for o in objects],'bounds_blender':[[min(p[a] for p in points) for a in range(3)],[max(p[a] for p in points) for a in range(3)]],'contacts':contact,'cold':True,'lights':0,'smoke':0,'geometry_authoring':'Blender MCP'}
(OUT/'blender-authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
manifest_path=ROOT/'assets/island_blender/asset_manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['revision']='Cold colored-ink campfire beside sleeping hero; former cape rock archived'
ref='../../artifacts/cape-campfire-review/README.md'
if ref not in manifest['source_manifests']:manifest['source_manifests'].append(ref)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('COLD_CAMPFIRE_EXPORTED',json.dumps(report))
