import streamlit as st
from datetime import datetime, timedelta

from kpi import get_available_date_range
from orchestration import run_investigation
from chatbot import ask_chatbot


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="InsightForge",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "stage" not in st.session_state:
    # "profile" -> Netflix-style profile picker (KPI/period already set above it)
    # "investigation" -> running / results screen
    st.session_state.stage = "profile"

if "investigation_result" not in st.session_state:
    st.session_state.investigation_result = None

if "investigation_completed" not in st.session_state:
    st.session_state.investigation_completed = False

if "action_audience" not in st.session_state:
    st.session_state.action_audience = None

if "last_start_period" not in st.session_state:
    st.session_state.last_start_period = None

if "last_end_period" not in st.session_state:
    st.session_state.last_end_period = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #080b11;
    --panel: #10151d;
    --border: #2a3442;
    --text: #f5f7fa;
    --muted: #a7b0bf;
    --purple: #7c6cff;
    --green: #43d995;
    --red: #ff7070;
    --blue: #4fa3ff;
    --amber: #e5c45c;
}

html,
body,
[data-testid="stAppViewContainer"] {
    background: var(--bg);
}

[data-testid="stHeader"] {
    background: var(--bg);
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0b0f16;
    border-right: 1px solid var(--border);
}

.sidebar-logo {
    color: #ffffff;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.sidebar-subtitle {
    color: #a0aaba;
    font-size: 11px;
}

.dash-link {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 9px 10px;
    border-radius: 10px;
    font-size: 12px;
    margin-bottom: 4px;
}

.dash-link.active {
    background: rgba(124,108,255,.12);
    border: 1px solid rgba(124,108,255,.28);
    color: #ffffff;
    font-weight: 700;
}

.dash-link.disabled {
    color: #6b7280;
}

.dash-link-soon {
    font-size: 9px;
    color: #6b7280;
    margin-left: auto;
}

.sidebar-note {
    padding: 12px;
    background: #101722;
    border: 1px solid #222c39;
    border-radius: 12px;
    color: #d9e1ec;
    font-size: 10px;
    line-height: 1.6;
}

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 54px;
    padding-top: 6px;
    padding-bottom: 18px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.main-header-left {
    display: flex;
    align-items: center;
    gap: 11px;
}

.header-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: linear-gradient(135deg, #6658ff, #9482ff);
    color: white;
    font-size: 18px;
    font-weight: 800;
}

.header-title {
    color: white;
    font-size: 16px;
    font-weight: 750;
    line-height: 1.35;
}

.header-subtitle {
    color: #a7b0bf;
    font-size: 10px;
}

.header-status {
    color: #6fe1aa;
    font-size: 10px;
    font-weight: 700;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(67,225,170,.05);
    border: 1px solid rgba(67,225,170,.15);
}

/* ============================================================
   TOP CONTROL BAR (KPI / period / new investigation)
   ============================================================ */

.st-key-topbar_wrap {
    background: #0e141c;
    border: 1px solid #232e3c;
    border-radius: 14px;
    padding: 6px 16px 14px;
    margin-bottom: 22px;
}

.topbar-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.topbar-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 11px;
}

.topbar-badge.period {
    background: rgba(124,108,255,.10);
    border: 1px solid rgba(124,108,255,.22);
    color: #c9c2ff;
}

.topbar-badge.compare {
    background: #131a24;
    border: 1px solid #253141;
    color: #a7b0bf;
}

.topbar-summary {
    color: #d9e1ec;
    font-size: 12px;
    padding: 10px 4px 2px;
}

/* ============================================================
   PROFILE GRID
   ============================================================ */

.hero {
    text-align: center;
    padding: 22px 10px 10px;
}

.hero-icon {
    width: 52px;
    height: 52px;
    margin: 0 auto 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    background: rgba(124,108,255,.08);
    border: 1px solid rgba(124,108,255,.18);
    color: #a99eff;
    font-size: 22px;
}

.hero-title {
    color: white;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    max-width: 620px;
    margin: 8px auto 0;
    color: #a7b0bf;
    font-size: 13px;
    line-height: 1.7;
}

