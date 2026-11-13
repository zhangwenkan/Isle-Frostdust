"""Start the installed Blender MCP bridge; no geometry authoring here."""
import bpy, sys
sys.path.insert(0,'C:/Users/51440/AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons')
import blender_mcp
def connect():
    if not hasattr(bpy.types.Scene,'blendermcp_port'):blender_mcp.register()
    server=getattr(bpy.types,'blendermcp_server',None)
    if server and server.running:server.stop()
    bpy.context.scene.blendermcp_port=9881
    bpy.types.blendermcp_server=blender_mcp.BlenderMCPServer(port=9881)
    bpy.types.blendermcp_server.start()
    bpy.context.scene.blendermcp_server_running=True
bpy.app.timers.register(connect,first_interval=1.0)
