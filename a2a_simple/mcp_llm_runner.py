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
    # 1. Load MCP tools
    tools = await mcp_client.list_tools()

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

    # 2. First LLM call
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

    # 3. No tool requested
    if not assistant.tool_calls:
        return assistant.content

    # 4. Tool requested
    tool_call = assistant.tool_calls[0]
    tool_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments or "{}")

    tool_result = await mcp_client.call_tool(tool_name, args)

    # 5. Final LLM call with tool output
    step2 = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
            assistant,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            },
        ],
    )

    return step2.choices[0].message.content
