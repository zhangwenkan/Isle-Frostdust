import bpy, json
print(json.dumps({'file':bpy.data.filepath, 'dirty':bpy.data.is_dirty, 'version':bpy.app.version_string, 'scenes':[s.name for s in bpy.data.scenes]}))
