"""
GuardianAI v2 — AI Emergency Detection & Response
New Theme  : White · Navy Blue · Black
New Feature: Auto detection panel, voice keyword via browser mic, 
"Are you okay?" verification, countdown → real SMS
"""

import streamlit as st
import time
import random
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import database as db
import utils as ut
from sms_manager import send_alerts_to_all, build_message

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="GuardianAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
#  GLOBAL CSS  —  White · Navy Blue · Black
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif!important; }

/* ── Background & text ── */
.stApp               { background:#F8FAFF; color:#0A1628; }
section[data-testid="stSidebar"] { background:#0A1628!important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container     { padding:0!important; max-width:100%!important; }

/* ── Top nav bar ── */
.g-topbar {
    background:linear-gradient(90deg,#0A1628 0%,#1A2F5E 100%);
    padding:14px 28px;
    border-bottom:2px solid #2563EB;
    display:flex; align-items:center; justify-content:space-between;
}
.g-logo { font-size:20px;font-weight:800;color:#FFFFFF;letter-spacing:-0.5px; }
.g-logo span { color:#60A5FA; }

/* ── Cards ── */
.g-card {
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:14px;
    padding:20px 22px;
    margin-bottom:14px;
    box-shadow:0 1px 6px rgba(10,22,40,0.07);
}
.g-card-navy {
    background:#0A1628;
    border:1px solid #1A2F5E;
    border-radius:14px;
    padding:20px 22px;
    margin-bottom:14px;
}
.g-card-danger {
    background:#FFF5F5;
    border:1.5px solid #EF4444;
    border-radius:14px;
    padding:20px 22px;
    margin-bottom:14px;
}
.g-card-warn {
    background:#FFFBEB;
    border:1.5px solid #F59E0B;
    border-radius:14px;
    padding:20px 22px;
    margin-bottom:14px;
}
.g-card-safe {
    background:#F0FDF4;
    border:1.5px solid #22C55E;
    border-radius:14px;
    padding:20px 22px;
    margin-bottom:14px;
}
.g-card-blue {
    background:#EFF6FF;
    border:1.5px solid #3B82F6;
    border-radius:14px;
    padding:20px 22px;
    margin-bottom:14px;
}

/* ── Stat cards ── */
.stat-card {
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:18px 16px;
    text-align:center;
    box-shadow:0 1px 4px rgba(10,22,40,0.06);
}
.stat-val { font-size:30px;font-weight:800; }
.stat-lbl { font-size:11px;color:#64748B;margin-top:4px;font-weight:600;
            text-transform:uppercase;letter-spacing:0.5px; }

/* ── Buttons ── */
div.stButton>button {
    border-radius:10px!important;
    font-weight:600!important;
    font-family:'Inter',sans-serif!important;
    transition:all 0.15s!important;
    border:none!important;
}
div.stButton>button[kind="primary"] {
    background:linear-gradient(135deg,#1E40AF,#2563EB)!important;
    color:white!important;
}
div.stButton>button:hover { opacity:0.88!important; transform:translateY(-1px)!important; }

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background:#F8FAFF!important;
    border:1.5px solid #CBD5E1!important;
    border-radius:9px!important;
    color:#0A1628!important;
    font-family:'Inter',sans-serif!important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color:#2563EB!important;
    box-shadow:0 0 0 3px rgba(37,99,235,0.12)!important;
}
label[data-testid="stWidgetLabel"] p {
    color:#334155!important; font-size:13px!important; font-weight:600!important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] button {
    color:#64748B!important; font-weight:600!important; border-radius:8px 8px 0 0!important;
    background:transparent!important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color:#1E40AF!important; border-bottom:2px solid #2563EB!important;
    background:#EFF6FF!important;
}

/* ── Badges ── */
.badge {
    display:inline-block; padding:3px 10px; border-radius:999px;
    font-size:11px; font-weight:700; letter-spacing:0.5px; text-transform:uppercase;
}
.badge-safe    { background:#DCFCE7;color:#16A34A;border:1px solid #22C55E; }
.badge-warning { background:#FEF9C3;color:#B45309;border:1px solid #F59E0B; }
.badge-danger  { background:#FEE2E2;color:#DC2626;border:1px solid #EF4444; }
.badge-blue    { background:#DBEAFE;color:#1D4ED8;border:1px solid #3B82F6; }

/* ── Contact card ── */
.contact-card {
    background:#FFFFFF; border:1px solid #E2E8F0; border-radius:11px;
    padding:13px 15px; margin-bottom:9px;
    display:flex; align-items:center; gap:13px;
    box-shadow:0 1px 3px rgba(10,22,40,0.05);
}
.contact-avatar {
    width:40px; height:40px;
    background:linear-gradient(135deg,#1E40AF,#3B82F6);
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-weight:800; font-size:15px; color:white; flex-shrink:0;
}
.contact-name { font-weight:700; font-size:14px; color:#0A1628; }
.contact-sub  { font-size:12px; color:#64748B; margin-top:2px; }

/* ── Page title ── */
.page-title { font-size:24px;font-weight:800;color:#0A1628;margin-bottom:3px; }
.page-sub   { font-size:13px;color:#64748B;margin-bottom:20px; }

/* ── Divider ── */
.g-divider { border:none;border-top:1px solid #E2E8F0;margin:16px 0; }

/* ── Log row ── */
.log-row {
    display:flex; align-items:center; gap:12px;
    padding:11px 0; border-bottom:1px solid #E2E8F0;
}
.log-icon { font-size:19px; }
.log-title { font-weight:600; font-size:13px; color:#0A1628; }
.log-sub   { font-size:11px; color:#64748B; margin-top:2px; }
.log-score { font-weight:800; font-size:17px; }

/* ── Auto detection panel ── */
.auto-panel {
    background:linear-gradient(135deg,#0A1628 0%,#1E3A5F 100%);
    border:2px solid #2563EB; border-radius:16px;
    padding:24px; margin-bottom:16px; text-align:center;
}
.auto-status {
    font-size:13px; color:#93C5FD; font-weight:600;
    text-transform:uppercase; letter-spacing:1px;
}
.auto-event {
    font-size:20px; font-weight:800; color:#FFFFFF; margin:10px 0 4px;
}
.pulse-ring {
    display:inline-block; width:14px; height:14px;
    background:#22C55E; border-radius:50%;
    animation:pulse 1.4s infinite;
    box-shadow:0 0 0 0 rgba(34,197,94,0.5);
    vertical-align:middle; margin-right:8px;
}
@keyframes pulse {
  0%,100% { box-shadow:0 0 0 0 rgba(34,197,94,0.5); }
  50%      { box-shadow:0 0 0 10px rgba(34,197,94,0); }
}
.pulse-ring-red {
    display:inline-block; width:14px; height:14px;
    background:#EF4444; border-radius:50%;
    animation:pulse-red 0.8s infinite;
    vertical-align:middle; margin-right:8px;
}
@keyframes pulse-red {
  0%,100% { box-shadow:0 0 0 0 rgba(239,68,68,0.6); }
  50%      { box-shadow:0 0 0 12px rgba(239,68,68,0); }
}

/* countdown */
.big-countdown { font-size:80px;font-weight:900;color:#EF4444;line-height:1; }
.countdown-lbl { font-size:13px;color:#64748B;margin-top:4px; }

/* voice widget */
.voice-box {
    background:#0A1628; border-radius:12px; padding:18px;
    border:1.5px dashed #3B82F6; margin-bottom:12px; text-align:center;
}

/* scrollbar */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:#F8FAFF; }
::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ── DB INIT ───────────────────────────────────────────────────
db.init_db()


# ── STATE HELPERS ─────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "home",
        "risk_events": [],
        "emergency_active": False,
        "awaiting_okay": False,      # "Are you okay?" stage
        "countdown_start": None,
        "countdown_seconds": 60,
        "sms_results": [],
        "sms_message": "",
        "alert_lat": None,
        "alert_lon": None,
        "auto_running": False,
        "auto_trigger": None,
        "detection_log": [],
        "edit_contact_id": None,
        "twilio_sid": "",
        "twilio_token": "",
        "twilio_from": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_logged_in():
    return st.session_state.get("user") is not None


def current_user():
    return st.session_state.get("user", {})


def uid():
    return current_user().get("id")


def logout():
    keys = list(st.session_state.keys())
    for k in keys:
        del st.session_state[k]
    st.rerun()


def nav(page):
    st.session_state["page"] = page
    st.rerun()


def trigger_event(event_type):
    """Add a risk event and check if emergency should fire."""
    events = st.session_state["risk_events"]
    if event_type not in events:
        events.append(event_type)
    score = ut.calculate_risk(events)

    # Log it
    st.session_state["detection_log"].insert(0, {
        "type": event_type,
        "score": score,
        "time": datetime.now().strftime("%H:%M:%S"),
    })

    # If score crosses WARNING → ask "Are you okay?"
    if score >= 41 and not st.session_state["awaiting_okay"] \
            and not st.session_state["emergency_active"]:
        st.session_state["awaiting_okay"] = True
        st.session_state["auto_trigger"]  = event_type
        st.session_state["countdown_start"] = time.time()


# ══════════════════════════════════════════════════════════════
#  NAV BAR
# ══════════════════════════════════════════════════════════════
def render_navbar():
    user = current_user()
    st.markdown(f"""
    <div class="g-topbar">
        <div class="g-logo">🛡️ Guardian<span>AI</span></div>
        <div style="font-size:13px;color:#93C5FD">
            Welcome, <strong style="color:white">{user.get('full_name','').split()[0]}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(6)
    pages = [
        ("🏠", "Home",       "home"),
        ("🤖", "Auto Detect","auto"),
        ("📋", "Contacts",   "contacts"),
        ("🚨", "Emergency",  "emergency"),
        ("📊", "Dashboard",  "dashboard"),
        ("⚙️", "Settings",   "settings"),
    ]
    for col, (icon, label, key) in zip(cols, pages):
        with col:
            active = st.session_state.get("page") == key
            style = "background:#1E3A5F;color:white;" if active else "color:#64748B;"
            if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                nav(key)

    st.markdown("<hr style='border:none;border-top:2px solid #E2E8F0;margin:0 0 20px 0'>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════
def page_login():
    # Top bar (minimal)
    st.markdown("""
    <div class="g-topbar" style="justify-content:center;margin-bottom:0">
        <div class="g-logo">🛡️ Guardian<span>AI</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
        <div style='text-align:center;margin-bottom:28px'>
            <div style='font-size:22px;color:#0A1628;font-weight:800'>
                AI-Powered Emergency Response
            </div>
            <div style='font-size:13px;color:#64748B;margin-top:6px'>
                Your safety guardian — always watching, always ready
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "✨ Sign Up"])

        with tab1:
            phone = st.text_input("📱 Phone Number", placeholder="+92 300 0000000", key="lp")
            pw    = st.text_input("🔒 Password", type="password", key="lpw")
            if st.button("Login →", key="btn_login", use_container_width=True, type="primary"):
                if phone and pw:
                    user = db.login_user(phone.strip(), pw)
                    if user:
                        st.session_state["user"] = user
                        init_state()
                        st.success(f"Welcome back, {user['full_name']}! 👋")
                        time.sleep(0.7)
                        st.rerun()
                    else:
                        st.error("❌ Wrong phone or password.")
                else:
                    st.warning("Fill all fields.")

        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                sn  = st.text_input("👤 Full Name *", key="sn")
                sp  = st.text_input("📱 Phone *", key="sp")
                se  = st.text_input("✉️ Email", key="se")
            with c2:
                sw  = st.text_input("🔒 Password *", type="password", key="sw")
                sw2 = st.text_input("🔒 Confirm *",  type="password", key="sw2")
                sb  = st.selectbox("🩸 Blood Group", ut.BLOOD_GROUPS, key="sb")
            sa = st.text_input("📍 Home Address", key="sa")
            if st.button("Create Account →", key="btn_su", use_container_width=True, type="primary"):
                if not all([sn, sp, sw, sw2]):
                    st.warning("Fill required fields.")
                elif sw != sw2:
                    st.error("Passwords don't match.")
                elif len(sw) < 6:
                    st.warning("Password must be 6+ chars.")
                else:
                    ok, msg = db.create_user(sn, sp.strip(), se, sw, sa, sb)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════════
def page_home():
    user   = current_user()
    events = st.session_state["risk_events"]
    score  = ut.calculate_risk(events)
    level, color, emoji = ut.get_risk_level(score)

    # Greeting
    st.markdown(f"""
    <div class="g-card" style="border-left:4px solid #2563EB">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
            <div>
                <div style="font-size:20px;font-weight:800;color:#0A1628">
                    Hello, {user.get('full_name','').split()[0]}! 👋
                </div>
                <div style="font-size:13px;color:#64748B;margin-top:3px">
                    GuardianAI is monitoring your safety in real-time
                </div>
            </div>
            <div style="text-align:right">
                <div class="badge badge-{'safe' if level=='SAFE' else 'warning' if level=='WARNING' else 'danger'}">
                    {emoji} {level}
                </div>
                <div style="font-size:11px;color:#94A3B8;margin-top:4px">Risk: {score}/100</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # "Are you okay?" overlay — fires when auto-detection triggers
    if st.session_state.get("awaiting_okay") and not st.session_state["emergency_active"]:
        elapsed   = time.time() - (st.session_state.get("countdown_start") or time.time())
        remaining = max(0, int(st.session_state["countdown_seconds"] - elapsed))

        st.markdown(f"""
        <div class="g-card-danger" style="text-align:center;padding:30px">
            <div style="font-size:48px">⚠️</div>
            <div style="font-size:22px;font-weight:900;color:#DC2626;margin:10px 0 4px">
                Are You Okay?
            </div>
            <div style="font-size:14px;color:#6B7280;margin-bottom:6px">
                Detected: <strong>{st.session_state.get('auto_trigger','Unknown')}</strong>
                · Risk Score: <strong style="color:#DC2626">{score}/100</strong>
            </div>
            <div style="font-size:13px;color:#9CA3AF">
                No response in <strong style="color:#EF4444">{remaining}s</strong>
                → Emergency alerts will be sent automatically
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(remaining / st.session_state["countdown_seconds"])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅  YES, I'M OKAY", key="okay_yes", use_container_width=True):
                st.session_state["awaiting_okay"]   = False
                st.session_state["countdown_start"] = None
                st.session_state["risk_events"]     = []
                st.success("✅ Great! Emergency cancelled. Stay safe! 💚")
                time.sleep(1)
                st.rerun()
        with c2:
            if st.button("🆘  NO, SEND HELP", key="okay_no",
                         use_container_width=True, type="primary"):
                st.session_state["awaiting_okay"]     = False
                st.session_state["emergency_active"]  = True
                lat, lon = ut.get_simulated_location()
                st.session_state["alert_lat"] = lat
                st.session_state["alert_lon"] = lon
                db.log_emergency(uid(), st.session_state.get("auto_trigger","SOS"),
                                 score, lat, lon, ut.get_location_string(lat, lon))
                nav("emergency")

        # Auto-fire if countdown expired
        if remaining == 0:
            trigger_event("No Response")
            st.session_state["awaiting_okay"]    = False
            st.session_state["emergency_active"] = True
            lat, lon = ut.get_simulated_location()
            st.session_state["alert_lat"] = lat
            st.session_state["alert_lon"] = lon
            db.log_emergency(uid(), "No Response / Timeout", score, lat, lon)
            nav("emergency")
        else:
            time.sleep(1)
            st.rerun()
        return

    # Gauge + stats
    col_g, col_s = st.columns([1, 1.3])
    with col_g:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Risk Score", "font": {"color": "#64748B", "size": 13}},
            number={"font": {"color": color, "size": 38, "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#CBD5E1",
                         "tickfont": {"color": "#94A3B8", "size": 10}},
                "bar": {"color": color, "thickness": 0.22},
                "bgcolor": "#F1F5F9",
                "bordercolor": "#E2E8F0",
                "steps": [
                    {"range": [0,  40], "color": "#F0FDF4"},
                    {"range": [40, 70], "color": "#FFFBEB"},
                    {"range": [70,100], "color": "#FEF2F2"},
                ],
            }
        ))
        fig.update_layout(height=230, margin=dict(l=20,r=20,t=40,b=10),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with col_s:
        contacts = db.get_contacts(uid())
        log      = db.get_emergency_log(uid(), 50)
        active   = sum(1 for e in log if e["status"]=="active")
        metrics  = [
            (str(score),         "Risk Score",    color),
            (str(len(contacts)), "Contacts",      "#2563EB"),
            (str(len(log)),      "Events Logged", "#7C3AED"),
            (str(active),        "Active Alerts", "#EF4444" if active else "#22C55E"),
        ]
        r1 = st.columns(2)
        r2 = st.columns(2)
        for i,(val,lbl,clr) in enumerate(metrics):
            c = (r1 if i<2 else r2)[i%2]
            with c:
                st.markdown(f"""
                <div class="stat-card" style="margin-bottom:10px">
                    <div class="stat-val" style="color:{clr}">{val}</div>
                    <div class="stat-lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)

    # Quick actions
    st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button("🤖 Open Auto Detection", use_container_width=True, type="primary"):
            nav("auto")
    with qa2:
        if st.button("📋 Manage Contacts", use_container_width=True):
            nav("contacts")
    with qa3:
        if st.button("🆘 Manual SOS", use_container_width=True):
            trigger_event("Manual SOS")
            nav("emergency")

    # Recent detections
    dlog = st.session_state.get("detection_log", [])
    if dlog:
        st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)
        st.markdown("**⚡ Recent Detections (this session)**")
        for d in dlog[:5]:
            _, clr, emj = ut.get_risk_level(d["score"])
            st.markdown(f"""
            <div class="log-row">
                <div class="log-icon">{emj}</div>
                <div style="flex:1">
                    <div class="log-title">{d['type']}</div>
                    <div class="log-sub">{d['time']}</div>
                </div>
                <div class="log-score" style="color:{clr}">{d['score']}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  AUTO DETECTION PAGE
# ══════════════════════════════════════════════════════════════
def page_auto():
    st.markdown('<div class="page-title">🤖 Auto Detection Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">App automatically detects danger and asks "Are you okay?" before sending alerts</div>', unsafe_allow_html=True)

    events = st.session_state["risk_events"]
    score  = ut.calculate_risk(events)
    level, color, emoji = ut.get_risk_level(score)

    # ── Auto status panel ──
    running = st.session_state.get("auto_running", False)
    status_dot = '<span class="pulse-ring"></span>' if running else '⚫'
    status_txt = "MONITORING ACTIVE" if running else "MONITORING PAUSED"
    status_clr = "#93C5FD" if running else "#64748B"

    st.markdown(f"""
    <div class="auto-panel">
        <div class="auto-status" style="color:{status_clr}">
            {status_dot} {status_txt}
        </div>
        <div class="auto-event" style="margin:12px 0 4px">
            Risk Level: <span style="color:{color}">{emoji} {level}</span>
        </div>
        <div style="font-size:13px;color:#93C5FD">
            Score: {score}/100 &nbsp;·&nbsp; Events: {len(events)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if not running:
            if st.button("▶️  START AUTO MONITORING", use_container_width=True, type="primary"):
                st.session_state["auto_running"] = True
                st.rerun()
        else:
            if st.button("⏹  STOP MONITORING", use_container_width=True):
                st.session_state["auto_running"] = False
                st.rerun()
    with c2:
        if st.button("🔄 Reset All Events", use_container_width=True):
            st.session_state["risk_events"]    = []
            st.session_state["awaiting_okay"]  = False
            st.session_state["countdown_start"]= None
            st.session_state["detection_log"]  = []
            st.rerun()

    st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)

    # ── 3 detection panels ──
    d1, d2, d3 = st.columns(3)

    # ── Voice / Keyword ──────────────────────────────────────
    with d1:
        st.markdown("""
        <div class="g-card-blue">
            <div style="font-size:28px;text-align:center">🎤</div>
            <div style="font-weight:700;color:#1E40AF;text-align:center;margin:6px 0 2px">
                Voice Keyword Detection
            </div>
            <div style="font-size:12px;color:#64748B;text-align:center">
                Type what you hear OR use browser mic below
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Browser mic via JS component
        st.markdown("""
        <div class="voice-box">
            <div style="color:#93C5FD;font-size:13px;font-weight:600;margin-bottom:10px">
                🎙️ Browser Microphone
            </div>
            <div id="voice-result" style="color:#FFFFFF;font-size:13px;min-height:20px">
                Click button and speak...
            </div>
            <button onclick="startVoice()"
                style="margin-top:10px;background:#2563EB;color:white;border:none;
                       padding:7px 18px;border-radius:8px;cursor:pointer;font-weight:600">
                🎤 Speak Now
            </button>
        </div>
        <script>
        function startVoice() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                document.getElementById('voice-result').innerText =
                    '❌ Browser does not support mic. Use text input below.';
                return;
            }
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SR();
            rec.lang = 'en-US';
            rec.interimResults = false;
            rec.onstart  = () => document.getElementById('voice-result').innerText = '🔴 Listening...';
            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                document.getElementById('voice-result').innerText = '✅ Heard: "' + text + '"';
                // Pass to Streamlit text box
                const el = window.parent.document.querySelector('input[aria-label="voice_transfer"]');
                if (el) { el.value = text; el.dispatchEvent(new Event('input', {bubbles:true})); }
            };
            rec.onerror  = (e) => document.getElementById('voice-result').innerText = '❌ Error: ' + e.error;
            rec.start();
        }
        </script>
        """, unsafe_allow_html=True)

        voice_text = st.text_input("⌨️ Or type spoken words here:", key="voice_input",
                                   label_visibility="visible", placeholder="e.g. help bachao")
        if st.button("🔍 Check for Keywords", key="kw_btn", use_container_width=True):
            if voice_text:
                kw = ut.check_keywords(voice_text)
                if kw:
                    st.error(f"🚨 Keyword '{kw}' detected!")
                    trigger_event("Emergency Keyword")
                    st.rerun()
                else:
                    st.success("✅ No keywords found.")
            else:
                st.warning("Enter text first.")

        # Simulate auto keyword trigger
        if running and st.button("🔴 SIMULATE Keyword", key="sim_kw", use_container_width=True):
            trigger_event("Emergency Keyword")
            st.success("Keyword trigger simulated!")
            st.rerun()

    # ── Sound Detection ──────────────────────────────────────
    with d2:
        st.markdown("""
        <div class="g-card-blue">
            <div style="font-size:28px;text-align:center">🔊</div>
            <div style="font-weight:700;color:#1E40AF;text-align:center;margin:6px 0 2px">
                Sound / Distress Detection
            </div>
            <div style="font-size:12px;color:#64748B;text-align:center">
                AI classifies screams, gunshots, and distress sounds
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🎙️ Run Audio Analysis", key="audio_btn", use_container_width=True):
            with st.spinner("Analyzing audio stream..."):
                time.sleep(1.3)
            label, conf = ut.simulate_audio_analysis()
            if label == "Scream Detected":
                st.error(f"😱 {label} ({conf}% confidence)")
                trigger_event("Scream Detected")
                st.rerun()
            elif label == "Gunshot Detected":
                st.error(f"🔫 {label} ({conf}% confidence)")
                trigger_event("Gunshot Detected")
                st.rerun()
            else:
                st.success(f"✅ Normal audio — {conf}% confidence")

        st.markdown("""
        <div style="font-size:12px;color:#94A3B8;text-align:center;margin-top:8px">
            🔧 In production, connects to device microphone<br>
            and runs continuous ML classification
        </div>
        """, unsafe_allow_html=True)

        if running:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("🔴 SIMULATE Scream", key="sim_scream", use_container_width=True):
                trigger_event("Scream Detected")
                st.rerun()
            if st.button("🔴 SIMULATE Gunshot", key="sim_gun", use_container_width=True):
                trigger_event("Gunshot Detected")
                st.rerun()

    # ── Fall Detection ───────────────────────────────────────
    with d3:
        st.markdown("""
        <div class="g-card-blue">
            <div style="font-size:28px;text-align:center">📱</div>
            <div style="font-weight:700;color:#1E40AF;text-align:center;margin:6px 0 2px">
                Fall / Impact Detection
            </div>
            <div style="font-size:12px;color:#64748B;text-align:center">
                Accelerometer + Gyroscope monitors sudden falls
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📡 Read Sensor Data", key="fall_btn", use_container_width=True):
            with st.spinner("Reading motion sensors..."):
                time.sleep(0.9)
            g, fell = ut.simulate_accelerometer()
            if fell:
                st.error(f"⚠️ FALL DETECTED! G-Force: {g}G")
                trigger_event("Fall Detected")
                st.rerun()
            else:
                st.success(f"✅ Normal movement — {g}G")

        st.markdown("""
        <div style="font-size:12px;color:#94A3B8;text-align:center;margin-top:8px">
            🔧 On mobile, reads accelerometer live.<br>
            Fall = free-fall &lt;0.4G → impact &gt;2.5G
        </div>
        """, unsafe_allow_html=True)

        if running:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("🔴 SIMULATE Fall", key="sim_fall", use_container_width=True):
                trigger_event("Fall Detected")
                st.rerun()

    # ── Flow diagram ──────────────────────────────────────────
    st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)
    st.markdown("**🔄 How Auto Detection Works**")
    st.markdown("""
    <div class="g-card" style="overflow-x:auto">
        <div style="display:flex;align-items:center;gap:0;flex-wrap:nowrap;
                    justify-content:center;padding:10px 0">
            <div style="text-align:center;min-width:110px">
                <div style="font-size:26px">🎤🔊📱</div>
                <div style="font-size:12px;font-weight:700;color:#1E40AF;margin-top:5px">DETECT</div>
                <div style="font-size:11px;color:#64748B">Voice / Sound / Fall</div>
            </div>
            <div style="font-size:22px;color:#CBD5E1;padding:0 8px">→</div>
            <div style="text-align:center;min-width:110px">
                <div style="font-size:26px">🔢</div>
                <div style="font-size:12px;font-weight:700;color:#7C3AED;margin-top:5px">SCORE</div>
                <div style="font-size:11px;color:#64748B">Risk Engine calculates</div>
            </div>
            <div style="font-size:22px;color:#CBD5E1;padding:0 8px">→</div>
            <div style="text-align:center;min-width:110px">
                <div style="font-size:26px">❓</div>
                <div style="font-size:12px;font-weight:700;color:#F59E0B;margin-top:5px">VERIFY</div>
                <div style="font-size:11px;color:#64748B">"Are You Okay?"</div>
            </div>
            <div style="font-size:22px;color:#CBD5E1;padding:0 8px">→</div>
            <div style="text-align:center;min-width:110px">
                <div style="font-size:26px">⏱️</div>
                <div style="font-size:12px;font-weight:700;color:#DC2626;margin-top:5px">WAIT 60s</div>
                <div style="font-size:11px;color:#64748B">Countdown starts</div>
            </div>
            <div style="font-size:22px;color:#CBD5E1;padding:0 8px">→</div>
            <div style="text-align:center;min-width:110px">
                <div style="font-size:26px">📨</div>
                <div style="font-size:12px;font-weight:700;color:#DC2626;margin-top:5px">ALERT</div>
                <div style="font-size:11px;color:#64748B">SMS sent to all contacts</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  EMERGENCY PAGE
# ══════════════════════════════════════════════════════════════
def page_emergency():
    events   = st.session_state["risk_events"]
    score    = ut.calculate_risk(events)
    level, color, emoji = ut.get_risk_level(score)
    contacts = db.get_contacts(uid())
    user     = current_user()

    # ── Not yet in emergency — show verification ──
    if not st.session_state.get("emergency_active"):
        st.markdown(f"""
        <div class="g-card-{'danger' if score>=71 else 'warn' if score>=41 else 'safe'}"
             style="text-align:center;padding:30px">
            <div style="font-size:52px">{emoji}</div>
            <div style="font-size:22px;font-weight:900;color:#0A1628;margin:10px 0 4px">
                Are You Safe?
            </div>
            <div style="font-size:14px;color:#64748B;margin-bottom:16px">
                Risk level: <strong style="color:{color}">{level}</strong> ({score}/100)
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅  YES, I'M SAFE", use_container_width=True, key="esafe"):
                st.session_state["risk_events"]    = []
                st.session_state["detection_log"]  = []
                st.session_state["awaiting_okay"]  = False
                st.success("✅ Glad you're safe! Stay alert. 💚")
                time.sleep(1.2)
                nav("home")
        with c2:
            if st.button("🆘  I NEED HELP", use_container_width=True, key="ehelp", type="primary"):
                st.session_state["emergency_active"] = True
                lat, lon = ut.get_simulated_location()
                st.session_state["alert_lat"] = lat
                st.session_state["alert_lon"] = lon
                db.log_emergency(uid(), "Manual Emergency", score, lat, lon,
                                 ut.get_location_string(lat, lon))
                st.rerun()

        st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)
        st.markdown("**⏱️ Manual Countdown Trigger**")
        st.markdown("""
        <div style="font-size:13px;color:#64748B;margin-bottom:12px">
            Start 60s countdown. If you don't respond → emergency alerts fire automatically.
        </div>
        """, unsafe_allow_html=True)

        if st.button("▶️  Start 60-Second Countdown", use_container_width=True):
            st.session_state["countdown_start"]  = time.time()
            st.session_state["awaiting_okay"]    = True
            st.session_state["auto_trigger"]     = "Manual Countdown"
            st.rerun()
        return

    # ════════════════════════════════════
    #  ACTIVE EMERGENCY MODE
    # ════════════════════════════════════
    lat = st.session_state.get("alert_lat")
    lon = st.session_state.get("alert_lon")
    loc_str   = ut.get_location_string(lat, lon) if lat else "Unavailable"
    maps_link = ut.get_maps_link(lat, lon) if lat else "#"

    st.markdown("""
    <div class="g-card-danger" style="text-align:center;padding:26px">
        <span class="pulse-ring-red"></span>
        <span style="font-size:22px;font-weight:900;color:#DC2626">EMERGENCY MODE ACTIVE</span>
        <div style="font-size:13px;color:#6B7280;margin-top:6px">
            Sending alerts to your emergency contacts
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_loc, tab_sms, tab_msg = st.tabs(["📍 Location", "📨 Send Alerts", "📋 Message"])

    with tab_loc:
        st.markdown(f"""
        <div class="g-card" style="border-left:3px solid #EF4444">
            <div style="font-size:12px;color:#64748B">📍 Last Known Location</div>
            <div style="font-size:18px;font-weight:700;color:#0A1628;margin:6px 0">{loc_str}</div>
            <a href="{maps_link}" target="_blank"
               style="color:#2563EB;font-size:13px;font-weight:600;text-decoration:none">
               🗺️ Open in Google Maps →
            </a>
        </div>
        """, unsafe_allow_html=True)

        if lat and lon:
            try:
                import folium
                from streamlit_folium import st_folium
                m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB positron")
                folium.Marker(
                    [lat, lon],
                    popup=f"🆘 {user.get('full_name')}",
                    tooltip="Emergency Location",
                    icon=folium.Icon(color="red", icon="exclamation-sign")
                ).add_to(m)
                folium.Circle([lat, lon], radius=300,
                              color="#EF4444", fill=True, fill_opacity=0.15).add_to(m)
                st_folium(m, height=310, use_container_width=True)
            except Exception:
                st.info(f"📍 Coordinates: {lat}, {lon}")

    with tab_sms:
        if not contacts:
            st.warning("⚠️ No emergency contacts! Add them in the Contacts page.")
            if st.button("➕ Add Contacts", type="primary"):
                nav("contacts")
        else:
            # Check if Twilio is configured
            has_twilio = bool(
                st.session_state.get("twilio_sid") and
                st.session_state.get("twilio_token") and
                st.session_state.get("twilio_from")
            )

            if not has_twilio:
                with st.expander("⚙️ Configure Twilio for REAL SMS (click to expand)"):
                    st.markdown("""
                    <div style="font-size:13px;color:#64748B;margin-bottom:10px">
                    To send real SMS:<br>
                    1. Create free account at <strong>twilio.com</strong><br>
                    2. Get Account SID, Auth Token, and a phone number<br>
                    3. Enter below — then SMS will be actually delivered!
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state["twilio_sid"]   = st.text_input("Twilio Account SID",   key="t_sid",   value=st.session_state["twilio_sid"])
                    st.session_state["twilio_token"] = st.text_input("Twilio Auth Token",     key="t_token", value=st.session_state["twilio_token"], type="password")
                    st.session_state["twilio_from"]  = st.text_input("Twilio Phone (e.g. +1xxxxxxxxxx)", key="t_from", value=st.session_state["twilio_from"])

            mode_badge = "🟢 Real SMS (Twilio)" if has_twilio else "📋 Simulation Mode"
            st.markdown(f"""
            <div style="font-size:13px;color:#64748B;margin-bottom:12px">
                SMS Mode: <strong>{mode_badge}</strong>
            </div>
            """, unsafe_allow_html=True)

            for c in contacts:
                initials = c["name"][0].upper()
                st.markdown(f"""
                <div class="contact-card">
                    <div class="contact-avatar">{initials}</div>
                    <div>
                        <div class="contact-name">{c['name']}</div>
                        <div class="contact-sub">📱 {c['phone']} · {c['relationship']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("📨 SEND EMERGENCY SMS TO ALL", use_container_width=True, type="primary"):
                with st.spinner("📡 Sending alerts..."):
                    results, msg_text = send_alerts_to_all(
                        contacts, user.get("full_name","User"),
                        loc_str, maps_link,
                        st.session_state.get("auto_trigger","Emergency SOS"),
                        score
                    )
                st.session_state["sms_results"] = results
                st.session_state["sms_message"] = msg_text
                st.rerun()

            if st.session_state.get("sms_results"):
                st.markdown("**📬 Delivery Report:**")
                for r in st.session_state["sms_results"]:
                    ok_icon = "✅" if r["ok"] else "❌"
                    real_badge = '<span class="badge badge-blue">REAL</span>' if r.get("real") else \
                                 '<span class="badge badge-warning">SIM</span>'
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:9px 0;border-bottom:1px solid #E2E8F0">
                        <span style="font-size:14px;color:#0A1628">
                            {ok_icon} <strong>{r['name']}</strong> ({r['phone']})
                        </span>
                        <span style="display:flex;align-items:center;gap:8px">
                            {real_badge}
                            <span style="font-size:12px;color:#64748B">{r['time']}</span>
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_msg:
        msg_preview = st.session_state.get("sms_message") or \
                      build_message(user.get("full_name","User"), loc_str, maps_link,
                                    st.session_state.get("auto_trigger","SOS"), score)
        st.markdown("**📝 SMS Message (sent to each contact):**")
        st.code(msg_preview, language=None)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("✅ I'm Safe — Cancel Emergency", use_container_width=True):
        log = db.get_emergency_log(uid(), 1)
        if log:
            db.resolve_emergency(log[0]["id"], uid())
        st.session_state.update({
            "emergency_active": False,
            "awaiting_okay":    False,
            "risk_events":      [],
            "sms_results":      [],
            "sms_message":      "",
            "detection_log":    [],
            "countdown_start":  None,
        })
        st.success("✅ Emergency resolved. You're marked safe.")
        time.sleep(1)
        nav("home")


# ══════════════════════════════════════════════════════════════
#  CONTACTS
# ══════════════════════════════════════════════════════════════
def page_contacts():
    st.markdown('<div class="page-title">📋 Emergency Contacts</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">These people receive SMS alerts when you need help</div>', unsafe_allow_html=True)

    contacts = db.get_contacts(uid())
    edit_id  = st.session_state.get("edit_contact_id")

    with st.expander("➕ Add New Contact", expanded=len(contacts)==0):
        c1,c2,c3,c4 = st.columns([2,2,2,1])
        with c1: nn = st.text_input("Full Name *", placeholder="Ali Khan", key="nc_n")
        with c2: np_ = st.text_input("Phone *", placeholder="+92 300 0000000", key="nc_p")
        with c3: nr = st.selectbox("Relationship", ut.RELATIONSHIP_OPTIONS, key="nc_r")
        with c4: npi = st.number_input("Priority", 1, 10, 1, key="nc_pi")
        if st.button("➕ Add", key="add_c", type="primary"):
            if nn and np_:
                db.add_contact(uid(), nn, np_.strip(), nr, npi)
                st.success(f"✅ {nn} added!")
                st.rerun()
            else:
                st.warning("Name and phone required.")

    if not contacts:
        st.markdown("""
        <div class="g-card" style="text-align:center;padding:40px">
            <div style="font-size:40px;margin-bottom:10px">📭</div>
            <div style="font-weight:700;color:#0A1628">No contacts yet</div>
            <div style="font-size:13px;color:#64748B;margin-top:4px">
                Add family or friends above so they can be alerted
            </div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"**{len(contacts)} Contact(s)**")

    for c in contacts:
        initials = c["name"][0].upper()
        ca, cb = st.columns([5,1])
        with ca:
            st.markdown(f"""
            <div class="contact-card">
                <div class="contact-avatar">{initials}</div>
                <div style="flex:1">
                    <div class="contact-name">{c['name']}</div>
                    <div class="contact-sub">
                        📱 {c['phone']} &nbsp;·&nbsp;
                        👥 {c['relationship']} &nbsp;·&nbsp;
                        ⭐ Priority {c['priority']}
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        with cb:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✏️", key=f"e_{c['id']}", help="Edit"):
                    st.session_state["edit_contact_id"] = c["id"]
                    st.rerun()
            with b2:
                if st.button("🗑️", key=f"d_{c['id']}", help="Delete"):
                    db.delete_contact(c["id"], uid())
                    st.rerun()

    if edit_id:
        t = next((c for c in contacts if c["id"]==edit_id), None)
        if t:
            st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)
            st.markdown(f"**✏️ Edit: {t['name']}**")
            e1,e2,e3,e4 = st.columns([2,2,2,1])
            with e1: en = st.text_input("Name",  value=t["name"],  key="ec_n")
            with e2: ep = st.text_input("Phone", value=t["phone"], key="ec_p")
            with e3:
                di = ut.RELATIONSHIP_OPTIONS.index(t["relationship"]) \
                     if t["relationship"] in ut.RELATIONSHIP_OPTIONS else 0
                er = st.selectbox("Relationship", ut.RELATIONSHIP_OPTIONS, index=di, key="ec_r")
            with e4: epr = st.number_input("Priority",1,10,t["priority"],key="ec_pi")
            s1,s2 = st.columns(2)
            with s1:
                if st.button("💾 Save", key="sv_e", type="primary", use_container_width=True):
                    db.update_contact(edit_id, uid(), en, ep.strip(), er, epr)
                    st.session_state["edit_contact_id"] = None
                    st.success("✅ Saved!"); st.rerun()
            with s2:
                if st.button("✖️ Cancel", key="cn_e", use_container_width=True):
                    st.session_state["edit_contact_id"] = None; st.rerun()


# ══════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown('<div class="page-title">📊 Safety Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Analytics and history of all safety events</div>', unsafe_allow_html=True)

    log = db.get_emergency_log(uid(), 50)
    if not log:
        st.markdown("""
        <div class="g-card" style="text-align:center;padding:40px">
            <div style="font-size:40px;margin-bottom:10px">📈</div>
            <div style="font-weight:700;color:#0A1628">No events yet</div>
            <div style="font-size:13px;color:#64748B;margin-top:4px">
                Use the detection features to start logging events
            </div>
        </div>""", unsafe_allow_html=True)
        return

    df = pd.DataFrame(log)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    c1,c2,c3,c4 = st.columns(4)
    for col,(val,lbl,clr) in zip([c1,c2,c3,c4],[
        (str(len(log)),              "Total Events",   "#2563EB"),
        (str(df["risk_score"].max()),"Peak Risk",      "#EF4444"),
        (f"{df['risk_score'].mean():.0f}","Avg Risk",  "#F59E0B"),
        (str(sum(1 for e in log if e["status"]=="resolved")),"Resolved","#22C55E"),
    ]):
        with col:
            st.markdown(f"""
            <div class="stat-card" style="margin-bottom:12px">
                <div class="stat-val" style="color:{clr}">{val}</div>
                <div class="stat-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    ca,cb = st.columns(2)
    with ca:
        daily = df.groupby("date").size().reset_index(name="count")
        fig = px.area(daily, x="date", y="count", title="Events Over Time",
                      color_discrete_sequence=["#2563EB"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F8FAFF",
                          font={"color":"#334155","family":"Inter"},
                          title_font={"color":"#0A1628","size":14},
                          xaxis={"gridcolor":"#E2E8F0"}, yaxis={"gridcolor":"#E2E8F0"},
                          margin=dict(l=10,r=10,t=40,b=10), height=240)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with cb:
        tc = df["trigger_type"].value_counts().reset_index()
        tc.columns = ["type","count"]
        fig2 = px.pie(tc, values="count", names="type", title="Event Types",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                           font={"color":"#334155","family":"Inter"},
                           title_font={"color":"#0A1628","size":14},
                           margin=dict(l=10,r=10,t=40,b=10), height=240)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    st.markdown("<hr class='g-divider'>", unsafe_allow_html=True)
    st.markdown("**📋 Event Log**")
    for e in log[:12]:
        _,clr,emj = ut.get_risk_level(e["risk_score"])
        bc = "safe" if e["risk_score"]<=40 else "warning" if e["risk_score"]<=70 else "danger"
        si = "✅" if e["status"]=="resolved" else "🔴"
        st.markdown(f"""
        <div class="log-row">
            <div class="log-icon">{emj}</div>
            <div style="flex:1">
                <div class="log-title">{e['trigger_type']}</div>
                <div class="log-sub">{ut.format_timestamp(e['timestamp'])} · {si} {e['status'].title()}</div>
            </div>
            <div class="log-score" style="color:{clr}">{e['risk_score']}</div>
            <div><span class="badge badge-{bc}">{bc.upper()}</span></div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════
def page_settings():
    user = current_user()
    st.markdown('<div class="page-title">⚙️ Settings & Profile</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "📨 SMS Config", "🔒 Security", "ℹ️ About"])

    with tab1:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            nn = st.text_input("Full Name", value=user.get("full_name",""), key="sp_n")
            ne = st.text_input("Email",     value=user.get("email",""),     key="sp_e")
            nb = st.selectbox("Blood Group", ut.BLOOD_GROUPS,
                              index=ut.BLOOD_GROUPS.index(user.get("blood_group","Unknown"))
                              if user.get("blood_group") in ut.BLOOD_GROUPS else 0, key="sp_b")
        with c2:
            na = st.text_input("Home Address", value=user.get("address",""), key="sp_a")
            nm = st.text_area("Medical Notes", value=user.get("medical_notes",""),
                              height=90, key="sp_m")
        if st.button("💾 Save Profile", type="primary"):
            db.update_user(uid(), full_name=nn, email=ne, blood_group=nb,
                           address=na, medical_notes=nm)
            st.session_state["user"].update(
                {"full_name":nn,"email":ne,"blood_group":nb,"address":na,"medical_notes":nm}
            )
            st.success("✅ Profile saved!")
        st.markdown('</div>', unsafe_allow_html=True)

        cd_sec = st.slider("⏱️ Countdown before auto-alert (seconds)",
                           15, 120, st.session_state.get("countdown_seconds",60), 5)
        st.session_state["countdown_seconds"] = cd_sec

    with tab2:
        st.markdown("""
        <div class="g-card-blue">
            <div style="font-weight:700;color:#1E40AF;margin-bottom:8px">📨 Twilio SMS Configuration</div>
            <div style="font-size:13px;color:#334155">
                Enter your Twilio credentials to enable real SMS delivery.<br>
                Free account: <strong>twilio.com/try-twilio</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ts  = st.text_input("Account SID",   value=st.session_state["twilio_sid"],   key="cfg_sid")
        tt  = st.text_input("Auth Token",    value=st.session_state["twilio_token"], key="cfg_tok", type="password")
        tf  = st.text_input("From Number (e.g. +12015551234)",
                             value=st.session_state["twilio_from"], key="cfg_frm")

        if st.button("💾 Save SMS Config", type="primary"):
            st.session_state["twilio_sid"]   = ts.strip()
            st.session_state["twilio_token"] = tt.strip()
            st.session_state["twilio_from"]  = tf.strip()
            if ts and tt and tf:
                st.success("✅ Twilio configured! Real SMS will now be sent.")
            else:
                st.info("📋 Running in simulation mode (credentials not complete).")

        status = "🟢 Real SMS Active" if (ts and tt and tf) else "📋 Simulation Mode"
        st.markdown(f"**Current SMS Status:** {status}")

    with tab3:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown("**Change Password**")
        op = st.text_input("Current Password", type="password", key="sec_o")
        np_ = st.text_input("New Password",    type="password", key="sec_n")
        cp = st.text_input("Confirm New",      type="password", key="sec_c")
        if st.button("🔒 Update Password", type="primary"):
            if not all([op,np_,cp]):
                st.warning("Fill all fields.")
            elif np_ != cp:
                st.error("Passwords don't match.")
            elif len(np_) < 6:
                st.warning("Min 6 characters.")
            else:
                if db.login_user(user["phone"], op):
                    db.update_user(uid(), password_hash=db.hash_pw(np_))
                    st.success("✅ Password updated!")
                else:
                    st.error("❌ Current password wrong.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown("""
        <div class="g-card" style="text-align:center;padding:30px;border-left:4px solid #2563EB">
            <div style="font-size:48px;margin-bottom:10px">🛡️</div>
            <div style="font-size:20px;font-weight:800;color:#0A1628">GuardianAI v2.0</div>
            <div style="font-size:13px;color:#64748B;margin-top:4px;margin-bottom:16px">
                AI-Powered Emergency Detection & Response
            </div>
            <hr class="g-divider">
            <div style="font-size:13px;color:#334155;line-height:2;text-align:left;max-width:340px;margin:0 auto">
                🎤 Voice keyword detection (browser mic)<br>
                🔊 Distress sound AI classification<br>
                📱 Accelerometer fall detection<br>
                ❓ "Are you okay?" verification<br>
                ⏱️ 60-second auto-countdown<br>
                📨 Real SMS via Twilio<br>
                📍 GPS location in alerts<br>
                🗺️ Live map in emergency mode<br>
                📊 Risk scoring engine
            </div>
            <hr class="g-divider">
            <div style="font-size:11px;color:#94A3B8">
                Built with Streamlit · SQLite · Twilio · Plotly · Folium
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            logout()


# ══════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════
def main():
    init_state()

    if not is_logged_in():
        page_login()
        return

    render_navbar()

    st.markdown("<div style='padding:0 28px 40px'>", unsafe_allow_html=True)
    page = st.session_state.get("page","home")
    {
        "home":      page_home,
        "auto":      page_auto,
        "contacts":  page_contacts,
        "emergency": page_emergency,
        "dashboard": page_dashboard,
        "settings":  page_settings,
    }.get(page, page_home)()
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
# rebuild trigger
