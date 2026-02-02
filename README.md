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

The MCP server will have some certificate issue while running in Mphasis network , in personal network it won't happen. For Mphasis network , please run below and then run the server .

set NODE_TLS_REJECT_UNAUTHORIZED=0
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
      "id": "263d05c2-5233-4e8f-8795-476f271fdc4e",
      "jsonrpc": "2.0",
      "result": {
        "contextId": null,
        "kind": "message",
        "messageId": "ab16c549-b8cc-44e6-a431-e761b350af39",
        "metadata": {
          "context_id": "70996de0-543d-4f36-899c-c37820131032", # Use this field context_id
          "current_state": {
            "category": "hardware",
            "affected_system": "hardware issue",
            "urgency": "medium"
          }
        },
        "parts": [
          {
            "kind": "text",
            "metadata": null,
            "text": "How is this impacting your work or service?"
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
          parts=[Part(root=TextPart(text="Client is Upset"))]
          contextId = "ewewewewe"  # Pass the context_id value here
      )

# ============================== Local Testing =======================================

We have used MockAPI.io as tools so if MockAPIs are down we need to use local data

1. Fetching Status of Incident

For this uncomment the lines inside fetchHardwareTicket.js and fetchSoftwareTicket.js

2. Creating a new Incident

We cannot test this locally as of now


# Introduction
===========================================
The POC is an AI driven incident management system that can create software and hardware tickets and It can fetch the ticket status .

Features of the Project
  1. It can reduces the manual ticket creation
  2. It can reduce manual intervention for troubleshooting steps using RAG
  3. It can reduce the LLM cost using RAG
  4. Reuses past solution instead of calling LLM every time 
  5. Compatibility by using MCP and A2A
  6. Clear separation of concerns using A2A
  7. Incident Lifecycle Mapping
  
Concepts Used in the project
1.MCP - Model context protocol
  MCP is standardized protocol that allows LLM to  securely interact with tools and resources
  tools - executable actions like DB calls, API calls, ticket creation
  resources- security boundaries (read, write permissions)
In our project we have implemented MCP server with 2 API calls that 
 one is for fetch the available tools from the MCP server and 2nd is to call the particular tool from the mcp server 
mcp will follow a schema. we can reuse this tools any where

2.A2A- Agent to Agent 
A2A is a multi-agent architecture every agent has a separate responsibilities and securely interact with other agents.
In our POC we have 3 agents
Host agent - Orchestrator responsible for gathering the ticket information from client and routes to responsible agent. Don't have access of tools and any db calls or business logic
Software agent - responsible for software related incidents
Hardware agent - responsible for hardware related incidents

3.RAG - Retrieval Augmented Generation
Rag ensures that it can use the past knowledge instead of giving the LLM Hallucination
In the RAG we have used the Pinecone vector db to store and retrieve the data in the form of embeddings.


# ==============================================================
# Flow
# ==============================================================
1. This application contains 3 LLM powered AI agents (Host , Hardware, Software) , a MCP server(Tools), RAG(Pinecone VectorDB) and a Client
2. The Client ( End User ) routes user tickets to Host Agent ( via A2A) from where ticket is routed to either of Hardware or Software Agents ( again via A2A )
3. The Hardware and Software Agents servers act as MCP clients and connect to the MCP server to handle the tickets :  advise correct tool to MCP server for that ticket
4. If LLM selects Create Ticket related tools then only the RAG will perform.
5. If matching issue found in the vectordb it won't call the LLM it can reuse the vectordb solution.
6. If no match found in the vectordb it can call the LLM for solution only and then store the new issue along with solution in the vectordb for future reuse.
4. MCP server process the ticket with the advised tool and returns response to hardware/software agents
5. Hardware/Software agents returns response to Host Agent
6. Host Agent returns response to Client (End User)


# =================== With RAG ======================

┌──────────────┐
│   React UI   │
│  (Frontend)  │
└──────┬───────┘
       │ User raises incident
       ▼
┌────────────────────────┐
│       Host Agent       │
│        (Python)        │
│  - Collect ticket info │
│  - Classify issue type │
│  - NO tools access     │
│  - NO MCP access       │
└──────┬─────────────────┘
       │ Software / Hardware classification
       ▼
┌────────────────────────────────────┐
│  Software Agent / Hardware Agent   │
│              (Python)              │
│  - Domain specific responsibility  │
│  - Has tools + MCP access          │
└──────┬─────────────────────────────┘
       │
       │ Pass available MCP tools
       │ to Agent LLM
       ▼
┌────────────────────────────────────┐
│        Agent LLM (OpenAI)           │
│  - Decides which tool to invoke     │
│  - Has MCP + Tools access           │
└──────┬─────────────────────────────┘
       │
       │ If "Create Ticket" flow
       ▼
┌────────────────────────────────────┐
│     Vector Search Tool (MCP)        │
│        (Search Pinecone)            │
└──────┬─────────────────────────────┘
       │
       │ Similar issue found?
       │
   ┌───┴──────────┐
   │               │
  YES             NO
   │               │
   ▼               ▼
┌────────────┐   ┌────────────────────────────┐
│ Retrieve   │   │ Call LLM for solution  │
│ solution   │   │                            │
│ from       │   └──────────┬─────────────────┘
│ Pinecone   │              │
└────┬───────┘              │
     │                      │
     │                      ▼
     │          ┌────────────────────────────┐
     │          │ Store Issue + Solution      │
     │          │ in Pinecone (via tool)      │
     │          └──────────┬─────────────────┘
     │                     │
     └──────────────┬──────┘
                    ▼
┌────────────────────────────────────┐
│     Create Ticket Tool (MCP)        │
│        (Mock Ticket API)            │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────┐
│ Ticket Created /       │
│ Status Returned        │
└──────┬─────────────────┘
       ▼
┌────────────────────────┐
│      Host Agent        │
└──────┬─────────────────┘
       ▼
┌──────────────┐
│   React UI   │
└──────────────┘  

# Tech Stack

LLM - OpenAI
AI Agents - Python + a2a-sdk
MCP Server - Node.js + Express
VectorDB - Pinecone
Tools  - MockAPI.io
UI Voice- browser’s Web Speech API 
# ======================= RAG==============================
MCP Server (Node.js)
   ├── vectorSearchIncident (Pinecone)
   ├── vectorStoreIncident (Pinecone)
   ├── createSoftwareTicket
   ├── createHardwareTicket
   ├── fetchSoftwareTicket
   └── fetchHardwareTicket
   

   # Run Python pinecone
   uvicorn embedding_service:app --port 9001
# SELF_SIGNED_CERT_IN_CHAIN issue
solution
set NODE_TLS_REJECT_UNAUTHORIZED=0