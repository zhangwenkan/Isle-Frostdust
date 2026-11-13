import bpy
bpy.ops.wm.open_mainfile(filepath='D:/自己做着玩的/孤屿霜尘/assets/island_blender/nameless_island.blend')
print('Restored Blender scene:',bpy.context.scene.name,len(bpy.context.scene.objects))
