import streamlit as st
import json
import pandas as pd
from google import genai
from PIL import Image
from supabase import create_client, Client

# ─────────────────────────────────────────────
# 1. PAGE CONFIG & ULTRA PREMIUM DARK THEME
# ─────────────────────────────────────────────
st.set_page_config(page_title="KhataAI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --purple: #7C6FFF;
  --purple-dim: rgba(124,111,255,0.15);
  --purple-border: rgba(124,111,255,0.25);
  --green: #00D68F;
  --green-dim: rgba(0,214,143,0.12);
  --amber: #FFB547;
  --amber-dim: rgba(255,181,71,0.12);
  --bg: #060608;
  --surface: rgba(255,255,255,0.03);
  --border: rgba(255,255,255,0.07);
  --text: #EAE8F5;
  --muted: #6B6880;
  --radius: 16px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container { padding: 0 2.5rem 4rem !important; max-width: 1300px !important; }

/* ── ANIMATED MESH BACKGROUND ── */
.bg-mesh {
  position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden;
}
.bg-mesh span {
  position: absolute; border-radius: 50%;
  filter: blur(80px); opacity: 0.55;
}
.bg-mesh span:nth-child(1) {
  width: 700px; height: 700px; top: -200px; left: -180px;
  background: radial-gradient(circle, rgba(124,111,255,0.22) 0%, transparent 65%);
  animation: meshDrift1 18s ease-in-out infinite alternate;
}
.bg-mesh span:nth-child(2) {
  width: 550px; height: 550px; bottom: -150px; right: -100px;
  background: radial-gradient(circle, rgba(0,214,143,0.15) 0%, transparent 65%);
  animation: meshDrift2 22s ease-in-out infinite alternate;
}
.bg-mesh span:nth-child(3) {
  width: 400px; height: 400px; top: 40%; left: 45%;
  background: radial-gradient(circle, rgba(255,181,71,0.08) 0%, transparent 65%);
  animation: meshDrift3 16s ease-in-out infinite alternate;
}
@keyframes meshDrift1 { from { transform: translate(0,0) scale(1); } to { transform: translate(60px,40px) scale(1.12); } }
@keyframes meshDrift2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-40px,-30px) scale(1.08); } }
@keyframes meshDrift3 { from { transform: translate(0,0) scale(1); } to { transform: translate(20px,-50px) scale(1.15); } }

/* ── HERO HEADER ── */
.khata-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 2rem 0 1.2rem; position: relative; z-index: 10;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
  animation: fadeSlideDown 0.7s cubic-bezier(.22,.68,0,1.2) both;
}
@keyframes fadeSlideDown {
  from { opacity: 0; transform: translateY(-18px); }
  to   { opacity: 1; transform: translateY(0); }
}
.khata-brand { display: flex; align-items: center; gap: 1rem; }
.khata-logo {
  width: 46px; height: 46px;
  background: linear-gradient(135deg, #7C6FFF 0%, #00D68F 100%);
  border-radius: 13px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem;
  box-shadow: 0 0 0 1px rgba(124,111,255,0.4), 0 0 28px rgba(124,111,255,0.35);
  animation: logoPulse 3s ease-in-out infinite;
}
@keyframes logoPulse {
  0%, 100% { box-shadow: 0 0 0 1px rgba(124,111,255,0.4), 0 0 28px rgba(124,111,255,0.35); }
  50% { box-shadow: 0 0 0 1px rgba(124,111,255,0.6), 0 0 44px rgba(124,111,255,0.55); }
}
.khata-title {
  font-family: 'Syne', sans-serif !important;
  font-size: 1.75rem !important;
  font-weight: 800 !important;
  background: linear-gradient(120deg, #FFFFFF 20%, #7C6FFF 60%, #00D68F 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1 !important;
  letter-spacing: -0.5px;
}
.khata-sub {
  font-size: 0.78rem;
  color: var(--muted);
  font-weight: 400;
  margin-top: 3px;
  letter-spacing: 0.4px;
}
.khata-pill {
  background: var(--purple-dim);
  border: 1px solid var(--purple-border);
  color: #A89EFF;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  gap: 6px !important;
  background: rgba(255,255,255,0.03) !important;
  border-radius: 14px !important;
  padding: 5px !important;
  border: 1px solid var(--border) !important;
  position: relative; z-index: 5;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 10px !important;
  color: var(--muted) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  padding: 8px 22px !important;
  border: none !important;
  transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(124,111,255,0.2), rgba(0,214,143,0.1)) !important;
  color: #C4BEFF !important;
  font-weight: 600 !important;
  box-shadow: inset 0 0 0 1px rgba(124,111,255,0.3) !important;
}

/* ── METRIC CARDS ── */
.metric-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem 1.6rem;
  position: relative; overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  animation: cardReveal 0.6s cubic-bezier(.22,.68,0,1.2) both;
  cursor: default;
}
.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 48px rgba(0,0,0,0.4);
}
.metric-card.purple:hover { border-color: rgba(124,111,255,0.35); box-shadow: 0 16px 48px rgba(124,111,255,0.15); }
.metric-card.green:hover  { border-color: rgba(0,214,143,0.35);  box-shadow: 0 16px 48px rgba(0,214,143,0.12); }
.metric-card.amber:hover  { border-color: rgba(255,181,71,0.35);  box-shadow: 0 16px 48px rgba(255,181,71,0.12); }

