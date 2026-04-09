import streamlit as st
import json
import pandas as pd
from google import genai
from google.genai import types
from PIL import Image
from supabase import create_client, Client
from fpdf import FPDF
import base64
import time
import requests
import io
from gtts import gTTS
from groq import Groq
import os

# ─────────────────────────────────────────────
# 1. PAGE CONFIG & ULTRA-PREMIUM CLAUDE UI/UX
# ─────────────────────────────────────────────
st.set_page_config(page_title="KhataAI Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════════
   DESIGN TOKENS
══════════════════════════════════════════ */
:root {
  --purple:        #7C6FFF;
  --purple-dim:    rgba(124,111,255,0.12);
  --purple-glow:   rgba(124,111,255,0.22);
  --purple-border: rgba(124,111,255,0.22);
  --purple-border-hover: rgba(124,111,255,0.55);
  --green:         #00D68F;
  --green-dim:     rgba(0,214,143,0.10);
  --green-glow:    rgba(0,214,143,0.18);
  --amber:         #FFB547;
  --amber-dim:     rgba(255,181,71,0.10);
  --amber-glow:    rgba(255,181,71,0.18);
  --bg:            #05050A;
  --bg-surface:    rgba(255,255,255,0.025);
  --bg-surface-2:  rgba(255,255,255,0.042);
  --border:        rgba(255,255,255,0.065);
  --border-hover:  rgba(255,255,255,0.13);
  --text:          #EAE8F5;
  --muted:         #635F7A;
  --muted-2:       #8A85A0;
  --radius:        18px;
  --radius-sm:     11px;
  --radius-xs:     8px;
  --glass-bg:      rgba(12,10,28,0.55);
  --glass-border:  rgba(124,111,255,0.18);
  --glass-blur:    blur(28px) saturate(160%);
  --transition-fast:   all 0.18s cubic-bezier(0.4,0,0.2,1);
  --transition-medium: all 0.28s cubic-bezier(0.4,0,0.2,1);
  --transition-bounce: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
}

/* ══════════════════════════════════════════
   RESET & BASE
══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
}

.stApp > header { background: transparent !important; }

.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 4rem !important;
  max-width: 1280px !important;
}

#MainMenu, footer, .stDeployButton { visibility: hidden !important; }

/* ══════════════════════════════════════════
   ANIMATED MESH BACKGROUND
══════════════════════════════════════════ */
.bg-mesh {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 0; overflow: hidden;
}
.bg-mesh span {
  position: absolute; border-radius: 50%;
  filter: blur(90px); opacity: 0.6;
  will-change: transform;
}
.bg-mesh span:nth-child(1) {
  width: 800px; height: 800px;
  top: -250px; left: -200px;
  background: radial-gradient(circle, rgba(124,111,255,0.20) 0%, transparent 60%);
  animation: meshDrift1 20s ease-in-out infinite alternate;
}
.bg-mesh span:nth-child(2) {
  width: 600px; height: 600px;
  bottom: -180px; right: -120px;
  background: radial-gradient(circle, rgba(0,214,143,0.13) 0%, transparent 60%);
  animation: meshDrift2 25s ease-in-out infinite alternate;
}
.bg-mesh span:nth-child(3) {
  width: 420px; height: 420px;
  top: 45%; left: 55%;
  background: radial-gradient(circle, rgba(255,181,71,0.07) 0%, transparent 65%);
  animation: meshDrift3 30s ease-in-out infinite alternate;
}

@keyframes meshDrift1 { from { transform: translate(0,0) scale(1); } to { transform: translate(70px,50px) scale(1.15); } }
@keyframes meshDrift2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-50px,-35px) scale(1.10); } }
@keyframes meshDrift3 { from { transform: translate(0,0) scale(1); } to { transform: translate(-30px,40px) scale(1.08); } }

/* ══════════════════════════════════════════
   SIDEBAR — ULTRA PREMIUM
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(8,6,20,0.97) 0%, rgba(10,8,24,0.95) 100%) !important;
  border-right: 1px solid var(--glass-border) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 4px 0 40px rgba(0,0,0,0.6) !important;
}
[data-testid="stSidebarNav"] { display: none !important; } 

[data-testid="stSidebar"] > div:first-child {
  padding: 2rem 1.4rem !important;
}

[data-testid="stSidebar"] h2 {
  font-family: 'Syne', sans-serif !important;
  font-size: 1.15rem !important;
  font-weight: 700 !important;
  color: #FFFFFF !important;
  letter-spacing: -0.01em !important;
  line-height: 1.3 !important;
}

/* Sidebar separator */
[data-testid="stSidebar"] hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 1.2rem 0 !important;
}

/* Sidebar expander */
[data-testid="stSidebar"] .streamlit-expanderHeader {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--muted-2) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 0.65rem 1rem !important;
  transition: var(--transition-fast) !important;
}

[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
  background: var(--bg-surface-2) !important;
  border-color: var(--purple-border) !important;
  color: #C4BEFF !important;
}

[data-testid="stSidebar"] .streamlit-expanderContent {
  background: rgba(124,111,255,0.03) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
  padding: 1rem !important;
}

/* Sidebar text inputs */
[data-testid="stSidebar"] .stTextInput > div > div > input {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-xs) !important;
  color: var(--text) !important;
  font-size: 0.83rem !important;
  padding: 8px 12px !important;
  transition: var(--transition-fast) !important;
}

[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
  border-color: var(--purple-border-hover) !important;
  box-shadow: 0 0 0 3px rgba(124,111,255,0.12) !important;
  background: rgba(124,111,255,0.05) !important;
}

