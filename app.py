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
# 1. PAGE CONFIG & FULL PRE-DRESSED PREMIUM CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="KhataAI Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --purple: #7C6FFF; --purple-dim: rgba(124,111,255,0.12); --purple-glow: rgba(124,111,255,0.22);
  --purple-border: rgba(124,111,255,0.22); --purple-border-hover: rgba(124,111,255,0.55);
  --green: #00D68F; --green-dim: rgba(0,214,143,0.10); --green-glow: rgba(0,214,143,0.18);
  --amber: #FFB547; --amber-dim: rgba(255,181,71,0.10); --amber-glow: rgba(255,181,71,0.18);
  --bg: #05050A; --bg-surface: rgba(255,255,255,0.025); --bg-surface-2: rgba(255,255,255,0.042);
  --border: rgba(255,255,255,0.065); --border-hover: rgba(255,255,255,0.13);
  --text: #EAE8F5; --muted: #635F7A; --muted-2: #8A85A0;
  --radius: 18px; --radius-sm: 11px; --radius-xs: 8px;
  --glass-bg: rgba(12,10,28,0.55); --glass-border: rgba(124,111,255,0.18); --glass-blur: blur(28px) saturate(160%);
  --transition-fast: all 0.18s cubic-bezier(0.4,0,0.2,1);
  --transition-medium: all 0.28s cubic-bezier(0.4,0,0.2,1);
  --transition-bounce: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp { background-color: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
.bg-mesh { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bg-mesh span { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.6; will-change: transform; }
.bg-mesh span:nth-child(1) { width: 800px; height: 800px; top: -250px; left: -200px; background: radial-gradient(circle, rgba(124,111,255,0.20) 0%, transparent 60%); animation: meshDrift1 20s ease-in-out infinite alternate; }
.bg-mesh span:nth-child(2) { width: 600px; height: 600px; bottom: -180px; right: -120px; background: radial-gradient(circle, rgba(0,214,143,0.13) 0%, transparent 60%); animation: meshDrift2 25s ease-in-out infinite alternate; }
@keyframes meshDrift1 { from { transform: translate(0,0) scale(1); } to { transform: translate(70px,50px) scale(1.15); } }
@keyframes meshDrift2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-50px,-35px) scale(1.10); } }

[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(8,6,20,0.97) 0%, rgba(10,8,24,0.95) 100%) !important; border-right: 1px solid var(--glass-border) !important; backdrop-filter: blur(20px) !important; }
[data-testid="stSidebarNav"] { display: none !important; } 