@keyframes cardReveal {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.metric-card:nth-child(1) { animation-delay: 0.05s; }
.metric-card:nth-child(2) { animation-delay: 0.15s; }
.metric-card:nth-child(3) { animation-delay: 0.25s; }

.metric-card::before {
  content: ''; position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  transition: opacity 0.25s ease;
}
.metric-card::after {
  content: ''; position: absolute;
  top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
  transition: left 0.5s ease;
}
.metric-card:hover::after { left: 100%; }

.metric-card.purple::before { background: linear-gradient(90deg, #7C6FFF, #A89EFF); }
.metric-card.green::before  { background: linear-gradient(90deg, #00D68F, #6EE7B7); }
.metric-card.amber::before  { background: linear-gradient(90deg, #FFB547, #FCD34D); }
.metric-card.center { text-align: center; }

.metric-icon { font-size: 1.6rem; margin-bottom: 0.75rem; display: block; }
.metric-label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.9px; font-weight: 500; margin-bottom: 0.35rem; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 700; color: #FFFFFF; line-height: 1; }
.metric-value.purple { color: #A89EFF; }
.metric-value.green  { color: #6EE7B7; }
.metric-value.amber  { color: #FCD34D; }

/* Animated counter shimmer */
.metric-value { position: relative; }

/* ── SECTIONS ── */
.section-title {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 1rem;
  display: flex; align-items: center; gap: 0.5rem;
  position: relative; z-index: 5;
}
.section-badge {
  background: var(--purple-dim);
  color: #A89EFF;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  font-family: 'JetBrains Mono', monospace;
  border: 1px solid var(--purple-border);
}

/* ── UPLOADER ── */
.stFileUploader > div {
  background: rgba(124,111,255,0.04) !important;
  border: 2px dashed rgba(124,111,255,0.25) !important;
  border-radius: var(--radius) !important;
  transition: border-color 0.3s, background 0.3s !important;
}
.stFileUploader > div:hover {
  border-color: rgba(124,111,255,0.5) !important;
  background: rgba(124,111,255,0.07) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
  border-color: rgba(124,111,255,0.5) !important;
  box-shadow: 0 0 0 3px rgba(124,111,255,0.1) !important;
}

/* ── BUTTONS ── */
div.stButton > button {
  background: linear-gradient(135deg, #7C6FFF, #5B4FE8) !important;
  color: white !important;
  border: none !important;
  border-radius: 11px !important;
  padding: 11px 24px !important;
  font-weight: 600 !important;
  font-family: 'DM Sans', sans-serif !important;
  width: 100%;
  box-shadow: 0 4px 20px rgba(124,111,255,0.3) !important;
  transition: all 0.2s ease !important;
  position: relative !important;
  overflow: hidden !important;
}
div.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 32px rgba(124,111,255,0.45) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }

div.stDownloadButton > button {
  background: linear-gradient(135deg, #00D68F, #00A86B) !important;
  color: white !important;
  border: none !important;
  border-radius: 11px !important;
  padding: 13px 28px !important;
  font-weight: 600 !important;
  font-family: 'DM Sans', sans-serif !important;
  box-shadow: 0 4px 24px rgba(0,214,143,0.3) !important;
  transition: all 0.2s ease !important;
}
div.stDownloadButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 36px rgba(0,214,143,0.45) !important;
}

/* ── EXPORT CARD ── */
.export-card {
  background: linear-gradient(135deg, rgba(0,214,143,0.06), rgba(124,111,255,0.06));
  border: 1px solid rgba(0,214,143,0.18);
  border-radius: 20px;
  padding: 2.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  animation: cardReveal 0.6s ease both;
}
.export-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,214,143,0.4), transparent);
}
.export-icon {
  font-size: 3rem; margin-bottom: 1rem; display: block;
  filter: drop-shadow(0 0 20px rgba(0,214,143,0.5));
  animation: iconBounce 2.5s ease-in-out infinite;
}
@keyframes iconBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.export-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.4rem; font-weight: 700; color: #FFFFFF;
}
.export-desc { color: var(--muted); font-size: 0.87rem; margin-top: 0.5rem; line-height: 1.6; }

/* ── DIVIDER ── */
.fancy-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin: 2rem 0;
}

/* ── DATA EDITOR & DATAFRAME ── */
.stDataFrame, [data-testid="stDataFrame"] {
  border-radius: 12px !important;
  overflow: hidden;
  border: 1px solid var(--border) !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
  background: rgba(239,68,68,0.06) !important;
  border: 1px solid rgba(239,68,68,0.15) !important;
  border-radius: 10px !important;
  color: #FCA5A5 !important;
}

/* ── FORM SUBMIT FEEDBACK ── */
.success-toast {
  background: linear-gradient(135deg, rgba(0,214,143,0.12), rgba(0,214,143,0.06));
  border: 1px solid rgba(0,214,143,0.25);
  border-radius: 12px;
  padding: 0.9rem 1.2rem;
  color: #6EE7B7;
  font-weight: 500;
  display: flex; align-items: center; gap: 0.6rem;
  animation: toastSlide 0.4s cubic-bezier(.22,.68,0,1.2) both;
}
@keyframes toastSlide {
  from { opacity: 0; transform: translateX(-12px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ── SCAN STEP INDICATOR ── */
.step-row {
  display: flex; align-items: center; gap: 0.75rem;
  margin-bottom: 1.5rem;
  animation: fadeSlideDown 0.5s ease both;
}
.step-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--purple-dim);
  border: 1px solid var(--purple-border);
  color: #A89EFF;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.step-label { font-size: 0.85rem; font-weight: 500; color: var(--text); }

/* ── SPINNER OVERRIDE ── */
[data-testid="stSpinner"] > div {
  border-top-color: var(--purple) !important;
}

/* ── IMAGE PREVIEW FRAME ── */
.preview-frame {
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  background: rgba(255,255,255,0.02);
  animation: cardReveal 0.5s ease both;
}

/* ── SELECTBOX ── */
.stSelectbox > div > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
}

/* ── INFO BOX ── */
.stAlert {
  background: rgba(124,111,255,0.08) !important;
  border: 1px solid var(--purple-border) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
}

/* z-index fix */
section[data-testid="stSidebar"] { z-index: 999; }
.stTabs { position: relative; z-index: 5; }
</style>

<!-- Mesh background -->
<div class="bg-mesh">
  <span></span><span></span><span></span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. CLIENT SETUP
# ─────────────────────────────────────────────
AI_API_KEY   = st.secrets["AI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "scanned_data" not in st.session_state:
    st.session_state.scanned_data = None

try:
    response = supabase.table("invoices").select("*").order("id", desc=True).execute()
    db_data = response.data
except Exception:
    db_data = []

# ─────────────────────────────────────────────
# 3. HERO HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="khata-topbar">
  <div class="khata-brand">
    <div class="khata-logo">⚡</div>
    <div>
      <div class="khata-title">KhataAI</div>
      <div class="khata-sub">Smart CA Assistant — GST · Tally · Cloud</div>
    </div>
  </div>
  <div class="khata-pill">v2.0 PRO</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📸  Scan Invoice", "📊  Analytics", "⚙️  Tally Export"])

# ══════════════════════════════════════════════
# TAB 1 — SCAN & EDIT
# ══════════════════════════════════════════════
with tab1:
    col_upload, col_preview = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown("""
        <div class="step-row"><div class="step-num">1</div><div class="step-label">Upload your GST invoice image</div></div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-title">📂 Upload Invoice <span class="section-badge">AI-POWERED</span></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop your GST invoice here", type=["jpg","png","jpeg"], label_visibility="collapsed")

        if uploaded_file is not None and st.session_state.scanned_data is None:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="step-row"><div class="step-num">2</div><div class="step-label">Run AI extraction on the invoice</div></div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Extract Data with AI", use_container_width=True):
                with st.spinner("Gemini is reading invoice, party details & line items..."):
                    try:
                        img = Image.open(uploaded_file)
                        prompt = """
                        You are an expert Data Extractor for an Indian CA.
                        Extract details from the invoice including Vendor's Full Address and Bank Details (A/c No, IFSC).
                        Return ONLY a valid JSON:
                        {
                          "vendor_name": "...", "gst_number": "...", "vendor_address": "...", "bank_details": "...",
                          "invoice_number": "...", "invoice_date": "DD-MM-YYYY",
                          "base_price": 0.00, "cgst_amount": 0.00, "sgst_amount": 0.00, "igst_amount": 0.00, "total_amount": 0.00, "category": "...",
                          "line_items": [ {"item_name": "...", "hsn_code": "...", "quantity": 0.0, "unit": "...", "rate": 0.0, "amount": 0.0} ]
                        }
                        """
                        ai_resp = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[img, prompt])
                        raw_text = ai_resp.text.strip().replace("```json","").replace("```","").strip()
                        st.session_state.scanned_data = json.loads(raw_text)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {e}")

    with col_preview:
        if uploaded_file is not None:
            st.markdown('<div class="section-title">🖼️ Invoice Preview</div>', unsafe_allow_html=True)
            st.markdown('<div class="preview-frame">', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.scanned_data is not None:
        data = st.session_state.scanned_data
        st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="step-row"><div class="step-num">3</div><div class="step-label">Verify & edit extracted data before saving</div></div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-title">✏️ Verify Extracted Data</div>', unsafe_allow_html=True)

        with st.form("edit_form"):
            st.markdown("**🏢 Vendor Details**")
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1: v_name = st.text_input("Vendor Name",  value=data.get("vendor_name",""))
            with r1c2: v_gst  = st.text_input("GST Number",   value=data.get("gst_number",""))
            with r1c3: v_cat  = st.text_input("Category",     value=data.get("category",""))

            r2c1, r2c2 = st.columns(2)
            with r2c1: v_addr = st.text_input("Vendor Address",         value=data.get("vendor_address",""))
            with r2c2: v_bank = st.text_input("Bank Details (A/c & IFSC)", value=data.get("bank_details",""))

            r3c1, r3c2 = st.columns(2)
            with r3c1: v_inv_no = st.text_input("Invoice Number", value=data.get("invoice_number",""))
            with r3c2: v_date   = st.text_input("Invoice Date",   value=data.get("invoice_date",""))

            st.markdown("<br>**📦 Line Items (Editable Table)**", unsafe_allow_html=True)
            raw_items = data.get("line_items", [])
            if not raw_items:
                raw_items = [{"item_name":"","hsn_code":"","quantity":0.0,"unit":"","rate":0.0,"amount":0.0}]
            edited_df = st.data_editor(pd.DataFrame(raw_items), num_rows="dynamic", use_container_width=True)

            st.markdown("<br>**💰 Tax & Totals**", unsafe_allow_html=True)
            a1, a2, a3, a4, a5 = st.columns(5)
            with a1: v_base  = st.number_input("Base Price ₹", value=float(data.get("base_price",0.0)))
            with a2: v_cgst  = st.number_input("CGST ₹",       value=float(data.get("cgst_amount",0.0)))
            with a3: v_sgst  = st.number_input("SGST ₹",       value=float(data.get("sgst_amount",0.0)))
            with a4: v_igst  = st.number_input("IGST ₹",       value=float(data.get("igst_amount",0.0)))
            with a5: v_total = st.number_input("Total ₹",      value=float(data.get("total_amount",0.0)))

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ Save Full Bill to Cloud", use_container_width=True):
                final_data = {
                    "vendor_name": v_name, "gst_number": v_gst, "vendor_address": v_addr,
                    "bank_details": v_bank, "invoice_date": v_date, "invoice_number": v_inv_no,
                    "base_price": v_base, "cgst_amount": v_cgst, "sgst_amount": v_sgst,
                    "igst_amount": v_igst, "total_gst_amount": v_cgst+v_sgst+v_igst,
                    "total_amount": v_total, "category": v_cat,
                    "line_items": edited_df.to_dict(orient='records')
                }
                supabase.table("invoices").insert(final_data).execute()
                st.session_state.scanned_data = None
                st.success("✅ Bill saved to cloud successfully!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 2 — ANALYTICS & MANAGE
# ══════════════════════════════════════════════
with tab2:
    total_bills   = len(db_data)
    total_expense = sum([float(x.get("total_amount") or 0) for x in db_data])
    total_gst     = sum([float(x.get("total_gst_amount") or 0) for x in db_data])

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        st.markdown(f"""
        <div class="metric-card purple">
          <span class="metric-icon">📄</span>
          <div class="metric-label">Total Bills Scanned</div>
          <div class="metric-value purple">{total_bills}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card green">
          <span class="metric-icon">💰</span>
          <div class="metric-label">Total Expense</div>
          <div class="metric-value green">₹{total_expense:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card amber">
          <span class="metric-icon">📑</span>
          <div class="metric-label">Total GST Paid</div>
          <div class="metric-value amber">₹{total_gst:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if total_bills > 0:
        st.markdown('<div class="section-title">📋 Invoice Records</div>', unsafe_allow_html=True)
        display_df = pd.DataFrame(db_data)

        def get_item_names(row):
            items = row.get('line_items')
            if isinstance(items, list) and len(items) > 0:
                return ", ".join([str(i.get('item_name','')) for i in items if i.get('item_name')])
            elif row.get('product_names'):
                return str(row.get('product_names'))
            return "No Items"

        display_df['Items_Summary'] = display_df.apply(get_item_names, axis=1)
        display_df.insert(0, 'Sr_No', range(1, len(display_df)+1))
        display_df_ui = display_df.drop(columns=['id','line_items','product_names','vendor_address','bank_details'], errors='ignore')
        st.dataframe(display_df_ui, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️ Danger Zone — Delete a Bill"):
            bill_options = {
                f"Sr {idx+1}  |  {row.get('vendor_name','Unknown')}  |  ₹{row.get('total_amount',0)}": row['id']
                for idx, row in enumerate(db_data)
            }
            selected_bill = st.selectbox("Select bill to delete:", options=list(bill_options.keys()))
            if st.button("❌ Delete Selected Bill"):
                supabase.table("invoices").delete().eq("id", bill_options[selected_bill]).execute()
                st.success("Bill deleted.")
                st.rerun()
    else:
        st.info("No bills scanned yet. Upload your first invoice from the Scan tab!")

# ══════════════════════════════════════════════
# TAB 3 — TALLY EXPORT
# ══════════════════════════════════════════════
with tab3:
    def generate_tally_xml(invoices_data):
        xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>All Masters</REPORTNAME>\n</REQUESTDESC>\n<REQUESTDATA>\n"
        parties_data = {}
        unique_items = set()

        for inv in invoices_data:
            p_name = str(inv.get('vendor_name') or 'Unknown').replace("&","&amp;")
            if p_name not in parties_data:
                parties_data[p_name] = {
                    'gst':     str(inv.get('gst_number') or '').replace("&","&amp;"),
                    'address': str(inv.get('vendor_address') or '').replace("&","&amp;"),
                    'bank':    str(inv.get('bank_details') or '').replace("&","&amp;")
                }
            line_items = inv.get('line_items') or []
            if isinstance(line_items, list):
                for itm in line_items:
                    item_name = str(itm.get('item_name','')).replace("&","&amp;")
                    unit = str(itm.get('unit','Nos')).replace("&","&amp;")
                    if item_name: unique_items.add((item_name, unit))

        for party, details in parties_data.items():
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<LEDGER ACTION="Create">\n<NAME>{party}</NAME>\n<PARENT>Sundry Creditors</PARENT>\n'
            if details['gst'] and details['gst'] != "None": xml_data += f'<PARTYGSTIN>{details["gst"]}</PARTYGSTIN>\n'
            if details['address'] and details['address'] != "None": xml_data += f'<ADDRESS.LIST>\n<ADDRESS>{details["address"]}</ADDRESS>\n</ADDRESS.LIST>\n'
            if details['bank'] and details['bank'] != "None": xml_data += f'<NARRATION>Bank Details: {details["bank"]}</NARRATION>\n'
            xml_data += '</LEDGER>\n</TALLYMESSAGE>\n'

        for item, unit in unique_items:
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<STOCKITEM ACTION="Create">\n<NAME>{item}</NAME>\n<PARENT>Primary</PARENT>\n<BASEUNITS>{unit}</BASEUNITS>\n</STOCKITEM>\n</TALLYMESSAGE>\n'

        for inv in invoices_data:
            raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-","")
            v_name   = str(inv.get('vendor_name') or 'Unknown').replace("&","&amp;")
            v_inv_no = str(inv.get('invoice_number') or 'Not Found').replace("&","&amp;")
            total_amt = float(inv.get('total_amount') or 0)

            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<VOUCHER VCHTYPE="Purchase" ACTION="Create">\n<DATE>{raw_date}</DATE>\n<REFERENCE>{v_inv_no}</REFERENCE>\n<VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>\n<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{v_name}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n<AMOUNT>{total_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

            line_items = inv.get('line_items') or []
            if isinstance(line_items, list) and len(line_items) > 0:
                for itm in line_items:
                    i_name = str(itm.get('item_name','')).replace("&","&amp;")
                    i_qty  = float(itm.get('quantity') or 0)
                    i_rate = float(itm.get('rate') or 0)
                    i_amt  = float(itm.get('amount') or 0)
                    i_unit = str(itm.get('unit','Nos')).replace("&","&amp;")
                    xml_data += f'<ALLINVENTORYENTRIES.LIST>\n<STOCKITEMNAME>{i_name}</STOCKITEMNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<BILLEDQTY>{i_qty} {i_unit}</BILLEDQTY>\n<RATE>{i_rate}</RATE>\n<AMOUNT>-{i_amt}</AMOUNT>\n'
                    xml_data += f'<ACCOUNTINGALLOCATIONS.LIST>\n<LEDGERNAME>Purchase A/c</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{i_amt}</AMOUNT>\n</ACCOUNTINGALLOCATIONS.LIST>\n</ALLINVENTORYENTRIES.LIST>\n'
            else:
                xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Purchase A/c</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{float(inv.get("base_price") or 0)}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

            for tax_type, amt in [("CGST", float(inv.get("cgst_amount") or 0)), ("SGST", float(inv.get("sgst_amount") or 0)), ("IGST", float(inv.get("igst_amount") or 0))]:
                if amt > 0:
                    xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Input {tax_type}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

            xml_data += '</VOUCHER>\n</TALLYMESSAGE>\n'

        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    # Export stats row
    ec1, ec2, ec3 = st.columns(3, gap="medium")
    with ec1:
        st.markdown("""
        <div class="metric-card purple center">
          <span class="metric-icon">🏦</span>
          <div class="metric-label">Format</div>
          <div style="color:#A89EFF;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">Tally ERP 9</div>
        </div>""", unsafe_allow_html=True)
    with ec2:
        st.markdown(f"""
        <div class="metric-card green center">
          <span class="metric-icon">📦</span>
          <div class="metric-label">Vouchers Ready</div>
          <div style="color:#6EE7B7;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">{len(db_data)} Bills</div>
        </div>""", unsafe_allow_html=True)
    with ec3:
        st.markdown("""
        <div class="metric-card amber center">
          <span class="metric-icon">⚡</span>
          <div class="metric-label">Voucher Type</div>
          <div style="color:#FCD34D;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">Purchase</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if len(db_data) > 0:
        st.markdown("""
        <div class="export-card">
          <span class="export-icon">📥</span>
          <div class="export-title">Download Tally XML</div>
          <div class="export-desc">All invoices are packaged into a Tally-compatible XML.<br>Import via: Tally ERP 9 → Gateway of Tally → Import Data.</div>
        </div><br>""", unsafe_allow_html=True)

        col_dl, col_empty = st.columns([1, 2])
        with col_dl:
            st.download_button(
                label="📥 Download KhataAI_Import.xml",
                data=generate_tally_xml(db_data),
                file_name="KhataAI_Pro_Import.xml",
                mime="application/xml",
                use_container_width=True
            )
    else:
        st.info("No bills scanned yet. Upload your first invoice from the Scan tab!")
