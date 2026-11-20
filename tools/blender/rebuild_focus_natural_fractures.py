"""Author disconnected-from-game rock study through the real Blender MCP.

Explicit, different surface networks. No bevel, uniform edge strip, noise
modifier, polygon-hole cutter, or Tripo mesh/texture reuse is present.
"""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/rock-sculpt-focus-review'
ASSET=ROOT/'assets/layered_island/rock_sculpt_focus'
NAME='Natural_Fracture_Rocks_20261119'
assert not bpy.data.scenes.get(NAME), 'Existing study: inspect/refine instead of resubmitting.'
old=bpy.context.window.scene
baseline=bpy.data.scenes['Rock_Sculpt_Focus_20261119']
protected=[ROOT/'assets/layered_island'/n for n in ['layered_island.blend','layered_island.glb','layout.json']]
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
s=bpy.data.scenes.new(NAME);bpy.context.window.scene=s
col=bpy.data.collections.new('Natural_Fracture_Authored');s.collection.children.link(col)
review=bpy.data.collections.new('Natural_Fracture_Review_Only');s.collection.children.link(review)
s['scope']='Independent rocks only. Game and surroundings untouched. No bevel.'

def mat(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.9
    return m
clay=mat('NaturalRock_Clay',(.30,.32,.33))

def mesh(name,v,f):
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), name+' control mesh must be closed'
    bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=10,use_grid_fill=True)
    bm.to_mesh(me);bm.free();me.update()
    o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(clay)
    return o

def sculpt(o,strokes,front_paths=(),top_paths=()):
    # Directional volume-conserving local losses never shrink a concave
    # junction along competing normals. Each radius and direction is authored.
    bm=bmesh.new();bm.from_mesh(o.data)
    tree=BVHTree.FromBMesh(bm);bm.free()
    surface_paths=[]
    for points in front_paths:
        pts=[]
        for x,z,width,depth in points:
            hit=tree.ray_cast(Vector((x,-4,z)),Vector((0,1,0)),8)[0]
            assert hit is not None, (o.name,x,z)
            pts.append((hit.copy(),width,depth))
        surface_paths.append(('front',pts))
    for points in top_paths:
        pts=[]
        for x,y,width,depth in points:
            hit=tree.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),8)[0]
            assert hit is not None, (o.name,x,y)
            pts.append((hit.copy(),width,depth))
        surface_paths.append(('top',pts))
    for v in o.data.vertices:
        p=v.co.copy();delta=Vector((0,0,0))
        for center,radii,direction in strokes:
            q=sum(((p[k]-center[k])/radii[k])**2 for k in range(3))
            delta+=Vector(direction)*math.exp(-q*1.9)
        for axis,pts in surface_paths:
            best=0
            for (a,wa,da),(b,wb,db) in zip(pts,pts[1:]):
                ab=b-a;t=max(0,min(1,(p-a).dot(ab)/ab.length_squared))
                c=a+ab*t;width=wa*(1-t)+wb*t;depth=da*(1-t)+db*t
                d=(p-c).length
                # Variable tapered width and depth. No enclosed pocket,
                # constant chamfer band or geometrically extruded hole.
                strength=depth*math.exp(-1.7*(d/max(width,.001))**2)
                best=max(best,strength)
            if axis=='front':delta.y+=best
            else:delta.z-=best
        v.co+=delta
    o.data.update()
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    sm=o.modifiers.new('Minimal local tessellation relaxation','SMOOTH');sm.factor=.19;sm.iterations=2
    bpy.ops.object.modifier_apply(modifier=sm.name)
    # This smooths the small tessellation only: no bevel surface is created.
    for p in o.data.polygons:p.use_smooth=True
    o.select_set(False)
    o['no_bevel']=True
    o['front_fractures']=json.dumps([[(list(p),w,d) for p,w,d in ps] for axis,ps in surface_paths if axis=='front'])
    return o

# Main exposed block: descending roof, broken left shoulder, a broad diagonal
# front junction, low inward return and projecting foot. No horizontal ring.
v=[(-1.22,-.56,.06),(-1.47,-.69,.48),(-1.35,-.82,1.12),(-1.03,-.74,1.81),
   (-.39,-.68,1.97),(.33,-.56,1.83),(.87,-.67,1.77),(1.22,-.62,1.39),
   (1.32,-.75,.71),(1.05,-.64,.20),(.48,-.74,.035),(-.36,-.57,.01),
   (-1.13,-.92,.76),(-.84,-.96,1.51),(-.43,-.90,1.20),(-.66,-1.02,.44),
   (.00,-.98,.88),(.37,-.91,1.49),(.69,-.96,.99),(.62,-.88,.47),(-.35,-1.10,.82),
   (-1.12,.48,1.98),(-.45,.78,1.82),(.32,.65,1.97),(.88,.61,1.64),(1.09,.39,1.48),
   (-1.41,.37,1.03),(-1.32,.63,.41),(-1.10,.58,.04),(.28,.65,.02),(1.02,.53,.17),
   (1.30,.43,.71),(-.40,.07,2.05),(.24,-.12,1.84),(-.42,.85,1.02),(.73,.72,.79)]
