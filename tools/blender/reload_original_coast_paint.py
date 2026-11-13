"""Reload authored/CC0-derived paint without rebuilding fitted geometry or UV2."""
import bpy
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/original_coastal_rock'
for image in bpy.data.images:
    if image.source=='FILE' and Path(bpy.path.abspath(image.filepath)).parent==A:
        image.reload()
studio=bpy.data.scenes['Original_Shore_Studio']
bpy.data.libraries.write(str(A/'original_coastal_rock.blend'),{studio},path_remap='ABSOLUTE',fake_user=True,compress=True)
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
