import random

import pandas as pd
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

if "current_page" not in st.session_state:
    # "home" -> the real, implemented Complaint Rate flow (profile picker /
    #           investigation). Reached only via the InsightForge logo.
    # anything else -> a dummy placeholder page, one per sidebar link
    #           (including "Complaint Rate" itself, for now).
    st.session_state.current_page = "home"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #12161d;
    --panel: #1a2029;
    --border: #3a4557;
    --text: #f8fafc;
    --muted: #c3cad6;
    --purple: #8a7dff;
    --green: #4fe0a3;
    --red: #ff8080;
    --blue: #5cadff;
    --amber: #f0cd6e;
}

/* ============================================================
   SIDEBAR COLLAPSE / EXPAND CONTROL — better contrast
   ============================================================ */

[data-testid="stSidebarCollapseButton"] button,
[data-testid="collapsedControl"] button,
[data-testid="stSidebar"] [data-testid="baseButton-headerNoPadding"],
[data-testid="stSidebar"] button[kind="header"] {
    background: var(--purple) !important;
    border: none !important;
    border-radius: 8px !important;
    position: relative !important;
    z-index: 1500 !important;
    width: 34px !important;
    height: 34px !important;
    box-shadow: 0 4px 12px rgba(138,125,255,.5) !important;
}

[data-testid="stSidebarCollapseButton"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stSidebar"] svg,
[data-testid="stSidebar"] button svg,
[data-testid="collapsedControl"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
    width: 20px !important;
    height: 20px !important;
}

[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="collapsedControl"] button:hover,
[data-testid="stSidebar"] button[kind="header"]:hover {
    background: #9d92ff !important;
    box-shadow: 0 4px 16px rgba(138,125,255,.7) !important;
}

html,
body,
[data-testid="stAppViewContainer"] {
    background: var(--bg);
}

[data-testid="stHeader"] {
    background: var(--bg);
}

.block-container,
[data-testid="stAppViewContainer"] .block-container,
[data-testid="stMain"] .block-container {
    max-width: 1140px !important;
    width: 1140px !important;
    padding-top: 2rem;
    padding-bottom: 3rem;
    margin-left: 260px !important;
    margin-right: auto !important;
    flex: none !important;
}

[data-testid="stSidebar"] {
    background: #151a22;
    border-right: 1px solid var(--border);
}

.sidebar-logo {
    color: #ffffff;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-top: 4rem;
}

.sidebar-subtitle {
    color: #a0aaba;
    font-size: 13px;
}

/* Logo acts as a home/navigation button now — style the button to
   look like plain text/logo instead of an obvious button */
.st-key-logo_home_btn {
    position: relative !important;
    z-index: 99999 !important;
}

.st-key-logo_home_btn button {
    background: #151a22 !important;
    border: none !important;
    padding: 0 !important;
    color: #ffffff !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    min-height: unset !important;
    margin-top: 4rem;
    box-shadow: none !important;
    position: relative !important;
    z-index: 99999 !important;
}

.st-key-logo_home_btn button:hover {
    color: #c9c2ff !important;
    background: #151a22 !important;
    border: none !important;
}

.st-key-logo_home_btn button p {
    font-size: 22px !important;
    font-weight: 800 !important;
}

.dash-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 14px;
    margin-bottom: 5px;
    border-left: 3px solid transparent;
}

.dash-link.active {
    background: rgba(138,125,255,.14);
    border: 1px solid rgba(138,125,255,.32);
    border-left: 3px solid var(--purple);
    color: #ffffff;
    font-weight: 700;
}

.dash-link.disabled {
    color: #7c8494;
}

.dash-link-soon {
    font-size: 14px;
    color: #7c8494;
    margin-left: auto;
}

/* Dashboard nav buttons — replace static divs so every entry is
   genuinely clickable, styled to look like the original dash-link */
.st-key-dashnav_complaint button,
.st-key-dashnav_debt button,
.st-key-dashnav_outage button,
.st-key-dashnav_billing button {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    gap: 10px;
    padding: 10px 12px !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    margin-bottom: 5px;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-left: 3px solid transparent !important;
    color: #c3cad6 !important;
    font-weight: 500 !important;
}

.st-key-dashnav_complaint button:hover,
.st-key-dashnav_debt button:hover,
.st-key-dashnav_outage button:hover,
.st-key-dashnav_billing button:hover {
    background: rgba(138,125,255,.08) !important;
    border-color: rgba(138,125,255,.2) !important;
}

.live-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--green);
    margin-left: auto;
    animation: pulse-dot 1.8s ease-in-out infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}

