"""Read-only Blender audit: roots, corridor visibility and unchanged authored route."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];deps=bpy.context.evaluated_depsgraph_get()
def G(p):return Vector((p[0],-p[2],p[1]))
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
lands=[tree(scene.objects[n]) for n in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']]
foreground=[(ob.name,tree(ob)) for ob in scene.objects if ob.name.startswith(('Depth_Foreground','Depth_Bamboo_Fore'))]
def height(x,z):
    if x>10:return 1.15+math.sin(x*.37)*.18+max(0,-z)*.16
    return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.1+max(0,-z-.3)*.23
def bridge(x):
    f=max(0,min(1,(x-4.2)/10.3));return (1-f)*height(4.2,.25)+f*height(14.5,.25)-math.sin(f*math.pi)*.48+.08
rows=[];contacts=[]
for i in range(161):
    x=-18+i*(41.7/160);z=.25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
    y=(bridge(x) if 4.2<x<14.5 else height(x,z))+.04
    camera=G((min(22,max(-17.4,x+1.2)),y+4.1,z+13.2))
    hits={}
    for label,up in [('feet',.1),('torso',.85),('head',1.65)]:
        target=G((x,y+up,z));ray=target-camera;length=ray.length;ray.normalize()
        hitnames=[]
        for name,bvh in foreground:
            q,n,idx,d=bvh.ray_cast(camera,ray,length)
            if q is not None:hitnames.append(name)
        hits[label]=hitnames
    rows.append({'x':x,**hits})
for ob in scene.objects:
    if ob.name.startswith('Depth_Bamboo_Main'):
        for x,y,z in json.loads(ob['root_positions_godot']):
            values=[b.ray_cast(G((x,40,z)),Vector((0,0,-1)))[0] for b in lands]
            actual=max((p.z for p in values if p is not None),default=None)
            contacts.append(None if actual is None else y-actual)
report={'samples':len(rows),'occluded_samples':{s:sum(bool(row[s]) for row in rows) for s in ['feet','torso','head']},
    'occlusions':[r for r in rows if any(r[k] for k in ['feet','torso','head'])],
    'main_bamboo_roots':len(contacts),'missing_ground':sum(c is None for c in contacts),
    'maximum_root_clearance':max(c for c in contacts if c is not None)}
(ROOT/'artifacts/depth-composition-review/contact-visibility-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DEPTH_CONTACT_VISIBILITY_AUDIT',json.dumps({k:v for k,v in report.items() if k!='occlusions'}))
