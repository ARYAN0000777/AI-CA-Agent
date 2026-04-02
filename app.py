import streamlit as st
import json
from google import genai
from PIL import Image
from supabase import create_client, Client

# --- SETUP KEYS (Tijori se) ---
AI_API_KEY = st.secrets["AI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# --- INITIALIZE TOOLS ---
ai_client = genai.Client(api_key=AI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SESSION STATE (Memory Setup) ---
if "scanned_data" not in st.session_state:
    st.session_state.scanned_data = None

# --- DASHBOARD UI ---
st.set_page_config(page_title="AI CA Agent Pro", page_icon="📈", layout="wide")
st.title("🤖 AI CA Agent - Pro Dashboard")

# --- 1. UPLOAD SECTION ---
st.subheader("📤 Naya Bill Scan Karein")
uploaded_file = st.file_uploader("Apne bill ki photo upload karein", type=["jpg", "png", "jpeg"])

if uploaded_file is not None and st.session_state.scanned_data is None:
    if st.button("🚀 AI Se Data Nikalo"):
        with st.spinner("AI dimaag laga raha hai..."):
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
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[img, prompt]
                )
                
                # --- AI JUGGAAD CLEANER ---
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:] 
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3] 
                    
                raw_text = raw_text.strip() 
                
                st.session_state.scanned_data = json.loads(raw_text)
                st.rerun() 
                
            except Exception as e:
                st.error(f"❌ Kuch gadbad ho gayi: {e}")

# --- 2. REVIEW & EDIT SCREEN ---
if st.session_state.scanned_data is not None:
    st.warning("⚠️ Kripya AI ka data check karein. Agar koi galti hai toh yahan theek karke 'Save' dabayein.")
    
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

        submit_btn = st.form_submit_button("✅ Final Save to Database")
        
        if submit_btn:
            final_data = {
                "vendor_name": v_name, 
                "gst_number": v_gst, 
                "invoice_date": v_date,
                "base_price": v_base, 
                "cgst_amount": v_cgst, 
                "sgst_amount": v_sgst,
                "igst_amount": v_igst, 
                "total_gst_amount": v_cgst + v_sgst + v_igst,
                "tds_amount": float(data.get("tds_amount", 0.0)), 
                "total_amount": v_total, 
                "category": v_cat
            }
            supabase.table("invoices").insert(final_data).execute()
            
            st.session_state.scanned_data = None
            st.success("✅ Data Successfully Saved!")
            st.rerun()

st.divider()

# --- 3. DATABASE TABLE SECTION ---
st.subheader("📋 Aapke Scanned Bills")
try:
    response = supabase.table("invoices").select("*").order("id", desc=True).execute()
    db_data = response.data
    if len(db_data) > 0:
        st.dataframe(db_data, use_container_width=True)
    else:
        st.info("Abhi tak koi bill scan nahi hua hai.")
except Exception as e:
    st.error(f"Database error: {e}")

st.divider()

# --- 4. TALLY EXPORT ENGINE (THE FINAL BOSS) ---
st.subheader("🎯 Export to Tally (XML)")
st.markdown("Database ke saare verified bills ko ek click me Tally XML me convert karein.")

def generate_tally_xml(invoices_data):
    xml_data = """<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
            </REQUESTDESC>
            <REQUESTDATA>"""
            
    for inv in invoices_data:
        # THE FIX: Safely handling None values
        raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-", "") 
        total_amt = float(inv.get('total_amount') or 0)
        base_price = float(inv.get('base_price') or 0)
        igst_amt = float(inv.get('igst_amount') or 0)
        v_name = str(inv.get('vendor_name') or 'Unknown')
        v_cat = str(inv.get('category') or '')
        
        xml_data += f"""
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="Purchase" ACTION="Create">
                        <DATE>{raw_date}</DATE>
                        <VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>
                        <PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>
                        <NARRATION>Bill Auto-Generated by AI CA Agent. Category: {v_cat}</NARRATION>
                        
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{v_name}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{total_amt}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Purchase A/c</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>-{base_price}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>"""
                        
        # IGST Entry (Ab yahan error nahi aayega!)
        if igst_amt > 0:
            xml_data += f"""
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Input IGST</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>-{igst_amt}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>"""
                        
        xml_data += """
                    </VOUCHER>
                </TALLYMESSAGE>"""
                
    xml_data += """
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
    return xml_data

if 'db_data' in locals() and len(db_data) > 0:
    tally_xml = generate_tally_xml(db_data)
    
    st.download_button(
        label="📥 Download Tally XML File",
        data=tally_xml,
        file_name="Tally_Auto_Entry.xml",
        mime="application/xml",
        type="primary"
    )
else:
    st.info("Export karne ke liye pehle kuch bills scan karein.")
