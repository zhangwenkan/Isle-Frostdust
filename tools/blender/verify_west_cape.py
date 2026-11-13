"""Check playable cape support and preserved roots in the actual Blender scene."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/west-cape-opening-review'
scene=bpy.data.scenes['Island_Refined']
ob=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
def h(x,z):return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.10+max(0,-z-.3)*.23
samples=[]
for i in range(89):
    x=-20.7+i*.1
    for offset in [-.55,0,.55]:
        z=.4+math.sin(x*.25)*.44+offset
        hit=tree.ray_cast(Vector((x,-z,30)),Vector((0,0,-1)))[0]
        assert hit is not None,('Missing walking ground',x,z)
        samples.append({'x':x,'offset':offset,'gap_m':h(x,z)+.04-hit.z})
worst=max(samples,key=lambda s:abs(s['gap_m']-.04))
assert abs(worst['gap_m']-.04)<.08,worst
roots=[]
for name in ['Coast_Low_Grass_00.003','Coast_Low_Grass_01.003','Coast_Low_Grass_02.003']:
    grass=scene.objects[name];pts=[grass.matrix_world@v.co for v in grass.data.vertices]
    bottom=min(p.z for p in pts);base=[p for p in pts if p.z<bottom+.04]
    p=sum(base,Vector())/len(base);hit=tree.ray_cast(Vector((p.x,p.y,30)),Vector((0,0,-1)))[0]
    roots.append({'object':name,'gap_m':None if hit is None else p.z-hit.z})
    assert hit is not None and p.z-hit.z<.12,roots[-1]
rock=scene.objects['InkSample_Rock_00'];base=bpy.data.objects['CapeBaseline_InkSample_Rock_00']
assert [tuple(v.co) for v in rock.data.vertices]==[tuple(v.co) for v in base.data.vertices]
assert [[tuple(d.uv) for d in l.data] for l in rock.data.uv_layers]==[[tuple(d.uv) for d in l.data] for l in base.data.uv_layers]
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
report={'walk_samples':len(samples),'worst_walk_support':worst,'grass_roots':roots,'western_rock_shape_and_uv_preserved':True,
        'active_meshes':len(active),'retired_bamboo_exported':any(o.name in ['Depth_Bamboo_Main_00','Depth_Bamboo_Main_01'] for o in active)}
assert not report['retired_bamboo_exported']
(OUT/'contact-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
