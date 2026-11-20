"""Lower the inner crown of the attached stair-side rock through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
record=LAYOUT['reference_cape']['forest_tip_extension'];assert not record.get('stair_rock_settled')
ob=SCENE.objects['Cape_Cliff_Plane_02'];archive=bpy.data.collections['90_Before_Forest_Tip_Crown_Polish']
saved=ob.copy();saved.data=ob.data.copy();saved.name='StairRock_Before_'+ob.name;archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
count=0
for v in ob.data.vertices:
    if v.co.z>5.0:v.co.z-=.28;count+=1
ob.data.update()
record['stair_rock_settled']={'upper_vertices':count,'lowered_m':.28,'reason':'Large cut top face crossed above the curved turf between its corners'}
export('forest-tip-stair-rock-settled')
