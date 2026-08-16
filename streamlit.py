import streamlit as st
from datetime import datetime, timedelta

from kpi import get_available_date_range
from orchestration import run_investigation


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

if "investigation_result" not in st.session_state:
    st.session_state.investigation_result = None

if "investigation_completed" not in st.session_state:
    st.session_state.investigation_completed = False

if "last_start_period" not in st.session_state:
    st.session_state.last_start_period = None

if "last_end_period" not in st.session_state:
    st.session_state.last_end_period = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #080b11;
    --panel: #10151d;
    --border: #242d39;
    --text: #f5f7fa;
    --muted: #8490a2;
    --purple: #7c6cff;
    --green: #43d995;
    --red: #ff7070;
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
    color: #788496;
    font-size: 11px;
}

.sidebar-note {
    padding: 12px;
    background: #101722;
    border: 1px solid #222c39;
    border-radius: 12px;
    color: #7f8b9d;
    font-size: 10px;
    line-height: 1.6;
}

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 18px;
    margin-bottom: 28px;
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
}

.header-subtitle {
    color: #788496;
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

.hero {
    text-align: center;
    padding: 36px 10px 22px;
}

.hero-icon {
    width: 58px;
    height: 58px;
    margin: 0 auto 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    background: rgba(124,108,255,.08);
    border: 1px solid rgba(124,108,255,.18);
    color: #a99eff;
    font-size: 24px;
}

.hero-title {
    color: white;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1px;
}

.hero-subtitle {
    max-width: 650px;
    margin: 10px auto 0;
    color: #8490a2;
    font-size: 13px;
    line-height: 1.7;
}

.start-card {
    max-width: 820px;
    margin: 18px auto 24px;
    padding: 30px;
    text-align: center;
    background: linear-gradient(145deg, #121923, #0d131a);
    border: 1px solid #293443;
    border-radius: 18px;
}

.start-label {
    color: #7d899b;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.start-kpi {
    color: white;
    font-size: 27px;
    font-weight: 750;
    margin-top: 8px;
}

.start-description {
    max-width: 620px;
    margin: 10px auto 0;
    color: #7f8b9d;
    font-size: 12px;
    line-height: 1.7;
}

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
    color: #7d899b;
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
    color: #7f8b9d;
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
    color: #7f8b9c;
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
    color: #8490a2;
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
    color: #7d899a;
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
    color: #84958f;
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
    color: #a38d92;
    font-size: 10px;
    line-height: 1.5;
    margin-top: 7px;
}

.action {
    background: linear-gradient(
        90deg,
        rgba(124,108,255,.10),
        rgba(124,108,255,.025)
    );
    border: 1px solid rgba(124,108,255,.18);
    border-left: 4px solid var(--purple);
    border-radius: 14px;
    padding: 18px;
}

.action-priority {
    color: #aaa0ff;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.action-text {
    color: #eef0f5;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 6px;
}

.footer {
    color: #536074;
    font-size: 10px;
    text-align: center;
    border-top: 1px solid var(--border);
    padding-top: 15px;
    margin-top: 30px;
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


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">✦ InsightForge</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'AI Operations Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### Investigation")

    kpi = st.selectbox(
        "Select KPI",
        ["Complaint Rate"],
    )

    st.markdown("### Investigation Period")

    default_end = max_date
    default_start = max(
        min_date,
        default_end - timedelta(days=6),
    )

    start_period = st.date_input(
        "Start Period",
        value=default_start,
        min_value=min_date,
        max_value=max_date,
    )

    end_period = st.date_input(
        "End Period",
        value=default_end,
        min_value=min_date,
        max_value=max_date,
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    valid_range = start_period <= end_period

    if valid_range:

        period_days = (
            end_period - start_period
        ).days + 1

        previous_end = (
            start_period
            - timedelta(days=1)
        )

        previous_start = (
            previous_end
            - timedelta(days=period_days - 1)
        )

        st.caption(
            f"Comparison: "
            f"{previous_start.strftime('%d %b %Y')} → "
            f"{previous_end.strftime('%d %b %Y')}"
        )

    else:

        st.error(
            "Start Period must be before End Period."
        )

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

    if st.session_state.investigation_completed:
        st.success("Investigation complete")
    else:
        st.info("Ready to investigate")

    if st.button(
        "↻ New Investigation",
        use_container_width=True,
    ):

        st.session_state.investigation_result = None
        st.session_state.investigation_completed = False
        st.session_state.last_start_period = None
        st.session_state.last_end_period = None

        st.rerun()

    st.markdown("---")

    st.caption("InsightForge")
    st.caption("AI Operations Intelligence")


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="main-header">

        <div class="main-header-left">

            <div class="header-icon">
                ✦
            </div>

            <div>

                <div class="header-title">
                    Operations Intelligence
                </div>

                <div class="header-subtitle">
                    Evidence-based KPI investigation
                </div>

            </div>

        </div>

        <div class="header-status">
            ● System ready
        </div>

    </div>
    """
)


# ============================================================
# RESULT
# ============================================================

result = st.session_state.investigation_result


# ============================================================
# START SCREEN
# ============================================================

if result is None:

    st.html(
        """
        <div class="hero">

            <div class="hero-icon">
                ✦
            </div>

            <div class="hero-title">
                Investigate what changed.
            </div>

            <div class="hero-subtitle">
                Understand KPI movement, identify the strongest
                operational drivers and surface evidence-backed
                recommendations.
            </div>

        </div>
        """
    )

    st.html(
        f"""
        <div class="start-card">

            <div class="start-label">
                Selected KPI
            </div>

            <div class="start-kpi">
                {kpi}
            </div>

            <div class="start-description">
                Start an investigation to calculate the KPI,
                compare the selected period with its prior
                equivalent period, investigate operational
                drivers, and determine the most likely root cause.
            </div>

        </div>

        <div class="period-card">

            <div class="period-label">
                Selected Investigation Period
            </div>

            <div class="period-value">
                {start_period.strftime('%d %b %Y')}
                →
                {end_period.strftime('%d %b %Y')}
            </div>

            <div class="period-compare">
                Comparison:
                {
                    previous_start.strftime('%d %b %Y')
                    if valid_range else '—'
                }
                →
                {
                    previous_end.strftime('%d %b %Y')
                    if valid_range else '—'
                }
            </div>

        </div>
        """
    )

    if st.button(
        "🔎 Start Investigation",
        type="primary",
        use_container_width=True,
        disabled=not valid_range,
    ):

        with st.status(
            "Running investigation...",
            expanded=True,
        ) as status:

            st.write("📊 Calculating KPI for selected period...")
            st.write("🧠 Selecting investigation path...")
            st.write("🔍 Evaluating evidence...")
            st.write("🎯 Validating root cause...")
            st.write("✓ Preparing result...")

            try:

                investigation_result = run_investigation(
                    start_period=start_period,
                    end_period=end_period,
                )

                st.session_state.investigation_result = (
                    investigation_result
                )

                st.session_state.investigation_completed = True
                st.session_state.last_start_period = start_period
                st.session_state.last_end_period = end_period

                status.update(
                    label="✅ Investigation complete",
                    state="complete",
                    expanded=False,
                )

                st.rerun()

            except Exception as exc:

                status.update(
                    label="❌ Investigation failed",
                    state="error",
                    expanded=True,
                )

                st.error(
                    f"Investigation failed:\n\n{exc}"
                )

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
# RESULT DATA
# ============================================================

current_value = result.get("current_value")
previous_value = result.get("previous_value")
unit = result.get("unit", "%")

absolute_change = result.get("absolute_change")
relative_change = result.get("relative_change_pct")

direction = str(
    result.get("direction", "unknown")
).lower()

executive_summary = result.get(
    "executive_summary",
    "",
)

primary_root_cause = result.get(
    "primary_root_cause",
    "",
)

secondary_factors = result.get(
    "secondary_factors",
    [],
)

watch_items = result.get(
    "watch_items",
    [],
)

recommended_actions = result.get(
    "recommended_actions",
    [],
)

supporting_evidence = result.get(
    "supporting_evidence",
    [],
)

confidence = result.get(
    "confidence",
    {},
)

timeline = result.get(
    "investigation_timeline",
    [],
)

final_conclusion = result.get(
    "final_conclusion",
    "",
)

result_period = result.get(
    "period",
    {},
)

result_comparison = result.get(
    "comparison_period",
    {},
)


# ============================================================
# RESULT PERIOD
# ============================================================

if result_period:

    selected_start = result_period.get(
        "start",
        "",
    )

    selected_end = result_period.get(
        "end",
        "",
    )

    compare_start = result_comparison.get(
        "start",
        "",
    )

    compare_end = result_comparison.get(
        "end",
        "",
    )

    st.html(
        f"""
        <div class="period-card">

            <div class="period-label">
                Investigation Period
            </div>

            <div class="period-value">
                {selected_start}
                →
                {selected_end}
            </div>

            <div class="period-compare">
                Comparison:
                {compare_start}
                →
                {compare_end}
            </div>

        </div>
        """
    )


# ============================================================
# KPI PERFORMANCE
# ============================================================

# ============================================================
# KPI PERFORMANCE
# ============================================================

st.markdown("### KPI Performance")

if current_value is not None:

    if direction == "improving":

        status_text = "● IMPROVING"
        status_bg = "rgba(67,217,149,.08)"
        status_border = "rgba(67,217,149,.18)"
        status_color = "#6fe3a9"

    elif direction == "worsening":

        status_text = "● WORSENING"
        status_bg = "rgba(255,112,112,.08)"
        status_border = "rgba(255,112,112,.18)"
        status_color = "#ff9797"

    else:

        status_text = "● STABLE"
        status_bg = "rgba(229,196,92,.08)"
        status_border = "rgba(229,196,92,.18)"
        status_color = "#e5c45c"

    previous_text = (
        f"{previous_value:.2f}{unit}"
        if previous_value is not None
        else "N/A"
    )

    absolute_text = (
        f"{absolute_change:+.2f} pp"
        if absolute_change is not None
        else "N/A"
    )

    relative_text = (
        f"{relative_change:+.1f}%"
        if relative_change is not None
        else "N/A"
    )

    st.html(
        f"""
        <div class="kpi-card">

            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:40px;
                align-items:center;
            ">

                <!-- COMPLAINT RATE -->
                <div>

                    <div class="kpi-label">
                        Complaint Rate
                    </div>

                    <div class="kpi-value">
                        {current_value:.2f}
                        <span style="
                            font-size:18px;
                            color:#9aa5b5;
                            margin-left:3px;
                        ">
                            {unit}
                        </span>
                    </div>

                    <div class="kpi-meta">
                        Previous:
                        <b>{previous_text}</b>
                    </div>

                </div>


                <!-- CHANGE RATE -->
                <div style="
                    border-left:1px solid #293443;
                    padding-left:40px;
                ">

                    <div class="kpi-label">
                        Change Rate
                    </div>

                    <div style="
                        font-size:42px;
                        font-weight:850;
                        line-height:1;
                        margin-top:10px;
                        color:{status_color};
                    ">
                        {relative_text}
                    </div>

                    <div class="kpi-meta">
                        {absolute_text}
                        vs previous period
                    </div>

                </div>

            </div>


            <!-- STATUS -->
            <div
                class="status-pill"
                style="
                    background:{status_bg};
                    border:1px solid {status_border};
                    color:{status_color};
                    margin-top:22px;
                "
            >
                {status_text}
            </div>

        </div>
        """
    )

else:

    st.warning(
        "The investigation did not return a KPI value."
    )
# ============================================================
# EXECUTIVE FINDING
# ============================================================

st.markdown("### Executive Finding")

col1, col2 = st.columns(
    [1.3, 1],
    gap="medium",
)

with col1:

    st.html(
        f"""
        <div class="info-card">

            <div class="info-label">
                Key Finding
            </div>

            <div class="info-text">
                {executive_summary or "No finding returned."}
            </div>

        </div>
        """
    )

with col2:

    st.html(
        f"""
        <div class="info-card">

            <div class="info-label">
                Primary Driver
            </div>

            <div class="info-text">
                {primary_root_cause or "No driver returned."}
            </div>

        </div>
        """
    )


# ============================================================
# DRIVERS
# ============================================================

if secondary_factors:

    st.markdown("### Main Drivers")

    columns = st.columns(
        min(len(secondary_factors[:3]), 3)
    )

    for i, factor in enumerate(
        secondary_factors[:3]
    ):

        change = factor.get("change")
        factor_unit = factor.get("unit", "%")

        change_text = (
            f"{change:+.1f}{factor_unit}"
            if change is not None
            else "—"
        )

        with columns[i]:

            st.html(
                f"""
                <div class="driver">

                    <div class="driver-value">
                        {change_text}
                    </div>

                    <div class="driver-name">
                        {factor.get("name", "Driver")}
                    </div>

                    <div class="driver-description">
                        {factor.get("description", "")}
                    </div>

                </div>
                """
            )


# ============================================================
# WATCH ITEMS
# ============================================================

if watch_items:

    st.markdown("### Watch Items")

    columns = st.columns(
        min(len(watch_items[:3]), 3)
    )

    for i, item in enumerate(
        watch_items[:3]
    ):

        change = item.get("change")
        item_unit = item.get("unit", "%")

        change_text = (
            f"{change:+.1f}{item_unit}"
            if change is not None
            else "—"
        )

        with columns[i]:

            st.html(
                f"""
                <div class="risk">

                    <div class="risk-value">
                        {change_text}
                    </div>

                    <div class="risk-name">
                        {item.get("name", "Watch item")}
                    </div>

                    <div class="risk-description">
                        {item.get("description", "")}
                    </div>

                </div>
                """
            )


# ============================================================
# ACTION
# ============================================================

if recommended_actions:

    st.markdown("### Recommended Action")

    first_action = recommended_actions[0]

    st.html(
        f"""
        <div class="action">

            <div class="action-priority">
                {first_action.get("priority", "Action")}
            </div>

            <div class="action-text">
                {first_action.get("action", "")}
            </div>

        </div>
        """
    )

    if len(recommended_actions) > 1:

        with st.expander("View additional actions"):

            for action in recommended_actions[1:]:

                st.write(
                    f"**{action.get('priority', 'Action')}** — "
                    f"{action.get('action', '')}"
                )


# ============================================================
# DETAIL
# ============================================================

st.markdown("### Investigation Detail")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Evidence",
        "Root Cause",
        "Timeline",
        "Confidence",
    ]
)


with tab1:

    if supporting_evidence:

        for item in supporting_evidence:

            st.markdown(
                f"**Evidence:** "
                f"{item.get('evidence', '')}"
            )

            st.caption(
                item.get(
                    "why_it_matters",
                    "",
                )
            )

            st.divider()

    else:

        st.info(
            "No supporting evidence returned."
        )


with tab2:

    st.html(
        f"""
        <div class="info-card">

            <div class="info-label">
                Primary Root Cause
            </div>

            <div class="info-text">
                {primary_root_cause or "Not established."}
            </div>

        </div>
        """
    )

    if final_conclusion:

        st.markdown("#### Conclusion")

        st.info(
            final_conclusion
        )


with tab3:

    if timeline:

        for step in timeline:

            with st.expander(
                f"Step {step.get('step', '')} • "
                f"{step.get('tool', '')}"
            ):

                st.write(
                    f"**Why:** "
                    f"{step.get('reason', '')}"
                )

                st.write(
                    f"**Finding:** "
                    f"{step.get('finding', '')}"
                )

                st.write(
                    f"**Decision:** "
                    f"{step.get('decision', '')}"
                )

    else:

        st.info(
            "No investigation timeline returned."
        )


with tab4:

    st.metric(
        "Confidence",
        confidence.get(
            "level",
            "Unknown",
        ),
    )

    if confidence.get("reason"):

        st.write(
            confidence.get("reason")
        )

    if confidence.get("limitations"):

        st.warning(
            confidence.get("limitations")
        )

#===================

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
