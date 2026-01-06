import httpx
import asyncio

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cached_tools = None

    async def list_tools(self):
        # Return cached tools if available
        if self.cached_tools is not None:
            return {
                "error": False,
                "tools": self.cached_tools
            }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(f"{self.base_url}/tools/list")

            if resp.status_code != 200:
                return {
                    "error": True,
                    "type": "MCP_HTTP_ERROR",
                    "status": resp.status_code,
                    "message": "Failed to list MCP tools"
                }

            data = resp.json()
            self.cached_tools = data.get("tools", [])

            return {
                "error": False,
                "tools": self.cached_tools
            }

        except httpx.ConnectError:
            return {
                "error": True,
                "type": "MCP_CONNECTION_ERROR",
                "message": "Ticketing system is unreachable"
            }

        except asyncio.TimeoutError:
            return {
                "error": True,
                "type": "MCP_TIMEOUT",
                "message": "Ticketing system timed out"
            }

        except Exception as e:
            return {
                "error": True,
                "type": "MCP_UNKNOWN_ERROR",
                "message": str(e)
            }

    async def call_tool(self, name: str, arguments: dict):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/tools/call",
                    json={
                        "name": name,
                        "arguments": arguments
                    }
                )
                print("Response from MCP:", resp.json())
            if resp.status_code != 200:
                return {
                    "error": True,
                    "type": "MCP_HTTP_ERROR",
                    "status": resp.status_code,
                    "message": "Tool execution failed"
                }

            return {
                "error": False,
                "data": resp.json()
            }

        except httpx.ConnectError:
            return {
                "error": True,
                "type": "MCP_CONNECTION_ERROR",
                "message": "Ticketing system is unreachable"
            }

        except asyncio.TimeoutError:
            return {
                "error": True,
                "type": "MCP_TIMEOUT",
                "message": "Ticketing system timed out"
            }

        except Exception as e:
            return {
                "error": True,
                "type": "MCP_UNKNOWN_ERROR",
                "message": str(e)
            }
