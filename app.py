import streamlit as st
import json
from google import genai
from PIL import Image
from supabase import create_client, Client

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="KhataAI", page_icon="⚡", layout="wide")

# ─────────────────────────────────────────────
# GLOBAL CSS — Premium Dark Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, .stApp {
    background-color: #0A0A0F !important;
    color: #E8E6F0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1280px !important; }

/* ── Animated gradient background blob ── */
.stApp::before {
    content: '';
    position: fixed;
    top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(99,91,255,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    animation: blobFloat 12s ease-in-out infinite alternate;
    z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    bottom: -150px; right: -150px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    animation: blobFloat 15s ease-in-out infinite alternate-reverse;
    z-index: 0;
}
@keyframes blobFloat {
    from { transform: translate(0, 0) scale(1); }
    to   { transform: translate(40px, 30px) scale(1.08); }
}

/* ── Hero Header ── */
.khata-hero {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    padding: 2.5rem 0 0.5rem;
    position: relative;
    z-index: 1;
}
.khata-logo {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #635BFF, #10B981);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
    box-shadow: 0 0 32px rgba(99,91,255,0.45);
}
.khata-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #FFFFFF 30%, #635BFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1 !important;
    letter-spacing: -0.5px;
}
.khata-sub {
    font-size: 0.9rem;
    color: #7E7A9A;
    font-weight: 300;
    margin-top: 3px;
    letter-spacing: 0.3px;
}

/* ── Divider ── */
.k-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,91,255,0.4), rgba(16,185,129,0.3), transparent);
    margin: 1.5rem 0 2rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    padding: 5px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: #7E7A9A !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 8px 20px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,91,255,0.2) !important;
    color: #A89EFF !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0 0 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Cards ── */
.k-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.k-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,91,255,0.5), transparent);
}

