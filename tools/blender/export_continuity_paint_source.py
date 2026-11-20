"""Export existing terrain UV registration for raster painting; read only."""
import bpy,numpy as np
from pathlib import Path
O=Path('D:/自己做着玩的/孤屿霜尘/artifacts/cape-forest-continuity-review')
triangles=[];uvs=[]
for name in ['WALK_Forest_Ground','WALK_Forest_NearSlope']:
    me=bpy.data.objects[name].data;me.calc_loop_triangles()
    for t in me.loop_triangles:
        p=me.polygons[t.polygon_index]
        if p.material_index!=0:continue
        co=[list(me.vertices[i].co) for i in t.vertices]
        if min(v[0] for v in co)>-49 or max(v[0] for v in co)<-64:continue
        triangles.append(co);uvs.append([list(me.uv_layers[0].data[li].uv) for li in t.loops])
np.savez_compressed(O/'forest_uv_source.npz',positions=np.asarray(triangles,dtype=np.float32),uv=np.asarray(uvs,dtype=np.float32))
print('Exported original UV registration triangles:',len(triangles))