f=[(0,1,12,15,11),(1,2,13,12),(2,3,13),(3,4,17,14,13),(4,5,17),(5,6,17),
   (6,7,18,17),(7,8,18),(8,9,19,18),(9,10,19),(10,11,15,16,19),
   (12,13,14,20,15),(14,17,18,16,20),(15,20,16),(16,18,19),
   (3,4,32,21),(4,5,33,32),(5,6,24,23,33),(21,32,33,23,22),(6,7,25,24),
   (0,1,27,28),(1,2,26,27),(2,3,21,26),(7,8,31,25),(8,9,30,31),(9,10,29,30),
   (21,22,34,26),(22,23,35,34),(23,24,25,31,35),(26,34,27),
   (34,35,30,29,28,27),(35,31,30),(0,28,29,10,11)]
hero=mesh('Natural_Rock_01_Main_Block',v,f)
sculpt(hero,[
    ((-1.11,-.73,1.66),(.28,.32,.26),(.11,.055,-.075)),
    ((-.42,-.69,1.92),(.25,.27,.22),(.018,.070,-.073)),
    ((.87,-.63,1.70),(.30,.28,.25),(-.063,.077,-.098)),
    ((1.28,-.68,.79),(.20,.27,.33),(-.105,.048,.031)),
    ((-1.39,-.77,.80),(.22,.24,.32),(.072,.033,-.020)),
    ((-.66,-.91,1.12),(.51,.23,.40),(.014,.046,-.003)),
    ((.30,-.94,1.27),(.58,.21,.43),(.012,-.035,.014)),
    ((-.38,.04,2.04),(.58,.53,.22),(.021,.007,-.025)),
    ((.02,-1.00,.62),(.28,.24,.20),(-.009,.032,.016)),
    ((-.94,.56,1.85),(.22,.29,.30),(.048,-.020,-.048))
],front_paths=[[
    (-1.16,.48,.009,.009),(-.85,.64,.041,.033),(-.53,.82,.055,.050),
    (-.21,1.11,.024,.025),(.13,1.29,.038,.038),(.36,1.54,.046,.041),(.43,1.72,.012,.007)],
    [(-1.28,1.26,.004,.003),(-1.06,1.23,.025,.025),(-.82,1.34,.023,.021),(-.62,1.48,.003,.002)]],
    top_paths=[[(-.78,-.46,.004,.003),(-.49,-.24,.020,.018),(-.21,.02,.034,.029),(.18,.23,.016,.015),(.44,.38,.003,.002)]])
hero['design']='Wide diagonal face, unequal shoulder and descending crown; continuous complete volume.'

# Rear shoulder: long low tilted slab with an offset front projection.
v=[(-1.25,-.55,.02),(-1.44,-.59,.53),(-1.12,-.53,1.25),(-.62,-.42,1.61),
   (.06,-.45,1.52),(.62,-.51,1.31),(1.01,-.42,.90),(1.20,-.60,.26),(.81,-.45,.02),
   (-.97,-.83,.61),(-.63,-.82,1.19),(-.05,-.73,1.02),(.46,-.77,.63),(.16,-.82,.26),
   (-1.16,.63,.04),(-1.33,.46,.69),(-.78,.49,1.51),(.02,.70,1.66),(.61,.58,1.20),
   (1.19,.55,.37),(.79,.71,.04),(-.36,.05,1.47)]
f=[(0,1,9),(0,9,13,8),(1,2,10,9),(2,3,10),(3,4,11,10),(4,5,12,11),
   (5,6,12),(6,7,13,12),(7,8,13),(9,10,11,13),(11,12,13),
   (2,3,16),(3,4,17,21,16),(4,5,18,17),(5,6,18),(6,7,19,18),
   (0,1,15,14),(1,2,16,15),(7,8,20,19),(8,0,14,20),(14,15,16,21,17,18,19,20)]
shoulder=mesh('Natural_Rock_02_Slant_Shoulder',v,f)
sculpt(shoulder,[
    ((-1.10,-.54,1.22),(.27,.30,.23),(.090,.060,-.070)),
    ((-.61,-.43,1.56),(.23,.28,.21),(.022,.061,-.065)),
    ((.62,-.46,1.29),(.23,.28,.26),(-.051,.063,-.071)),
    ((1.10,-.53,.42),(.25,.24,.22),(-.055,.049,.020)),
    ((-.20,-.76,.94),(.47,.22,.42),(-.012,.042,-.013)),
    ((-.77,.48,1.45),(.27,.30,.23),(.029,-.028,-.043))
],front_paths=[[(-1.28,.45,.007,.006),(-.91,.70,.032,.027),(-.55,.98,.041,.033),(-.26,1.25,.018,.014),(-.05,1.42,.003,.002)]],
top_paths=[[(-.85,-.19,.004,.003),(-.54,.03,.026,.019),(-.11,.30,.032,.025),(.24,.47,.004,.002)]])
shoulder.location=(-1.92,1.00,.005);shoulder.rotation_euler.z=math.radians(-18)
shoulder['design']='Long oblique shoulder with high rear crown and shorter broken front lip.'

