"""Blender MCP: place each complete swim ellipse clear of the actual reefs."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
dg=bpy.context.evaluated_depsgraph_get()
obstacles=[]
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if ob.name=='Fish_Seabed' or any(s in ob.name for s in ['Rock','Reef','Crag','Continuous_Land']):
        corners=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        bounds=[min(p.x for p in corners),max(p.x for p in corners),min(p.y for p in corners),max(p.y for p in corners)]
        obstacles.append((ob,BVHTree.FromObject(ob,dg),ob.matrix_world.inverted(),bounds))
def floor_at(x,y):
    top=-20.0
    for ob,tree,inv,b in obstacles:
        if x<b[0] or x>b[1] or y<b[2] or y>b[3]:continue
        hit=tree.ray_cast(inv@Vector((x,y,10)),(inv.to_3x3()@Vector((0,0,-1))).normalized())[0]
        if hit is not None:top=max(top,(ob.matrix_world@hit).z)
    return top
def route_floor(x,z):
    top=-20.0
    for k in range(48):
        t=math.tau*k/48
        for a in range(8):
            x1=x+math.sin(t)*.70+math.cos(a*math.tau/8)*.29
            z1=z+math.cos(t)*.42+math.sin(a*math.tau/8)*.29
            top=max(top,floor_at(x1,-z1))
    return top
selected=[]
originals=[(6.4,1.6,-2.92),(8.4,1.42,-3.68),(11.0,-1.72,-3.42),(13.0,.55,-2.8)]
for i,(ox,oz,oy) in enumerate(originals):
    candidates=[]
    for ix in range(19):
        x=4.5+ix*.5
        for iz in range(15):
            z=-3.0+iz*.5
            if any(math.hypot(x-s['x'],z-s['z'])<1.8 for s in selected):continue
            score=(x-ox)**2+(z-oz)**2
            candidates.append((score,x,z))
    for score,x,z in sorted(candidates):
        floor=route_floor(x,z)
        # Keep the body submerged and leave room for the entire vertical bob.
        y=max(oy,floor+.36)
        if y> -2.80:continue
        selected.append({'fish':i,'x':x,'y':y,'z':z,'route_floor':floor})
        scene.objects['Fish_Underwater_Swimmer_%02d'%i].location=Vector((x,-z,y))
        break
    else:raise RuntimeError('No clear route for fish '+str(i))
(ROOT/'artifacts/cinematic-coast-review/swim-placement.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
print('SAFE_SWIM_ROUTES',json.dumps(selected))
