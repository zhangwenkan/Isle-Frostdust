"""Read terrain/UV/material joins after user feedback; no modeling changes."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/reference-cape-review'
names=['WALK_Forest_Ground','WALK_Forest_NearSlope','WALK_Cape_Neck','Cape_Connection_Shoulder']
report={'materials':{},'surface_samples':[],'new_neck_shader_uv_formula':'((author_x+50)/54, (author_y+4)/40)','sampler':'forest_ground repeat_disable'}
trees=[]
for name in names:
    ob=bpy.data.objects[name];paths=[]
    for mat in ob.data.materials:
        paths.append({'material':mat.name,'images':[bpy.path.abspath(n.image.filepath) for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if mat.use_nodes else []})
    report['materials'][name]=paths
    trees.append((name,BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])))
for x in [-59.8,-60.9,-61.4,-62,-63.04,-64,-65.5,-67,-68.8]:
    y=13.7-1.5*max(0,min(1,(-x-60.9)/8.45))
    for name,t in trees:
        h=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
        if h:report['surface_samples'].append({'x':x,'y':y,'mesh':name,'z':h.z,'current_new_shader_u':(x+50)/54})
(OUT/'transition-diagnosis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
