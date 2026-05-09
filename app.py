import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import io
from database import *
from chatbot import ask_chatbot

st.set_page_config(page_title="NewsIntel", page_icon="🗞️", layout="wide")

for k, v in {
    "user": None, "page": "Dashboard", "chat_history": [],
    "selected_q": None, "dark_mode": False, "login_role": "Admin",
    "table_sub": None, "story_page": 0, "source_page": 0,
    "interview_page": 0, "doc_page": 0, "loc_page": 0,
    "note_page": 0, "timeline_page": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

dark = st.session_state.dark_mode

if dark:
    BG      = "#13110e"; CARD    = "#1e1b17"; SIDEBAR = "#181512"
    TEXT    = "#ede6db"; SUBTEXT = "#9e8f7e"; BORDER  = "#2e2820"
    ACCENT  = "#c9975a"; ACCENT2 = "#e8b87a"; SURFACE = "#252018"
    INPUT_BG= "#252018"
else:
    BG      = "#faf8f5"; CARD    = "#ffffff"; SIDEBAR = "#f4efe8"
    TEXT    = "#2c2010"; SUBTEXT = "#8a7560"; BORDER  = "#e6ddd0"
    ACCENT  = "#b8763a"; ACCENT2 = "#d4944e"; SURFACE = "#ede8e0"
    INPUT_BG= "#fdfaf6"

ROLE_COLORS = {"Admin": "#b03030", "Journalist": "#1a5fa0", "Viewer": "#5a3a90"}

CAT_COLORS = {
    "Crime":       "#e05050",
    "Politics":    "#5080e0",
    "Environment": "#50a060",
    "Health":      "#e07030",
    "Business":    "#8050d0",
    "Education":   "#30a0b0",
}
CAT_ICONS = {
    "Crime":"🔍","Politics":"🏛️","Environment":"🌿",
    "Health":"🏥","Business":"💼","Education":"🎓",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=DM+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after {{ box-sizing: border-box; margin: 0; }}
html, body, .stApp {{ font-family: 'DM Sans', sans-serif !important; }}
h1,h2,h3 {{ font-family: 'Playfair Display', serif !important; }}
.stApp {{ background: {BG} !important; color: {TEXT} !important; }}
.stApp > header {{ background: transparent !important; box-shadow: none !important; }}
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden !important; height: 0 !important; }}
.block-container {{ padding: 1.5rem 2rem 2rem !important; max-width: 100% !important; }}

section[data-testid="stSidebar"] {{
    background: {SIDEBAR} !important;
    border-right: 1px solid {BORDER} !important;
}}
section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important; border: none !important;
    color: {SUBTEXT} !important; text-align: left !important;
    width: 100% !important; padding: 9px 16px !important;
    border-radius: 8px !important; font-size: 13.5px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 400 !important;
    margin: 1px 0 !important; transition: all 0.18s ease !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {SURFACE} !important; color: {ACCENT} !important; padding-left: 22px !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2}) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 500 !important; font-family: 'DM Sans', sans-serif !important;
    padding: 9px 22px !important; transition: all 0.2s ease !important;
    font-size: 13.5px !important; box-shadow: 0 2px 8px rgba(184,118,58,0.20) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(184,118,58,0.35) !important;
}}

.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {{
    background: {INPUT_BG} !important; border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important; color: {TEXT} !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 14px !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(184,118,58,0.12) !important;
}}
.stTextInput label, .stTextArea label, .stSelectbox label {{
    color: {SUBTEXT} !important; font-size: 11px !important;
    font-weight: 600 !important; letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}}

.stDataFrame {{
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 2px 12px rgba(140,80,20,0.06) !important;
}}

.stProgress > div > div > div {{
    background: linear-gradient(90deg, {ACCENT}, {ACCENT2}) !important;
    border-radius: 10px !important;
}}

