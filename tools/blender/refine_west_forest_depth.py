"""Refine the observed forest canopy, near slope and coastal seam in Blender."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast,random
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/bamboo-west-extension-review';COL=bpy.data.collections['43_West_Forest']
assert not SCENE.objects.get('WALK_Forest_NearSlope')
tree=ast.parse((ROOT/'tools/blender/build_left_vegetation.py').read_text(encoding='utf-8'))
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name=='leaf':exec(compile(ast.Module(body=[node],type_ignores=[]),'leaf','exec'))
forest=SCENE.objects['WALK_Forest_Ground'];old=SCENE.objects['WALK_Left_Ground']
trees=[BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]) for ob in [forest,old]]
def floor(x,y):
    hits=[tree.ray_cast(Vector((x,y,35)),Vector((0,0,-1)))[0] for tree in trees];hits=[p.z for p in hits if p is not None]
    return max(hits) if hits else None
front=json.loads((REVIEW/'forest-layout.json').read_text())['outline'][:6]
vs=[];fs=[]
for i in range(101):
    x=-49+(49-18.25)*i/100
    k=min(len(front)-2,max(0,next((j for j in range(len(front)-1) if front[j+1][0]>=x),len(front)-2)))
    a,b=front[k:k+2];t=max(0,min(1,(x-a[0])/(b[0]-a[0])));y=a[1]+(b[1]-a[1])*t
    z=floor(x,y+.055)
    if z is None:z=5.7
    for j in range(15):
        d=j/14;yy=y+.08-11*d;zz=z-.95*sm(0,1,d)+.14*math.sin(x*.39+d*2.5)*math.sin(d*math.pi)
        vs.append((x,yy,zz))
for i in range(100):
    for j in range(14):
        a=i*15+j;fs.extend([(a,a+15,a+16),(a,a+16,a+1)])
m=Mesh('WALK_Forest_NearSlope');m.part(vs,fs,bpy.data.materials['Forest_Floor'],[((p[0]+50)/54,(p[1]+4)/40) for p in vs]);ob=m.build(smooth=True)
trees.append(BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
bank=SCENE.objects['Forest_Continuous_Bank'];bank.hide_set(True);bank.hide_render=True
archive=bpy.data.collections['90_Before_Forest_Composition'];COL.objects.unlink(bank);archive.objects.link(bank)

# Additional overlapping sprays form a canopy, while preserving the clear
# lower culms. Clusters have directional branch attachments, no whole-tree cards.
records=json.loads((REVIEW/'forest-authoring.json').read_text())['roots'];rng=random.Random(2347)
groups={}
for rec in records:groups.setdefault(rec['object'],[]).append(rec)
canopy_records=[]
for name,roots in groups.items():
    band=roots[0]['band'];builder=Mesh('Forest_Bamboo_Canopy_'+name[-2:])
    if band=='front':continue
    for si,rec in enumerate(roots):
        x,y,z=rec['root'];h=rec['height']
        # Middle forest foliage enters the frame above the walking band.
        for level in range(2):
            ch=(3.3 if band in ['rear','old'] else 3.7)+level*1.32
            start=Vector((x,y,z+ch));phase=si*2.4+int(name[-2:])*.65+level*1.8
            for branch in range(3):
                a=phase+branch*2.18;axis=Vector((math.cos(a),math.sin(a),.06));L=1.55 if level else 1.35
                end=start+axis*L+Vector((0,0,.1));elbow=start.lerp(end,.46)+Vector((0,0,.15))
                tube(builder,[start,elbow,end],[.026,.015,.006],'branch',5,[.32,.42,.52])
                for tw in [-1,0,1]:
                    begin=elbow.lerp(end,.36 if tw else .8);aa=a+tw*.74;ax=Vector((math.cos(aa),math.sin(aa),-.18));tip=begin+ax*.98
                    tube(builder,[begin,tip],[.009,.003],'branch',5,[.42,.52])
                    for li in range(9):
                        side=-1 if li%2 else 1;angle=aa+side*.80;d=Vector((math.cos(angle),math.sin(angle),[-.30,.01,-.17][li%3]))
                        length=[.47,.60,.56,.67][(li+si)%4]
                        leaf(builder,begin.lerp(tip,.08+li*.103),d,length,length*.23,(li%3-1)*.35,.52,[.9,1.04,.97][li%3])
        canopy_records.append({'grove':name,'root':rec['root']})
    ob=builder.build();LAYOUT['forest_extension']['groves'].append({'name':ob.name,'band':band})

# Wide fern-like understory and grouped grass occupy the banks, with gaps around
# the path. They receive the same sunlight and move independently of the actor.
under=Mesh('Forest_Grass_Understory')
centers=[(-22,9.0),(-25.5,8),(-29,7.0),(-33.5,8.4),(-38,7.7),(-43.5,8.8),(-47,10),
(-18.8,17.4),(-22,18),(-25,18.2),(-28.1,19.8),(-31.8,17.2),(-35.7,19.2),(-39.1,18.3),(-43,20),(-46.2,19.5),
(-6.1,10.9),(-4.1,9.0),(-2.4,6.6),(-7.6,15.4),(-11,19.6),(-16,22),(-20,24.6),(-30,26),(-36,26),(-41,27)]
for ci,(x,y) in enumerate(centers):
    z=floor(x,y)
    if z is None:continue
    for fr in range(8):
        a=fr*2.399+ci*.75;axis=Vector((math.cos(a),math.sin(a),.28));L=[.73,.88,1.02,.68][(fr+ci)%4]
        base=Vector((x,y,z-.03));elbow=base+axis*L*.46+Vector((0,0,.28));tip=base+axis*L+Vector((0,0,.14))
        tube(under,[base,elbow,tip],[.014,.01,.002],'grass_blade',5,[0,.55,1])
        for j in range(6):
            p=elbow.lerp(tip,j/6);ln=(.24*(1-j/7)+.10)
            for side in [-1,1]:
                aa=a+side*.94;leaf(under,p,Vector((math.cos(aa),math.sin(aa),.08-j*.04)),ln,ln*.32,side*.2,.8,[.96,1.08,.90][(j+ci)%3],'grass_blade')
under.build()

# A narrow embedded rock shoulder gives the coastal side a readable transition,
# replacing the exposed featureless wedge without blocking the path.
for i,(x,y,sx,sy,h) in enumerate([(-2.0,5.2,.95,.60,.44),(-3.8,8.5,1.15,.8,.51),(-6.5,12.8,1.2,.9,.63)]):
    z=floor(x,y)
    if z is None:continue
    b=Mesh('Forest_Rock_CoastalShoulder_%02d'%i);plan=[(-1,-.30),(-.65,-.72),(.58,-.62),(1,.24),(.42,.85),(-.70,.55)]
    low=[(x+px*sx,y+py*sy,z-.3) for px,py in plan];high=[(x+px*sx*.86,y+py*sy*.8,z+h+.08*px-.09*py) for px,py in plan]
    b.part(low+high,[(j,(j+1)%6,(j+1)%6+6,j+6) for j in range(6)],'rock_b');b.part(high,tri(high),'rock_top');b.part(low,[tuple(reversed(t)) for t in tri(low)],'rock_c');b.build()
LAYOUT['camera']['physical_offset']=[0,6.15,32.85]
LAYOUT['camera']['physical_fov']=22.5
for im in bpy.data.images:
    if 'forest_extension/forest_floor.png' in bpy.path.abspath(im.filepath).replace('\\','/'):
        if im.packed_file:im.unpack(method='REMOVE')
        im.reload();im.pack()
export('west-forest-depth')