.st-key-profile_grid button {
    width: 100% !important;
    height: 108px !important;
    border-radius: 16px !important;
    background: #10151d !important;
    border: 1px solid #232e3c !important;
    color: #eef2f7 !important;
    font-size: 12px !important;
    font-weight: 650 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    white-space: normal !important;
}

.st-key-profile_grid button:hover {
    transform: translateY(-2px);
    border-color: rgba(124,108,255,.45) !important;
}

.st-key-profile_grid button p {
    font-size: 12px !important;
    font-weight: 650 !important;
}

/* per-profile accent (targets the button's first line as an icon-like badge via border-top color) */
.st-key-profile_general button { border-top: 3px solid var(--blue) !important; }
.st-key-profile_ops button { border-top: 3px solid var(--purple) !important; }
.st-key-profile_billing button { border-top: 3px solid var(--amber) !important; }
.st-key-profile_service button { border-top: 3px solid var(--green) !important; }
.st-key-profile_finance button { border-top: 3px solid #8a93a3 !important; }
.st-key-profile_senior button { border-top: 3px solid #8a93a3 !important; }

.start-description {
    max-width: 620px;
    margin: 4px auto 22px;
    color: #d9e1ec;
    font-size: 12px;
    line-height: 1.7;
    text-align: center;
}

/* ============================================================
   RESULT SCREEN (largely unchanged from original)
   ============================================================ */

.period-card {
    max-width: 820px;
    margin: 0 auto 24px;
    padding: 16px 18px;
    background: #0e141c;
    border: 1px solid #232e3c;
    border-radius: 14px;
    text-align: center;
}

.period-label {
    color: #aeb7c5;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.period-value {
    color: white;
    font-size: 13px;
    font-weight: 650;
    margin-top: 5px;
}

.period-compare {
    color: #d9e1ec;
    font-size: 10px;
    margin-top: 4px;
}

.kpi-card {
    background: linear-gradient(145deg, #121923, #0e141c);
    border: 1px solid #293443;
    border-radius: 18px;
    padding: 25px 28px;
    margin-top: 20px;
}

.kpi-label {
    color: #aeb7c5;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.kpi-value {
    color: white;
    font-size: 52px;
    font-weight: 850;
    line-height: 1;
    margin-top: 10px;
}

.kpi-meta {
    color: #a7b0bf;
    font-size: 12px;
    margin-top: 9px;
}

.status-pill {
    display: inline-block;
    margin-top: 13px;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
}

.info-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 20px;
    min-height: 145px;
}

.info-label {
    color: #aeb7c5;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .9px;
}

.info-text {
    color: #e5e9ef;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 9px;
}

.driver {
    background: #0d2018;
    border: 1px solid #1f4839;
    border-radius: 14px;
    padding: 18px;
    min-height: 120px;
}

.driver-value {
    color: #70e3a7;
    font-size: 24px;
    font-weight: 850;
}

.driver-name {
    color: white;
    font-size: 12px;
    font-weight: 700;
    margin-top: 5px;
}

.driver-description {
    color: #aebbb5;
    font-size: 10px;
    line-height: 1.5;
    margin-top: 7px;
}

.risk {
    background: #251719;
    border: 1px solid #593137;
    border-radius: 14px;
    padding: 18px;
    min-height: 120px;
}

.risk-value {
    color: #ff8f8f;
    font-size: 24px;
    font-weight: 850;
}

.risk-name {
    color: white;
    font-size: 12px;
    font-weight: 700;
    margin-top: 5px;
}

.risk-description {
    color: #c0adb1;
    font-size: 10px;
    line-height: 1.5;
    margin-top: 7px;
}

.action {
    background: #121620;
    border: 1px solid #232e3c;
    border-radius: 14px;
    padding: 18px;
}

.action-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.action-badge.immediate {
    background: rgba(255,112,112,.12);
    border: 1px solid rgba(255,112,112,.28);
    color: #ff9797;
}

.action-badge.near-term {
    background: rgba(229,196,92,.12);
    border: 1px solid rgba(229,196,92,.28);
    color: #e9d38b;
}

.action-badge.monitor {
    background: rgba(124,108,255,.12);
    border: 1px solid rgba(124,108,255,.28);
    color: #c9c2ff;
}

.action-text {
    color: #eef0f5;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 8px;
}

.confidence-pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
}

.confidence-pill.high {
    background: rgba(67,217,149,.10);
    border: 1px solid rgba(67,217,149,.24);
    color: #6fe3a9;
}

.confidence-pill.medium {
    background: rgba(229,196,92,.10);
    border: 1px solid rgba(229,196,92,.24);
    color: #e5c45c;
}

.confidence-pill.low {
    background: rgba(255,112,112,.10);
    border: 1px solid rgba(255,112,112,.24);
    color: #ff9797;
}

.footer {
    color: #7f8a9a;
    font-size: 10px;
    text-align: center;
    border-top: 1px solid var(--border);
    padding-top: 15px;
    margin-top: 30px;
}


/* ============================================================
   FLOATING CHAT BUTTON
   ============================================================ */

.st-key-chat_support {
    position: fixed !important;
    right: 28px !important;
    bottom: 24px !important;
    z-index: 9999 !important;
}

.st-key-chat_support button {
    width: 64px !important;
    height: 64px !important;
    min-width: 64px !important;
    min-height: 64px !important;
    padding: 0 !important;
    margin: 0 !important;
    background: linear-gradient(135deg, #6658ff, #9482ff) !important;
    border: none !important;
    outline: none !important;
    border-radius: 50% !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35) !important;
    position: relative !important;
    font-size: 0 !important;
}

.st-key-chat_support button > * {
    visibility: hidden !important;
}

.st-key-chat_support button::before {
    content: "✦" !important;
    visibility: visible !important;
    position: absolute !important;
    left: 50% !important;
    top: 50% !important;
    transform: translate(-50%, -55%) !important;
    color: #ffffff !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    line-height: 1 !important;
}

.st-key-chat_support button::after {
    content: none !important;
    display: none !important;
}

.st-key-chat_support button:hover {
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4) !important;
}


