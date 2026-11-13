"""Bake contact shading from the five original module meshes in Blender via MCP."""
import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/original_coastal_rock';O=R/'artifacts/original-shore-review';old=bpy.context.window.scene
s=bpy.data.scenes['Original_Shore_Studio'];bpy.context.window.scene=s;s.render.engine='CYCLES';s.cycles.samples=24
objects=[o for o in s.objects if o.type=='MESH'];images=[]
for prefix,size in [('Side',(2048,1024)),('Top',(1024,1024))]:
 img=bpy.data.images.new('OriginalCoastAO_'+prefix,width=size[0],height=size[1],alpha=False);img.generated_color=(1,1,1,1);img.colorspace_settings.name='Non-Color';images.append(img)
for ob in objects:
 for mat in ob.data.materials:
  if mat is None:continue
  image=images[1 if 'Top' in mat.name else 0]
  node=mat.node_tree.nodes.get('ContactBake') or mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='ContactBake';node.image=image
  mat.node_tree.nodes.active=node
s.render.bake.use_clear=False;s.render.bake.margin=8;s.render.bake.target='IMAGE_TEXTURES';s.world.color=(1,1,1)
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.bake(type='AO')
for im,suffix in zip(images,['sides','tops']):im.filepath_raw=str(A/('rock_contact_'+suffix+'.png'));im.file_format='PNG';im.save()
bpy.context.window.scene=old
print('ORIGINAL_CONTACT_BAKED')
