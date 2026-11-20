"""Reorient folded leaf widths for the real close perspective. Blender MCP."""
import bpy,json,math,random
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Pixel_Cavern_Coast'];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-living-vegetation-8'
r=random.Random(634);count=0
for ob in scene.objects:
    if not ob.get('pixel_cavern') or not ob.name.startswith(('LiveCanopy_','LiveVineLeaf_','LiveBambooLeaf_','LiveGrass_')):continue
    me=ob.data
    normals=[tuple(n.vector) for n in me.corner_normals]
    for k in range(0,len(me.vertices),10):
        if k+9>=len(me.vertices):break
        centers=[(me.vertices[k+j*2].co+me.vertices[k+j*2+1].co)*.5 for j in range(5)]
        d=(centers[-1]-centers[0]).normalized()
        view=Vector((r.uniform(-.40,.25),-1,r.uniform(.32,.72))).normalized()
        side=d.cross(view).normalized()
        scale=1.18 if ob.name.startswith('LiveCanopy_') else 1.05
        if ob.name.startswith('LiveBambooLeaf_'):scale=1.14
        for j in range(5):
            a=me.vertices[k+j*2];b=me.vertices[k+j*2+1];w=(a.co-b.co).length*.5*scale
            a.co=centers[j]-side*w;b.co=centers[j]+side*w
        count+=1
    me.update()
    me.normals_split_custom_set(normals)
bpy.data.libraries.write(str(root/'assets/pixel_cavern_coast/pixel_cavern_coast.blend'),{scene},fake_user=True,compress=True)
print(json.dumps({'leaf_planes_refined':count,'reason':'folded widths were edge-on to close camera'}))
