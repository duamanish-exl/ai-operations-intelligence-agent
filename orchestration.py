import os
import json
import re
from pathlib import Path

from openai import OpenAI

from kpi import (
    SUPPORTED_KPIS,
    calculate_kpi,
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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set."
    )

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "anthropic/claude-sonnet-4.5",
)

MAX_INVESTIGATION_STEPS = int(
    os.getenv(
        "MAX_INVESTIGATION_STEPS",
        "3",
    )
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
                "and complaint patterns between the selected "
                "and comparison periods."
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
                "Analyse payment behaviour, payment failures, "
                "methods, and status changes."
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
                "call outcomes, and interaction trends."
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
                "Analyse balances, arrears, debt status, "
                "vulnerability, and financial health."
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

    mapping = {
        "investigate_complaints": investigate_complaints,
        "investigate_billing": investigate_billing,
        "investigate_meter": investigate_meter,
        "investigate_payments": investigate_payments,
        "investigate_customer_interactions": (
            investigate_customer_interactions
        ),
        "investigate_account_health": investigate_account_health,
    }

    function = mapping.get(name)

    if function is None:
        return {
            "error": f"Unknown tool: {name}"
        }

    return function(periods)


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
# JSON
# ============================================================

def parse_json_response(content):
    """
    Parse Claude's JSON even if it accidentally surrounds the
    object with prose or Markdown fences.
    """

    if not content:
        raise RuntimeError(
            "Claude returned an empty response."
        )

    text = content.strip()

    # Remove Markdown fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    text = text.strip()

    # Direct JSON.
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # JSON embedded in surrounding prose.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:
        candidate = text[start:end + 1]

        try:
            result = json.loads(candidate)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        "Claude did not return valid JSON.\n\n"
        f"Response:\n{text}"
    )


# ============================================================
# RESULT VALIDATION
# ============================================================

REQUIRED_FIELDS = [
    "kpi",
    "period",
    "comparison_period",
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


def validate_result(result, kpi_name):

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

    if result.get("kpi") != kpi_name:
        result["kpi"] = kpi_name

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
# MODEL CALL
# ============================================================

def call_model(messages, use_tools=True):

    try:

        if use_tools:

            return client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=4500,
            )

        return client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tool_choice="none",
            max_tokens=4500,
        )

    except Exception as exc:

        message = str(exc)

        if "401" in message or "User not found" in message:

            raise RuntimeError(
                "OpenRouter authentication failed. "
                "Check OPENROUTER_API_KEY."
            ) from exc

        raise


# ============================================================
# MAIN INVESTIGATION
# ============================================================

def run_investigation(
    kpi_name,
    start_period,
    end_period,
    action_audience,
):

    if kpi_name not in SUPPORTED_KPIS:
        raise ValueError(
            f"Unsupported KPI: {kpi_name}"
        )

    prompt = load_prompt()

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    kpi = calculate_kpi(
    kpi_name=kpi_name,
    start_period=start_period,
    end_period=end_period,
)

    # --------------------------------------------------------
    # PERIODS
    # --------------------------------------------------------

    periods = get_investigation_periods(
    start_period=start_period,
    end_period=end_period,
    kpi_name=kpi_name,
)

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    messages = [
        {
            "role": "user",
            "content": (
                f"Investigate the KPI: {kpi_name}\n\n"
                "Selected investigation period:\n"
                f"{periods['current_start'].date()} "
                f"to {periods['current_end'].date()}\n\n"
                "Comparison period:\n"
                f"{periods['previous_start'].date()} "
                f"to {periods['previous_end'].date()}\n\n"
                "KPI calculation:\n"
                + json.dumps(
                    kpi,
                    indent=2,
                    default=str,
                )
                + "\n\n"
                "Use investigation tools to determine WHY "
                "this KPI moved."
            ),
        }
    ]

    # --------------------------------------------------------
    # TOOL LOOP
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

        # Claude can finish early.
        if not message.tool_calls:

            result = parse_json_response(
                message.content
            )

            result = validate_result(
                result,
                kpi_name,
            )

            result["_raw_kpi"] = kpi
            result["_periods"] = periods
            result["_investigation_steps"] = step_number

            return result

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

    messages.append(
        {
            "role": "user",
            "content": (
                "FINAL RESPONSE INSTRUCTION. "
                "Do not call any more tools. "
                "Return ONLY one valid JSON object. "
                "Do not write prose before or after the JSON. "
                "Do not use Markdown or code fences. "
                "The first character must be { and the final "
                "character must be }. "
                "Use only the evidence already collected. "
                "Follow the required schema exactly."
            ),
        }
    )

    final_response = call_model(
        [
            {
                "role": "system",
                "content": prompt,
            },
            *messages,
        ],
        use_tools=False,
    )

    result = parse_json_response(
        final_response.choices[0].message.content
    )

    result = validate_result(
        result,
        kpi_name,
    )

    result["_raw_kpi"] = kpi
    result["_periods"] = periods
    result["_investigation_steps"] = (
        MAX_INVESTIGATION_STEPS
    )

    return result
