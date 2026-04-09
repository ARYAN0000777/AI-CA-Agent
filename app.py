import streamlit as st
import json
import pandas as pd
from google import genai
from google.genai import types
from PIL import Image
from supabase import create_client, Client
from fpdf import FPDF
import base64
import time
import requests
import io
from gtts import gTTS
from groq import Groq

# ─────────────────────────────────────────────
# 1. PAGE CONFIG & THE "CLAUDE-PREMIUM" CSS (FULL VERSION)
# ─────────────────────────────────────────────
st.set_page_config(page_title="KhataAI Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════════
   DESIGN TOKENS & ULTRA CSS
══════════════════════════════════════════ */
:root {
  --purple:        #7C6FFF;
  --purple-dim:    rgba(124,111,255,0.12);
  --purple-glow:   rgba(124,111,255,0.22);
  --purple-border: rgba(124,111,255,0.22);
  --purple-border-hover: rgba(124,111,255,0.55);
  --green:         #00D68F;
  --amber:         #FFB547;
  --bg:            #05050A;
  --bg-surface:    rgba(255,255,255,0.025);
  --border:        rgba(255,255,255,0.065);
  --text:          #EAE8F5;
  --muted:         #635F7A;
  --glass-bg:      rgba(12,10,28,0.55);
  --glass-blur:    blur(28px) saturate(160%);
}

/* RESET & BASE */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* Kill Streamlit's default white flash */
.stApp > header { background: transparent !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; max-width: 1280px !important; }
#MainMenu, footer, .stDeployButton { visibility: hidden !important; }

/* ANIMATED MESH BACKGROUND */
.bg-mesh { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bg-mesh span { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.6; will-change: transform; }
.bg-mesh span:nth-child(1) { width: 800px; height: 800px; top: -250px; left: -200px; background: radial-gradient(circle, rgba(124,111,255,0.20) 0%, transparent 60%); animation: meshDrift1 20s ease-in-out infinite alternate; }
.bg-mesh span:nth-child(2) { width: 600px; height: 600px; bottom: -180px; right: -120px; background: radial-gradient(circle, rgba(0,214,143,0.13) 0%, transparent 60%); animation: meshDrift2 25s ease-in-out infinite alternate; }
@keyframes meshDrift1 { from { transform: translate(0,0) scale(1); } to { transform: translate(70px,50px) scale(1.15); } }
@keyframes meshDrift2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-50px,-35px) scale(1.10); } }

/* SIDEBAR — FULL PREMIUM */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(8,6,20,0.97) 0%, rgba(10,8,24,0.95) 100%) !important;
  border-right: 1px solid var(--purple-border) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 4px 0 40px rgba(0,0,0,0.6) !important;
}
[data-testid="stSidebarNav"] { display: none !important; } 

/* TABS STYLING */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px !important;
  background: rgba(255,255,255,0.03) !important;
  border-radius: 14px !important;
  padding: 6px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px !important;
  color: var(--muted) !important;
  font-weight: 500 !important;
  padding: 10px 24px !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(124,111,255,0.25) 0%, rgba(0,214,143,0.12) 100%) !important;
  color: #FFFFFF !important;
  box-shadow: 0 4px 15px rgba(124,111,255,0.2);
}

/* METRIC CARDS */
.metric-card {
  background: var(--glass-bg);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.5rem;
  backdrop-filter: var(--glass-blur);
  transition: transform 0.3s ease;
}
.metric-card:hover { transform: translateY(-5px); border-color: var(--purple-border-hover); }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; color: white; }

