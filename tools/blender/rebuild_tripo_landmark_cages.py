"""Tripo replica study: individually traced control cages, via Blender MCP.

Authoring is reference-dependent: footprint landmarks are drawn from the
orthographic views; surface heights and fine multires positions are measured
against the supplied guide. No source vertices, faces, UVs or textures are
copied into the authored objects. This is not an approved independent workflow.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘')
O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
SN='Tripo_Landmark_Cage_Replica_20261119'
assert not bpy.data.scenes.get(SN),'Inspect the saved landmark replica instead of rerunning.'
old=bpy.context.window.scene
ref=bpy.data.scenes['Tripo_Coast_Processing_20261119'].objects['Tripo_Coast_Original_Surface']
bm=bmesh.new();bm.from_mesh(ref.data);tree=BVHTree.FromBMesh(bm);bm.free()
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
c=bpy.data.collections.new('Replica_Individually_Traced_Rock_Cages');s.collection.children.link(c)
rev=bpy.data.collections.new('Replica_Comparison_Only');s.collection.children.link(rev)
clay=bpy.data.materials['Replica_Neutral_Clay']
records=[]

def surface_height(x,y,guess):
    hit,n,i,d=tree.ray_cast(Vector((x,y,.55)),Vector((0,0,-1)),.56)
    return hit.z if hit is not None else guess

def make_mesh(name,vs,fs):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);c.objects.link(o);me.materials.append(clay)
    return o

def fit_detail(o,limit=.027,level=3):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    mr=o.modifiers.new('Measured sculpt detail on authored cage','MULTIRES')
    for _ in range(level):bpy.ops.object.multires_subdivide(modifier=mr.name,mode='SIMPLE')
    mr.levels=level;mr.sculpt_levels=level;mr.render_levels=level
    dg=bpy.context.evaluated_depsgraph_get()
    high=bpy.data.objects.new('TEMP_reference_fitting',bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg));c.objects.link(high)
    fitted=0;dist=[]
    for v in high.data.vertices:
        h,n,i,d=tree.find_nearest(v.co)
        # Preserve the bounded authored support when no close surface exists.
        # Never replace missing faces with a sphere or shoot through thin shells.
        if h is not None and d<limit:
            v.co=h;fitted+=1;dist.append(d)
    high.data.update();o.select_set(True);high.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.multires_reshape(modifier=mr.name)
    bpy.data.objects.remove(high,do_unlink=True);o.select_set(False)
    for p in o.data.polygons:p.use_smooth=True
    o['method']='Individually traced hull cage + reference-measured multires surface detail; no bevel.'
    o['reference_dependent']=True
    return {'fitted_samples':fitted,'detail_samples':len(dist),'fit_max':max(dist,default=0)}

def rock(label,outline,base,depth,shift=(0,0),limit=.028):
    # Every outline below is separately traced, not a randomized common rock.
    top=[(x,y,surface_height(x,y,base+depth)) for x,y in outline]
    cx=sum(p[0] for p in top)/len(top);cy=sum(p[1] for p in top)/len(top)
    vs=list(top)
    for k,(x,y,z) in enumerate(top):
        # Individual basal lean and unequal setbacks define the volume; these
        # are not equal-width bevels around a top face.
        factor=[.87,.97,1.04,.91,1.0,.93,1.02,.90,.98,1.03,.92,1.0][k%12]
        vs.append((cx+(x-cx)*factor+shift[0],cy+(y-cy)*factor+shift[1],base+depth*[.03,.09,0,.045,.02][k%5]))
    # A small number of explicitly displaced shoulder landmarks, at unequal
    # heights, retains the broad break planes without concentric edge strips.
    for k in range(0,len(top),3):
        x,y,z=top[k]
        vs.append((cx+(x-cx)*1.04+shift[0]*.45,cy+(y-cy)*1.025+shift[1]*.4,base+(z-base)*[.48,.68,.39,.57][(k//3)%4]))
    bm=bmesh.new()
    for v in vs:bm.verts.new(v)
    bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    for v in list(bm.verts):
        if not v.link_faces:bm.verts.remove(v)
    me=bpy.data.meshes.new('Cage_'+label);bm.to_mesh(me);bm.free();me.update()
    o=bpy.data.objects.new('Replica_Rock_'+label,me);c.objects.link(o);me.materials.append(clay)
    trace={'name':o.name,'traced_outline':outline,'base':base,'control_vertices':len(me.vertices),'control_faces':len(me.polygons)}
    trace.update(fit_detail(o,limit));records.append(trace)
    return o

specs=[
('Front_Left_Main',[(-.30,-.26),(-.245,-.286),(-.17,-.285),(-.12,-.251),(-.112,-.205),(-.172,-.148),(-.248,-.133),(-.303,-.171),(-.323,-.224)],.13,.21,(.004,.012),.037),
('Front_Right_Main',[(.078,-.275),(.139,-.329),(.213,-.333),(.27,-.301),(.29,-.246),(.282,-.206),(.238,-.167),(.174,-.172),(.127,-.21)],.12,.23,(-.015,.009),.034),
('Left_Long_Shoulder',[(-.353,-.104),(-.314,-.128),(-.26,-.104),(-.24,-.052),(-.244,.045),(-.246,.121),(-.278,.151),(-.337,.138),(-.362,.093),(-.368,.012)],.11,.24,(.013,.004),.035),
('Left_Mid_Back',[(-.288,.177),(-.24,.147),(-.17,.152),(-.135,.181),(-.15,.232),(-.189,.254),(-.26,.233),(-.302,.211)],.16,.17,(.009,-.007),.030),
('Left_Outer_Back',[(-.335,.223),(-.299,.204),(-.251,.23),(-.25,.268),(-.296,.288),(-.337,.274)],.10,.15,(.008,-.008),.025),
('Left_Rear_Crown',[(-.235,.307),(-.203,.276),(-.158,.281),(-.133,.326),(-.152,.365),(-.20,.389),(-.243,.36),(-.265,.334)],.14,.20,(.009,-.01),.027),
('Rear_Left_Ridge',[(-.131,.382),(-.074,.366),(-.02,.39),(-.027,.435),(-.074,.446),(-.124,.43),(-.15,.412)],.15,.20,(0,-.01),.026),
('Rear_Middle_Ridge',[(.027,.37),(.049,.421),(.076,.46),(.106,.448),(.117,.405),(.092,.373)],.14,.22,(0,-.009),.024),
('Rear_Right_Ridge',[(.111,.413),(.118,.461),(.166,.45),(.204,.414),(.222,.37),(.196,.359),(.161,.38)],.14,.23,(-.007,-.008),.024),
('Right_Tall_Crown',[(.182,.25),(.159,.301),(.172,.346),(.207,.354),(.257,.338),(.303,.282),(.323,.243),(.297,.205),(.241,.195)],.18,.28,(-.006,-.012),.035),
('Right_Rear_Shoulder',[(.298,.307),(.31,.343),(.347,.333),(.379,.295),(.37,.257),(.329,.246)],.14,.20,(-.012,-.003),.028),
('Right_Long_Main',[(.21,-.118),(.156,-.097),(.123,-.033),(.148,.035),(.16,.086),(.166,.168),(.207,.193),(.255,.161),(.312,.116),(.344,.048),(.324,-.051),(.294,-.113)],.16,.22,(-.008,.01),.034),
('Right_Outcrop_Top',[(.354,.184),(.347,.24),(.382,.26),(.415,.217),(.412,.178),(.39,.157)],.20,.19,(-.01,0),.028),
('Right_Outer_Shelf',[(.37,.125),(.445,.133),(.463,.114),(.472,.09),(.434,.06),(.397,.06),(.373,.095)],.15,.17,(-.02,-.012),.028),
('Right_Outer_Wall',[(.391,-.073),(.392,.014),(.425,.065),(.469,.057),(.472,.012),(.447,-.061)],.055,.21,(-.018,.007),.034),
('Left_Front_Foot',[(-.387,-.263),(-.33,-.28),(-.284,-.242),(-.289,-.192),(-.32,-.152),(-.367,-.163),(-.405,-.213)],.009,.16,(.009,.007),.033),
('Left_Inset_Foot',[(-.259,-.366),(-.219,-.375),(-.157,-.337),(-.163,-.296),(-.204,-.274),(-.269,-.296),(-.282,-.331)],.006,.17,(.008,.012),.035),
('Left_Stair_Toe',[(-.174,-.425),(-.115,-.437),(-.104,-.394),(-.122,-.35),(-.167,-.359),(-.195,-.399)],.003,.09,(.005,.012),.026),
('Right_Front_Foot',[(.089,-.414),(.154,-.423),(.202,-.398),(.213,-.346),(.177,-.308),(.121,-.32),(.067,-.375)],.004,.16,(-.01,.006),.033),
('Right_Outer_Foot',[(.229,-.361),(.294,-.336),(.334,-.277),(.327,-.228),(.299,-.21),(.277,-.251),(.243,-.279),(.223,-.32)],.006,.18,(-.009,.006),.032),
('Right_Return_Foot',[(.34,-.256),(.37,-.222),(.369,-.161),(.338,-.133),(.317,-.157),(.321,-.216)],.007,.15,(-.013,.005),.030),
('Left_Sea_Ledge',[(-.494,.03),(-.46,.002),(-.421,.004),(-.419,.053),(-.442,.086),(-.482,.081)],.038,.09,(.011,-.006),.021),
('Left_Sea_Foot',[(-.437,-.106),(-.38,-.125),(-.353,-.088),(-.372,-.01),(-.416,-.011),(-.445,-.06)],.006,.12,(.01,.005),.023),
('Left_Back_Foot',[(-.351,.242),(-.318,.254),(-.321,.295),(-.357,.31),(-.38,.279)],.02,.14,(.008,-.006),.022),
]
for sp in specs:rock(*sp)

# The central plate is drawn as an uneven footprint and triangulated to an
# interior support fan. It is not an ellipse, and excludes the static camp props.
outline=[(-.187,-.132),(-.113,-.202),(-.029,-.221),(.067,-.195),(.113,-.12),(.158,-.045),(.151,.092),(.11,.168),(.045,.213),(-.055,.222),(-.151,.195),(-.184,.113),(-.185,.021),(-.18,-.065)]
top=[(x,y,min(.337,surface_height(x,y,.315))) for x,y in outline]
vs=top+[(x*.97,y*.97,z-.053) for x,y,z in top]+[(0,.018,.316)]
n=len(top);fs=[]
for i in range(n):
    j=(i+1)%n;fs.extend([(2*n,i,j),(i,n+i,n+j,j)])
fs.append(tuple(range(2*n-1,n-1,-1)))
plate=make_mesh('Replica_Camp_Plate_Authored',vs,fs)
records.append({'name':plate.name,**fit_detail(plate,.018,3)})

# Individually sized step volumes follow measured nose/height landmarks.
# The reference-only rear stair is included in this study, not an extra game route.
for prefix,count,y0,y1,x0,x1 in [('Front',13,-.448,-.192,-.083,.088),('Rear',6,.242,.38,-.039,.108)]:
    for j in range(count):
        y=y0+(y1-y0)*j/count;yn=y0+(y1-y0)*(j+1)/count
        ym=(y+yn)*.5;z=surface_height((x0+x1)*.5,ym,.06+.23*j/count)
        left=x0+[0,.003,-.002,.001,-.004][j%5];right=x1+[.001,-.002,.003,-.001][j%4]
        vs=[(left,y,z-.007),(right-.002,y+.001,z-.004),(right,yn,z),(left+.002,yn,z+.001),
            (left+.003,y,z-.027),(right-.004,y,z-.027),(right-.001,yn,z-.026),(left+.003,yn,z-.025)]
        fs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
        o=make_mesh('Replica_'+prefix+'_Step_%02d'%j,vs,fs)
        records.append({'name':o.name,**fit_detail(o,.01,2)})

base=bpy.data.scenes['Tripo_Reference_Reconstruction_20261119']
for ob in base.objects:
    if ob.type in {'CAMERA','LIGHT'} or (ob.type=='MESH' and ob.name.startswith('DiagnosticFloor')):
        cp=ob.copy();cp.data=ob.data.copy();rev.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
cam=s.camera;cam.data.ortho_scale=1.43;target=Vector((0,0,.21))
s['revision']='landmark-cages-visual-study-1'
bpy.data.libraries.write(str(A/'tripo_landmark_cage_replica.blend'),{s},fake_user=True,compress=True)
for angle in [0,35]:
    a=math.radians(angle);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(O/('landmark-replica-gray-%s.png'%angle));bpy.ops.render.render(write_still=True)
(O/'landmark-cage-authoring.json').write_text(json.dumps({'scene':SN,'records':records,'method':__doc__,'source':'tools/blender/rebuild_tripo_landmark_cages.py'},ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old
print(json.dumps({'scene':SN,'rocks':len(specs),'objects':len(c.objects),'revision':s['revision'],'status':'Rendered sample for actual visual inspection. Not accepted or a final workflow.'}))
