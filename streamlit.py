import streamlit as st
from backend import investigate

st.set_page_config(
    page_title="AI Operations Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Operations Intelligence Agent")
st.markdown("Investigate changes in business KPIs using AI.")
kpi = st.sidebar.selectbox(
    "Select KPI",
    ["Debt %", "Complaint %"]
)

st.sidebar.header("Input KPI Data")

previous_debt = st.sidebar.number_input(
    "Previous Debt (%)",
    min_value=0.0,
    value=30.0,
    step=0.1
)

current_debt = st.sidebar.number_input(
    "Current Debt (%)",
    min_value=0.0,
    value=34.0,
    step=0.1
)

if kpi == "Debt %":
    previous_value = st.sidebar.number_input(
        "Previous Debt %",
        value=30.0
    )

    current_value = st.sidebar.number_input(
        "Current Debt %",
        value=34.0
    )

elif kpi == "Complaint %":
    previous_value = st.sidebar.number_input(
        "Previous Complaint %",
        value=5.0
    )

    current_value = st.sidebar.number_input(
        "Current Complaint %",
        value=7.0
    )

payment_change = st.sidebar.number_input(
    "Payment Change (%)",
    value=12.0,
    step=0.1
)

billing_change = st.sidebar.number_input(
    "Billing Change (%)",
    value=22.0,
    step=0.1
)

consumption_change = st.sidebar.number_input(
    "Consumption Change (%)",
    value=18.0,
    step=0.1
)

st.subheader("Current KPI Values")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Previous Debt",
        f"{previous_debt:.2f}%"
    )

with col2:
    delta = current_debt - previous_debt
    st.metric(
        "Current Debt",
        f"{current_debt:.2f}%",
        delta=f"{delta:.2f}%"
    )

if st.button("🔍 Investigate", use_container_width=True):

    with st.spinner("Investigating..."):

        result = investigate(
            kpi,
            previous_debt,
            current_debt,
            payment_change,
            billing_change,
            consumption_change
        )

    st.success("Investigation Complete")

    st.markdown(result)