/* ============================================================
   NOTIFICATION DOT
   ============================================================ */

.chat-notification-dot {
    position: fixed;
    right: 25px;
    bottom: 78px;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #ff7070;
    border: 2px solid #080b11;
    z-index: 10000;
    pointer-events: none;
}

/* ============================================================
   SUGGESTED QUESTIONS
   ============================================================ */

.suggested-title {
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 8px;
}

.suggested-subtitle {
    color: #d9e1ec;
    font-size: 10px;
    margin-bottom: 14px;
}

.suggestion-button {
    width: 100%;
    text-align: left;
    padding: 10px 12px;
    margin-bottom: 8px;
    background: #101620;
    color: #e9ecf3;
    border: 1px solid #252f3d;
    border-radius: 10px;
    font-size: 11px;
    line-height: 1.4;
    cursor: pointer;
}

.suggestion-button:hover {
    background: #151c29;
    border-color: rgba(124,108,255,.45);
}

/* ============================================================
   FINAL CONTRAST POLISH
   ============================================================ */

[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: #eef2f7 !important;
}

[data-testid="stTabs"] button {
    color: #aeb7c5 !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffffff !important;
    font-weight: 600 !important;
}

[data-testid="stTabs"] p {
    color: #d9e0e9;
}

[data-testid="stTabs"] [data-testid="stCaptionContainer"] {
    color: #aeb7c5 !important;
}

[data-testid="stExpander"] summary {
    color: #d7dee8 !important;
}

[data-testid="stExpander"] summary p {
    color: #d7dee8 !important;
}

[data-testid="stExpander"] {
    color: #d9e0e9 !important;
}

[data-testid="stSidebar"] label {
    color: #c5ceda !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #a7b0bf !important;
}

.footer {
    color: #7f8a9a !important;
}

