import bpy,json
from pathlib import Path
scene=bpy.data.scenes['Fresh_Pixel_Cape']
bpy.context.window.scene=scene
root=Path('D:/自己做着玩的/孤屿霜尘')
out=root/'assets/fresh_pixel_cape'
bpy.ops.object.select_all(action='DESELECT')
objects=[o for o in scene.objects if o.type=='MESH' and o.get('fresh_sample')]
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.gltf(filepath=str(out/'fresh_pixel_cape.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
manifest={'revision':scene['revision'],'source':'empty Blender scene through MCP','imported_geometry':[],'mesh_objects':len(objects),'hero_blender':[-2.7,-1.15,3.16],'top_height':3.13,'stairs':[]}
for ob in objects:
    if '_Tread_' in ob.name:
        verts=[ob.matrix_world@v.co for v in ob.data.vertices]
        manifest['stairs'].append({'name':ob.name,'top':max(v.z for v in verts),'bottom':min(v.z for v in verts)})
(out/'design.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'fresh_pixel_cape.blend'))
print(json.dumps(manifest))
