import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
REF=Path('D:/steam/steamapps/common/I Just Wanted to Fish Demo/analysis/exported_all')
original=bpy.context.scene
scene=bpy.data.scenes.get('Fish_Reference_Study') or bpy.data.scenes.new('Fish_Reference_Study')
bpy.context.window.scene=scene
for ob in list(scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
def mat(name,texture,alpha=False):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.9
 image=bpy.data.images.load(str(REF/'textures'/texture),check_existing=True)
 t=n.new('ShaderNodeTexImage');t.image=image
 m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if alpha:m.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha'])
 return m
leaf=mat('REF_Leaf','T_Leaves_619.png',True)
report=[]
for j,(file,texture) in enumerate([('Tree_A_3939.obj','T_Tree_A_Albedo_481.png'),('Tree_B_5160.obj','T_Tree_B_Albedo_475.png'),('Rock_A_4518.obj','T_Rock_A_Albedo_667.png'),('Rock_B_4192.obj','T_Rock_B_Albedo_460.png'),('Rock_C_3602.obj','T_Rock_C_Albedo_564.png')]):
 bpy.ops.wm.obj_import(filepath=str(REF/'meshes'/file),forward_axis='NEGATIVE_Z',up_axis='Y',use_split_objects=False,use_split_groups=True)
 material=mat('REF_'+file.split('_')[0]+'_'+str(j),texture)
 for ob in bpy.context.selected_objects:
  ob.location.x+=(-4 if j==0 else 3 if j==1 else (j-2)*3-4)
  ob.location.y+=0 if j<2 else -3.5
  ob.data.materials.clear();ob.data.materials.append(leaf if j<2 and ob.name.endswith('_0') else material)
  report.append({'name':ob.name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'bounds':[list(v) for v in ob.bound_box],'material':ob.data.materials[0].name})
bpy.ops.mesh.primitive_plane_add(size=200)
ground=bpy.context.object;ground.location.z=-.22
m=bpy.data.materials.new('REF_Background');m.diffuse_color=(.19,.28,.14,1);ground.data.materials.append(m)
world=bpy.data.worlds.new('REF_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.75,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.world=world
sun_data=bpy.data.lights.new('REF_Sun','SUN');sun_data.energy=2;sun_data.angle=.08
sun=bpy.data.objects.new('REF_Sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(.3,-.4,-.6)
cam_data=bpy.data.cameras.new('REF_Camera');cam=bpy.data.objects.new('REF_Camera',cam_data);scene.collection.objects.link(cam)
cam.location=(10,-23,14);target=Vector((0,0,2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.type='ORTHO';cam_data.ortho_scale=18;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'artifacts/fish-style-review/reference-models.png')
(ROOT/'artifacts/fish-style-review/reference-mesh-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.render.render(write_still=True)
bpy.context.window.scene=original
print('Reference models inspected and rendered; original island unchanged.')
