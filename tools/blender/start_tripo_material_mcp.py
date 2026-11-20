"""Start only the MCP bridge. All asset authoring is submitted through MCP."""
import bpy, sys
from pathlib import Path
root = Path('D:/自己做着玩的/孤屿霜尘')
sys.stdout = open(root/'artifacts/tripo-replica-review/material-blender-addon.log', 'w', buffering=1, encoding='utf-8')
sys.stderr = sys.stdout
sys.path.insert(0, 'C:/Users/51440/AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons')
import blender_mcp
def connect():
    if not hasattr(bpy.types.Scene, 'blendermcp_port'):
        blender_mcp.register()
    bpy.context.scene.blendermcp_port = 19887
    bpy.types.blendermcp_server = blender_mcp.BlenderMCPServer(host='127.0.0.1', port=19887)
    bpy.types.blendermcp_server.start()
    bpy.context.scene.blendermcp_server_running = True
    print('Material authoring MCP ready:', bpy.data.filepath, flush=True)
bpy.app.timers.register(connect, first_interval=1.0)
