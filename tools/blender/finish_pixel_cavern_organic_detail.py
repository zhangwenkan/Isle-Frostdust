"""Finish contact detail, curved roots and foreground depth. Blender MCP only."""
import bpy
from pathlib import Path
exec((Path('D:/自己做着玩的/孤屿霜尘/tools/blender/pixel_cavern_lib.py')).read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-composition-4'
P=palette();cave=collection('05_Cavern');green=collection('08_Undergrowth');cliff=collection('02_Cliffs')

# Rebuild only the new roots' center lines with a smooth spatial interpolation.
def catmull(points,subdiv=7):
    output=[]
    for i in range(len(points)-1):
        p0=points[max(0,i-1)];p1=points[i];p2=points[i+1];p3=points[min(len(points)-1,i+2)]
        for j in range(subdiv):
            t=j/subdiv
            output.append((p1*2+(p2-p0)*t+(p0*2-p1*5+p2*4-p3)*t*t+(-p0+p1*3-p2*3+p3)*t*t*t)*.5)
    return output+[points[-1]]
archive=bpy.data.collections.new('PCC_Archive_Angular_Roots')
for ob in list(scene.objects):
    if not ob.name.startswith(('Root_Cavern_','Root_Ridge_')):continue
    sides=8 if ob.name.startswith('Root_Cavern') else 5
    pts=[];radii=[]
    for i in range(len(ob.data.vertices)//sides):
        verts=[ob.data.vertices[i*sides+j].co.copy() for j in range(sides)];c=sum(verts,Vector())/sides;pts.append(c);radii.append(sum((v-c).length for v in verts)/sides)
    name=ob.name;ob.name=name+'_angular'
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob['pixel_cavern']=False
    smooth=catmull(pts);rr=[]
    for i in range(len(smooth)):
        t=i/(len(smooth)-1)*(len(radii)-1);j=min(len(radii)-2,int(t));rr.append(radii[j]*(1-(t-j))+radii[j+1]*(t-j))
    tube(name,smooth,.1,cave,P['root'] if sides==8 else P['wood'],radii=rr,sides=sides)

# Several compact irregular shrub masses grow on the platform edges, not in the
# path center. Each is a cluster of overlapping leaf fans with shared light.
specs=[(-10.2,-3.7,4.48,1.0),(-5.3,-2.15,4.49,.85),(-4,-2.4,4.49,.8),(-12.4,3.7,4.48,1.1),(-9.4,5.5,4.5,.8),(-8.9,-7,.28,.72),(-4.9,-6.8,.3,.65),(7,-1.5,4.48,1.0),(9.4,-2.0,4.49,1.0),(13.8,-1.9,4.49,1.1),(15.6,.6,4.5,.9),(7.7,2.1,4.55,.8)]
for i,(x,y,z,s) in enumerate(specs):
    for j in range(8):
        a=j*2.4+i;origin=Vector((x+math.cos(a)*s*.24,y+math.sin(a)*s*.24,z+.15+(j%3)*.11))
        leaf_group('Plant_Edge_Shrub_%02d_%d'%(i,j),origin,a,s,green,[P['fern'],P['leaf']],7000+i*11+j,fullness=10)

# The near right shore continues down beyond the frame, matching the enclosing
# cliff in the image instead of a freestanding little rock in open water.
rock('Rock_Foreground_Continuation',(15.0,-10.0,-1.4),(4.1,3.4,3.7),cliff,[P['stone_shadow'],P['stone_moss']],8031,-.2)
rock('Rock_Foreground_Crown',(14.2,-9.5,1.3),(2.6,2.4,1.1),cliff,[P['stone'],P['stone_moss']],8035,.25)
for j in range(15):
    a=j*2.399;leaf_group('Plant_Foreground_%02d'%j,(13.8+math.cos(a)*1.5,-9.6+math.sin(a)*1.3,2.1),a,1.3,green,[P['leaf_dark'],P['fern']],8200+j,fullness=12)

# A small amount of hanging greenery connects the cliff face to the turf.
for i,(x,y,z,l) in enumerate([(-4.3,-4.2,3.9,1.7),(-11.0,-5.3,4.0,1.4),(8.5,-3.9,4.05,2.0),(14.8,-3.9,3.95,2.5)]):
    pts=[(x+.10*math.sin(t*6+i),y-.03*t,z-l*t) for t in [j/8 for j in range(9)]]
    tube('Root_Cliff_Creeper_%d'%i,pts,.018,green,P['root'],sides=5)
    for j in range(8):leaf_group('Plant_Cliff_Creeper_%d_%d'%(i,j),pts[j],-1.2+(j%2)*2.2,.44,green,[P['fern'],P['leaf']],8500+i*10+j,fullness=5)

scene['revision']='pixel-cavern-organic-detail-5';export_scene(scene['revision'])
