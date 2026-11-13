"""Inspect original map geometry and placement via Blender MCP; never save the island."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix
R=Path('D:/自己做着玩的/孤屿霜尘')
O=R/'artifacts/coast-junction-study-20261111'
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
original=bpy.context.window.scene
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
reference=next((s for s in bpy.data.scenes if s.library and s.name=='WS_Bamboo_Study'),None)
if reference is None:
    with bpy.data.libraries.load(str(S/'bamboo-study-editable.blend'), link=True) as (source,target):
        target.scenes=[n for n in source.scenes if n=='WS_Bamboo_Study']
    reference=target.scenes[0]
scene=bpy.data.scenes.get('WS_Junction_Inspection_20261111') or bpy.data.scenes.new('WS_Junction_Inspection_20261111')
for old in list(scene.objects): bpy.data.objects.remove(old,do_unlink=True)
bpy.context.window.scene=scene
report=[]
placements={(p['component'],p['instance']):p for p in json.loads((S/'placements.json').read_text(encoding='utf8'))}
Q=Matrix.Diagonal((1,-1,1,1))
bounds_cache={}
for ob in reference.objects:
    if ob.type!='MESH': continue
    pkg=ob.get('source_package','')
    is_land=ob.name.startswith('WS_Landscape')
    if not (is_land or '/Cliff/StaticMesh' in pkg or '/Grounds/StaticMesh' in pkg or '/NewCliff' in pkg): continue
    if is_land: matrix=Matrix.Identity(4)
    else:
        record=placements[(ob['source_component'],ob['source_instance'])]
        matrix=Q@Matrix(record['matrix_ue'])@Q;matrix.translation*=.01
    if ob.data.name not in bounds_cache:
        verts=ob.data.vertices
        bounds_cache[ob.data.name]=[(min(v.co[i] for v in verts),max(v.co[i] for v in verts)) for i in range(3)]
    b=bounds_cache[ob.data.name]
    points=[matrix@Vector((x,y,z)) for x in b[0] for y in b[1] for z in b[2]]
    lo=Vector([min(v[i] for v in points) for i in range(3)])
    hi=Vector([max(v[i] for v in points) for i in range(3)])
    if hi.x<25 or lo.x>43 or hi.y<-86 or lo.y>-68 or hi.z<-4 or lo.z>8: continue
    copy=ob.copy();scene.collection.objects.link(copy)
    copy.matrix_world=matrix
    copy.hide_render=False;copy.hide_set(False)
    report.append({'name':ob.name,'source':pkg or ob.get('source',''),
                   'min':list(lo),'max':list(hi),
                   'matrix_world':[list(v) for v in matrix]})
world=bpy.data.worlds.new('JunctionStudyWorld');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.26,.28,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.world=world
ld=bpy.data.lights.new('JunctionStudySun','SUN');ld.energy=2.0;ld.angle=.13
light=bpy.data.objects.new('JunctionStudySun',ld);scene.collection.objects.link(light)
light.rotation_euler=(.45,-.55,-.45)
cd=bpy.data.cameras.new('JunctionStudyCamera');cam=bpy.data.objects.new('JunctionStudyCamera',cd)
scene.collection.objects.link(cam);scene.camera=cam
center=Vector((33.8,-77,3));cam.location=center+Vector((-18,-8,11))
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
cd.type='ORTHO';cd.ortho_scale=16.8;cd.clip_end=200
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=750;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
scene.render.filepath=str(O/'original-layout-ground-rock.png')
bpy.ops.render.render(write_still=True,scene=scene.name)
clay=bpy.data.materials.new('JunctionStudyClay');clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.31,.34,.32,1);bs.inputs['Roughness'].default_value=1
scene.view_layers[0].material_override=clay
scene.render.filepath=str(O/'original-layout-clay.png');bpy.ops.render.render(write_still=True,scene=scene.name)
scene.view_layers[0].material_override=None
(O/'original-layout-evidence.json').write_text(json.dumps({
    'source_blend':str(S/'bamboo-study-editable.blend'),
    'note':'Original recovered meshes, UVs and placements. Plants omitted to inspect contact. Materials and light are prior approximate reconstruction, NOT original runtime rendering.',
    'objects':report},ensure_ascii=False,indent=2),encoding='utf8')
bpy.data.libraries.write(str(O/'junction-inspection.blend'),{scene},path_remap='ABSOLUTE',fake_user=True,compress=True)
bpy.context.window.scene=original
print('JUNCTION_STUDY_COMPLETE',len(report),'objects; formal island was not saved or edited')
