"""Deliberate stone planes and embedded stone stairs, executed by Blender MCP.

Only the new Fresh_Pixel_Cape sample is accessed. No older cape assets read.
"""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-reference-polish-6'
rockcol=bpy.data.collections['Fresh_02_Rock_Faces']
staircol=bpy.data.collections['Fresh_03_Stairway']
shore=bpy.data.collections['Fresh_06_Shore']
archive=bpy.data.collections.new('Archive_Fresh_Sculpt_And_Regular_Steps')

def retire(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob['fresh_sample']=False

for ob in list(rockcol.objects):
    if ob.type=='MESH':retire(ob)
for ob in list(staircol.objects):retire(ob)
for name in ['Lower_Stair_Rock_Apron','Landing_Outer_Buttress']:
    ob=bpy.data.objects.get(name)
    if ob and ob.name in scene.objects:retire(ob)

def material(name,hexcode):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    rgb=[int(hexcode[i:i+2],16)/255 for i in (0,2,4)]
    lin=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m.diffuse_color=(*lin,1)
    m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*lin,1)
    m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
    return m

stone=material('Fresh_Clean_Stone','949d90')
stone_lip=material('Fresh_Clean_Stone_Lip','a7ae9c')
stone_side=material('Fresh_Clean_Stone_Side','87968d')
step=material('Fresh_Weathered_Step','b2b49e')
step_alt=material('Fresh_Weathered_Step_Alternate','a8af9c')
seam=material('Fresh_Stone_Recess','63796f')
moss=material('Fresh_Stone_Edge_Moss','758553')

def mesh(name,verts,faces,coll,mats,indices=None,bevel=0):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);coll.objects.link(ob)
    for mat in mats:me.materials.append(mat)
    if indices:
        for p,i in zip(me.polygons,indices):p.material_index=i
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        axes=(0,1) if abs(p.normal.z)>.55 else (0,2) if abs(p.normal.y)>.5 else (1,2)
        for li in p.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]]*.2,q[axes[1]]*.2)
    ob['fresh_sample']=True;ob['authored_from']='fresh sample; deliberate fracture planes and fitted masonry via Blender MCP'
    if bevel:
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('Selective worn arris','BEVEL');mod.width=bevel;mod.segments=1;mod.affect='EDGES';mod.limit_method='ANGLE';mod.angle_limit=.65
        mod.profile=.5;mod.material=1 if len(mats)>1 else 0
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def block(name,foot,z0,z1,lean=(0,0),slope=(0,0),coll=rockcol,mat=stone,lip=.028):
    # Broad polygon cap, near-vertical fracture walls, narrow eroded arris.
    n=len(foot);cx=sum(p[0] for p in foot)/n;cy=sum(p[1] for p in foot)/n
    vs=[(x,y,z0+slope[0]*(x-cx)*.2) for x,y in foot]
    vs += [(x+lean[0],y+lean[1],z1+slope[0]*(x-cx)+slope[1]*(y-cy)) for x,y in foot]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,coll,[mat,stone_lip],[0]*(n+2),lip)