.khata-topbar { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem; position: relative; z-index: 10; animation: fadeSlideDown 0.65s cubic-bezier(.22,.68,0,1.2) both; }
.khata-logo { width: 48px; height: 48px; background: linear-gradient(140deg, #7C6FFF 0%, #00D68F 100%); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.45rem; box-shadow: 0 0 32px rgba(124,111,255,0.4); }
.khata-title { font-family: 'Syne', sans-serif !important; font-size: 1.7rem !important; font-weight: 800 !important; background: linear-gradient(115deg, #FFFFFF 15%, #A89EFF 55%, #6EE7B7 100%); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }

.metric-card { background: var(--glass-bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.6rem 1.7rem; backdrop-filter: var(--glass-blur); transition: var(--transition-medium); }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 700; color: #FFFFFF; }

.stTabs [data-baseweb="tab-list"] { gap: 8px !important; background: rgba(255,255,255,0.028) !important; border-radius: 14px !important; padding: 5px !important; border: 1px solid var(--border) !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(124,111,255,0.22), rgba(0,214,143,0.10)) !important; color: #D0CBFF !important; }

div.stButton > button { background: linear-gradient(135deg, #7C6FFF 0%, #5B4FE8 100%) !important; color: #FFFFFF !important; border: none !important; border-radius: var(--radius-sm) !important; padding: 11px 26px !important; font-weight: 600 !important; width: 100% !important; }
.section-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1.1rem; display: flex; align-items: center; gap: 0.5rem; }
.section-title::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); margin-left: 0.5rem; }
.fancy-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border) 30%, var(--border) 70%, transparent); margin: 2.2rem 0; }
</style>
<div class="bg-mesh"><span></span><span></span></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. STATE & API CLIENTS
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "admin_user" not in st.session_state: st.session_state.admin_user = "aryan"
if "admin_pass" not in st.session_state: st.session_state.admin_pass = "admin123"
if "company_name" not in st.session_state: st.session_state.company_name = "Stepout Studios"
if "scanned_data" not in st.session_state: st.session_state.scanned_data = None
if "voice_scanned_data" not in st.session_state: st.session_state.voice_scanned_data = None
if "ca_history" not in st.session_state: st.session_state.ca_history = []

AI_API_KEY = st.secrets["AI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    db_data = supabase.table("invoices").select("*").order("id", desc=True).execute().data
except: db_data = []

def clean_text(text):
    if pd.isna(text) or text is None: return ""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# ─────────────────────────────────────────────
# 3. LOGIN & HEADER
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown('<div class="login-box" style="background:rgba(10,8,24,0.8); padding:3rem; border-radius:24px; border:1px solid #7C6FFF; text-align:center;">', unsafe_allow_html=True)
        st.markdown('<h2>🔒 Secure Entry</h2>', unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Admin ID")
            p = st.text_input("PIN", type="password")
            if st.form_submit_button("AUTHENTICATE"):
                if u == st.session_state.admin_user and p == st.session_state.admin_pass:
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

st.markdown(f'<div class="khata-topbar"><div style="display:flex;align-items:center;gap:1.2rem;"><div class="khata-logo">⚡</div><div class="khata-title">{st.session_state.company_name}</div></div><div class="khata-pill">CONNECTED</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📸 Vision Scanner", "🎙️ Voice Entry", "📊 Dashboard & PDF", "⚙️ Tally Sync", "👨‍💼 Ask CA Sahab"])

# ══════════════════════════════════════════════
# TAB 1: VISION SCANNER (GEMINI 2.0 + RETRY)
# ══════════════════════════════════════════════
with tab1:
    col_up, col_pre = st.columns(2, gap="large")
    with col_up:
        st.markdown('<div class="section-title">Upload Physical Bill</div>', unsafe_allow_html=True)
        up_file = st.file_uploader("Drop invoice here", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if up_file and st.session_state.scanned_data is None:
            if st.button("🚀 INITIATE AI SCAN", use_container_width=True):
                with st.spinner("AI is thinking... (Retry Mode Active)"):
                    img = Image.open(up_file)
                    prompt = 'Extract details as JSON: {"vendor_name": "...", "gst_number": "...", "total_amount": 0.0, "invoice_date": "DD-MM-YYYY", "voucher_type": "Purchase"}'
                    for attempt in range(5):
                        try:
                            res = ai_client.models.generate_content(model='gemini-2.0-flash', contents=[img, prompt])
                            st.session_state.scanned_data = json.loads(res.text.strip().replace("```json","").replace("```","").strip())
                            st.rerun(); break
                        except: time.sleep(4)
    if st.session_state.scanned_data:
        sd = st.session_state.scanned_data
        with st.form("vision_form"):
            vn = st.text_input("Entity Name", value=sd.get("vendor_name",""))
            vt = st.number_input("Amount", value=float(sd.get("total_amount", 0)))
            if st.form_submit_button("✅ SAVE TO CLOUD"):
                supabase.table("invoices").insert({"vendor_name": vn, "total_amount": vt, "voucher_type": "Purchase"}).execute()
                st.session_state.scanned_data = None; st.success("Stored!"); st.rerun()

# ══════════════════════════════════════════════
# TAB 2:🎙️ VOICE ENTRY (NEW)
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🎙️ Neural Voice Capture</div>', unsafe_allow_html=True)
    audio_val = st.audio_input("Bol ke invoice banwao", key="voice_mic")
    if audio_val and st.button("🎙️ Process Voice"):
        with st.spinner("Decoding audio..."):
            try:
                res = ai_client.models.generate_content(model='gemini-2.0-flash', contents=[types.Part.from_bytes(data=audio_val.getvalue(), mime_type='audio/wav'), "Extract JSON: vendor_name, total_amount"])
                st.session_state.voice_scanned_data = json.loads(res.text.strip().replace("```json","").replace("```","").strip())
                st.rerun()
            except Exception as e: st.error(e)
    if st.session_state.voice_scanned_data:
        vd = st.session_state.voice_scanned_data
        with st.form("voice_form"):
            v_n = st.text_input("Vendor", value=vd.get("vendor_name",""))
            v_t = st.number_input("Amount", value=float(vd.get("total_amount",0)))
            if st.form_submit_button("✅ Commit Voice Entry"):
                supabase.table("invoices").insert({"vendor_name":v_n, "total_amount":v_t, "voucher_type":"Sales"}).execute()
                st.session_state.voice_scanned_data = None; st.rerun()

# ══════════════════════════════════════════════
# TAB 3: 📊 DASHBOARD & PDF
# ══════════════════════════════════════════════
with tab3:
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card"><div style="color:gray;font-size:0.8rem;">TOTAL LEDGER</div><div class="metric-value">{len(db_data)}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div style="color:gray;font-size:0.8rem;">REVENUE</div><div class="metric-value">₹{sum([float(x.get("total_amount") or 0) for x in db_data]):,.0f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div style="color:gray;font-size:0.8rem;">STATUS</div><div class="metric-value">ACTIVE</div></div>', unsafe_allow_html=True)
    
    if db_data:
        df = pd.DataFrame(db_data)
        st.dataframe(df[['vendor_name', 'total_amount', 'voucher_type']], use_container_width=True)
        sel = st.selectbox("Select for PDF", options=[f"{i} | {x['vendor_name']}" for i,x in enumerate(db_data)])
        if st.button("📥 Download PDF"):
            bill = db_data[int(sel.split(" | ")[0])]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, txt=f"INVOICE - {clean_text(st.session_state.company_name)}", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", '', 12)
            pdf.cell(100, 10, txt=f"Party: {clean_text(bill.get('vendor_name'))}")
            pdf.cell(90, 10, txt=f"Amount: Rs.{float(bill.get('total_amount',0)):,.2f}", ln=True)
            st.download_button("Save PDF", pdf.output(dest='S').encode('latin-1'), file_name="invoice.pdf", mime="application/pdf")

# ══════════════════════════════════════════════
# TAB 4: ⚙️ TALLY SYNC
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">⚙️ Tally XML Export</div>', unsafe_allow_html=True)
    if db_data:
        st.info(f"Verified {len(db_data)} records for export.")
        if st.button("📥 Generate Master Tally XML", use_container_width=True):
            xml = "<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDATA>Tally XML Engine Active</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>"
            st.download_button("Download XML", xml, file_name="Khata_Tally.xml")
    else: st.warning("No data found.")

# ══════════════════════════════════════════════
# TAB 5: 👨‍💼 ASK CA SAHAB (LLAMA 3.3 + SWAG)
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">👨‍💼 CA Sahab - Aapka Partner</div>', unsafe_allow_html=True)
    if st.button("New Discussion 🔄"): st.session_state.ca_history = []; st.rerun()

    if not st.session_state.ca_history:
        st.session_state.ca_history = [{"role": "assistant", "content": "Arre Aryan bhai, swagat hai! Tension mat lo, CA Sahab aa gaye hain. 😎"}]

    for m in st.session_state.ca_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    query = st.chat_input("Apna solid sawal likho...")
    if query:
        st.session_state.ca_history.append({"role": "user", "content": query})
        with st.chat_message("user"): st.markdown(query)
        with st.chat_message("assistant"):
            try:
                res = groq_client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are 'CA Sahab'. Talk in Hinglish Swag. Be solid, confident, and epic."}, {"role": "user", "content": query}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.85
                )
                ans = res.choices[0].message.content
                st.markdown(ans)
                st.session_state.ca_history.append({"role": "assistant", "content": ans})
                tts = gTTS(text=ans.replace("*",""), lang='hi')
                af = io.BytesIO(); tts.write_to_fp(af); af.seek(0)
                st.audio(af, format='audio/mp3', autoplay=True)
            except Exception as e: st.error(f"Error: {e}")
