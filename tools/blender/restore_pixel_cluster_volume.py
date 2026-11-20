"""Correct the first harmony pass after inspecting actual game views. MCP only."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘');s=bpy.data.scenes['Pixel_Cavern_Coast'];bpy.context.window.scene=s
assert s['revision']=='pixel-cavern-vegetation-harmony-9'
count=0
for o in s.objects:
    if not o.get('pixel_cavern') or not o.name.startswith(('LiveGrass_','LiveBambooLeaf_')):continue
    me=o.data;norms=[]
    if o.name.startswith('LiveGrass_'):
        for k in range(0,len(me.vertices),10):
            origin=(me.vertices[k].co+me.vertices[k+1].co)*.5
            f=.5+.27*math.sin(origin.x*.76+origin.y*.31)+.20*math.cos(origin.y*1.04-origin.x*.23)
            t=max(0,min(1,(f-.36)/.38));t=t*t*(3-2*t);old=.24+.73*t
            # Wider, soft hills of blades with no exposed flat carpet between them.
            new=.58+.90*t;ratio=new/old
            dx=.27*.76*math.cos(origin.x*.76+origin.y*.31)+.20*.23*math.sin(origin.y*1.04-origin.x*.23)
            dy=.27*.31*math.cos(origin.x*.76+origin.y*.31)-.20*1.04*math.sin(origin.y*1.04-origin.x*.23)
            n=Vector((-dx*2.1,-dy*2.1,1)).normalized()
            for j in range(10):
                v=me.vertices[k+j];v.co.z=origin.z+(v.co.z-origin.z)*ratio
            norms.extend([tuple(n)]*10)
    else:
        uv=me.uv_layers[0];uv2=me.uv_layers[1];roots={}
        for l in me.loops:
            x,y=uv.data[l.index].uv;z,_=uv2.data[l.index].uv;roots[l.vertex_index]=Vector((x,y-1,z))
        for k in range(0,len(me.vertices),10):
            origin=roots[k]
            for j in range(5):
                a=me.vertices[k+2*j];b=me.vertices[k+2*j+1];center=(a.co+b.co)*.5
                for v in (a,b):v.co=origin+(center-origin)*1.52+(v.co-center)*1.68
            tip=(me.vertices[k+8].co+me.vertices[k+9].co)*.5;d=(tip-origin).normalized()
            # Shared fan-facing normals preserve a rounded shoulder, not lit stripes.
            n=Vector((d.x*.32,d.y*.32,.86)).normalized();norms.extend([tuple(n)]*10)
        count+=1
    me.update();me.normals_split_custom_set_from_vertices(norms)
s['revision']='pixel-cavern-vegetation-harmony-10'
bpy.data.libraries.write(str(root/'assets/pixel_cavern_coast/pixel_cavern_coast.blend'),{s},fake_user=True,compress=True)
print(json.dumps({'revision':s['revision'],'bamboo_meshes':count}))
