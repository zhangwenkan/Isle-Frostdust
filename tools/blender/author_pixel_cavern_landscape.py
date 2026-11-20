"""New complete coast composition, authored from user image through Blender MCP."""
import bpy
from pathlib import Path
exec((Path('D:/自己做着玩的/孤屿霜尘/tools/blender/pixel_cavern_lib.py')).read_text(encoding='utf-8'),globals())
assert SCENE not in bpy.data.scenes,'Scene exists: use a scoped refinement.'
scene=bpy.data.scenes.new(SCENE);bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene['revision']='pixel-cavern-landscape-1'
scene['source_reference']='user-cavern-coast.png; new scene, no prior assets'
ground=collection('01_Ground');cliff=collection('02_Cliffs');stairs=collection('03_Stone_Routes');bridge=collection('04_Rope_Bridge');cave=collection('05_Cavern');sea=collection('06_Shore')
P=palette()

# Continuous core profiles are designed for this composition, with a stair bay
# removed from the front left. Visible rocks articulate the surrounding volumes.
left=[(-17,-3.0),(-14,-4.6),(-10,-5.1),(-8.7,-3.8),(-8.6,-.6),(-5.7,-.45),(-5.2,-3.0),(-3.7,-3.05),(-1.7,-1.25),(-1.65,2.5),(-3.6,5.3),(-7,8.6),(-12,10.5),(-17,8)]
right=[(5.8,-.8),(6.3,-2.4),(8.8,-3.35),(12,-3),(16.5,-2.0),(18,1),(17.5,9),(14,11),(9,10),(6.9,5)]
slab('Rock_Left_Continuous_Core',left,4.27,6.2,ground,[P['stone_shadow']])
slab('Soil_Left_Root_Bank',left,4.44,.40,ground,[P['earth']],.03)
slab('Grass_Left_Terrace',left,4.47,.12,ground,[P['grass']],.015)
slab('Rock_Right_Continuous_Core',right,4.25,10.0,ground,[P['stone_shadow']])
slab('Soil_Right_Root_Bank',right,4.40,.35,ground,[P['earth']],.02)
slab('Grass_Right_Terrace',right,4.45,.10,ground,[P['grass']],.015)

# Rock masses are fitted into the terrain; varying shoulder scale creates
# alternate vertical breaks and low shelves rather than identical layered rings.
spec=[
 ('LWest',(-15,-3.9,1.8),(3.5,1.75,3.0),3,.10),
 ('LFront',(-11.2,-4.5,1.6),(2.8,1.45,3.0),8,-.12),
 ('LStairJamb',(-9.2,-2.7,2.0),(1.20,1.7,2.6),14,.1),
 ('LBridgeShoulder',(-4.25,-2.8,1.8),(2.2,1.8,3.05),19,-.26),
 ('LBridgeToe',(-2.6,-1.20,.5),(1.6,1.7,2.15),23,.12),
 ('LLowWide',(-12,-6.0,-.12),(2.8,1.5,1.2),21,-.3),
 ('LStairToe',(-5.4,-5.3,.45),(1.3,1.2,1.5),27,-.3),
 ('RBridgeFace',(7.35,-2.3,1.1),(2.25,1.55,3.9),32,.3),
 ('RFront',(10.9,-3.1,.25),(2.5,1.55,4.1),39,-.1),
 ('REdge',(14.8,-2.4,1.0),(2.8,2.25,4.8),43,.2),
 ('RLow',(11.6,-3.8,-2.8),(2.7,1.6,2.7),51,-.2),
 ('RNear',(15.3,-6.2,-2.3),(3.2,2.1,4.0),61,-.3)]
for name,c,s,seed,turn in spec:rock('Rock_Cliff_'+name,c,s,cliff,[P['stone'],P['stone_light']],seed,turn)

