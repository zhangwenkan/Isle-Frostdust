"""Connection bootstrap only. All modeling is submitted via blender-mcp."""
import bpy,sys
sys.path.insert(0,r'C:\Users\51440\AppData\Roaming\Blender Foundation\Blender\5.1\scripts\addons')
import blender_mcp
if not hasattr(bpy.types.Scene,'blendermcp_port'):
    blender_mcp.register()
bpy.context.scene.blendermcp_port=9878
bpy.context.scene.blendermcp_auto_start_server=True
def start_bridge():
    blender_mcp._blendermcp_ensure_server_running()
    return None
bpy.app.timers.register(start_bridge,first_interval=1.0)

