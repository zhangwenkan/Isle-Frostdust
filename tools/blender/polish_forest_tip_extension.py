"""Fit exposed rock crowns to the single joined turf in the Blender MCP session."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
O=ROOT/'artifacts/forest-tip-extension-review'
record=LAYOUT['reference_cape']['forest_tip_extension'];assert not record.get('crown_polish')
archive=bpy.data.collections.new('90_Before_Forest_Tip_Crown_Polish');SCENE.collection.children.link(archive)
ground=SCENE.objects['WALK_Forest_Ground']
floor=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
# The old core follows the superseded terrace outline. Its top rim cuts
# diagonally across the new turf. The new perimeter bedrock replaces it.
core=SCENE.objects['Cape_Attached_Cliff_Core']
for c in list(core.users_collection):c.objects.unlink(core)
archive.objects.link(core);core.hide_set(True);core.hide_render=True
changes={}
for name in LAYOUT['reference_cape']['cliff_masses']:
    ob=SCENE.objects[name];saved=ob.copy();saved.data=ob.data.copy();saved.name='Crown_Before_'+name
    archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    count=0
    for v in ob.data.vertices:
        if v.co.z<5.0:continue
        hit=floor.ray_cast(Vector((v.co.x,v.co.y,40)),Vector((0,0,-1)))[0]
        if hit is None:hit=floor.find_nearest(Vector((v.co.x,v.co.y,6.25)))[0]
        if hit:
            # Embedded top faces remain below the turf; exposed faces retain
            # their cut silhouette where the terrain perimeter turns inward.
            v.co.z=min(v.co.z,hit.z-.045);count+=1
    ob.data.update();changes[name]=count
record['crown_polish']={'date':'2026-11-19','superseded_core_archived':core.name,'fitted_top_vertices':changes,'joined_floor_positions_uv_unchanged':True}
export('forest-tip-crown-fit')
