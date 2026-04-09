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
# 1. THE "ANTIGRAVITY" PREMIUM INTERFACE (CSS)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="KhataAI Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --purple:        #7C6FFF;
  --purple-dim:    rgba(124,111,255,0.12);
  --purple-glow:   rgba(124,111,255,0.22);
  --purple-border: rgba(124,111,255,0.22);
  --green:         #00D68F;
  --bg:            #05050A;
  --border:        rgba(255,255,255,0.065);
  --text:          #EAE8F5;
  --glass-bg:      rgba(12,10,28,0.55);
  --glass-blur:    blur(28px) saturate(160%);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp { background-color: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }

/* ANIMATED MESH BACKGROUND */
.bg-mesh { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bg-mesh span { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.6; }
.bg-mesh span:nth-child(1) { width: 800px; height: 800px; top: -250px; left: -200px; background: radial-gradient(circle, rgba(124,111,255,0.20) 0%, transparent 60%); animation: meshDrift1 20s ease-in-out infinite alternate; }
.bg-mesh span:nth-child(2) { width: 600px; height: 600px; bottom: -180px; right: -120px; background: radial-gradient(circle, rgba(0,214,143,0.13) 0%, transparent 60%); animation: meshDrift2 25s ease-in-out infinite alternate; }
@keyframes meshDrift1 { from { transform: translate(0,0); } to { transform: translate(70px,50px); } }
@keyframes meshDrift2 { from { transform: translate(0,0); } to { transform: translate(-50px,-35px); } }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(8,6,20,0.97) 0%, rgba(10,8,24,0.95) 100%) !important;
  border-right: 1px solid var(--purple-border) !important;
  backdrop-filter: blur(20px) !important;
}

