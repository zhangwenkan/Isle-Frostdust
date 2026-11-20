"""Remove only our incomplete unsaved independent study after endpoint failure."""
import bpy
s=bpy.data.scenes['Natural_Fracture_Rocks_20261119']
assert not s.get('revision'), 'Saved completed study must never be removed.'
assert set(o.name for o in s.objects)=={'Natural_Rock_01_Main_Block','Natural_Rock_02_Slant_Shoulder','Natural_Rock_03_Projecting_Toe'}
bpy.context.window.scene=bpy.data.scenes['Layered_Island_20261116']
for o in list(s.objects):
    assert len(o.users_scene)==1
    bpy.data.objects.remove(o,do_unlink=True)
bpy.data.scenes.remove(s)
for name in ['Natural_Fracture_Authored','Natural_Fracture_Review_Only']:
    c=bpy.data.collections.get(name)
    if c:
        assert not c.objects
        bpy.data.collections.remove(c)
print('Incomplete unsaved owned scene removed. Saved prior assets and game untouched.')
