import bpy,bmesh,json
from pathlib import Path
s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];o=s.objects['Recovery_WALK_Forest_Ground'];bm=bmesh.new();bm.from_mesh(o.data);es=[e for e in bm.edges if e.is_boundary and e.verts[0].co.x<-53 and e.verts[1].co.x<-53]
print('BOUNDARY',len(es));print([[list(v.co) for v in e.verts] for e in es][:45]);print('mats',[(i,m.name) for i,m in enumerate(o.data.materials)]);bm.free()