/* ── Intelligence Card ── */
.intel-card {{
    background: {CARD};
    border-radius: 18px;
    border: 1px solid {BORDER};
    padding: 0;
    margin-bottom: 18px;
    overflow: hidden;
    transition: transform 0.25s cubic-bezier(.34,1.56,.64,1), box-shadow 0.25s;
    cursor: pointer;
    position: relative;
}}
.intel-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 20px 48px rgba(140,80,20,0.16);
}}
.intel-card-header {{
    padding: 18px 18px 14px;
    position: relative;
}}
.intel-card-cat-strip {{
    height: 4px;
    border-radius: 18px 18px 0 0;
    margin-bottom: 0;
}}
.intel-card-title {{
    font-family: 'Playfair Display', serif;
    font-size: 14.5px;
    font-weight: 700;
    color: {TEXT};
    line-height: 1.35;
    margin-bottom: 10px;
    margin-top: 4px;
}}
.intel-card-badges {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}}
.intel-card-stats {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    padding: 12px 18px 16px;
    background: {SURFACE};
    border-top: 1px solid {BORDER};
}}
.intel-stat {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: {SUBTEXT};
}}
.intel-stat-val {{
    font-weight: 700;
    color: {TEXT};
    font-size: 13px;
}}
.intel-progress-ring {{
    position: absolute;
    top: 14px;
    right: 14px;
}}
.badge {{
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 11px;
    font-weight: 600; letter-spacing: 0.04em;
}}
.badge-ongoing    {{ background: #fff4e0; color: #c07010; }}
.badge-completed  {{ background: #e6f4eb; color: #2a7a40; }}
.badge-open       {{ background: #fce8e8; color: #b02020; }}
.badge-rectified   {{ background: #e6f4eb; color: #2a7a40; }}
.badge-admin      {{ background: #fce8e8; color: #b02020; }}
.badge-journalist {{ background: #e6eef8; color: #1a5090; }}
.badge-viewer     {{ background: #f0eaf8; color: #5a2a90; }}

.page-title {{
    font-family: 'Playfair Display', serif !important;
    font-size: 1.9rem !important; font-weight: 700 !important;
    color: {TEXT} !important; margin-bottom: 2px !important;
}}
.page-sub {{ font-size: 13.5px; color: {SUBTEXT}; margin-bottom: 22px; }}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem; font-weight: 600; color: {TEXT};
    margin: 20px 0 14px; padding-bottom: 8px;
    border-bottom: 2px solid {BORDER};
}}
.custom-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {BORDER}, transparent);
    margin: 20px 0;
}}
.stat-card {{
    background: {CARD}; border-radius: 16px;
    padding: 20px 18px 16px; border: 1px solid {BORDER};
    transition: transform 0.25s cubic-bezier(.34,1.56,.64,1), box-shadow 0.25s;
    margin-bottom: 12px; position: relative; overflow: hidden;
}}
.stat-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; background: var(--card-color, {ACCENT});
    border-radius: 16px 16px 0 0;
}}
.stat-card:hover {{ transform: translateY(-4px); box-shadow: 0 14px 32px rgba(140,80,20,0.12); }}
.stat-icon   {{ font-size: 1.5rem; margin-bottom: 10px; display: block; }}
.stat-number {{ font-family: 'Playfair Display', serif; font-size: 2.3rem; font-weight: 700; color: {TEXT}; display: block; }}
.stat-label  {{ font-size: 11px; color: {SUBTEXT}; margin-top: 5px; text-transform: uppercase; letter-spacing: 0.08em; display: block; font-weight: 600; }}

.welcome-banner {{
    background: linear-gradient(135deg, {ACCENT} 0%, {ACCENT2} 60%, #f0c080 100%);
    border-radius: 20px; padding: 28px 32px; margin-bottom: 24px;
    color: white; position: relative; overflow: hidden;
    box-shadow: 0 8px 32px rgba(184,118,58,0.30);
}}
.welcome-banner::before {{
    content: '🗞️'; position: absolute; right: 24px; top: 50%;
    transform: translateY(-50%); font-size: 5rem; opacity: 0.15;
}}
.welcome-title {{ font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; margin-bottom: 6px; }}
.welcome-sub   {{ font-size: 13.5px; opacity: 0.88; }}

.sidebar-section-label {{
    font-size: 10px; color: {SUBTEXT}; text-transform: uppercase;
    letter-spacing: 0.12em; padding: 12px 4px 6px; display: block; font-weight: 700;
}}
.pagination-wrap {{
    display: flex; align-items: center; justify-content: center;
    gap: 12px; margin: 24px 0 8px; padding: 14px 20px;
    background: {SURFACE}; border-radius: 14px; border: 1px solid {BORDER};
}}
.pagination-info {{
    font-size: 13px; color: {SUBTEXT}; font-weight: 500; white-space: nowrap;
}}
.source-card {{
    background: {CARD}; border-radius: 16px; border: 1px solid {BORDER};
    padding: 18px; margin-bottom: 14px; overflow: hidden; position: relative;
    transition: transform 0.22s cubic-bezier(.34,1.56,.64,1), box-shadow 0.22s;
}}
.source-card:hover {{ transform: translateY(-4px); box-shadow: 0 14px 32px rgba(140,80,20,0.12); }}
.source-card-top {{ display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }}
.source-avatar {{
    width: 46px; height: 46px; border-radius: 13px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 700;
}}
.source-name  {{ font-family: 'Playfair Display', serif; font-size: 14px; font-weight: 700; color: {TEXT}; }}
.source-type  {{ font-size: 11px; color: {SUBTEXT}; margin-top: 2px; }}
.source-stats {{ display: flex; gap: 12px; padding-top: 10px; border-top: 1px solid {BORDER}; }}
.source-stat  {{ font-size: 12px; color: {SUBTEXT}; }}
.source-stat span {{ font-weight: 700; color: {TEXT}; }}

.interview-card {{
    background: {CARD}; border-radius: 14px; border: 1px solid {BORDER};
    padding: 16px 18px; margin-bottom: 12px;
    border-left: 4px solid {ACCENT};
    transition: transform 0.2s, box-shadow 0.2s;
}}
.interview-card:hover {{ transform: translateX(4px); box-shadow: 0 6px 20px rgba(140,80,20,0.10); }}

.doc-card {{
    background: {CARD}; border-radius: 14px; border: 1px solid {BORDER};
    padding: 16px 18px; margin-bottom: 12px; position: relative;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.doc-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(140,80,20,0.10); }}
.doc-type-badge {{
    display: inline-block; padding: 3px 10px; border-radius: 8px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.04em;
    background: {SURFACE}; color: {ACCENT}; border: 1px solid {BORDER};
}}

.timeline-item {{
    display: flex; gap: 16px; padding: 14px 0;
    border-bottom: 1px solid {BORDER};
}}
.timeline-dot-wrap {{
    display: flex; flex-direction: column; align-items: center; gap: 0; flex-shrink: 0;
}}
.timeline-dot {{
    width: 12px; height: 12px; border-radius: 50%;
    background: {ACCENT}; flex-shrink: 0;
    box-shadow: 0 0 0 3px rgba(184,118,58,0.18);
    margin-top: 4px;
}}
.timeline-line {{
    width: 2px; flex: 1; background: {BORDER}; min-height: 20px;
}}
.timeline-content {{ flex: 1; padding-bottom: 8px; }}
.timeline-title {{ font-weight: 700; font-size: 14px; color: {TEXT}; margin-bottom: 4px; }}
.timeline-meta  {{ font-size: 12px; color: {SUBTEXT}; margin-bottom: 6px; }}
.timeline-desc  {{ font-size: 13px; color: {TEXT}; line-height: 1.5; opacity: 0.85; }}

.note-card {{
    background: {CARD}; border-radius: 14px; border: 1px solid {BORDER};
    padding: 16px 18px; margin-bottom: 12px;
    border-left: 4px solid {ACCENT2};
    transition: transform 0.2s;
}}
.note-card:hover {{ transform: translateX(4px); }}

.chat-user {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2});
    color: #fff; padding: 13px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px 80px; font-size: 14px; line-height: 1.5;
    box-shadow: 0 4px 14px rgba(184,118,58,0.25);
}}
.chat-bot {{
    background: {CARD}; color: {TEXT}; padding: 13px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 80px 8px 0; font-size: 14px;
    border: 1px solid {BORDER}; line-height: 1.5;
}}
.sql-box {{
    background: {SIDEBAR}; color: {ACCENT2}; padding: 14px;
    border-radius: 10px; font-family: 'Courier New', monospace;
    font-size: 12px; white-space: pre-wrap; border: 1px solid {BORDER};
    margin-top: 6px; line-height: 1.6;
}}
.complaint-card {{
    background: {CARD}; border-radius: 14px; padding: 20px; margin: 10px 0;
    border: 1px solid {BORDER}; border-left: 4px solid #e05050;
}}
.live-item {{
    background: {CARD}; border-radius: 10px; padding: 13px 16px;
    margin: 7px 0; border: 1px solid {BORDER}; border-left: 3px solid {ACCENT};
    transition: transform 0.15s;
}}
.live-item:hover {{ transform: translateX(4px); }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════
if st.session_state.user is None:
    st.markdown("""<style>
    .stApp { background: linear-gradient(145deg,#f0e9e0 0%,#e8ddd2 50%,#f5ede4 100%) !important; }
    .block-container { padding: 0 !important; }
    </style>""", unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1.05, 1])
    with center_col:
        st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center;margin-bottom:28px;'>
            <div style='background:linear-gradient(135deg,#b8763a,#d4944e);width:70px;height:70px;
            border-radius:22px;display:flex;align-items:center;justify-content:center;
            margin:0 auto 16px;font-size:32px;box-shadow:0 12px 32px rgba(184,118,58,0.35);'>🗞️</div>
            <div style='font-family:"Playfair Display",serif;font-size:2.2rem;font-weight:700;
            color:#2c2010;letter-spacing:-0.02em;'>NewsIntel</div>
            <div style='color:#8a7560;font-size:12px;margin-top:6px;letter-spacing:0.08em;
            text-transform:uppercase;font-weight:600;'>Investigation Management System</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div style='background:white;border-radius:22px 22px 0 0;padding:28px 36px 4px;
        box-shadow:0 24px 64px rgba(120,80,30,0.14);border:1px solid #e6ddd0;border-bottom:none;'>
        <div style='font-size:11px;font-weight:700;color:#8a7560;text-transform:uppercase;
        letter-spacing:0.12em;margin-bottom:12px;'>Select your role</div></div>""", unsafe_allow_html=True)

        role_choice = st.radio("Role", ["Admin","Journalist","Viewer"], horizontal=True,
            index=["Admin","Journalist","Viewer"].index(st.session_state.login_role),
            label_visibility="collapsed", key="login_role_radio")
        st.session_state.login_role = role_choice

        role_desc = {
            "Admin":      ("🛡️","#b03030","Full access — manage users, audit logs, resolve complaints"),
            "Journalist": ("✍️","#1a5fa0","Create & edit stories, sources, interviews, documents"),
            "Viewer":     ("👁️","#5a3a90","Read-only access to stories, sources & live feed"),
        }
        ic, rc, desc = role_desc[role_choice]
        r,g,b = int(rc[1:3],16),int(rc[3:5],16),int(rc[5:7],16)
        st.markdown(f"""<div style='background:rgba({r},{g},{b},0.06);border:1px solid rgba({r},{g},{b},0.20);
        border-radius:10px;padding:10px 14px;margin:6px 0 4px;font-size:13px;color:{rc};'>
        {ic} &nbsp; {desc}</div>""", unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username", key="login_u")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_p")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button(f"Sign In as {role_choice}  →", use_container_width=True):
            user = verify_login(username, password)
            if user:
                if user["Role"] != role_choice:
                    st.error(f"This account is '{user['Role']}'. Please select '{user['Role']}'.")
                else:
                    st.session_state.user = user
                    st.session_state.page = "Dashboard"
                    st.rerun()
            else:
                st.error("Invalid username or password.")

        st.markdown("""<div style='background:white;border-radius:0 0 22px 22px;padding:16px 36px 28px;
        box-shadow:0 24px 64px rgba(120,80,30,0.14);border:1px solid #e6ddd0;border-top:none;text-align:center;'>
        <div style='color:#c0b4a8;font-size:11px;'>NewsIntel Investigation System © 2026</div>
        </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
user       = st.session_state.user
role       = user["Role"]
uname      = user["Username"]
ADMIN_ONLY = role == "Admin"

# ── SIDEBAR ──
with st.sidebar:
    initials = "".join(p[0].upper() for p in user["Full_Name"].split()[:2])
    st.markdown(f"""
    <div style='padding:18px 16px 14px;margin-bottom:8px;background:{SURFACE};
    border-radius:14px;border:1px solid {BORDER};'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:44px;height:44px;border-radius:13px;
            background:linear-gradient(135deg,{ACCENT},{ACCENT2});
            display:flex;align-items:center;justify-content:center;
            font-size:16px;font-weight:700;color:white;flex-shrink:0;
            box-shadow:0 4px 12px rgba(184,118,58,0.30);'>{initials}</div>
            <div>
                <div style='font-size:14px;font-weight:700;color:{TEXT};
                font-family:"Playfair Display",serif;'>{user["Full_Name"]}</div>
                <div style='font-size:11px;color:{SUBTEXT};margin-top:2px;'>@{uname}</div>
                <span class='badge badge-{role.lower()}'>{role}</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    dm_label = "☀️  Light Mode" if dark else "🌙  Dark Mode"
    if st.button(dm_label, key="dm_toggle", use_container_width=True):
        st.session_state.dark_mode = not dark; st.rerun()

    st.markdown(f"<span class='sidebar-section-label'>Navigation</span>", unsafe_allow_html=True)

    if role == "Admin":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("👥","Users"),("💬","Complaints"),("📡","Live Feed"),("🤖","AI Chatbot")]
    elif role == "Journalist":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("💬","Complaints"),("📡","Live Feed"),("🤖","AI Chatbot")]
    else:
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("💬","Complaints"),("📡","Live Feed"),("🤖","AI Chatbot")]

    for ico, p in pages:
        if p == "AI Chatbot":
            # Highly highlighted and attractive button for AI Chatbot
            label = "✨ 🤖 AI Chatbot ✨"
            if st.button(label, key=f"nav_{p}", use_container_width=True, type="primary"):
                st.session_state.page = p; st.rerun()
        else:
            label = f"**{ico}  {p}**" if st.session_state.page == p else f"{ico}  {p}"
            if st.button(label, key=f"nav_{p}", use_container_width=True):
                st.session_state.page = p; st.rerun()

    st.markdown(f"<div class='custom-divider'></div>", unsafe_allow_html=True)
    if st.button("→  Sign Out", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

page = st.session_state.page


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def page_header(title, sub=""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if sub: st.markdown(f'<div class="page-sub">{sub}</div>', unsafe_allow_html=True)

def ok(msg):  st.success(f"✓  {msg}")
def err(msg): st.error(f"✗  {msg}")

def paginate(df, page_key, per_page=10):
    total   = len(df)
    n_pages = max(1, -(-total // per_page))
    cur     = st.session_state.get(page_key, 0)
    cur     = min(cur, n_pages - 1)
    start   = cur * per_page
    chunk   = df.iloc[start:start + per_page]

    st.markdown(f"""
    <div class='pagination-wrap'>
        <span class='pagination-info'>
            Showing {start+1}–{min(start+per_page, total)} of {total} records
            &nbsp;·&nbsp; Page {cur+1} of {n_pages}
        </span>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("← Prev", key=f"prev_{page_key}", disabled=cur == 0):
            st.session_state[page_key] = cur - 1; st.rerun()
    with c3:
        if st.button("Next →", key=f"next_{page_key}", disabled=cur >= n_pages - 1):
            st.session_state[page_key] = cur + 1; st.rerun()
    return chunk

def progress_ring_svg(pct, color, size=44):
    r = 16; circ = 2 * 3.14159 * r
    dash = pct / 100 * circ
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="{r}" fill="none" stroke="{BORDER}" stroke-width="4"/>
      <circle cx="20" cy="20" r="{r}" fill="none" stroke="{color}" stroke-width="4"
        stroke-dasharray="{dash:.1f} {circ:.1f}"
        stroke-dashoffset="{circ/4:.1f}" stroke-linecap="round"/>
      <text x="20" y="24" text-anchor="middle" font-size="9"
        font-family="DM Sans,sans-serif" fill="{color}" font-weight="700">{pct}%</text>
    </svg>"""

def story_card(row):
    cat    = str(row.get("Category",""))
    status = str(row.get("Status",""))
    title  = str(row.get("Title",""))
    cat_color  = CAT_COLORS.get(cat, ACCENT)
    cat_icon   = CAT_ICONS.get(cat, "📁")
    badge_cls  = "badge-ongoing" if status == "Ongoing" else "badge-completed"

    try: interviews = int(row.get("Total_Interviews", 0))
    except: interviews = 0
    try: documents = int(row.get("Total_Documents", 0))
    except: documents = 0
    try: notes = int(row.get("Total_Notes", 0))
    except: notes = 0
    try: events = int(row.get("Total_Events", 0))
    except: events = 0
    try: locations = int(row.get("Total_Locations", 0))
    except: locations = 0

    st.markdown(f"""
    <div class='intel-card'>
        <div class='intel-card-cat-strip' style='background:{cat_color};'></div>
        <div class='intel-card-header'>
            <div style='font-size:11px;color:{cat_color};font-weight:700;
            text-transform:uppercase;letter-spacing:0.08em;margin-bottom:5px;'>
                {cat_icon} {cat}
            </div>
            <div class='intel-card-title'>{title}</div>
            <div class='intel-card-badges'>
                <span class='badge {badge_cls}'>{status}</span>
                <span style='font-size:11px;color:{SUBTEXT};padding-top:3px;'>
                    #{row.get("Story_ID","")}
                </span>
            </div>
        </div>
        <div class='intel-card-stats'>
            <div class='intel-stat'>🎙️ <span class='intel-stat-val'>{interviews}</span>&nbsp;Interviews</div>
            <div class='intel-stat'>📄 <span class='intel-stat-val'>{documents}</span>&nbsp;Docs</div>
            <div class='intel-stat'>📝 <span class='intel-stat-val'>{notes}</span>&nbsp;Notes</div>
            <div class='intel-stat'>📅 <span class='intel-stat-val'>{events}</span>&nbsp;Events</div>
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════
if page == "Dashboard":
    stats   = get_stats()
    hour    = datetime.now().hour
    greeting= "Good morning" if hour<12 else "Good afternoon" if hour<18 else "Good evening"
    first   = user["Full_Name"].split()[0]
    today   = datetime.now().strftime("%A, %d %B %Y")

    st.markdown(f"""
    <div class='welcome-banner'>
        <div class='welcome-title'>{greeting}, {first} 👋</div>
        <div class='welcome-sub'>{today} &nbsp;·&nbsp; {role} Dashboard &nbsp;·&nbsp; NewsIntel</div>
    </div>""", unsafe_allow_html=True)

    if ADMIN_ONLY and stats.get("complaints",0) > 0:
        st.warning(f"⚠️  {stats['complaints']} open complaint(s) awaiting review.")

    st.markdown("<div class='section-title'>📰 Stories Overview</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col,(ico,val,lbl,clr) in zip([c1,c2,c3,c4],[
        ("📰",stats["stories"],  "Total Stories", ACCENT),
        ("🔄",stats["ongoing"],  "Ongoing",       "#c07010"),
        ("✅",stats["completed"],"Completed",     "#2a7a40"),
        ("👤",stats["sources"],  "Sources",       "#6050a0"),
    ]):
        with col:
            st.markdown(f"""<div class='stat-card' style='--card-color:{clr}'>
                <span class='stat-icon'>{ico}</span>
                <span class='stat-number'>{val}</span>
                <span class='stat-label'>{lbl}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🗂️ Investigation Assets</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col,(ico,val,lbl,clr) in zip([c1,c2,c3,c4],[
        ("🎙️",stats["interviews"],"Interviews",     "#c05020"),
        ("📄",stats["documents"], "Documents",      "#1a6a90"),
        ("📍",stats["locations"], "Locations",      "#9a3060"),
        ("📅",stats["events"],    "Timeline Events","#40703a"),
    ]):
        with col:
            st.markdown(f"""<div class='stat-card' style='--card-color:{clr}'>
                <span class='stat-icon'>{ico}</span>
                <span class='stat-number'>{val}</span>
                <span class='stat-label'>{lbl}</span>
            </div>""", unsafe_allow_html=True)

    total = max(stats["stories"], 1)
    st.markdown("<div class='section-title'>📊 Progress</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f"<div style='font-size:12px;font-weight:600;color:{SUBTEXT};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>🔄 Ongoing Rate</div>", unsafe_allow_html=True)
        st.progress(stats["ongoing"] / total)
        st.markdown(f"<div style='font-size:12px;color:{SUBTEXT};margin-top:4px;'>{stats['ongoing']} of {stats['stories']} active</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='font-size:12px;font-weight:600;color:{SUBTEXT};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>✅ Completion Rate</div>", unsafe_allow_html=True)
        st.progress(stats["completed"] / total)
        st.markdown(f"<div style='font-size:12px;color:{SUBTEXT};margin-top:4px;'>{stats['completed']} of {stats['stories']} closed</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🃏 Latest Story Cards</div>", unsafe_allow_html=True)
    df_s, _ = get_stories()
    if df_s is not None and not df_s.empty:
        cols = st.columns(4)
        for i, row in enumerate(df_s.head(4).itertuples()):
            with cols[i % 4]:
                story_card(row._asdict())


# ══════════════════════════════════════════════════════════
# DATA TABLES
# ══════════════════════════════════════════════════════════
elif page == "Data Tables":
    page_header("🗂️ Data Tables", "Manage all your records in one place")
    
    if ADMIN_ONLY:
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline"]
    elif role == "Journalist":
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline"]
    else:
        tab_names = ["Stories", "Sources"]

    tabs = st.tabs(tab_names)
    
    if "Stories" in tab_names:
        with tabs[tab_names.index("Stories")]:
            st.markdown("### Stories")
            
            page_header("🃏 Story Intelligence Cards", "Browse all investigations")
            df, _ = get_stories()
            if df is None or df.empty:
                st.info("No stories found.")
            else:
                # Search
                search = st.text_input("🔍 Search stories", placeholder="Filter by title, category, status…", label_visibility="collapsed")
                if search:
                    mask = df.apply(lambda c: c.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]

                chunk = paginate(df, "story_page", per_page=8)
                cols  = st.columns(4)
                for i, row in enumerate(chunk.itertuples()):
                    with cols[i % 4]:
                        story_card(row._asdict())



    if "Sources" in tab_names:
        with tabs[tab_names.index("Sources")]:
            st.markdown("### Sources")
            
            page_header("👤 Sources", "All registered investigation sources")
            df, _ = get_sources()
            if df is None or df.empty:
                st.info("No sources found.")
            else:
                search = st.text_input("🔍 Search sources", placeholder="Filter by name, type, credibility…", label_visibility="collapsed")
                if search:
                    mask = df.apply(lambda c: c.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]

                chunk = paginate(df, "source_page", per_page=8)
                cols  = st.columns(4)
                CRED_COLORS = {"High":"#2a7a40","Medium":"#c07010","Low":"#b02020"}
                CRED_BG     = {"High":"#e6f4eb","Medium":"#fff4e0","Low":"#fce8e8"}
                TYPE_ICON   = {"Person":"👤","Organization":"🏛️"}

                for i, row in enumerate(chunk.itertuples()):
                    d = row._asdict()
                    cred     = str(d.get("Credibility",""))
                    cred_c   = CRED_COLORS.get(cred, SUBTEXT)
                    cred_bg  = CRED_BG.get(cred, SURFACE)
                    typ      = str(d.get("Type",""))
                    typ_icon = TYPE_ICON.get(typ,"👤")
                    name     = str(d.get("Name",""))
                    initials = "".join(w[0].upper() for w in name.split()[:2])
                    interviews = d.get("Total_Interviews", 0)
                    with cols[i % 4]:
                        st.markdown(f"""
                        <div class='source-card'>
                            <div class='source-card-top'>
                                <div class='source-avatar' style='background:linear-gradient(135deg,{ACCENT},{ACCENT2});color:white;'>
                                    {typ_icon}
                                </div>
                                <div>
                                    <div class='source-name'>{name}</div>
                                    <div class='source-type'>{typ}</div>
                                </div>
                            </div>
                            <div style='display:flex;gap:8px;margin-bottom:10px;'>
                                <span style='background:{cred_bg};color:{cred_c};padding:3px 10px;
                                border-radius:20px;font-size:11px;font-weight:700;'>
                                    ● {cred} Credibility
                                </span>
                            </div>
                            <div class='source-stats'>
                                <div class='source-stat'>🎙️ <span>{interviews}</span> interviews</div>
                                <div class='source-stat'>🆔 <span>#{d.get("Source_ID","")}</span></div>
                            </div>
                        </div>""", unsafe_allow_html=True)



    if "Interviews" in tab_names:
        with tabs[tab_names.index("Interviews")]:
            st.markdown("### Interviews")
            
            page_header("🎙️ Interviews", "All conducted interviews")
            df, _ = get_interviews()
            if df is None or df.empty:
                st.info("No interviews found.")
            else:
                search = st.text_input("🔍 Search", placeholder="Filter interviews…", label_visibility="collapsed")
                if search:
                    mask = df.apply(lambda c: c.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]

                chunk = paginate(df, "interview_page", per_page=10)
                for row in chunk.itertuples():
                    d = row._asdict()
                    mode_icon  = "💻" if str(d.get("Mode","")) == "Online" else "🤝"
                    cred       = str(d.get("Credibility",""))
                    cred_color = {"High":"#2a7a40","Medium":"#c07010","Low":"#b02020"}.get(cred, SUBTEXT)
                    st.markdown(f"""
                    <div class='interview-card'>
                        <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                            <div>
                                <div style='font-weight:700;font-size:14px;color:{TEXT};margin-bottom:4px;'>
                                    {mode_icon} {d.get("Source_Name","")}
                                    <span style='font-size:11px;color:{cred_color};font-weight:600;
                                    background:rgba(0,0,0,0.04);padding:2px 8px;border-radius:10px;margin-left:6px;'>
                                    {cred}</span>
                                </div>
                                <div style='font-size:12px;color:{SUBTEXT};margin-bottom:6px;'>
                                    📰 {d.get("Story_Title","")} &nbsp;·&nbsp;
                                    📅 {str(d.get("Interview_Date",""))[:10]} &nbsp;·&nbsp;
                                    {d.get("Mode","")}
                                </div>
                                <div style='font-size:13px;color:{TEXT};line-height:1.5;opacity:0.85;'>
                                    {str(d.get("Transcript",""))[:120]}{"…" if len(str(d.get("Transcript","")))>120 else ""}
                                </div>
                            </div>
                            <div style='font-size:11px;color:{SUBTEXT};white-space:nowrap;margin-left:12px;'>
                                #{d.get("Interview_ID","")}
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)



    if "Documents" in tab_names:
        with tabs[tab_names.index("Documents")]:
            st.markdown("### Documents")
            
            page_header("📄 Documents", "All investigation documents")
            df, _ = get_documents()
            if df is None or df.empty:
                st.info("No documents found.")
            else:
                search = st.text_input("🔍 Search", placeholder="Filter documents…", label_visibility="collapsed")
                if search:
                    mask = df.apply(lambda c: c.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]

                chunk = paginate(df, "doc_page", per_page=10)
                cols  = st.columns(4)
                DOC_ICONS = {"PDF":"📕","Excel":"📗","Word":"📘","Financial Record":"💰",
                             "Witness Statement":"👁️","Official Order":"⚖️","Other":"📄"}
                for i, row in enumerate(chunk.itertuples()):
                    d = row._asdict()
                    doc_type = str(d.get("Document_Type",""))
                    doc_icon = DOC_ICONS.get(doc_type,"📄")
                    with cols[i % 4]:
                        st.markdown(f"""
                        <div class='doc-card'>
                            <div style='font-size:2rem;margin-bottom:10px;'>{doc_icon}</div>
                            <div style='font-weight:700;font-size:13.5px;color:{TEXT};
                            margin-bottom:8px;line-height:1.35;'>
                                {d.get("Document_Title","")}
                            </div>
                            <span class='doc-type-badge'>{doc_type}</span>
                            <div style='font-size:12px;color:{SUBTEXT};margin-top:10px;'>
                                📰 {d.get("Story_Title","")}<br>
                                📅 {str(d.get("Upload_Date",""))[:10]}
                            </div>
                        </div>""", unsafe_allow_html=True)



    if "Locations" in tab_names:
        with tabs[tab_names.index("Locations")]:
            st.markdown("### Locations")
            
            page_header("📍 Locations", "All investigation locations")
            df, _ = get_locations()
            if df is None or df.empty:
                st.info("No locations found.")
            else:
                search = st.text_input("🔍 Search", placeholder="Filter by city, state, country…", label_visibility="collapsed")
                if search:
                    mask = df.apply(lambda c: c.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]

                chunk = paginate(df, "loc_page", per_page=8)
                cols  = st.columns(4)
                for i, row in enumerate(chunk.itertuples()):
                    d = row._asdict()
                    with cols[i % 4]:
                        st.markdown(f"""
                        <div class='doc-card'>
                            <div style='font-size:2rem;margin-bottom:10px;'>📍</div>
                            <div style='font-weight:700;font-size:13.5px;color:{TEXT};margin-bottom:6px;'>
                                {d.get("Place_Name","")}
                            </div>
                            <div style='font-size:12px;color:{SUBTEXT};line-height:1.7;'>
                                🏙️ {d.get("City","")}, {d.get("State","")}<br>
                                🌍 {d.get("Country","")}<br>
                                📰 {d.get("Story_Title","")}
                            </div>
                        </div>""", unsafe_allow_html=True)



    if "Notes" in tab_names:
        with tabs[tab_names.index("Notes")]:
            st.markdown("### Notes")
            
            page_header("📝 Notes", "Investigation notes and observations")
            df, _ = get_notes()
            if df is None or df.empty:
                st.info("No notes found.")
            else:
                search = st.text_input("🔍 Search", placeholder="Filter notes…", label_visibility="collapsed")
                if search:
                    mask = df.apply(lambda c: c.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]

                chunk = paginate(df, "note_page", per_page=10)
                for row in chunk.itertuples():
                    d = row._asdict()
                    st.markdown(f"""
                    <div class='note-card'>
                        <div style='display:flex;justify-content:space-between;margin-bottom:8px;'>
                            <div style='font-weight:700;font-size:13px;color:{ACCENT};'>
                                📰 {d.get("Story_Title","")}
                            </div>
                            <div style='font-size:11px;color:{SUBTEXT};'>
                                📅 {str(d.get("Created_Date",""))[:10]}
                            </div>
                        </div>
                        <div style='font-size:14px;color:{TEXT};line-height:1.6;'>
                            {d.get("Content","")}
                        </div>
                    </div>""", unsafe_allow_html=True)



    if "Timeline" in tab_names:
        with tabs[tab_names.index("Timeline")]:
            st.markdown("### Timeline")
            
            page_header("📅 Timeline", "Key investigation events in chronological order")
            df, _ = get_timeline()
            if df is None or df.empty:
                st.info("No timeline events found.")
            else:
                search = st.text_input("🔍 Search", placeholder="Filter events…", label_visibility="collapsed")
                if search:
                    mask = df.apply(lambda c: c.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
                    df = df[mask]

                chunk = paginate(df, "timeline_page", per_page=10)
                for i, row in enumerate(chunk.itertuples()):
                    d    = row._asdict()
                    last = (i == len(chunk) - 1)
                    st.markdown(f"""
                    <div class='timeline-item'>
                        <div class='timeline-dot-wrap'>
                            <div class='timeline-dot'></div>
                            {"" if last else "<div class='timeline-line'></div>"}
                        </div>
                        <div class='timeline-content'>
                            <div class='timeline-title'>{d.get("Event_Title","")}</div>
                            <div class='timeline-meta'>
                                📅 {str(d.get("Event_Date",""))[:10]}
                                &nbsp;·&nbsp; 📰 {d.get("Story_Title","")}
                            </div>
                            <div class='timeline-desc'>{d.get("Event_Description","")}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)




# ══════════════════════════════════════════════════════════
# USERS
# ══════════════════════════════════════════════════════════
elif page == "Users":
    if not ADMIN_ONLY: st.warning("Admins only."); st.stop()
    page_header("👥 Users", "All system accounts")
    with st.expander("＋ Add New User"):
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            new_uname = c1.text_input("Username")
            new_pwd = c2.text_input("Password", type="password")
            new_fn = st.text_input("Full Name")
            new_role = st.selectbox("Role", ["Admin", "Journalist", "Viewer"])
            if st.form_submit_button("Create User"):
                if new_uname and new_pwd and new_fn:
                    aff, err = add_user(new_uname, new_pwd, new_role, new_fn)
                    if err:
                        st.error(err)
                    else:
                        st.success("User created successfully!")
                        st.rerun()
                else:
                    st.error("Please fill in all fields.")
    df, _ = get_users()
    if df is None or df.empty:
        st.info("No users found.")
    else:
        cols = st.columns(4)
        for i, row in enumerate(df.itertuples()):
            d        = row._asdict()
            role_val = str(d.get("Role",""))
            badge    = f"badge-{role_val.lower()}"
            initials = "".join(w[0].upper() for w in str(d.get("Full_Name","")).split()[:2])
            with cols[i % 4]:
                st.markdown(f'''
                <div class='source-card'>
                    <div class='source-card-top'>
                        <div class='source-avatar'
                        style='background:linear-gradient(135deg,#b8763a,#d4944e);color:white;font-size:16px;'>
                            {initials}
                        </div>
                        <div>
                            <div class='source-name'>{d.get("Full_Name","")}</div>
                            <div class='source-type'>@{d.get("Username","")}</div>
                        </div>
                    </div>
                    <span class='badge {badge}'>{role_val}</span>
                    <div style='font-size:11px;color:#8a7560;margin-top:8px;'>
                        Joined {str(d.get("Created_At",""))[:10]}
                    </div>
                </div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# COMPLAINTS
# ══════════════════════════════════════════════════════════
elif page == "Complaints":
    page_header("💬 Complaints")
    if ADMIN_ONLY:
        st.markdown('<div class="page-sub">Review and rectify journalist complaints</div>', unsafe_allow_html=True)
        df, _ = get_complaints()
        if df is not None and not df.empty:
            open_df = df[df["Status"]=="Open"]
            res_df  = df[df["Status"]=="Rectified"]
            c1,c2,c3 = st.columns(3)
            for col,(ico,val,lbl,clr) in zip([c1,c2,c3],[
                ("🔴",len(open_df),"Open","#b02020"),
                ("✅",len(res_df),"Rectified","#2a7a40"),
                ("📋",len(df),"Total","#b8763a"),
            ]):
                with col:
                    st.markdown(f'''<div class='stat-card' style='--card-color:{clr}'>
                        <span class='stat-icon'>{ico}</span>
                        <span class='stat-number'>{val}</span>
                        <span class='stat-label'>{lbl}</span>
                    </div>''', unsafe_allow_html=True)
            st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
            if not open_df.empty:
                st.markdown("<div style='font-weight:700;color:#b02020;margin-bottom:10px;'>🔴 Open (" + str(len(open_df)) + ")</div>", unsafe_allow_html=True)
                for row in open_df.itertuples():
                    st.markdown(f'''
                    <div class='complaint-card'>
                        <b style='color:#2c2010;font-size:15px;'>{row.Title}</b>
                        <span class='badge badge-open' style='margin-left:10px;'>Open</span><br>
                        <small style='color:#8a7560;'>By {row.Submitted_By} · {str(row.Created_At)[:16]}</small>
                        <p style='margin:10px 0 0;font-size:14px;color:#2c2010;line-height:1.5;'>{row.Description}</p>
                    </div>''', unsafe_allow_html=True)
                    note = st.text_input(f"Reply / Rectification note for #{row.Complaint_ID}", key=f"rn_{row.Complaint_ID}")
                    if st.button(f"✓ Rectify #{row.Complaint_ID}", key=f"res_{row.Complaint_ID}"):
                        n,e = resolve_complaint(row.Complaint_ID, note)
                        if e: err(e)
                        else: ok("Rectified!"); st.rerun()
            if not res_df.empty:
                st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
                st.markdown("<div style='font-weight:700;color:#2a7a40;margin-bottom:10px;'>✅ Rectified (" + str(len(res_df)) + ")</div>", unsafe_allow_html=True)
                for row in res_df.itertuples():
                    admin_note = getattr(row,"Admin_Note",None)
                    note_html = f'<div style="margin-top:8px;padding:8px;background:#e6f4eb;border-radius:8px;font-size:12px;color:#2a7a40;"><b>Note:</b> {admin_note}</div>' if admin_note else ""
                    st.markdown(f'''
                    <div class='complaint-card' style='border-left-color:#2a7a40;'>
                        <b style='color:#2c2010;'>{row.Title}</b>
                        <span class='badge badge-rectified' style='margin-left:10px;'>Rectified</span><br>
                        <small style='color:#8a7560;'>By {row.Submitted_By}</small>
                        <p style='margin:8px 0 4px;font-size:13px;color:#2c2010;'>{row.Description}</p>
                        {note_html}
                    </div>''', unsafe_allow_html=True)
        else:
            st.info("No complaints yet.")
    else:
        st.markdown('<div class="page-sub">Submit issues or feedback to administrators</div>', unsafe_allow_html=True)
        with st.expander("＋  Submit New Complaint"):
            ct = st.text_input("Title", key="c_t")
            cd = st.text_area("Description", key="c_d")
            if st.button("Submit", key="c_sub"):
                n,e = add_complaint(ct,cd,uname)
                if e: err(e)
                else: ok("Submitted!"); st.rerun()
        df, _ = get_complaints_for_user(uname)
        if df is not None and not df.empty:
            for row in df.itertuples():
                badge_cls = "badge-rectified" if row.Status=="Rectified" else "badge-open"
                admin_note = getattr(row,"Admin_Note",None)
                note_html = f"<div style='margin-top:8px;padding:8px;background:#e6f4eb;border-radius:8px;font-size:12px;color:#2a7a40;'><b>Admin note:</b> {admin_note}</div>" if admin_note else ""
                st.markdown(f'''
                <div class='complaint-card'>
                    <b>{row.Title}</b>
                    <span class='badge {badge_cls}' style='margin-left:8px;'>{row.Status}</span><br>
                    <small style='color:#8a7560;'>{str(row.Created_At)[:16]}</small>
                    <p style='margin:8px 0;font-size:13px;'>{row.Description}</p>
                    {note_html}
                </div>''', unsafe_allow_html=True)
        else:
            st.info("No complaints submitted yet.")
elif page == "Live Feed":
    page_header("📡 Live Feed","Real-time updates · refreshes every 5 seconds")
    st.info("💡 Open in two browsers to see live multi-user changes.")
    refresh_slot = st.empty()
    feed_slot    = st.empty()
    for _ in range(1000):
        df_s,_ = get_stories()
        df_c,_ = get_complaints()
        with feed_slot.container():
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("<div class='section-title'>📰 Latest Stories</div>", unsafe_allow_html=True)
                if df_s is not None and not df_s.empty:
                    for row in df_s.head(6).itertuples():
                        d = row._asdict()
                        story_card(d)
            with c2:
                st.markdown("<div class='section-title'>📣 Latest Complaints</div>", unsafe_allow_html=True)
                if df_c is not None and not df_c.empty:
                    for row in df_c.head(6).itertuples():
                        badge_cls = "badge-rectified" if row.Status=="Rectified" else "badge-open"
                        st.markdown(f"""
                        <div class='live-item' style='border-left-color:#e05050;'>
                            <b style='color:{TEXT};font-size:13.5px;'>{row.Title}</b>
                            <span class='badge {badge_cls}' style='margin-left:8px;'>{row.Status}</span><br>
                            <small style='color:{SUBTEXT};'>By {row.Submitted_By}</small>
                        </div>""", unsafe_allow_html=True)
        with refresh_slot.container():
            st.caption(f"🔄 Last updated: {datetime.now().strftime('%H:%M:%S')}")
        time.sleep(5)
        st.rerun()


# ══════════════════════════════════════════════════════════
# AI CHATBOT
# ══════════════════════════════════════════════════════════
elif page == "AI Chatbot":
    page_header("🤖 AI Chatbot","Ask anything about your investigations in plain English")
    samples = {
        "Admin":      ["Show all ongoing stories","Show the audit log","Which users are in the system?","Most active cities","List high credibility sources"],
        "Journalist": ["Show all crime stories","List sources in politics stories","Show all interviews this month","Which stories have no documents?","Show recent timeline events"],
        "Viewer":     ["Show all ongoing stories","List completed stories","Show recent timeline events","Which city has the most stories?"],
    }
    with st.sidebar:
        st.markdown(f"<span class='sidebar-section-label'>Try asking</span>", unsafe_allow_html=True)
        for q in samples.get(role,[]):
            if st.button(q, key=f"sq_{q[:25]}", use_container_width=True):
                st.session_state.selected_q = q

    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="chat-user">🧑 {chat["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bot">🤖 {chat["answer"]}</div>', unsafe_allow_html=True)
        if chat.get("sql"):
            with st.expander("🔍 SQL Query Used"):
                st.markdown(f'<div class="sql-box">{chat["sql"]}</div>', unsafe_allow_html=True)
        if chat.get("dataframe") is not None and not chat["dataframe"].empty:
            with st.expander("📊 View Data Table"):
                st.dataframe(chat["dataframe"], use_container_width=True, hide_index=True)
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    if st.session_state.chat_history:
        if st.button("🗑  Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []; st.rerun()

    user_input = st.chat_input("Ask a question about your investigations…")
    if st.session_state.selected_q:
        user_input = st.session_state.selected_q
        st.session_state.selected_q = None

    # AI Chatbot Examples
    st.markdown("<div style='margin-bottom: 10px; color: #8a7560; font-size: 13px;'><b>Example Questions:</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("📊 Show all ongoing stories"): user_input = "Show all ongoing stories"
    if c2.button("👥 List high credibility sources"): user_input = "List high credibility sources"
    if c3.button("📅 Show recent timeline events"): user_input = "Show recent timeline events"

    if user_input:
        with st.spinner("Analysing…"):
            result = ask_chatbot(user_input, role)
        st.session_state.chat_history.append({
            "question":  user_input,
            "answer":    result["answer"],
            "sql":       result["sql"],
            "dataframe": result.get("dataframe"),
        })
        st.rerun()