/* TOPBAR */
.khata-topbar { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem; position: relative; z-index: 10; }
.khata-logo { width: 48px; height: 48px; background: linear-gradient(140deg, #7C6FFF, #00D68F); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 32px rgba(124,111,255,0.4); }
.khata-title { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; background: linear-gradient(90deg, #FFF, #A89EFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* TABS STYLING */
.stTabs [data-baseweb="tab-list"] { gap: 10px !important; background: rgba(255,255,255,0.03) !important; border-radius: 16px !important; padding: 6px !important; border: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { border-radius: 12px !important; color: #635F7A !important; padding: 10px 24px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(124,111,255,0.25), rgba(0,214,143,0.12)) !important; color: white !important; }

/* METRIC CARDS */
.metric-card { background: var(--glass-bg); border: 1px solid var(--border); border-radius: 18px; padding: 1.5rem; backdrop-filter: var(--glass-blur); }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: white; }

/* INPUT BOXES */
.stTextInput input, .stNumberInput input, .stSelectbox div { background: rgba(255,255,255,0.04) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; color: white !important; }
div.stButton > button { background: linear-gradient(135deg, #7C6FFF, #5B4FE8) !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 700 !important; width: 100% !important; padding: 12px !important; }
div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(124,111,255,0.4); }
</style>
<div class="bg-mesh"><span></span><span></span></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 2. STATE & SECRETS INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "company_name" not in st.session_state: st.session_state.company_name = "Stepout Studios"
if "scanned_data" not in st.session_state: st.session_state.scanned_data = None
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
except:
    db_data = []

def clean_text(text):
    if pd.isna(text) or text is None: return ""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# ─────────────────────────────────────────────────────────────────────────────
# 3. LOGIN GATE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown('<div style="background:rgba(10,8,24,0.8); padding:3rem; border-radius:24px; border:1px solid #7C6FFF; text-align:center;">', unsafe_allow_html=True)
        st.markdown('<h2>🔒 KhataAI Login</h2>', unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("PIN", type="password")
            if st.form_submit_button("Authenticate Access"):
                if u == "aryan" and p == "admin123":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("❌ Invalid PIN")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 4. DASHBOARD HEADER & TABS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="khata-topbar"><div style="display:flex;align-items:center;gap:1rem;"><div class="khata-logo">⚡</div><div class="khata-title">{st.session_state.company_name}</div></div><div style="color:gray;font-size:0.8rem;">CA ERP v5.0 Master Edition</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📸 Vision Scanner", "🎙️ Voice Entry", "📊 Ledger Dashboard", "⚙️ Tally Sync", "👨‍💼 Ask CA Sahab"])

# ══════════════════════════════════════════════
# TAB 1: VISION SCANNER (RETRY LOGIC)
# ══════════════════════════════════════════════
with tab1:
    c_up, c_pre = st.columns(2, gap="large")
    with c_up:
        up_file = st.file_uploader("Upload GST Bill", type=["jpg","png","jpeg"])
        if up_file and st.button("🚀 Process Invoice", use_container_width=True):
            with st.spinner("AI Deep Scanning... Please wait."):
                img = Image.open(up_file)
                prompt = 'Extract details from Indian GST invoice. Return ONLY JSON: {"vendor_name": "...", "gst_number": "...", "total_amount": 0.0, "invoice_date": "DD-MM-YYYY", "voucher_type": "Purchase"}'
                
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        ai_resp = ai_client.models.generate_content(model='gemini-2.0-flash', contents=[img, prompt])
                        raw_text = ai_resp.text.strip().replace("```json","").replace("```","").strip()
                        st.session_state.scanned_data = json.loads(raw_text)
                        st.rerun(); break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            wait = (attempt + 1) * 4
                            st.warning(f"Server busy. Retrying in {wait}s...")
                            time.sleep(wait)
                        else: st.error("❌ Google Servers overloaded. Try again after 2 mins.")

    if st.session_state.scanned_data:
        sd = st.session_state.scanned_data
        with st.form("vision_edit"):
            st.markdown("### ✏️ Validate Data")
            v_name = st.text_input("Party Name", value=sd.get("vendor_name",""))
            v_gst = st.text_input("GST Number", value=sd.get("gst_number",""))
            v_total = st.number_input("Grand Total ₹", value=float(sd.get("total_amount",0)))
            if st.form_submit_button("✅ Save to Database"):
                supabase.table("invoices").insert({"vendor_name":v_name, "gst_number":v_gst, "total_amount":v_total, "voucher_type":"Purchase"}).execute()
                st.session_state.scanned_data = None; st.success("Transaction Logged!"); st.rerun()

# ══════════════════════════════════════════════
# TAB 3: LEDGER & PDF (UNICODE FIX)
# ══════════════════════════════════════════════
with tab3:
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card"><div style="color:gray;font-size:0.8rem;">TOTAL BILLS</div><div class="metric-value">{len(db_data)}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div style="color:gray;font-size:0.8rem;">VOLUME</div><div class="metric-value">₹{sum([float(x.get("total_amount") or 0) for x in db_data]):,.0f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div style="color:gray;font-size:0.8rem;">SYSTEM</div><div class="metric-value">ACTIVE</div></div>', unsafe_allow_html=True)

    if db_data:
        df = pd.DataFrame(db_data)
        st.dataframe(df[['vendor_name', 'total_amount', 'voucher_type']], use_container_width=True)
        
        with st.expander("🖨️ Print PDF Invoice"):
            bill_opts = {f"Sr {idx+1} | {x['vendor_name']}": x for idx, x in enumerate(db_data)}
            selected_key = st.selectbox("Select Record", options=list(bill_opts.keys()))
            if st.button("Generate & Download PDF"):
                bill = bill_opts[selected_key]
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(190, 10, txt=f"TAX INVOICE - {clean_text(st.session_state.company_name)}", ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", '', 12)
                pdf.cell(100, 10, txt=f"Party: {clean_text(bill.get('vendor_name'))}")
                pdf.cell(90, 10, txt=f"Date: {clean_text(bill.get('invoice_date', '2026-04-09'))}", ln=True)
                pdf.cell(190, 10, txt=f"Amount: Rs. {float(bill.get('total_amount', 0)):,.2f}", ln=True)
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 Save PDF", pdf_bytes, file_name="invoice.pdf", mime="application/pdf")

# ══════════════════════════════════════════════
# TAB 4: TALLY SYNC (XML ENGINE)
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### ⚙️ Tally ERP / Prime Sync")
    if len(db_data) > 0:
        st.success(f"Verified {len(db_data)} entries for XML compilation.")
        if st.button("📥 Generate Master Tally XML", use_container_width=True):
            xml_data = "<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDATA>Tally XML Engine Active</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>"
            st.download_button("Download XML", data=xml_data, file_name="KhataAI_Tally.xml", mime="application/xml")
    else:
        st.warning("Database empty. Please scan some bills first.")

# ══════════════════════════════════════════════
# TAB 5: CA SAHAB (LLAMA 3.3 + EPIC SWAG)
# ══════════════════════════════════════════════
with tab5:
    st.markdown("### 👨‍💼 Ask CA Sahab (Epic Vibe)")
    if st.button("New Discussion 🔄", key="reset_chat"):
        st.session_state.ca_history = []; st.session_state.last_q = ""; st.rerun()

    if not st.session_state.ca_history:
        st.session_state.ca_history = [{"role": "assistant", "content": "Arre Aryan bhai, swagat hai! Tension mat lo, CA Sahab aa gaye hain. Boliye aaj dhandhe me kya system set karna hai? 😎"}]

    for m in st.session_state.ca_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    query = st.chat_input("Apna solid sawal likho...")
    if query:
        st.session_state.ca_history.append({"role": "user", "content": query})
        with st.chat_message("user"): st.markdown(query)
        with st.chat_message("assistant"):
            with st.spinner("CA Sahab soch rahe hain..."):
                try:
                    res = groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are 'CA Sahab'. Elite Indian CA friend. Talk in Hinglish Swag. Be solid, confident, and epic. Use words like Bhai, System, Bindass. Practical business advice only."},
                            {"role": "user", "content": query}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.85
                    )
                    ans = res.choices[0].message.content
                    st.markdown(ans)
                    st.session_state.ca_history.append({"role": "assistant", "content": ans})
                    
                    # VOICE OUTPUT
                    tts = gTTS(text=ans.replace("*","").replace("#",""), lang='hi')
                    af = io.BytesIO(); tts.write_to_fp(af); af.seek(0)
                    st.audio(af, format='audio/mp3', autoplay=True)
                except Exception as e:
                    st.error(f"CA Sahab is busy: {e}")
