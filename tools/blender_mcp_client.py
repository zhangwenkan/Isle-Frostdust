"""Call the installed blender-mcp server through the MCP stdio protocol."""
import asyncio
import json
import os
from pathlib import Path
import sys
import shutil
from datetime import timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

UVX = shutil.which("uvx")


async def main():
    env = dict(os.environ)
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env["PYTHONIOENCODING"] = "utf-8"
    port = env.get("BLENDER_PORT", "9877")
    env["BLENDER_PORT"] = port
    if not UVX:
        raise RuntimeError("uvx is required to launch the installed blender-mcp server")
    params = StdioServerParameters(command=UVX, args=["--offline", "--from", "blender-mcp", "blender-mcp", "--port", port], env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=240)) as session:
            await session.initialize()
            action = sys.argv[1] if len(sys.argv) > 1 else "list"
            if action == "list":
                result = await session.list_tools()
                print(json.dumps([{ "name": t.name, "schema": t.inputSchema} for t in result.tools if t.name in ["execute_blender_code", "get_scene_info", "get_viewport_screenshot", "get_object_info"]], indent=2))
                return
            if action == "exec":
                code_path = Path(sys.argv[2])
                tool, arguments = "execute_blender_code", {"code": code_path.read_text(encoding="utf-8")}
            else:
                tool = action
                arguments = json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
            result = await session.call_tool(tool, arguments, read_timeout_seconds=timedelta(seconds=240))
            for content in result.content:
                if content.type == "text":
                    print(content.text)
            if result.isError:
                raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main())
