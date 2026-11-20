"""Blender MCP: hand-place broad lower tread ends and worn top planes."""
import bpy,json,math
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-cape-weight-review';A=R/'assets/layered_island/tripo_replica';s=bpy.data.scenes['Rock_Cape_Weight_Game_20261119'];bpy.context.window.scene=s
assert s['revision']=='rock-cape-weight-game-3'
ob=s.objects['WALK_Tripo_Stairs'];me=ob.data
# Explicit asymmetry, in metres, for the lower seven stone treads.
# left extension, right extension, centre shift, front corner recession.
rows=[(.23,.05,-.06,.10),(.03,.18,.04,.17),(.17,-.04,-.07,.04),(-.05,.12,.03,.14),(.10,.02,-.04,.08),(.02,.11,.01,.05),(.04,-.01,-.015,.08)]
fronts=[[.10,.025,-.035,-.055,-.02,.015,.14],[.15,.045,0,.025,-.035,-.01,.06],[.03,-.02,.025,.045,.015,-.035,.09],[.12,.025,-.01,-.045,-.02,.04,.15],[.04,-.035,.015,.035,.02,-.015,.08],[.07,.025,-.025,.01,.03,-.015,.11],[.09,0,-.02,-.03,.01,.025,.06]]
for j,row in enumerate(rows):
    le,re,shift,corner=row
    for k,u in enumerate([-1,-.74,-.38,0,.37,.72,1]):
        i=j*28+k*4
        dx=(shift+(-le if u<0 else re)*abs(u))/14.125
        for offset in range(4):me.vertices[i+offset].co.x+=dx
        front=me.vertices[i];rear=me.vertices[i+1];bottom=me.vertices[i+2]
        dy=fronts[j][k]/14.125;front.co.y+=dy;bottom.co.y+=dy
        # Wear is a shallow change of a real top plane, not a perimeter bevel.
        wear=[-.030,-.008,0,-.012,.008,-.004,-.020][k]*([1,.55,.8,.6,1,.4,.6][j])/14.125
        front.co.z+=wear
        if j==0:front.co.z+=.050/14.125;rear.co.z+=.035/14.125
me.update()
col=me.color_attributes.new(name='Stone_Plane_Value',type='FLOAT_COLOR',domain='CORNER')
values=[1.02,.97,1.045,.985,1.01,.96,1.025,1,.98,1.02,1,1.015,.99,1.02,1,1]
for p in me.polygons:
    j=min(15,me.loops[p.loop_start].vertex_index//28);v=values[j]
    for li in p.loop_indices:col.data[li].color=(v,v,v,1)
# Give the concealed core enough width to close the prior narrow sea slits.
core=s.objects['Rock_Stair_Embedded_Core']
for v in core.data.vertices:
    y=v.co.y;cx=-.070+(y+.449)*.287
    v.co.x=cx+(v.co.x-cx)*1.16
core.data.update()
s['revision']='rock-cape-weight-game-4';fit=json.loads((A/'game_assembly.json').read_text());fit['revision']=s['revision'];(A/'game_assembly.json').write_text(json.dumps(fit,indent=2),encoding='utf8')
for x in s.objects:x.select_set(x.type=='MESH')
bpy.context.view_layer.objects.active=ob;bpy.data.libraries.write(str(A/'tripo_game_assembly.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
(O/'lower-tread-refine.json').write_text(json.dumps({'revision':s['revision'],'lower_treads_authored':7,'shape_adjustments_metres':rows,'automatic_bevel':False,'buried_core_widened':1.16},indent=2),encoding='utf8');print('Seven lower tread outlines and top planes refined.')
