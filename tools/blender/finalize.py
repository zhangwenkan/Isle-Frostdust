import bpy,json
from pathlib import Path
ns=bpy.app.driver_namespace['island_authoring']
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
bpy.ops.object.select_all(action='DESELECT')
scene['asset_workflow']='Blender modeling via blender-mcp; export GLB for Godot; no Godot mesh generation'
scene['gameplay_camera']='Side view, mild downward angle, character medium shot, smooth follow'
for c in scene.collection.children:
    c['description']=c.name.replace('_',' ')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath='D:/自己做着玩的/孤屿霜尘/assets/island_blender/nameless_island.blend')
print('Final Blender source saved, all editing collections retained, gameplay camera view active.')
