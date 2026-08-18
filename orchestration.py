import os
import json
from pathlib import Path

from openai import OpenAI

from kpi import (
    calculate_complaint_rate,
    get_investigation_periods,
)

from tools.investigation_tools import (
    investigate_complaints,
    investigate_billing,
    investigate_meter,
    investigate_payments,
    investigate_customer_interactions,
    investigate_account_health,
)


# ============================================================
# CONFIG
# ============================================================

OPENROUTER_API_KEY = ""
if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. "
        "Set it in the same terminal used to start Streamlit."
    )

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "anthropic/claude-sonnet-4.5",
)

MAX_INVESTIGATION_STEPS = int(
    os.getenv("MAX_INVESTIGATION_STEPS", "3")
)

PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "agent_prompt.txt"
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY.strip(),
)


# ============================================================
# TOOLS
# ============================================================

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
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "investigate_billing",
            "description": (
                "Analyse billing activity, bill amounts, "
                "billing trends, and billing anomalies."
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
                "Analyse meter readings, reading status, "
                "consumption patterns, and meter faults."
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
                "Analyse payment activity, failed payments, "
                "payment status, and payment methods."
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
                "Analyse customer calls, contact reasons, "
                "call outcomes, and customer interaction trends."
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
                "Analyse account types, balances, arrears, "
                "vulnerability, and debt status."
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
        "error": f"Unknown tool: {name}"
    }


# ============================================================
# PROMPT
# ============================================================

def load_prompt():
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    return PROMPT_PATH.read_text(
        encoding="utf-8"
    )


# ============================================================
# JSON PARSING
# ============================================================

def parse_json_response(content):
    if not content:
        raise RuntimeError(
            "Claude returned an empty response."
        )

    text = content.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Claude did not return valid JSON.\n\n"
            f"Response:\n{text}"
        ) from exc

    if not isinstance(result, dict):
        raise RuntimeError(
            "Claude returned JSON, but the result was not an object."
        )

    return result


# ============================================================
# VALIDATION
# ============================================================

REQUIRED_FIELDS = [
    "kpi",
    "previous_value",
    "current_value",
    "unit",
    "absolute_change",
    "relative_change_pct",
    "direction",
    "severity",
    "executive_summary",
    "primary_root_cause",
    "secondary_factors",
    "watch_items",
    "recommended_actions",
    "supporting_evidence",
    "confidence",
    "investigation_timeline",
    "final_conclusion",
]


def validate_result(result):
    missing = [
        field
        for field in REQUIRED_FIELDS
        if field not in result
    ]

    if missing:
        raise RuntimeError(
            "Investigation result is missing fields: "
            + ", ".join(missing)
        )

    for field in (
        "secondary_factors",
        "watch_items",
        "recommended_actions",
        "supporting_evidence",
        "investigation_timeline",
    ):
        if not isinstance(result[field], list):
            result[field] = []

    if not isinstance(result["confidence"], dict):
        result["confidence"] = {}

    return result


# ============================================================
# OPENROUTER CALL
# ============================================================

def call_model(messages, *, use_tools=True, force_json=False):
    try:
        kwargs = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 4500,
        }

        if use_tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        else:
            kwargs["tool_choice"] = "none"
            if force_json:
                kwargs["response_format"] = {"type": "json_object"}

        try:
            return client.chat.completions.create(**kwargs)
        except Exception:
            if force_json and "response_format" in kwargs:
                kwargs.pop("response_format", None)
                return client.chat.completions.create(**kwargs)
            raise

    except Exception as exc:
        error_text = str(exc)

        if "401" in error_text or "User not found" in error_text:
            raise RuntimeError(
                "OpenRouter authentication failed. "
                "Check OPENROUTER_API_KEY and the OpenRouter account."
            ) from exc

        raise


# ============================================================
# FINAL JSON SYNTHESIS
# ============================================================

def synthesize_final_json(prompt, messages):
    final_messages = [
        {
            "role": "system",
            "content": (
                prompt
                + "\n\nFINAL RESPONSE ENFORCEMENT:\n"
                + "Return ONLY the required JSON object. "
                  "Do not return Markdown, headings, prose, emojis, "
                  "or code fences. The response must start with { "
                  "and end with }."
            ),
        },
        *messages,
        {
            "role": "user",
            "content": (
                "The investigation is complete. Using only the evidence "
                "collected above, return the final result as the exact JSON "
                "object required by the system prompt."
            ),
        },
    ]

    response = call_model(
        final_messages,
        use_tools=False,
        force_json=True,
    )

    return parse_json_response(
        response.choices[0].message.content
    )


# ============================================================
# MAIN INVESTIGATION
# ============================================================

def run_investigation(
    start_period,
    end_period,
    action_audience="General / Business"
):
    """
    Run a Complaint Rate investigation for the selected period.

    The comparison period is automatically calculated as the
    immediately preceding period of equal duration.
    """

    prompt = load_prompt()

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    kpi = calculate_complaint_rate(
        start_period=start_period,
        end_period=end_period,
    )

    # --------------------------------------------------------
    # PERIODS
    # --------------------------------------------------------

    periods = get_investigation_periods(
        start_period=start_period,
        end_period=end_period,
    )

    # --------------------------------------------------------
    # INITIAL MESSAGE
    # --------------------------------------------------------

    messages = [
        {
            "role": "user",
            "content": (
                "Investigate the Complaint Rate.\n\n"

                "Selected investigation period:\n"
                f"{periods['current_start'].date()} "
                f"to {periods['current_end'].date()}\n\n"

                "Comparison period:\n"
                f"{periods['previous_start'].date()} "
                f"to {periods['previous_end'].date()}\n\n"

                "Action Audience:\n"
                f"{action_audience}\n\n"

                "KPI data:\n"
                + json.dumps(
                    kpi,
                    indent=2,
                    default=str,
                )
                + "\n\n"

                "Investigation periods:\n"
                + json.dumps(
                    periods,
                    indent=2,
                    default=str,
                )
            ),
        }
    ]

    # --------------------------------------------------------
    # INVESTIGATION LOOP
    # --------------------------------------------------------

    for step_number in range(
        1,
        MAX_INVESTIGATION_STEPS + 1,
    ):
        response = call_model(
            [
                {
                    "role": "system",
                    "content": prompt,
                },
                *messages,
            ],
            use_tools=True,
        )

        message = response.choices[0].message

        # Claude may finish before max steps. Always perform a
        # dedicated JSON synthesis instead of parsing the model's
        # natural-language completion directly.
        if not message.tool_calls:

            messages.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                }
            )

            result = synthesize_final_json(
                prompt,
                messages,
            )

            result = validate_result(result)

            result["_raw_kpi"] = kpi
            result["_periods"] = periods
            result["_investigation_steps"] = step_number

            return result

        # Save assistant tool call request.
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ],
            }
        )

        # Execute tools.
        for call in message.tool_calls:

            try:
                tool_result = execute_tool(
                    call.function.name,
                    periods,
                )
            except Exception as exc:
                tool_result = {
                    "error": str(exc)
                }

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(
                        tool_result,
                        indent=2,
                        default=str,
                    ),
                }
            )

    # --------------------------------------------------------
    # FINAL SYNTHESIS
    # --------------------------------------------------------

    result = synthesize_final_json(
        prompt,
        messages,
    )

    result = validate_result(result)

    result["_raw_kpi"] = kpi
    result["_periods"] = periods
    result["_investigation_steps"] = MAX_INVESTIGATION_STEPS

    return result