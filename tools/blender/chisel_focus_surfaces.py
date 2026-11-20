"""MCP medium-scale chisel pass on selected actual stone surfaces."""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/rock-sculpt-focus-review';ASSET=ROOT/'assets/layered_island/rock_sculpt_focus'
s=bpy.data.scenes['Rock_Sculpt_Focus_20261119'];old=bpy.context.window.scene;bpy.context.window.scene=s
assert s.get('weather_pass')==2 and not s.get('chisel_pass'), 'Review existing cuts before repeating.'
col=bpy.data.collections['Rock_Focus_Authored'];rocks=list(col.objects)
archive=bpy.data.collections.new('Rock_Focus_Before_Chisel');s.collection.children.link(archive)
for o in rocks:
    cp=o.copy();cp.data=o.data.copy();cp.name='BeforeChisel_'+o.name;archive.objects.link(cp);cp.hide_render=True;cp.hide_set(True)

def cut(o,label,ring,axis='y',outer=-2.1):
    # Each listed ring is an individually designed planar loss, in local
    # stone coordinates. Extrude only the cutter outwards, not the rock.
    ax={'x':0,'y':1,'z':2}[axis];n=len(ring)
    verts=[list(p) for p in ring]
    for p in ring:
        q=list(p);q[ax]=outer;verts.append(q)
    faces=[tuple(range(n)),tuple(reversed(range(n,n*2)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new('Chisel_'+label);me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    c=bpy.data.objects.new(me.name,me);col.objects.link(c);c.matrix_world=o.matrix_world.copy()
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    m=o.modifiers.new(label,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(c,do_unlink=True);o.select_set(False)

hero=col.objects['Focus_Rock_01_Principal']
cut(hero,'Upper left slate loss',[(-1.08,-.88,1.66),(-.69,-.89,1.99),(-.34,-.92,1.80),(-.40,-.90,1.51),(-.82,-.88,1.29)])
cut(hero,'Lower inward fracture',[(-.68,-.90,1.06),(-.21,-.94,1.17),(.12,-.91,.82),(-.02,-.89,.46),(-.53,-.90,.43)])
cut(hero,'Short right recess',[(.60,-.84,1.65),(.97,-.81,1.92),(1.10,-.77,1.64),(.95,-.80,1.33),(.73,-.83,1.35)])
cut(hero,'Crown edge break',[(-.77,-.80,2.03),(-.61,-.63,2.07),(-.38,-.70,2.08),(-.43,-.92,1.95)],axis='z',outer=3.0)
cut(hero,'Right facing schist cleft',[(1.07,-.55,1.79),(.99,-.10,1.75),(.95,.14,1.17),(1.02,-.12,.98),(1.08,-.56,1.15)],axis='x',outer=2.0)
rear=col.objects['Focus_Rock_02_Oblique_Shoulder']
cut(rear,'Shoulder face pocket',[(-1.02,-.74,1.18),(-.65,-.77,1.41),(-.35,-.77,1.13),(-.47,-.73,.75),(-.89,-.72,.79)])
cut(rear,'Shoulder low step',[(-.23,-.77,.82),(.24,-.79,.98),(.50,-.72,.59),(.16,-.75,.35),(-.25,-.73,.40)])
cut(rear,'Roof chipped end',[(-.78,-.65,1.53),(-.49,-.55,1.59),(-.28,-.63,1.56),(-.42,-.83,1.44)],axis='z',outer=2.4)
foot=col.objects['Focus_Rock_03_Foot_Wedge']
cut(foot,'Wedge front shallow face',[(-.42,-.47,.66),(-.10,-.46,.72),(.17,-.45,.52),(.03,-.49,.25),(-.37,-.49,.29)])
low=col.objects['Focus_Rock_04_Low_Return']
cut(low,'Shelf stepped edge',[(-.65,-.49,.55),(-.21,-.45,.61),(.06,-.43,.42),(-.04,-.42,.25),(-.53,-.46,.25)])

for o in rocks:
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    # Small real wear at the new cut mouths only. Angle-limited modifier
    # ignores the gently curved already sculpted surface.
    bev=o.modifiers.new('Wear at new broken lips','BEVEL');bev.width=.012;bev.segments=2;bev.limit_method='ANGLE';bev.angle_limit=.55
    bpy.ops.object.modifier_apply(modifier=bev.name);o.select_set(False)
    # Large newly exposed planes keep their own normal. Voxel faces retain
    # their smooth relief, with no global balloon smoothing.
    for p in o.data.polygons:
        if p.area>.018:p.use_smooth=False
s['chisel_pass']=1
cam=s.camera;cam.data.ortho_scale=4.25;cam.location=(3.4,-6.5,4.0)
cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
for o in rocks:o.hide_render=o!=hero
s.render.filepath=str(OUT/'pass4-principal-clay.png');bpy.ops.render.render(write_still=True)
for o in rocks:o.hide_render=False
cam.data.ortho_scale=6.6;cam.location=(3.3,-7,4.6);cam.rotation_euler=(Vector((-.4,.3,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(OUT/'pass4-group-clay.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(ASSET/'sculpted_coastal_rocks.blend'),{s},fake_user=True,compress=True)
bpy.context.window.scene=old
print('Individually placed medium-scale surface losses saved and rendered.')
