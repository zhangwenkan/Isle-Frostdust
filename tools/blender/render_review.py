import bpy
from pathlib import Path
scene=bpy.data.scenes['Island_Refined']
bpy.context.window.scene=scene
scene.render.engine='CYCLES'
scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=75
scene.render.image_settings.file_format='PNG'
scene.render.filepath='D:/自己做着玩的/孤屿霜尘/artifacts/blender/blender-authoring-review.png'
bpy.ops.render.render(write_still=True)
print('Blender source render saved.')
