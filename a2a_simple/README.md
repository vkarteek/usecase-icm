### Eli Lily POC using A2A and MCP

This README document describes all you need to know about this project - Incident Management System
Below is the flow from 1 to 6 :

# Flow

1. This application contains 3 LLM powered AI agents (Host , Hardware, Software) , a MCP server and a Client
2. The Client ( End User ) routes user tickets to Host Agent ( via A2A) from where ticket is routed to either of Hardware or Software Agents ( again via A2A )
3. The Hardware and Software Agents servers act as MCP clients and connect to the MCP server to handle the tickets :  advise correct tool to MCP server for that ticket
4. MCP server process the ticket with the advised tool and returns response to hardware/software agents
5. Hardware/Software agents returns response to Host Agent
6. Host Agent returns response to Client (End User)


# Diagram  - Above flow can be represented by below architecture 
┌──────────────┐ → ┌────────────────────────┐ → ┌────────────────┐ →  → ┌──────────────┐
│ End User     │   │ Host Agent Server      │   │ Hardware Agent │      │ MCP Server   │
│ (Client.py)  │   │ (9000) [Orchestrator]  │   │ (9999)         │      │ (3000)       │
└──────────────┘   └────────────────────────┘   └────────────────┘      └──────────────┘
                                              → ┌────────────────┐ →  → ┌──────────────┐
                                                │ Software Agent │      │ MCP Server   │  
                                                │ (9998)         │      │ (3000)       │
                                                └────────────────┘      └──────────────┘

# Tech Stack

LLM - OpenAI
AI Agents - Python + a2a-sdk
MCP Server - Node.js + Express
Tools  - MockAPI.io

## Setup and Deployment

### Prerequisites

Before running the application locally, ensure you have the following installed:

1. **uv:** The Python package management tool used in this project. Follow the installation guide: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
2. **python 3.13** Python 3.13 is required to run a2a-sdk 


### FOLLOW BELOW STEPS TO RUN THE APPLICATION ~

# Run Steps 1 , 2 and 4 inside a2a_simple
# Run Step 3 outside a2a_simple

## 1. Install dependencies

This will create a virtual environment in the `.venv` directory and install the required packages.

```bash
uv venv
source .venv/bin/activate
```

Provide OPENAI API KEY inside host_agent_executor and mcp_llm_runner

## 2. Run the Agents
Open a terminal for each of the below 3 AI Agents and run the server the given command in the respective terminal

# Run hardware agent with below command
uv run hardware_server.py

The agent will be running on `http://localhost:9999`.

# Run software agent with below command
uv run software_server.py

The agent will be running on `http://localhost:9998`.

# Run host agent with below command
uv run host_server.py

The agent will be running on `http://localhost:9000`.

## 3. Run the MCP Server

Create a .env file and paste the below env values . Provide the OPENAI API KEY

PORT=4000
MCP_SERVER_URL=http://localhost:3000
OPENAI_API_KEY=""
SOFTWARE_TICKET_API = https://69411fe3686bc3ca8165b797.mockapi.io/incidents
HARDWARE_TICKET_API = https://69411fe3686bc3ca8165b797.mockapi.io/incidentsP

Navigate to the path where server is present and run below -

npm install
node server.js

## 4. Run the Client
Open a new terminal and run the test client:

```bash
uv run --active client.py
```

You will see the client interact with the host agent in the terminal output.
Follow your individual terminals to understand how each server interacts with others

# ======== Multi-turn conversation / Progressive investigation / Slot Filing ==============

Our POC supports to and fro conversation between client and host agent . 
Read below steps to use this feature

1. Any conversation in our POC is uniquely identified by contextId inside the HostAgentExecutor.py
2. This contextId is provided by A2A 
3. For the very first time client does not send any contextId . contextId gets generated from 
   host agent server and is sent inside response to client . From next time onwareds, client send this contextId everytime it gets a followup from host agent . Host agent knows from this contextId that 
   it is the same user continuing the conversation

   New contextId =  New conversation
4. First time client receives below response from host agent
       
    {
      "id": "6ce712a8-824b-433e-8cfb-e1378e34737f",
      "jsonrpc": "2.0",
      "result": {
        "contextId": "jkhjkhjkhjkhjhjhsdefrfr" , # this is the contextId you need to use
        "kind": "message",
        "messageId": "0a597606-955f-4c60-9b07-f8b51864035d",
        "metadata": null,
        "parts": [
          {
            "kind": "text",
            "metadata": null,
            "text": "The status of hardware ticket 30 is pending. The type of issue reported is that the Python installation is failing."
          }
        ],
        "referenceTaskIds": null,
        "role": "agent",
        "taskId": null
      }
    }

5. In Client Code , pass contextId here to continue the conversation ( answer followups )- 

      message_payload = Message(
          role=Role.user,
          messageId=str(uuid.uuid4()),
          parts=[Part(root=TextPart(text="What is the status of hardware ticket 30?"))]
          contextId = "ewewewewe"  # Pass here
      )

# ============================== Local Testing =======================================

We have used MockAPI.io as tools so if MockAPIs are down we need to use local data

1. Fetching Status of Incident

For this uncomment the lines inside fetchHardwareTicket.js and fetchSoftwareTicket.js

2. Creating a new Incident

We cannot test this locally as of now