import streamlit as st
import json
import pandas as pd
from google import genai
from PIL import Image
from supabase import create_client, Client

# ─────────────────────────────────────────────
# 1. PAGE CONFIG & ULTRA PREMIUM DARK THEME
# ─────────────────────────────────────────────
st.set_page_config(page_title="KhataAI Pro", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

:root { --bg: #060608; --surface: rgba(255,255,255,0.03); --border: rgba(255,255,255,0.07); --text: #EAE8F5; --muted: #6B6880; }
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp { background-color: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container { padding: 0 2.5rem 4rem !important; max-width: 1300px !important; }

/* Mesh Background */
.bg-mesh { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.bg-mesh span { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.55; }
.bg-mesh span:nth-child(1) { width: 700px; height: 700px; top: -200px; left: -180px; background: radial-gradient(circle, rgba(124,111,255,0.22) 0%, transparent 65%); animation: meshDrift1 18s ease-in-out infinite alternate; }
.bg-mesh span:nth-child(2) { width: 550px; height: 550px; bottom: -150px; right: -100px; background: radial-gradient(circle, rgba(0,214,143,0.15) 0%, transparent 65%); animation: meshDrift2 22s ease-in-out infinite alternate; }
@keyframes meshDrift1 { from { transform: translate(0,0) scale(1); } to { transform: translate(60px,40px) scale(1.12); } }
@keyframes meshDrift2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-40px,-30px) scale(1.08); } }

/* Hero Header */
.khata-topbar { display: flex; align-items: center; justify-content: space-between; padding: 2rem 0 1.2rem; position: relative; z-index: 10; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
.khata-brand { display: flex; align-items: center; gap: 1rem; }
.khata-logo { width: 46px; height: 46px; background: linear-gradient(135deg, #7C6FFF 0%, #00D68F 100%); border-radius: 13px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; box-shadow: 0 0 0 1px rgba(124,111,255,0.4), 0 0 28px rgba(124,111,255,0.35); }
.khata-title { font-family: 'Syne', sans-serif !important; font-size: 1.75rem !important; font-weight: 800 !important; background: linear-gradient(120deg, #FFFFFF 20%, #7C6FFF 60%, #00D68F 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.khata-sub { font-size: 0.78rem; color: var(--muted); font-weight: 400; margin-top: 3px; }
.khata-pill { background: rgba(124,111,255,0.15); border: 1px solid rgba(124,111,255,0.25); color: #A89EFF; font-size: 0.72rem; font-weight: 600; padding: 4px 12px; border-radius: 20px; }

/* Tabs & UI */
.stTabs [data-baseweb="tab-list"] { gap: 6px !important; background: rgba(255,255,255,0.03) !important; border-radius: 14px !important; padding: 5px !important; border: 1px solid var(--border) !important; position: relative; z-index: 5; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 10px !important; color: var(--muted) !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; font-size: 0.85rem !important; padding: 8px 22px !important; border: none !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(124,111,255,0.2), rgba(0,214,143,0.1)) !important; color: #C4BEFF !important; font-weight: 600 !important; box-shadow: inset 0 0 0 1px rgba(124,111,255,0.3) !important; }

.section-title { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.section-badge { background: rgba(124,111,255,0.15); color: #A89EFF; font-size: 0.68rem; font-weight: 600; padding: 2px 8px; border-radius: 20px; border: 1px solid rgba(124,111,255,0.25); }

.stFileUploader > div, div[data-testid="stAudioInput"] > div { background: rgba(124,111,255,0.04) !important; border: 2px dashed rgba(124,111,255,0.25) !important; border-radius: 16px !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input { background: rgba(255,255,255,0.04) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; color: var(--text) !important; }

div.stButton > button { background: linear-gradient(135deg, #7C6FFF, #5B4FE8) !important; color: white !important; border: none !important; border-radius: 11px !important; padding: 11px 24px !important; font-weight: 600 !important; width: 100%; box-shadow: 0 4px 20px rgba(124,111,255,0.3) !important; }
div.stDownloadButton > button { background: linear-gradient(135deg, #00D68F, #00A86B) !important; color: white !important; width: 100%; border-radius: 11px !important; padding: 13px 28px !important; font-weight: 600 !important; box-shadow: 0 4px 24px rgba(0,214,143,0.3) !important; }
div.stButton > button:has(span:contains("Delete")) { background: rgba(239,68,68,0.12) !important; color: #FCA5A5 !important; border: 1px solid rgba(239,68,68,0.25) !important; box-shadow: none !important; }

.export-card { background: linear-gradient(135deg, rgba(0,214,143,0.06), rgba(124,111,255,0.06)); border: 1px solid rgba(0,214,143,0.18); border-radius: 20px; padding: 2.5rem; text-align: center; }
.metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem 1.6rem; position: relative; overflow: hidden; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 700; color: #FFFFFF; } .metric-value.purple { color: #A89EFF; } .metric-value.green { color: #6EE7B7; } .metric-value.amber { color: #FCD34D; }
</style>
<div class="bg-mesh"><span></span><span></span></div>
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
# 3. HERO & TABS (NEW 4TH TAB ADDED)
# ─────────────────────────────────────────────
st.markdown(f'<div class="khata-topbar"><div class="khata-brand"><div class="khata-logo">⚡</div><div><div class="khata-title">KhataAI</div><div class="khata-sub">Smart CA Assistant — GST · Voice · Tally</div></div></div><div class="khata-pill">v3.0 VOICE</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📸 Scan Invoice", "🎙️ Voice Bill", "📊 Analytics", "⚙️ Tally Export"])

# ══════════════════════════════════════════════
# TAB 1: IMAGE SCAN (Purana Code)
# ══════════════════════════════════════════════
with tab1:
    col_up, col_prev = st.columns([1, 1], gap="large")
    with col_up:
        st.markdown('<div class="section-title">📂 Upload Invoice Image <span class="section-badge">AI-VISION</span></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop invoice", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if uploaded_file and not st.session_state.scanned_data:
            if st.button("🚀 Extract Data from Image"):
                with st.spinner("AI is reading image..."):
                    try:
                        img = Image.open(uploaded_file)
                        prompt = '''Extract details into JSON: {"vendor_name": "...", "gst_number": "...", "vendor_address": "...", "bank_details": "...", "invoice_number": "...", "invoice_date": "DD-MM-YYYY", "base_price": 0.0, "cgst_amount": 0.0, "sgst_amount": 0.0, "igst_amount": 0.0, "total_amount": 0.0, "category": "...", "line_items": [{"item_name": "...", "hsn_code": "...", "quantity": 0.0, "unit": "...", "rate": 0.0, "amount": 0.0}]}'''
                        resp = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[img, prompt])
                        st.session_state.scanned_data = json.loads(resp.text.strip().replace("```json","").replace("```","").strip())
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    with col_prev:
        if uploaded_file: st.image(uploaded_file, use_container_width=True)

    if st.session_state.scanned_data:
        data = st.session_state.scanned_data
        st.markdown('<hr><div class="section-title">✏️ Verify Image Data</div>', unsafe_allow_html=True)
        with st.form("edit_img_form"):
            c1, c2 = st.columns(2)
            with c1: v_name = st.text_input("Vendor", data.get("vendor_name",""))
            with c2: v_gst = st.text_input("GST", data.get("gst_number",""))
            
            edited_df = st.data_editor(pd.DataFrame(data.get("line_items", [{"item_name":""}])), num_rows="dynamic", use_container_width=True)
            v_total = st.number_input("Total Amount ₹", value=float(data.get("total_amount", 0.0)))
            
            if st.form_submit_button("✅ Save Image Bill"):
                final = {"vendor_name": v_name, "gst_number": v_gst, "total_amount": v_total, "line_items": edited_df.to_dict('records')}
                supabase.table("invoices").insert(final).execute()
                st.session_state.scanned_data = None
                st.rerun()

# ══════════════════════════════════════════════
# TAB 2: 🎙️ VOICE BILLING (THE GAME CHANGER)
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🎙️ AI Voice Billing <span class="section-badge">MAGIC</span></div>', unsafe_allow_html=True)
    st.info("💡 Mic icon par click karein aur bole: *'Sharma Hardware se 10 pipe aaye 50 ke rate par aur 5 box aaye 100 ke rate par'*")
    
    # The magical audio input widget
    audio_value = st.audio_input("Record Sales/Purchase Bill", label_visibility="collapsed")
    
    if audio_value is not None and st.session_state.voice_scanned_data is None:
        if st.button("🚀 Generate Bill from Voice"):
            with st.spinner("AI is listening to your voice and making the bill..."):
                try:
                    # Pass audio bytes directly to Gemini 2.5 Flash
                    audio_prompt = """
                    Listen to this audio in Hindi/English. You are an expert Accountant.
                    Extract the vendor name, and list of items purchased/sold along with their quantities and rates.
                    Calculate amounts automatically. 
                    Return ONLY a valid JSON:
                    {
                      "vendor_name": "...", 
                      "base_price": 0.0, "total_amount": 0.0,
                      "line_items": [{"item_name": "...", "quantity": 0.0, "unit": "Nos", "rate": 0.0, "amount": 0.0}]
                    }
                    """
                    # Provide audio data to Gemini
                    resp = ai_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            {'mime_type': 'audio/wav', 'data': audio_value.getvalue()},
                            audio_prompt
                        ]
                    )
                    clean_json = resp.text.strip().replace("```json","").replace("```","").strip()
                    st.session_state.voice_scanned_data = json.loads(clean_json)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Voice understanding failed: {e}")

    # Show Editable Table for Voice Data
    if st.session_state.voice_scanned_data is not None:
        v_data = st.session_state.voice_scanned_data
        st.markdown('<hr><div class="section-title">✏️ Verify Voice Bill</div>', unsafe_allow_html=True)
        st.success("✨ AI ne aapki aawaz sun kar yeh bill banaya hai!")
        
        with st.form("edit_voice_form"):
            c1, c2 = st.columns(2)
            with c1: voice_vendor = st.text_input("Party / Vendor Name", value=v_data.get("vendor_name", "Local Party"))
            with c2: voice_date = st.text_input("Invoice Date", value="2026-04-08")
            
            st.markdown("**📦 Items Mentioned in Audio**")
            raw_voice_items = v_data.get("line_items", [])
            voice_edited_df = st.data_editor(pd.DataFrame(raw_voice_items), num_rows="dynamic", use_container_width=True)
            
            voice_total = st.number_input("Total Amount ₹", value=float(v_data.get("total_amount", 0.0)))
            
            if st.form_submit_button("✅ Save Voice Bill to Database"):
                voice_final_data = {
                    "vendor_name": voice_vendor, "invoice_date": voice_date,
                    "total_amount": voice_total, "category": "Voice Entry",
                    "line_items": voice_edited_df.to_dict(orient='records')
                }
                supabase.table("invoices").insert(voice_final_data).execute()
                st.session_state.voice_scanned_data = None
                st.success("✅ Voice Bill Saved!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 3: ANALYTICS (Purana Code)
# ══════════════════════════════════════════════
with tab3:
    total_bills = len(db_data)
    m1, m2, m3 = st.columns(3, gap="medium")
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-value purple">{total_bills}</div><div>Total Bills</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-value green">₹{sum([float(x.get("total_amount") or 0) for x in db_data]):,.0f}</div><div>Total Expense</div></div>', unsafe_allow_html=True)
    
    if total_bills > 0:
        display_df = pd.DataFrame(db_data)
        def get_items(r): return ", ".join([str(i.get('item_name','')) for i in r.get('line_items',[])]) if isinstance(r.get('line_items'), list) else str(r.get('product_names',''))
        display_df['Items_Summary'] = display_df.apply(get_items, axis=1)
        display_df.insert(0, 'Sr_No', range(1, len(display_df)+1))
        st.dataframe(display_df.drop(columns=['id','line_items','product_names','vendor_address','bank_details'], errors='ignore'), use_container_width=True, hide_index=True)

        with st.expander("🗑️ Delete Bill"):
            opts = {f"Sr {idx+1} | {r.get('vendor_name','')} | ₹{r.get('total_amount',0)}": r['id'] for idx, r in enumerate(db_data)}
            sel = st.selectbox("Select:", list(opts.keys()))
            if st.button("❌ Delete"): supabase.table("invoices").delete().eq("id", opts[sel]).execute(); st.rerun()

# ══════════════════════════════════════════════
# TAB 4: TALLY EXPORT (MASTER LOGIC)
# ══════════════════════════════════════════════
with tab4:
    def generate_tally_xml(invoices_data):
        xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>All Masters</REPORTNAME>\n</REQUESTDESC>\n<REQUESTDATA>\n"
        unique_items, parties_data = set(), {}
        for inv in invoices_data:
            p = str(inv.get('vendor_name') or 'Unknown').replace("&","&amp;")
            parties_data[p] = {'gst': str(inv.get('gst_number') or '').replace("&","&amp;"), 'addr': str(inv.get('vendor_address') or '').replace("&","&amp;")}
            if isinstance(inv.get('line_items'), list):
                for i in inv.get('line_items'): 
                    if i.get('item_name'): unique_items.add((str(i['item_name']).replace("&","&amp;"), str(i.get('unit','Nos')).replace("&","&amp;")))

        for p, d in parties_data.items():
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<LEDGER ACTION="Create">\n<NAME>{p}</NAME>\n<PARENT>Sundry Creditors</PARENT>\n'
            if d['gst'] and d['gst'] != "None": xml_data += f'<PARTYGSTIN>{d["gst"]}</PARTYGSTIN>\n'
            xml_data += '</LEDGER>\n</TALLYMESSAGE>\n'

        for itm, unt in unique_items:
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<STOCKITEM ACTION="Create">\n<NAME>{itm}</NAME>\n<PARENT>Primary</PARENT>\n<BASEUNITS>{unt}</BASEUNITS>\n</STOCKITEM>\n</TALLYMESSAGE>\n'

        for inv in invoices_data:
            raw_date = str(inv.get("invoice_date") or "2026-03-27").replace("-","")
            v_name = str(inv.get('vendor_name') or 'Unknown').replace("&","&amp;")
            total_amt = float(inv.get('total_amount') or 0)
            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<VOUCHER VCHTYPE="Purchase" ACTION="Create">\n<DATE>{raw_date}</DATE>\n<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{v_name}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n<AMOUNT>{total_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'
            
            line_items = inv.get('line_items') or []
            if isinstance(line_items, list) and len(line_items) > 0:
                for itm in line_items:
                    xml_data += f'<ALLINVENTORYENTRIES.LIST>\n<STOCKITEMNAME>{str(itm.get("item_name","")).replace("&","&amp;")}</STOCKITEMNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<BILLEDQTY>{float(itm.get("quantity",0))} {str(itm.get("unit","Nos"))}</BILLEDQTY>\n<RATE>{float(itm.get("rate",0))}</RATE>\n<AMOUNT>-{float(itm.get("amount",0))}</AMOUNT>\n<ACCOUNTINGALLOCATIONS.LIST>\n<LEDGERNAME>Purchase A/c</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>-{float(itm.get("amount",0))}</AMOUNT>\n</ACCOUNTINGALLOCATIONS.LIST>\n</ALLINVENTORYENTRIES.LIST>\n'
            xml_data += '</VOUCHER>\n</TALLYMESSAGE>\n'
        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    if len(db_data) > 0:
        st.markdown('<div class="export-card"><span class="export-icon">📥</span><div class="export-title">Download Master Tally XML</div></div><br>', unsafe_allow_html=True)
        st.download_button("📥 Download KhataAI_Import.xml", generate_tally_xml(db_data), "KhataAI_Voice_Import.xml", "application/xml", use_container_width=True)
    else: st.info("No bills to export.")