# The front has two major beds with staggered joints and connected lower toes.
# Individual planes are quiet; changes in depth and inclination provide relief.
block('Bedrock_West_Main',[(-10.8,-2.55),(-10.65,-3.25),(-9.5,-3.62),(-7.35,-3.58),(-6.75,-3.19),(-6.9,-2.45)],.65,2.86,(.10,.04),(-.075,.06),lip=.055)
block('Bedrock_West_Foot',[(-10.9,-2.8),(-11,-3.6),(-9.4,-3.85),(-8.15,-3.77),(-7.7,-3.15),(-8,-2.5)],-.66,.89,(.12,-.04),(-.08,.16),lip=.06)
block('Bedrock_Middle_Lower',[(-8.2,-2.65),(-8.35,-3.82),(-6.9,-4.01),(-5.35,-3.78),(-4.8,-3.15),(-5.15,-2.5)],-.67,1.44,(-.03,.13),(.07,.14),lip=.052)
block('Bedrock_Middle_Upper',[(-7.1,-2.4),(-7.15,-3.28),(-5.55,-3.59),(-4.1,-3.34),(-3.45,-2.83),(-4.0,-2.3)],1.33,2.90,(.10,-.04),(.035,.12),lip=.055)
block('Bedrock_Entry_Pier',[(-4.2,-2.3),(-4.35,-3.18),(-3.48,-3.48),(-2.5,-3.28),(-1.64,-2.78),(-1.55,-1.95),(-2.7,-1.85)],-.62,2.68,(-.13,.10),(.045,.13),lip=.064)
block('Bedrock_Entry_Toe',[(-4.1,-3.01),(-4.35,-3.72),(-3.08,-3.93),(-1.84,-3.58),(-1.24,-2.84),(-1.65,-2.5)],-.63,.76,(-.1,.03),(.04,.15),lip=.048)
block('Bedrock_End_Lower',[(3.5,-1),(4.85,-.95),(5.67,-.1),(5.95,1),(5.35,2.5),(4.4,2.8),(3.6,1.6)],-.6,1.46,(-.15,.02),(.03,.10),lip=.05)
block('Bedrock_End_Crown',[(3.4,-.83),(4.55,-.87),(5.20,-.2),(5.4,1.05),(4.98,2.30),(4.1,2.5),(3.5,1.5)],1.32,3.02,(-.12,.03),(.04,.03),lip=.045)
block('Bedrock_End_Foot',[(4.75,-.5),(5.85,-.65),(6.45,.05),(6.57,.85),(5.8,1.6),(4.9,1.1)],-.66,.58,(-.12,.04),(-.03,.1),lip=.04)

# Calm exposed slabs merge into the turf, instead of random faceted humps.
block('Rock_Terrace_Slab',[(1.8,1.35),(3.1,1.12),(3.85,1.65),(3.6,2.6),(2.45,2.75),(1.65,2.1)],2.93,3.35,(-.08,.05),(.035,.035),lip=.035)
block('Rock_Bamboo_Buried',[(-6.3,2.25),(-4.85,1.8),(-3.65,2.25),(-3.85,3.15),(-5.65,3.5)],2.9,3.63,(-.04,.06),(.045,.055),lip=.04)

# Stair-bay walls have horizontal fractures of different lengths and setbacks.
# Front faces sit behind the tread corridor, so they enclose rather than cover it.
block('Bay_Upper_Bed',[(-1.2,-1.37),(.26,-1.5),(1.55,-1.15),(1.65,-.67),(-1.2,-.7)],2.25,2.98,(-.03,.02),(-.04,.03),lip=.03)
block('Bay_Upper_End',[(1.50,-1.17),(2.54,-1.23),(3.65,-.98),(3.7,-.4),(1.6,-.6)],2.21,2.99,(-.03,.03),(.02,.04),lip=.035)
block('Bay_Middle_Bed',[(-.45,-1.45),(1.13,-1.55),(2.67,-1.38),(3.65,-1.05),(3.7,-.4),(-.4,-.6)],1.38,2.24,(.03,.02),(-.025,.025),lip=.035)
block('Bay_Lower_Bed',[(.9,-1.55),(2.0,-1.8),(3.55,-1.46),(4.2,-.7),(3.7,-.3),(1,-.6)],-.5,1.48,(.03,.07),(.03,.06),lip=.04)

def tread(name,start,direction,width,run,top,index,split=False,coll=staircol):
    d=Vector(direction).normalized();p=Vector((-d.y,d.x));s=Vector(start)
    # Receding/back ends stay buried. Only exposed corners are selectively chipped.
    widths=[1.00,.97,1.04,.99,1.02,1.00]
    w=width*widths[index%6]
    skew=[.00,.025,-.035,.04,-.018,.015][index%6]
    bounds=[(-w*.5,w*.5)] if not split else [(-w*.5,w*.12-.012),(w*.12+.012,w*.5)]
    for j,(a,b) in enumerate(bounds):
        # Polygon around a substantial stone slab, not a thin rectangular stair decal.
        coords=[(-.04,a+.05),(-.025,b-.04),(.10,b+.005),(run-.09,b+skew),(run+.018,b-.07),(run+.025,a+.075),(run-.075,a-.008),(.08,a-.016)]
        poly=[tuple(s+d*u+p*v) for u,v in coords]
        ob=block(name+('_Part_%d'%j if split else ''),poly,top-.31-(index%2)*.018,top,(0,0),tuple(-d*.022),coll,step if index%3!=1 else step_alt,.018)
        ob['stair_top']=top;ob['stair_run']=run;ob['structural_thickness']=.31
    return s+d*run

