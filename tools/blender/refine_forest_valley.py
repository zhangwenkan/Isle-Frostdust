"""Let the rear forest fall away from the path; do not tilt the whole World."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
REVIEW=ROOT/'artifacts/bamboo-west-extension-review';COL=bpy.data.collections['43_West_Forest']
assert not LAYOUT['forest_extension'].get('rear_valley')
def sink(y):return .34*max(0,y-14.7)*sm(14.7,17.7,y)
for ob in COL.objects:
    if ob.type!='MESH':continue
    for v in ob.data.vertices:v.co.z-=sink(v.co.y)
    ob.data.update()
# Reduce the regular star-like understory clusters into low fern groupings.
ob=SCENE.objects.get('Forest_Grass_Understory')
if ob:
    # Individual connected fronds are kept; a uniform material adjustment is
    # done in Godot so their roots and foliage shadows remain coherent.
    ob['understory_tint']=[.63,.77,.53]
LAYOUT['forest_extension']['rear_valley']=True
LAYOUT['camera']['physical_offset']=[0,8.80,32.30]
LAYOUT['camera']['physical_fov']=22.5
export('west-forest-valley')
