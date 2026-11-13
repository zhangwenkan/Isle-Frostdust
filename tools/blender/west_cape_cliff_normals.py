"""Give the continuous cape flank broad sedimentary planes, through Blender MCP."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/west-cape-opening-review'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
ob=scene.objects['Fish_West_Continuous_Land'];me=ob.data
# The slope and turf stay smooth. Only the exposed western cliff receives
# a controlled mixture of its real planar normal and its existing corner normal.
me.normals_split_custom_set([(0.,0.,0.)]*len(me.loops))
me.update()
existing=[n.vector.copy() for n in me.corner_normals]
normals=[];changed=0
for p in me.polygons:
    center=sum((me.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    t=max(0.,min(1.,(-center.x-15.0)/4.0));w=t*t*(3-2*t)
    strength=.64*w if p.material_index==1 else 0.
    for li in p.loop_indices:normals.append(tuple(existing[li].lerp(p.normal,strength).normalized()))
    if strength>0:changed+=1
me.normals_split_custom_set(normals);me.update()
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
(OUT/'cliff-normals.json').write_text(json.dumps({'cape_faces':changed,'geometry_changed':False,'normal_plane_mix':.64},indent=2),encoding='utf-8')
print('CAPE_CLIFF_PLANES_EXPORTED')
