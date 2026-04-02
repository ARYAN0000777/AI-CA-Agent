import streamlit as st
import json
from google import genai
from PIL import Image
from supabase import create_client, Client

# --- 1. UI CONFIGURATION (Sabse pehle likhna zaruri hai) ---
st.set_page_config(page_title="KhataAI Automation", page_icon="⚡", layout="wide")

# Hide Streamlit Branding (Menu & Footer)
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

# --- SETUP KEYS ---
AI_API_KEY = st.secrets["AI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SESSION STATE ---
if "scanned_data" not in st.session_state:
    st.session_state.scanned_data = None

# --- FETCH DATABASE DATA FIRST ---
try:
    response = supabase.table("invoices").select("*").order("id", desc=True).execute()
    db_data = response.data
except Exception:
    db_data = []

# --- APP HEADER ---
st.title("⚡ KhataAI - Smart CA Assistant")
st.markdown("Automate your bill entries to Tally instantly. Powered by AI.")
st.write("---")

# --- PRO UI TABS ---
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
                    
                    raw_text = response.text.strip()
                    if raw_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

Isko GitHub par commit karo aur apni site ko refresh karo. Tum dekhoge ki app ab kitni clean lag rahi hai, upar ekdam professional Tabs aa gaye hain, aur Dashboard me Kharcha (Expense) ke bade-bade Numbers dikh rahe hain!

Batao bhai, UI upgrade kaisa laga? Kya is "KhataAI" naam ko permanent kar lein ya tumne koi aur kadak naam socha hai?
