"""Final local leaf silhouette rhythm, Blender MCP."""
import bpy,random,math,json
from mathutils import Vector,Matrix
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Pixel_Cavern_Coast'];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-living-vegetation-8'
r=random.Random(692);changed=0
for ob in scene.objects:
    if not ob.get('pixel_cavern') or not ob.name.startswith(('LiveVineLeaf_','LiveCanopy_')):continue
    me=ob.data;normals=[tuple(n.vector) for n in me.corner_normals]
    for k in range(0,len(me.vertices),10):
        c=[(me.vertices[k+j*2].co+me.vertices[k+j*2+1].co)*.5 for j in range(5)]
        origin=c[0];vine=ob.name.startswith('LiveVineLeaf_')
        length=r.uniform(.66,1.0) if vine else r.uniform(.78,1.10)
        width=r.uniform(.86,1.28) if vine else 1.15
        rot=Matrix.Rotation(r.uniform(-.35,.35) if vine else r.uniform(-.14,.14),3,'Y')
        for j in range(5):
            for n in [0,1]:
                v=me.vertices[k+j*2+n];delta=c[j]-origin
                v.co=origin+rot@(delta*length+(v.co-c[j])*width)
        changed+=1
    me.update();me.normals_split_custom_set(normals)
bpy.data.libraries.write(str(root/'assets/pixel_cavern_coast/pixel_cavern_coast.blend'),{scene},fake_user=True,compress=True)
print(json.dumps({'refined_leaf_silhouettes':changed}))
