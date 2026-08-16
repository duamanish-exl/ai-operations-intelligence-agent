import re
import streamlit as st
from datetime import datetime

from orchestration import run_investigation
from chatbot import ask_chatbot


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="InsightForge | AI Operations Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "investigation_result" not in st.session_state:
    st.session_state.investigation_result = None

if "investigation_completed" not in st.session_state:
    st.session_state.investigation_completed = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       PAGE
    ======================================================== */

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }


    /* ========================================================
       SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc;
    }


    /* ========================================================
       HEADER
    ======================================================== */

    .hero-title {
        font-size: 38px;
        font-weight: 750;
        color: #0f172a;
        margin-bottom: 4px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 28px;
    }


    /* ========================================================
       METRIC CARDS
    ======================================================== */

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
    }

    div[data-testid="stMetricValue"] {
        color: #0f172a;
    }


    /* ========================================================
       INVESTIGATION CARD
    ======================================================== */

    .investigation-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-top: 12px;
        margin-bottom: 20px;
    }


    /* ========================================================
       REPORT CARD
    ======================================================== */

    .report-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-top: 12px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    }


    /* ========================================================
       SOURCE BOX
    ======================================================== */

    .source-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        margin-top: 18px;
    }


    /* ========================================================
       FLOATING CHATBOT
    ======================================================== */

    div[data-testid="stPopover"] {
        position: fixed;
        right: 28px;
        bottom: 28px;
        z-index: 999999;
    }

    div[data-testid="stPopover"] > button {
        width: 74px !important;
        height: 74px !important;
        min-width: 74px !important;
        min-height: 74px !important;

        border-radius: 50% !important;

        border: 3px solid #ffffff !important;

        background: linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed
        ) !important;

        color: white !important;

        font-size: 34px !important;

        box-shadow:
            0 10px 28px rgba(79, 70, 229, 0.40),
            0 3px 10px rgba(15, 23, 42, 0.15) !important;

        transition:
            transform 0.2s ease-in-out,
            box-shadow 0.2s ease-in-out !important;
    }

    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.08);

        box-shadow:
            0 14px 35px rgba(79, 70, 229, 0.50),
            0 4px 12px rgba(15, 23, 42, 0.18) !important;
    }


    /* ========================================================
       CHAT WINDOW
    ======================================================== */

    div[data-testid="stPopoverBody"] {
        width: 410px !important;
        max-width: 90vw !important;
    }


    /* ========================================================
       FOOTER
    ======================================================== */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 13px;
        padding-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🤖 InsightForge")

    st.caption("AI Operations Intelligence")

    st.divider()

    st.markdown("### Investigation")

    kpi = st.selectbox(
        "Select KPI",
        ["Complaint Rate"],
    )

    st.divider()

    st.markdown("### Investigation Settings")

    max_steps = st.number_input(
        "Maximum investigation steps",
        min_value=1,
        max_value=3,
        value=3,
        step=1,
    )

    st.divider()

    if st.session_state.investigation_completed:
        st.success("Investigation completed")
    else:
        st.info("Ready to investigate")

    st.divider()

    st.caption("InsightForge AI Operations Intelligence")
    st.caption("Powered by OpenRouter + Claude")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">🤖 AI Operations Intelligence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-subtitle">'
    'Investigate operational KPI movements, uncover evidence-based '
    'root causes and identify the actions that should be taken next.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# TOP INFORMATION CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Selected KPI",
        value=kpi,
    )

with col2:
    st.metric(
        label="🧠 Intelligence",
        value="AI Powered",
    )

with col3:
    st.metric(
        label="🔍 Investigation Steps",
        value=str(max_steps),
    )

with col4:

    status = (
        "Complete"
        if st.session_state.investigation_completed
        else "Ready"
    )

    st.metric(
        label="⚡ Status",
        value=status,
    )


st.divider()


# ============================================================
# INVESTIGATION
# ============================================================

st.markdown("## 🔎 Run Investigation")

st.write(
    f"Investigate the current **{kpi}** using the available "
    "business investigation tools."
)