[data-testid="stDivider"] {
    border-color: #2a3442 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# AVAILABLE DATES
# ============================================================

date_range = get_available_date_range()

min_date = date_range["min_date"].date()
max_date = date_range["max_date"].date()

default_end = max_date
default_start = max(min_date, default_end - timedelta(days=7))


# ============================================================
# ACTION AUDIENCE PROFILES
# (maps every existing audience option onto a profile card;
#  nothing from the original dropdown was dropped)
# ============================================================

AUDIENCE_PROFILES = [
    {"key": "profile_general", "label": "General / Business", "icon": "🏢"},
    {"key": "profile_ops", "label": "Operations Manager", "icon": "⚙️"},
    {"key": "profile_billing", "label": "Billing Team", "icon": "🧾"},
    {"key": "profile_service", "label": "Customer Service", "icon": "🎧"},
    {"key": "profile_finance", "label": "Finance Team", "icon": "💳"},
    {"key": "profile_senior", "label": "Senior Management", "icon": "🎯"},
]


# ============================================================
# LEFT DRAWER: DASHBOARD LINKS
# (native Streamlit sidebar - collapsible out of the box)
# ============================================================

with st.sidebar:

    st.markdown('<div class="sidebar-logo">✦ InsightForge</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">AI Operations Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Dashboards")

    st.markdown(
        """
        <div class="dash-link active">💬 Complaint Rate</div>
        <div class="dash-link disabled">💳 Debt % <span class="dash-link-soon">Coming soon</span></div>
        <div class="dash-link disabled">⚡ Outage Impact <span class="dash-link-soon">Coming soon</span></div>
        <div class="dash-link disabled">🧾 Billing Accuracy <span class="dash-link-soon">Coming soon</span></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div class="sidebar-note">
            Available data:
            {min_date.strftime('%d %b %Y')}
            →
            {max_date.strftime('%d %b %Y')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("InsightForge")
    st.caption("AI Operations Intelligence")


# ============================================================
# TOP CONTROL BAR (KPI / period / new investigation)
# Collapsed by default once an investigation is running,
# expanded by default on the profile-picker screen.
# ============================================================

default_expanded = st.session_state.stage == "profile"

with st.container(key="topbar_wrap"):

    with st.expander("Investigation controls", expanded=default_expanded):

        col_kpi, col_start, col_end, col_spacer, col_reset = st.columns(
            [1.4, 1, 1, 1.6, 1.2]
        )

        with col_kpi:
            kpi = st.selectbox("KPI", ["Complaint Rate"])

        with col_start:
            start_period = st.date_input(
                "Start period",
                value=default_start,
                min_value=min_date,
                max_value=max_date,
            )

        with col_end:
            end_period = st.date_input(
                "End period",
                value=default_end,
                min_value=min_date,
                max_value=max_date,
            )

        with col_reset:
            st.write("")
            if st.button("↻ New investigation", use_container_width=True):
                st.session_state.stage = "profile"
                st.session_state.investigation_result = None
                st.session_state.investigation_completed = False
                st.session_state.action_audience = None
                st.session_state.last_start_period = None
                st.session_state.last_end_period = None
                st.session_state.chat_history = []
                st.rerun()

    valid_range = start_period <= end_period

    if valid_range:

        period_days = (end_period - start_period).days + 1
        previous_end = start_period - timedelta(days=1)
        previous_start = previous_end - timedelta(days=period_days - 1)

        badges_html = f"""
        <div class="topbar-badges">
            <span class="topbar-badge period">📅 {start_period.strftime('%d %b')} → {end_period.strftime('%d %b %Y')}</span>
            <span class="topbar-badge compare">↩ Comparison: {previous_start.strftime('%d %b')} → {previous_end.strftime('%d %b %Y')}</span>
        """

        if st.session_state.action_audience:
            badges_html += f'<span class="topbar-badge period">👤 {st.session_state.action_audience}</span>'

        badges_html += "</div>"

        st.markdown(badges_html, unsafe_allow_html=True)

    else:
        st.error("Start period must be before end period.")
        previous_start = None
        previous_end = None


# ============================================================
# FLOATING CHAT SUPPORT (unchanged position/behaviour)
# ============================================================

st.markdown('<div class="chat-notification-dot"></div>', unsafe_allow_html=True)

suggested_questions = [
    "Why did the complaint rate change?",
    "Which factors drove the change?",
    "What should I do next?",
    "How does this compare with the previous period?",
]

with st.popover("💬", key="chat_support"):

    st.markdown(
        """
        <div class="suggested-title">✨ Suggested Questions</div>
        <div class="suggested-subtitle">Ask about the current investigation</div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.chat_history:

        for i, suggestion in enumerate(suggested_questions):
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.chat_question = suggestion
                st.rerun()

    st.divider()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if "chat_question" not in st.session_state:
        st.session_state.chat_question = ""

    with st.form("chat_form", clear_on_submit=True):

        question = st.text_input(
            "Message",
            value=st.session_state.chat_question,
            placeholder="Ask something about the investigation...",
            label_visibility="collapsed",
        )

        submitted = st.form_submit_button("Send", use_container_width=True, type="primary")

    if submitted and question.strip():

        previous_history = list(st.session_state.chat_history)
        investigation_result = st.session_state.investigation_result or {}

        periods = {
            "start_period": str(st.session_state.last_start_period),
            "end_period": str(st.session_state.last_end_period),
            "comparison_period": investigation_result.get("comparison_period", {}),
        }

        try:
            with st.spinner("Thinking..."):
                response = ask_chatbot(
                    question=question.strip(),
                    investigation_result=investigation_result,
                    periods=periods,
                    chat_history=previous_history,
                )

            st.session_state.chat_history.append({"role": "user", "content": question.strip()})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.chat_question = ""
            st.rerun()

        except Exception as exc:
            st.error(f"Unable to get response: {exc}")


# ============================================================
# SCREEN 1: PROFILE PICKER
# ============================================================

if st.session_state.stage == "profile":

    st.html(
        """
        <div class="hero">
            <div class="hero-icon">✦</div>
            <div class="hero-title">Who is this investigation for.</div>
            <div class="hero-subtitle">
                Pick a profile to start investigating the KPI and period selected above.
                The investigation runs immediately using those settings.
            </div>
        </div>
        """
    )

    with st.container(key="profile_grid"):

        cols = st.columns(3)

        for i, profile in enumerate(AUDIENCE_PROFILES):

            with cols[i % 3]:

                clicked = st.button(
                    f"{profile['icon']}\n\n{profile['label']}",
                    key=profile["key"],
                    disabled=not valid_range,
                    use_container_width=True,
                )

                if clicked:

                    st.session_state.action_audience = profile["label"]

                    with st.status("Running investigation...", expanded=True) as status:

                        st.write("📊 Calculating KPI for selected period...")
                        st.write("🧠 Selecting investigation path...")
                        st.write("🔍 Evaluating evidence...")
                        st.write("🎯 Validating root cause...")
                        st.write("✓ Preparing result...")

                        try:
                            investigation_result = run_investigation(
                                start_period=start_period,
                                end_period=end_period,
                                action_audience=profile["label"],
                            )

                            st.session_state.investigation_result = investigation_result
                            st.session_state.investigation_completed = True
                            st.session_state.last_start_period = start_period
                            st.session_state.last_end_period = end_period
                            st.session_state.stage = "investigation"

                            status.update(label="✅ Investigation complete", state="complete", expanded=False)
                            st.rerun()

                        except Exception as exc:
                            status.update(label="❌ Investigation failed", state="error", expanded=True)
                            st.error(f"Investigation failed:\n\n{exc}")

    if not valid_range:
        st.info("Fix the investigation period above before picking a profile.")

    st.markdown(
        f"""
        <div class="footer">
            InsightForge • AI Operations Intelligence •
            {datetime.now().strftime("%d %b %Y %H:%M")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# SCREEN 2: INVESTIGATION / RESULTS
# ============================================================

result = st.session_state.investigation_result

if result is None:
    # Safety net: stage says "investigation" but there's no result
    # (e.g. a stale session). Send back to the profile picker.
    st.session_state.stage = "profile"
    st.rerun()


current_value = result.get("current_value")
previous_value = result.get("previous_value")
unit = result.get("unit", "%")

absolute_change = result.get("absolute_change")
relative_change = result.get("relative_change_pct")

direction = str(result.get("direction", "unknown")).lower()

executive_summary = result.get("executive_summary", "")
primary_root_cause = result.get("primary_root_cause", "")
secondary_factors = result.get("secondary_factors", [])
watch_items = result.get("watch_items", [])
recommended_actions = result.get("recommended_actions", [])
supporting_evidence = result.get("supporting_evidence", [])
confidence = result.get("confidence", {})
timeline = result.get("investigation_timeline", [])
final_conclusion = result.get("final_conclusion", "")
result_period = result.get("period", {})
result_comparison = result.get("comparison_period", {})


# ============================================================
# RESULT PERIOD
# ============================================================

if result_period:

    st.html(
        f"""
        <div class="period-card">
            <div class="period-label">Investigation Period</div>
            <div class="period-value">
                {result_period.get("start", "")} → {result_period.get("end", "")}
            </div>
            <div class="period-compare">
                Comparison: {result_comparison.get("start", "")} → {result_comparison.get("end", "")}
            </div>
        </div>
        """
    )


# ============================================================
# KPI PERFORMANCE
# ============================================================

st.markdown("### KPI Performance")

if current_value is not None:

    if direction == "improving":
        status_text, status_bg, status_border, status_color = (
            "● IMPROVING", "rgba(67,217,149,.08)", "rgba(67,217,149,.18)", "#6fe3a9",
        )
    elif direction == "worsening":
        status_text, status_bg, status_border, status_color = (
            "● WORSENING", "rgba(255,112,112,.08)", "rgba(255,112,112,.18)", "#ff9797",
        )
    else:
        status_text, status_bg, status_border, status_color = (
            "● STABLE", "rgba(229,196,92,.08)", "rgba(229,196,92,.18)", "#e5c45c",
        )

    previous_text = f"{previous_value:.2f}{unit}" if previous_value is not None else "N/A"
    absolute_text = f"{absolute_change:+.2f} pp" if absolute_change is not None else "N/A"
    relative_text = f"{relative_change:+.1f}%" if relative_change is not None else "N/A"

    st.html(
        f"""
        <div class="kpi-card">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center;">
                <div>
                    <div class="kpi-label">Complaint Rate</div>
                    <div class="kpi-value">
                        {current_value:.2f}
                        <span style="font-size:18px;color:#9aa5b5;margin-left:3px;">{unit}</span>
                    </div>
                    <div class="kpi-meta">Previous: <b>{previous_text}</b></div>
                </div>
                <div style="border-left:1px solid #293443;padding-left:40px;">
                    <div class="kpi-label">Change Rate</div>
                    <div style="font-size:42px;font-weight:850;line-height:1;margin-top:10px;color:{status_color};">
                        {relative_text}
                    </div>
                    <div class="kpi-meta">{absolute_text} vs previous period</div>
                </div>
            </div>
            <div class="status-pill" style="background:{status_bg};border:1px solid {status_border};color:{status_color};margin-top:22px;">
                {status_text}
            </div>
        </div>
        """
    )

else:
    st.warning("The investigation did not return a KPI value.")


# ============================================================
# EXECUTIVE FINDING
# ============================================================

st.markdown("### Executive Finding")

col1, col2 = st.columns([1.3, 1], gap="medium")

with col1:
    st.html(
        f"""
        <div class="info-card">
            <div class="info-label">Key Finding</div>
            <div class="info-text">{executive_summary or "No finding returned."}</div>
        </div>
        """
    )

with col2:
    st.html(
        f"""
        <div class="info-card">
            <div class="info-label">Primary Driver</div>
            <div class="info-text">{primary_root_cause or "No driver returned."}</div>
        </div>
        """
    )


# ============================================================
# DRIVERS
# ============================================================

if secondary_factors:

    st.markdown("### Main Drivers")

    columns = st.columns(min(len(secondary_factors[:3]), 3))

    for i, factor in enumerate(secondary_factors[:3]):

        change = factor.get("change")
        factor_unit = factor.get("unit", "%")
        change_text = f"{change:+.1f}{factor_unit}" if change is not None else "—"

        with columns[i]:
            st.html(
                f"""
                <div class="driver">
                    <div class="driver-value">{change_text}</div>
                    <div class="driver-name">{factor.get("name", "Driver")}</div>
                    <div class="driver-description">{factor.get("description", "")}</div>
                </div>
                """
            )


# ============================================================
# WATCH ITEMS
# ============================================================

if watch_items:

    st.markdown("### Watch Items")

    columns = st.columns(min(len(watch_items[:3]), 3))

    for i, item in enumerate(watch_items[:3]):

        change = item.get("change")
        item_unit = item.get("unit", "%")
        change_text = f"{change:+.1f}{item_unit}" if change is not None else "—"

        with columns[i]:
            st.html(
                f"""
                <div class="risk">
                    <div class="risk-value">{change_text}</div>
                    <div class="risk-name">{item.get("name", "Watch item")}</div>
                    <div class="risk-description">{item.get("description", "")}</div>
                </div>
                """
            )


# ============================================================
# RECOMMENDED ACTIONS (now with colored priority badges)
# ============================================================

def _priority_badge_class(priority_text):
    p = (priority_text or "").strip().lower()
    if p == "immediate":
        return "immediate"
    if p == "near-term" or p == "near term":
        return "near-term"
    return "monitor"


if recommended_actions:

    st.markdown("### Recommended Action")

    first_action = recommended_actions[0]
    badge_class = _priority_badge_class(first_action.get("priority"))

    st.html(
        f"""
        <div class="action">
            <span class="action-badge {badge_class}">{first_action.get("priority", "Action")}</span>
            <div class="action-text">{first_action.get("action", "")}</div>
        </div>
        """
    )

    if len(recommended_actions) > 1:

        with st.expander("View additional actions"):

            for action in recommended_actions[1:]:

                badge_class = _priority_badge_class(action.get("priority"))

                st.html(
                    f"""
                    <div style="margin-bottom: 14px;">
                        <span class="action-badge {badge_class}">{action.get("priority", "Action")}</span>
                        <div class="action-text">{action.get("action", "")}</div>
                    </div>
                    """
                )


# ============================================================
# DETAIL
# ============================================================

st.markdown("### Investigation Detail")

tab1, tab2, tab3, tab4 = st.tabs(["Evidence", "Root Cause", "Timeline", "Confidence"])

with tab1:

    if supporting_evidence:
        for item in supporting_evidence:
            st.markdown(f"**Evidence:** {item.get('evidence', '')}")
            st.caption(item.get("why_it_matters", ""))
            st.divider()
    else:
        st.info("No supporting evidence returned.")

with tab2:

    st.html(
        f"""
        <div class="info-card">
            <div class="info-label">Primary Root Cause</div>
            <div class="info-text">{primary_root_cause or "Not established."}</div>
        </div>
        """
    )

    if final_conclusion:
        st.markdown("#### Conclusion")
        st.info(final_conclusion)

with tab3:

    if timeline:
        for step in timeline:
            with st.expander(f"Step {step.get('step', '')} • {step.get('tool', '')}"):
                st.write(f"**Why:** {step.get('reason', '')}")
                st.write(f"**Finding:** {step.get('finding', '')}")
                st.write(f"**Decision:** {step.get('decision', '')}")
    else:
        st.info("No investigation timeline returned.")

with tab4:

    level = str(confidence.get("level", "Unknown"))
    level_class = level.strip().lower() if level.strip().lower() in ("high", "medium", "low") else "medium"

    st.html(f'<span class="confidence-pill {level_class}">{level}</span>')

    if confidence.get("reason"):
        st.write(confidence.get("reason"))

    if confidence.get("limitations"):
        st.warning(confidence.get("limitations"))


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="footer">
        InsightForge • AI Operations Intelligence •
        {datetime.now().strftime("%d %b %Y %H:%M")}
    </div>
    """,
    unsafe_allow_html=True,
)