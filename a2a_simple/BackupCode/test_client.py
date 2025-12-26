import uuid

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
from openai import AsyncOpenAI
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




PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
BASE_URL = "http://localhost:9999"
HARDWARE_AGENT_URL = "http://localhost:9999"
SOFTWARE_AGENT_URL = "http://localhost:9998"


timeout = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=10.0,
    pool=30.0,
)

async def main() -> None:
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:
        # Initialize A2ACardResolver
        hardware_resolver = A2ACardResolver(
        httpx_client=httpx_client,
        base_url=HARDWARE_AGENT_URL,
        )

        software_resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=SOFTWARE_AGENT_URL,
        )

        #final_agent_card_to_use: AgentCard | None = None

        try:
            hardware_card = await hardware_resolver.get_agent_card()
            software_card = await software_resolver.get_agent_card()
            print("Fetched public agent cards")
            print(hardware_card.model_dump_json(indent=2))
            print(software_card.model_dump_json(indent=2))

            #final_agent_card_to_use = hardware_card

        except Exception as e:
            print(f"Error fetching public agent card: {e}")
            raise RuntimeError("Failed to fetch public agent card")

        hardware_client = A2AClient(
            httpx_client=httpx_client,
            agent_card=hardware_card,
        )

        software_client = A2AClient(
            httpx_client=httpx_client,
            agent_card=software_card,
        )

        print("A2AClients initialized")
        user_input_text="Hello, Rabbitmq and Postgresql servers are down, need immediate help!"

        
        llm_output = await classify_issue_type(user_input_text)

        print("LLM decision:", llm_output)

        # Choose client based on LLM output
        if llm_output == "hardware":
            client = hardware_client
            print("Routing to Hardware Agent")
        else:
            client = software_client
            print("Routing to Software Agent")

        message_payload = Message(
        role=Role.user,
        messageId=str(uuid.uuid4()),
        parts=[Part(root=TextPart(text=user_input_text))],
        )

    
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message=message_payload,
            ),
        )
        print(f"Sending message to {llm_output} Agent:")

        response = await client.send_message(request)
        print("Response:")
        print(response.model_dump_json(indent=2))
        #print(response.result.parts[0].text)
    



    


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
