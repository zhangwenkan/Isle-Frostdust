import bpy,json
print('ACTIVE_BLENDER',json.dumps({'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'scenes':[s.name for s in bpy.data.scenes]}))
