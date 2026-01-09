from openai import AsyncOpenAI
import json
#PROVIDE KEY HERE
mykey=""
openai_client = AsyncOpenAI(api_key=mykey,timeout=10.0)

async def run_llm_with_mcp_tools(
    user_message: str,
    mcp_client,
    system_prompt: str
) -> str:
    # 1️⃣ Load MCP tools safely
    tools_result = await mcp_client.list_tools()
    #print("Tools Result while calling:", tools_result)

    if tools_result["error"]:
        return (
            "I’m unable to access the ticketing system right now. "
            "Please try again later."
        )

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

    # 2️⃣ First LLM call (tool selection)
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

    # 3️⃣ No tool requested → return LLM answer
    if not assistant.tool_calls:
        return assistant.content or "I couldn’t determine an action to take."

    # 4️⃣ Tool requested
    tool_call = assistant.tool_calls[0]
    tool_name = tool_call.function.name

    try:
        args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        return "I couldn’t understand the request parameters. Please try again."

    tool_result = await mcp_client.call_tool(tool_name, args)

    # 🚨 MCP FAILURE HANDLING
    if tool_result["error"]:
        return (
            "I tried to access the ticketing system, but it’s currently unavailable. "
            "Please try again later or contact support if this is urgent."
        )
    print("Tool Result after calling:", tool_result["data"])
    # 5️⃣ Final LLM call with tool output
    step2 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
            assistant,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result["data"]),
            },
        ],
    )

    return step2.choices[0].message.content or "Operation completed."
