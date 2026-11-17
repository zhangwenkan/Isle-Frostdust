"""Rollback only the unexported interrupted sample build inside Blender MCP."""
import bpy
scene=bpy.data.scenes['Layered_Island_20261116']
col=bpy.data.collections.get('40_Spatial_Foundation')
archive=bpy.data.collections.get('90_Before_Spatial_Foundation')
assert col and archive
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(col)
original=bpy.data.collections['Layered_Island_Authored']
for ob in list(archive.objects):
    archive.objects.unlink(ob);original.objects.link(ob)
    ob.name=ob.name.removeprefix('Before_Space_');ob.hide_render=False;ob.hide_set(False)
bpy.data.collections.remove(archive)
print('Rolled back incomplete sample collection; saved files untouched')
