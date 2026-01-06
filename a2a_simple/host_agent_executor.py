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
from a2a.types import Message, Part, TextPart, Role

from openai import AsyncOpenAI
from host_state import HostConversationState
import asyncio

# =========================
# OpenAI setup (classifier)
# =========================

#PROVIDE KEY HERE
OPENAI_API_KEY = ""
openai_client = AsyncOpenAI(api_key= OPENAI_API_KEY,timeout=10.0)


async def extract_fields(llm, user_input: str):
    prompt = f"""
    You are a STRICT classifier.

    FIRST decide intent.

    If the user is asking for status, update, progress, or mentions a ticket number,
    respond with EXACTLY one of these strings and NOTHING ELSE:
    - hardware_update
    - software_update

    DO NOT return JSON in that case.

    ONLY IF it is NOT an update request, then return JSON EXACTLY in this format:

    {{
    "category": "hardware|software|null",
    "affected_system": string|null,
    "impact": string|null,
    "urgency": "low|medium|high|critical|null"
    }}

    User input:
    \"\"\"{user_input}\"\"\"
    """

    response = await llm.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    text = response.output_text.strip()

    if text in ("hardware_update", "software_update"):
        return text

    return json.loads(text)

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
        self.state_store = HostConversationState()
        self.llm = openai_client

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
        # Error handling for fetching agent cards of downstream agents
        try:
            await self._init_agents()
        except httpx.ConnectError:
            # Return response to user
            event_queue.enqueue_event(
                new_agent_text_message("We are facing connectivity issues with our specialist agents. Please try again later.")
            )
            return
        
        except asyncio.TimeoutError:
            event_queue.enqueue_event(
                new_agent_text_message("Our specialist agents are taking longer than expected to respond. Please try again later.")
            )
            return

        except Exception as e:
            event_queue.enqueue_event(
                new_agent_text_message("An unexpected error occurred. Please try again later.")
            )
            return

        context_id = context.context_id
        print(f"[HostAgent] Context ID: {context_id}")
        user_input = context.get_user_input()
        # Load existing state
        state = self.state_store.get(context_id)
        print(f"[HostAgent] User input: {user_input}")

         # Extract new fields
        extracted = await extract_fields(self.llm, user_input)

        if extracted == "hardware_update" or extracted == "software_update":
            # Forward request to both agents for status update

            target_client = None
            if extracted == "hardware_update":  
                target_client = self.hardware_client
                print("[HostAgent] Routing status update to Hardware Agent")
            else:
                target_client = self.software_client
                print("[HostAgent] Routing status update to Software Agent")

            # Error handling for fetching incident status from target agent    
            try:
                agent_status_response = await target_client.send_message(
                    self._build_request(user_input)
                )

                # Extract replies
                agent_status_reply = agent_status_response.root.result.parts[0].root.text

                # Return combined response to user
                event_queue.enqueue_event(
                    new_agent_text_message(agent_status_reply)
                )
                return
            except httpx.ConnectError:
            # Return response to user
                event_queue.enqueue_event(
                    new_agent_text_message("We are facing connectivity issues with our specialist agents. Please try again later.")
                )


            except asyncio.TimeoutError:
                event_queue.enqueue_event(
                    new_agent_text_message("Our specialist agents are taking longer than expected to respond. Please try again later.")
                )

            except Exception as e:
                event_queue.enqueue_event(
                    new_agent_text_message("An unexpected error occurred. Please try again later.")
                )
        # Update state
        state = self.state_store.update(context_id, {
            k: v for k, v in extracted.items() if v
        })

        # Check missing fields
        missing = find_missing_fields(state)

        if missing:
            followup = build_followup_question(missing)
            event_queue.enqueue_event(
            Message(
                role=Role.agent,
                messageId=str(uuid.uuid4()),
                parts=[
                Part(
                    root=TextPart(text=followup)
                )
                ],
                metadata={
                "context_id": context.context_id,
                "current_state": self.state_store.get(context_id)
                }
            )
            )
            return

        # All info collected → ROUTE
        category = state["category"] or "software"  # Default to software

        self.state_store.clear(context_id)

        # Decide routing

        if category == "hardware":
            target_client = self.hardware_client
            print("[HostAgent] Routing to Hardware Agent")
        else:
            target_client = self.software_client
            print("[HostAgent] Routing to Software Agent")
        # Compose user problem and Forward request
        user_issue=f"My type of issue is {state['category']} . My ugency is {state['urgency']} . My affected system is {state['affected_system']} . My impact is {state['impact']} ."

        # Error handling for sending incident details to target agent    
        try:
            response = await target_client.send_message(
                self._build_request(user_issue)
            )

            agent_reply = response.root.result.parts[0].root.text


            # Return response to user
            event_queue.enqueue_event(
                new_agent_text_message(agent_reply)
            )
        except httpx.ConnectError:
            # Return response to user
            event_queue.enqueue_event(
                new_agent_text_message("We are facing connectivity issues with our specialist agents. Please try again later.")
            )


        except asyncio.TimeoutError:
            event_queue.enqueue_event(
                new_agent_text_message("Our specialist agents are taking longer than expected to respond. Please try again later.")
            )

        except Exception as e:
            event_queue.enqueue_event(
                new_agent_text_message("An unexpected error occurred. Please try again later.")
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
