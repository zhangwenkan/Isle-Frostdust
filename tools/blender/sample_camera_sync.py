import bpy, math
cam=bpy.data.scenes['Island_Refined'].camera
cam.data.sensor_fit='VERTICAL'
cam.data.sensor_height=24
cam.data.lens=24/(2*math.tan(math.radians(17)))
# Hide the screen-effect plane only in Blender's viewport/render; selection export
# still includes it if a later asset pass is exported.
surface=bpy.data.objects.get('HD2D_Lens_Surface')
if surface:
    surface.hide_render=True
    surface.hide_set(False)
    surface.display_type='WIRE'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Blender review camera matches Godot vertical FOV 34 degrees. Source saved.')