.sidebar-note {
    padding: 12px;
    background: #101722;
    border: 1px solid #222c39;
    border-radius: 12px;
    color: #d9e1ec;
    font-size: 14px;
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
    font-size: 14px;
}

.header-status {
    color: #6fe1aa;
    font-size: 14px;
    font-weight: 700;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(67,225,170,.05);
    border: 1px solid rgba(67,225,170,.15);
}

/* ============================================================
   DEFAULT BUTTON STYLING — fixes the white/unreadable
   background Streamlit uses out of the box. Profile cards and
   the chat button use more specific selectors and are unaffected.
   ============================================================ */

.stButton button,
.stFormSubmitButton button {
    background: #1f2733 !important;
    color: #f8fafc !important;
    border: 1px solid #3a4557 !important;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: #2a3444 !important;
    border-color: rgba(138,125,255,.6) !important;
    color: #ffffff !important;
}

.stButton button p,
.stFormSubmitButton button p {
    color: inherit !important;
}

/* ============================================================
   TOP CONTROL BAR (KPI / period / new investigation)
   ============================================================ */

.st-key-topbar_wrap {
    background: #1a2029;
    border: 1px solid #3a4557;
    border-radius: 14px;
    padding: 4px 16px 10px;
    position: fixed;
    top: 3.6rem;
    left: 340px;
    width: calc(100% - 340px - 4rem);
    max-width: 1400px;
    z-index: 999;
    box-shadow: 0 8px 20px rgba(0,0,0,.35);
}

/* Spacer so fixed-position content doesn't sit under the bar.
   Height tracks the topbar's ACTUAL rendered height live (via JS
   below) plus a small buffer — a hardcoded guess kept drifting out
   of sync whenever padding/font-size changed and caused overlap. */
.st-key-topbar_spacer {
    height: max(200px, calc(var(--topbar-h, 118px) + 16px));
}

.topbar-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 10px 0 6px;
}

.topbar-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 13px;
}

.topbar-badge.period {
    background: rgba(138,125,255,.16);
    border: 1px solid rgba(138,125,255,.34);
    color: #d6d0ff;
}

.topbar-badge.compare {
    background: #202836;
    border: 1px solid #3a4557;
    color: #c3cad6;
}

.topbar-summary {
    color: #d9e1ec;
    font-size: 14px;
    padding: 10px 4px 2px;
}

.st-key-topbar_wrap [data-testid="stSelectbox"],
.st-key-topbar_wrap [data-testid="stDateInput"] {
    min-width: 100% !important;
}

.st-key-topbar_wrap [data-baseweb="select"] > div,
.st-key-topbar_wrap [data-baseweb="input"] > div {
    min-height: 44px !important;
    font-size: 14px !important;
}

.st-key-topbar_wrap button {
    min-height: 44px !important;
    font-size: 14px !important;
}

/* ============================================================
   PROFILE GRID
   ============================================================ */

.hero {
    text-align: center;
    padding: 82px 10px 10px;
}

