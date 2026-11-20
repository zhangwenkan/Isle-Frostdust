"""Restrained authored seams and turf contact; Blender MCP only."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-stone-steps-clarity-4'
rockcol=bpy.data.collections['Fresh_02_Rock_Faces'];staircol=bpy.data.collections['Fresh_03_Stairway']
stone=bpy.data.materials['Fresh_Clean_Stone'];stone_lip=bpy.data.materials['Fresh_Clean_Stone_Lip']
source=(root/'tools/blender/refine_fresh_cape_stone_steps.py').read_text(encoding='utf-8')
exec(source[source.index('def mesh('):source.index('# The front has')],globals())
seam=bpy.data.materials['Fresh_Stone_Recess'];moss=bpy.data.materials['Fresh_Stone_Edge_Moss']
for name in ['Landing_Stone_Joint','Entry_Stone_Joint']:
    prior=scene.objects.get(name)
    if prior:bpy.data.objects.remove(prior,do_unlink=True)
def current_mesh(name):
    return next(o for o in scene.objects if o.name==name or o.name.startswith(name+'.'))

def top_line(name,ob,xy,width,material):
    vs=[]
    for i,(x,y) in enumerate(xy):
        prev=Vector(xy[max(0,i-1)]);nxt=Vector(xy[min(len(xy)-1,i+1)]);d=(nxt-prev).normalized();p=Vector((-d.y,d.x))
        for sign in [-1,1]:
            q=Vector((x,y))+p*width*.5*sign
            hit,pos,n,idx=ob.ray_cast(Vector((q.x,q.y,10)),Vector((0,0,-1)))
            if not hit:return
            vs.append(tuple(pos+Vector((0,0,.004))))
    mesh(name,vs,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(len(xy)-1)],staircol,[material])

land=current_mesh('Turn_Landing_Stone')
top_line('Landing_Stone_Joint',land,[(2.17,-2.40),(2.55,-2.45),(2.72,-2.52),(3.08,-2.58)],.021,seam)
entry=current_mesh('Upper_Entry_Landing')
top_line('Entry_Stone_Joint',entry,[(-1.36,-2.46),(-1.25,-2.05),(-1.31,-1.67)],.018,seam)
# Small pockets of ground cover on landing edges. None fills the tread center.
for i,(obname,poly) in enumerate([
    ('Upper_Entry_Landing',[(-1.61,-1.40),(-1.49,-1.31),(-1.22,-1.38),(-1.34,-1.46)]),
    ('Turn_Landing_Stone',[(2.12,-1.66),(2.25,-1.70),(2.42,-1.74),(2.30,-1.83),(2.12,-1.75)]),
    ('Rock_Bay_Upper_Right',[(2.38,-.56),(2.61,-.62),(2.85,-.61),(2.76,-.78),(2.50,-.73)])
]):
    ob=current_mesh(obname);vs=[]
    for x,y in poly:
        hit,q,n,j=ob.ray_cast(Vector((x,y,10)),Vector((0,0,-1)))
        if not hit:break
        vs.append(tuple(q+Vector((0,0,.005))))
    if len(vs)==len(poly):mesh('Grass_Stair_Contact_%02d'%i,vs,[tuple(range(len(vs)))],staircol,[moss])

scene['revision']='fresh-cape-stone-steps-clarity-5'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision']}))
