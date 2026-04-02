import streamlit as st
import json
from google import genai
from PIL import Image
from supabase import create_client, Client

# --- 1. UI CONFIGURATION ---
st.set_page_config(page_title="KhataAI Automation", page_icon="⚡", layout="wide")

# Streamlit ki branding (menu/footer) chhupana
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            div.stButton > button:first-child {
                background-color: #4F46E5;
                color: white;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. SETUP KEYS ---
AI_API_KEY = st.secrets["AI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 3. SESSION STATE ---
if "scanned_data" not in st.session_state:
    st.session_state.scanned_data = None

# --- 4. FETCH DATABASE DATA FIRST ---
try:
    response = supabase.table("invoices").select("*").order("id", desc=True).execute()
    db_data = response.data
except Exception:
    db_data = []

# --- 5. APP HEADER ---
st.title("⚡ KhataAI - Smart CA Assistant")
st.markdown("Automate your bill entries to Tally instantly. Powered by AI.")
st.write("---")

# --- 6. PRO UI TABS ---
tab1, tab2, tab3 = st.tabs(["📸 Scan New Bill", "📊 Analytics Dashboard", "⚙️ Export to Tally"])

# ==========================================
# TAB 1: SCAN & EDIT SCREEN
# ==========================================
with tab1:
    st.subheader("Upload Bill Image")
    uploaded_file = st.file_uploader("Drag & drop invoice here", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if uploaded_file is not None and st.session_state.scanned_data is None:
        if st.button("🚀 Extract Data with AI"):
            with st.spinner("AI is analyzing the invoice..."):
                try:
                    img = Image.open(uploaded_file)
                    prompt = """
                    You are an expert Data Extractor for an Indian CA. 
                    Read this invoice image and extract details. If value is missing, output 0.00 or 'Not Found'.
                    Return ONLY a valid JSON.
                    {
                      "vendor_name": "...",
                      "gst_number": "...",
                      "invoice_date": "DD-MM-YYYY",
                      "base_price": 0.00,
                      "cgst_amount": 0.00,
                      "sgst_amount": 0.00,
                      "igst_amount": 0.00,
                      "total_gst_amount": 0.00,
                      "tds_amount": 0.00,
                      "total_amount": 0.00,
                      "category": "..."
                    }
                    """
                    response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[img, prompt])
                    
                    # --- BULLETPROOF AI CLEANER ---
                    raw_text = response.text.strip()
                    raw_text = raw_text.replace("```json", "")
                    raw_text = raw_text.replace("```", "")
                    raw_text = raw_text.strip() 
                    
                    st.session_state.scanned_data = json.loads(raw_text)
                    st.rerun() 
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # REVIEW FORM
    if st.session_state.scanned_data is not None:
        st.info("💡 Please verify the extracted data below and save.")
        data = st.session_state.scanned_data
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2) 
            with col1:
                v_name = st.text_input("Vendor Name", value=data.get("vendor_name", ""))
                v_gst = st.text_input("GST Number", value=data.get("gst_number", ""))
                v_date = st.text_input("Invoice Date", value=data.get("invoice_date", ""))
                v_cat = st.text_input("Category", value=data.get("category", ""))
            with col2:
                v_base = st.number_input("Base Price (₹)", value=float(data.get("base_price", 0.0)))
                v_cgst = st.number_input("CGST (₹)", value=float(data.get("cgst_amount", 0.0)))
                v_sgst = st.number_input("SGST (₹)", value=float(data.get("sgst_amount", 0.0)))
                v_igst = st.number_input("IGST (₹)", value=float(data.get("igst_amount", 0.0)))
                v_total = st.number_input("Total Amount (₹)", value=float(data.get("total_amount", 0.0)))

            if st.form_submit_button("✅ Save to Cloud Database"):
                final_data = {
                    "vendor_name": v_name, "gst_number": v_gst, "invoice_date": v_date,
                    "base_price": v_base, "cgst_amount": v_cgst, "sgst_amount": v_sgst,
                    "igst_amount": v_igst, "total_gst_amount": v_cgst + v_sgst + v_igst,
                    "tds_amount": float(data.get("tds_amount", 0.0)), "total_amount": v_total, "category": v_cat
                }
                supabase.table("invoices").insert(final_data).execute()
                st.session_state.scanned_data = None
                st.success("Saved successfully!")
                st.rerun()

# ==========================================
# TAB 2: DASHBOARD & METRICS
# ==========================================
with tab2:
    st.subheader("Business Analytics")
    
    # Calculate Metrics
    total_bills = len(db_data)
    total_expense = sum([float(x.get('total_amount') or 0) for x in db_data])
    total_tax = sum([float(x.get('total_gst_amount') or 0) for x in db_data])
    
    # Display Beautiful Metric Cards
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Total Bills Scanned", value=total_bills)
    m2.metric(label="Total Expense", value=f"₹ {total_expense:,.2f}")
    m3.metric(label="Total Tax (GST)", value=f"₹ {total_tax:,.2f}")
    
    st.write("---")
    st.write("**Recent Invoices**")
    if len(db_data) > 0:
        st.dataframe(db_data, use_container_width=True, hide_index=True)
    else:
        st.info("No bills scanned yet.")

# ==========================================
# TAB 3: TALLY EXPORT
# ==========================================
with tab3:
    st.subheader("Tally XML Generator")
    st.markdown("Download all your verified bills in Tally-compatible XML format. Just import this file in Tally Prime.")
    
    def generate_tally_xml(invoices_data):
        xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>Vouchers</REPORTNAME>\n</REQUESTDESC>\n<REQUESTDATA>\n"
        
        for inv in invoices_data:
            raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-", "") 
            total_amt = float(inv.get('total_amount') or 0)
            base_price = float(inv.get('base_price') or 0)
            igst_amt = float(inv.get('igst_amount') or 0)
            v_name = str(inv.get('vendor_name') or 'Unknown')
            v_cat = str(inv.get('category') or '')
            
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n'
            xml_data += f'<VOUCHER VCHTYPE="Purchase" ACTION="Create">\n'
            xml_data += f'<DATE>{raw_date}</DATE>\n'
            xml_data += f'<VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>\n'
            xml_data += f'<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
            xml_data += f'<NARRATION>Bill Auto-Generated by KhataAI. Category: {v_cat}</NARRATION>\n'
            
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n'
            xml_data += f'<LEDGERNAME>{v_name}</LEDGERNAME>\n'
            xml_data += f'<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n'
            xml_data += f'<AMOUNT>{total_amt}</AMOUNT>\n'
            xml_data += f'</ALLLEDGERENTRIES.LIST>\n'
            
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n'
            xml_data += f'<LEDGERNAME>Purchase A/c</LEDGERNAME>\n'
            xml_data += f'<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n'
            xml_data += f'<AMOUNT>-{base_price}</AMOUNT>\n'
            xml_data += f'</ALLLEDGERENTRIES.LIST>\n'
            
            if igst_amt > 0:
                xml_data += f'<ALLLEDGERENTRIES.LIST>\n'
                xml_data += f'<LEDGERNAME>Input IGST</LEDGERNAME>\n'
                xml_data += f'<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n'
                xml_data += f'<AMOUNT>-{igst_amt}</AMOUNT>\n'
                xml_data += f'</ALLLEDGERENTRIES.LIST>\n'
                
            xml_data += f'</VOUCHER>\n</TALLYMESSAGE>\n'
            
        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    if len(db_data) > 0:
        tally_xml = generate_tally_xml(db_data)
        st.download_button(
            label="📥 Download Tally XML",
            data=tally_xml,
            file_name="KhataAI_Tally_Import.xml",
            mime="application/xml",
            type="primary"
        )
    else:
        st.warning("Please scan some bills first to generate the XML.")
