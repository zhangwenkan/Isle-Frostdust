"""Read-only Blender MCP check of the actual animated swim volumes."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined']
dg=bpy.context.evaluated_depsgraph_get()
obstacles=[]
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection): continue
    if ob.name=='Fish_Seabed' or any(s in ob.name for s in ['Rock','Reef','Crag','Continuous_Land']):
        obstacles.append((ob,BVHTree.FromObject(ob,dg),ob.matrix_world.inverted()))
records=[]
for i in range(4):
    ob=scene.objects['Fish_Underwater_Swimmer_%02d'%i]
    origin=ob.matrix_world.translation
    minimum=100.; at=None
    for k in range(241):
        seconds=math.tau/.31*k/240
        t=seconds*.31+i*1.9
        # Test the lowest possible bob on the whole ellipse, covering all phase cycles.
        center=origin+Vector((math.sin(t)*.70,-math.cos(t)*.42,-.065))
        # Cover the whole body/tail footprint independent of its changing yaw.
        for a in range(9):
            p=center+Vector((math.cos(a*math.tau/8)*.28,math.sin(a*math.tau/8)*.28,0)) if a<8 else center
            for obstacle,tree,inverse in obstacles:
                start=inverse@Vector((p.x,p.y,10))
                direction=(inverse.to_3x3()@Vector((0,0,-1))).normalized()
                hit=tree.ray_cast(start,direction)[0]
                if hit is None: continue
                floor=(obstacle.matrix_world@hit).z
                clearance=p.z-.10-floor
                if clearance<minimum:minimum=clearance;at={'seconds':seconds,'obstacle':obstacle.name}
    records.append({'fish':ob.name,'minimum_floor_clearance_m':minimum,'worst_sample':at,'minimum_surface_clearance_m':-2.1-(origin.z+.065+.10)})
report={'path_period_seconds':math.tau/.31,'samples_per_fish':241,'footprint_radius_m':.28,'obstacles':[o[0].name for o in obstacles],'fish':records}
(ROOT/'artifacts/cinematic-coast-review/swim-clearance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(records,indent=2))