# Curved sand cove, with a broad shallow bed under transparent-looking water.
shorepoly=[(-18,-9.0),(-16,-12),(-11,-13.1),(-7,-12.1),(-4,-10.2),(-3.8,-7.8),(-5.4,-5.6),(-8,-4.9),(-11,-5.2),(-15,-5.3),(-17,-6.3)]
slab('Sand_Cove',shorepoly,.24,1.05,sea,[P['sand']],.06)
wet=[(-18.4,-9.5),(-16.1,-12.5),(-11.0,-13.5),(-6.8,-12.65),(-3.8,-10.45),(-3.5,-8.5),(-4.0,-9.8),(-7.3,-11.9),(-11,-12.65),(-15.6,-11.65),(-17.7,-9.2)]
slab('Sand_Wet_Edge',wet,.07,.5,sea,[P['sand_wet']])
slab('Rock_Submerged_Shelf',[(-20,-15),(-10,-17),(-1,-12),(-1,-5),(-8,-5),(-19,-6)],-.55,.8,sea,[P['stone_cool']])
mesh('Water_Main',[(-180,-180,0),(180,-180,0),(180,180,0),(-180,180,0)],[(0,1,2,3)],sea,[P['water']])

# The stair route is constructed as stone masonry laid into an earth/stone ramp.
def stairway(name,start,end,count,width,base):
    a=Vector(start);b=Vector(end);d=Vector((b.x-a.x,b.y-a.y,0));total=d.length;d.normalize();p=Vector((-d.y,d.x,0));run=total/count;rise=(b.z-a.z)/count
    pts=[a-p*width*.55,b-p*width*.55,b+p*width*.55,a+p*width*.55]
    vs=[(q.x,q.y,base) for q in pts]+[(pts[0].x,pts[0].y,a.z-.12),(pts[1].x,pts[1].y,b.z-.12),(pts[2].x,pts[2].y,b.z-.12),(pts[3].x,pts[3].y,a.z-.12)]
    mesh('Rock_'+name+'_Buried_Ramp',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stairs,[P['stone_shadow']])
    for i in range(count):
        c=a+d*((i+.5)*run);top=a.z+(i+1)*rise
        split=2 if i%4!=2 else 3;cutoffs=[-width*.5]
        for j in range(1,split):cutoffs.append(-width*.5+width*j/split+(.14 if (i+j)%2 else -.10))
        cutoffs.append(width*.5)
        for j in range(split):
            l,r=cutoffs[j]+.012,cutoffs[j+1]-.012
            poly=[tuple((c+d*u+p*v).xy) for u,v in [(-run*.52,l+.03),(-run*.51,r-.045),(-run*.38,r+.01),(run*.52,r-.02),(run*.51,l+.08),(run*.35,l-.01)]]
            slab('Step_'+name+'_%02d_%d'%(i,j),poly,top,rise+.16,stairs,[P['step'] if (i+j)%3 else P['step_alt']],.016)
        if name=='Beach':
            for sign in [-1,1]:
                q=c+p*sign*(width*.5+.15)
                poly=[tuple((q+d*u+p*v).xy) for u,v in [(-run*.5,-.14),(run*.5,-.14),(run*.5,.14),(-run*.5,.14)]]
                slab('Rock_Stair_Curb_%d_%d'%(i,sign),poly,top+.06,rise+.42,stairs,[P['stone']],.018)
    return a,b
stairway('Beach',(-7.15,-8.35,.28),(-7.15,-.65,4.44),16,2.62,-.45)
stairway('Forest',(-8.5,2.5,4.47),(-10.2,7.2,6.00),7,2.8,3.5)
slab('Soil_Upper_Forest',[(-15,5),(-11,5.7),(-8.7,7),(-7.4,9),(-11,12),(-17,11)],5.95,2.0,ground,[P['earth']])
slab('Grass_Upper_Forest',[(-15,5),(-11,5.7),(-8.7,7),(-7.4,9),(-11,12),(-17,11)],6.03,.12,ground,[P['grass_dark']])

