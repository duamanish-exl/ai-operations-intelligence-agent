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
            "description": """
            Investigate complaint patterns between the current and previous periods.
            Useful for identifying complaint volume, categories, severity, escalation,
            repeat complaints and patterns that may explain changes in operational KPIs.
            """,
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
            "description": """
            Investigate billing changes between the current and previous periods.
            Useful when billing may explain changes in complaints, customer contacts,
            payments or account health. Focus on bill amounts, estimated billing,
            consumption and billing patterns.
            """,
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
            "description": """
            Investigate meter and consumption patterns between the current and previous
            periods. Useful for estimated readings, meter faults, reading types and
            consumption changes that may explain billing or complaint issues.
            """,
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
            "description": """
            Investigate payment behavior between the current and previous periods.
            Useful for payment failures, cancelled or declined payments and payment
            patterns that may contribute to arrears or customer complaints.
            """,
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
            "description": """
            Investigate customer call and interaction patterns between the current and
            previous periods. Useful for call volume, contact reasons, outcomes,
            teams and interaction patterns related to operational issues.
            """,
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
            "description": """
            Investigate account health and financial risk between the current and previous
            periods. Useful for debt, arrears, vulnerability, collections, payment plans
            and financial-risk indicators.
            """,
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
    You are InsightForge, an AI Operations Intelligence assistant for a UK energy utility.

    Your responses are displayed inside a small website chatbot window.

    RESPONSE LENGTH:
    - Keep every answer concise.
    - Default to 1-3 short sentences.
    - Maximum 60 words unless the user explicitly asks for detail.
    - Answer the user's question directly.
    - Do not repeat the investigation report.
    - Do not provide unnecessary background.
    - Do not expose hidden reasoning or chain-of-thought.

    EVIDENCE RULES:
    - Use the available investigation evidence before making conclusions.
    - Use exact numbers when available.
    - Prefer the strongest 1-2 pieces of evidence.
    - Never invent numbers or facts.
    - Distinguish correlation from causation.
    - Do not claim something is the root cause unless the evidence supports it.
    - If evidence is insufficient, say:
    "The available evidence does not confirm this."

    INVESTIGATION RULES:
    - Use the existing investigation result first.
    - Do not call a tool if the answer is already clearly supported.
    - Call a tool only when additional evidence is needed.
    - Prefer the most relevant investigation tool.
    - Use a second tool when it helps confirm or challenge the leading explanation.
    - Stop investigating when sufficient evidence exists.
    - Never use more than 3 investigation rounds.

    QUESTION STYLE:

    For WHY questions:
    Return:
    Key Finding:
    <root cause>
    Evidence:
    <1-2 strongest supporting metrics>
    Impact:
    <customer/business impact>

    Action:
    <single recommendation>
    Example:
    "Billing is the strongest driver. Billing complaints increased 46% while estimated billing increased 45%. Causation is not confirmed."

    For WHAT CHANGED questions:
    Give the KPI movement and the largest driver.

    Example:
    "Complaint rate increased 23%, mainly driven by billing-related complaints (+46%)."

    For WHAT SHOULD WE DO questions:
    Give the single most important next action.

    Example:
    "Prioritise customers with estimated bills, especially vulnerable or high-debt accounts."

    For simple factual questions:
    Answer directly in one sentence.

    For follow-up questions:
    Use the previous conversation context and answer only the new question.
    Do not repeat information already provided.

    CONFIDENCE:
    - Use high confidence when multiple relevant indicators support the same conclusion.
    - Use medium confidence when evidence is supportive but incomplete.
    - Use low confidence when evidence is weak or conflicting.

    Do not use headings unless they improve readability.
    Do not use tables unless explicitly requested.
    Do not produce long bullet lists unless explicitly requested.

    RESPONSE FORMAT:

    For all investigation questions provide:

    1. Key Finding
    2. Supporting Evidence
    3. Business Impact
    4. Recommended Action

    Keep concise.
    Maximum 80 words.
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
    # ========================================================
    # AGENTIC INVESTIGATION LOOP
    # ========================================================

    model = os.getenv(
        "OPENROUTER_MODEL",
        "anthropic/claude-sonnet-4.5"
    )

    MAX_TOOL_LOOPS = 3

    for _ in range(MAX_TOOL_LOOPS):

        # ----------------------------------------------------
        # Ask the model whether additional investigation
        # is required
        # ----------------------------------------------------

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # ----------------------------------------------------
        # No additional tool required
        # ----------------------------------------------------

        if not message.tool_calls:

            # -----------------------------------------------
            # Final short-answer pass
            # -----------------------------------------------

            final_messages = messages + [
                {
                    "role": "system",
                    "content": """
                    Return ONLY the final chatbot answer.

                    Requirements:
                    - 1-3 short sentences.
                    - Maximum 60 words.
                    - Answer the user's exact question.
                    - Include only the strongest 1-2 pieces of evidence.
                    - Use exact numbers when relevant.
                    - Do not repeat the investigation report.
                    - Do not explain your investigation process.
                    - Do not expose hidden reasoning.
                    - Do not add recommendations unless the user asks for them.
                    """
                }
            ]

            final_response = client.chat.completions.create(
                model=model,
                messages=final_messages,
            )

            return final_response.choices[0].message.content.strip()

        # ----------------------------------------------------
        # Add assistant tool request to conversation
        # ----------------------------------------------------

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
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in message.tool_calls
                ]
            }
        )

        # ----------------------------------------------------
        # Execute requested investigation tools
        # ----------------------------------------------------

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

    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    return "I couldn't confirm the answer from the available evidence."

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