if st.button(
    "🚀 Start Investigation",
    type="primary",
    use_container_width=True,
):

    with st.status(
        "Running InsightForge investigation...",
        expanded=True,
    ) as investigation_status:

        st.write("📊 Calculating KPI movement...")
        st.write("📅 Determining investigation period...")
        st.write("🧠 Analysing the KPI...")
        st.write("🔍 Selecting investigation tools...")
        st.write("🧩 Testing potential explanations...")
        st.write("🎯 Identifying root cause and recommended actions...")

        try:

            # ------------------------------------------------
            # RUN EXISTING INVESTIGATION
            # ------------------------------------------------

            result = run_investigation()

            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            st.session_state.investigation_result = result
            st.session_state.investigation_completed = True

            # New investigation = new conversation
            st.session_state.chat_history = []

            investigation_status.update(
                label="✅ Investigation completed",
                state="complete",
                expanded=False,
            )

        except Exception as e:

            st.session_state.investigation_result = None
            st.session_state.investigation_completed = False

            investigation_status.update(
                label="❌ Investigation failed",
                state="error",
                expanded=True,
            )

            st.error(
                f"Error while running investigation:\n\n{str(e)}"
            )


# ============================================================
# REPORT HELPERS
# ============================================================

def extract_section(text, start_heading, end_headings):
    """
    Extract one section from the investigation report.

    This allows the large AI response to be displayed across
    intuitive UI tabs rather than as one large block.
    """

    if not text:
        return ""

    start_pattern = re.escape(start_heading)

    pattern = rf"{start_pattern}(.*?)(?="

    if end_headings:

        pattern += "|".join(
            re.escape(h) for h in end_headings
        )

    pattern += r"|$)"

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return ""

    return match.group(1).strip()


def clean_section(text):
    """
    Remove unnecessary separator lines.
    """

    if not text:
        return ""

    text = re.sub(
        r"^-{3,}$",
        "",
        text,
        flags=re.MULTILINE,
    )

    return text.strip()


# ============================================================
# INVESTIGATION REPORT
# ============================================================

result = st.session_state.investigation_result


if result:

    st.divider()

    st.markdown("## 📋 Investigation Report")

    st.caption(
        "Navigate the investigation using the sections below."
    )

    # --------------------------------------------------------
    # EXTRACT REPORT SECTIONS
    # --------------------------------------------------------

    summary = extract_section(
        result,
        "🤖 EXECUTIVE SUMMARY",
        [
            "🔍 INVESTIGATION TRAIL",
            "🎯 ROOT CAUSE ANALYSIS",
            "📊 SUPPORTING EVIDENCE",
            "📈 CONFIDENCE",
            "💡 RECOMMENDED ACTIONS",
            "📌 FINAL CONCLUSION",
        ],
    )

    trail = extract_section(
        result,
        "🔍 INVESTIGATION TRAIL",
        [
            "🎯 ROOT CAUSE ANALYSIS",
            "📊 SUPPORTING EVIDENCE",
            "📈 CONFIDENCE",
            "💡 RECOMMENDED ACTIONS",
            "📌 FINAL CONCLUSION",
        ],
    )

    root_cause = extract_section(
        result,
        "🎯 ROOT CAUSE ANALYSIS",
        [
            "📊 SUPPORTING EVIDENCE",
            "📈 CONFIDENCE",
            "💡 RECOMMENDED ACTIONS",
            "📌 FINAL CONCLUSION",
        ],
    )

    evidence = extract_section(
        result,
        "📊 SUPPORTING EVIDENCE",
        [
            "📈 CONFIDENCE",
            "💡 RECOMMENDED ACTIONS",
            "📌 FINAL CONCLUSION",
        ],
    )

    confidence = extract_section(
        result,
        "📈 CONFIDENCE",
        [
            "💡 RECOMMENDED ACTIONS",
            "📌 FINAL CONCLUSION",
        ],
    )

    actions = extract_section(
        result,
        "💡 RECOMMENDED ACTIONS",
        [
            "📌 FINAL CONCLUSION",
        ],
    )

    conclusion = extract_section(
        result,
        "📌 FINAL CONCLUSION",
        [],
    )

    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    tab_summary, tab_evidence, tab_root, tab_actions, tab_trail = st.tabs(
        [
            "📋 Summary",
            "🔍 Evidence",
            "🎯 Root Cause",
            "💡 Actions",
            "🧭 Investigation Trail",
        ]
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    with tab_summary:

        if summary:

            st.markdown(
                '<div class="report-card">',
                unsafe_allow_html=True,
            )

            st.markdown(summary)

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.markdown(result)

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    with tab_evidence:

        if evidence:

            st.markdown(
                '<div class="report-card">',
                unsafe_allow_html=True,
            )

            st.markdown(evidence)

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "No separate evidence section was returned."
            )

    # --------------------------------------------------------
    # ROOT CAUSE
    # --------------------------------------------------------

    with tab_root:

        if root_cause:

            st.markdown(
                '<div class="report-card">',
                unsafe_allow_html=True,
            )

            st.markdown(root_cause)

            if conclusion:

                st.divider()

                st.markdown("### 📌 Final Conclusion")

                st.markdown(conclusion)

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "No separate root-cause section was returned."
            )

    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    with tab_actions:

        if actions:

            st.markdown(
                '<div class="report-card">',
                unsafe_allow_html=True,
            )

            st.markdown(actions)

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "No recommended actions were returned."
            )

    # --------------------------------------------------------
    # INVESTIGATION TRAIL
    # --------------------------------------------------------

    with tab_trail:

        if trail:

            st.markdown(
                '<div class="report-card">',
                unsafe_allow_html=True,
            )

            st.markdown(trail)

            if confidence:

                st.divider()

                st.markdown("### 📈 Confidence")

                st.markdown(confidence)

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "No investigation trail was returned."
            )


    # ========================================================
    # RAW REPORT
    # ========================================================

    with st.expander("View full investigation report"):

        st.markdown(result)


    # ========================================================
    # DATA SOURCES
    # ========================================================

    st.markdown("### 🔗 Investigation Data Sources")

    st.markdown(
        """
        <div class="source-box">

        The investigation uses evidence from the following
        operational datasets:

        **Complaints** ·
        **Billing History** ·
        **Meter Reading** ·
        **Meter Information** ·
        **Payments** ·
        **Customer Calls** ·
        **Account Health** ·
        **Account Balance** ·
        **Contract**

        </div>
        """,
        unsafe_allow_html=True,
    )


