from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message

from mcp_client import MCPClient
from mcp_llm_runner import run_llm_with_mcp_tools


MCP_SERVER_URL = "http://localhost:3000"
SYSTEM_PROMPT = """
IMPORTANT RULES FOR HARDWARE TICKETS:
- Use ONLY hardware tools.
- Laptop, mouse, keyboard, charger, display, etc.
- Always show ticket ID.
"""

class HardwareAgentExecutor(AgentExecutor):
    def __init__(self):
        self.mcp_client = MCPClient(MCP_SERVER_URL)

    async def execute(self, context, event_queue):
        user_input = context.get_user_input()

        result = await run_llm_with_mcp_tools(
            user_message=user_input,
            mcp_client=self.mcp_client,
            system_prompt=SYSTEM_PROMPT,
        )

        event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context, event_queue):
        pass
