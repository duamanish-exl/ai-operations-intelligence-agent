import streamlit as st
import json
from datetime import datetime

from orchestration import run_investigation


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Operations Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .status-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🤖 Operations AI")

    st.markdown("---")

    st.markdown("### Investigation")

    kpi = st.selectbox(
        "Select KPI",
        [
            "Complaint Rate",
        ]
    )

    st.markdown("---")

    st.markdown("### Investigation Settings")

    max_steps = st.number_input(
        "Maximum investigation steps",
        min_value=1,
        max_value=3,
        value=3
    )

    st.markdown("---")

    st.caption(
        "AI Operations Intelligence Agent"
    )

    st.caption(
        "Powered by OpenRouter + Claude"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 AI Operations Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Investigate KPI anomalies and identify evidence-based root causes.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# TOP INFORMATION CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        label="📊 Selected KPI",
        value=kpi
    )

with col2:

    st.metric(
        label="🔍 Investigation",
        value="AI Powered"
    )

with col3:

    st.metric(
        label="🧠 Investigation Steps",
        value=f"{max_steps}"
    )

with col4:

    st.metric(
        label="⚡ Status",
        value="Ready"
    )


st.markdown("---")


# ============================================================
# INVESTIGATION BUTTON
# ============================================================

st.markdown(
    "### 🔎 Run Investigation"
)

st.write(
    f"Investigate the current **{kpi}** using the available "
    "business investigation tools."
)


if st.button(
    "🚀 Start Investigation",
    type="primary",
    use_container_width=True
):

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    with st.status(
        "Running AI investigation...",
        expanded=True
    ) as status:

        st.write("📊 Calculating KPI...")

        st.write("📅 Determining investigation period...")

        st.write("🧠 AI Operations Agent analysing the KPI...")

        st.write("🔍 Selecting investigation tools...")

        try:

            result = run_investigation()

            status.update(
                label="✅ Investigation completed",
                state="complete",
                expanded=False
            )

        except Exception as e:

            status.update(
                label="❌ Investigation failed",
                state="error",
                expanded=True
            )

            st.error(
                f"Error while running investigation:\n\n{str(e)}"
            )

            result = None


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    if result:

        st.markdown("---")

        st.markdown(
            "## 📋 Investigation Report"
        )

        st.markdown(result)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    f"AI Operations Intelligence • "
    f"{datetime.now().strftime('%d %b %Y %H:%M')}"
)
