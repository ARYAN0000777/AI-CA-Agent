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

# ─────────────────────────────────────────────────────────────────────────────
# 1. THE "ANTIGRAVITY" ULTRA-PREMIUM INTERFACE (FULL CSS RESTORED)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="KhataAI Pro | Stepout Studios", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

/* GLOBAL THEME DESIGN TOKENS */
:root {
  --purple:        #7C6FFF;
  --purple-dim:    rgba(124,111,255,0.12);
  --purple-glow:   rgba(124,111,255,0.25);
  --purple-border: rgba(124,111,255,0.22);
  --purple-border-hover: rgba(124,111,255,0.55);
  --green:         #00D68F;
  --green-glow:    rgba(0,214,143,0.18);
  --amber:         #FFB547;
  --bg:            #05050A;
  --bg-surface:    rgba(255,255,255,0.025);
  --border:        rgba(255,255,255,0.065);
  --text:          #EAE8F5;
  --muted:         #635F7A;
  --glass-bg:      rgba(12,10,28,0.55);
  --glass-blur:    blur(32px) saturate(160%);
  --radius:        18px;
}

/* RESET & BASE */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ANIMATED MESH BACKGROUND */
.bg-mesh { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bg-mesh span { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.5; will-change: transform; }
.bg-mesh span:nth-child(1) { width: 900px; height: 900px; top: -300px; left: -250px; background: radial-gradient(circle, rgba(124,111,255,0.22) 0%, transparent 70%); animation: drift1 25s infinite alternate; }
.bg-mesh span:nth-child(2) { width: 700px; height: 700px; bottom: -200px; right: -150px; background: radial-gradient(circle, rgba(0,214,143,0.15) 0%, transparent 70%); animation: drift2 30s infinite alternate; }
@keyframes drift1 { from { transform: translate(0,0); } to { transform: translate(100px,80px); } }
@keyframes drift2 { from { transform: translate(0,0); } to { transform: translate(-80px,-60px); } }

/* SIDEBAR — MASTER ADMIN LOOK */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(8,6,24,0.98) 0%, rgba(5,5,10,1) 100%) !important;
  border-right: 1px solid var(--purple-border) !important;
  backdrop-filter: blur(20px) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* TOPBAR DESIGN */
.khata-topbar { display: flex; align-items: center; justify-content: space-between; padding: 1.8rem 0 1.4rem; border-bottom: 1px solid var(--border); margin-bottom: 2rem; position: relative; z-index: 10; animation: fadeSlideDown 0.8s ease; }
@keyframes fadeSlideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }

