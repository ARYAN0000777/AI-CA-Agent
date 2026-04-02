import streamlit as st
import json
from google import genai
from PIL import Image
from supabase import create_client, Client

# --- SETUP KEYS (Apni asli keys yahan daalna) ---
AI_API_KEY = "AIzaSyCtPMfZXfWCqtXkuGnYYggkvyAyuV-vhRw"
SUPABASE_URL = "https://vaiafjkhevagdyzgrcjs.supabase.co"
SUPABASE_KEY = "sb_publishable_UzobnS8S3kYmKxG08DjdXw_gvrXJWgu"

# --- INITIALIZE TOOLS ---
ai_client = genai.Client(api_key=AI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- DASHBOARD UI BANANA SHURU ---
st.set_page_config(page_title="AI CA Agent", page_icon="📈", layout="wide")
st.title("🤖 AI CA Agent - Startup Dashboard")
st.markdown("Welcome Aryan! Apne bills upload karo aur AI ko apna jaadu karne do.")

# --- 1. UPLOAD SECTION ---
st.subheader("📤 Naya Bill Scan Karein")
uploaded_file = st.file_uploader("Apne bill ki photo yahan drag & drop karein", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Button banaya AI ko chalane ke liye
    if st.button("🚀 AI Se Data Nikalo"):
        with st.spinner("AI dimaag laga raha hai... kripya wait karein..."):
            try:
                # Photo Load Karo
                img = Image.open(uploaded_file)
                
                # AI Prompt
                prompt = """
                You are an expert Data Extractor for an Indian CA. 
                Read this invoice image and extract the details.
                Return ONLY a valid JSON dictionary in this exact format. Do NOT use markdown blocks like ```json.
                {
                  "vendor_name": "...",
                  "invoice_date": "DD-MM-YYYY",
                  "total_amount": 0.00,
                  "category": "..."
                }
                """
                
                # AI se result mango
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[img, prompt]
                )
                
                # Data ko JSON me badlo aur Database me dalo
                bill_data = json.loads(response.text.strip())
                supabase.table("invoices").insert(bill_data).execute()
                
                st.success("✅ Bill Successfully Scanned aur Database me Save ho gaya!")
                st.rerun() # Page ko refresh karne ke liye taaki table update ho jaye
                
            except Exception as e:
                st.error(f"❌ Kuch gadbad ho gayi: {e}")

st.divider()

# --- 2. DATABASE TABLE SECTION ---
st.subheader("📋 Aapke Scanned Bills")

try:
    response = supabase.table("invoices").select("*").order("id", desc=True).execute()
    data = response.data
    
    if len(data) > 0:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("Abhi tak koi bill scan nahi hua hai.")
except Exception as e:
    st.error(f"Database error: {e}")