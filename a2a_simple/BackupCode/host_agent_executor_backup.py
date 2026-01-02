import uuid
import httpx
import json
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
from a2a.utils import new_agent_text_message

from openai import AsyncOpenAI


# =========================
# OpenAI setup (classifier)
# =========================

mykey=""
openai_client = AsyncOpenAI(api_key=mykey,timeout=10.0)

async def classify_issue_type(ticket_text: str) -> str:
    """
    Behavior:
      - Classify the issue as hardware or software
      - If hardware issue → return EXACTLY: hardware
      - If software issue → return EXACTLY: software
    """

    prompt = f"""
You are an issue classification engine.

TASK:
Determine whether the incident described is a HARDWARE issue or a SOFTWARE issue.

RULES:
- If the issue involves physical components (servers, disks, memory, CPU, power supply,
  fans, cables, networking hardware, sensors, devices), return EXACTLY: hardware
- If the issue involves applications, operating systems, drivers, firmware logic,
  services, configuration, bugs, crashes, or performance tuning, return EXACTLY: software
- Output must be ONE lowercase word only.
- No explanations, no punctuation, no extra text.

Incident description:
\"\"\"{ticket_text}\"\"\"
"""

    response = await openai_client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.0
    )

    # Extract text safely

    return response.output_text

async def extract_fields(llm, user_input: str):
    prompt = f"""
Extract structured fields from the user input.

Return JSON only.

Fields:
- category (hardware | software | null)
- affected_system (string | null)
- impact (string | null)
- urgency (low | medium | high | critical | null)

User input:
\"\"\"{user_input}\"\"\"
"""
    response = await llm.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    return json.loads(response.output_text)

def find_missing_fields(state: dict):
    missing = []

    if "category" not in state:
        missing.append("category")

    if "affected_system" not in state:
        missing.append("affected_system")

    if "impact" not in state:
        missing.append("impact")

    if "urgency" not in state:
        missing.append("urgency")

    return missing

def build_followup_question(missing_fields):
    questions = {
        "category": "Is this a hardware issue or a software issue?",
        "affected_system": "Which system or component is affected?",
        "impact": "How is this impacting your work or service?",
        "urgency": "How urgent is this (low, medium, high, critical)?",
    }

    return " ".join(questions[f] for f in missing_fields)


# =========================
# Host Agent Executor
# =========================

class HostAgentExecutor(AgentExecutor):
    """
    Orchestrator agent that routes requests to specialist agents.
    """

    def __init__(self):
        self.httpx_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0)
        )
        self._initialized = False

    # -------------------------
    # Initialize downstream agents ONCE
    # -------------------------
    async def _init_agents(self):
        if self._initialized:
            return

        # Fetch agent cards
        hardware_resolver = A2ACardResolver(
            httpx_client=self.httpx_client,
            base_url="http://localhost:9999",
        )
        software_resolver = A2ACardResolver(
            httpx_client=self.httpx_client,
            base_url="http://localhost:9998",
        )

        hardware_card = await hardware_resolver.get_agent_card()
        software_card = await software_resolver.get_agent_card()

        # Create clients
        self.hardware_client = A2AClient(
            httpx_client=self.httpx_client,
            agent_card=hardware_card,
        )
        self.software_client = A2AClient(
            httpx_client=self.httpx_client,
            agent_card=software_card,
        )

        self._initialized = True
        print("HostAgentExecutor initialized downstream agents")

    # -------------------------
    # Build A2A request
    # -------------------------
    def _build_request(self, user_input: str) -> SendMessageRequest:
        return SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    messageId=str(uuid.uuid4()),
                    parts=[Part(root=TextPart(text=user_input))],
                )
            ),
        )

    # -------------------------
    # Main execution
    # -------------------------
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        await self._init_agents()

        user_input = context.get_user_input()
        print(f"[HostAgent] User input: {user_input}")

        # Decide routing
        is_emergency = await classify_issue_type(user_input)
        print(f"[HostAgent] Emergency detected: {is_emergency}")

        if is_emergency == "hardware":
            target_client = self.hardware_client
            print("[HostAgent] Routing to Hardware Agent")
        else:
            target_client = self.software_client
            print("[HostAgent] Routing to Software Agent")
        # Forward request
        response = await target_client.send_message(
            self._build_request(user_input)
        )

        print(f"[HostAgent] Received response: {response}")

        # Extract text safely
        # agent_reply = ""
        # if response.result and response.result.parts:
        #     agent_reply = response.result.parts[0].text
        agent_reply = response.root.result.parts[0].root.text


        # Return response to user
        event_queue.enqueue_event(
            new_agent_text_message(agent_reply)
        )

    # -------------------------
    # Cancel handling
    # -------------------------
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        raise Exception("Cancel not supported")
