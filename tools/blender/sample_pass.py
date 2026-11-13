"""Execute via blender-mcp. Explicitly composed sample assets, editable in Blender."""
import bpy
from pathlib import Path
ns=bpy.app.driver_namespace['island_authoring']
exec(compile(Path('D:/自己做着玩的/孤屿霜尘/tools/blender/sample_pass_body.py').read_text(encoding='utf-8'),'sample_pass_body.py','exec'),ns)