.hero-icon {
    width: 56px;
    height: 56px;
    margin: 0 auto 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    background: rgba(138,125,255,.14);
    border: 1px solid rgba(138,125,255,.3);
    color: #c9c2ff;
    font-size: 24px;
    box-shadow: 0 6px 18px rgba(138,125,255,.15);
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
    color: #c3cad6;
    font-size: 15px;
    line-height: 1.7;
}
.st-key-profile_grid {
    width: min(calc(100vw - var(--if-sidebar-w, 244px) - 4rem), 1400px) !important;
    max-width: 1400px !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

.st-key-profile_grid button {
    width: 100% !important;
    height: 118px !important;
    border-radius: 999px !important;
    background: #1a2029 !important;
    border: 1px solid #3a4557 !important;
    color: #f8fafc !important;
    font-size: 15px !important;
    font-weight: 650 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    white-space: normal !important;
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease !important;
}

.st-key-profile_grid button:hover {
    transform: translateY(-3px);
    border-color: rgba(138,125,255,.5) !important;
    box-shadow: 0 10px 24px rgba(0,0,0,.35) !important;
}

.st-key-profile_grid button p {
    font-size: 15px !important;
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
    font-size: 14px;
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
    background: #1a2029;
    border: 1px solid #3a4557;
    border-radius: 14px;
    text-align: center;
}

.period-label {
    color: #c3cad6;
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.period-value {
    color: white;
    font-size: 15px;
    font-weight: 650;
    margin-top: 5px;
}

.period-compare {
    color: #d9e1ec;
    font-size: 14px;
    margin-top: 4px;
}

.kpi-card {
    background: linear-gradient(145deg, #1c2431, #171e29);
    border: 1px solid #3a4557;
    border-radius: 18px;
    padding: 25px 28px;
    margin-top: 20px;
    box-shadow: 0 10px 26px rgba(0,0,0,.22);
}

.kpi-label {
    color: #c3cad6;
    font-size: 14px;
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
    font-size: 14px;
    margin-top: 9px;
}

.status-pill {
    display: inline-block;
    margin-top: 13px;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 800;
}

.info-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 20px;
    min-height: 145px;
    box-shadow: 0 6px 16px rgba(0,0,0,.18);
}

.info-label {
    color: #c3cad6;
    font-size: 14px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .9px;
}

.info-text {
    color: #eef2f7;
    font-size: 15px;
    line-height: 1.7;
    margin-top: 9px;
}

.driver {
    background: #12271e;
    border: 1px solid #275a45;
    border-radius: 14px;
    padding: 18px;
    min-height: 120px;
    box-shadow: 0 6px 16px rgba(0,0,0,.16);
}

.driver-value {
    color: #70e3a7;
    font-size: 24px;
    font-weight: 850;
}

.driver-name {
    color: white;
    font-size: 14px;
    font-weight: 700;
    margin-top: 5px;
}

.driver-description {
    color: #aebbb5;
    font-size: 14px;
    line-height: 1.5;
    margin-top: 7px;
}

.risk {
    background: #2b1a1c;
    border: 1px solid #6b3a41;
    border-radius: 14px;
    padding: 18px;
    min-height: 120px;
    box-shadow: 0 6px 16px rgba(0,0,0,.16);
}

.risk-value {
    color: #ff8f8f;
    font-size: 24px;
    font-weight: 850;
}

.risk-name {
    color: white;
    font-size: 14px;
    font-weight: 700;
    margin-top: 5px;
}

.risk-description {
    color: #c0adb1;
    font-size: 14px;
    line-height: 1.5;
    margin-top: 7px;
}

.action {
    background: #1a2029;
    border: 1px solid #3a4557;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 6px 16px rgba(0,0,0,.18);
}

.action-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 13px;
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
    font-size: 15px;
    line-height: 1.6;
    margin-top: 8px;
}

.confidence-pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 14px;
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
    font-size: 14px;
    text-align: center;
    border-top: 1px solid var(--border);
    padding-top: 15px;
    margin-top: 30px;
}

/* ============================================================
   DUMMY DASHBOARD PLACEHOLDER
   ============================================================ */

.dummy-page-header {
    max-width: 1000px;
    margin: 2rem auto 1.5rem;
    text-align: center;
}

.dummy-page-icon {
    font-size: 36px;
    margin-bottom: 0.75rem;
}

.dummy-page-title {
    color: #f8fafc;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.dummy-page-text {
    color: #c3cad6;
    font-size: 13px;
    line-height: 1.6;
    max-width: 640px;
    margin: 0 auto;
}

.dummy-metric {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 6px 16px rgba(0,0,0,.16);
}

.dummy-metric-label {
    color: #c3cad6;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .8px;
}

.dummy-metric-value {
    color: #f8fafc;
    font-size: 26px;
    font-weight: 800;
    margin-top: 6px;
}

.dummy-metric-delta {
    font-size: 12px;
    margin-top: 4px;
    font-weight: 600;
}

.dummy-metric-delta.up {
    color: #ff9797;
}

.dummy-metric-delta.down {
    color: #6fe3a9;
}

.dummy-chart-wrap {
    max-width: 1000px;
    margin: 1.5rem auto 0;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 6px 16px rgba(0,0,0,.16);
}

.dummy-chart-title {
    color: #c3cad6;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .8px;
    margin-bottom: 10px;
}

/* ============================================================
   STYLED SECTION HEADERS
   ============================================================ */

.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 30px 0 4px;
}

.section-header-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(138,125,255,.18);
    border: 1px solid rgba(138,125,255,.36);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}

.section-header-title {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.2px;
}

.section-underline {
    height: 2px;
    width: 46px;
    margin: 8px 0 16px 38px;
    background: linear-gradient(90deg, var(--purple), transparent);
    border-radius: 2px;
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
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 8px;
}