def support(name,start,direction,count,run,rise,width,top):
    d=Vector(direction).normalized();p=Vector((-d.y,d.x));s=Vector(start)
    # Individually fitted foundation stones. Each descending joint is offset
    # from the tread above; the visible outer side reads as weight-bearing rock.
    for i in range(count):
        a=s+d*(i*run-.07);b=s+d*((i+1)*run+.035)
        half=width*.465
        poly=[tuple(a-p*half),tuple(b-p*(half+.015)),tuple(b+p*half),tuple(a+p*half)]
        z=top-i*rise-.25
        block(name+'_Foot_%02d'%i,poly,-.48,z,(0,0),(.0,.0),staircol,stone_side,.025)

block('Upper_Entry_Landing',[(-1.72,-2.7),(-.55,-2.68),(-.40,-1.30),(-1.52,-1.15)],2.76,3.12,(0,0),(.015,.01),staircol,step,.025)
start=Vector((-.6,-2.0));d=Vector((1,-.09)).normalized();run=.55
support('Upper_Stone_Foundation',start,d,5,run,.245,1.6,3.08)
for i in range(5):tread('Upper_Flight_Tread_%02d'%i,start+d*(i*run),d,1.64,run,3.08-i*.245,i,split=i in [1,4])
end=start+d*(5*run)
landing=[(end.x-.12,end.y-.88),(end.x+.90,end.y-.96),(end.x+1.15,end.y-.65),(end.x+1.12,end.y+.52),(end.x+.03,end.y+.74)]
block('Turn_Landing_Stone',landing,1.52,1.855,(0,0),(.008,.008),staircol,step,.025)
block('Turn_Landing_Base',[(1.7,-3.12),(2.73,-3.4),(3.38,-2.85),(3.13,-1.68),(2.05,-1.5)],-.54,1.56,(.02,.02),(.015,.01),staircol,stone,.038)
start=end+Vector((.92,-.20));d=Vector((1,-.48)).normalized();run=.56
support('Lower_Stone_Foundation',start,d,6,run,.245,1.50,1.61)
for i in range(6):tread('Lower_Flight_Tread_%02d'%i,start+d*(i*run),d,1.56,run,1.61-i*.245,i+2,split=i in [0,3])

# A broad partly buried apron receives the last step. Three shallow stones
# continue its direction; the shore remains visible around them.
block('Stair_Foot_Apron',[(5.15,-4.05),(6.0,-4.82),(7.05,-4.66),(7.43,-3.99),(6.97,-3.38),(5.73,-3.45)],-.53,.17,(0,0),(-.015,.035),shore,stone,.03)
block('Shore_Flagstone_A',[(6.23,-4.62),(6.93,-4.77),(7.22,-4.48),(7.08,-4.04),(6.38,-4.02)],.105,.155,(0,0),(0,0),shore,step_alt,.009)
block('Shore_Flagstone_B',[(7.18,-4.54),(7.66,-4.49),(7.85,-4.11),(7.31,-3.85),(7.13,-4.07)],.105,.146,(0,0),(0,0),shore,step_alt,.009)

# Restrained seams on two major planes, and moss only at damp/recessed ledges.
def strip(name,points,width,mat):
    vs=[]
    for x,y,z in points:vs.extend([(x,y,z-width*.5),(x,y,z+width*.5)])
    return mesh(name,vs,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(len(points)-1)],rockcol,[mat])
strip('West_Stone_Cleft',[(-10.02,-3.573,1.41),(-9.65,-3.618,1.46),(-9.22,-3.620,1.43)],.018,seam)
strip('Middle_Stone_Cleft',[(-6.58,-3.430,2.16),(-6.14,-3.512,2.12),(-5.82,-3.565,2.13)],.017,seam)

scene['revision']='fresh-cape-stone-steps-clarity-1'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'authored_rock_objects':len(rockcol.objects),'stair_objects':len(staircol.objects),'archived_new_sample_objects':len(archive.objects)}))
