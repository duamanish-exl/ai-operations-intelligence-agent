import os
import json

from openai import OpenAI

from kpi import calculate_complaint_rate, get_investigation_periods

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
    api_key=" "
)


# --------------------------------------------------
# Available investigation tools
# --------------------------------------------------

tools = [

    {
        "type": "function",
        "function": {
            "name": "investigate_complaints",
            "description": (
                "Investigate complaint categories, subcategories, "
                "severity, channels and root causes. "
                "Use this when complaints themselves need deeper analysis."
            ),
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
            "description": (
                "Investigate billing activity, bill amounts and "
                "billing status to determine whether billing issues "
                "may be contributing to the complaint rate."
            ),
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
            "description": (
                "Investigate meter readings, reading types, "
                "reading status, meter faults and smart meter status "
                "to determine whether meter issues may be contributing "
                "to complaints."
            ),
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
            "description": (
                "Investigate payment activity, payment status and "
                "payment methods to determine whether payment issues "
                "may be contributing to complaints."
            ),
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
            "description": (
                "Investigate customer calls, contact reasons and "
                "call outcomes to identify customer interaction "
                "patterns related to complaints."
            ),
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
            "description": (
                "Investigate account types, vulnerability and debt "
                "status to determine whether customer account health "
                "may be related to the complaint rate."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# --------------------------------------------------
# Execute a Python investigation tool
# --------------------------------------------------

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


# --------------------------------------------------
# Main investigation
# --------------------------------------------------

def run_investigation():

    # ----------------------------------------------
    # 1. Calculate KPI
    # ----------------------------------------------

    kpi_result = calculate_complaint_rate()

    # Get the investigation period once.
    # All tools use these same dates.
    periods = get_investigation_periods()


    # ----------------------------------------------
    # 2. Load investigation prompt
    # ----------------------------------------------

    with open(
        "prompts/agent_prompt.txt",
        "r",
        encoding="utf-8"
    ) as file:

        system_prompt = file.read()


    # ----------------------------------------------
    # 3. Give Claude the KPI
    # ----------------------------------------------

    messages = [
        {
            "role": "user",
            "content": (
                "Investigate the current Complaint Rate.\n\n"
                "Here is the KPI data:\n\n"
                + json.dumps(
                    kpi_result,
                    indent=2,
                    default=str
                )
            )
        }
    ]


    # ----------------------------------------------
    # 4. Investigation loop
    # ----------------------------------------------

    for investigation_number in range(3):

        response = client.chat.completions.create(

            # Set this in your environment.
            # Example:
            # $env:OPENROUTER_MODEL="your-model-id"
            model=os.getenv(
                "OPENROUTER_MODEL",
                "anthropic/claude-sonnet-4.5"
            ),

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                *messages
            ],

            tools=tools,

            tool_choice="auto",

            max_tokens=4000
        )


        message = response.choices[0].message


        # ------------------------------------------
        # 5. Claude has finished
        # ------------------------------------------

        if not message.tool_calls:

            return message.content


        # ------------------------------------------
        # 6. Add Claude's response to conversation
        # ------------------------------------------

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


        # ------------------------------------------
        # 7. Execute requested tools
        # ------------------------------------------

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


            # --------------------------------------
            # 8. Send tool result back to Claude
            # --------------------------------------

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


    # ----------------------------------------------
    # 9. Maximum investigation limit reached
    # ----------------------------------------------

    return (
        "The investigation reached the maximum number "
        "of investigation steps without producing a "
        "final conclusion."
    )