# Flagstones follow the bridge path, with incomplete edge stones and green gaps.
def paved_path(name,points,width):
    for seg in range(len(points)-1):
        a=Vector(points[seg]);b=Vector(points[seg+1]);di=b-a;length=di.length;di.normalize();p=Vector((-di.y,di.x,0))
        rows=max(2,int(length/.65))
        for i in range(rows):
            c=a+(b-a)*(i+.5)/rows
            for j in range(3):
                q=c+p*((j-1)*width/3+.04*math.sin(i*3+j));ln=length/rows*.47;w=width/3*.46
                poly=[tuple((q+di*u+p*v).xy) for u,v in [(-ln,-w*.78),(-ln*.85,w*.8),(-ln*.4,w),(ln*.87,w*.9),(ln,w*.35),(ln*.9,-w*.9),(-ln*.25,-w)]]
                slab('Path_'+name+'_%d_%d_%d'%(seg,i,j),poly,q.z,.09,stairs,[P['path'] if (i+j)%3 else P['step_alt']],.008)
paved_path('Left',[(-8.5,2.3,4.51),(-7.15,.0,4.51),(-4.7,.1,4.51),(-1.75,.8,4.51)],2.2)
paved_path('Cave',[(6,.8,4.50),(8,1.65,4.50),(10.7,3.9,4.50)],2.5)

# Suspension bridge: individual planks, longitudinal load ropes and hanging rails.
x0=-1.9;x1=6.25;y=.8
def bridge_z(t):return 4.43-.65*math.sin(math.pi*t)
for i in range(26):
    t=(i+.5)/26;x=x0+(x1-x0)*t;z=bridge_z(t)
    skew=.025*math.sin(i*2.7)
    poly=[(x-.145,y-1.00+skew),(x+.145,y-1.03),(x+.14,y+1.02),(x-.14,y+.98-skew)]
    slab('Plank_Bridge_%02d'%i,poly,z,.16,bridge,[P['wood'] if i%3 else P['wood_lit']],.012,slope=(.0,.025*math.sin(i)))
    # Sparse inset grain, scale larger than subpixel hairs.
    if i%3==0:
        tube('Wood_Grain_%02d'%i,[(x-.05,y-.8,z+.005),(x-.06,y,z+.005),(x-.04,y+.60,z+.005)],.009,bridge,P['wood_dark'],sides=4)
for sign in [-1,1]:
    tube('Rope_Under_%d'%sign,[(x0+(x1-x0)*j/40,y+sign*.82,bridge_z(j/40)-.15) for j in range(41)],.060,bridge,P['wood_dark'])
    tube('Rope_Handrail_%d'%sign,[(x0+(x1-x0)*j/40,y+sign*1.08,bridge_z(j/40)+1.16) for j in range(41)],.051,bridge,P['rope'])
    for i in range(12):
        t=(i+.3)/12;u=(i+.85)/12
        tube('Rope_Brace_%d_%02d'%(sign,i),[(x0+(x1-x0)*t,y+sign*1.08,bridge_z(t)+1.12),(x0+(x1-x0)*u,y+sign*.93,bridge_z(u)+.02)],.029,bridge,P['rope'],sides=5)
    for j,x in enumerate([x0,x1]):
        tube('Wood_Bridge_Post_%d_%d'%(sign,j),[(x,y+sign*1.10,3.95),(x+.02,y+sign*1.10,5.95)],.14,bridge,P['wood'],sides=9)
        for k in range(3):
            pts=[(x+.17*math.cos(a*math.tau/18),y+sign*1.10+.17*math.sin(a*math.tau/18),5.52+k*.055) for a in range(19)]
            tube('Rope_Post_Knot_%d_%d_%d'%(sign,j,k),pts,.027,bridge,P['rope'],sides=5)
        tube('Rope_Post_Anchor_%d_%d'%(sign,j),[(x,y+sign*1.10,5.53),(x+(-.8 if j==0 else .8),y+sign*1.65,4.52)],.047,bridge,P['rope'])

