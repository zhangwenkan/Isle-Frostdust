import bpy
from pathlib import Path
ns=bpy.app.driver_namespace['island_authoring']
src=Path('D:/自己做着玩的/孤屿霜尘/tools/blender/foundation.py').read_text(encoding='utf-8')
exec(src[src.index('def texture('):src.index('def mesh(')],ns)
ns['save']()
print('Rebuilt sRGB color textures for correct Blender and Godot brightness.')
