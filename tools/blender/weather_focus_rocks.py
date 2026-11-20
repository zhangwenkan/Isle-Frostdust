"""Second MCP sculpt pass: wear the authored edges without random noise.

Voxel remesh joins the chisel topology. Sculpt strokes are explicitly placed
at chosen corners and along two geological bedding directions. The broad
cut planes remain, but the manufactured bevel seams are removed.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/rock-sculpt-focus-review'
ASSET=ROOT/'assets/layered_island/rock_sculpt_focus'
s=bpy.data.scenes['Rock_Sculpt_Focus_20261119'];original=bpy.context.window.scene;bpy.context.window.scene=s
assert not s.get('weather_pass'), 'Already sculpted; inspect instead of repeating.'
archive=bpy.data.collections.new('Rock_Focus_Before_Weather');s.collection.children.link(archive)
rocks=list(bpy.data.collections['Rock_Focus_Authored'].objects)
strokes={
 'Focus_Rock_01_Principal':[
   ((-.96,-.84,1.95),(.22,.25,.21),-.115),((-.53,-1.02,1.92),(.16,.23,.12),-.065),
   ((.40,-.59,2.31),(.26,.22,.13),-.075),((1.02,-.64,1.99),(.17,.20,.22),-.088),
   ((1.16,-.67,1.04),(.15,.20,.22),-.092),((-.94,-.77,.29),(.24,.20,.18),-.072),
   ((.95,.55,1.84),(.22,.22,.14),-.064),((-.85,.56,2.23),(.15,.23,.17),-.066),
   ((-.43,-1.04,1.28),(.57,.30,.68),-.055),((.91,.01,1.22),(.35,.52,.43),-.063),
   ((-.18,.05,2.32),(.48,.59,.20),-.036)],
 'Focus_Rock_02_Oblique_Shoulder':[
   ((-1.25,-.67,1.33),(.22,.25,.18),-.093),((-.70,-.62,1.60),(.21,.22,.14),-.075),
   ((.42,-.64,1.47),(.18,.22,.17),-.078),((1.05,-.50,1.02),(.24,.23,.24),-.065),
   ((-1.33,-.69,.57),(.15,.23,.18),-.070),((.19,-.90,.62),(.42,.28,.32),-.044),
   ((-.54,.57,1.60),(.24,.24,.16),-.052)],
 'Focus_Rock_03_Foot_Wedge':[
   ((-.39,-.46,.79),(.16,.18,.13),-.065),((.24,-.41,.89),(.14,.21,.12),-.052),
   ((.55,-.38,.53),(.17,.15,.18),-.050),((-.66,-.46,.29),(.13,.15,.13),-.056)],
 'Focus_Rock_04_Low_Return':[
   ((-.54,-.50,.66),(.16,.14,.13),-.047),((.31,-.49,.55),(.19,.18,.12),-.043),
   ((-.81,-.54,.36),(.14,.13,.15),-.039)]}
for o in rocks:
    cp=o.copy();cp.data=o.data.copy();cp.name='BeforeWeather_'+o.name;archive.objects.link(cp);cp.hide_render=True;cp.hide_set(True)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    rem=o.modifiers.new('Joined sculpt volume','REMESH');rem.mode='VOXEL';rem.voxel_size=.027 if '01_' in o.name else .029
    rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=o.modifiers.new('Edge wear sculpt relaxation','SMOOTH');sm.factor=.60;sm.iterations=4
    bpy.ops.object.modifier_apply(modifier=sm.name);o.data.update()
    for v in o.data.vertices:
        p=v.co.copy();amount=0
        for center,radii,strength in strokes[o.name]:
            q=sum(((p[k]-center[k])/radii[k])**2 for k in range(3))
            amount+=strength*math.exp(-q*2.2)
        # Two deliberately sparse, shallow mineral beds on principal stone.
        if '01_' in o.name:
            bed=p.z+.20*p.x-.09*p.y
            front=math.exp(-((p.y+1.0)/.31)**2)
            amount-=front*(.013*math.exp(-((bed-.63)/.057)**2)+.010*math.exp(-((bed-1.32)/.048)**2))
        elif '02_' in o.name:
            bed=p.z-.12*p.x
            amount-=.014*math.exp(-((bed-.70)/.044)**2)*math.exp(-((p.y+.80)/.28)**2)
        v.co += v.normal*amount
    o.data.update()
    # A limited retopology pass keeps edge loss and hollows while removing
    # voxel stair steps. It doesn't use polygon count as a quality measure.
    dec=o.modifiers.new('Sculpt surface simplification','DECIMATE');dec.ratio=.24
    bpy.ops.object.modifier_apply(modifier=dec.name)
    for p in o.data.polygons:p.use_smooth=True
    o.select_set(False)
s['weather_pass']=1
cam=s.camera;cam.data.ortho_scale=4.25;cam.location=(3.4,-6.5,4.0)
cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
for o in rocks:o.hide_render=o.name!='Focus_Rock_01_Principal'
s.render.filepath=str(OUT/'pass2-principal-clay.png');bpy.ops.render.render(write_still=True)
for o in rocks:o.hide_render=False
cam.data.ortho_scale=6.6;cam.location=(3.3,-7,4.6)
cam.rotation_euler=(Vector((-.4,.3,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(OUT/'pass2-group-clay.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(ASSET/'sculpted_coastal_rocks.blend'),{s},fake_user=True,compress=True)
(OUT/'weather-state.json').write_text(json.dumps({'stage':2,'method':'Joined volume, selected sculpt strokes, controlled edge losses and shallow beds; no random noise displacement.',
    'rocks':[{'name':o.name,'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)} for o in rocks]},indent=2),encoding='utf8')
bpy.context.window.scene=original
print('Second actual sculpt pass saved and rendered.')