.khata-logo { width: 50px; height: 50px; background: linear-gradient(140deg, #7C6FFF, #00D68F); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 32px rgba(124,111,255,0.4); animation: pulse 4s infinite; }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }

.khata-title { font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important; font-weight: 800 !important; background: linear-gradient(115deg, #FFFFFF 15%, #A89EFF 55%, #6EE7B7 100%); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }

/* TABS — GLASS DESIGN */
.stTabs [data-baseweb="tab-list"] { gap: 12px !important; background: rgba(255,255,255,0.03) !important; border-radius: 16px !important; padding: 8px !important; border: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { border-radius: 12px !important; color: #635F7A !important; padding: 12px 28px !important; font-weight: 700 !important; transition: all 0.3s ease !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(124,111,255,0.3) 0%, rgba(0,214,143,0.1) 100%) !important; color: white !important; box-shadow: 0 4px 20px rgba(124,111,255,0.2); border: 1px solid var(--purple-border) !important; }

/* METRIC CARDS */
.metric-card { background: var(--glass-bg); border: 1px solid var(--border); border-radius: 20px; padding: 1.8rem; backdrop-filter: var(--glass-blur); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.metric-card:hover { transform: translateY(-8px); border-color: var(--purple-border-hover); box-shadow: 0 15px 40px rgba(124,111,255,0.2); }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; color: white; margin-top: 8px; }

/* BUTTONS — NEON GLOW */
div.stButton > button {
  background: linear-gradient(135deg, #7C6FFF 0%, #5B4FE8 100%) !important;
  color: white !important; border-radius: 14px !important; border: none !important;
  font-weight: 700 !important; width: 100% !important; padding: 14px !important;
  letter-spacing: 0.5px !important; text-transform: uppercase !important;
  transition: all 0.3s ease !important; box-shadow: 0 4px 15px rgba(124,111,255,0.3) !important;
}
div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(124,111,255,0.5) !important; }

/* DATA EDITOR & TABLES */
[data-testid="stDataFrame"] { border-radius: 15px !important; border: 1px solid var(--border) !important; overflow: hidden !important; }

/* CHAT MESSAGES */
[data-testid="stChatMessage"] { background: rgba(255,255,255,0.02) !important; border-radius: 15px !important; border: 1px solid var(--border) !important; margin-bottom: 12px !important; }
</style>
<div class="bg-mesh"><span></span><span></span></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 2. STATE & API INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "admin_user" not in st.session_state: st.session_state.admin_user = "aryan"
if "admin_pass" not in st.session_state: st.session_state.admin_pass = "admin123"
if "company_name" not in st.session_state: st.session_state.company_name = "Stepout Studios"
if "scanned_data" not in st.session_state: st.session_state.scanned_data = None
if "ca_history" not in st.session_state: st.session_state.ca_history = []

# Clients Setup
AI_API_KEY = st.secrets["AI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    db_data = supabase.table("invoices").select("*").order("id", desc=True).execute().data
except:
    db_data = []

def clean_text(text):
    """Prevents PDF generation crashes with Unicode characters"""
    if pd.isna(text) or text is None: return ""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# ─────────────────────────────────────────────────────────────────────────────
# 3. SECURE LOGIN GATE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        st.markdown('<div style="background:rgba(8,6,20,0.85); padding:4rem; border-radius:30px; border:1px solid var(--purple-border); text-align:center; box-shadow:0 20px 60px rgba(0,0,0,0.5); backdrop-filter:blur(20px);">', unsafe_allow_html=True)
        st.markdown('<div class="khata-logo" style="margin:0 auto 2rem; width:70px; height:70px; font-size:2rem;">🔒</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="font-family:Syne; margin-bottom:2rem;">KhataAI Login</h1>', unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Admin Username", placeholder="Enter ID")
            p = st.text_input("Security PIN", type="password", placeholder="Enter PIN")
            if st.form_submit_button("AUTHENTICATE SYSTEM", use_container_width=True):
                if u == st.session_state.admin_user and p == st.session_state.admin_pass:
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("❌ Invalid Access Key")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 4. DASHBOARD HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="khata-topbar">
  <div style="display:flex; align-items:center; gap:1.2rem;">
    <div class="khata-logo">⚡</div>
    <div>
      <div class="khata-title">{st.session_state.company_name}</div>
      <div style="color:var(--muted); font-size:0.8rem; letter-spacing:1px;">MASTER ERP DASHBOARD • v5.0 PRO</div>
    </div>
  </div>
  <div style="display:flex; gap:1rem;">
    <div style="background:var(--purple-dim); border:1px solid var(--purple-border); padding:6px 16px; border-radius:20px; color:#B4ABFF; font-weight:700; font-size:0.7rem;">AI CONNECTED</div>
    <div style="background:rgba(0,214,143,0.1); border:1px solid rgba(0,214,143,0.2); padding:6px 16px; border-radius:20px; color:#6EE7B7; font-weight:700; font-size:0.7rem;">DB ACTIVE</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📸 Vision Scanner", "🎙️ Voice Entry", "📊 Ledger Dashboard", "⚙️ Tally Sync", "👨‍💼 Ask CA Sahab"])

# ══════════════════════════════════════════════
# TAB 1: VISION SCANNER (RETRY LOGIC FIXED)
# ══════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("### 📄 Upload Document")
        up = st.file_uploader("Drop Invoice (JPG/PNG/JPEG)", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if up and st.button("🚀 INITIATE DEEP SCAN", use_container_width=True):
            with st.spinner("AI is analyzing document structure... (Retry Mode Active)"):
                img = Image.open(up)
                prompt = 'Extract details from Indian GST invoice. Return ONLY JSON: {"vendor_name": "...", "gst_number": "...", "total_amount": 0.0, "invoice_date": "DD-MM-YYYY", "voucher_type": "Purchase"}'
                
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        # Humne model 2.0 kiya hai stability ke liye
                        res = ai_client.models.generate_content(model='gemini-2.0-flash', contents=[img, prompt])
                        raw_text = res.text.strip().replace("```json","").replace("```","").strip()
                        st.session_state.scanned_data = json.loads(raw_text)
                        st.rerun(); break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 4
                            st.warning(f"Server busy. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                            time.sleep(wait_time)
                        else: st.error("❌ Google Servers overloaded. Please try again after 2 mins.")
    with col2:
        if up: st.image(up, caption="Invoice Preview", use_container_width=True)

    if st.session_state.scanned_data:
        st.markdown("<br>### ✏️ Validate Extracted Metadata", unsafe_allow_html=True)
        sd = st.session_state.scanned_data
        with st.form("vision_save_form"):
            c1, c2 = st.columns(2)
            with c1: vn = st.text_input("Party Legal Name", value=sd.get("vendor_name",""))
            with c2: vg = st.text_input("GST Number", value=sd.get("gst_number",""))
            c3, c4 = st.columns(2)
            with c3: vt = st.number_input("Grand Total (INR) ₹", value=float(sd.get("total_amount",0)))
            with c4: vd = st.text_input("Invoice Date", value=sd.get("invoice_date","2026-04-09"))
            if st.form_submit_button("✅ COMMIT TO CLOUD STORAGE", use_container_width=True):
                supabase.table("invoices").insert({"vendor_name":vn, "gst_number":vg, "total_amount":vt, "invoice_date":vd, "voucher_type":"Purchase"}).execute()
                st.session_state.scanned_data = None; st.success("Transaction Logged!"); st.rerun()

# ══════════════════════════════════════════════
# TAB 3: LEDGER & PDF (UNICODE FIX)
# ══════════════════════════════════════════════
with tab3:
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card"><div style="color:var(--muted);font-size:0.75rem;letter-spacing:1px;">TOTAL LEDGER ENTRIES</div><div class="metric-value">{len(db_data)}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div style="color:var(--muted);font-size:0.75rem;letter-spacing:1px;">GROSS VOLUME</div><div class="metric-value">₹{sum([float(x.get("total_amount") or 0) for x in db_data]):,.0f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div style="color:var(--muted);font-size:0.75rem;letter-spacing:1px;">SYNC STATUS</div><div class="metric-value" style="color:var(--green);">ACTIVE</div></div>', unsafe_allow_html=True)

    if db_data:
        st.markdown("<br>### 📋 Active Business Ledger", unsafe_allow_html=True)
        df = pd.DataFrame(db_data)
        st.dataframe(df[['vendor_name', 'total_amount', 'invoice_date', 'voucher_type']], use_container_width=True)
        
        with st.expander("🖨️ Compile & Print PDF Invoice"):
            bill_opts = {f"Sr {idx+1} | {x['vendor_name']} | ₹{x['total_amount']}": x for idx, x in enumerate(db_data)}
            sel_key = st.selectbox("Select Record for PDF", options=list(bill_opts.keys()))
            if st.button("Generate Pro-forma Invoice"):
                bill = bill_opts[sel_key]
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(190, 10, txt=f"TAX INVOICE - {clean_text(st.session_state.company_name)}", ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", '', 12)
                pdf.cell(100, 10, txt=f"Billed To: {clean_text(bill.get('vendor_name'))}")
                pdf.cell(90, 10, txt=f"Date: {clean_text(bill.get('invoice_date'))}", ln=True)
                pdf.cell(190, 10, txt=f"Total Amount: Rs. {float(bill.get('total_amount',0)):,.2f}", ln=True)
                pdf_b = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 Click to Download PDF", pdf_b, file_name="invoice.pdf", mime="application/pdf", use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5: CA SAHAB (EPIC PERSONALITY FIX)
# ══════════════════════════════════════════════
with tab5:
    st.markdown("### 👨‍💼 Ask CA Sahab (Llama 3.3 Engine)")
    
    if st.button("Clear Chat / New Consultation 🔄"):
        st.session_state.ca_history = []; st.session_state.last_q = ""; st.rerun()

    if not st.session_state.ca_history:
        st.session_state.ca_history = [{"role": "assistant", "content": "Arre Aryan bhai, swagat hai! Tension mat lo, CA Sahab aa gaye hain. Boliye aaj dhandhe me kya system set karna hai? 😎"}]

    for m in st.session_state.ca_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    query = st.chat_input("Apna sawal yahan likhein (Solid Vibe mein)...")
    if query:
        st.session_state.ca_history.append({"role": "user", "content": query})
        with st.chat_message("user"): st.markdown(query)
        with st.chat_message("assistant"):
            with st.spinner("CA Sahab soch rahe hain... 🧠"):
                try:
                    # EPIC PROMPT FOR HUMAN VIBE
                    res = groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are 'CA Sahab'. Elite Indian CA. Talk like a friend/mentor in Hinglish. Be solid, confident, and epic. Never sound like a robot. Use words like Bhai, System, Bindass."},
                            {"role": "user", "content": query}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.85
                    )
                    ans = res.choices[0].message.content
                    st.markdown(ans)
                    st.session_state.ca_history.append({"role": "assistant", "content": ans})
                    
                    # VOICE OUTPUT ENGINE
                    tts = gTTS(text=ans.replace("*","").replace("#",""), lang='hi')
                    af = io.BytesIO(); tts.write_to_fp(af); af.seek(0)
                    st.audio(af, format='audio/mp3', autoplay=True)
                except Exception as e:
                    st.error(f"⚠️ CA Sahab is busy in a meeting. Error: {e}")
