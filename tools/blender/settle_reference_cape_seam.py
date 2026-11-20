"""Settle only the new shoulder's eastern seam onto the unchanged old slope."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
assert LAYOUT['reference_cape'].get('seam_settled',{}).get('revision',1)<3
old=SCENE.objects['WALK_Forest_NearSlope'];new=SCENE.objects['Cape_Connection_Shoulder']
seam=sorted([v.co.copy() for v in old.data.vertices if abs(v.co.x+63.04)<.002],key=lambda p:p.y)
def z_at(y):
    if y<=seam[0].y:return seam[0].z
    # Keep the old upper corner in the triangulated interpolation rather than
    # letting a row on the higher neck lift the boundary before that corner.
    if abs(y-seam[-1].y)<.15:return seam[-1].z
    for a,b in zip(seam,seam[1:]):
        if a.y<=y<=b.y:return a.z+(b.z-a.z)*(y-a.y)/(b.y-a.y)
    return None
changed=0
for v in new.data.vertices:
    weight=1-sm(0,.64,-v.co.x-63.04)
    z=z_at(v.co.y)
    if z is not None and weight>0:
        v.co.z=v.co.z*(1-weight)+z*weight;changed+=1
new.data.update()
# The near lip follows the new surface; update the corresponding imported
# skirt's top edge, leaving its submerged bottom intact.
from mathutils.bvhtree import BVHTree
tree=BVHTree.FromPolygons([v.co for v in new.data.vertices],[list(p.vertices) for p in new.data.polygons])
for v in SCENE.objects['Cape_Connection_Closed_Skirt'].data.vertices:
    if v.co.z>2.5:
        hit=tree.find_nearest(v.co)[0]
        if hit is not None and (hit.xy-v.co.xy).length<.01:v.co.z=hit.z
SCENE.objects['Cape_Connection_Closed_Skirt'].data.update()
floors=[o for o in bpy.data.collections['49_Reference_Cape'].objects if o.type=='MESH' and (o.name.startswith(('WALK_','Cape_Cliff_')) or o.name in ['Cape_Attached_Cliff_Core','Cape_Connection_Shoulder'])]
trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in floors]
grass=SCENE.objects['Cape_Shore_Grass'].data
for p in grass.polygons:
    roots=[grass.loops[li].vertex_index for li in p.loop_indices if grass.uv_layers[1].data[li].uv.x<.01]
    assert len(roots)==2
    root=(grass.vertices[roots[0]].co+grass.vertices[roots[1]].co)/2
    hits=[t.ray_cast(Vector((root.x,root.y,40)),Vector((0,0,-1)))[0] for t in trees];hits=[h for h in hits if h is not None]
    if hits:delta=Vector((0,0,max(h.z for h in hits)+.014-root.z))
    else:
        near=[t.find_nearest(root)[0] for t in trees];near=[h for h in near if h is not None and (h.xy-root.xy).length<.7]
        assert near,list(root)
        h=min(near,key=lambda h:(h-root).length);delta=h-root+Vector((0,0,.014))
    for i in p.vertices:grass.vertices[i].co+=delta
grass.update()
LAYOUT['reference_cape']['seam_settled']={'revision':3,'modified_new_vertices':changed,'old_slope_unchanged':True,'new_eastern_boundary_interpolated_from_old':True,'grass_roots_identified_by_zero_wind_weight':True}
export('reference-cape-seam-settled')
