"""Inspect original Wandering Sword cliff assets; run inside Blender via MCP only."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/wandering-cliff-study';O.mkdir(exist_ok=True)
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
D=json.loads((S/'scene-manifest.json').read_text(encoding='utf8'))
old=bpy.context.window.scene
scene=bpy.data.scenes.new('Actual_Shore_Rocks_Study');bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=730;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
w=bpy.data.worlds.new('CliffStudyWorld');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.21,.25,.27,1);w.node_tree.nodes['Background'].inputs[1].default_value=.7;scene.world=w
report=[]
for i,n in enumerate(['SM_XYNJiangnan017','SM_XYNJiangnan001','SM_XYNJiangnan014','SM_XYNJiangnan018']):
 e=next(v for k,v in D['meshes'].items() if k.endswith('/'+n+'.uasset'))
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=e['gltf']);added=set(bpy.data.objects)-before
 ob=next(o for o in added if o.type=='MESH');ob.name='Study_'+n
 ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
 lo=Vector([min(v.co[j] for v in ob.data.vertices) for j in range(3)]);hi=Vector([max(v.co[j] for v in ob.data.vertices) for j in range(3)])
 scale=5.8/max(hi.x-lo.x,hi.y-lo.y)
 for v in ob.data.vertices:v.co=(v.co-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)))*scale
 ob.location.x=i*7.1
 mat=bpy.data.materials.new('Original_'+n);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
 src=D['materials'][e['material_refs'][0]];tex_path=src['textures']['贴图']['png']
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(tex_path,check_existing=True);tex.interpolation='Closest';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 ob.data.materials.clear();ob.data.materials.append(mat)
 uvs=[list(uv.uv) for uv in ob.data.uv_layers.active.data]
 report.append(dict(name=n,triangles=e['triangles'],size_gltf_m=e['size_gltf_m'],source=e['gltf'],material=src['source'],base_color=tex_path,normal_source=src['textures']['法线贴图']['source'],uv_count=len(uvs),bounds_blender=[list(lo),list(hi)]))
 # UV wireframe data allows a direct atlas-overlay proof without editing reference files.
 if i==0:
  polys=[[list(ob.data.uv_layers.active.data[j].uv) for j in p.loop_indices] for p in ob.data.polygons]
  (O/'shore-rock-uv.json').write_text(json.dumps(polys),encoding='utf8')
camd=bpy.data.cameras.new('CliffStudyCamera');cam=bpy.data.objects.new('CliffStudyCamera',camd);scene.collection.objects.link(cam);scene.camera=cam
target=Vector((10.65,0,1.0));cam.location=(13,-34,17);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=28
ld=bpy.data.lights.new('CliffStudySun','SUN');ld.energy=2.2;ld.angle=.15
light=bpy.data.objects.new('CliffStudySun',ld);scene.collection.objects.link(light);light.rotation_euler=(.5,-.4,-.5)
neutral=bpy.data.materials.new('CliffStudyNeutral');neutral.use_nodes=True;neutral.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.30,.32,.29,1);neutral.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
for suffix,override in [('textured',None),('geometry',neutral)]:
 scene.view_layers[0].material_override=override;scene.render.filepath=str(O/('original-shore-rocks-'+suffix+'.png'));bpy.ops.render.render(write_still=True,scene=scene.name)
scene.view_layers[0].material_override=None
(O/'shore-rock-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.data.libraries.write(str(O/'original-shore-rocks-study.blend'),{scene},path_remap='ABSOLUTE',fake_user=True,compress=True)
bpy.context.window.scene=old
print('ACTUAL_CLIFF_STUDY_COMPLETE',len(report))
