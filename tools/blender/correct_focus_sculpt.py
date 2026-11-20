"""Replace unstable normal strokes with directional chisel strokes via MCP."""
import bpy, math, json, bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/rock-sculpt-focus-review';ASSET=ROOT/'assets/layered_island/rock_sculpt_focus'
s=bpy.data.scenes['Rock_Sculpt_Focus_20261119'];old=bpy.context.window.scene;bpy.context.window.scene=s
assert s.get('weather_pass')==1, 'Inspect current revision before applying correction.'
rocks=list(bpy.data.collections['Rock_Focus_Authored'].objects)
# Restore the intact first sculpt, retaining the failed images for diagnosis.
for o in rocks:
    o.data=bpy.data.objects['BeforeWeather_'+o.name].data.copy()
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    rem=o.modifiers.new('Joined chisel volume','REMESH');rem.mode='VOXEL';rem.voxel_size=.023 if '01_' in o.name else .025;rem.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=o.modifiers.new('Small edge relaxation','SMOOTH');sm.factor=.45;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
    # Broad, directional sculpt strokes have a constant inward direction,
    # avoiding convergence and self intersections around normal discontinuities.
    if '01_' in o.name:
        strokes=[((-.91,-.78,2.08),(.32,.31,.28),(.040,.040,-.045)),
                 ((.49,-.63,2.27),(.35,.30,.20),(-.018,.026,-.045)),
                 ((1.05,-.65,1.90),(.26,.28,.32),(-.036,.023,-.026)),
                 ((1.13,-.70,1.13),(.25,.32,.39),(-.038,.028,.007)),
                 ((-.49,-1.01,1.27),(.52,.31,.61),(.000,.062,.012)),
                 ((.45,-.94,.50),(.47,.35,.32),(.023,.045,-.003)),
                 ((.98,.32,1.19),(.39,.59,.51),(-.052,.006,.011)),
                 ((-.91,.54,2.15),(.27,.35,.27),(.034,-.014,-.037))]
    elif '02_' in o.name:
        strokes=[((-1.21,-.66,1.30),(.30,.34,.23),(.038,.026,-.045)),
                 ((-.57,-.62,1.59),(.28,.32,.21),(.004,.023,-.037)),
                 ((.42,-.63,1.47),(.28,.28,.24),(-.015,.027,-.037)),
                 ((.19,-.88,.64),(.43,.34,.35),(.002,.043,.000))]
    elif '03_' in o.name:
        strokes=[((-.40,-.43,.80),(.25,.25,.19),(.021,.018,-.030)),
                 ((.22,-.42,.89),(.24,.25,.18),(-.014,.020,-.029))]
    else:strokes=[((-.55,-.51,.63),(.25,.23,.17),(.017,.020,-.026))]
    for v in o.data.vertices:
        p=v.co.copy();delta=Vector((0,0,0))
        for center,radii,direction in strokes:
            q=sum(((p[k]-center[k])/radii[k])**2 for k in range(3))
            delta+=Vector(direction)*math.exp(-q*1.7)
        v.co+=delta
    o.data.update()
    dec=o.modifiers.new('Preserve worn facets','DECIMATE');dec.ratio=.30;bpy.ops.object.modifier_apply(modifier=dec.name)
    for p in o.data.polygons:p.use_smooth=True
    o.select_set(False)
s['weather_pass']=2
cam=s.camera;cam.data.ortho_scale=4.25;cam.location=(3.4,-6.5,4.0)
cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
for o in rocks:o.hide_render=o.name!='Focus_Rock_01_Principal'
s.render.filepath=str(OUT/'pass3-principal-clay.png');bpy.ops.render.render(write_still=True)
for o in rocks:o.hide_render=False
cam.data.ortho_scale=6.6;cam.location=(3.3,-7,4.6);cam.rotation_euler=(Vector((-.4,.3,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(OUT/'pass3-group-clay.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(ASSET/'sculpted_coastal_rocks.blend'),{s},fake_user=True,compress=True)
bpy.context.window.scene=old
print('Directional sculpt correction saved, with two actual renders.')
