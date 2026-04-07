import streamlit as st
import json
import pandas as pd
from google import genai
from google.genai import types
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
  --purple: #7C6FFF; --purple-dim: rgba(124,111,255,0.15); --purple-border: rgba(124,111,255,0.25);
  --green: #00D68F; --green-dim: rgba(0,214,143,0.12);
  --amber: #FFB547; --amber-dim: rgba(255,181,71,0.12);
  --bg: #060608; --surface: rgba(255,255,255,0.03); --border: rgba(255,255,255,0.07);
  --text: #EAE8F5; --muted: #6B6880; --radius: 16px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp { background-color: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container { padding: 0 2.5rem 4rem !important; max-width: 1300px !important; }

.bg-mesh { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bg-mesh span { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.55; }
.bg-mesh span:nth-child(1) { width: 700px; height: 700px; top: -200px; left: -180px; background: radial-gradient(circle, rgba(124,111,255,0.22) 0%, transparent 65%); animation: meshDrift1 18s ease-in-out infinite alternate; }
.bg-mesh span:nth-child(2) { width: 550px; height: 550px; bottom: -150px; right: -100px; background: radial-gradient(circle, rgba(0,214,143,0.15) 0%, transparent 65%); animation: meshDrift2 22s ease-in-out infinite alternate; }
@keyframes meshDrift1 { from { transform: translate(0,0) scale(1); } to { transform: translate(60px,40px) scale(1.12); } }
@keyframes meshDrift2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-40px,-30px) scale(1.08); } }

