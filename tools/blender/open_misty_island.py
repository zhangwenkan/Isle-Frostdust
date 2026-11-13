import bpy
from pathlib import Path
p=Path('D:/自己做着玩的/孤屿霜尘/assets/island_blender/nameless_island.blend')
if Path(bpy.data.filepath)!=p:
    assert not bpy.data.filepath and set(bpy.data.objects.keys())=={'Cube','Camera','Light'}, 'Unexpected Blender document; preserve current scene'
    bpy.ops.wm.open_mainfile(filepath=str(p))
print('MISTY_PROJECT_OPEN',bpy.data.filepath)
