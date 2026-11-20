"""MCP: finish tread edge design using the original interleaved vertex layout."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-cape-weight-review';A=R/'assets/layered_island/tripo_replica';s=bpy.data.scenes['Rock_Cape_Weight_Game_20261119'];bpy.context.window.scene=s
assert s['revision']=='rock-cape-weight-game-2'
st=s.objects['WALK_Tripo_Stairs'];st.data=bpy.data.scenes['Rock_Cape_Weight_Delivery_20261119'].objects['Weight_Delivery_Stairs'].data.copy()
def xc(y):return -.070+(y+.449)*.287
edge_offsets=[[-.005,-.002,0,.001,-.001,0,.004],[.004,.001,-.002,-.003,0,.002,.006],[-.003,-.001,.001,.002,0,-.002,-.003],[.005,.002,.001,-.002,-.001,0,-.004],[-.004,-.001,0,.001,.002,0,.003],[.003,.001,-.001,0,.002,.001,-.003]]
for v in st.data.vertices:
    oldy=v.co.y;newy=-.184+(oldy+.184)*(.306/.356);v.co.x+=xc(newy)-xc(oldy);v.co.y=newy
for j in range(16):
    for k in range(7):
        i=j*28+k*4;front=st.data.vertices[i];rear=st.data.vertices[i+1];bf=st.data.vertices[i+2]
        off=edge_offsets[j%6][k]*(1.0 if j<7 else .55)
        front.co.y+=off;bf.co.y=front.co.y+.00035;bf.co.x=front.co.x
        # Broad unequal stone ends, not uniformly bevelled rectangles.
        if k in [0,6]:
            sx=(-1 if k==0 else 1)*([.003,-.002,.004,0,-.003,.002][j%6])
            front.co.x+=sx;rear.co.x+=sx;bf.co.x+=sx
st.data.update()
# Keep the original planar beach heights. Burial is achieved by the step base;
# raising a few beach vertices intersects the existing swash overlay.
sand=s.objects['GameJoin_WALK_Cape_Sand']
with bpy.data.libraries.load(str(R/'assets/layered_island/layered_island.blend'),link=False) as (available,loaded):loaded.objects=['WALK_Cape_Sand']
src=loaded.objects[0]
for dst,v in zip(sand.data.vertices,src.data.vertices):dst.co=v.co
sand.data.update()
s['revision']='rock-cape-weight-game-3';fit=json.loads((A/'game_assembly.json').read_text());fit['revision']=s['revision'];(A/'game_assembly.json').write_text(json.dumps(fit,indent=2),encoding='utf8')
for ob in s.objects:ob.select_set(ob.type=='MESH')
bpy.context.view_layer.objects.active=st;bpy.data.libraries.write(str(A/'tripo_game_assembly.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
print('Step contours corrected, regular nosing reduced; original beach height restored.')
