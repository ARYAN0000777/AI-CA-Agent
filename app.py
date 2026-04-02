import streamlit as st
import json
from google import genai
from PIL import Image
from supabase import create_client, Client

# --- 1. UI SETUP ---
st.set_page_config(page_title="KhataAI Automation", page_icon="⚡", layout="wide")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
            div.stButton > button:first-child { background-color: #4F46E5; color: white; border-radius: 8px; padding: 10px 24px; font-weight: bold; }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. KEYS & DATABASE ---
AI_API_KEY = st.secrets["AI_API_KEY"]
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

# --- 3. HEADER ---
st.title("⚡ KhataAI - Smart CA Assistant")
st.markdown("Automate your bill entries to Tally instantly. Powered by AI.")
st.write("---")

tab1, tab2, tab3 = st.tabs(["📸 Scan New Bill", "📊 Analytics & Manage", "⚙️ Export to Tally"])

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
                    Extract details from invoice. For 'product_names', list items separated by commas.
                    Return ONLY a valid JSON:
                    {
                      "vendor_name": "...", "gst_number": "...", "invoice_number": "...",
                      "invoice_date": "DD-MM-YYYY", "product_names": "...",
                      "base_price": 0.00, "cgst_amount": 0.00, "sgst_amount": 0.00,
                      "igst_amount": 0.00, "total_amount": 0.00, "category": "..."
                    }
                    """
                    response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[img, prompt])
                    
                    raw_text = response.text.strip().replace("```json", "").replace("```", "").strip() 
                    st.session_state.scanned_data = json.loads(raw_text)
                    st.rerun() 
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    if st.session_state.scanned_data is not None:
        st.info("💡 Please verify the extracted data below and save.")
        data = st.session_state.scanned_data
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2) 
            with col1:
                v_name = st.text_input("Vendor Name", value=data.get("vendor_name", ""))
                v_gst = st.text_input("GST Number", value=data.get("gst_number", ""))
                v_inv_no = st.text_input("Invoice Number", value=data.get("invoice_number", ""))
                v_date = st.text_input("Invoice Date", value=data.get("invoice_date", ""))
                v_cat = st.text_input("Category", value=data.get("category", ""))
                
            with col2:
                v_prods = st.text_area("Product Names (Items)", value=data.get("product_names", ""))
                v_base = st.number_input("Base Price (₹)", value=float(data.get("base_price", 0.0)))
                v_cgst = st.number_input("CGST (₹)", value=float(data.get("cgst_amount", 0.0)))
                v_sgst = st.number_input("SGST (₹)", value=float(data.get("sgst_amount", 0.0)))
                v_igst = st.number_input("IGST (₹)", value=float(data.get("igst_amount", 0.0)))
                v_total = st.number_input("Total Amount (₹)", value=float(data.get("total_amount", 0.0)))

            if st.form_submit_button("✅ Save to Cloud Database"):
                final_data = {
                    "vendor_name": v_name, "gst_number": v_gst, "invoice_date": v_date,
                    "invoice_number": v_inv_no, "product_names": v_prods,
                    "base_price": v_base, "cgst_amount": v_cgst, "sgst_amount": v_sgst,
                    "igst_amount": v_igst, "total_gst_amount": v_cgst + v_sgst + v_igst,
                    "total_amount": v_total, "category": v_cat
                }
                supabase.table("invoices").insert(final_data).execute()
                st.session_state.scanned_data = None
                st.success("Saved successfully!")
                st.rerun()

# ==========================================
# TAB 2: DASHBOARD & DELETE FEATURE (DONO EK SATH)
# ==========================================
with tab2:
    st.subheader("Business Analytics")
    
    total_bills = len(db_data)
    total_expense = sum([float(x.get('total_amount') or 0) for x in db_data])
    total_tax = sum([float(x.get('total_gst_amount') or 0) for x in db_data])
    
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Total Bills Scanned", value=total_bills)
    m2.metric(label="Total Expense", value=f"₹ {total_expense:,.2f}")
    m3.metric(label="Total Tax (GST)", value=f"₹ {total_tax:,.2f}")
    
    st.write("---")
    
    if len(db_data) > 0:
        st.dataframe(db_data, use_container_width=True, hide_index=True)
        
        # --- THE DELETE FEATURE ---
        st.write("---")
        with st.expander("🗑️ Manage Bills (Delete Data)"):
            st.warning("⚠️ Warning: Data deleted from here cannot be recovered.")
            
            bill_options = {f"ID: {row['id']} | {row.get('vendor_name', 'Unknown')} | ₹{row.get('total_amount', 0)}": row['id'] for row in db_data}
            selected_bill = st.selectbox("Select a bill to delete:", options=list(bill_options.keys()))
            
            if st.button("❌ Delete Selected Bill"):
                bill_id_to_delete = bill_options[selected_bill]
                try:
                    supabase.table("invoices").delete().eq("id", bill_id_to_delete).execute()
                    st.success(f"Bill deleted successfully!")
                    st.rerun() 
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("No bills scanned yet.")

# ==========================================
# TAB 3: ADVANCED TALLY EXPORT (PURCHASE ENTRY)
# ==========================================
with tab3:
    st.subheader("Tally XML Generator")
    st.markdown("Download detailed Tally XML file with **Item Names** and **Invoice Numbers**.")
    
    def generate_tally_xml(invoices_data):
        xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>Vouchers</REPORTNAME>\n</REQUESTDESC>\n<REQUESTDATA>\n"
        
        for inv in invoices_data:
            raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-", "") 
            total_amt = float(inv.get('total_amount') or 0)
            base_price = float(inv.get('base_price') or 0)
            cgst_amt = float(inv.get('cgst_amount') or 0)
            sgst_amt = float(inv.get('sgst_amount') or 0)
            igst_amt = float(inv.get('igst_amount') or 0)
            
            # Anti-Crash trick for Tally (replaces & with &amp;)
            v_name = str(inv.get('vendor_name') or 'Unknown').replace("&", "&amp;")
            v_inv_no = str(inv.get('invoice_number') or 'Not Found').replace("&", "&amp;")
            v_prods = str(inv.get('product_names') or 'Various Items').replace("&", "&amp;")
            
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n'
            xml_data += f'<VOUCHER VCHTYPE="Purchase" ACTION="Create">\n'
            xml_data += f'<DATE>{raw_date}</DATE>\n'
            
            # 1. INVOICE NUMBER YAHAN HAI
            xml_data += f'<REFERENCE>{v_inv_no}</REFERENCE>\n'
            
            xml_data += f'<VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>\n'
            xml_data += f'<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
            
            # 2. PRODUCT KA NAAM YAHAN HAI
            xml_data += f'<NARRATION>Bill No: {v_inv_no} | Items: {v_prods}</NARRATION>\n'
            
            # Ledger Entries
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{v_name}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n<AMOUNT>{total_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
            
            # 3. PURCHASE ACCOUNT YAHAN HAI
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Purchase A/c</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{base_price}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
            
            # Taxes
            if cgst_amt > 0:
                xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Input CGST</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{cgst_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
            if sgst_amt > 0:
                xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Input SGST</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{sgst_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
            if igst_amt > 0:
                xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>Input IGST</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{igst_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
                
            xml_data += f'</VOUCHER>\n</TALLYMESSAGE>\n'
            
        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    if len(db_data) > 0:
        tally_xml = generate_tally_xml(db_data)
        st.download_button(
            label="📥 Download Detailed Tally XML", 
            data=tally_xml, 
            file_name="KhataAI_Pro_Import.xml", 
            mime="application/xml", 
            type="primary"
        )
