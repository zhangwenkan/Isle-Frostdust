"""Read/import reference rock geometry in an isolated Blender study scene via MCP."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/bamboo-mist-depth-review/rock-study';O.mkdir(exist_ok=True)
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
D=json.loads((S/'scene-manifest.json').read_text(encoding='utf-8'))
island=bpy.data.scenes['Island_Refined']
scene=bpy.data.scenes.new('Reference_Bamboo_Rocks');bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=650;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('RockStudyWorld');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.14,.17,.15,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.world=w
report=[];objects=[]
for i,n in enumerate(['SM_XYNJiangnan011','SM_XYNJiangnan012','SM_XYNJiangnan037','SM_XYNJiangnan017']):
    e=next(v for k,v in D['meshes'].items() if k.endswith('/'+n+'.uasset'))
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=e['gltf']);added=set(bpy.data.objects)-before
    ob=next(o for o in added if o.type=='MESH');ob.name='Study_'+n
    ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
    lo=Vector([min(v.co[j] for v in ob.data.vertices) for j in range(3)]);hi=Vector([max(v.co[j] for v in ob.data.vertices) for j in range(3)])
    scale=2.9/max(hi.x-lo.x,hi.y-lo.y)
    for v in ob.data.vertices:v.co=(v.co-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)))*scale
    ob.location.x=i*3.7;objects.append(ob)
    mat=bpy.data.materials.new('StudyPaint_'+n);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
    src=D['materials'][e['material_refs'][0]];tex_path=src['textures']['贴图']['png']
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(tex_path,check_existing=True);tex.interpolation='Closest';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    ob.data.materials.clear();ob.data.materials.append(mat)
    report.append(dict(name=n,triangles=e['triangles'],size_gltf_m=e['size_gltf_m'],source=e['gltf'],material=src['source'],base_color=tex_path,normal_source=src['textures']['法线贴图']['source'],study_scaled_width=2.9))
camd=bpy.data.cameras.new('RockStudyCamera');cam=bpy.data.objects.new('RockStudyCamera',camd);scene.collection.objects.link(cam);scene.camera=cam
cam.location=(9,-16,9);target=Vector((5.5,0,.6));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=15.5
ld=bpy.data.lights.new('RockStudyKey','AREA');ld.energy=1400;ld.shape='DISK';ld.size=7
light=bpy.data.objects.new('RockStudyKey',ld);scene.collection.objects.link(light);light.location=(2,-4,9);light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(O/'reference-rocks-textured.png');bpy.ops.render.render(write_still=True,scene=scene.name)
neutral=bpy.data.materials.new('StudyNeutral');neutral.use_nodes=True;neutral.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.25,.29,.26,1);neutral.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
scene.view_layers[0].material_override=neutral;scene.render.filepath=str(O/'reference-rocks-shape.png');bpy.ops.render.render(write_still=True,scene=scene.name);scene.view_layers[0].material_override=None
(O/'reference-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'reference-rocks-study.blend'),copy=True)
bpy.context.window.scene=island
print('REFERENCE_ROCKS_STUDIED',len(report))
