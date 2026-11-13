"""Read-only verification inside Blender; no scene mutation."""
import bpy,json,math
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-integration-review';s=bpy.data.scenes['Island_Refined']
land=s.objects['Fish_West_Continuous_Land'];base=s.objects['IntegrationBaseline_Land'];protected=0;changed=0
for i in range(2626):
    a=base.data.vertices[i].co;b=land.data.vertices[i].co
    safe=abs(a.y+.25)<=1.05 or math.hypot(a.x+27.35,a.y-2.15)<=1.35
    if safe:assert (a-b).length==0;protected+=1
    if (a-b).length>0:changed+=1
assert len(land.data.polygons)==len(base.data.polygons)
assert all(tuple(a.uv)==tuple(b.uv) for a,b in zip(land.data.uv_layers[0].data,base.data.uv_layers[0].data))
shell=s.objects['Integrated_Coast_Surface'];boundary=[i*26 for i in range(101)]+[2600+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
top=[v.co for v in shell.data.vertices if v.index%12==0]
maxgap=max(min((land.data.vertices[i].co-p).length for p in top) for i in boundary)
assert maxgap<1e-5,maxgap
active=[o.name for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
assert not any(n.startswith(('Original_Coast_Rock_','WS_Reference_Shore_','Cliff_Fern_')) for n in active)
report={'protected_lane_and_fire_vertices':protected,'protected_positions_exact':True,'ground_topology_uv0_exact':True,'outer_ground_vertices_changed':changed,'coast_to_turf_max_gap_m':maxgap,'archived_original_modules_excluded':True,'hanging_ferns_absent':True}
(O/'blender-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('INTEGRATION_VERIFIED',json.dumps(report))