.suggested-subtitle {
    color: #d9e1ec;
    font-size: 14px;
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
    font-size: 13px;
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

[data-testid="stExpander"] {
    background: #1a2029 !important;
    border: 1px solid #3a4557 !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
}

[data-testid="stExpander"] > details,
[data-testid="stExpander"] summary,
[data-testid="stExpanderDetails"],
[data-testid="stExpander"] [data-testid="stVerticalBlock"] {
    background: #1a2029 !important;
    color: #f8fafc !important;
}

[data-testid="stExpanderDetails"] {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

[data-testid="stExpander"] summary {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

[data-testid="stExpander"] summary {
    font-weight: 650 !important;
    position: relative !important;
    padding-right: 36px !important;
}

[data-testid="stExpander"] summary::after {
    content: "⌄";
    position: absolute;
    right: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;
    font-weight: 700;
    color: #c9c2ff;
    transition: transform .15s ease;
}

[data-testid="stExpander"] details[open] > summary::after {
    transform: translateY(-50%) rotate(180deg);
}

[data-testid="stExpander"] summary p {
    color: #f8fafc !important;
    font-weight: 650 !important;
}

[data-testid="stExpander"] label,
[data-testid="stExpander"] label p,
[data-testid="stExpander"] [data-testid="stWidgetLabel"] p {
    color: #d6dbe3 !important;
    font-size: 13px !important;
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


def section_header(icon, title):
    """Styled replacement for plain st.markdown('### ...') headings —
    icon chip + bold title + thin accent underline."""
    st.html(
        f"""
        <div class="section-header">
            <span class="section-header-icon">{icon}</span>
            <span class="section-header-title">{title}</span>
        </div>
        <div class="section-underline"></div>
        """
    )


def go_home():
    """Reset to the main InsightForge landing page (Complaint Rate profile picker).
    This is now the ONLY way to reach the real flow — every sidebar
    dashboard link, including Complaint Rate, is a dummy page for now."""
    st.session_state.current_page = "home"
    st.session_state.stage = "profile"
    st.session_state.investigation_result = None
    st.session_state.investigation_completed = False
    st.session_state.action_audience = None
    st.session_state.last_start_period = None
    st.session_state.last_end_period = None
    st.session_state.chat_history = []


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

# All 4 dashboard links are dummy pages for now, including Complaint
# Rate — the real flow is reached only via the InsightForge logo.
# Each entry also carries fabricated demo metrics/chart config purely
# for visual flavor — NOT real data, since these dashboards aren't built.
DUMMY_DASHBOARDS = {
    "complaint_rate": {
        "key": "dashnav_complaint", "label": "Complaint Rate", "icon": "💬",
        "metrics": [
            ("Total complaints", "1,284", "+6.2%", "up"),
            ("Escalation rate", "6.4%", "+1.1pp", "up"),
            ("Avg resolution time", "5.2 days", "-0.4 days", "down"),
        ],
        "chart_label": "Weekly complaint volume (demo data)",
        "chart_range": (60, 140),
    },
    "debt": {
        "key": "dashnav_debt", "label": "Debt %", "icon": "💳",
        "metrics": [
            ("Total debt", "£2.4M", "+3.8%", "up"),
            ("Accounts in arrears", "1,204", "+2.1%", "up"),
            ("Avg debt / account", "£340", "-1.5%", "down"),
        ],
        "chart_label": "Weekly debt balance (demo data)",
        "chart_range": (200, 320),
    },
    "outage": {
        "key": "dashnav_outage", "label": "Outage Impact", "icon": "⚡",
        "metrics": [
            ("Outages this month", "12", "+2", "up"),
            ("Avg duration", "42 min", "-6 min", "down"),
            ("Customers affected", "8,900", "+14%", "up"),
        ],
        "chart_label": "Weekly outage count (demo data)",
        "chart_range": (2, 20),
    },
    "billing": {
        "key": "dashnav_billing", "label": "Billing Accuracy", "icon": "🧾",
        "metrics": [
            ("Estimated bills", "6.3%", "-0.8pp", "down"),
            ("Billing disputes", "210", "+18", "up"),
            ("Accuracy score", "94.1%", "+0.6pp", "down"),
        ],
        "chart_label": "Weekly billing disputes (demo data)",
        "chart_range": (10, 60),
    },
}


# ============================================================
# LEFT DRAWER: DASHBOARD LINKS
# (native Streamlit sidebar - collapsible out of the box)
# ============================================================

with st.sidebar:

    if st.button("✦ InsightForge", key="logo_home_btn"):
        go_home()
        st.rerun()

    st.markdown('<div class="sidebar-subtitle">AI Operations Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Dashboards")

    # Active-state styling is injected as CSS keyed to each button's own
    # .st-key-<key> wrapper (the pattern already used for the topbar/profile
    # cards) — NOT by wrapping raw <div> tags around st.button() calls,
    # which don't actually nest in the DOM since each st.* call renders as
    # its own separate element.
    if st.session_state.current_page in DUMMY_DASHBOARDS:
        active_key = DUMMY_DASHBOARDS[st.session_state.current_page]["key"]
        st.markdown(
            f"""
            <style>
            .st-key-{active_key} button {{
                background: rgba(138,125,255,.14) !important;
                border: 1px solid rgba(138,125,255,.32) !important;
                border-left: 3px solid var(--purple) !important;
                color: #ffffff !important;
                font-weight: 700 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    for dash_id, dash in DUMMY_DASHBOARDS.items():
        if st.button(f"{dash['icon']} {dash['label']}", key=dash["key"], use_container_width=True):
            st.session_state.current_page = dash_id
            st.rerun()

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
# DUMMY DASHBOARD PAGE (shared placeholder, now with demo
# metrics + a chart so it reads as an actual dashboard, not
# just an empty card. All numbers here are fabricated for
# visual demo purposes only — no real data backs these dashboards.)
# ============================================================

if st.session_state.current_page != "home":

    dash_id = st.session_state.current_page
    dash_meta = DUMMY_DASHBOARDS.get(dash_id)

    if dash_meta is None:
        dash_meta = {
            "label": "Dashboard", "icon": "📊",
            "metrics": [("Metric A", "—", "", "up"), ("Metric B", "—", "", "up"), ("Metric C", "—", "", "up")],
            "chart_label": "Demo data", "chart_range": (10, 100),
        }

    st.html(
        f"""
        <div class="dummy-page-header">
            <div class="dummy-page-icon">{dash_meta['icon']}</div>
            <div class="dummy-page-title">{dash_meta['label']}</div>
            <div class="dummy-page-text">
                Demo dashboard — the numbers below are placeholder data
                to show what this page will look like. Use the
                ✦ InsightForge logo in the sidebar to return to the
                live investigation flow.
            </div>
        </div>
        """
    )

    metric_cols = st.columns(3)
    for col, (label, value, delta, direction) in zip(metric_cols, dash_meta["metrics"]):
        with col:
            st.html(
                f"""
                <div class="dummy-metric">
                    <div class="dummy-metric-label">{label}</div>
                    <div class="dummy-metric-value">{value}</div>
                    <div class="dummy-metric-delta {direction}">{delta} vs last period</div>
                </div>
                """
            )

    st.markdown('<div class="dummy-chart-wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="dummy-chart-title">{dash_meta["chart_label"]}</div>', unsafe_allow_html=True)

    low, high = dash_meta["chart_range"]
    chart_df = pd.DataFrame(
        {"Value": [random.randint(low, high) for _ in range(8)]},
        index=[f"Wk {i + 1}" for i in range(8)],
    )
    st.bar_chart(chart_df, height=220)

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ============================================================
# TOP CONTROL BAR (KPI / period / new investigation)
# Collapsed by default once an investigation is running,
# expanded by default on the profile-picker screen.
# ============================================================

default_expanded = False

# Sizes the spacer below the topbar to the topbar's real rendered
# height, since that changes with expanded/collapsed state and a
# hardcoded guess kept drifting out of sync.
st.markdown(
    """
    <script>
    (function () {
        function syncLayout() {
            const topbar = document.querySelector('.st-key-topbar_wrap');
            if (topbar) {
                const topbarHeight = topbar.getBoundingClientRect().height;
                document.documentElement.style.setProperty('--topbar-h', topbarHeight + 'px');
            }
        }
        const observer = new MutationObserver(syncLayout);
        observer.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['style', 'class'] });
        window.addEventListener('resize', syncLayout);
        syncLayout();
        setInterval(syncLayout, 400);
    })();
    </script>
    """,
    unsafe_allow_html=True,
)

with st.container(key="topbar_wrap"):

    with st.expander("Investigation controls", expanded=default_expanded):

        col_kpi, col_start, col_end, col_spacer, col_reset = st.columns(
            [1.9, 1.3, 1.3, 0.6, 1.4]
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
            st.markdown(
                '<div data-testid="stWidgetLabel" style="visibility:hidden;"><p>Action</p></div>',
                unsafe_allow_html=True,
            )
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

with st.container(key="topbar_spacer"):
    st.write("")


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

section_header("📊", "KPI Performance")

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

section_header("🧠", "Executive Finding")

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

    section_header("📈", "Main Drivers")

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

    section_header("⚠️", "Watch Items")

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

    section_header("✅", "Recommended Action")

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

section_header("🔍", "Investigation Detail")

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