/* ══════════════════════════════════════════
   TOP HEADER / HERO TOPBAR
══════════════════════════════════════════ */
.khata-topbar {
  display: flex; align-items: center;
  justify-content: space-between;
  padding: 1.8rem 0 1.4rem;
  position: relative; z-index: 10;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
  animation: fadeSlideDown 0.65s cubic-bezier(.22,.68,0,1.2) both;
}
@keyframes fadeSlideDown {
  from { opacity: 0; transform: translateY(-16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.khata-brand { display: flex; align-items: center; gap: 1rem; }

.khata-logo {
  width: 48px; height: 48px;
  background: linear-gradient(140deg, #7C6FFF 0%, #4ECDAA 100%);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.45rem;
  box-shadow:
    0 0 0 1px rgba(124,111,255,0.5),
    0 0 0 4px rgba(124,111,255,0.10),
    0 0 32px rgba(124,111,255,0.40),
    inset 0 1px 0 rgba(255,255,255,0.2);
  animation: logoPulse 4s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes logoPulse {
  0%, 100% {
    box-shadow: 0 0 0 1px rgba(124,111,255,0.5), 0 0 0 4px rgba(124,111,255,0.10), 0 0 32px rgba(124,111,255,0.38), inset 0 1px 0 rgba(255,255,255,0.2);
  }
  50% {
    box-shadow: 0 0 0 1px rgba(124,111,255,0.7), 0 0 0 6px rgba(124,111,255,0.14), 0 0 52px rgba(124,111,255,0.60), inset 0 1px 0 rgba(255,255,255,0.25);
  }
}

.khata-title {
  font-family: 'Syne', sans-serif !important;
  font-size: 1.7rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.02em !important;
  background: linear-gradient(115deg, #FFFFFF 15%, #A89EFF 55%, #6EE7B7 100%);
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
  line-height: 1.15 !important;
}

.khata-sub {
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 400;
  margin-top: 4px;
  letter-spacing: 0.01em;
}

.khata-pill {
  background: linear-gradient(135deg, rgba(124,111,255,0.18), rgba(0,214,143,0.10));
  border: 1px solid rgba(124,111,255,0.30);
  color: #B4ABFF;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 5px 14px;
  border-radius: 30px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  box-shadow: 0 2px 12px rgba(124,111,255,0.18);
  backdrop-filter: blur(8px);
}

/* ══════════════════════════════════════════
   TABS
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px !important;
  background: rgba(255,255,255,0.028) !important;
  border-radius: 14px !important;
  padding: 5px !important;
  border: 1px solid var(--border) !important;
  position: relative; z-index: 5;
  backdrop-filter: blur(12px) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 10px !important;
  color: var(--muted-2) !important;
  font-weight: 500 !important;
  font-size: 0.86rem !important;
  padding: 9px 22px !important;
  border: none !important;
  transition: var(--transition-fast) !important;
  position: relative;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
  color: #C4BEFF !important;
  background: rgba(124,111,255,0.07) !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg,
    rgba(124,111,255,0.22) 0%,
    rgba(0,214,143,0.10) 100%
  ) !important;
  color: #D0CBFF !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 16px rgba(124,111,255,0.18), inset 0 1px 0 rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(124,111,255,0.22) !important;
}
/* Tab content panel */
.stTabs [data-baseweb="tab-panel"] {
  padding-top: 1.8rem !important;
}

/* ══════════════════════════════════════════
   METRIC CARDS — GLASSMORPHISM
══════════════════════════════════════════ */
.metric-card {
  background: var(--glass-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.6rem 1.7rem;
  position: relative;
  overflow: hidden;
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  transition: var(--transition-medium);
  animation: cardReveal 0.55s cubic-bezier(.22,.68,0,1.2) both;
  cursor: default;
}

/* Noise texture overlay */
.metric-card::after {
  content: '';
  position: absolute; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  border-radius: inherit;
  pointer-events: none;
  opacity: 0.6;
}

/* Top accent bar */
.metric-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  transition: opacity 0.3s ease;
  opacity: 0.9;
}
.metric-card.purple::before { background: linear-gradient(90deg, #7C6FFF, #A89EFF, #7C6FFF); background-size: 200% 100%; animation: shimmer 3s linear infinite; }
.metric-card.green::before  { background: linear-gradient(90deg, #00D68F, #6EE7B7, #00D68F); background-size: 200% 100%; animation: shimmer 3.5s linear infinite; }
.metric-card.amber::before  { background: linear-gradient(90deg, #FFB547, #FCD34D, #FFB547); background-size: 200% 100%; animation: shimmer 4s linear infinite; }

@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

/* Hover states */
.metric-card:hover {
  transform: translateY(-5px) scale(1.008);
  border-color: var(--border-hover);
}
.metric-card.purple:hover {
  box-shadow: 0 20px 60px rgba(124,111,255,0.18), 0 0 0 1px rgba(124,111,255,0.22);
  border-color: rgba(124,111,255,0.38) !important;
  background: rgba(12,10,30,0.70);
}
.metric-card.green:hover {
  box-shadow: 0 20px 60px rgba(0,214,143,0.14), 0 0 0 1px rgba(0,214,143,0.22);
  border-color: rgba(0,214,143,0.35) !important;
  background: rgba(8,22,18,0.68);
}
.metric-card.amber:hover {
  box-shadow: 0 20px 60px rgba(255,181,71,0.13), 0 0 0 1px rgba(255,181,71,0.22);
  border-color: rgba(255,181,71,0.35) !important;
  background: rgba(22,16,6,0.68);
}

/* Inner glow blobs */
.metric-card.purple { background-image: radial-gradient(ellipse at top right, rgba(124,111,255,0.09) 0%, transparent 60%); }
.metric-card.green  { background-image: radial-gradient(ellipse at top right, rgba(0,214,143,0.08) 0%, transparent 60%); }
.metric-card.amber  { background-image: radial-gradient(ellipse at top right, rgba(255,181,71,0.07) 0%, transparent 60%); }

@keyframes cardReveal {
  from { opacity: 0; transform: translateY(22px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.metric-icon {
  font-size: 1.55rem; margin-bottom: 0.9rem;
  display: inline-block;
  filter: drop-shadow(0 0 8px currentColor);
}
.metric-label {
  font-size: 0.68rem;
  color: var(--muted);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.10em;
  margin-bottom: 0.4rem;
}
.metric-value {
  font-family: 'Syne', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1;
  letter-spacing: -0.02em;
}
.metric-value.purple { color: #B4ABFF; text-shadow: 0 0 24px rgba(124,111,255,0.5); }
.metric-value.green  { color: #6EE7B7; text-shadow: 0 0 24px rgba(0,214,143,0.4); }
.metric-value.amber  { color: #FCD34D; text-shadow: 0 0 24px rgba(255,181,71,0.4); }

/* ══════════════════════════════════════════
   FORM INPUTS — GLOBAL
══════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
  background: rgba(255,255,255,0.034) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-xs) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.875rem !important;
  transition: var(--transition-fast) !important;
  caret-color: var(--purple) !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color: var(--muted) !important; }

.stTextInput > div > div > input:hover,
.stTextArea > div > div > textarea:hover,
.stNumberInput > div > div > input:hover {
  border-color: var(--border-hover) !important;
  background: rgba(255,255,255,0.042) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
  border-color: rgba(124,111,255,0.55) !important;
  box-shadow: 0 0 0 4px rgba(124,111,255,0.10), 0 0 16px rgba(124,111,255,0.08) !important;
  background: rgba(124,111,255,0.045) !important;
  outline: none !important;
}

/* Selectbox & Multiselect */
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: rgba(255,255,255,0.034) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-xs) !important;
  color: var(--text) !important;
  transition: var(--transition-fast) !important;
}

.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
  border-color: var(--border-hover) !important;
}

/* Dropdown menu */
[data-baseweb="popover"], [data-baseweb="menu"] {
  background: rgba(14,12,28,0.97) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 24px 60px rgba(0,0,0,0.6) !important;
}
[data-baseweb="option"]:hover, [data-baseweb="option"][aria-selected="true"] {
  background: var(--purple-dim) !important;
}

/* Input labels */
.stTextInput label, .stNumberInput label, .stTextArea label,
.stSelectbox label, .stMultiSelect label, .stRadio label {
  color: var(--muted-2) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.02em !important;
}

/* ══════════════════════════════════════════
   FILE UPLOADER & AUDIO INPUT
══════════════════════════════════════════ */
.stFileUploader > div,
div[data-testid="stAudioInput"] > div {
  background: rgba(124,111,255,0.035) !important;
  border: 2px dashed rgba(124,111,255,0.22) !important;
  border-radius: var(--radius) !important;
  transition: var(--transition-medium) !important;
  padding: 2rem !important;
}

.stFileUploader > div:hover,
div[data-testid="stAudioInput"] > div:hover {
  border-color: rgba(124,111,255,0.55) !important;
  background: rgba(124,111,255,0.065) !important;
  box-shadow: 0 0 0 4px rgba(124,111,255,0.07), inset 0 0 32px rgba(124,111,255,0.04) !important;
}

/* Upload zone text */
.stFileUploader label { color: var(--muted-2) !important; font-size: 0.85rem !important; }

/* ══════════════════════════════════════════
   BUTTONS — PRIMARY
══════════════════════════════════════════ */
div.stButton > button {
  background: linear-gradient(135deg, #7C6FFF 0%, #5B4FE8 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 11px 26px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  letter-spacing: 0.01em !important;
  width: 100% !important;
  cursor: pointer !important;
  position: relative !important;
  overflow: hidden !important;
  transition: var(--transition-bounce) !important;
  box-shadow:
    0 4px 20px rgba(124,111,255,0.35),
    0 1px 0 rgba(255,255,255,0.12) inset !important;
}

div.stButton > button::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.14) 0%, transparent 60%);
  border-radius: inherit;
  pointer-events: none;
}

div.stButton > button:hover {
  transform: translateY(-3px) scale(1.008) !important;
  box-shadow:
    0 10px 40px rgba(124,111,255,0.50),
    0 0 0 1px rgba(124,111,255,0.30),
    0 1px 0 rgba(255,255,255,0.18) inset !important;
  background: linear-gradient(135deg, #8F83FF 0%, #6B5EF0 100%) !important;
}

div.stButton > button:active {
  transform: translateY(-1px) scale(0.998) !important;
  box-shadow: 0 4px 16px rgba(124,111,255,0.30) !important;
}

/* Logout / Danger buttons */
div.stButton > button[kind="secondary"],
div.stButton > button:has(span:-webkit-any-link) {
  background: transparent !important;
}

[data-testid="stSidebar"] div.stButton > button {
  background: rgba(239,68,68,0.08) !important;
  color: #FCA5A5 !important;
  border: 1px solid rgba(239,68,68,0.20) !important;
  box-shadow: none !important;
  font-weight: 500 !important;
}

[data-testid="stSidebar"] div.stButton > button:hover {
  background: rgba(239,68,68,0.16) !important;
  border-color: rgba(239,68,68,0.40) !important;
  box-shadow: 0 4px 20px rgba(239,68,68,0.15) !important;
  transform: translateY(-2px) scale(1.002) !important;
}

/* ══════════════════════════════════════════
   DOWNLOAD BUTTON — GREEN CTA
══════════════════════════════════════════ */
div.stDownloadButton > button {
  background: linear-gradient(135deg, #00D68F 0%, #00A86B 100%) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 13px 28px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  letter-spacing: 0.01em !important;
  width: 100% !important;
  position: relative !important;
  overflow: hidden !important;
  transition: var(--transition-bounce) !important;
  box-shadow:
    0 6px 28px rgba(0,214,143,0.35),
    0 1px 0 rgba(255,255,255,0.18) inset !important;
}

div.stDownloadButton > button::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 55%);
  pointer-events: none;
}

div.stDownloadButton > button:hover {
  transform: translateY(-3px) scale(1.010) !important;
  box-shadow:
    0 14px 48px rgba(0,214,143,0.50),
    0 0 0 1px rgba(0,214,143,0.35),
    0 1px 0 rgba(255,255,255,0.22) inset !important;
  background: linear-gradient(135deg, #1FDFA0 0%, #00BE7A 100%) !important;
}

div.stDownloadButton > button:active {
  transform: translateY(0px) scale(0.996) !important;
}

/* ══════════════════════════════════════════
   FORM SUBMIT BUTTONS
══════════════════════════════════════════ */
button[kind="primaryFormSubmit"],
div.stFormSubmitButton > button {
  background: linear-gradient(135deg, #7C6FFF 0%, #5B4FE8 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 12px 26px !important;
  font-weight: 700 !important;
  width: 100% !important;
  transition: var(--transition-bounce) !important;
  box-shadow: 0 4px 20px rgba(124,111,255,0.35) !important;
}

div.stFormSubmitButton > button:hover {
  transform: translateY(-3px) scale(1.008) !important;
  box-shadow: 0 12px 40px rgba(124,111,255,0.50) !important;
}

/* ══════════════════════════════════════════
   DATA EDITOR & DATAFRAME
══════════════════════════════════════════ */
.stDataFrame, [data-testid="stDataFrame"] {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  overflow: hidden !important;
  box-shadow: 0 4px 32px rgba(0,0,0,0.25) !important;
  transition: border-color 0.25s ease !important;
}

.stDataFrame:hover, [data-testid="stDataFrame"]:hover {
  border-color: var(--border-hover) !important;
}

/* Data grid header row */
[data-testid="stDataFrame"] th,
.stDataEditor th {
  background: rgba(124,111,255,0.07) !important;
  color: var(--muted-2) !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid var(--border) !important;
}

[data-testid="stDataFrame"] td,
.stDataEditor td {
  color: var(--text) !important;
  font-size: 0.84rem !important;
  border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}

[data-testid="stDataFrame"] tr:hover td {
  background: rgba(124,111,255,0.05) !important;
}

/* ══════════════════════════════════════════
   EXPANDER PANELS
══════════════════════════════════════════ */
.streamlit-expanderHeader {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--muted-2) !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  transition: var(--transition-fast) !important;
}

.streamlit-expanderHeader:hover {
  background: var(--bg-surface-2) !important;
  border-color: var(--purple-border) !important;
  color: #C4BEFF !important;
}

.streamlit-expanderContent {
  background: rgba(124,111,255,0.025) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
  padding: 1.2rem !important;
}

/* ══════════════════════════════════════════
   ALERTS — INFO / SUCCESS / ERROR / WARNING
══════════════════════════════════════════ */
[data-testid="stAlert"],
div[data-testid="stInfoMessage"],
div[data-testid="stWarningMessage"],
div[data-testid="stErrorMessage"],
div[data-testid="stSuccessMessage"] {
  border-radius: var(--radius-sm) !important;
  border-width: 1px !important;
  border-left-width: 3px !important;
  backdrop-filter: blur(10px) !important;
  font-size: 0.875rem !important;
}

div[data-testid="stInfoMessage"]    { background: rgba(124,111,255,0.07) !important; border-color: rgba(124,111,255,0.35) !important; }
div[data-testid="stSuccessMessage"] { background: rgba(0,214,143,0.07) !important;   border-color: rgba(0,214,143,0.35) !important; }
div[data-testid="stErrorMessage"]   { background: rgba(239,68,68,0.07) !important;   border-color: rgba(239,68,68,0.35) !important; }
div[data-testid="stWarningMessage"] { background: rgba(255,181,71,0.07) !important;  border-color: rgba(255,181,71,0.35) !important; }

/* ══════════════════════════════════════════
   RADIO BUTTONS
══════════════════════════════════════════ */
.stRadio > div {
  display: flex !important;
  gap: 0.5rem !important;
  flex-wrap: wrap !important;
}
.stRadio > div > label {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-xs) !important;
  padding: 8px 18px !important;
  color: var(--muted-2) !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: var(--transition-fast) !important;
}
.stRadio > div > label:hover {
  border-color: var(--purple-border) !important;
  color: #C4BEFF !important;
  background: var(--purple-dim) !important;
}
.stRadio > div [aria-checked="true"] + label,
.stRadio > div > label:has(input:checked) {
  border-color: rgba(124,111,255,0.45) !important;
  background: rgba(124,111,255,0.14) !important;
  color: #D0CBFF !important;
}

/* ══════════════════════════════════════════
   SPINNER
══════════════════════════════════════════ */
.stSpinner > div {
  border-color: rgba(124,111,255,0.3) !important;
  border-top-color: var(--purple) !important;
}

/* ══════════════════════════════════════════
   LOGIN BOX — DEEP GLASSMORPHISM
══════════════════════════════════════════ */
.login-box {
  background: rgba(8,6,20,0.70);
  border: 1px solid rgba(124,111,255,0.22);
  border-radius: 24px;
  padding: 3rem 2.2rem;
  text-align: center;
  box-shadow:
    0 0 0 1px rgba(124,111,255,0.10),
    0 30px 80px rgba(0,0,0,0.65),
    0 0 60px rgba(124,111,255,0.10),
    inset 0 1px 0 rgba(255,255,255,0.08);
  backdrop-filter: blur(32px) saturate(180%);
  -webkit-backdrop-filter: blur(32px) saturate(180%);
  animation: cardReveal 0.6s cubic-bezier(.22,.68,0,1.2) both;
}

/* Login logo */
.login-box .khata-logo {
  width: 68px !important; height: 68px !important;
  font-size: 2.2rem !important;
  border-radius: 20px !important;
  box-shadow:
    0 0 0 1px rgba(124,111,255,0.5),
    0 0 0 6px rgba(124,111,255,0.12),
    0 0 40px rgba(124,111,255,0.45) !important;
}

/* ══════════════════════════════════════════
   EXPORT CARD — GLASSMORPHISM CTA
══════════════════════════════════════════ */
.export-card {
  background: linear-gradient(
    135deg,
    rgba(0,214,143,0.055) 0%,
    rgba(124,111,255,0.055) 50%,
    rgba(0,214,143,0.03) 100%
  );
  border: 1px solid rgba(0,214,143,0.20);
  border-radius: 22px;
  padding: 2.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(16px) !important;
  box-shadow: 0 0 0 1px rgba(0,214,143,0.07), 0 16px 48px rgba(0,0,0,0.25);
  transition: var(--transition-medium);
}
.export-card:hover {
  border-color: rgba(0,214,143,0.35);
  box-shadow: 0 0 0 1px rgba(0,214,143,0.12), 0 24px 64px rgba(0,214,143,0.12);
  transform: translateY(-2px);
}
.export-card::before {
  content: '';
  position: absolute; top: -60px; right: -60px;
  width: 180px; height: 180px;
  background: radial-gradient(circle, rgba(0,214,143,0.12) 0%, transparent 65%);
  pointer-events: none;
}
.export-card .export-icon { font-size: 2.4rem; display: block; margin-bottom: 0.6rem; }
.export-card .export-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem; font-weight: 700;
  color: #FFFFFF; margin-bottom: 0.4rem;
}
.export-card .export-desc {
  font-size: 0.82rem; color: var(--muted-2);
  max-width: 320px; margin: 0 auto;
}

/* ══════════════════════════════════════════
   CUSTOM UI COMPONENTS
══════════════════════════════════════════ */
.section-title {
  font-family: 'Syne', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  letter-spacing: -0.005em;
}
.section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border), transparent);
  margin-left: 0.5rem;
}

.fancy-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border) 30%, var(--border) 70%, transparent);
  margin: 2.2rem 0;
}

.step-row {
  display: flex; align-items: center; gap: 0.85rem;
  margin-bottom: 1.4rem;
  animation: fadeSlideDown 0.45s ease both;
}
.step-num {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--purple-dim);
  border: 1px solid var(--purple-border);
  color: #B4ABFF;
  font-weight: 700; font-size: 0.8rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 0 12px rgba(124,111,255,0.2);
}
.step-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
}

.preview-frame {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: rgba(255,255,255,0.018);
  transition: border-color 0.25s ease;
}
.preview-frame:hover { border-color: var(--border-hover); }

/* ══════════════════════════════════════════
   SCROLLBAR STYLING
══════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(124,111,255,0.25);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(124,111,255,0.45);
}

/* ══════════════════════════════════════════
   TYPOGRAPHY HIERARCHY
══════════════════════════════════════════ */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; color: #FFFFFF !important; letter-spacing: -0.02em !important; }
h1 { font-size: 2rem !important; font-weight: 800 !important; }
h2 { font-size: 1.4rem !important; font-weight: 700 !important; }
h3 { font-size: 1.1rem !important; font-weight: 700 !important; }
p, li, span { color: var(--text) !important; }
strong, b { color: #FFFFFF !important; font-weight: 600 !important; }

code {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.8rem !important;
  background: rgba(124,111,255,0.12) !important;
  border: 1px solid rgba(124,111,255,0.20) !important;
  border-radius: 5px !important;
  padding: 2px 7px !important;
  color: #B4ABFF !important;
}

/* ══════════════════════════════════════════
   MARKDOWN TEXT INSIDE FORMS
══════════════════════════════════════════ */
.stMarkdown p, .stMarkdown span { color: var(--text) !important; }
.stMarkdown strong { color: #FFFFFF !important; font-weight: 600 !important; }

/* ══════════════════════════════════════════
   COLUMN GAPS — breathing room
══════════════════════════════════════════ */
[data-testid="column"] { padding: 0 0.4rem !important; }

/* ══════════════════════════════════════════
   Z-INDEX & LAYERING CLEANUP
══════════════════════════════════════════ */
.main .block-container { position: relative; z-index: 1; }

</style>
<div class="bg-mesh"><span></span><span></span><span></span></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. STATE MANAGEMENT (LOGIN & PROFILE SETTINGS)
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "admin_user" not in st.session_state: st.session_state.admin_user = "aryan"
if "admin_pass" not in st.session_state: st.session_state.admin_pass = "admin123"
if "company_name" not in st.session_state: st.session_state.company_name = "Stepout Studios"
if "company_logo" not in st.session_state: st.session_state.company_logo = None

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""
        <div class="login-box">
            <div class="khata-logo" style="margin: 0 auto 1.5rem auto; width: 75px; height: 75px; font-size: 2.8rem;">🔒</div>
            <div class="khata-title" style="font-size: 2.4rem !important; margin-bottom: 0.5rem; line-height:1.2;">Secure Portal</div>
            <div class="khata-sub" style="margin-bottom: 2.5rem; font-size: 0.95rem;">Authorized Personnel Only</div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            entered_user = st.text_input("Admin Username", placeholder="Enter your ID")
            entered_pass = st.text_input("Security PIN", type="password", placeholder="Enter your Password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("🔓 Authenticate Access", use_container_width=True):
                if entered_user == st.session_state.admin_user and entered_pass == st.session_state.admin_pass:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Access Denied! Incorrect Credentials.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() 

# ─────────────────────────────────────────────
# 3. SIDEBAR (THE 3-LINE MENU) & PROFILE SETTINGS
# ─────────────────────────────────────────────
with st.sidebar:
    if st.session_state.company_logo:
        logo_display = f"<img src='{st.session_state.company_logo}' style='width: 80px; height: 80px; border-radius: 20px; object-fit: cover; box-shadow: 0 0 25px rgba(124,111,255,0.4); border: 2px solid rgba(124,111,255,0.3); margin-bottom: 1rem;'>"
    else:
        logo_display = "<div class='khata-logo' style='margin: 0 auto 1rem auto; width: 60px; height: 60px; font-size: 2rem;'>🏢</div>"

    st.markdown(f"<div style='text-align: center; margin-top: 1rem;'>{logo_display}<h2 style='color: white; font-family: Syne, sans-serif; font-size: 1.5rem; font-weight:800; margin-bottom:0;'>{st.session_state.company_name}</h2><div style='color: #A89EFF; font-size: 0.8rem; letter-spacing:1px; margin-bottom: 2.5rem; text-transform:uppercase; font-weight:600;'>Master Admin Dashboard</div></div>", unsafe_allow_html=True)
    
    with st.expander("⚙️ System Preferences", expanded=False):
        with st.form("settings_form"):
            st.markdown("**Update Profile Details**")
            new_logo = st.file_uploader("Upload Company Logo (Optional)", type=['png', 'jpg', 'jpeg'])
            new_comp = st.text_input("Workspace Name", value=st.session_state.company_name)
            new_user = st.text_input("Admin ID", value=st.session_state.admin_user)
            new_pass = st.text_input("New Password", type="password", value=st.session_state.admin_pass)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Save Configuration", use_container_width=True):
                if new_logo is not None:
                    base64_image = base64.b64encode(new_logo.getvalue()).decode("utf-8")
                    st.session_state.company_logo = f"data:image/png;base64,{base64_image}"
                st.session_state.company_name = new_comp
                st.session_state.admin_user = new_user
                st.session_state.admin_pass = new_pass
                st.success("Preferences Updated!")
                st.rerun()
                
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Terminate Session", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ─────────────────────────────────────────────
# 4. CLIENT SETUP
# ─────────────────────────────────────────────
AI_API_KEY   = st.secrets["AI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

ai_client = genai.Client(api_key=AI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "scanned_data" not in st.session_state: st.session_state.scanned_data = None
if "voice_scanned_data" not in st.session_state: st.session_state.voice_scanned_data = None

try:
    response = supabase.table("invoices").select("*").order("id", desc=True).execute()
    db_data = response.data
except Exception:
    db_data = []

# ─────────────────────────────────────────────
# 5. DYNAMIC HERO HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="khata-topbar">
  <div class="khata-brand">
    <div class="khata-logo">⚡</div>
    <div>
      <div class="khata-title">{st.session_state.company_name}</div>
      <div class="khata-sub">KhataAI Powered • CA ERP System</div>
    </div>
  </div>
  <div class="khata-pill">v5.0 PRO</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📸 Vision Scanner", "🎙️ Voice Entry", "📊 Dashboard & PDF", "⚙️ Tally Sync", "👨‍💼 Ask CA Sahab"])

# ══════════════════════════════════════════════
# TAB 1 — SCAN & EDIT
# ══════════════════════════════════════════════
with tab1:
    col_upload, col_preview = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<div class="step-row"><div class="step-num">1</div><div class="step-label">Upload Physical Bill / GST Invoice</div></div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop your GST invoice here", type=["jpg","png","jpeg"], label_visibility="collapsed")

        if uploaded_file is not None and st.session_state.scanned_data is None:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="step-row"><div class="step-num">2</div><div class="step-label">Initiate Deep Extraction</div></div>', unsafe_allow_html=True)
            if st.button("🚀 Process with Gemini AI", use_container_width=True):
                with st.spinner("Neural network analyzing document structure..."):
                    import time
                    try:
                        img = Image.open(uploaded_file)
                        prompt = """
                        You are an expert Data Extractor for an Indian CA.
                        Extract details from the invoice including Vendor's Full Address and Bank Details.
                        Determine if this is a "Purchase" invoice (goods bought) or "Sales" invoice (goods sold).
                        Return ONLY a valid JSON:
                        {
                          "voucher_type": "Purchase", 
                          "vendor_name": "...", "gst_number": "...", "vendor_address": "...", "bank_details": "...",
                          "invoice_number": "...", "invoice_date": "DD-MM-YYYY",
                          "base_price": 0.00, "cgst_amount": 0.00, "sgst_amount": 0.00, "igst_amount": 0.00, "total_amount": 0.00, "category": "...",
                          "line_items": [ {"item_name": "...", "hsn_code": "...", "quantity": 0.0, "unit": "...", "rate": 0.0, "amount": 0.0} ]
                        }
                        """
                        max_retries = 5 # 🚀 Retries badha diye
                        for attempt in range(max_retries):
                            try:
                                ai_resp = ai_client.models.generate_content(model='gemini-2.0-flash', contents=[img, prompt])
                                raw_text = ai_resp.text.strip().replace("```json","").replace("```","").strip()
                                st.session_state.scanned_data = json.loads(raw_text)
                                st.rerun()
                                break
                            except Exception as api_e:
                                if "503" in str(api_e) or "high demand" in str(api_e).lower() or "429" in str(api_e):
                                    if attempt < max_retries - 1:
                                        # 🚀 Exponential Backoff: 8s, 16s, 24s...
                                        wait_time = (attempt + 1) * 8 
                                        st.warning(f"⏳ Server traffic is high. Auto-retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                                        time.sleep(wait_time)
                                    else:
                                        st.error("❌ Servers are currently overloaded. Please try again after a minute.")
                                else:
                                    st.error(f"❌ API Error: {api_e}")
                                    break
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {e}")

    with col_preview:
        if uploaded_file is not None:
            st.markdown('<div class="section-title">📄 Document Preview</div>', unsafe_allow_html=True)
            st.markdown('<div class="preview-frame">', unsafe_allow_html=True)
            st.image(uploaded_file, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.scanned_data is not None:
        data = st.session_state.scanned_data
        st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="step-row"><div class="step-num">3</div><div class="step-label">Validate & Push to Database</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">✏️ AI Extracted Payload</div>', unsafe_allow_html=True)

        with st.form("edit_form"):
            st.markdown("**🧾 Voucher Matrix**")
            v_type_val = data.get("voucher_type", "Purchase")
            v_idx = 1 if "sale" in v_type_val.lower() else 0
            v_type = st.selectbox("Voucher Type (Auto-detected)", ["Purchase", "Sales"], index=v_idx)
            
            st.markdown("<br>**🏢 Entity Details**", unsafe_allow_html=True)
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1: v_name = st.text_input("Entity Name",  value=data.get("vendor_name",""))
            with r1c2: v_gst  = st.text_input("GST Identification",   value=data.get("gst_number",""))
            with r1c3: v_cat  = st.text_input("Ledger Category",     value=data.get("category",""))

            r2c1, r2c2 = st.columns(2)
            with r2c1: v_addr = st.text_input("Registered Address", value=data.get("vendor_address",""))
            with r2c2: v_bank = st.text_input("Banking Info", value=data.get("bank_details",""))

            r3c1, r3c2 = st.columns(2)
            with r3c1: v_inv_no = st.text_input("Invoice ID", value=data.get("invoice_number",""))
            with r3c2: v_date   = st.text_input("Timestamp",   value=data.get("invoice_date",""))

            st.markdown("<br>**📦 Inventory Line Items**", unsafe_allow_html=True)
            raw_items = data.get("line_items", [])
            if not raw_items: raw_items = [{"item_name":"","hsn_code":"","quantity":0.0,"unit":"","rate":0.0,"amount":0.0}]
            edited_df = st.data_editor(pd.DataFrame(raw_items), num_rows="dynamic", use_container_width=True)

            st.markdown("<br>**💰 Financials & Taxation**", unsafe_allow_html=True)
            a1, a2, a3, a4, a5 = st.columns(5)
            with a1: v_base  = st.number_input("Taxable Value ₹", value=float(data.get("base_price",0.0)))
            with a2: v_cgst  = st.number_input("CGST ₹",       value=float(data.get("cgst_amount",0.0)))
            with a3: v_sgst  = st.number_input("SGST ₹",       value=float(data.get("sgst_amount",0.0)))
            with a4: v_igst  = st.number_input("IGST ₹",       value=float(data.get("igst_amount",0.0)))
            with a5: v_total = st.number_input("Grand Total ₹",      value=float(data.get("total_amount",0.0)))

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ Secure Database Commit", use_container_width=True):
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
                st.success(f"✅ Transaction log secured in cloud storage!")
                st.rerun()

# ══════════════════════════════════════════════
# TAB 2: 🎙️ VOICE BILLING (FIXED VERSION)
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🎙️ Neural Voice Capture</div>', unsafe_allow_html=True)
    st.info("💡 Pro Tip: Speak naturally. e.g., 'Sold 10 pipes to Manoj Enterprises at 50 rupees each with 18% GST. His GST is 07AAAA...'")

    audio_value = st.audio_input("Initialize Voice Recording", label_visibility="collapsed")

    if audio_value is not None and st.session_state.voice_scanned_data is None:
        if st.button("🚀 Transcribe & Generate", use_container_width=True):
            with st.spinner("Running acoustic models and calculating GST..."):
                import time
                max_retries = 4 # 🚀 Retries set to 4
                for attempt in range(max_retries):
                    try:
                        audio_prompt = """
                        Listen to this audio. You are an expert Indian CA.
                        Determine if the user is BUYING (Purchase) or SELLING (Sales).
                        Extract the party name, GST number (if mentioned), Address, items, quantities and rates.
                        If GST percentage is mentioned, calculate the Base Price, CGST & SGST (if local) or IGST (if interstate).
                        Return ONLY a valid JSON:
                        {
                          "voucher_type": "Purchase",
                          "vendor_name": "...", "gst_number": "...", "vendor_address": "...", "bank_details": "...",
                          "base_price": 0.0, "cgst_amount": 0.0, "sgst_amount": 0.0, "igst_amount": 0.0, "total_amount": 0.0,
                          "line_items": [{"item_name": "...", "quantity": 0.0, "unit": "Nos", "rate": 0.0, "amount": 0.0}]
                        }
                        """
                        resp = ai_client.models.generate_content(
                            model='gemini-2.0-flash', # Model fixed for stability
                            contents=[types.Part.from_bytes(data=audio_value.getvalue(), mime_type='audio/wav'), audio_prompt]
                        )
                        clean_json = resp.text.strip().replace("```json","").replace("```","").strip()
                        st.session_state.voice_scanned_data = json.loads(clean_json)
                        st.rerun()
                        break
                    except Exception as e:
                        if "503" in str(e) or "high demand" in str(e).lower() or "429" in str(e):
                            if attempt < max_retries - 1:
                                # 🚀 Long Wait for Voice: 10s, 15s...
                                wait_time = 10 + (attempt * 5) 
                                st.warning(f"⏳ Server is busy. Auto-retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                                time.sleep(wait_time)
                            else:
                                st.error("❌ Servers are currently overloaded. Please try again after a minute.")
                        else:
                            st.error(f"❌ Audio processing error: {e}")
                            break

    if st.session_state.voice_scanned_data is not None:
        v_data = st.session_state.voice_scanned_data
        st.markdown('<div class="fancy-divider"></div><div class="section-title">✏️ Validate Audio Transcript</div>', unsafe_allow_html=True)

        st.markdown("**🏢 Party Info (Auto-Fetch)**")
        if "current_gst" not in st.session_state: st.session_state.current_gst = v_data.get("gst_number", "")
        if "fetched_name" not in st.session_state: st.session_state.fetched_name = v_data.get("vendor_name", "")
        if "fetched_address" not in st.session_state: st.session_state.fetched_address = v_data.get("vendor_address", "")

        g1, g2 = st.columns([3, 1])
        with g1:
            voice_gst = st.text_input("GST Number", value=st.session_state.current_gst)
        with g2:
            st.markdown("<br>", unsafe_allow_html=True)
            fetch_btn = st.button("🔍 Fetch API", use_container_width=True)

        if fetch_btn and voice_gst:
            with st.spinner("Fetching from Server..."):
                dummy_db = {
                    "10AABCU9355J1Z9": {"name": "Jai Shree Ram Packaging", "address": "Uttar Pradesh, India"},
                    "07AABCB1234C1Z1": {"name": "Stepout Studios", "address": "Delhi, India"}
                }
                api_key = "2bc451a563msh61eee8c6a8a1ef0p1586c6jsnb626801c0c68"
                url = "https://gst-verification.p.rapidapi.com/v1/verify"
                headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "gst-verification.p.rapidapi.com"}
                
                api_success = False
                try:
                    res = requests.get(url, headers=headers, params={"gstin": voice_gst}, timeout=3)
                    if res.status_code == 200:
                        d = res.json()
                        st.session_state.fetched_name = d.get('data', {}).get('tradeName', '')
                        st.session_state.fetched_address = d.get('data', {}).get('pradr', {}).get('adr', '')
                        api_success = True
                except:
                    pass

                if not api_success and voice_gst in dummy_db:
                    st.session_state.fetched_name = dummy_db[voice_gst]["name"]
                    st.session_state.fetched_address = dummy_db[voice_gst]["address"]
                    api_success = True

                if api_success:
                    st.success(f"✅ Auto-filled: {st.session_state.fetched_name}")
                else:
                    st.warning("⚠️ API failed. Please enter manually.")

        with st.form("edit_voice_form"):
            st.markdown("**🧾 Transaction Details**")
            c0, c1, c2 = st.columns([1, 2, 1])
            with c0:
                v_type_val = v_data.get("voucher_type", "Sales")
                v_idx = 1 if "sale" in v_type_val.lower() else 0
                voice_type = st.selectbox("Operation", ["Purchase", "Sales"], index=v_idx)
            with c1: voice_vendor = st.text_input("Counterparty", value=v_data.get("vendor_name", "Local Party"))
            with c2: voice_date = st.text_input("Timestamp", value="2026-04-09")

            r1, r2 = st.columns(2)
            with r1: final_vendor_name = st.text_input("Legal Name", value=st.session_state.fetched_name)
            with r2: final_address = st.text_input("Registered Address", value=st.session_state.fetched_address)

            voice_bank = st.text_input("Bank / Payment Details", value=v_data.get("bank_details", ""))

            st.markdown("**📦 Detected Inventory Items**")
            voice_edited_df = st.data_editor(pd.DataFrame(v_data.get("line_items", [])), num_rows="dynamic", use_container_width=True)

            st.markdown("**💰 Financials & Taxation**")
            t1, t2, t3, t4, t5 = st.columns(5)
            with t1: v_base  = st.number_input("Base Value ₹", value=float(v_data.get("base_price", 0.0)))
            with t2: v_cgst  = st.number_input("CGST ₹",       value=float(v_data.get("cgst_amount", 0.0)))
            with t3: v_sgst  = st.number_input("SGST ₹",       value=float(v_data.get("sgst_amount", 0.0)))
            with t4: v_igst  = st.number_input("IGST ₹",       value=float(v_data.get("igst_amount", 0.0)))
            with t5: voice_total = st.number_input("Gross Amount ₹", value=float(v_data.get("total_amount", 0.0)))

            if st.form_submit_button("✅ Commit Voice Entry", use_container_width=True):
                voice_final_data = {
                    "voucher_type": voice_type, "vendor_name": final_vendor_name, "invoice_date": voice_date,
                    "gst_number": voice_gst, "vendor_address": final_address, "bank_details": voice_bank,
                    "base_price": v_base, "cgst_amount": v_cgst, "sgst_amount": v_sgst,
                    "igst_amount": v_igst, "total_gst_amount": v_cgst + v_sgst + v_igst,
                    "total_amount": voice_total, "category": "Voice Entry",
                    "line_items": voice_edited_df.to_dict(orient='records')
                }
                supabase.table("invoices").insert(voice_final_data).execute()
                st.session_state.voice_scanned_data = None
                st.session_state.fetched_name = ""
                st.session_state.fetched_address = ""
                st.session_state.current_gst = ""
                st.success("✅ Voice transaction secured!")
                st.rerun() 

# ══════════════════════════════════════════════
# TAB 3 — ANALYTICS, MANAGE & PDF PRINT
# ══════════════════════════════════════════════
with tab3:
    total_bills = len(db_data)
    total_sales = sum([float(x.get("total_amount") or 0) for x in db_data if x.get("voucher_type") == "Sales"])
    total_purch = sum([float(x.get("total_amount") or 0) for x in db_data if x.get("voucher_type", "Purchase") == "Purchase"])

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1: st.markdown(f'<div class="metric-card purple"><span class="metric-icon">📄</span><div class="metric-label">Ledger Entries</div><div class="metric-value purple">{total_bills}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card green"><span class="metric-icon">📈</span><div class="metric-label">Gross Revenue</div><div class="metric-value green">₹{total_sales:,.0f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card amber"><span class="metric-icon">📉</span><div class="metric-label">Total Outflow</div><div class="metric-value amber">₹{total_purch:,.0f}</div></div>', unsafe_allow_html=True)

    if total_bills > 0:
        st.markdown('<br><div class="section-title">📋 Secure Ledger Records</div>', unsafe_allow_html=True)
        display_df = pd.DataFrame(db_data)
        def get_item_names(row):
            items = row.get('line_items')
            if isinstance(items, list) and len(items) > 0: return ", ".join([str(i.get('item_name','')) for i in items if i.get('item_name')])
            elif row.get('product_names'): return str(row.get('product_names'))
            return "No Items"
        display_df['Items_Summary'] = display_df.apply(get_item_names, axis=1)
        display_df.insert(0, 'Sr_No', range(1, len(display_df)+1))
        
        if 'voucher_type' not in display_df.columns: display_df['voucher_type'] = 'Purchase'
        cols = ['Sr_No', 'voucher_type'] + [c for c in display_df.columns if c not in ['Sr_No', 'voucher_type', 'id', 'line_items', 'product_names', 'vendor_address', 'bank_details']]
        
        st.dataframe(display_df[cols], use_container_width=True, hide_index=True)

        def clean_text(text):
            if pd.isna(text) or text is None: return ""
            return str(text).encode('latin-1', 'replace').decode('latin-1')

        def create_pdf_bill(bill_data):
            c_vendor_name = clean_text(bill_data.get('vendor_name', 'Unknown'))
            c_vendor_address = clean_text(bill_data.get('vendor_address', 'N/A'))
            c_gst_number = clean_text(bill_data.get('gst_number', 'N/A'))
            c_invoice_number = clean_text(bill_data.get('invoice_number', 'N/A'))
            c_invoice_date = clean_text(bill_data.get('invoice_date', 'N/A'))
            c_category = clean_text(bill_data.get('category', 'General'))
            c_bank_details = clean_text(bill_data.get('bank_details', 'N/A'))
            c_voucher_type = clean_text(bill_data.get('voucher_type', 'INVOICE')).upper()
            c_comp_name = clean_text(st.session_state.company_name)

            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            pdf.rect(5, 5, 200, 287)
            
            pdf.set_font("Arial", 'B', 18)
            pdf.cell(190, 12, txt=f"TAX {c_voucher_type}", ln=True, align='C')
            pdf.line(5, 17, 205, 17)
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(110, 6, txt="Billed To (Party Details):", border=0, ln=0)
            pdf.cell(80, 6, txt="Invoice Details:", border=0, ln=1)
            
            pdf.set_font("Arial", '', 10)
            x_y_start = pdf.get_y()
            pdf.multi_cell(100, 5, txt=f"Name: {c_vendor_name}\nAddress: {c_vendor_address}\nGSTIN: {c_gst_number}")
            pdf.set_xy(120, x_y_start)
            pdf.multi_cell(80, 5, txt=f"Invoice No: {c_invoice_number}\nDate: {c_invoice_date}\nCategory: {c_category}")
            
            pdf.ln(8)
            pdf.line(5, pdf.get_y(), 205, pdf.get_y())
            pdf.ln(2)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(15, 8, "S.No", 1, 0, 'C')
            pdf.cell(85, 8, "Description of Goods", 1, 0, 'C')
            pdf.cell(25, 8, "Qty", 1, 0, 'C')
            pdf.cell(30, 8, "Rate", 1, 0, 'C')
            pdf.cell(35, 8, "Amount", 1, 1, 'C')
            
            pdf.set_font("Arial", '', 10)
            line_items = bill_data.get('line_items', [])
            base_total = 0
            if isinstance(line_items, list):
                for idx, item in enumerate(line_items):
                    i_name = clean_text(item.get('item_name', ''))[:42]
                    qty_str = clean_text(f"{item.get('quantity', 0)} {item.get('unit', '')}")
                    rate = float(item.get('rate', 0))
                    amt = float(item.get('amount', 0))
                    base_total += amt
                    
                    pdf.cell(15, 8, str(idx+1), 'LR', 0, 'C')
                    pdf.cell(85, 8, i_name, 'LR', 0, 'L')
                    pdf.cell(25, 8, qty_str, 'LR', 0, 'C')
                    pdf.cell(30, 8, f"{rate:,.2f}", 'LR', 0, 'R')
                    pdf.cell(35, 8, f"{amt:,.2f}", 'LR', 1, 'R')
            
            pdf.cell(190, 0, "", 'T', 1) 
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(155, 8, "Taxable Amount", 1, 0, 'R')
            base_val = float(bill_data.get('base_price') or base_total)
            pdf.cell(35, 8, f"{base_val:,.2f}", 1, 1, 'R')
            
            cgst = float(bill_data.get('cgst_amount') or 0)
            sgst = float(bill_data.get('sgst_amount') or 0)
            igst = float(bill_data.get('igst_amount') or 0)
            
            if cgst > 0:
                pdf.cell(155, 8, "Add: CGST", 1, 0, 'R')
                pdf.cell(35, 8, f"{cgst:,.2f}", 1, 1, 'R')
            if sgst > 0:
                pdf.cell(155, 8, "Add: SGST", 1, 0, 'R')
                pdf.cell(35, 8, f"{sgst:,.2f}", 1, 1, 'R')
            if igst > 0:
                pdf.cell(155, 8, "Add: IGST", 1, 0, 'R')
                pdf.cell(35, 8, f"{igst:,.2f}", 1, 1, 'R')
                
            total_amt = float(bill_data.get('total_amount') or 0)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(155, 10, "Grand Total (Rs.)", 1, 0, 'R')
            pdf.cell(35, 10, f"{total_amt:,.2f}", 1, 1, 'R')
            
            pdf.ln(8)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(100, 6, "Bank Details:", 0, 1)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(100, 5, txt=f"{c_bank_details}\n\nTerms: E.& O.E.\n1. Goods once sold will not be taken back.")
            
            pdf.set_xy(130, pdf.get_y() - 15)
            pdf.cell(60, 6, f"For {c_comp_name}", 0, 1, 'C')
            pdf.line(140, pdf.get_y()+8, 190, pdf.get_y()+8)
            
            pdf_out = pdf.output(dest='S')
            return pdf_out.encode('latin-1') if isinstance(pdf_out, str) else pdf_out

        col_print, col_delete = st.columns(2, gap="large")
        with col_print:
            with st.expander("🖨️ PDF Generation Matrix"):
                pdf_options = {f"Sr {idx+1} | {row.get('voucher_type','Purchase')} | {row.get('vendor_name','Unknown')}": row for idx, row in enumerate(db_data)}
                selected_pdf_key = st.selectbox("Select entity to compile:", options=list(pdf_options.keys()), key="pdf_select")
                if selected_pdf_key:
                    selected_row_data = pdf_options[selected_pdf_key]
                    pdf_bytes = create_pdf_bill(selected_row_data)
                    st.download_button(
                        label="📥 Generate & Download PDF",
                        data=pdf_bytes,
                        file_name=f"Invoice_{clean_text(selected_row_data.get('vendor_name', 'Bill'))}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

        with col_delete:
            with st.expander("🗑️ Destructive Actions (Admin Only)"):
                bill_options = {f"Sr {idx+1} | {row.get('voucher_type','Purchase')} | {row.get('vendor_name','Unknown')}": row['id'] for idx, row in enumerate(db_data)}
                selected_bill = st.selectbox("Select record to purge:", options=list(bill_options.keys()))
                if st.button("❌ Purge Selected Record", use_container_width=True):
                    supabase.table("invoices").delete().eq("id", bill_options[selected_bill]).execute()
                    st.rerun()

# ══════════════════════════════════════════════
# TAB 4 — TALLY EXPORT
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">⚙️ Tally ERP Integration</div>', unsafe_allow_html=True)
    if len(db_data) > 0:
        export_mode = st.radio("Export Protocol:", ["📤 Full Database Export", "✅ Selective Batch Export"], horizontal=True)
        selected_invoices = db_data 
        if export_mode == "✅ Selective Batch Export":
            bill_options = {f"Sr {idx+1} | {row.get('voucher_type','Purchase')} | {row.get('vendor_name','Unknown')} | ₹{row.get('total_amount',0)}": row for idx, row in enumerate(db_data)}
            selected_keys = st.multiselect("Select transactions for batch:", options=list(bill_options.keys()), default=list(bill_options.keys()))
            selected_invoices = [bill_options[k] for k in selected_keys]
    else:
        selected_invoices = []

    def generate_tally_xml(invoices_data):
        xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>All Masters</REPORTNAME>\n</REQUESTDESC>\n<REQUESTDATA>\n"
        parties_data = {}
        unique_items = set()

        for inv in invoices_data:
            p_name = str(inv.get('vendor_name') or 'Unknown').replace("&","&amp;")
            if p_name not in parties_data:
                parties_data[p_name] = {'group': 'Sundry Debtors' if inv.get('voucher_type') == 'Sales' else 'Sundry Creditors', 'gst': str(inv.get('gst_number') or '').replace("&","&amp;"), 'address': str(inv.get('vendor_address') or '').replace("&","&amp;")}
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
            total_amt = float(inv.get('total_amount') or 0)
            party_is_debit = "Yes" if v_type == "Sales" else "No"
            party_amt = f"-{total_amt}" if v_type == "Sales" else f"{total_amt}"
            main_ledger = "Sales A/c" if v_type == "Sales" else "Purchase A/c"
            main_is_debit = "No" if v_type == "Sales" else "Yes"

            xml_data += f'<TALLYMESSAGE xmlns:UDF="TallyUDF">\n<VOUCHER VCHTYPE="{v_type}" ACTION="Create">\n<DATE>{raw_date}</DATE>\n<REFERENCE>{v_inv_no}</REFERENCE>\n<VOUCHERTYPENAME>{v_type}</VOUCHERTYPENAME>\n<PARTYLEDGERNAME>{v_name}</PARTYLEDGERNAME>\n'
            xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{v_name}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>{party_is_debit}</ISDEEMEDPOSITIVE>\n<AMOUNT>{party_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

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

            for tax_type, amt in [("CGST", float(inv.get("cgst_amount") or 0)), ("SGST", float(inv.get("sgst_amount") or 0)), ("IGST", float(inv.get("igst_amount") or 0))]:
                if amt > 0:
                    t_amt = f"{amt}" if v_type == "Sales" else f"-{amt}"
                    tax_ledger = f"Output {tax_type}" if v_type == "Sales" else f"Input {tax_type}"
                    xml_data += f'<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{tax_ledger}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>{main_is_debit}</ISDEEMEDPOSITIVE>\n<AMOUNT>{t_amt}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n'

            xml_data += '</VOUCHER>\n</TALLYMESSAGE>\n'
        xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
        return xml_data

    ec1, ec2, ec3 = st.columns(3, gap="medium")
    with ec1: st.markdown("""<div class="metric-card purple center"><span class="metric-icon">🏦</span><div class="metric-label">Target Format</div><div style="color:#A89EFF;font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;">Tally ERP 9</div></div>""", unsafe_allow_html=True)
    with ec2: st.markdown(f"""<div class="metric-card green center"><span class="metric-icon">📦</span><div class="metric-label">Compiled Batch</div><div style="color:#6EE7B7;font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;">{len(selected_invoices)} Records</div></div>""", unsafe_allow_html=True)
    with ec3: st.markdown("""<div class="metric-card amber center"><span class="metric-icon">⚡</span><div class="metric-label">System Status</div><div style="color:#FCD34D;font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;">Ready for Link</div></div>""", unsafe_allow_html=True)

    if len(selected_invoices) > 0:
        st.markdown("""<br><div class="export-card"><span class="export-icon">📥</span><div class="export-title">Download XML Payload</div><div class="export-desc">Auto-creates ledgers, registers GST, and populates inventory seamlessly.</div></div><br>""", unsafe_allow_html=True)
        st.download_button(label="📥 Initialize Download (KhataAI_ERP.xml)", data=generate_tally_xml(selected_invoices), file_name="KhataAI_ERP_Import.xml", mime="application/xml", use_container_width=True)


# ══════════════════════════════════════════════
# 👨‍💼 TAB 5 — CA SAHAB WITH VOICE INPUT + MALE TTS
# ══════════════════════════════════════════════
with tab5:
    import hashlib
    import asyncio
    import edge_tts

    async def generate_male_voice(text: str) -> bytes:
        """Microsoft ka solid male Hindi voice"""
        voice = "hi-IN-MadhurNeural"  # Ekdam solid male voice
        communicate = edge_tts.Communicate(text, voice)
        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        audio_buffer.seek(0)
        return audio_buffer.read()

    def get_male_audio(text: str) -> bytes:
        """Sync wrapper for async TTS"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(generate_male_voice(text))
            loop.close()
            return result
        except Exception as e:
            return None

    st.markdown('<div class="section-title">👨‍💼 CA Sahab - Aapka Business Partner</div>', unsafe_allow_html=True)

    # Reset button
    if st.button("New Discussion 🔄"):
        st.session_state.ca_history = []
        st.session_state.last_query = ""
        st.session_state.last_audio_hash = ""
        st.rerun()

    # Init history
    if "ca_history" not in st.session_state or not st.session_state.ca_history:
        st.session_state.ca_history = [{"role": "assistant", "text": "Arre Aryan bhai, swagat hai! Tension mat lo, CA Sahab aa gaye hain. Boliye, aaj kaunsa bada kaand... mera matlab hai, kaunsa bada business deal set karna hai? 😎"}]

    # Chat history display
    for msg in st.session_state.ca_history:
        with st.chat_message(msg["role"]):
            st.markdown(f'<div style="font-family: \'DM Sans\', sans-serif; font-size: 1rem;">{msg["text"]}</div>', unsafe_allow_html=True)

    # ── INPUT SECTION ──
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎤 Apna Sawal Puchho</div>', unsafe_allow_html=True)

    input_mode = st.radio("Input Mode:", ["⌨️ Type", "🎙️ Voice"], horizontal=True)

    final_query = None

    # ── TEXT INPUT ──
    if input_mode == "⌨️ Type":
        final_query = st.chat_input("Apna solid sawal yahan likho...")

    # ── VOICE INPUT ──
    else:
        st.info("🎙️ Mic press karo, apna sawal bolo, phir 'Transcribe' dabao")
        voice_question = st.audio_input("Yahan bolo apna sawal:", label_visibility="collapsed")

        if voice_question is not None:
            if st.button("🔍 Transcribe & Ask CA Sahab", use_container_width=True):
                with st.spinner("Awaaz sun raha hoon... 👂"):
                    try:
                        # Groq Whisper se transcribe
                        transcription = groq_client.audio.transcriptions.create(
                            file=("question.wav", voice_question.getvalue(), "audio/wav"),
                            model="whisper-large-v3",
                            language="hi",  # Hindi priority, English bhi handle karega
                            response_format="text"
                        )
                        final_query = str(transcription).strip()
                        st.success(f"✅ Suna mujhe: **{final_query}**")
                    except Exception as e:
                        st.error(f"❌ Transcription fail: {str(e)[:100]}")

    # ── PROCESS QUERY ──
    if final_query and final_query.strip():
        # Duplicate prevention
        if "last_query" not in st.session_state:
            st.session_state.last_query = ""

        if st.session_state.last_query != final_query.strip():
            st.session_state.last_query = final_query.strip()
            st.session_state.ca_history.append({"role": "user", "text": final_query})

            with st.chat_message("user"):
                st.markdown(final_query)

            with st.chat_message("assistant"):
                with st.spinner("CA Sahab dimaag laga rahe hain... 🧠"):
                    try:
                        system_instructions = """
                        You are 'CA Sahab'. You are NOT a robot. You are a high-level, elite Indian Chartered Accountant who talks like a mentor and a friend.
                        - Use 'Hinglish' (Hindi in English script).
                        - Be confident, solid, and epic. Use words like 'Bhai', 'Bindass', 'Solid', 'System'.
                        - Don't give boring textbook answers. Give practical, 'dhandha' oriented advice.
                        - Keep it human. If the user asks something simple, reply with wit.
                        - IMPORTANT: Never start your answer the same way. Be fresh every time!
                        """

                        # Build full conversation history for context
                        messages_for_api = [{"role": "system", "content": system_instructions}]
                        for h in st.session_state.ca_history[:-1]:  # Exclude latest user msg (already added)
                            messages_for_api.append({
                                "role": h["role"] if h["role"] != "assistant" else "assistant",
                                "content": h["text"]
                            })
                        messages_for_api.append({"role": "user", "content": final_query})

                        response = groq_client.chat.completions.create(
                            messages=messages_for_api,
                            model="llama-3.3-70b-versatile",
                            temperature=0.85,
                            top_p=0.9,
                            max_tokens=1024
                        )
                        ans = response.choices[0].message.content
                        st.markdown(f'<div style="line-height: 1.6;">{ans}</div>', unsafe_allow_html=True)
                        st.session_state.ca_history.append({"role": "assistant", "text": ans})

                        # ── MALE VOICE OUTPUT ──
                        st.markdown("---")
                        st.markdown("**🔊 CA Sahab bol rahe hain...**")

                        current_hash = hashlib.md5(ans.encode()).hexdigest()
                        if "last_audio_hash" not in st.session_state:
                            st.session_state.last_audio_hash = ""

                        if st.session_state.last_audio_hash != current_hash:
                            with st.spinner("🎙️ Awaaz taiyaar ho rahi hai..."):
                                # Clean text for TTS — remove markdown symbols
                                clean_ans = ans.replace("*", "").replace("#", "").replace("`", "").replace("_", "").strip()
                                if len(clean_ans) > 3000:
                                    clean_ans = clean_ans[:3000] + "..."

                                audio_bytes = get_male_audio(clean_ans)

                                if audio_bytes and len(audio_bytes) > 1000:
                                    st.audio(audio_bytes, format="audio/mp3", autoplay=False)
                                    st.session_state.last_audio_hash = current_hash
                                    st.success("✅ Solid awaaz taiyaar! Play karo. 🎙️")
                                else:
                                    # Fallback to gTTS if edge_tts fails
                                    try:
                                        tts = gTTS(text=clean_ans[:2000], lang='hi', slow=False)
                                        fallback_buffer = io.BytesIO()
                                        tts.write_to_fp(fallback_buffer)
                                        fallback_buffer.seek(0)
                                        st.audio(fallback_buffer, format='audio/mp3', autoplay=False)
                                        st.session_state.last_audio_hash = current_hash
                                        st.info("🔊 Fallback voice use hua (edge_tts unavailable)")
                                    except:
                                        st.warning("⚠️ Voice abhi available nahi. Text padh lo bhai!")

                    except Exception as api_error:
                        st.error(f"❌ CA Sahab ko connect nahi kar paye: {str(api_error)[:150]}")
