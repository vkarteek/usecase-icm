import logging

logger = logging.getLogger("host_agent")
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

async def analyze_rootagent_error(
    llm_client,
    error_message: str,
    error_type: str,
    agent_type: str
) -> None:
    """
    Host Agent diagnostic function.

    Parameters:
    - llm_client: LLM client instance
    - error_message: Raw error string
    - error_type: High-level error classification (CONNECTIVITY, TIMEOUT, GETTING_AGENT_CARD, etc.)
    - agent_type: Either explicit agent type ('hardware', 'software', 'specialist', 'host') 
                  or ambiguous ('may be either software or hardware')
    
    The LLM will infer agent_type if it is ambiguous and log full diagnostics.
    """

    logger.error(
        "Host Agent caught error | Agent: %s | Type: %s | Message: %s",
        agent_type,
        error_type,
        error_message
    )

    # Include instruction for agent_type inference if ambiguous
    agent_instruction = (
        "If the agent_type is ambiguous, infer the correct agent type "
        "from the error message."
        if agent_type.lower() in ["may be either software or hardware", "ambiguous"]
        else f"The agent type is {agent_type}."
    )

    prompt = f"""
You are an expert incident-response engineer assisting an AI Host Agent.

Analyze the error below and provide:
1. Issue summary
2. Likely root cause
3. Category (Hardware, Software, Network, Configuration, External Dependency)
4. Troubleshooting steps (numbered)
5. Recommended host-agent action (retry, fallback, escalate, log-only)
6. If agent type was ambiguous, specify the most probable agent type based on the error message.

Error type: {error_type}
Agent type: {agent_type}
{agent_instruction}
Error message:
\"\"\"{error_message}\"\"\"

Keep the response concise and actionable.
"""

    try:
        response = await llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You analyze agent and system failures."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        logger.info(
            "LLM Diagnostic Analysis | Provided agent_type: %s | Error type: %s\n%s",
            agent_type,
            error_type,
            response.choices[0].message.content
        )

    except Exception as llm_error:
        logger.warning(
            "LLM analysis failed | Agent: %s | Type: %s | Error: %s",
            agent_type,
            error_type,
            str(llm_error)
        )
