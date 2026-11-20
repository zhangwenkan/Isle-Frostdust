"""Independent rock authoring, executed only inside Blender through MCP.

The principal stone has a hand drawn surface network, a tilted crown, an
inward fracture and variable wear. Other stones have separate structural
designs. This file never edits the game scene or exports its surroundings.
"""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/rock-sculpt-focus-review'
ASSET=ROOT/'assets/layered_island/rock_sculpt_focus'
OUT.mkdir(exist_ok=True);ASSET.mkdir(exist_ok=True)
NAME='Rock_Sculpt_Focus_20261119'
assert not bpy.data.scenes.get(NAME), 'Author already executed. Refine the saved scene.'
original=bpy.context.window.scene
game=bpy.data.scenes['Layered_Island_20261116']
protected=[ROOT/'assets/layered_island'/n for n in ['layered_island.blend','layered_island.glb','layout.json']]
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
scene=bpy.data.scenes.new(NAME);bpy.context.window.scene=scene
col=bpy.data.collections.new('Rock_Focus_Authored');scene.collection.children.link(col)
review=bpy.data.collections.new('Rock_Focus_Review_Only');scene.collection.children.link(review)
scene['scope']='Standalone rock study. Game geometry, placement, stairs and environment unchanged.'

def material(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True
    m.diffuse_color=(*color,1)
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.86
    return m
clay=material('RockFocus_Neutral_Clay',(.31,.33,.34))

def mesh(name,verts,faces):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(me);bm.free();me.update()
    o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(clay)
    for p in me.polygons:p.use_smooth=False
    return o

def wear(o,offset,angle,segments=3,upper=None):
    bm=bmesh.new();bm.from_mesh(o.data)
    edges=[e for e in bm.edges if e.is_manifold and e.calc_face_angle() > angle and
           (upper is None or (e.verts[0].co.z+e.verts[1].co.z)/2>upper)]
    if edges:
        res=bmesh.ops.bevel(bm,geom=edges,offset=offset,segments=segments,affect='EDGES',clamp_overlap=True)
        for f in res['faces']:f.smooth=True
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(o.data);bm.free();o.data.update()

def boolean(o,verts,faces,label):
    cutter=mesh('Temporary_Chisel_'+label,verts,faces)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    mod=o.modifiers.new('Authored fracture '+label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True);o.select_set(False)

# Principal rock. No repeated horizontal ring: an individually drawn front
# network carries a broad diagonal ridge, a lower recess and unequal shoulders.
V=[(-1.00,-.62,.02),(-1.26,-.84,.60),(-1.15,-.94,1.70),(-.91,-.72,2.15),
   (.55,-.57,2.34),(1.05,-.61,2.07),(1.19,-.78,1.15),(1.00,-.62,.28),(.55,-.73,.04),
   (-.63,-1.01,1.90),(-.72,-1.03,.96),(-.27,-1.08,.46),(.19,-1.01,1.46),
   (.68,-.91,1.78),(.59,-1.00,.92),
   (-.90,.61,2.28),(.03,.85,2.05),(1.05,.57,1.91),
   (-1.02,.66,.22),(.88,.65,.10),(1.12,.82,1.07),(-1.09,.92,1.31),(-.38,.22,2.31)]
F=[(1,2,9,10),(2,3,9),(3,4,13,9),(9,13,12,10),(1,10,11,0),
   (0,11,8),(10,12,14,11),(12,13,5,6,14),(13,4,5),(14,6,7),(14,7,8,11),
   (3,4,22),(3,22,15),(22,4,5,17),(15,22,17,16),
   (5,17,20,6),(6,20,19,7),(7,19,8),
   (1,0,18,21),(1,21,2),(2,21,15,3),
   (15,16,21),(16,17,20,21),(21,20,19,18),(0,8,19,18)]
hero=mesh('Focus_Rock_01_Principal',V,F)
hero['design']='Tilted crown, wide upper face, diagonal inner ridge, recessed lower face, intact back volume.'
wear(hero,.065,.55,3,upper=1.55)
wear(hero,.024,.42,2)

# One open, tapering fracture crosses the right shoulder and terminates in
# the lower front face. It is a shallow V cut, not an overlay black ribbon.
path=[(.95,2.17,.041),(.73,1.77,.046),(.21,1.43,.032),(-.10,.85,.025),(-.29,.58,.006)]
cv=[]
for i,(x,z,w) in enumerate(path):
    tangent=Vector((path[min(i+1,len(path)-1)][0]-path[max(i-1,0)][0],0,path[min(i+1,len(path)-1)][1]-path[max(i-1,0)][1])).normalized()
    across=Vector((-tangent.z,0,tangent.x))*w
    cv += [(x+across.x,-1.42,z+across.z),(x-across.x,-1.42,z-across.z),(x,-.82,z)]
cf=[(0,1,2)]
for i in range(len(path)-1):
    a=i*3;b=(i+1)*3
    cf += [(a,b,b+1,a+1),(a+1,b+1,b+2,a+2),(a+2,b+2,b,a)]
cf.append(tuple(range((len(path)-1)*3,len(path)*3)))
boolean(hero,cv,cf,'diagonal shoulder joint')

# Two asymmetric corner losses, each tied to a real face junction.
boolean(hero,[(-1.5,-1.3,.93),(-.95,-1.3,.91),(-1.0,-1.3,1.29),(-1.38,-.72,1.13),(-1.10,-.87,1.06)],
        [(0,1,2),(0,3,4,1),(1,4,2),(2,4,3),(0,2,3)],'left edge loss')
wear(hero,.010,.85,2)

# Companion shoulder: independent oblique slab profile, a stepped roof and
# split front buttress. It is drawn directly, not scaled from the principal.
v=[(-1.20,-.66,.06),(-1.43,-.73,.66),(-1.24,-.76,1.37),(-.55,-.57,1.65),
   (.48,-.67,1.52),(1.08,-.51,1.06),(1.22,-.62,.37),(.85,-.60,.02),
   (-.88,-.96,.72),(-.35,-.86,1.14),(.31,-.94,.78),(.32,-.86,.21),
   (-1.17,.77,.16),(-1.23,.57,1.40),(-.55,.84,1.72),(.62,.81,1.43),
   (1.27,.51,.78),(1.0,.71,.06),(-.15,.15,1.52)]
f=[(0,1,8),(0,8,11,7),(1,2,9,8),(2,3,9),(3,4,10,9),(9,10,11,8),(4,5,10),
   (5,6,11,10),(6,7,11),(2,3,14,13),(3,4,18,14),(4,5,15,18),(14,18,15),
   (5,16,15),(5,6,16),(6,7,17,16),(7,0,12,17),(0,1,13,12),(1,2,13),
   (12,13,14,15,16,17)]
rear=mesh('Focus_Rock_02_Oblique_Shoulder',v,f)
rear['design']='Low slanting roof with two unequal exposed slabs and a broken projecting front buttress.'
wear(rear,.049,.48,3);rear.location=(-1.57,.93,.025);rear.rotation_euler.z=math.radians(-14)

# Foot stone: almost a triangular wedge, different balance and fracture
# direction. A concave upper saddle joins the two front faces.
v=[(-.61,-.48,.03),(-.71,-.49,.34),(-.39,-.45,.84),(.20,-.40,.94),(.60,-.40,.55),(.65,-.25,.13),
   (.22,-.59,.20),(-.15,-.58,.51),(-.45,.43,.08),(-.48,.47,.72),(.25,.42,.81),(.62,.45,.22),(-.08,.04,.73)]
f=[(0,1,7,6),(1,2,7),(2,3,7),(3,4,6,7),(4,5,6),(5,0,6),
   (2,3,12),(2,12,9),(3,10,12),(9,12,10),(3,4,10),(4,5,11,10),
   (5,0,8,11),(0,1,9,8),(1,2,9),(8,9,10,11)]
foot=mesh('Focus_Rock_03_Foot_Wedge',v,f);wear(foot,.033,.49,3)
foot.location=(-.86,-1.07,0);foot.rotation_euler.z=math.radians(22)
foot['design']='Broken triangular wedge with concave saddle. Not a miniature of the main rock.'

# Low rear return is a fully closed flatter shelf, deliberately quiet.
v=[(-.82,-.53,.02),(-.92,-.60,.40),(-.56,-.52,.70),(.31,-.49,.60),(.80,-.42,.35),(.69,-.48,.04),
   (-.73,.59,.03),(-.76,.57,.60),(.35,.59,.68),(.76,.49,.09),(-.22,.08,.72)]
f=[(0,1,2),(0,2,3,4,5),(2,10,3),(2,7,10),(7,8,10),(8,3,10),(3,8,4),(4,8,9,5),
   (5,9,6,0),(0,6,7,1),(1,7,2),(6,9,8,7)]
low=mesh('Focus_Rock_04_Low_Return',v,f);wear(low,.024,.50,2)
low.location=(1.22,.46,.03);low.rotation_euler.z=math.radians(-23)

# Neutral review setup. The floor, camera and lights are never exported.
floor=mesh('Review_Floor',[(-200,-200,-.02),(200,-200,-.02),(200,200,-.02),(-200,200,-.02)],[(0,1,2,3)])
col.objects.unlink(floor);review.objects.link(floor);floor.data.materials.clear()
floor.data.materials.append(material('RockFocus_Floor',(.15,.17,.19)))
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.new('RockFocus_World');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.21,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.45;scene.world=world
for key,power,pos,size in [('Key',900,(-3.5,-4.5,7),4),('Fill',240,(4,-1,4),5),('Rim',500,(1,4,5),3)]:
    d=bpy.data.lights.new('RockFocus_'+key,'AREA');d.energy=power;d.size=size
    o=bpy.data.objects.new(d.name,d);review.objects.link(o);o.location=pos
    o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('RockFocus_Camera');cam=bpy.data.objects.new(d.name,d);review.objects.link(cam);scene.camera=cam
d.type='ORTHO';d.ortho_scale=4.25;cam.location=(3.4,-6.5,4.0)
cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
for o in [rear,foot,low]:o.hide_render=True
scene.render.filepath=str(OUT/'pass1-principal-clay.png');bpy.ops.render.render(write_still=True)
for o in [rear,foot,low]:o.hide_render=False
d.ortho_scale=6.6;cam.location=(3.3,-7,4.6);cam.rotation_euler=(Vector((-.4,.3,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'pass1-group-clay.png');bpy.ops.render.render(write_still=True)

report={'scope':scene['scope'],'scene':NAME,'protected_file_sha256':hashes,
        'rocks':[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'design':o.get('design','quiet shelf')} for o in col.objects],
        'stage':'First actual sculpted geometry, pending visual refinement. Not user acceptance.'}
(OUT/'authoring-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.data.libraries.write(str(ASSET/'sculpted_coastal_rocks.blend'),{scene},fake_user=True,compress=True)
assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
bpy.context.window.scene=original
print(json.dumps({'scene':NAME,'rendered':2,'standalone_source':str(ASSET/'sculpted_coastal_rocks.blend'),'game_files_unchanged':True}))
