"""Second visual pass: replace regular cliff prisms and stair bars with bedding.
Runs inside Blender through MCP, exclusively on the new sample.
"""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-stone-steps-clarity-1'
ns={}
rockcol=bpy.data.collections['Fresh_02_Rock_Faces']
stone=bpy.data.materials['Fresh_Clean_Stone']
# Load only the helper definitions from this turn's NEW sample author.
source=(root/'tools/blender/refine_fresh_cape_stone_steps.py').read_text(encoding='utf-8')
exec(source[source.index('def mesh('):source.index('# The front has')],globals())
rockcol=bpy.data.collections['Fresh_02_Rock_Faces'];staircol=bpy.data.collections['Fresh_03_Stairway'];shore=bpy.data.collections['Fresh_06_Shore']
stone=bpy.data.materials['Fresh_Clean_Stone'];stone_lip=bpy.data.materials['Fresh_Clean_Stone_Lip'];stone_side=bpy.data.materials['Fresh_Clean_Stone_Side']
step=bpy.data.materials['Fresh_Weathered_Step'];step_alt=bpy.data.materials['Fresh_Weathered_Step_Alternate']
archive=bpy.data.collections.new('Archive_Fresh_Regular_Clarity_Pass')

def retire(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob['fresh_sample']=False

# Retain the fresh upper grass boundary and route. Discard the mechanical faces.
for ob in list(rockcol.objects):
    if ob.name.startswith(('Bedrock_','Bay_','West_Stone_Cleft','Middle_Stone_Cleft')):retire(ob)
for ob in list(staircol.objects):
    if 'Foundation' in ob.name or ob.name=='Turn_Landing_Base':retire(ob)

def rock(name,foot,z0,z1,lean=(0,0),tilt=(0,0),profile=.77):
    n=len(foot);cx=sum(p[0] for p in foot)/n;cy=sum(p[1] for p in foot)/n
    h=z1-z0;bottom=[];shoulder=[];crown=[]
    # Different footprint/lean at the foot and crown avoids an extruded column.
    for i,(x,y) in enumerate(foot):
        q=Vector((x-cx,y-cy));plane=tilt[0]*q.x+tilt[1]*q.y
        bottom.append((cx+q.x*1.07-lean[0]*.3,cy+q.y*1.09-lean[1]*.3,z0+plane*.3))
        shoulder.append((x+lean[0]*.64,y+lean[1]*.64,z0+h*profile+plane))
        crown.append((cx+q.x*.84+lean[0],cy+q.y*.85+lean[1],z1+plane))
    vs=bottom+shoulder+crown
    fs=[tuple(reversed(range(n))),tuple(range(n*2,n*3))]
    for ring in range(2):
        for i in range(n):fs.append((ring*n+i,ring*n+(i+1)%n,(ring+1)*n+(i+1)%n,(ring+1)*n+i))
    ob=mesh(name,vs,fs,rockcol,[stone,stone_lip],bevel=.014)
    return ob

# Major natural pieces; broad quiet faces interrupted by asymmetrical shoulders.
rock('Rock_West_Crown',[(-10.7,-2.20),(-10.8,-2.94),(-9.65,-3.48),(-7.9,-3.58),(-6.80,-3.13),(-6.92,-2.06)],.49,2.92,(.16,-.06),(-.08,.13),.78)
rock('Rock_West_Foot',[(-11,-2.78),(-11.1,-3.56),(-9.42,-3.94),(-8.05,-3.70),(-7.8,-2.93),(-9.1,-2.6)],-.64,.84,(.10,.13),(-.09,.14),.57)
rock('Rock_Mid_Lower',[(-8.12,-2.53),(-8.47,-3.63),(-7.15,-4.10),(-5.9,-3.90),(-4.88,-3.2),(-5.25,-2.27)],-.65,1.43,(.18,.22),(.07,.19),.64)
rock('Rock_Mid_Crown',[(-7.06,-2.10),(-7.16,-3.11),(-5.60,-3.49),(-4.28,-3.28),(-3.4,-2.65),(-4,-2.05)],1.29,2.95,(.09,-.11),(.065,.08),.67)
rock('Rock_Entry_Main',[(-4.26,-2.0),(-4.37,-3.02),(-3.57,-3.51),(-2.42,-3.29),(-1.60,-2.62),(-1.52,-1.72),(-2.8,-1.6)],-.63,2.79,(-.20,.09),(-.07,.14),.82)
rock('Rock_Entry_Foot',[(-4.22,-2.92),(-4.47,-3.62),(-3.18,-4.02),(-1.86,-3.52),(-1.26,-2.80),(-1.8,-2.48)],-.64,.81,(-.08,.08),(.09,.22),.55)
rock('Rock_End_Lower',[(3.55,-1.05),(4.80,-1.05),(5.79,-.13),(6.0,.95),(5.36,2.5),(4.4,2.8),(3.6,1.6)],-.6,1.63,(-.25,.10),(.04,.10),.68)
rock('Rock_End_Crown',[(3.39,-.81),(4.6,-.80),(5.25,-.12),(5.46,1.04),(4.98,2.3),(4.1,2.5),(3.5,1.5)],1.30,3.01,(-.23,.0),(.035,.03),.83)
rock('Rock_End_Foot',[(4.75,-.5),(5.85,-.65),(6.45,.05),(6.57,.85),(5.8,1.6),(4.9,1.1)],-.66,.56,(-.12,.1),(-.05,.1),.48)

# Face behind stairs: diagonal bedding, unequal ledges, no giant plain panel.
rock('Rock_Bay_Upper_Left',[(-1.20,-.78),(-1.0,-1.43),(.22,-1.58),(1.48,-1.22),(1.5,-.50),(-.8,-.45)],2.10,3.02,(.02,.03),(-.065,.03),.72)
rock('Rock_Bay_Upper_Right',[(1.40,-.65),(1.55,-1.23),(2.6,-1.35),(3.67,-.98),(3.7,-.4),(2.2,-.4)],1.95,2.99,(-.1,.06),(.05,.08),.69)
rock('Rock_Bay_Middle',[(.1,-.65),(.0,-1.42),(1.18,-1.65),(2.67,-1.42),(3.65,-1.01),(3.7,-.4)],.6,2.13,(-.08,.03),(.015,.11),.79)

# Continuous slope beneath each flight. Irregular outer break moves with the
# falling stair profile; a shallow segmented foot replaces upright fence bars.
def stairbed(name,start,direction,count,run,rise,width,height):
    d=Vector(direction).normalized();p=Vector((-d.y,d.x));s=Vector(start)
    vs=[]
    ts=[-.13,.21,.53,.77,1.03];out=[.08,.21,.14,.20,.06]
    for i,t in enumerate(ts):
        q=s+d*(t*count*run);z=height-t*count*rise-.19
        outer=q-p*(width*.5+out[i]);inner=q+p*(width*.49)
        toe=outer-p*(.19+(.12 if i%2 else 0))+d*.02
        vs.extend([(inner.x,inner.y,-.46),(toe.x,toe.y,-.46),(outer.x,outer.y,z),(inner.x,inner.y,z)])
    fs=[]
    for i in range(len(ts)-1):
        k=i*4;j=(i+1)*4
        fs.extend([(k,j,j+1,k+1),(k+1,j+1,j+2,k+2),(k+2,j+2,j+3,k+3),(k+3,j+3,j,k)])
    fs.extend([(3,2,1,0),(16,17,18,19)])
    ob=mesh(name,vs,fs,staircol,[stone_side,stone_lip],bevel=.015)
    return ob
start=Vector((-.6,-2));d=Vector((1,-.09)).normalized();end=start+d*2.75
stairbed('Upper_Flight_Embedded_Rockbed',start,d,5,.55,.245,1.6,3.08)
rock('Rock_Landing_Buttress',[(1.60,-2.4),(1.55,-3.13),(2.53,-3.59),(3.18,-3.21),(3.44,-2.68),(3.10,-1.65),(2.1,-1.5)],-.56,1.64,(-.02,.05),(.05,.12),.73)
start=end+Vector((.92,-.2));d=Vector((1,-.48)).normalized()
stairbed('Lower_Flight_Embedded_Rockbed',start,d,6,.56,.245,1.5,1.61)

# Lower perimeter partially embedded, ending before shore to keep the last tread legible.
rock('Rock_Lower_Bank',[(-1.8,-2.7),(-1.75,-3.25),(-.8,-3.70),(.65,-3.62),(1.55,-3.15),(1.3,-2.55),(-.5,-2.4)],-.57,.92,(.12,.1),(-.04,.16),.59)

# Treads are individually fitted stones: varied depth and chipped ends, restrained
# joint splits. Avoid regular broad illuminated strips on every front edge.
for ob in staircol.objects:
    if '_Tread_' not in ob.name:continue
    i=int(ob.name.split('_Tread_')[1][:2]);lower=ob.name.startswith('Lower')
    d=Vector((1,-.48 if lower else -.09,0)).normalized();p=Vector((-d.y,d.x,0))
    coords=[v.co for v in ob.data.vertices];center=sum(coords,Vector())/len(coords)
    for v in ob.data.vertices:
        q=v.co-center;u=q.dot(d);w=q.dot(p)
        # Each front has a slight lean and asymmetric breadth, preserving rise.
        if u>.12:v.co+=d*([.015,-.025,.038,-.018,.02,.0][i%6])
        v.co+=p*(u*[.04,-.06,.03,.07,-.035,.02][i%6])
    for poly in ob.data.polygons:poly.material_index=0

scene['revision']='fresh-cape-stone-steps-clarity-2'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'rock_objects':len(rockcol.objects),'stair_objects':len(staircol.objects)}))
