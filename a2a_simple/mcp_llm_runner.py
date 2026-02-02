from openai import AsyncOpenAI
import json
#PROVIDE KEY HERE
mykey=""
openai_client = AsyncOpenAI(api_key=mykey,timeout=10.0)
SIMILARITY_THRESHOLD = 0.15


CREATE_TICKET_TOOLS = {
    "create_software_ticket",
    "create_hardware_ticket"
}

async def run_llm_with_mcp_tools(
    user_message: str,
    mcp_client,
    system_prompt: str
) -> str:

    # 1️⃣ Load MCP tools
    tools_result = await mcp_client.list_tools()
    if tools_result.get("error"):
        return "Ticketing system is unavailable. Please try again later."

    tools = tools_result["tools"]

    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["inputSchema"],
            },
        }
        for t in tools
    ]

    # 2️⃣ LLM decides which tool to use
    step1 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        tools=openai_tools,
        tool_choice="auto",
    )

    assistant = step1.choices[0].message

    # 3️⃣ If no tool → return text
    if not assistant.tool_calls:
        return assistant.content or "I couldn’t determine an action."

    tool_call = assistant.tool_calls[0]
    tool_name = tool_call.function.name

    try:
        args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        return "Invalid request parameters."

    # --------------------------------------------------
    # 4️⃣ VECTOR DB LOGIC (ONLY FOR CREATE TICKET TOOLS)
    # --------------------------------------------------

    if tool_name in CREATE_TICKET_TOOLS:

        domain = "software" if "software" in tool_name else "hardware"

        #  Vector search
        search_result = await mcp_client.call_tool(
            "vector_search_incident",
            {
                "query": user_message,
                "domain": domain
            }
        )
        
        data = search_result.get("data", {})
        score = data.get("score", 0)
        solution = data.get("solution")

        print("pinecone score and solution",score,solution)
        
        # Explicit similarity check (DO NOT trust only 'matched')
        is_similar = solution is not None and score >= SIMILARITY_THRESHOLD
        print(" Vector DB Check:", {
            "domain": domain,
            "score": score
            
            })
        # CASE 1: No vector hit → generate + store
        if solution is None:
            solution_prompt = "Provide ONLY the simple and clean solution steps."
            llm_solution = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": solution_prompt},
                    {"role": "user", "content": user_message},
                ],
            )

            solution = llm_solution.choices[0].message.content
            await mcp_client.call_tool(
                "vector_store_incident",
                {
                    "issue": user_message,
                    "solution": solution,
                    "domain": domain
                }
            )
    # CASE 2: Strong match → reuse (NO STORE)
        elif solution is not None and score >= SIMILARITY_THRESHOLD:
            print(" Strong match found — reusing solution")
    # CASE 3: Weak match → reuse (NO STORE)
        else:
            print(" Weak match found — reusing solution (not storing)")
        #  Inject solution into ticket args
        args = {
        "message": user_message,
        "solution": solution,
        "type": domain   # <-- FORCE software / hardware
    }

    # -----------------------------------------
    # 5️⃣ CALL MCP TOOL (CREATE / FETCH / OTHER)
    # -----------------------------------------

    tool_result = await mcp_client.call_tool(tool_name, args)

    if tool_result.get("error"):
        return "Ticketing service is currently unavailable."

    # -----------------------------------------
    # 6️⃣ RETURN FINAL RESPONSE TO USER
    # -----------------------------------------

    data = tool_result.get("data", {})
    content = data.get("content")

    if content and isinstance(content, list):
        return content[0].get("text", "Operation completed.")

    return "Operation completed successfully."
