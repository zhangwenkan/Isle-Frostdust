"""Blender MCP: recess the stair flight and bring existing toe rock around it."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-cape-weight-review';A=R/'assets/layered_island/tripo_replica';s=bpy.data.scenes['Rock_Cape_Weight_Game_20261119'];bpy.context.window.scene=s
assert s['revision']=='rock-cape-weight-game-1'
st=s.objects['WALK_Tripo_Stairs'];core=s.objects['Rock_Stair_Embedded_Core'];P=st.matrix_world
def xc(y):return -.070+(y+.449)*.287
def remap_y(y):return -.184+(y+.184)*(.306/.356)
# Preserve vertices and UVs, but remove the mechanically identical nosing
# ledge from most steps. Only selected chipped noses retain small variation.
for ob in [st,core]:
    for v in ob.data.vertices:
        oldy=v.co.y;newy=remap_y(oldy);v.co.x+=xc(newy)-xc(oldy);v.co.y=newy
        if ob==st:
            j=v.index//28;k=v.index%28
            if k in range(14,21):
                src=ob.data.vertices[j*28+k-14].co
                # Solid near-vertical front, exposed thickness comes from mass.
                v.co.y=src.y+.00025
                v.co.x=src.x
    ob.data.update()
# Extend only the existing low flank rock toward the shortened lower steps.
rock=s.objects['WALK_Tripo_Rock_Surface'];inv=rock.matrix_world.inverted();count=0
for v in rock.data.vertices:
    p=inv@(rock.matrix_world@v.co);x,y,z=p
    side=abs(x-xc(y));w=max(0,1-abs(side-.115)/.07)*max(0,1-abs(y+.39)/.11)*max(0,1-z/.22)
    if w>0:
        v.co.y-=.024*w;count+=1
rock.data.update()
# Restore the original beach heights first, then apply an even lower blend at
# the revised step foot. This is a geometry contact, not a painted contact disk.
fit=json.loads((A/'game_assembly.json').read_text());sand=s.objects['GameJoin_WALK_Cape_Sand']
with bpy.data.libraries.load(str(R/'assets/layered_island/layered_island.blend'),link=False) as (available,loaded):loaded.objects=['WALK_Cape_Sand']
original=loaded.objects[0];assert len(original.data.vertices)==len(sand.data.vertices)
for dst,src in zip(sand.data.vertices,original.data.vertices):dst.co=src.co
start=P@Vector((xc(-.484),-.484,.082));end=P@Vector((xc(-.184),-.184,.343));axis=(Vector((end.x,end.y))-Vector((start.x,start.y))).normalized();sidevec=Vector((axis.y,-axis.x))
for v in sand.data.vertices:
    d=Vector((v.co.x-start.x,v.co.y-start.y));a=d.dot(axis);b=abs(d.dot(sidevec))
    if -.7<a<.9 and b<1.9 and v.co.z>-.15:v.co.z+=(.012+.042*min(1,b/1.25))*math.exp(-((a-.1)/.52)**2)*math.exp(-(b/1.5)**4)
sand.data.update()
fit['sample_anchors']['cape_stair_bottom']=[start.x,start.z,-start.y]
fit['revision']='rock-cape-weight-game-2';s['revision']=fit['revision'];(A/'game_assembly.json').write_text(json.dumps(fit,indent=2),encoding='utf8')
for ob in s.objects:ob.select_set(ob.type=='MESH')
bpy.context.view_layer.objects.active=rock
bpy.data.libraries.write(str(A/'tripo_game_assembly.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
(O/'steps-refined.json').write_text(json.dumps({'revision':s['revision'],'stair_plan_shortened':.306/.356,'flank_vertices_reshaped':count,'new_bottom':fit['sample_anchors']['cape_stair_bottom']},indent=2),encoding='utf8');print('Recessed step flight and original rock toe exported.')
