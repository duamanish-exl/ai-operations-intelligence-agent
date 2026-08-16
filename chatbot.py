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

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=""
)


# ============================================================
# CHATBOT TOOLS
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "investigate_complaints",
            "description": "Get complaint data for the current and previous investigation periods.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_billing",
            "description": "Get billing data for the current and previous investigation periods.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_meter",
            "description": "Get meter reading data for the current and previous investigation periods.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_payments",
            "description": "Get payment data for the current and previous investigation periods.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_customer_interactions",
            "description": "Get customer call and interaction data for the current and previous investigation periods.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_account_health",
            "description": "Get account health, vulnerability and financial data for the current and previous investigation periods.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ============================================================
# EXECUTE TOOL
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
    investigation_result,
    periods,
    chat_history=None
):

    if chat_history is None:
        chat_history = []

    system_prompt = """
You are InsightForge, an AI Operations Intelligence assistant.

Answer questions using the investigation result and supplied data context.

RESPONSE STYLE:
- Be extremely concise.
- Answer the question directly.
- Prefer 1-3 short sentences.
- Use bullets when listing more than one item.
- Do not repeat the investigation report.
- Do not explain your reasoning process.
- Do not provide unnecessary background.
- Do not restate the user's question.
- Do not add recommendations unless the user asks for them.
- If the answer is not supported by the available evidence, say:
  "The available evidence does not confirm this."
- Use exact numbers when they are available.
- Keep the answer business-focused.

Examples:

Question:
"Why is billing the likely driver?"

Good:
"Billing is the leading driver because billing-related complaints increased while billing activity also increased during the same period."

Question:
"What should we do first?"

Good:
"First, identify the customers affected by the billing issue and check whether the issue is still ongoing."

Question:
"Give me the key evidence."

Good:
"- Billing complaints increased.
- Billing activity also increased.
- The timing aligns with the complaint increase."

Never produce long paragraphs unless the user explicitly asks for detail.
"""

    # --------------------------------------------------------
    # Base context
    # --------------------------------------------------------

    context_message = {
        "role": "system",
        "content": (
            system_prompt
            + "\n\nCURRENT INVESTIGATION RESULT:\n"
            + json.dumps(
                investigation_result,
                indent=2,
                default=str
            )
            + "\n\nINVESTIGATION PERIODS:\n"
            + json.dumps(
                periods,
                indent=2,
                default=str
            )
        )
    }

    messages = [
        context_message,
        *chat_history[-6:],
        {
            "role": "user",
            "content": question
        }
    ]

    # --------------------------------------------------------
    # First Claude call
    # --------------------------------------------------------

    response = client.chat.completions.create(
        model=os.getenv(
            "OPENROUTER_MODEL",
            "anthropic/claude-sonnet-4.5"
        ),
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # --------------------------------------------------------
    # No tool required
    # --------------------------------------------------------

    if not message.tool_calls:

        return message.content

    # --------------------------------------------------------
    # Add assistant tool request
    # --------------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in message.tool_calls
            ]
        }
    )

    # --------------------------------------------------------
    # Execute tools
    # --------------------------------------------------------

    for tool_call in message.tool_calls:

        tool_name = tool_call.function.name

        try:

            result = execute_tool(
                tool_name,
                periods
            )

        except Exception as e:

            result = {
                "error": str(e)
            }

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    indent=2,
                    default=str
                )
            }
        )

    # --------------------------------------------------------
    # Ask Claude for final answer
    # --------------------------------------------------------

    final_response = client.chat.completions.create(
        model=os.getenv(
            "OPENROUTER_MODEL",
            "anthropic/claude-sonnet-4.5"
        ),
        messages=messages,
    )

    return final_response.choices[0].message.content