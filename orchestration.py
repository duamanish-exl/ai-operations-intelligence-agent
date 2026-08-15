import os
import json

from openai import OpenAI

from kpi import (
    calculate_complaint_rate,
    get_investigation_periods
)

from tools.investigation_tools import (
    investigate_complaints,
    investigate_billing,
    investigate_meter,
    investigate_payments,
    investigate_customer_interactions,
    investigate_account_health
)


# --------------------------------------------------
# OpenRouter client
# --------------------------------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=""
)


# --------------------------------------------------
# Tools available to Claude
# --------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "investigate_complaints",
            "description": (
                "Analyse complaint categories, subcategories, "
                "and complaint patterns between the current "
                "and previous periods."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "investigate_billing",
            "description": (
                "Analyse billing activity, bill amounts "
                "and billing status between the current "
                "and previous periods."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "investigate_meter",
            "description": (
                "Analyse meter readings, reading status "
                "and meter faults."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "investigate_payments",
            "description": (
                "Analyse payment activity, payment status "
                "and payment methods."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "investigate_customer_interactions",
            "description": (
                "Analyse customer calls, contact reasons "
                "and call outcomes."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "investigate_account_health",
            "description": (
                "Analyse account types, vulnerability "
                "and debt status."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# --------------------------------------------------
# Execute a tool
# --------------------------------------------------

def execute_tool(name, periods):

    if name == "investigate_complaints":
        return investigate_complaints(periods)

    if name == "investigate_billing":
        return investigate_billing(periods)

    if name == "investigate_meter":
        return investigate_meter(periods)

    if name == "investigate_payments":
        return investigate_payments(periods)

    if name == "investigate_customer_interactions":
        return investigate_customer_interactions(periods)

    if name == "investigate_account_health":
        return investigate_account_health(periods)

    return {
        "error": "Unknown tool: " + name
    }


# --------------------------------------------------
# Main investigation
# --------------------------------------------------

def run_investigation():

    # Get KPI
    kpi = calculate_complaint_rate()

    # Get investigation periods
    periods = get_investigation_periods()

    # Load investigation prompt
    with open(
        "prompts/agent_prompt.txt",
        "r",
        encoding="utf-8"
    ) as file:
        prompt = file.read()

    # Initial conversation
    messages = [
        {
            "role": "user",
            "content": (
                "Investigate the Complaint Rate.\n\n"
                "Here is the KPI data:\n\n"
                + json.dumps(
                    kpi,
                    indent=2,
                    default=str
                )
            )
        }
    ]

    # Continue until Claude gives a final answer
    while True:

        response = client.chat.completions.create(

            model=os.getenv(
                "OPENROUTER_MODEL",
                "anthropic/claude-sonnet-4.5"
            ),

            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                *messages
            ],

            tools=tools,

            tool_choice="auto"
        )

        message = response.choices[0].message

        # Claude has finished
        if not message.tool_calls:
            return message.content

        # Add Claude's tool request to conversation
        messages.append(
            {
                "role": "assistant",
                "content": message.content,

                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }

                    for call in message.tool_calls
                ]
            }
        )

        # Execute tools requested by Claude
        for call in message.tool_calls:

            try:

                result = execute_tool(
                    call.function.name,
                    periods
                )

            except Exception as e:

                result = {
                    "error": str(e)
                }

            # Send tool result back to Claude
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(
                        result,
                        indent=2,
                        default=str
                    )
                }
            )