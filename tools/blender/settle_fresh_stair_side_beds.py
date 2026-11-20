"""Resolve stair flank into fitted rock masses instead of a straight wall."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-stone-steps-clarity-3'
rockcol=bpy.data.collections['Fresh_02_Rock_Faces'];staircol=bpy.data.collections['Fresh_03_Stairway']
stone=bpy.data.materials['Fresh_Clean_Stone'];stone_lip=bpy.data.materials['Fresh_Clean_Stone_Lip']
source=(root/'tools/blender/refine_fresh_cape_stone_steps.py').read_text(encoding='utf-8')
exec(source[source.index('def mesh('):source.index('# The front has')],globals())
archive=bpy.data.collections.new('Archive_Fresh_Straight_Stair_Beds')
for ob in list(rockcol.objects):
    if ob.name.startswith('Stair_Bed_'):
        rockcol.objects.unlink(ob);archive.objects.link(ob);ob['fresh_sample']=False

# Narrow the concealed load-bearing core; the authored stair slabs remain intact.
for ob in staircol.objects:
    if 'Embedded_Rockbed' not in ob.name:continue
    lower=ob.name.startswith('Lower');d=Vector((1,-.48 if lower else -.09,0)).normalized();p=Vector((-d.y,d.x,0))
    s=Vector((3.059,-2.446,0)) if lower else Vector((-.6,-2,0))
    for v in ob.data.vertices:
        dist=(v.co-s).dot(p)
        if dist<0:v.co-=p*dist*.50

def mass(name,start,direction,length,width,top,rise,low):
    d=Vector(direction).normalized();p=Vector((-d.y,d.x));s=Vector(start)
    # Ends lean in different directions; top descends under the stone treads.
    pts=[(-.14,-width*.42),(.06,-width*.61),(length*.69,-width*.55),(length+.1,-width*.28),(length-.06,width*.44),(.0,width*.48)]
    poly=[s+d*u+p*v for u,v in pts];n=len(poly)
    vs=[(q.x,q.y,low) for q in poly]
    for (u,v),q in zip(pts,poly):
        q=q+p*.035+d*.04
        vs.append((q.x,q.y,top-rise*u))
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=mesh(name,vs,fs,rockcol,[stone,stone_lip],bevel=.016)
    return ob

d=Vector((1,-.09)).normalized();s=Vector((-.6,-2))
mass('Stair_Rock_Upper_Load',s+Vector((0,-.20)),d,1.12,1.65,2.78,.38,.98)
mass('Stair_Rock_Upper_End',s+d*1.05+Vector((0,-.18)),d,1.72,1.62,2.32,.39,.63)
mass('Stair_Rock_Upper_Foot',(-.82,-2.67),d,2.63,1.31,1.10,.17,-.54)
d=Vector((1,-.48)).normalized();s=Vector((3.059,-2.446))
mass('Stair_Rock_Lower_Load',s+Vector((0,-.12)),d,1.18,1.61,1.32,.35,-.44)
mass('Stair_Rock_Lower_End',s+d*1.10+Vector((0,-.11)),d,1.94,1.56,.82,.32,-.44)

# A few small joints and moss wedges lie on real stone surfaces, clustered only
# at ground-facing contacts; the broad lit planes are left quiet.
seam=bpy.data.materials['Fresh_Stone_Recess'];moss=bpy.data.materials['Fresh_Stone_Edge_Moss']
def surface_mark(obname,name,xzs,width,mat):
    ob=bpy.data.objects[obname];vs=[]
    for x,z in xzs:
        for dz in [-width*.5,width*.5]:
            hit,q,no,idx=ob.ray_cast(Vector((x,-12,z+dz)),Vector((0,1,0)))
            if not hit:return
            vs.append(tuple(q+no*.006))
    mesh(name,vs,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(len(xzs)-1)],rockcol,[mat])
surface_mark('Rock_West_Crown','Stone_Split_West',[(-9.95,1.50),(-9.62,1.47),(-9.24,1.50)],.018,seam)
surface_mark('Rock_Entry_Main','Stone_Split_Entry',[(-3.58,1.65),(-3.30,1.62),(-2.95,1.68)],.018,seam)
surface_mark('Rock_End_Crown','Stone_Split_End',[(4.27,2.35),(4.54,2.30),(4.81,2.32)],.016,seam)
surface_mark('Rock_Mid_Lower','Stone_Moss_Mid',[(-7.35,.94),(-7.16,.92),(-6.83,.94)],.045,moss)
scene['revision']='fresh-cape-stone-steps-clarity-4'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision']}))
