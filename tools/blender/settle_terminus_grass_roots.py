"""Fit every fixed root vertex to its actual rock or terrain surface."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
rc=LAYOUT['reference_cape'];assert not rc['rocky_terminus'].get('root_vertex_fit')
names=['WALK_Forest_Ground']+rc['cliff_masses']
trees=[BVHTree.FromPolygons([v.co for v in SCENE.objects[n].data.vertices],[list(p.vertices) for p in SCENE.objects[n].data.polygons]) for n in names]
o=SCENE.objects['Forest_Grass_Terminus'];me=o.data;uv=me.uv_layers[1];roots=set()
for i,loop in enumerate(me.loops):
    if uv.data[i].uv.x<.001:roots.add(loop.vertex_index)
for vi in roots:
    p=me.vertices[vi].co;hits=[t.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0] for t in trees];p.z=max(h.z for h in hits if h is not None)+.012
me.update();rc['rocky_terminus']['root_vertex_fit']={'fixed_vertices':len(roots),'fit':'each actual vertex; UV2 weights unchanged'}
export('forest-rocky-terminus-review')
