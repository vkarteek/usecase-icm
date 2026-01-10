import uvicorn
from starlette.middleware.cors import CORSMiddleware
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from host_agent_executor import HostAgentExecutor


def run_host_agent():
        host_skill = AgentSkill(
        id="host_router",
        name="Host Router",
        description="Routes user requests to the correct specialist agent",
        tags=["router", "orchestrator", "gateway"],
        examples=[
            "My laptop won't turn on",
            "My keyboard is not working",
            "Python installation is failing",
        ],
    )


        host_agent_card = AgentCard(
        name="Host Agent",
        description="An orchestrator agent that routes requests to specialist agents",
        url="http://localhost:9000/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[host_skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )


        host_request_handler = DefaultRequestHandler(
            agent_executor=HostAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )

        host_server = A2AStarletteApplication(
            http_handler=host_request_handler,
            agent_card=host_agent_card,
        )
        # 🔑 BUILD ASGI APP
        app = host_server.build()
    
        # ✅ ENABLE CORS HERE
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3001"],  # React app
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        uvicorn.run(app, host="0.0.0.0", port=9000)


if __name__ == "__main__":
    run_host_agent()