.khata-topbar { display: flex; align-items: center; justify-content: space-between; padding: 2rem 0 1.2rem; position: relative; z-index: 10; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
.khata-brand { display: flex; align-items: center; gap: 1rem; }
.khata-logo { width: 46px; height: 46px; background: linear-gradient(135deg, #7C6FFF 0%, #00D68F 100%); border-radius: 13px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; }
.khata-title { font-family: 'Syne', sans-serif !important; font-size: 1.75rem !important; font-weight: 800 !important; background: linear-gradient(120deg, #FFFFFF 20%, #7C6FFF 60%, #00D68F 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.khata-sub { font-size: 0.78rem; color: var(--muted); font-weight: 400; margin-top: 3px; }
.khata-pill { background: var(--purple-dim); border: 1px solid var(--purple-border); color: #A89EFF; font-size: 0.72rem; font-weight: 600; padding: 4px 12px; border-radius: 20px; }

.stTabs [data-baseweb="tab-list"] { gap: 6px !important; background: rgba(255,255,255,0.03) !important; border-radius: 14px !important; padding: 5px !important; border: 1px solid var(--border) !important; position: relative; z-index: 5; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 10px !important; color: var(--muted) !important; font-weight: 500 !important; padding: 8px 22px !important; border: none !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(124,111,255,0.2), rgba(0,214,143,0.1)) !important; color: #C4BEFF !important; font-weight: 600 !important; box-shadow: inset 0 0 0 1px rgba(124,111,255,0.3) !important; }

.metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem 1.6rem; position: relative; overflow: hidden; }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.metric-card.purple::before { background: linear-gradient(90deg, #7C6FFF, #A89EFF); }
.metric-card.green::before  { background: linear-gradient(90deg, #00D68F, #6EE7B7); }
.metric-card.amber::before  { background: linear-gradient(90deg, #FFB547, #FCD34D); }
.metric-icon { font-size: 1.6rem; margin-bottom: 0.75rem; display: block; }
.metric-label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; font-weight: 500; margin-bottom: 0.35rem; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 700; color: #FFFFFF; }
.metric-value.purple { color: #A89EFF; } .metric-value.green  { color: #6EE7B7; } .metric-value.amber  { color: #FCD34D; }

.section-title { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.section-badge { background: var(--purple-dim); color: #A89EFF; font-size: 0.68rem; font-weight: 600; padding: 2px 8px; border-radius: 20px; border: 1px solid var(--purple-border); }

.stFileUploader > div, div[data-testid="stAudioInput"] > div { background: rgba(124,111,255,0.04) !important; border: 2px dashed rgba(124,111,255,0.25) !important; border-radius: var(--radius) !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input, .stSelectbox > div > div { background: rgba(255,255,255,0.04) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; color: var(--text) !important; }

div.stButton > button { background: linear-gradient(135deg, #7C6FFF, #5B4FE8) !important; color: white !important; border: none !important; border-radius: 11px !important; padding: 11px 24px !important; font-weight: 600 !important; width: 100%; box-shadow: 0 4px 20px rgba(124,111,255,0.3) !important; }
div.stDownloadButton > button { background: linear-gradient(135deg, #00D68F, #00A86B) !important; color: white !important; width: 100%; border-radius: 11px !important; padding: 13px 28px !important; font-weight: 600 !important; }
div.stButton > button:has(span:contains("Delete")) { background: rgba(239,68,68,0.12) !important; color: #FCA5A5 !important; border: 1px solid rgba(239,68,68,0.25) !important; box-shadow: none !important; }

.export-card { background: linear-gradient(135deg, rgba(0,214,143,0.06), rgba(124,111,255,0.06)); border: 1px solid rgba(0,214,143,0.18); border-radius: 20px; padding: 2.5rem; text-align: center; }
.export-icon { font-size: 3rem; margin-bottom: 1rem; display: block; }
.export-title { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; color: #FFFFFF; }
.export-desc { color: var(--muted); font-size: 0.87rem; margin-top: 0.5rem; }

.fancy-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 2rem 0; }
.stDataFrame, [data-testid="stDataFrame"] { border-radius: 12px !important; border: 1px solid var(--border) !important; }
div[data-testid="stAlert"] { background: rgba(124,111,255,0.08) !important; border: 1px solid var(--purple-border) !important; border-radius: 12px !important; color: var(--text) !important; }
.step-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
.step-num { width: 28px; height: 28px; border-radius: 50%; background: var(--purple-dim); border: 1px solid var(--purple-border); color: #A89EFF; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.step-label { font-size: 0.85rem; font-weight: 500; color: var(--text); }
.preview-frame { border: 1px solid var(--border); border-radius: 14px; overflow: hidden; background: rgba(255,255,255,0.02); }
</style>
<div class="bg-mesh"><span></span><span></span><span></span></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. CLIENT SETUP
# ─────────────────────────────────────────────
AI_API_KEY   = st.secrets["AI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "scanned_data" not in st.session_state: st.session_state.scanned_data = None
if "voice_scanned_data" not in st.session_state: st.session_state.voice_scanned_data = None

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
      <div class="khata-sub">Smart CA Assistant — GST · Voice · Tally</div>
    </div>
  </div>
  <div class="khata-pill">v4.0 ERP PRO</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📸 Scan Invoice", "🎙️ Voice Bill", "📊 Analytics", "⚙️ Tally Export"])

# ══════════════════════════════════════════════
# TAB 1 — SCAN & EDIT
# ══════════════════════════════════════════════
with tab1:
    col_upload, col_preview = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<div class="step-row"><div class="step-num">1</div><div class="step-label">Upload your GST invoice image</div></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop your GST invoice here", type=["jpg","png","jpeg"], label_visibility="collapsed")

        if uploaded_file is not None and st.session_state.scanned_data is None:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Extract Data with AI", use_container_width=True):
                with st.spinner("AI is reading invoice & detecting Voucher Type..."):
                    try:
                        img = Image.open(uploaded_file)
                        prompt = """
                        You are an expert Data Extractor for an Indian CA.
                        Extract details from the invoice including Vendor's Full Address and Bank Details.
                        Determine if this is a "Purchase" invoice (goods bought) or "Sales" invoice (goods sold).
                        Return ONLY a valid JSON:
                        {
                          "voucher_type": "Purchase",  // Or "Sales"
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
            st.markdown('<div class="preview-frame">', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.scanned_data is not None:
        data = st.session_state.scanned_data
        st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">✏️ Verify Extracted Data</div>', unsafe_allow_html=True)

        with st.form("edit_form"):
            st.markdown("**🧾 Voucher Details**")
            # --- NEW VOUCHER TYPE DROPDOWN ---
            v_type_val = data.get("voucher_type", "Purchase")
            v_idx = 1 if "sale" in v_type_val.lower() else 0
            v_type = st.selectbox("Voucher Type (Auto-detected)", ["Purchase", "Sales"], index=v_idx)
            
            st.markdown("**🏢 Party Details**")
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1: v_name = st.text_input("Party Name",  value=data.get("vendor_name",""))
            with r1c2: v_gst  = st.text_input("GST Number",   value=data.get("gst_number",""))
            with r1c3: v_cat  = st.text_input("Category",     value=data.get("category",""))

            r2c1, r2c2 = st.columns(2)
            with r2c1: v_addr = st.text_input("Address", value=data.get("vendor_address",""))
            with r2c2: v_bank = st.text_input("Bank Details", value=data.get("bank_details",""))

            r3c1, r3c2 = st.columns(2)
            with r3c1: v_inv_no = st.text_input("Invoice Number", value=data.get("invoice_number",""))
            with r3c2: v_date   = st.text_input("Invoice Date",   value=data.get("invoice_date",""))

            st.markdown("<br>**📦 Line Items (Editable Table)**", unsafe_allow_html=True)
            raw_items = data.get("line_items", [])
            if not raw_items: raw_items = [{"item_name":"","hsn_code":"","quantity":0.0,"unit":"","rate":0.0,"amount":0.0}]
            edited_df = st.data_editor(pd.DataFrame(raw_items), num_rows="dynamic", use_container_width=True)

            st.markdown("<br>**💰 Tax & Totals**", unsafe_allow_html=True)
            a1, a2, a3, a4, a5 = st.columns(5)
            with a1: v_base  = st.number_input("Base Price ₹", value=float(data.get("base_price",0.0)))
            with a2: v_cgst  = st.number_input("CGST ₹",       value=float(data.get("cgst_amount",0.0)))
            with a3: v_sgst  = st.number_input("SGST ₹",       value=float(data.get("sgst_amount",0.0)))
            with a4: v_igst  = st.number_input("IGST ₹",       value=float(data.get("igst_amount",0.0)))
            with a5: v_total = st.number_input("Total ₹",      value=float(data.get("total_amount",0.0)))

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ Save Bill to Cloud", use_container_width=True):
                final_data = {
                    "voucher_type": v_type, "vendor_name": v_name, "gst_number": v_gst, "vendor_address": v_addr,
                    "bank_details": v_bank, "invoice_date": v_date, "invoice_number": v_inv_no,
                    "base_price": v_base, "cgst_amount": v_cgst, "sgst_amount": v_sgst,
                    "igst_amount": v_igst, "total_gst_amount": v_cgst+v_sgst+v_igst,
                    "total_amount": v_total, "category": v_cat,
                    "line_items": edited_df.to_dict(orient='records')
                }
                supabase.table("invoices").insert(final_data).execute()
                st.session_state.scanned_data = None
                st.success(f"✅ {v_type} Bill saved successfully!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 2: 🎙️ VOICE BILLING (SALES & PURCHASE)
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🎙️ AI Voice Billing</div>', unsafe_allow_html=True)
    st.info("💡 Bole: *'Manoj Enterprises ko 10 pipe beche 50 ke rate par'* (Sales) YA *'Sharma se 5 box kharide'* (Purchase)")
    
    audio_value = st.audio_input("Record Sales/Purchase Bill", label_visibility="collapsed")
    
    if audio_value is not None and st.session_state.voice_scanned_data is None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Generate Bill from Voice", use_container_width=True):
            with st.spinner("AI is determining if it's Sales or Purchase..."):
                try:
                    audio_prompt = """
                    Listen to this audio. You are an expert Accountant.
                    Determine if the user is BUYING (Purchase) or SELLING (Sales).
                    Extract the party name, items, quantities and rates.
                    Return ONLY a valid JSON:
                    {
                      "voucher_type": "Purchase", // Or "Sales"
                      "vendor_name": "...", "base_price": 0.0, "total_amount": 0.0,
                      "line_items": [{"item_name": "...", "quantity": 0.0, "unit": "Nos", "rate": 0.0, "amount": 0.0}]
                    }
                    """
                    resp = ai_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[types.Part.from_bytes(data=audio_value.getvalue(), mime_type='audio/wav'), audio_prompt]
                    )
                    clean_json = resp.text.strip().replace("```json","").replace("```","").strip()
                    st.session_state.voice_scanned_data = json.loads(clean_json)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Voice understanding failed: {e}")

    if st.session_state.voice_scanned_data is not None:
        v_data = st.session_state.voice_scanned_data
        st.markdown('<div class="fancy-divider"></div><div class="section-title">✏️ Verify Voice Bill</div>', unsafe_allow_html=True)
        
        with st.form("edit_voice_form"):
            c0, c1, c2 = st.columns([1, 2, 1])
            with c0: 
                v_type_val = v_data.get("voucher_type", "Sales")
                v_idx = 1 if "sale" in v_type_val.lower() else 0
                voice_type = st.selectbox("Type", ["Purchase", "Sales"], index=v_idx)
            with c1: voice_vendor = st.text_input("Party Name", value=v_data.get("vendor_name", "Local Party"))
            with c2: voice_date = st.text_input("Date", value="2026-04-08")
            
            st.markdown("**📦 Items Mentioned in Audio**")
            voice_edited_df = st.data_editor(pd.DataFrame(v_data.get("line_items", [])), num_rows="dynamic", use_container_width=True)
            voice_total = st.number_input("Total Amount ₹", value=float(v_data.get("total_amount", 0.0)))
            
            if st.form_submit_button("✅ Save Voice Bill", use_container_width=True):
                voice_final_data = {
                    "voucher_type": voice_type, "vendor_name": voice_vendor, "invoice_date": voice_date,
                    "total_amount": voice_total, "category": "Voice Entry",
                    "line_items": voice_edited_df.to_dict(orient='records')
                }
                supabase.table("invoices").insert(voice_final_data).execute()
                st.session_state.voice_scanned_data = None
                st.success("✅ Voice Bill Saved successfully!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 3 — ANALYTICS & MANAGE (NOW SHOWS SALES VS PURCHASE)
# ══════════════════════════════════════════════
with tab3:
    total_bills = len(db_data)
    total_sales = sum([float(x.get("total_amount") or 0) for x in db_data if x.get("voucher_type") == "Sales"])
    total_purch = sum([float(x.get("total_amount") or 0) for x in db_data if x.get("voucher_type", "Purchase") == "Purchase"])

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1: st.markdown(f'<div class="metric-card purple"><span class="metric-icon">📄</span><div class="metric-label">Total Bills</div><div class="metric-value purple">{total_bills}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card green"><span class="metric-icon">📈</span><div class="metric-label">Total Sales</div><div class="metric-value green">₹{total_sales:,.0f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card amber"><span class="metric-icon">📉</span><div class="metric-label">Total Purchase</div><div class="metric-value amber">₹{total_purch:,.0f}</div></div>', unsafe_allow_html=True)

    if total_bills > 0:
        st.markdown('<br><div class="section-title">📋 Voucher Records</div>', unsafe_allow_html=True)
        display_df = pd.DataFrame(db_data)
        def get_item_names(row):
            items = row.get('line_items')
            if isinstance(items, list) and len(items) > 0: return ", ".join([str(i.get('item_name','')) for i in items if i.get('item_name')])
            elif row.get('product_names'): return str(row.get('product_names'))
            return "No Items"
        display_df['Items_Summary'] = display_df.apply(get_item_names, axis=1)
        display_df.insert(0, 'Sr_No', range(1, len(display_df)+1))
        
        # Bring voucher type to front
        if 'voucher_type' not in display_df.columns: display_df['voucher_type'] = 'Purchase'
        cols = ['Sr_No', 'voucher_type'] + [c for c in display_df.columns if c not in ['Sr_No', 'voucher_type', 'id', 'line_items', 'product_names', 'vendor_address', 'bank_details']]
        
        st.dataframe(display_df[cols], use_container_width=True, hide_index=True)

        with st.expander("🗑️ Danger Zone — Delete a Bill"):
            bill_options = {f"Sr {idx+1} | {row.get('voucher_type','Purchase')} | {row.get('vendor_name','Unknown')}": row['id'] for idx, row in enumerate(db_data)}
            selected_bill = st.selectbox("Select bill to delete:", options=list(bill_options.keys()))
            if st.button("❌ Delete Selected Bill"):
                supabase.table("invoices").delete().eq("id", bill_options[selected_bill]).execute()
                st.rerun()

# ══════════════════════════════════════════════
# TAB 4 — TALLY EXPORT (SALES & PURCHASE DEBIT/CREDIT LOGIC)
# ══════════════════════════════════════════════
with tab4:
    def generate_tally_xml(invoices_data):
        xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>All Masters</REPORTNAME>\n</REQUESTDESC>\n<REQUESTDATA>\n"
        parties_data = {}
        unique_items = set()

        for inv in invoices_data:
            p_name = str(inv.get('vendor_name') or 'Unknown').replace("&","&amp;")
            if p_name not in parties_data:
                parties_data[p_name] = {
                    'group': 'Sundry Debtors' if inv.get('voucher_type') == 'Sales' else 'Sundry Creditors',
                    'gst': str(inv.get('gst_number') or '').replace("&","&amp;"),
                    'address': str(inv.get('vendor_address') or '').replace("&","&amp;")
                }
            line_items = inv.get('line_items') or []
            if isinstance(line_items, list):
                for itm in line_items:
                    item_name = str(itm.get('item_name','')).replace("&","&amp;")
                    if item_name: unique_items.add((item_name, str(itm.get('unit','Nos')).replace("&","&amp;")))

        for party, details in parties_data.items():
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<LEDGER ACTION="Create">\n<NAME>{party}</NAME>\n<PARENT>{details["group"]}</PARENT>\n'
            if details['gst'] and details['gst'] != "None": xml_data += f'<PARTYGSTIN>{details["gst"]}</PARTYGSTIN>\n'
            if details['address'] and details['address'] != "None": xml_data += f'<ADDRESS.LIST>\n<ADDRESS>{details["address"]}</ADDRESS>\n</ADDRESS.LIST>\n'
            xml_data += '</LEDGER>\n</TALLYMESSAGE>\n'

        for item, unit in unique_items:
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<STOCKITEM ACTION="Create">\n<NAME>{item}</NAME>\n<PARENT>Primary</PARENT>\n<BASEUNITS>{unit}</BASEUNITS>\n</STOCKITEM>\n</TALLYMESSAGE>\n'

        for inv in invoices_data:
            raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-","")
            v_name = str(inv.get('vendor_name') or 'Unknown').replace("&","&amp;")
            v_inv_no = str(inv.get('invoice_number') or 'Not Found').replace("&","&amp;")
            v_type = inv.get('voucher_type') or 'Purchase'
            
            # --- THE CORE TALLY DEBIT/CREDIT LOGIC ---
            total_amt = float(inv.get('total_amount') or 0)
            party_is_debit = "Yes" if v_type == "Sales" else "No"
            party_amt = f"-{total_amt}" if v_type == "Sales" else f"{total_amt}"
            
            main_ledger = "Sales A/c" if v_type == "Sales" else "Purchase A/c"
            main_is_debit = "No" if v_type == "Sales" else "Yes"

            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<VOUCHER VCHTYPE="{v_type}" ACTION="Create">\n<DATE>{raw_date}</DATE>\n<REFERENCE>{v_inv_no}</REFERENCE>\n<VOUCHERTYPENAME>{v_type}</VOUCHERTYPENAME>\n<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
            
            # Party Ledger Entry
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{v_name}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>{party_is_debit}</ISDEEMEDPOSITIVE>\n<AMOUNT>{party_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

            # Items Entry
            line_items = inv.get('line_items') or []
            if isinstance(line_items, list) and len(line_items) > 0:
                for itm in line_items:
                    i_name = str(itm.get('item_name','')).replace("&","&amp;")
                    i_amt = float(itm.get('amount') or 0)
                    alloc_amt = f"{i_amt}" if v_type == "Sales" else f"-{i_amt}"
                    
                    xml_data += f'<ALLINVENTORYENTRIES.LIST>\n<STOCKITEMNAME>{i_name}</STOCKITEMNAME>\n<ISDEEMEDPOSITIVE>{main_is_debit}</ISDEEMEDPOSITIVE>\n<BILLEDQTY>{float(itm.get("quantity") or 0)} {str(itm.get("unit","Nos"))}</BILLEDQTY>\n<RATE>{float(itm.get("rate") or 0)}</RATE>\n<AMOUNT>{alloc_amt}</AMOUNT>\n'
                    xml_data += f'<ACCOUNTINGALLOCATIONS.LIST>\n<LEDGERNAME>{main_ledger}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>{main_is_debit}</ISDEEMEDPOSITIVE>\n<AMOUNT>{alloc_amt}</AMOUNT>\n</ACCOUNTINGALLOCATIONS.LIST>\n</ALLINVENTORYENTRIES.LIST>\n'
            else:
                base_amt = float(inv.get("base_price") or 0)
                a_amt = f"{base_amt}" if v_type == "Sales" else f"-{base_amt}"
                xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{main_ledger}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>{main_is_debit}</ISDEEMEDPOSITIVE>\n<AMOUNT>{a_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

            # Taxes
            for tax_type, amt in [("CGST", float(inv.get("cgst_amount") or 0)), ("SGST", float(inv.get("sgst_amount") or 0)), ("IGST", float(inv.get("igst_amount") or 0))]:
                if amt > 0:
                    t_amt = f"{amt}" if v_type == "Sales" else f"-{amt}"
                    tax_ledger = f"Output {tax_type}" if v_type == "Sales" else f"Input {tax_type}"
                    xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{tax_ledger}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>{main_is_debit}</ISDEEMEDPOSITIVE>\n<AMOUNT>{t_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

            xml_data += '</VOUCHER>\n</TALLYMESSAGE>\n'

        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    ec1, ec2, ec3 = st.columns(3, gap="medium")
    with ec1: st.markdown("""<div class="metric-card purple center"><span class="metric-icon">🏦</span><div class="metric-label">Format</div><div style="color:#A89EFF;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">Tally ERP 9</div></div>""", unsafe_allow_html=True)
    with ec2: st.markdown(f"""<div class="metric-card green center"><span class="metric-icon">📦</span><div class="metric-label">Vouchers Ready</div><div style="color:#6EE7B7;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">{len(db_data)} Bills</div></div>""", unsafe_allow_html=True)
    with ec3: st.markdown("""<div class="metric-card amber center"><span class="metric-icon">⚡</span><div class="metric-label">Status</div><div style="color:#FCD34D;font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;">Multi-Voucher</div></div>""", unsafe_allow_html=True)

    if len(db_data) > 0:
        st.markdown("""<br><div class="export-card"><span class="export-icon">📥</span><div class="export-title">Download Master Tally XML</div><div class="export-desc">Auto-creates Sundry Debtors for Sales & Creditors for Purchases!</div></div><br>""", unsafe_allow_html=True)
        st.download_button(label="📥 Download KhataAI_ERP_Import.xml", data=generate_tally_xml(db_data), file_name="KhataAI_ERP_Import.xml", mime="application/xml", use_container_width=True)