# Toe: oblique projecting shard with a broken tall left side, not a rounded pebble.
v=[(-.71,-.44,.025),(-.84,-.45,.34),(-.57,-.40,.88),(-.24,-.46,1.02),
   (.21,-.31,.74),(.62,-.36,.48),(.71,-.25,.10),(.19,-.46,.005),
   (-.45,-.62,.48),(-.18,-.58,.73),(.23,-.55,.27),
   (-.64,.41,.025),(-.72,.41,.65),(-.20,.48,.93),(.34,.43,.68),(.67,.49,.16),(-.04,.06,.81)]
f=[(0,1,8,7),(1,2,9,8),(2,3,9),(3,4,9),(4,5,10,9),(5,6,10),(6,7,10),
   (8,9,10,7),(2,3,13,12),(3,4,16,13),(4,5,14,16),(13,16,14),(5,6,15,14),
   (6,7,0,11,15),(0,1,12,11),(1,2,12),(11,12,13,14,15)]
toe=mesh('Natural_Rock_03_Projecting_Toe',v,f)
sculpt(toe,[
    ((-.55,-.41,.85),(.20,.21,.18),(.058,.044,-.048)),
    ((-.24,-.43,.98),(.17,.23,.15),(.031,.019,-.032)),
    ((.56,-.37,.47),(.20,.21,.20),(-.051,.027,-.023)),
    ((-.47,-.58,.41),(.23,.22,.26),(.022,.033,.015))
],front_paths=[[(-.71,.38,.006,.004),(-.40,.48,.023,.024),(-.12,.62,.019,.014),(.18,.70,.003,.002)]])
toe.location=(-.73,-1.04,.005);toe.rotation_euler.z=math.radians(27)
toe['design']='Angular oblique toe with broken crown and low rightward runout.'

# Quiet low shelf has its own broad tilted top and a notched far corner.
v=[(-.93,-.45,.02),(-1.04,-.45,.31),(-.70,-.35,.70),(-.18,-.36,.72),
   (.32,-.48,.59),(.83,-.37,.27),(.69,-.36,.02),(-.31,-.54,.27),
   (-.90,.55,.03),(-.73,.63,.54),(-.16,.51,.71),(.29,.61,.61),(.87,.47,.15),(-.30,.02,.65)]
f=[(0,1,7),(1,2,3,7),(3,4,5,7),(5,6,0,7),(2,3,13,9),(3,4,11,10,13),(9,13,10),
   (4,5,12,11),(5,6,12),(6,0,8,12),(0,1,9,8),(1,2,9),(8,9,10,11,12)]
shelf=mesh('Natural_Rock_04_Low_Shelf',v,f)
sculpt(shelf,[
    ((-.71,-.38,.66),(.24,.22,.18),(.065,.035,-.038)),
    ((.33,-.43,.55),(.23,.22,.18),(-.025,.040,-.041)),
    ((.78,.47,.23),(.20,.22,.19),(-.049,-.020,.018))])
shelf.location=(1.36,.53,.008);shelf.rotation_euler.z=math.radians(-21)
shelf['design']='Wide quiet shelf with off-axis crown and uneven front lip.'
rocks=[hero,shoulder,toe,shelf]

# Same neutral lighting as the preceding failed study, for honest comparison.
for o in baseline.objects:
    if o.type in {'CAMERA','LIGHT'} or o.name=='Review_Floor':
        cp=o.copy();cp.data=o.data.copy();review.objects.link(cp)
        cp.hide_render=False;cp.hide_set(False)
        if cp.type=='CAMERA':s.camera=cp
s.world=baseline.world.copy()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
cam=s.camera;cam.data.ortho_scale=4.25;cam.location=(3.4,-6.5,4.0)
cam.rotation_euler=(Vector((0,0,1.06))-cam.location).to_track_quat('-Z','Y').to_euler()
for o in rocks:o.hide_render=o!=hero
s.render.filepath=str(OUT/'natural-pass1-main-clay.png');bpy.ops.render.render(write_still=True)
for o in rocks:o.hide_render=False
cam.data.ortho_scale=6.6;cam.location=(3.3,-7,4.6)
cam.rotation_euler=(Vector((-.4,.3,.9))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(OUT/'natural-pass1-group-clay.png');bpy.ops.render.render(write_still=True)
s['revision']='natural-control-surfaces-1'
bpy.data.libraries.write(str(ASSET/'natural_fracture_rocks.blend'),{s},fake_user=True,compress=True)
assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
report={'scope':s['scope'],'scene':s.name,'revision':s['revision'],'protected_file_sha256':hashes,
 'no_bevel_or_boolean_holes':True,'source':'tools/blender/rebuild_focus_natural_fractures.py',
 'rocks':[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'design':o['design']} for o in rocks],
 'status':'Actual standalone gray study. Pending visual review; not user approval.'}
(OUT/'natural-authoring-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old
print('Natural-control surfaces saved and two actual clay renders completed. Game files unchanged.')
