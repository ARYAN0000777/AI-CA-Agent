import streamlit as st
import json
import pandas as pd
from google import genai
from PIL import Image
from supabase import create_client, Client

# ─────────────────────────────────────────────
# 1. PAGE CONFIG & PREMIUM DARK THEME
# ─────────────────────────────────────────────
st.set_page_config(page_title="KhataAI Pro", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp { background-color: #0A0A0F !important; color: #E8E6F0 !important; font-family: 'DM Sans', sans-serif !important; }

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1280px !important; }

.stApp::before { content: ''; position: fixed; top: -200px; left: -200px; width: 600px; height: 600px; background: radial-gradient(circle, rgba(99,91,255,0.18) 0%, transparent 70%); border-radius: 50%; pointer-events: none; animation: blobFloat 12s ease-in-out infinite alternate; z-index: 0; }
.stApp::after { content: ''; position: fixed; bottom: -150px; right: -150px; width: 500px; height: 500px; background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%); border-radius: 50%; pointer-events: none; animation: blobFloat 15s ease-in-out infinite alternate-reverse; z-index: 0; }

.khata-hero { display: flex; align-items: center; gap: 1.2rem; padding: 2.5rem 0 0.5rem; position: relative; z-index: 1; }
.khata-logo { width: 52px; height: 52px; background: linear-gradient(135deg, #635BFF, #10B981); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; box-shadow: 0 0 32px rgba(99,91,255,0.45); }
.khata-title { font-family: 'Syne', sans-serif !important; font-size: 2.2rem !important; font-weight: 800 !important; background: linear-gradient(135deg, #FFFFFF 30%, #635BFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1 !important; letter-spacing: -0.5px; }
.khata-sub { font-size: 0.9rem; color: #7E7A9A; font-weight: 300; margin-top: 3px; letter-spacing: 0.3px; }
.k-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(99,91,255,0.4), rgba(16,185,129,0.3), transparent); margin: 1.5rem 0 2rem; }

.stTabs [data-baseweb="tab-list"] { gap: 4px !important; background: rgba(255,255,255,0.04) !important; border-radius: 12px !important; padding: 5px !important; border: 1px solid rgba(255,255,255,0.07) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 9px !important; color: #7E7A9A !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; font-size: 0.88rem !important; padding: 8px 20px !important; border: none !important; }
.stTabs [aria-selected="true"] { background: rgba(99,91,255,0.2) !important; color: #A89EFF !important; font-weight: 600 !important; }

.k-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.6rem 1.8rem; position: relative; overflow: hidden; backdrop-filter: blur(12px); }
.metric-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.4rem 1.6rem; position: relative; overflow: hidden; }
.metric-icon { font-size: 1.5rem; margin-bottom: 0.7rem; display: block; }
.metric-label { font-size: 0.75rem; color: #7E7A9A; text-transform: uppercase; font-weight: 500; margin-bottom: 0.3rem; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.75rem; font-weight: 700; color: #FFFFFF; line-height: 1; }

.section-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.section-badge { background: rgba(99,91,255,0.18); color: #A89EFF; font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 20px; }

.stFileUploader > div { background: rgba(99,91,255,0.06) !important; border: 2px dashed rgba(99,91,255,0.3) !important; border-radius: 16px !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #E8E6F0 !important; }

div.stButton > button { background: linear-gradient(135deg, #635BFF, #4F46E5) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 10px 24px !important; font-weight: 600 !important; }
.export-card { background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(99,91,255,0.08)); border: 1px solid rgba(16,185,129,0.2); border-radius: 20px; padding: 2.5rem; text-align: center; }
</style>
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

st.markdown('<div class="khata-hero"><div class="khata-logo">⚡</div><div><div class="khata-title">KhataAI</div><div class="khata-sub">Smart CA Assistant — GST · Tally · Cloud</div></div></div><div class="k-divider"></div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📸  Scan New Bill", "📊  Analytics & Manage", "⚙️  Export to Tally"])

# ══════════════════════════════════════════════
# TAB 1: SCAN & EDIT (WITH ADDRESS & BANK)
# ══════════════════════════════════════════════
with tab1:
    col_upload, col_preview = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<div class="section-title">📂 Upload Invoice</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop your GST invoice here", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

        if uploaded_file is not None and st.session_state.scanned_data is None:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Extract Data with AI", use_container_width=True):
                with st.spinner("AI is reading invoice, party details & line items..."):
                    try:
                        img = Image.open(uploaded_file)
                        # --- AI PROMPT UPDATED FOR ADDRESS & BANK ---
                        prompt = """
                        You are an expert Data Extractor for an Indian CA. 
                        Extract details from the invoice including Vendor's Full Address and Bank Details (A/c No, IFSC).
                        Return ONLY a valid JSON:
                        {
                          "vendor_name": "...", "gst_number": "...", "vendor_address": "...", "bank_details": "...",
                          "invoice_number": "...", "invoice_date": "DD-MM-YYYY",
                          "base_price": 0.00, "cgst_amount": 0.00, "sgst_amount": 0.00, "igst_amount": 0.00, "total_amount": 0.00, "category": "...",
                          "line_items": [
                            {"item_name": "...", "hsn_code": "...", "quantity": 0.0, "unit": "...", "rate": 0.0, "amount": 0.0}
                          ]
                        }
                        """
                        ai_resp = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[img, prompt])
                        raw_text = ai_resp.text.strip().replace("```json", "").replace("```", "").strip()
                        st.session_state.scanned_data = json.loads(raw_text)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {e}")

    with col_preview:
        if uploaded_file is not None:
            st.markdown('<div class="section-title">🖼️ Invoice Preview</div>', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)

    if st.session_state.scanned_data is not None:
        data = st.session_state.scanned_data
        st.markdown("<br><div class='k-card'><div class='section-title'>✏️ Verify Extracted Data</div>", unsafe_allow_html=True)
        
        with st.form("edit_form"):
            st.markdown("**🏢 Basic Details**")
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1: v_name = st.text_input("Vendor Name", value=data.get("vendor_name", ""))
            with r1c2: v_gst = st.text_input("GST Number", value=data.get("gst_number", ""))
            with r1c3: v_cat = st.text_input("Category", value=data.get("category", ""))

            # --- NEW FIELDS IN UI ---
            r2c1, r2c2 = st.columns(2)
            with r2c1: v_addr = st.text_input("Vendor Address", value=data.get("vendor_address", ""))
            with r2c2: v_bank = st.text_input("Bank Details (A/c & IFSC)", value=data.get("bank_details", ""))

            r3c1, r3c2 = st.columns(2)
            with r3c1: v_inv_no = st.text_input("Invoice Number", value=data.get("invoice_number", ""))
            with r3c2: v_date = st.text_input("Invoice Date (DD-MM-YYYY)", value=data.get("invoice_date", ""))

            st.markdown("<br>**📦 Line Items (Editable Table)**", unsafe_allow_html=True)
            raw_items = data.get("line_items", [])
            if not raw_items: raw_items = [{"item_name": "", "hsn_code": "", "quantity": 0.0, "unit": "", "rate": 0.0, "amount": 0.0}]
            df_items = pd.DataFrame(raw_items)
            edited_df = st.data_editor(df_items, num_rows="dynamic", use_container_width=True)

            st.markdown("<br>**💰 Tax & Totals**", unsafe_allow_html=True)
            a1, a2, a3, a4, a5 = st.columns(5)
            with a1: v_base = st.number_input("Base Price ₹", value=float(data.get("base_price", 0.0)))
            with a2: v_cgst = st.number_input("CGST ₹", value=float(data.get("cgst_amount", 0.0)))
            with a3: v_sgst = st.number_input("SGST ₹", value=float(data.get("sgst_amount", 0.0)))
            with a4: v_igst = st.number_input("IGST ₹", value=float(data.get("igst_amount", 0.0)))
            with a5: v_total = st.number_input("Total ₹", value=float(data.get("total_amount", 0.0)))

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ Save Full Bill to Cloud", use_container_width=True):
                final_data = {
                    "vendor_name": v_name, "gst_number": v_gst, "vendor_address": v_addr, "bank_details": v_bank,
                    "invoice_date": v_date, "invoice_number": v_inv_no,
                    "base_price": v_base, "cgst_amount": v_cgst, "sgst_amount": v_sgst, "igst_amount": v_igst,
                    "total_gst_amount": v_cgst + v_sgst + v_igst, "total_amount": v_total, "category": v_cat,
                    "line_items": edited_df.to_dict(orient='records')
                }
                supabase.table("invoices").insert(final_data).execute()
                st.session_state.scanned_data = None
                st.success("✅ Saved successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2: ANALYTICS & SMART TABLE
# ══════════════════════════════════════════════
with tab2:
    total_bills = len(db_data)
    m1, m2, m3 = st.columns(3, gap="medium")
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-value purple">{total_bills}</div><div class="metric-label">Total Bills</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-value green">₹{sum([float(x.get("total_amount") or 0) for x in db_data]):,.0f}</div><div class="metric-label">Total Expense</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="metric-value amber">₹{sum([float(x.get("total_gst_amount") or 0) for x in db_data]):,.0f}</div><div class="metric-label">Total GST</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if total_bills > 0:
        display_df = pd.DataFrame(db_data)
        def get_item_names(row):
            items = row.get('line_items')
            if isinstance(items, list) and len(items) > 0: return ", ".join([str(i.get('item_name', '')) for i in items if i.get('item_name')])
            elif row.get('product_names'): return str(row.get('product_names'))
            return "No Items"
            
        display_df['Items_Summary'] = display_df.apply(get_item_names, axis=1)
        display_df = display_df.drop(columns=['line_items', 'product_names'], errors='ignore')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        with st.expander("🗑️ Danger Zone — Delete a Bill"):
            bill_options = {f"ID {row['id']} | {row.get('vendor_name', 'Unknown')} | ₹{row.get('total_amount', 0)}": row['id'] for row in db_data}
            selected_bill = st.selectbox("Select bill to delete:", options=list(bill_options.keys()))
            if st.button("❌ Delete Selected Bill"):
                supabase.table("invoices").delete().eq("id", bill_options[selected_bill]).execute()
                st.success("Bill deleted.")
                st.rerun()
    else:
        st.info("No bills scanned yet.")

# ══════════════════════════════════════════════
# TAB 3: TALLY EXPORT (MASTER CREATION W/ ADDRESS & BANK)
# ══════════════════════════════════════════════
with tab3:
    def generate_tally_xml(invoices_data):
        xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>All Masters</REPORTNAME>\n</REQUESTDESC>\n<REQUESTDATA>\n"
        
        parties_data = {}
        unique_items = set()

        for inv in invoices_data:
            p_name = str(inv.get('vendor_name') or 'Unknown').replace("&", "&amp;")
            if p_name not in parties_data:
                parties_data[p_name] = {
                    'gst': str(inv.get('gst_number') or '').replace("&", "&amp;"),
                    'address': str(inv.get('vendor_address') or '').replace("&", "&amp;"),
                    'bank': str(inv.get('bank_details') or '').replace("&", "&amp;")
                }
            
            line_items = inv.get('line_items') or []
            if isinstance(line_items, list):
                for itm in line_items:
                    item_name = str(itm.get('item_name', '')).replace("&", "&amp;")
                    unit = str(itm.get('unit', 'Nos')).replace("&", "&amp;")
                    if item_name: unique_items.add((item_name, unit))

        # --- STEP 1: CREATE PARTY LEDGERS (WITH GST, ADDRESS & BANK) ---
        for party, details in parties_data.items():
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<LEDGER ACTION="Create">\n<NAME>{party}</NAME>\n<PARENT>Sundry Creditors</PARENT>\n'
            if details['gst'] and details['gst'] != "None":
                xml_data += f'<PARTYGSTIN>{details["gst"]}</PARTYGSTIN>\n'
            if details['address'] and details['address'] != "None":
                xml_data += f'<ADDRESS.LIST>\n<ADDRESS>{details["address"]}</ADDRESS>\n</ADDRESS.LIST>\n'
            if details['bank'] and details['bank'] != "None":
                xml_data += f'<NARRATION>Bank Details: {details["bank"]}</NARRATION>\n'
            xml_data += '</LEDGER>\n</TALLYMESSAGE>\n'

        # --- STEP 2: CREATE ITEMS ---
        for item, unit in unique_items:
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<STOCKITEM ACTION="Create">\n<NAME>{item}</NAME>\n<PARENT>Primary</PARENT>\n<BASEUNITS>{unit}</BASEUNITS>\n</STOCKITEM>\n</TALLYMESSAGE>\n'

        # --- STEP 3: VOUCHER ENTRY ---
        for inv in invoices_data:
            raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-", "")
            v_name = str(inv.get('vendor_name') or 'Unknown').replace("&", "&amp;")
            v_inv_no = str(inv.get('invoice_number') or 'Not Found').replace("&", "&amp;")
            total_amt = float(inv.get('total_amount') or 0)
            
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<VOUCHER VCHTYPE="Purchase" ACTION="Create">\n<DATE>{raw_date}</DATE>\n<REFERENCE>{v_inv_no}</REFERENCE>\n<VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>\n<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
            
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{v_name}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n<AMOUNT>{total_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
            
            line_items = inv.get('line_items') or []
            if isinstance(line_items, list) and len(line_items) > 0:
                for itm in line_items:
                    i_name = str(itm.get('item_name', '')).replace("&", "&amp;")
                    i_qty = float(itm.get('quantity') or 0)
                    i_rate = float(itm.get('rate') or 0)
                    i_amt = float(itm.get('amount') or 0)
                    i_unit = str(itm.get('unit', 'Nos')).replace("&", "&amp;")
                    
                    xml_data += f'<ALLINVENTORYENTRIES.LIST>\n<STOCKITEMNAME>{i_name}</STOCKITEMNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<BILLEDQTY>{i_qty} {i_unit}</BILLEDQTY>\n<RATE>{i_rate}</RATE>\n<AMOUNT>-{i_amt}</AMOUNT>\n'
                    xml_data += f'<ACCOUNTINGALLOCATIONS.LIST>\n<LEDGERNAME>Purchase A/c</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{i_amt}</AMOUNT>\n</ACCOUNTINGALLOCATIONS.LIST>\n</ALLINVENTORYENTRIES.LIST>\n'
            else:
                base_price = float(inv.get("base_price") or 0)
                xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Purchase A/c</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{base_price}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
            
            for tax_type, amt in [("CGST", float(inv.get("cgst_amount") or 0)), ("SGST", float(inv.get("sgst_amount") or 0)), ("IGST", float(inv.get("igst_amount") or 0))]:
                if amt > 0: xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Input {tax_type}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
                    
            xml_data += '</VOUCHER>\n</TALLYMESSAGE>\n'
        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    if len(db_data) > 0:
        st.markdown('<div class="export-card"><span class="export-icon">📦</span><div class="export-title">Download Master Tally XML</div><div class="export-desc">This file will AUTO-CREATE Party Ledgers (with GST, Address & Bank Details) before posting the entry!</div></div><br>', unsafe_allow_html=True)
        st.download_button("📥 Download Auto-Ledger Tally XML", data=generate_tally_xml(db_data), file_name="KhataAI_Pro_Import.xml", mime="application/xml", use_container_width=True)
    else:
        st.info("No bills scanned yet.")
