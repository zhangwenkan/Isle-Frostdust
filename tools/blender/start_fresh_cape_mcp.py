"""Start a dedicated blank Blender session. No asset authoring happens here."""
import importlib.util
import pathlib
import bpy

addon_path = pathlib.Path.home() / 'AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons/blender_mcp.py'
spec = importlib.util.spec_from_file_location('blender_mcp', addon_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.register()
bpy.context.scene.blendermcp_port = 19887
bpy.context.scene.blendermcp_auto_start_server = False
bpy.types.blendermcp_server = module.BlenderMCPServer(host='127.0.0.1', port=19887)
bpy.types.blendermcp_server.start()
bpy.context.scene.blendermcp_server_running = True
print('FRESH_CAPE_MCP_READY port=19887')
