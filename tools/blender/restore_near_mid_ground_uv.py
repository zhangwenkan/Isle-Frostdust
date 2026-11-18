"""Blender MCP: project the archived original ground UV onto refined topology."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
REVIEW=ROOT/'artifacts/near-mid-depth-review'
record=LAYOUT['forest_extension']['near_mid_depth'];assert not record.get('uv_restore'),'Inspect saved UV restoration before repeating.'
old=SCENE.objects['NearMid_Before_WALK_Forest_Ground'].data
new=SCENE.objects['WALK_Forest_Ground'].data
tree=BVHTree.FromPolygons([v.co for v in old.vertices],[list(p.vertices) for p in old.polygons])
uvs=old.uv_layers[0];cache={};fallback=0
for vertex in new.vertices:
    co=vertex.co
    hit,normal,index,distance=tree.ray_cast(Vector((co.x,co.y,40)),Vector((0,0,-1)))
    if index is None:
        hit,normal,index,distance=tree.find_nearest(co);fallback+=1
    face=old.polygons[index];assert len(face.vertices)==3
    points=[Vector((old.vertices[i].co.x,old.vertices[i].co.y,0)) for i in face.vertices]
    values=[Vector((uvs.data[i].uv.x,uvs.data[i].uv.y,0)) for i in face.loop_indices]
    value=barycentric_transform(Vector((co.x,co.y,0)),*points,*values)
    cache[vertex.index]=value.xy
for loop in new.loops:new.uv_layers[0].data[loop.index].uv=cache[loop.vertex_index]
new.update()
record['uv_restore']={'source':'90_Before_Near_Middle_Depth original ground UV','method':'Barycentric transfer in original terrain triangles, including inserted edge vertices','vertices':len(new.vertices),'boundary_fallbacks':fallback,'intent':'Retain the original painting registration instead of repeating it across the extended western ground'}
(REVIEW/'uv-restore.json').write_text(json.dumps(record['uv_restore'],indent=2),encoding='utf-8')
export('near-middle-depth-original-uv')
