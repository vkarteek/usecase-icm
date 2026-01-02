import httpx

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.cached_tools = None

    async def list_tools(self):
        async with httpx.AsyncClient(timeout=10) as client:
            # Return cached tools if available
            # do not fetch tools if already cached
            if self.cached_tools is not None:
                return self.cached_tools
            res = await client.post(f"{self.base_url}/tools/list")
            res.raise_for_status()
            self.cached_tools = res.json()["tools"]
            return self.cached_tools

    async def call_tool(self, name: str, arguments: dict):
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                f"{self.base_url}/tools/call",
                json={
                    "name": name,
                    "arguments": arguments
                }
            )
            res.raise_for_status()
            return res.json()
