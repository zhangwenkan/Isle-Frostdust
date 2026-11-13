"""Reload original paint, bake original module contacts, save sources and fit via MCP."""
import bpy
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/original_coastal_rock'
for image in bpy.data.images:
    if image.source=='FILE' and Path(bpy.path.abspath(image.filepath)).parent==A:
        image.reload()
exec(compile((R/'tools/blender/bake_original_coast_occlusion.py').read_text(encoding='utf8'),'bake_original_coast_occlusion.py','exec'))
studio=bpy.data.scenes['Original_Shore_Studio']
bpy.data.libraries.write(str(A/'original_coastal_rock.blend'),{studio},path_remap='ABSOLUTE',fake_user=True,compress=True)
exec(compile((R/'tools/blender/fit_original_coastal_rock.py').read_text(encoding='utf8'),'fit_original_coastal_rock.py','exec'))