/* ── Metric Cards ── */
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    border-color: rgba(99,91,255,0.35);
    box-shadow: 0 0 24px rgba(99,91,255,0.12);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.purple::before { background: linear-gradient(90deg, #635BFF, #A89EFF); }
.metric-card.green::before  { background: linear-gradient(90deg, #10B981, #6EE7B7); }
.metric-card.amber::before  { background: linear-gradient(90deg, #F59E0B, #FCD34D); }

.metric-icon {
    font-size: 1.5rem;
    margin-bottom: 0.7rem;
    display: block;
}
.metric-label {
    font-size: 0.75rem;
    color: #7E7A9A;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 500;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
}
.metric-value.purple { color: #A89EFF; }
.metric-value.green  { color: #6EE7B7; }
.metric-value.amber  { color: #FCD34D; }

/* ── Section titles ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-badge {
    background: rgba(99,91,255,0.18);
    color: #A89EFF;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}

/* ── Upload zone ── */
.stFileUploader > div {
    background: rgba(99,91,255,0.06) !important;
    border: 2px dashed rgba(99,91,255,0.3) !important;
    border-radius: 16px !important;
    transition: all 0.25s ease !important;
}
.stFileUploader > div:hover {
    border-color: rgba(99,91,255,0.6) !important;
    background: rgba(99,91,255,0.1) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E8E6F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: rgba(99,91,255,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,91,255,0.12) !important;
    outline: none !important;
}
label[data-testid="stWidgetLabel"] p {
    color: #9E9AB8 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 4px !important;
}

/* ── Buttons ── */
div.stButton > button {
    background: linear-gradient(135deg, #635BFF, #4F46E5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(99,91,255,0.3) !important;
    letter-spacing: 0.2px !important;
}
div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,91,255,0.45) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }

/* Delete button — red accent */
div.stButton > button[kind="secondary"],
div.stButton > button:has(span:contains("Delete")) {
    background: rgba(239,68,68,0.12) !important;
    color: #FCA5A5 !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    box-shadow: none !important;
}
div.stButton > button[kind="secondary"]:hover {
    background: rgba(239,68,68,0.2) !important;
    box-shadow: 0 4px 15px rgba(239,68,68,0.2) !important;
}

/* ── Download button ── */
div.stDownloadButton > button {
    background: linear-gradient(135deg, #10B981, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.35) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.2px !important;
}
div.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(16,185,129,0.5) !important;
}

/* ── Alerts & Info ── */
div[data-testid="stAlert"] {
    background: rgba(99,91,255,0.1) !important;
    border: 1px solid rgba(99,91,255,0.25) !important;
    border-radius: 12px !important;
    color: #C4BFFF !important;
}
div[data-testid="stSuccess"] {
    background: rgba(16,185,129,0.1) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 12px !important;
    color: #6EE7B7 !important;
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: rgba(239,68,68,0.05) !important;
    border: 1px solid rgba(239,68,68,0.15) !important;
    border-radius: 14px !important;
}
div[data-testid="stExpander"] summary {
    color: #FCA5A5 !important;
    font-weight: 600 !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stDataFrame iframe { background: transparent !important; }

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E8E6F0 !important;
}

/* ── Spinner ── */
div[data-testid="stSpinner"] { color: #A89EFF !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,91,255,0.3); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,91,255,0.5); }

/* ── Tag pill ── */
.k-tag {
    display: inline-block;
    background: rgba(99,91,255,0.15);
    border: 1px solid rgba(99,91,255,0.3);
    color: #A89EFF;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* Export card ── */
.export-card {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(99,91,255,0.08));
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
}
.export-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
    filter: drop-shadow(0 0 16px rgba(16,185,129,0.5));
}
.export-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.5rem;
}
.export-desc {
    color: #7E7A9A;
    font-size: 0.88rem;
    margin-bottom: 1.5rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CLIENTS
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
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="khata-hero">
    <div class="khata-logo">⚡</div>
    <div>
        <div class="khata-title">KhataAI</div>
        <div class="khata-sub">Smart CA Assistant — GST · Tally · Cloud</div>
    </div>
</div>
<div class="k-divider"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📸  Scan New Bill", "📊  Analytics & Manage", "⚙️  Export to Tally"])

# ══════════════════════════════════════════════
# TAB 1 — SCAN
# ══════════════════════════════════════════════
with tab1:
    col_upload, col_preview = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<div class="section-title">📂 Upload Invoice <span class="section-badge">AI-Powered</span></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop your GST invoice here",
            type=["jpg", "png", "jpeg"],
            label_visibility="collapsed"
        )

        if uploaded_file is not None and st.session_state.scanned_data is None:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Extract Data with AI", use_container_width=True):
                with st.spinner("Gemini AI is reading your invoice..."):
                    try:
                        img = Image.open(uploaded_file)
                        prompt = '''You are an expert Data Extractor for an Indian CA. Extract details from invoice. For 'product_names', list items separated by commas. Return ONLY a valid JSON: {"vendor_name": "...", "gst_number": "...", "invoice_number": "...", "invoice_date": "DD-MM-YYYY", "product_names": "...", "base_price": 0.00, "cgst_amount": 0.00, "sgst_amount": 0.00, "igst_amount": 0.00, "total_amount": 0.00, "category": "..."}'''
                        ai_resp = ai_client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[img, prompt]
                        )
                        raw_text = ai_resp.text.strip().replace("```json", "").replace("```", "").strip()
                        st.session_state.scanned_data = json.loads(raw_text)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {e}")

    with col_preview:
        if uploaded_file is not None:
            st.markdown('<div class="section-title">🖼️ Invoice Preview</div>', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)

    # ── Extracted data form ──
    if st.session_state.scanned_data is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="k-card">
            <div class="section-title">✏️ Verify Extracted Data <span class="section-badge">Review & Edit</span></div>
        """, unsafe_allow_html=True)
        st.info("💡 AI has filled the fields below. Please verify before saving.")
        st.markdown("</div>", unsafe_allow_html=True)

        data = st.session_state.scanned_data
        with st.form("edit_form"):
            st.markdown("**🏢 Vendor Information**")
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                v_name   = st.text_input("Vendor Name", value=data.get("vendor_name", ""))
            with r1c2:
                v_gst    = st.text_input("GST Number", value=data.get("gst_number", ""))
            with r1c3:
                v_cat    = st.text_input("Category", value=data.get("category", ""))

            r2c1, r2c2 = st.columns(2)
            with r2c1:
                v_inv_no = st.text_input("Invoice Number", value=data.get("invoice_number", ""))
            with r2c2:
                v_date   = st.text_input("Invoice Date (DD-MM-YYYY)", value=data.get("invoice_date", ""))

            st.markdown("<br>**📦 Items & Amounts**", unsafe_allow_html=True)
            v_prods = st.text_area("Product Names (comma-separated)", value=data.get("product_names", ""), height=80)

            a1, a2, a3, a4, a5 = st.columns(5)
            with a1: v_base  = st.number_input("Base Price ₹", value=float(data.get("base_price", 0.0)), format="%.2f")
            with a2: v_cgst  = st.number_input("CGST ₹",       value=float(data.get("cgst_amount", 0.0)), format="%.2f")
            with a3: v_sgst  = st.number_input("SGST ₹",       value=float(data.get("sgst_amount", 0.0)), format="%.2f")
            with a4: v_igst  = st.number_input("IGST ₹",       value=float(data.get("igst_amount", 0.0)), format="%.2f")
            with a5: v_total = st.number_input("Total ₹",      value=float(data.get("total_amount", 0.0)), format="%.2f")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✅  Save to Cloud Database", use_container_width=True)
            if submitted:
                final_data = {
                    "vendor_name": v_name, "gst_number": v_gst,
                    "invoice_date": v_date, "invoice_number": v_inv_no,
                    "product_names": v_prods, "base_price": v_base,
                    "cgst_amount": v_cgst, "sgst_amount": v_sgst,
                    "igst_amount": v_igst,
                    "total_gst_amount": v_cgst + v_sgst + v_igst,
                    "total_amount": v_total, "category": v_cat,
                }
                supabase.table("invoices").insert(final_data).execute()
                st.session_state.scanned_data = None
                st.success("✅ Invoice saved to Supabase successfully!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ══════════════════════════════════════════════
with tab2:
    total_bills   = len(db_data)
    total_expense = sum([float(x.get('total_amount') or 0) for x in db_data])
    total_gst     = sum([float(x.get('total_gst_amount') or 0) for x in db_data])

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        st.markdown(f"""
        <div class="metric-card purple">
            <span class="metric-icon">🧾</span>
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
        st.dataframe(db_data, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️  Danger Zone — Delete a Bill"):
            st.markdown("⚠️ This action is permanent and cannot be undone.")
            bill_options = {
                f"ID {row['id']}  |  {row.get('vendor_name', 'Unknown')}  |  ₹{row.get('total_amount', 0)}": row['id']
                for row in db_data
            }
            selected_bill = st.selectbox("Select bill to delete:", options=list(bill_options.keys()))
            if st.button("❌  Delete Selected Bill"):
                supabase.table("invoices").delete().eq("id", bill_options[selected_bill]).execute()
                st.success("Bill deleted.")
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; padding: 4rem 2rem; color: #7E7A9A;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; color:#E8E6F0; margin-bottom:0.5rem;">No invoices yet</div>
            <div style="font-size:0.88rem;">Scan your first bill from the Scan tab to get started.</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — TALLY EXPORT
# ══════════════════════════════════════════════
with tab3:

    def generate_tally_xml(invoices_data):
        xml_data = (
            "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n"
            "<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>Vouchers</REPORTNAME>\n</REQUESTDESC>\n"
            "<REQUESTDATA>\n"
        )
        for inv in invoices_data:
            raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-", "")
            v_name   = str(inv.get('vendor_name') or 'Unknown').replace("&", "&amp;")
            v_inv_no = str(inv.get('invoice_number') or 'Not Found').replace("&", "&amp;")
            v_prods  = str(inv.get('product_names') or 'Various Items').replace("&", "&amp;")

            xml_data += (
                f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n'
                f'<VOUCHER VCHTYPE="Purchase" ACTION="Create">\n'
                f'<DATE>{raw_date}</DATE>\n'
                f'<REFERENCE>{v_inv_no}</REFERENCE>\n'
                f'<VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>\n'
                f'<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
                f'<NARRATION>Bill No: {v_inv_no} | Items: {v_prods}</NARRATION>\n'
            )
            xml_data += (
                f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{v_name}</LEDGERNAME>\n'
                f'<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n'
                f'<AMOUNT>{float(inv.get("total_amount") or 0)}</AMOUNT>\n'
                f'</ALLLEDGERENTRIES.LIST>\n'
            )
            xml_data += (
                f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Purchase A/c</LEDGERNAME>\n'
                f'<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n'
                f'<AMOUNT>-{float(inv.get("base_price") or 0)}</AMOUNT>\n'
                f'</ALLLEDGERENTRIES.LIST>\n'
            )
            for tax_type, amt in [
                ("CGST", float(inv.get("cgst_amount") or 0)),
                ("SGST", float(inv.get("sgst_amount") or 0)),
                ("IGST", float(inv.get("igst_amount") or 0)),
            ]:
                if amt > 0:
                    xml_data += (
                        f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Input {tax_type}</LEDGERNAME>\n'
                        f'<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n'
                        f'<AMOUNT>-{amt}</AMOUNT>\n'
                        f'</ALLLEDGERENTRIES.LIST>\n'
                    )
            xml_data += '</VOUCHER>\n</TALLYMESSAGE>\n'

        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    # ── Info strip ──
    ec1, ec2, ec3 = st.columns(3, gap="medium")
    with ec1:
        st.markdown("""
        <div class="metric-card purple" style="text-align:center">
            <span class="metric-icon">🏦</span>
            <div class="metric-label">Format</div>
            <div style="color:#A89EFF;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">Tally ERP 9</div>
        </div>""", unsafe_allow_html=True)
    with ec2:
        st.markdown(f"""
        <div class="metric-card green" style="text-align:center">
            <span class="metric-icon">📦</span>
            <div class="metric-label">Vouchers Ready</div>
            <div style="color:#6EE7B7;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">{len(db_data)} Bills</div>
        </div>""", unsafe_allow_html=True)
    with ec3:
        st.markdown("""
        <div class="metric-card amber" style="text-align:center">
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
            <div class="export-desc">
                All invoices are packaged into a Tally-compatible XML.<br>
                Simply import this file into Tally ERP 9 → Gateway of Tally → Import Data.
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_dl, col_empty = st.columns([1, 2])
        with col_dl:
            st.download_button(
                label="📥  Download KhataAI_Import.xml",
                data=generate_tally_xml(db_data),
                file_name="KhataAI_Pro_Import.xml",
                mime="application/xml",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 XML Preview</div>', unsafe_allow_html=True)
        with st.expander("👁️ Show raw XML (first 3000 chars)"):
            preview = generate_tally_xml(db_data)[:3000]
            st.code(preview, language="xml")
    else:
        st.markdown("""
        <div style="text-align:center; padding: 4rem 2rem; color: #7E7A9A;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; color:#E8E6F0; margin-bottom:0.5rem;">Nothing to export yet</div>
            <div style="font-size:0.88rem;">Scan and save some invoices first, then come back here.</div>
        </div>""", unsafe_allow_html=True)

    # ── Feature footnotes ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="border-top:1px solid rgba(255,255,255,0.06); padding-top:1rem; display:flex; gap:2rem; flex-wrap:wrap;">
        <div style="color:#4B4868; font-size:0.75rem;">✅ &amp; symbol safe (XML escaped)</div>
        <div style="color:#4B4868; font-size:0.75rem;">✅ Inventory crash fix applied</div>
        <div style="color:#4B4868; font-size:0.75rem;">✅ Auto CGST / SGST / IGST split</div>
        <div style="color:#4B4868; font-size:0.75rem;">✅ Tally ERP 9 &amp; Prime compatible</div>
    </div>
    """, unsafe_allow_html=True)
