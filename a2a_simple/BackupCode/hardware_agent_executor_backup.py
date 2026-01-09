from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel

from openai import AsyncOpenAI
mykey=""
openai_client = AsyncOpenAI(api_key=mykey,timeout=10.0)

async def respond_hardware_incident(ticket_text: str) -> str:
    """
    Behavior:
      - Always treat input as a hardware incident ticket
      - Return EXACTLY 4 sentences:
            1. Potential cause of the issue
            2. Severity of the issue
            3. Fix or remediation plan
            4. Estimated time to resolve
    """

    prompt = f"""
You are a senior hardware engineer handling infrastructure incident tickets.

TASK:
Analyze the hardware incident ticket and produce a STRICTLY FORMATTED response.

OUTPUT RULES:
- Respond with EXACTLY 4 English sentences.
- Sentence 1: Describe the most likely hardware-related cause of the issue.
- Sentence 2: Clearly state the severity (Low, Medium, High, or Critical).
- Sentence 3: Explain what action will be taken to fix the issue.
- Sentence 4: Estimate the time required to resolve the problem.
- No numbering, no bullet points, no extra explanations, no headers.

Hardware incident ticket:
\"\"\"{ticket_text}\"\"\"
"""

    response = await openai_client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.2
    )

    # Safe extraction of output text
    return response.output_text


class HardwareAgent(BaseModel):
    """Hardware agent that responds to hardware incidents"""

    async def invoke(self, user_input_text: str) -> str:
        response = await respond_hardware_incident(user_input_text)
        print(response)
        return response


class HardwareAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = HardwareAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        print("Executing HardwareAgentExecutor")
        print(f"Context is {context.get_user_input()}")
        user_input_text = context.get_user_input() # or whatever field holds the user text

        result = await self.agent.invoke(user_input_text)
        event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")
