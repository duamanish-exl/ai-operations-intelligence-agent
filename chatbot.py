import os
import json

from openai import OpenAI

from tools.investigation_tools import (
    investigate_complaints,
    investigate_billing,
    investigate_meter,
    investigate_payments,
    investigate_customer_interactions,
    investigate_account_health,
)


# ============================================================
# OPENROUTER CLIENT
# ============================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set."
    )

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "anthropic/claude-sonnet-4.5",
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY.strip(),
)


# ============================================================
# CHATBOT TOOLS
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "investigate_complaints",
            "description": (
                "Get complaint data for the selected "
                "investigation period and comparison period."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_billing",
            "description": (
                "Get billing data for the selected "
                "investigation period and comparison period."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_meter",
            "description": (
                "Get meter data for the selected "
                "investigation period and comparison period."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_payments",
            "description": (
                "Get payment data for the selected "
                "investigation period and comparison period."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_customer_interactions",
            "description": (
                "Get customer interaction data for the selected "
                "investigation period and comparison period."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_account_health",
            "description": (
                "Get account health, vulnerability and financial "
                "data for the selected investigation period and "
                "comparison period."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(tool_name, periods):

    if tool_name == "investigate_complaints":
        return investigate_complaints(periods)

    if tool_name == "investigate_billing":
        return investigate_billing(periods)

    if tool_name == "investigate_meter":
        return investigate_meter(periods)

    if tool_name == "investigate_payments":
        return investigate_payments(periods)

    if tool_name == "investigate_customer_interactions":
        return investigate_customer_interactions(periods)

    if tool_name == "investigate_account_health":
        return investigate_account_health(periods)

    return {
        "error": f"Unknown tool: {tool_name}"
    }


# ============================================================
# CHAT FUNCTION
# ============================================================

def ask_chatbot(
    question,
    investigation_result=None,
    periods=None,
    chat_history=None,
):
    """
    Answer a user question using the active investigation context.

    The chatbot can:
    - answer from the existing investigation result
    - query investigation tools for more evidence
    - remember the last few chat turns
    """

    if chat_history is None:
        chat_history = []

    if periods is None:
        periods = {}

    if investigation_result is None:
        investigation_context = (
            "There is currently no completed investigation. "
            "The user may still ask general questions, but do not "
            "pretend that investigation-specific evidence exists."
        )
    else:
        investigation_context = (
            "CURRENT INVESTIGATION RESULT:\n"
            + json.dumps(
                investigation_result,
                indent=2,
                default=str,
            )
        )

    system_prompt = """
You are InsightForge, an AI Operations Intelligence assistant
for a UK Utility company.

You sit alongside the KPI investigation dashboard.

Your job is to answer the user's operational questions using:
1. The active investigation result.
2. The selected investigation and comparison periods.
3. Investigation tools when additional evidence is needed.

RESPONSE STYLE
- Be concise.
- Answer directly.
- Prefer 1-4 short sentences.
- Use bullets for multiple items.
- Do not repeat the entire investigation.
- Do not restate the question.
- Do not invent facts.
- Use exact numbers when available.
- Distinguish observed evidence from interpretation.
- Do not claim causation when evidence only supports correlation.
- Only recommend actions when the user asks for them.
- If the available evidence does not answer the question, say:
  "The available evidence does not confirm this."

INVESTIGATION CONTEXT
- Treat the supplied selected period as authoritative.
- Treat the supplied comparison period as authoritative.
- When using an investigation tool, use those periods.
"""

    context_message = {
        "role": "system",
        "content": (
            system_prompt
            + "\n\n"
            + investigation_context
            + "\n\nINVESTIGATION PERIODS:\n"
            + json.dumps(
                periods,
                indent=2,
                default=str,
            )
        ),
    }

    messages = [
        context_message,
        *chat_history[-8:],
        {
            "role": "user",
            "content": question,
        },
    ]

    # --------------------------------------------------------
    # First model call
    # --------------------------------------------------------

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1200,
        )
    except Exception as exc:
        error_text = str(exc)

        if "401" in error_text or "User not found" in error_text:
            raise RuntimeError(
                "OpenRouter authentication failed. "
                "Check OPENROUTER_API_KEY."
            ) from exc

        raise

    message = response.choices[0].message

    # --------------------------------------------------------
    # No tools required
    # --------------------------------------------------------

    if not message.tool_calls:

        return (
            message.content or
            "I could not produce an answer."
        )

    # --------------------------------------------------------
    # Save assistant tool request
    # --------------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in message.tool_calls
            ],
        }
    )

    # --------------------------------------------------------
    # Execute requested tools
    # --------------------------------------------------------

    for tool_call in message.tool_calls:

        try:
            tool_result = execute_tool(
                tool_call.function.name,
                periods,
            )

        except Exception as exc:

            tool_result = {
                "error": str(exc),
            }

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    tool_result,
                    indent=2,
                    default=str,
                ),
            }
        )

    # --------------------------------------------------------
    # Final answer
    # --------------------------------------------------------

    try:
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tool_choice="none",
            max_tokens=1200,
        )
    except Exception as exc:
        error_text = str(exc)

        if "401" in error_text or "User not found" in error_text:
            raise RuntimeError(
                "OpenRouter authentication failed. "
                "Check OPENROUTER_API_KEY."
            ) from exc

        raise

    return (
        final_response.choices[0].message.content
        or "I could not produce an answer."
    )