else:

    # ========================================================
    # EMPTY STATE
    # ========================================================

    st.divider()

    st.info(
        "🔎 **Ready to investigate**\n\n"
        f"Start an investigation to understand what is driving "
        f"the **{kpi}** movement.\n\n"
        "Once the investigation is complete, you will be able "
        "to explore the summary, evidence, root cause and "
        "recommended actions."
    )


# ============================================================
# FLOATING CHATBOT
# ============================================================

with st.popover("🤖"):

    st.markdown("### 🤖 Ask InsightForge")

    if not st.session_state.investigation_result:

        st.info(
            "Run an investigation first. "
            "Once the investigation is complete, you can ask "
            "questions about the findings."
        )

    else:

        st.caption(
            "Ask follow-up questions about the investigation, "
            "evidence, root cause or recommended actions."
        )

        # ----------------------------------------------------
        # PREVIOUS MESSAGES
        # ----------------------------------------------------

        if st.session_state.chat_history:

            for message in st.session_state.chat_history:

                if message["role"] == "user":

                    with st.chat_message("user"):
                        st.write(message["content"])

                else:

                    with st.chat_message("assistant"):
                        st.write(message["content"])


        # ----------------------------------------------------
        # CHAT INPUT
        # ----------------------------------------------------

        question = st.text_area(
            "Your question",
            placeholder=(
                "For example:\n\n"
                "Why is billing the most likely driver?\n\n"
                "What evidence supports the root cause?\n\n"
                "What should we do first?"
            ),
            height=120,
            key="chat_question",
        )

        if st.button(
            "Ask InsightForge",
            type="primary",
            use_container_width=True,
        ):

            if not question.strip():

                st.warning("Please enter a question.")

            else:

                # ------------------------------------------------
                # SAVE USER QUESTION
                # ------------------------------------------------

                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": question,
                    }
                )

                with st.spinner(
                    "InsightForge is analysing the investigation..."
                ):

                    try:

                        # ------------------------------------------------
                        # IMPORTANT:
                        # Uses ask_chatbot, NOT ask_question
                        # ------------------------------------------------

                        answer = ask_chatbot(
                                question=question,
                                investigation_result=st.session_state.investigation_result,
                                periods=st.session_state.get("investigation_periods", {}),
                                chat_history=st.session_state.chat_history,
                            )

                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "Unable to answer the question.\n\n"
                            f"{str(e)}"
                        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    f"""
    <div class="footer">
        InsightForge • AI Operations Intelligence •
        {datetime.now().strftime("%d %b %Y %H:%M")}
    </div>
    """,
    unsafe_allow_html=True,
)