import uvicorn
import asyncio
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from software_agent_executor import SoftwareAgentExecutor


def run_software_agent():

    software_skill = AgentSkill(
        id="Software_Responder",
        name="Software Responder",
        description="Respond to software incident tickets.",
        tags=["software", "incident"],
        examples=["My application is crashing frequently."],
    )

    software_agent_card = AgentCard(
        name="Software Responder",
        description="A simple agent that responds to software incident tickets",
        url="http://localhost:9998/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[software_skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    software_request_handler = DefaultRequestHandler(
        agent_executor=SoftwareAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    software_server = A2AStarletteApplication(
        http_handler=software_request_handler,
        agent_card=software_agent_card,
    )

    uvicorn.run(software_server.build(), host="0.0.0.0", port=9998)


if __name__ == "__main__":
    asyncio.run(run_software_agent())
