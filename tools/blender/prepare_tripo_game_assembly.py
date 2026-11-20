"""Game assembly in an isolated Blender scene, submitted through Blender MCP.
Keeps the main island source untouched, clips only copied ground beneath rock.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-game-integration-review';A=R/'assets/layered_island/tripo_replica'
SN='Tripo_Game_Assembly_20261119';assert not bpy.data.scenes.get(SN)
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
source=bpy.data.scenes['Tripo_Grit_Textured_Delivery_20261119']
with bpy.data.libraries.load(str(R/'assets/layered_island/layered_island.blend'),link=False) as (available,loaded):
    loaded.objects=[name for name in ['WALK_Forest_Ground','Cape_Terminus_Bedrock','Forest_Strict_Grass','Forest_Strict_Understory','Forest_Strict_Flowers'] if name in available.objects]
loaded_map={o.name:o for o in loaded.objects}
# Uniform scale respects the existing material sample's proportions.
scale=(3.8564-.15)/(.343-.0806)
angle=math.atan2(4.8,-.8)-math.atan2(.265,.076055)
rot=Matrix.Rotation(angle,4,'Z');scale_mat=Matrix.Diagonal((scale,scale,scale,1))
origin=Vector((-62.5,4,.15))-(rot@(Vector((-.07,-.449,.0806))*scale))
placement=Matrix.Translation(origin)@rot@scale_mat
rock=None;stairs=None
for key,new in [('Grit_Delivery_Rocks','WALK_Tripo_Rock_Surface'),('Grit_Delivery_Stairs','WALK_Tripo_Stairs')]:
    old=source.objects[key];ob=old.copy();ob.data=old.data.copy();ob.name=new;s.collection.objects.link(ob)
    ob.matrix_world=placement@old.matrix_world
    if key.endswith('Rocks'):rock=ob
    else:stairs=ob
report={'scene':SN,'scale':scale,'angle_radians':angle,'origin_blender':list(origin),'copied_clips':[]}
for old in loaded.objects:
    s.collection.objects.link(old);old['original_game_name']=old.name
    name=old.name
    bm=bmesh.new();bm.from_mesh(old.data)
    count=len(bm.faces)
    # Exact bisects confine the removal to the rock footprint intersection,
    # preserving UV interpolation on the retained forest/slope mesh.
    for point,normal in [((-59.8,0,0),(1,0,0)),((0,14.5,0),(0,1,0))]:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,dist=.00001)
    cut=[f for f in bm.faces if (lambda c:c.x<-59.80001 and c.y<14.49999)(f.calc_center_median())]
    bmesh.ops.delete(bm,geom=cut,context='FACES');bm.to_mesh(old.data);bm.free();old.data.update()
    old.name='GameJoin_'+name
    report['copied_clips'].append({'name':old.name,'original':name,'before_faces':count,'removed_faces':len(cut),'after_faces':len(old.data.polygons)})
def godot(v):return [float(v.x),float(v.z),float(-v.y)]
report['sample_anchors']={
 'cape_center':godot(placement@Vector((.065,.015,.355))),
 'cape_stair_top':godot(placement@Vector((.006055,-.184,.343))),
 'cape_stair_bottom':godot(placement@Vector((-.07,-.449,.0806))),
 'fire_center':godot(placement@Vector((0,0,.361)))}
report['placement_matrix']=[list(row) for row in placement]
for ob in s.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=rock
# Exports only this addon. Replacements retain their Blender-authored UV/data.
s['revision']='grit-game-assembly-first-fit'
bpy.data.libraries.write(str(A/'tripo_game_assembly.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
(O/'assembly.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