# A real cavern void, built as irregular continuous inner rings plus massive
# external stones; the roof does not fill the opening.
cx=11.1;cy=4.25;base=4.45
profile=[(-2.2,0),(-2.35,1.5),(-1.95,3.1),(-1.12,4.35),(.15,4.70),(1.40,4.1),(2.15,2.8),(2.30,1.2),(2.15,0)]
vs=[]
for ri,depth in enumerate([0,1.0,3.2,6.7]):
    for x,z in profile:vs.append((cx+x*(1-.035*ri)+.13*ri,cy+depth,base+z+ri*.10))
n=len(profile);fs=[]
for ri in range(3):
    for i in range(n-1):fs.append((ri*n+i,ri*n+i+1,(ri+1)*n+i+1,(ri+1)*n+i))
mesh('CaveInterior_Vault',vs,fs,cave,[P['cave'],P['cave_inner']],[0 if i<16 else 1 for i in range(len(fs))])
mesh('CaveInterior_Dark_End',[(cx+x*.9+.39,cy+6.8,base+z+.3) for x,z in profile],[tuple(range(n))],cave,[P['cave_inner']])
stairway('Cave',(cx,cy+.25,4.46),(cx+.2,cy+5.8,6.5),11,3.9,3.9)

arch_specs=[
 ('LeftBase',(8.55,4.3,5.1),(1.6,1.7,1.9),81,-.2),
 ('LeftJamb',(8.45,4.55,7.2),(1.45,1.85,1.95),84,-.13),
 ('LeftCrown',(9.35,4.7,9.10),(1.65,1.85,1.55),88,.1),
 ('Lintel',(11.30,4.8,10.0),(2.2,2.0,1.4),92,-.15),
 ('RightCrown',(13.2,4.8,9.0),(1.55,1.85,1.8),97,.25),
 ('RightJamb',(13.8,4.9,6.8),(1.5,2.0,2.1),102,.2),
 ('RightToe',(14.6,3.2,4.7),(1.8,1.9,1.2),107,-.3),
 ('LeftToe',(7.8,3.1,4.6),(1.5,1.65,1.1),111,.2),
 ('RoofBack',(11.3,7.7,10.2),(4.0,3.0,1.5),115,-.1),
 ('RightRear',(16,6.4,7.0),(2.4,3.0,3.4),117,.1)]
for name,c,s,se,rot in arch_specs:rock('Rock_Cave_'+name,c,s,cave,[P['stone'],P['stone_light']],se,rot)

# Major roots follow the rim rather than obstruct the void.
roots=[[(7.9,2.95,4.6),(8.2,2.95,5.8),(8.05,2.8,7.3),(8.55,3.0,8.5),(9.6,3.2,9.4),(11.4,3.2,10.85)],
[(14.1,2.8,4.55),(13.7,2.95,5.65),(14.0,2.9,7.1),(13.5,3.0,8.65),(12.4,3.10,9.8),(11.4,3.2,10.85)],
[(11.6,3.2,10.7),(10.9,2.8,9.9),(9.65,2.65,9.35),(8.6,2.9,8.2)],
[(13.85,2.95,6.8),(14.5,2.9,7.5),(14.8,3.3,8.1),(14.4,4.2,9.6)]]
for i,pts in enumerate(roots):
    tube('Root_Cavern_%02d'%i,pts,.13,cave,P['root'],radii=[.075+(.16-.075)*j/(len(pts)-1) for j in range(len(pts))],sides=8)
    tube('Root_Ridge_%02d'%i,[(x-.035,y-.1,z+.015) for x,y,z in pts],.023,cave,P['wood_lit'],sides=5)

scene['revision']='pixel-cavern-landscape-1'
OUT.mkdir(exist_ok=True,parents=True);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'pixel_cavern_coast.blend'))
print(json.dumps({'scene':SCENE,'revision':scene['revision'],'objects':len(scene.objects)}))