/* CUSTOM TOPBAR */
.khata-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.5rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem;
}
.khata-logo { width: 50px; height: 50px; background: linear-gradient(140deg, #7C6FFF, #00D68F); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 20px rgba(124,111,255,0.4); }
.khata-title { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; background: linear-gradient(90deg, #FFF, #A89EFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* INPUT BOXES */
.stTextInput input, .stSelectbox div[data-baseweb="select"] {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border) !important;
  color: white !important;
  border-radius: 10px !important;
}

/* CHAT UI FOR CA SAHAB */
[data-testid="stChatMessage"] {
  background: rgba(255,255,255,0.03) !important;
  border-radius: 15px !important;
  border: 1px solid var(--border) !important;
  margin-bottom: 10px !important;
}

</style>
<div class="bg-mesh"><span></span><span></span><span></span></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. STATE & LOGIN
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "admin_user" not in st.session_state: st.session_state.admin_user = "aryan"
if "admin_pass" not in st.session_state: st.session_state.admin_pass = "admin123"
if "company_name" not in st.session_state: st.session_state.company_name = "Stepout Studios"
if "company_logo" not in st.session_state: st.session_state.company_logo = None

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown('<div style="background:rgba(10,8,24,0.8); padding:3rem; border-radius:24px; border:1px solid #7C6FFF; text-align:center;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color:white; font-family:Syne;">🔒 KhataAI Portal</h2>', unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("PIN", type="password")
            if st.form_submit_button("🔓 Authenticate", use_container_width=True):
                if u == st.session_state.admin_user and p == st.session_state.admin_pass:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# 3. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='text-align:center;'><div class='khata-logo' style='margin:0 auto 1rem;'>🏢</div><h2 style='color:white; font-family:Syne;'>{st.session_state.company_name}</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("⚙️ Preferences"):
        new_name = st.text_input("Workspace Name", value=st.session_state.company_name)
        if st.button("Save Changes"):
            st.session_state.company_name = new_name
            st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ─────────────────────────────────────────────
# 4. API CLIENTS
# ─────────────────────────────────────────────
AI_API_KEY   = st.secrets["AI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "scanned_data" not in st.session_state: st.session_state.scanned_data = None
if "voice_scanned_data" not in st.session_state: st.session_state.voice_scanned_data = None
try: db_data = supabase.table("invoices").select("*").order("id", desc=True).execute().data
except: db_data = []

# ─────────────────────────────────────────────
# 5. HEADER & TABS
# ─────────────────────────────────────────────
st.markdown(f"""<div class="khata-topbar"><div class="khata-brand"><div class="khata-logo">⚡</div><div><div class="khata-title">{st.session_state.company_name}</div><div class="khata-sub">KhataAI Powered • CA ERP v5.0</div></div></div><div class="khata-pill">MASTER ADMIN</div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📸 Vision Scanner", "🎙️ Voice Entry", "📊 Dashboard & PDF", "⚙️ Tally Sync", "👨‍💼 Ask CA Sahab"])

# --- TAB 1: VISION ---
with tab1:
    col_up, col_pre = st.columns(2, gap="large")
    with col_up:
        up_file = st.file_uploader("Upload GST Bill", type=["jpg","png","jpeg"])
        if up_file and st.session_state.scanned_data is None:
            if st.button("🚀 Process Invoice", use_container_width=True):
                with st.spinner("AI Analysis..."):
                    img = Image.open(up_file)
                    prompt = 'Extract details. Return ONLY JSON: {"voucher_type": "Purchase", "vendor_name": "...", "gst_number": "...", "total_amount": 0.0, "line_items": []}'
                    for attempt in range(3):
                        try:
                            ai_resp = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[img, prompt])
                            st.session_state.scanned_data = json.loads(ai_resp.text.strip().replace("```json","").replace("```","").strip())
                            st.rerun(); break
                        except: time.sleep(3)
    with col_pre:
        if up_file: st.image(up_file, use_container_width=True)
    if st.session_state.scanned_data:
        d = st.session_state.scanned_data
        with st.form("vision_form"):
            v_name = st.text_input("Party Name", value=d.get("vendor_name",""))
            v_total = st.number_input("Total Amount", value=float(d.get("total_amount",0.0)))
            if st.form_submit_button("✅ Save to Database"):
                supabase.table("invoices").insert({"vendor_name": v_name, "total_amount": v_total, "voucher_type":"Purchase"}).execute()
                st.session_state.scanned_data = None; st.rerun()

# --- TAB 2: VOICE ---
with tab2:
    audio = st.audio_input("Bol ke puchiye")
    if audio and st.session_state.voice_scanned_data is None:
        if st.button("🎙️ Process Voice"):
            with st.spinner("Transcribing..."):
                prompt = 'Listen to audio. Return ONLY JSON: {"vendor_name": "...", "total_amount": 0.0}'
                resp = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[types.Part.from_bytes(data=audio.getvalue(), mime_type='audio/wav'), prompt])
                st.session_state.voice_scanned_data = json.loads(resp.text.strip().replace("```json","").replace("```","").strip())
                st.rerun()
    if st.session_state.voice_scanned_data:
        vd = st.session_state.voice_scanned_data
        with st.form("voice_form"):
            vn = st.text_input("Vendor", value=vd.get("vendor_name",""))
            vt = st.number_input("Amount", value=float(vd.get("total_amount",0.0)))
            if st.form_submit_button("✅ Save Voice Entry"):
                supabase.table("invoices").insert({"vendor_name": vn, "total_amount": vt, "category":"Voice"}).execute()
                st.session_state.voice_scanned_data = None; st.rerun()

# --- TAB 3: DASHBOARD ---
with tab3:
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card purple"><div style="font-size:0.8rem; color:gray;">TOTAL ENTRIES</div><div class="metric-value">{len(db_data)}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card green"><div style="font-size:0.8rem; color:gray;">GROSS SALES</div><div class="metric-value">₹{sum([float(x.get("total_amount") or 0) for x in db_data]):,.0f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card amber"><div style="font-size:0.8rem; color:gray;">SYSTEM STATUS</div><div class="metric-value">ONLINE</div></div>', unsafe_allow_html=True)
    st.markdown("### 📋 Record Ledger")
    if db_data: st.dataframe(pd.DataFrame(db_data)[['vendor_name', 'total_amount', 'voucher_type']], use_container_width=True)

# --- TAB 5: CA SAHAB (GROQ + VOICE) ---
with tab5:
    st.markdown("### 👨‍💼 Ask CA Sahab (Powered by Groq)")
    if "ca_history" not in st.session_state: st.session_state.ca_history = [{"role": "assistant", "content": "Boliye bhai, aaj business me kya madad karu?"}]
    for m in st.session_state.ca_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    query = st.chat_input("Puchiye...")
    if query:
        st.session_state.ca_history.append({"role": "user", "content": query})
        with st.chat_message("user"): st.markdown(query)
        with st.chat_message("assistant"):
            with st.spinner("CA Sahab soch rahe hain..."):
                for attempt in range(3):
                    try:
                        res = groq_client.chat.completions.create(
                            messages=[{"role": "system", "content": "Tu ek expert CA hai. Hinglish me baat kar."}, {"role": "user", "content": query}],
                            model="llama3-70b-8192"
                        )
                        ans = res.choices[0].message.content
                        st.markdown(ans)
                        st.session_state.ca_history.append({"role": "assistant", "content": ans})
                        # Audio
                        tts = gTTS(text=ans.replace("*",""), lang='hi')
                        afp = io.BytesIO(); tts.write_to_fp(afp); afp.seek(0)
                        st.audio(afp, format='audio/mp3', autoplay=True)
                        break
                    except: time.sleep(3)
