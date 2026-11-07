import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import base64
import mimetypes
import re
import hmac
import hashlib
import secrets
import time
from threading import Lock
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

GOOGLE_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Tus Cesantías al Instante",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- CSS PREMIUM ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: linear-gradient(145deg, #FFFFFF 0%, #F1F8FC 100%); padding: 0 !important; }
    .glass-container {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 32px;
        padding: 2rem 1.5rem;
        margin: 1rem auto;
        max-width: 480px;
        box-shadow: 0 20px 60px rgba(10, 37, 64, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #102868;
        text-align: center;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }
    .main-title span {
        background: linear-gradient(135deg, #1769C2, #16A6D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    .hero-icon {
        text-align: center;
        font-size: 4.5rem;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    .benefit-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 0.8rem;
        margin: 1.5rem 0;
    }
    .benefit-card {
        background: white;
        padding: 1.2rem 0.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #E2E8F0;
        transition: all 0.3s;
    }
    .benefit-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    .benefit-card .icon {
        font-size: 2.2rem;
        display: block;
        margin-bottom: 0.3rem;
    }
    .benefit-card h4 {
        margin: 0;
        font-size: 0.85rem;
        font-weight: 700;
        color: #102868;
    }
    .benefit-card p {
        margin: 0.2rem 0 0 0;
        font-size: 0.7rem;
        color: #94A3B8;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1769C2, #16A6D8) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 60px !important;
        width: 100% !important;
        padding: 0.9rem !important;
        font-size: 1.1rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(23, 105, 194, 0.22) !important;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(23, 105, 194, 0.30) !important;
    }
    .stButton > button:active {
        transform: scale(0.97) !important;
    }
    .stRadio > div {
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem;
        justify-content: center;
    }
    .stRadio > div > label {
        background: white;
        border: 2px solid #DCEAF4;
        border-radius: 16px;
        padding: 0.9rem 1.2rem;
        cursor: pointer;
        transition: all 0.2s ease;
        flex: 1;
        min-width: 120px;
        text-align: center;
        font-weight: 600;
        color: #102868;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .stRadio > div > label:hover {
        border-color: #1769C2;
        background: #EFF8FD;
        transform: translateY(-2px);
    }
    .stRadio > div > label > div {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    .stRadio > div > label[data-checked="true"] {
        border-color: #1769C2;
        background: #EFF8FD;
        box-shadow: 0 4px 12px rgba(23, 105, 194, 0.14);
    }
    .stTextInput > div > div > input {
        border-radius: 16px !important;
        border: 2px solid #E2E8F0 !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s !important;
        background: white;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1769C2 !important;
        box-shadow: 0 0 0 4px rgba(23, 105, 194, 0.12) !important;
    }
    .progress-container {
        background: #E2E8F0;
        border-radius: 40px;
        height: 6px;
        margin: 1.5rem 0 1rem 0;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        border-radius: 40px;
        background: linear-gradient(90deg, #1769C2, #16A6D8);
        transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .step-text {
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        border-left: 6px solid #16A6D8;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        margin: 1rem 0;
    }
    .price-tag {
        background: linear-gradient(135deg, #1769C2, #16A6D8);
        color: white;
        padding: 0.6rem 2rem;
        border-radius: 60px;
        display: inline-block;
        font-weight: 800;
        font-size: 2rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 20px rgba(0, 102, 255, 0.2);
    }
    .phone-number {
        background: #102868;
        color: white;
        padding: 1rem;
        border-radius: 20px;
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 1px;
        margin: 0.5rem 0;
        box-shadow: 0 8px 24px rgba(10, 37, 64, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    .verified-badge {
        background: #16A6D8;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    @media (max-width: 480px) {
        .glass-container {
            padding: 1.5rem 1rem;
            border-radius: 24px;
            margin: 0.5rem 0.5rem;
        }
        .main-title { font-size: 2.2rem; }
        .phone-number { font-size: 1.5rem; padding: 0.8rem; }
        .benefit-grid { grid-template-columns: 1fr 1fr; }
    }

    /* ---------- LEGIBILIDAD Y CONTRASTE (ESPECIALMENTE MÓVILES) ---------- */
    :root { color-scheme: light; }
    .stApp {
        color: #172B4D !important;
    }
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stText"] {
        color: #263B53 !important;
        opacity: 1 !important;
    }
    .stApp [data-testid="stMarkdownContainer"] strong,
    .stApp [data-testid="stMarkdownContainer"] b {
        color: #102A43 !important;
    }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stTextInput"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stRadio"] label {
        color: #102A43 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-baseweb="popover"] [role="option"] * {
        color: #142B45 !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #C5D8E8 !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #65758B !important;
        opacity: 1 !important;
    }
    [data-testid="stTextInput"] input:disabled {
        color: #34495E !important;
        -webkit-text-fill-color: #34495E !important;
        opacity: 1 !important;
        background-color: #F1F5F9 !important;
    }
    [data-testid="stCaptionContainer"] p,
    .stCaption,
    .step-text {
        color: #40566E !important;
        opacity: 1 !important;
    }
    .sub-title { color: #40566E !important; }
    .benefit-card p { color: #52657B !important; }
    .stRadio > div > label { color: #102A43 !important; }
    /* Textos informativos (st.info): gris medio, no negro */
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] b {
        color: #52657B !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }
    .fund-logo-box {
        height: 112px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 8px;
        background: #FFFFFF;
        border-radius: 12px;
        margin-bottom: 8px;
    }
    .fund-logo-box img {
        display: block;
        max-width: 100%;
        max-height: 94px;
        width: auto;
        height: auto;
        object-fit: contain;
    }
    .fund-emoji {
        height: 112px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.4rem;
    }
    .fund-name {
        color: #102A43 !important;
        font-size: 1.05rem;
        line-height: 1.3;
        font-weight: 800;
        text-align: center;
        min-height: 2.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 4px 0 10px 0;
    }
    @media (max-width: 640px) {
        .glass-container {
            padding: 1.2rem 0.85rem;
            margin: 0.45rem 0.2rem;
            border-radius: 22px;
        }
        .main-title { font-size: 2.15rem; }
        .sub-title { font-size: 1rem; }
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] span {
            font-size: 0.98rem !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] [data-baseweb="select"] {
            font-size: 16px !important;
        }
        .fund-logo-box, .fund-emoji { height: 96px; }
        .fund-logo-box img { max-height: 80px; }
        .fund-name { font-size: 1rem; min-height: 2.5rem; }
    }

</style>
<style>
    /* ---------- REDISEÑO FINTECH: CAPA VISUAL ---------- */
    :root {
        --brand-navy:#082B66; --brand-blue:#0874D1; --brand-cyan:#10BCEB;
        --brand-gold:#FFB51B; --brand-ink:#142B45; --brand-muted:#5B6F86;
        --brand-line:#D9E6F2;
    }
    html, body, [class*="css"], .stApp { font-family:'Inter',sans-serif!important; }
    .stApp {
        background:radial-gradient(circle at 8% 4%,rgba(16,188,235,.13),transparent 25rem),
        radial-gradient(circle at 95% 28%,rgba(8,116,209,.10),transparent 28rem),
        linear-gradient(145deg,#F7FAFE 0%,#EAF3FB 100%)!important;
        color:var(--brand-ink)!important;
    }
    .main .block-container { max-width:1060px; padding:1.2rem 1.35rem 3rem; }
    .brand-header { max-width:980px; margin:.15rem auto 1rem; padding:.7rem 1.1rem;
        display:flex; align-items:center; justify-content:space-between; gap:1rem;
        background:rgba(255,255,255,.9); border:1px solid var(--brand-line);
        border-radius:22px; box-shadow:0 10px 30px rgba(8,43,102,.07); }
    .brand-logo-wrap { display:flex; align-items:center; min-width:0; }
    .brand-logo-wrap img { display:block; max-height:72px; width:auto; max-width:100%; object-fit:contain; }
    .brand-trust { display:flex; align-items:center; gap:.45rem; color:var(--brand-navy); font-size:.8rem; font-weight:800; white-space:nowrap; }
    .brand-trust span { display:inline-flex; width:29px; height:29px; border-radius:50%; align-items:center; justify-content:center; color:#fff; background:linear-gradient(135deg,var(--brand-blue),var(--brand-cyan)); }
    .journey-wrap { max-width:980px; margin:0 auto 1.1rem; padding:.75rem 1rem .6rem; background:rgba(255,255,255,.8); border:1px solid var(--brand-line); border-radius:18px; }
    .journey { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.3rem; }
    .journey-step { display:flex; flex-direction:column; align-items:center; gap:.32rem; text-align:center; color:#8798AA; font-size:.7rem; font-weight:750; }
    .journey-dot { width:30px; height:30px; display:flex; align-items:center; justify-content:center; border-radius:50%; background:#E5EDF5; color:#52677E; font-size:.78rem; font-weight:900; border:2px solid white; box-shadow:0 0 0 1px var(--brand-line); }
    .journey-step.active { color:var(--brand-navy); }
    .journey-step.active .journey-dot { color:#fff; background:linear-gradient(135deg,var(--brand-blue),var(--brand-cyan)); box-shadow:0 4px 14px rgba(8,116,209,.24); }
    .journey-step.done { color:#1687B8; }
    .journey-step.done .journey-dot { color:#fff; background:#13B9D8; }
    .glass-container { position:relative; overflow:hidden; max-width:980px; margin:.7rem auto 1rem;
        padding:clamp(1.1rem,3vw,2.35rem); border-radius:28px; background:rgba(255,255,255,.97);
        border:1px solid #D6E5F3; box-shadow:0 18px 55px rgba(8,43,102,.10); }
    .glass-container:after { content:""; position:absolute; z-index:0; pointer-events:none; width:220px; height:220px; right:-145px; bottom:-165px; border-radius:50%; border:24px solid rgba(16,188,235,.10); }
    .glass-container > * { position:relative; z-index:1; }
    .main-title { font-size:clamp(2.15rem,5vw,3.6rem); line-height:1.03; letter-spacing:-.05em; font-weight:900; color:var(--brand-navy); }
    .main-title span { color:var(--brand-cyan); background:none; -webkit-text-fill-color:var(--brand-cyan); }
    .sub-title { max-width:680px; color:var(--brand-muted)!important; font-size:1.07rem; line-height:1.55; }
    .hero-kicker { display:inline-flex; align-items:center; gap:.4rem; padding:.42rem .8rem; border-radius:999px; background:#E8F7FD; color:#0875B8; font-size:.76rem; font-weight:850; letter-spacing:.04em; text-transform:uppercase; }
    .hero-trust-row { display:flex; flex-wrap:wrap; gap:.5rem; margin:1rem 0 1.2rem; }
    .hero-trust-pill { display:inline-flex; align-items:center; gap:.35rem; padding:.52rem .78rem; border-radius:999px; background:#F0F7FC; color:var(--brand-navy); border:1px solid #DCEAF5; font-size:.8rem; font-weight:750; }
    .benefit-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.75rem; margin:1.35rem 0; }
    .benefit-card { min-width:0; padding:1rem .6rem; border-radius:18px; text-align:center; background:linear-gradient(180deg,#fff,#F5FAFE); border:1px solid var(--brand-line); box-shadow:0 7px 20px rgba(8,43,102,.055); transition:transform .2s,box-shadow .2s; }
    .benefit-card:hover { transform:translateY(-3px); box-shadow:0 12px 26px rgba(8,43,102,.11); }
    .benefit-card .icon { width:46px; height:46px; display:inline-flex; align-items:center; justify-content:center; border-radius:14px; margin-bottom:.5rem; color:white; background:linear-gradient(145deg,var(--brand-blue),var(--brand-cyan)); font-size:1.45rem; }
    .benefit-card h4 { margin:0; color:var(--brand-navy); font-size:.9rem; font-weight:850; }
    .benefit-card p { margin:.28rem 0 0; color:var(--brand-muted)!important; font-size:.75rem; line-height:1.35; }
    [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--brand-line)!important; border-radius:20px!important; background:linear-gradient(180deg,#fff,#F7FBFE)!important; box-shadow:0 8px 22px rgba(8,43,102,.055)!important; }
    .stRadio > div > label { border:2px solid #DCEAF5!important; border-radius:18px!important; background:#fff!important; color:var(--brand-navy)!important; font-weight:750!important; box-shadow:0 4px 12px rgba(8,43,102,.04)!important; }
    .stRadio > div > label:hover { border-color:var(--brand-blue)!important; background:#F0F8FE!important; }
    .stRadio > div > label[data-checked="true"] { border-color:var(--brand-blue)!important; background:#EAF6FE!important; }
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] span,
    [data-testid="stTextInput"] label, [data-testid="stSelectbox"] label { color:var(--brand-navy)!important; font-weight:750!important; opacity:1!important; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div { min-height:47px; border:1.5px solid #C9DCEC!important; border-radius:13px!important; background:#fff!important; color:var(--brand-ink)!important; }
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus { border-color:var(--brand-blue)!important; box-shadow:0 0 0 3px rgba(8,116,209,.12)!important; }
    [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder { color:#8293A6!important; opacity:1!important; }
    [data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] *, [data-baseweb="popover"] [role="option"] * { color:var(--brand-ink)!important; opacity:1!important; }
    [data-testid="stCaptionContainer"] p, .stCaption { color:var(--brand-muted)!important; opacity:1!important; }
    .stButton > button, [data-testid="stDownloadButton"] button, [data-testid="stLinkButton"] a { min-height:47px; border:0!important; border-radius:14px!important; padding:.72rem 1.15rem!important; color:white!important; background:linear-gradient(110deg,var(--brand-navy),var(--brand-blue) 68%,#0A9DD7)!important; font-weight:800!important; font-size:.98rem!important; box-shadow:0 8px 20px rgba(8,74,151,.19)!important; transition:transform .18s,box-shadow .18s!important; }
    .stButton > button:hover, [data-testid="stDownloadButton"] button:hover { transform:translateY(-2px); box-shadow:0 12px 25px rgba(8,74,151,.25)!important; }
    div.st-key-landing_start button { color:#082B66!important; background:linear-gradient(110deg,#FFD34F,#FFB51B)!important; box-shadow:0 10px 24px rgba(255,181,27,.28)!important; font-size:1.08rem!important; }
    .step-text, .progress-container { display:none!important; }
    .result-card { background:linear-gradient(135deg,#fff,#F0F8FE); padding:1.35rem; border-radius:20px; border:1px solid var(--brand-line); border-left:5px solid var(--brand-cyan); box-shadow:0 8px 22px rgba(8,43,102,.07); margin:1rem 0; }
    .price-tag { display:inline-block; padding:.65rem 1.5rem; border-radius:15px; color:#fff; background:linear-gradient(120deg,var(--brand-navy),var(--brand-blue),var(--brand-cyan)); font-weight:900; font-size:clamp(1.5rem,4vw,2.1rem); }
    .phone-number { display:flex; align-items:center; justify-content:center; gap:.5rem; padding:1rem; margin:.6rem 0; border-radius:17px; color:#fff; background:linear-gradient(120deg,var(--brand-navy),var(--brand-blue),var(--brand-cyan)); font-size:clamp(1.4rem,4vw,2rem); font-weight:900; letter-spacing:.04em; }
    [data-testid="stAlert"] { border-radius:15px!important; border:1px solid #D6E9F7!important; }
    @media (max-width:700px) {
        .main .block-container { padding:.65rem .65rem 2rem; }
        .brand-header { padding:.55rem .7rem; border-radius:17px; }
        .brand-logo-wrap img { max-height:55px; max-width:70vw; }
        .brand-trust { font-size:.68rem; gap:.25rem; }
        .brand-trust span { width:24px; height:24px; }
        .journey-wrap { padding:.6rem .3rem; border-radius:14px; }
        .journey { gap:.08rem; }
        .journey-step { font-size:.58rem; gap:.25rem; }
        .journey-dot { width:25px; height:25px; font-size:.68rem; }
        .glass-container { padding:1.15rem .9rem; margin:.45rem 0; border-radius:21px; }
        .benefit-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:.55rem; }
        .benefit-card { padding:.8rem .45rem; }
        .benefit-card .icon { width:40px; height:40px; }
        [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] [data-baseweb="select"] { font-size:16px!important; }
        .stButton > button { min-height:48px; font-size:.92rem!important; }
    }
    @media (max-width:390px) { .brand-trust { display:none; } .journey-step { font-size:.52rem; } }
</style>
""", unsafe_allow_html=True)


# ---------- ESTADO INICIAL ----------
if 'step' not in st.session_state:
    st.session_state.step = 'landing'

for key in [
    'proposito', 'monto', 'monto_limpio', 'fondo',
    'nombre', 'cedula', 'telefono', 'email', 'empresa',
    'nit', 'ciudad', 'departamento', 'empresa_manual', 'nit_manual', 'saldo_verificado', 'saldo_limpio',
    'solicitud_guardada', 'doc_id_plantilla',
    'nombre_plantilla', 'plantilla_url',
    'doc_id_copia', 'url_copia', 'solicitud_id', 'documento_rellenado',
    'pdf_id', 'pdf_url', 'pdf_generado'
]:
    if key not in st.session_state:
        st.session_state[key] = ""

conn = st.connection("gsheets", type=GSheetsConnection)


# ---------- GOOGLE OAUTH: AUTORIZACIÓN ADMINISTRATIVA DE DRIVE ----------
def obtener_config_oauth():
    """Lee la configuración OAuth guardada de forma privada en Streamlit Secrets."""
    try:
        return dict(st.secrets["google_oauth"])
    except Exception as e:
        raise RuntimeError(
            "Falta la sección [google_oauth] en Streamlit Secrets."
        ) from e


@st.cache_resource
def obtener_almacen_pkce():
    """Almacén temporal compartido entre sesiones Streamlit para completar PKCE."""
    return {"lock": Lock(), "verificadores": {}}


def guardar_verificador_pkce(state, code_verifier):
    """Guarda el verificador en el servidor, nunca en la URL ni en el navegador."""
    almacen = obtener_almacen_pkce()
    ahora = time.time()
    with almacen["lock"]:
        # Elimina solicitudes anteriores para que el almacén no crezca sin límite.
        vencidos = [
            clave for clave, valor in almacen["verificadores"].items()
            if ahora - valor["creado"] > 600
        ]
        for clave in vencidos:
            almacen["verificadores"].pop(clave, None)
        almacen["verificadores"][state] = {
            "code_verifier": code_verifier,
            "creado": ahora
        }


def consumir_verificador_pkce(state):
    """Recupera una sola vez el verificador asociado al state y valida su vigencia."""
    almacen = obtener_almacen_pkce()
    with almacen["lock"]:
        registro = almacen["verificadores"].pop(state, None)
    if not registro or time.time() - registro["creado"] > 600:
        return None
    return registro["code_verifier"]


def crear_flujo_oauth(
    state=None,
    code_verifier=None,
    autogenerate_code_verifier=True
):
    """Prepara OAuth y permite reutilizar el mismo verificador PKCE en el callback."""
    datos = obtener_config_oauth()
    config_cliente = {
        "web": {
            "client_id": datos["client_id"],
            "client_secret": datos["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [datos["redirect_uri"]]
        }
    }
    flujo = Flow.from_client_config(
        config_cliente,
        scopes=[GOOGLE_DRIVE_SCOPE],
        state=state,
        code_verifier=code_verifier,
        autogenerate_code_verifier=autogenerate_code_verifier
    )
    flujo.redirect_uri = datos["redirect_uri"]
    return flujo


def crear_estado_oauth(clave_admin):
    """Crea un state firmado y de corta duración para proteger el callback OAuth."""
    contenido = f"{int(time.time())}:{secrets.token_urlsafe(24)}"
    firma = hmac.new(
        clave_admin.encode("utf-8"),
        contenido.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    contenido_codificado = base64.urlsafe_b64encode(
        contenido.encode("utf-8")
    ).decode("ascii").rstrip("=")
    return f"{contenido_codificado}.{firma}"


def validar_estado_oauth(state, clave_admin):
    """Comprueba la firma y que el intento OAuth no tenga más de 10 minutos."""
    try:
        contenido_codificado, firma_recibida = state.split(".", 1)
        relleno = "=" * (-len(contenido_codificado) % 4)
        contenido = base64.urlsafe_b64decode(
            contenido_codificado + relleno
        ).decode("utf-8")
        firma_esperada = hmac.new(
            clave_admin.encode("utf-8"),
            contenido.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(firma_recibida, firma_esperada):
            return False
        marca_tiempo = int(contenido.split(":", 1)[0])
        return 0 <= time.time() - marca_tiempo <= 600
    except Exception:
        return False


def render_configuracion_drive():
    """Pantalla de configuración accesible solo con la clave administrativa."""
    st.title("Configuración privada de Google Drive")
    st.caption(
        "Esta pantalla es para el administrador. Los clientes no necesitan "
        "iniciar sesión con Google para usar la aplicación."
    )

    try:
        datos = obtener_config_oauth()
        clave_correcta = str(datos.get("admin_key", ""))
        if not clave_correcta:
            st.error(
                "Falta admin_key dentro de [google_oauth] en Streamlit Secrets. "
                "Agrega esa clave privada antes de continuar."
            )
            st.stop()
    except Exception as e:
        st.error(str(e))
        st.stop()

    with st.form("form_admin_drive"):
        clave_ingresada = st.text_input(
            "Clave administrativa",
            type="password"
        )
        continuar = st.form_submit_button("Continuar")

    if continuar:
        if hmac.compare_digest(clave_ingresada, clave_correcta):
            st.session_state["admin_drive_autorizado"] = True
        else:
            st.session_state["admin_drive_autorizado"] = False
            st.error("La clave administrativa no coincide.")

    if not st.session_state.get("admin_drive_autorizado", False):
        st.info("Introduce la clave administrativa para iniciar la conexión.")
        st.stop()

    # Prueba administrativa de solo lectura: valida el token y localiza la
    # carpeta de plantillas sin crear solicitudes ni modificar archivos.
    if str(datos.get("refresh_token", "")).strip():
        if st.button("Probar conexión a Google Drive", use_container_width=True):
            try:
                servicio = obtener_servicio_drive()
                perfil = servicio.about().get(
                    fields="user(displayName,emailAddress)"
                ).execute()
                usuario_drive = perfil.get("user", {})
                st.success("La conexión OAuth con Google Drive funciona.")
                if usuario_drive.get("emailAddress"):
                    st.write(
                        f"**Cuenta autorizada:** {usuario_drive['emailAddress']}"
                    )
                if usuario_drive.get("displayName"):
                    st.write(
                        f"**Nombre de la cuenta:** {usuario_drive['displayName']}"
                    )

                consulta = (
                    "name = 'Plantillas_Cesantias' and "
                    "mimeType = 'application/vnd.google-apps.folder' and "
                    "trashed = false"
                )
                resultado = servicio.files().list(
                    q=consulta,
                    spaces="drive",
                    pageSize=100,
                    fields="files(id,name,mimeType,webViewLink)"
                ).execute()
                carpetas = resultado.get("files", [])

                if carpetas:
                    st.success(
                        f"Encontré {len(carpetas)} carpeta(s) llamada(s) "
                        "Plantillas_Cesantias."
                    )
                    for carpeta in carpetas:
                        st.write(
                            f"**Carpeta:** {carpeta.get('name', '')}  "
                            f"· **ID:** `{carpeta.get('id', '')}`"
                        )
                        contenido = servicio.files().list(
                            q=f"'{carpeta['id']}' in parents and trashed = false",
                            spaces="drive",
                            pageSize=100,
                            fields="files(id,name,mimeType,webViewLink)"
                        ).execute().get("files", [])
                        st.write(
                            f"Archivos visibles dentro de esta carpeta: "
                            f"**{len(contenido)}**"
                        )
                        if contenido:
                            st.dataframe(
                                [{
                                    "Nombre": archivo.get("name", ""),
                                    "Tipo": archivo.get("mimeType", ""),
                                    "ID": archivo.get("id", "")
                                } for archivo in contenido],
                                use_container_width=True,
                                hide_index=True
                            )
                else:
                    st.warning(
                        "La conexión funciona, pero no encontré una carpeta "
                        "con el nombre exacto Plantillas_Cesantias. Comprueba "
                        "que seleccionaste el Gmail correcto y que la carpeta "
                        "esté en su Drive o compartida con esa cuenta."
                    )
            except Exception as e:
                st.error(
                    "No se pudo comprobar el acceso a Google Drive. "
                    f"Detalle: {e}"
                )

    if st.button("Generar enlace de autorización de Google"):
        state = crear_estado_oauth(clave_correcta)
        flujo = crear_flujo_oauth(state=state)
        url_autorizacion, state_generado = flujo.authorization_url(
            access_type="offline",
            prompt="consent",
            include_granted_scopes="true"
        )
        # PKCE: el verificador creado para esta solicitud debe sobrevivir al
        # regreso desde Google y reutilizarse exactamente en el intercambio.
        if not flujo.code_verifier:
            st.error(
                "No se pudo generar el verificador de seguridad PKCE. "
                "Revisa que google-auth-oauthlib esté instalado y vuelve a intentar."
            )
            st.stop()
        guardar_verificador_pkce(state_generado, flujo.code_verifier)
        st.session_state["url_autorizacion_drive"] = url_autorizacion

    url = st.session_state.get("url_autorizacion_drive")
    if url:
        st.link_button(
            "Conectar la cuenta Gmail administradora",
            url,
            use_container_width=True
        )
        st.caption(
            "Abre el enlace, selecciona la cuenta Gmail propietaria de "
            "Plantillas_Cesantias y acepta el permiso de Google Drive."
        )


def procesar_callback_oauth():
    """Intercambia el código OAuth y muestra el refresh token al administrador."""
    parametros = st.query_params
    error_google = parametros.get("error")
    if error_google:
        st.error(
            f"Google no completó la autorización: {error_google}. "
            "Puedes volver a abrir la configuración privada de Drive."
        )
        st.stop()

    codigo = parametros.get("code")
    state = parametros.get("state")
    if not codigo or not state:
        st.error("La respuesta de Google no contiene el código o el state esperado.")
        st.stop()

    try:
        datos = obtener_config_oauth()
        clave_admin = str(datos.get("admin_key", ""))
        if not clave_admin or not validar_estado_oauth(state, clave_admin):
            raise RuntimeError(
                "La validación de seguridad expiró o no coincide. "
                "Vuelve a iniciar la autorización desde la configuración privada."
            )

        # El callback puede abrirse en otra pestaña y crear otra sesión Streamlit.
        # Por eso el verificador se recupera del almacén privado del servidor,
        # usando el state firmado como identificador de esta autorización.
        code_verifier = consumir_verificador_pkce(state)
        if not code_verifier:
            raise RuntimeError(
                "No se encontró el verificador PKCE de esta autorización o ya venció. "
                "Vuelve a Configuración de Drive y genera un enlace de autorización nuevo."
            )

        flujo = crear_flujo_oauth(
            state=state,
            code_verifier=code_verifier,
            autogenerate_code_verifier=False
        )
        flujo.fetch_token(code=codigo, code_verifier=code_verifier)
        credenciales = flujo.credentials
        refresh_token = credenciales.refresh_token

        if not refresh_token:
            raise RuntimeError(
                "Google no devolvió un refresh token. Vuelve a iniciar la conexión "
                "y asegúrate de seleccionar la cuenta correcta y aceptar el permiso."
            )

        # Guarda el token solo en la sesión temporal del administrador. No lo
        # muestra en una página pública ni vuelve a intercambiar el mismo code.
        st.session_state["oauth_pending_refresh_token"] = refresh_token
        st.session_state["oauth_token_unlocked"] = False
        st.session_state.pop("url_autorizacion_drive", None)
        st.query_params.clear()
        st.rerun()

    except Exception as e:
        # El código OAuth de esta vuelta es de un solo uso; para reintentar se
        # debe generar un enlace nuevo y, por tanto, un nuevo verificador PKCE.
        st.session_state.pop("url_autorizacion_drive", None)
        st.error(f"No se pudo completar la autorización OAuth: {e}")
        if st.button("Volver a configuración de Drive"):
            st.query_params.clear()
            st.query_params["configurar_drive"] = "1"
            st.rerun()
        st.stop()


def render_token_oauth():
    """Muestra el refresh token solo después de volver a validar la clave admin."""
    st.title("Autorización de Google completada")
    st.success("Google autorizó el acceso a Drive.")
    st.caption(
        "Por seguridad, vuelve a introducir la clave administrativa para ver "
        "el token privado que debes guardar en Streamlit Secrets."
    )

    try:
        clave_correcta = str(obtener_config_oauth().get("admin_key", ""))
    except Exception as e:
        st.error(str(e))
        st.stop()

    with st.form("form_desbloquear_refresh_token"):
        clave_ingresada = st.text_input(
            "Clave administrativa", type="password"
        )
        desbloquear = st.form_submit_button("Mostrar token privado")

    if desbloquear:
        st.session_state["oauth_token_unlocked"] = bool(
            clave_correcta and hmac.compare_digest(
                clave_ingresada, clave_correcta
            )
        )
        if not st.session_state["oauth_token_unlocked"]:
            st.error("La clave administrativa no coincide.")

    if not st.session_state.get("oauth_token_unlocked", False):
        st.stop()

    token = st.session_state.get("oauth_pending_refresh_token", "")
    if not token:
        st.error(
            "El token temporal ya no está disponible en esta sesión. "
            "Vuelve a realizar la autorización de Google."
        )
        st.stop()

    st.warning(
        "Copia este valor directamente a Streamlit Secrets. Es una credencial "
        "privada: no lo compartas ni lo pegues en el chat."
    )
    st.code(token, language=None)
    st.markdown(
        'Dentro de `[google_oauth]`, agrega la línea '
        '`refresh_token = "PEGA_AQUI_EL_TOKEN"`. Guarda Secrets y espera '
        'a que Streamlit reinicie la aplicación.'
    )
    if st.button("Ya guardé el refresh token en Secrets"):
        st.session_state.pop("oauth_pending_refresh_token", None)
        st.session_state.pop("oauth_token_unlocked", None)
        st.session_state.pop("url_autorizacion_drive", None)
        st.session_state["admin_drive_autorizado"] = False
        st.query_params["configurar_drive"] = "1"
        st.rerun()


# ---------- GOOGLE DRIVE: BUSCAR Y COPIAR PLANTILLAS ----------
@st.cache_resource
def obtener_servicio_drive():
    """Crea Drive API usando el refresh token OAuth de la cuenta Gmail administradora."""
    try:
        datos = obtener_config_oauth()
        refresh_token = str(datos.get("refresh_token", "")).strip()
        if not refresh_token:
            raise RuntimeError(
                "Drive aún no está conectado. El administrador debe completar "
                "la autorización OAuth y guardar refresh_token en Streamlit Secrets."
            )

        credenciales = UserCredentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=datos["client_id"],
            client_secret=datos["client_secret"],
            scopes=[GOOGLE_DRIVE_SCOPE]
        )

        return build(
            "drive",
            "v3",
            credentials=credenciales,
            cache_discovery=False
        )

    except Exception as e:
        raise RuntimeError(
            f"No se pudo iniciar Google Drive con OAuth: {e}"
        ) from e


@st.cache_data(ttl=300, show_spinner=False)
def obtener_info_plantilla(doc_id):
    """Comprueba que el Doc_ID exista y devuelve sus metadatos."""

    if not doc_id or not str(doc_id).strip():
        raise ValueError(
            "La empresa no tiene un Doc_ID configurado en la hoja Empresas."
        )

    servicio = obtener_servicio_drive()

    archivo = servicio.files().get(
        fileId=str(doc_id).strip(),
        fields="id,name,mimeType,webViewLink",
        supportsAllDrives=True
    ).execute()

    return archivo


@st.cache_resource
def obtener_servicio_docs():
    """Crea Google Docs API con la misma cuenta OAuth administradora."""
    datos = obtener_config_oauth()
    refresh_token = str(datos.get("refresh_token", "")).strip()
    if not refresh_token:
        raise RuntimeError("Falta refresh_token en [google_oauth] de Streamlit Secrets.")

    credenciales = UserCredentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=datos["client_id"],
        client_secret=datos["client_secret"],
        scopes=[GOOGLE_DRIVE_SCOPE]
    )
    return build("docs", "v1", credentials=credenciales, cache_discovery=False)


def obtener_id_carpeta_solicitudes():
    """Lee el ID de la carpeta destino configurada por el administrador."""
    datos = obtener_config_oauth()
    folder_id = str(datos.get("solicitudes_folder_id", "")).strip()
    if not folder_id:
        raise RuntimeError(
            "Falta solicitudes_folder_id en [google_oauth] de Streamlit Secrets. "
            "Crea la carpeta Solicitudes_Cesantias en Mi unidad y pega su ID."
        )

    servicio = obtener_servicio_drive()
    carpeta = servicio.files().get(
        fileId=folder_id,
        fields="id,name,mimeType,trashed"
    ).execute()
    if carpeta.get("mimeType") != "application/vnd.google-apps.folder" or carpeta.get("trashed"):
        raise RuntimeError("solicitudes_folder_id no corresponde a una carpeta válida de Google Drive.")
    return folder_id


def copiar_plantilla(doc_id, solicitud_id, nombre_persona):
    """Copia la plantilla directamente dentro de Solicitudes_Cesantias."""
    servicio = obtener_servicio_drive()
    folder_id = obtener_id_carpeta_solicitudes()

    nombre_seguro = re.sub(
        r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ_-]+",
        "_",
        str(nombre_persona)
    ).strip("_")
    nombre_archivo = f"Solicitud_{solicitud_id}_{nombre_seguro}"[:180]

    copia = servicio.files().copy(
        fileId=str(doc_id).strip(),
        body={"name": nombre_archivo, "parents": [folder_id]},
        supportsAllDrives=True,
        fields="id,name,webViewLink,parents"
    ).execute()
    return copia


def rellenar_plantilla_google_docs(document_id, valores):
    """Sustituye los marcadores de la copia sin modificar la plantilla original."""
    servicio = obtener_servicio_docs()
    solicitudes = []
    for marcador, valor in valores.items():
        solicitudes.append({
            "replaceAllText": {
                "containsText": {"text": marcador, "matchCase": True},
                "replaceText": str(valor or "").upper()
            }
        })

    resultado = servicio.documents().batchUpdate(
        documentId=document_id,
        body={"requests": solicitudes}
    ).execute()
    return resultado


def exportar_google_doc_a_pdf(document_id, solicitud_id, nombre_persona):
    """Exporta la copia rellenada a PDF y guarda/actualiza el PDF en la carpeta de solicitudes.

    Si Streamlit reintenta el proceso, reutiliza el PDF de esa solicitud en vez
    de crear archivos duplicados.
    """
    servicio = obtener_servicio_drive()
    folder_id = obtener_id_carpeta_solicitudes()

    nombre_seguro = re.sub(
        r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ_-]+",
        "_",
        str(nombre_persona)
    ).strip("_")
    nombre_pdf = f"Solicitud_{solicitud_id}_{nombre_seguro}.pdf"[:180]
    nombre_pdf_q = nombre_pdf.replace("\\", "\\\\").replace("'", "\\'")

    # Google Docs exporta directamente a PDF conservando el diseño del documento.
    contenido_pdf = servicio.files().export(
        fileId=document_id,
        mimeType="application/pdf"
    ).execute()

    media = MediaIoBaseUpload(
        BytesIO(contenido_pdf),
        mimetype="application/pdf",
        resumable=False
    )

    # Buscar primero si ya existe el PDF de esta solicitud para evitar duplicados.
    encontrados = servicio.files().list(
        q=f"name = '{nombre_pdf_q}' and '{folder_id}' in parents and trashed = false",
        pageSize=10,
        fields="files(id,name,webViewLink)"
    ).execute().get("files", [])

    if encontrados:
        archivo_pdf = servicio.files().update(
            fileId=encontrados[0]["id"],
            media_body=media,
            fields="id,name,webViewLink"
        ).execute()
    else:
        archivo_pdf = servicio.files().create(
            body={
                "name": nombre_pdf,
                "mimeType": "application/pdf",
                "parents": [folder_id]
            },
            media_body=media,
            fields="id,name,webViewLink"
        ).execute()

    return archivo_pdf


# ---------- PANTALLAS ----------
def obtener_logo_app_path():
    """Busca el logo propio de Cesantías al Instante para la interfaz; nunca se inserta en documentos ni PDF."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    carpetas = [
        os.path.join(base_dir, "assets"),
        os.path.join(base_dir, "assets", "logos"),
        base_dir,
    ]
    nombres_preferidos = [
        "logo_cesantias_al_instante",
        "cesantias_al_instante",
        "logo_cesantias",
        "logo_app_cesantias",
        "logo_cesantias_al_instante",
    ]
    extensiones = [".png", ".jpg", ".jpeg", ".webp"]
    for carpeta in carpetas:
        for nombre in nombres_preferidos:
            for extension in extensiones:
                ruta = os.path.join(carpeta, nombre + extension)
                if os.path.isfile(ruta):
                    return ruta
        # También acepta variantes de nombre, pero exige identificar la marca.
        if os.path.isdir(carpeta):
            for archivo in os.listdir(carpeta):
                nombre_archivo, extension = os.path.splitext(archivo)
                nombre_lower = nombre_archivo.lower()
                if (extension.lower() in extensiones
                        and "logo" in nombre_lower
                        and ("cesantia" in nombre_lower or "instante" in nombre_lower)):
                    return os.path.join(carpeta, archivo)
    return None


def render_brand_header(width=190):
    """Muestra la marca y el avance de seis etapas solo dentro de la app."""
    logo_app = obtener_logo_app_path()
    etapa_por_pantalla = {
        "pregunta1": 1, "pregunta2": 2, "verificar_saldo": 3,
        "monto_exacto": 4, "resultados": 5,
        "generando": 6, "whatsapp_entrega": 6, "pago": 6
    }
    etiquetas = ["Motivo", "Fondo", "Saldo", "Datos", "Resumen", "Finalizar"]
    activa = etapa_por_pantalla.get(st.session_state.get("step", ""), 0)
    logo_html = ""
    if logo_app:
        try:
            with open(logo_app, "rb") as archivo_logo:
                logo_b64 = base64.b64encode(archivo_logo.read()).decode("ascii")
            mime = mimetypes.guess_type(logo_app)[0] or "image/png"
            logo_html = f'<img src="data:{mime};base64,{logo_b64}" alt="Cesantías al Instante">'
        except OSError:
            logo_html = ""
    if activa == 0:
        izquierda, centro, derecha = st.columns([1, 2, 1])
        with centro:
            if logo_app:
                st.image(logo_app, width=width)
        return
    st.markdown(
        f'<div class="brand-header"><div class="brand-logo-wrap">{logo_html}</div>'
        '<div class="brand-trust"><span>✓</span> Seguro y confiable</div></div>',
        unsafe_allow_html=True
    )
    pasos_html = []
    for numero, etiqueta in enumerate(etiquetas, start=1):
        clase = "active" if numero == activa else ("done" if numero < activa else "")
        simbolo = "✓" if numero < activa else str(numero)
        pasos_html.append(
            f'<div class="journey-step {clase}"><div class="journey-dot">{simbolo}</div>'
            f'<span>{etiqueta}</span></div>'
        )
    st.markdown(
        '<div class="journey-wrap"><div class="journey">' + ''.join(pasos_html) + '</div></div>',
        unsafe_allow_html=True
    )


def render_landing():
    render_brand_header(width=320)

    st.markdown("""
    <div class="glass-container">
        <div class="hero-kicker">✦ Tu bienestar, más cerca</div>
        <div class="main-title">Tus cesantías,<br><span>más cerca de ti</span></div>
        <div class="sub-title">Gestiona tu solicitud de retiro de cesantías de manera fácil, rápida y segura, desde cualquier lugar.</div>
        <div class="hero-trust-row">
            <span class="hero-trust-pill">⚡ Rápido</span>
            <span class="hero-trust-pill">✓ Seguro</span>
            <span class="hero-trust-pill">♡ Fácil</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="benefit-grid">
        <div class="benefit-card">
            <span class="icon">🎯</span>
            <h4>1. Propósito</h4>
            <p>Elige el motivo</p>
        </div>
        <div class="benefit-card">
            <span class="icon">🏦</span>
            <h4>2. Fondo</h4>
            <p>Selecciona tu fondo</p>
        </div>
        <div class="benefit-card">
            <span class="icon">📞</span>
            <h4>3. Verifica</h4>
            <p>Tu saldo disponible</p>
        </div>
        <div class="benefit-card">
            <span class="icon">💰</span>
            <h4>4. Retira</h4>
            <p>Monto exacto</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Comenzar ahora →", use_container_width=True, key="landing_start"):

        for key in [
            'proposito', 'monto', 'monto_limpio', 'fondo',
            'nombre', 'cedula', 'telefono', 'email', 'empresa',
            'nit', 'ciudad', 'departamento', 'empresa_manual', 'nit_manual', 'saldo_verificado', 'saldo_limpio',
            'solicitud_guardada', 'doc_id_plantilla',
            'nombre_plantilla', 'plantilla_url',
            'doc_id_copia', 'url_copia', 'solicitud_id', 'documento_rellenado',
            'pdf_id', 'pdf_url', 'pdf_generado'
        ]:
            st.session_state[key] = ""
        # Limpiar también los widgets del lugar de firma para la próxima solicitud.
        st.session_state["ciudad_widget"] = ""
        st.session_state["departamento_widget"] = ""
        st.session_state["empresa_manual_widget"] = ""
        st.session_state["nit_manual_widget"] = ""

        st.session_state.step = 'pregunta1'
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_pregunta1():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 1 de 4</div>
        <div class="progress-container">
            <div class="progress-bar" style="width:25%;"></div>
        </div>
        <h3 style="color:#102868;font-weight:700;margin-bottom:1rem;">
            🎯 ¿Para qué quieres retirar?
        </h3>
    """, unsafe_allow_html=True)

    st.session_state.proposito = st.radio(
        "",
        [
            "🏠 Mejora de Vivienda",
            "📚 Educación",
            "💼 Desempleo",
            "❓ Otro"
        ],
        key="p1"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("↩️ Atrás", use_container_width=True):
            st.session_state.step = 'landing'
            st.rerun()

    with col2:
        if st.button("Siguiente →", use_container_width=True):
            st.session_state.step = 'pregunta2'
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_pregunta2():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 2 de 4</div>
        <div class="progress-container">
            <div class="progress-bar" style="width:50%;"></div>
        </div>
        <h3 style="color:#102868;font-weight:700;margin-bottom:1rem;">
            🏦 ¿En qué fondo estás?
        </h3>
    """, unsafe_allow_html=True)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "assets")

    def get_logo_path(filename):
        """Busca el logo en assets/ o assets/logos/, admitiendo PNG, JPG y WEBP."""
        if not filename:
            return None

        nombre_base = os.path.splitext(filename)[0]
        # También acepta nombres simples, por ejemplo porvenir.png.
        nombre_simple = re.sub(r"_logo$", "", nombre_base, flags=re.IGNORECASE)
        nombres_validos = {nombre_base.lower(), nombre_simple.lower()}
        extensiones = {".png", ".jpg", ".jpeg", ".webp"}

        for carpeta in (assets_dir, os.path.join(assets_dir, "logos")):
            if not os.path.isdir(carpeta):
                continue
            try:
                for archivo in os.listdir(carpeta):
                    base, extension = os.path.splitext(archivo)
                    if base.lower() in nombres_validos and extension.lower() in extensiones:
                        return os.path.join(carpeta, archivo)
            except OSError:
                continue
        return None

    fondos = [
        {"key": "porv", "nombre": "Porvenir", "logo": "Porvenir_logo.png", "emoji": "🏦"},
        {"key": "colf", "nombre": "Colfondos", "logo": "Colfondos_logo.png", "emoji": "🏢"},
        {"key": "prot", "nombre": "Protección", "logo": "Proteccion_logo.png", "emoji": "🛡️"},
        {"key": "fna", "nombre": "FNA", "logo": "FNA_logo.png", "emoji": "🏛️"},
        {"key": "otro", "nombre": "Otro", "logo": None, "emoji": "❓"}
    ]

    # Dos tarjetas por fila: son más fáciles de leer y tocar en pantallas pequeñas.
    for inicio in range(0, len(fondos), 2):
        columnas = st.columns(2, gap="medium")
        for columna, fondo in zip(columnas, fondos[inicio:inicio + 2]):
            with columna:
                with st.container(border=True):
                    logo_path = get_logo_path(fondo["logo"])

                    if logo_path:
                        with open(logo_path, "rb") as archivo_logo:
                            logo_bytes = archivo_logo.read()
                        logo_b64 = base64.b64encode(logo_bytes).decode("ascii")
                        mime_type = mimetypes.guess_type(logo_path)[0] or "image/png"
                        st.markdown(
                            f'<div class="fund-logo-box"><img '
                            f'src="data:{mime_type};base64,{logo_b64}" '
                            f'alt="Logo de {fondo["nombre"]}"></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="fund-emoji">{fondo["emoji"]}</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown(
                        f'<div class="fund-name">{fondo["nombre"]}</div>',
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "Seleccionar",
                        key=fondo["key"],
                        use_container_width=True
                    ):
                        st.session_state.fondo = fondo["nombre"]
                        st.session_state.step = 'verificar_saldo'
                        st.rerun()

    if st.button("↩️ Atrás", use_container_width=True):
        st.session_state.step = 'pregunta1'
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_verificar_saldo():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 3 de 4</div>
        <div class="progress-container">
            <div class="progress-bar" style="width:75%;"></div>
        </div>
        <h3 style="color:#102868;font-weight:700;margin-bottom:0.5rem;">
            📞 Verifica tu saldo
        </h3>
    """, unsafe_allow_html=True)

    numeros = {
        "Porvenir": "01 8000 111 222",
        "Colfondos": "01 8000 123 456",
        "Protección": "01 8000 789 012",
        "FNA": "01 8000 456 789",
        "Otro": "01 8000 000 000"
    }

    numero = numeros.get(
        st.session_state.fondo,
        "01 8000 000 000"
    )

    st.markdown(
        f'<div class="phone-number"><span>📱 {numero}</span></div>',
        unsafe_allow_html=True
    )

    st.info(
        "Marca, presiona 1, digita tu cédula y escucha tu saldo."
    )

    saldo_raw = st.text_input(
        "💰 Saldo exacto",
        placeholder="Ej: 10000000"
    )

    if saldo_raw:
        limpio = re.sub(r'[^0-9]', '', saldo_raw)

        if limpio:
            st.success(
                f"Saldo ingresado: "
                f"**{f'{int(limpio):,}'.replace(',', '.')}**"
            )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("↩️ Atrás", use_container_width=True):
            st.session_state.step = 'pregunta2'
            st.rerun()

    with col2:
        if st.button("Siguiente →", use_container_width=True):

            if saldo_raw:
                st.session_state.saldo_limpio = re.sub(
                    r'[^0-9]',
                    '',
                    saldo_raw
                )

                st.session_state.saldo_verificado = (
                    f"${f'{int(st.session_state.saldo_limpio):,}'.replace(',', '.')}"
                )

                st.session_state.step = 'monto_exacto'
                st.rerun()

            else:
                st.error("Ingresa el saldo.")

    st.markdown("</div>", unsafe_allow_html=True)


def limpiar_telefono_widget():
    """Mantiene el WhatsApp compuesto únicamente por dígitos."""
    valor = str(st.session_state.get("telefono_widget", ""))
    st.session_state.telefono_widget = re.sub(r"\D", "", valor)[:10]


def limpiar_cedula_widget():
    """Mantiene la cédula compuesta únicamente por dígitos, sin límite fijo."""
    valor = str(st.session_state.get("cedula_widget", ""))
    st.session_state.cedula_widget = re.sub(r"\D", "", valor)


def render_monto_exacto():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 4 de 4</div>
        <div class="progress-container">
            <div class="progress-bar" style="width:100%;"></div>
        </div>
        <h3 style="color:#102868;font-weight:700;margin-bottom:1rem;">
            💰 Monto y tus datos
        </h3>
    """, unsafe_allow_html=True)

    if st.session_state.saldo_verificado:
        st.info(
            f"💰 Saldo ingresado: **{st.session_state.saldo_verificado}**"
        )

    monto_raw = st.text_input(
        "Monto exacto a retirar",
        value=st.session_state.get('monto_raw_display', ''),
        key="monto_raw_widget"
    )

    if monto_raw:
        limpio = re.sub(r'[^0-9]', '', monto_raw)

        if limpio:
            st.success(
                f"✅ Monto a retirar: "
                f"**{f'{int(limpio):,}'.replace(',', '.')}**"
            )

    st.markdown("### 📋 Tus datos personales")

    col1, col2 = st.columns(2)

    with col1:
        telefono = st.text_input(
            "📱 WhatsApp",
            value=st.session_state.get('telefono_display', ''),
            key="telefono_widget",
            on_change=limpiar_telefono_widget
        )

        nombre = st.text_input(
            "👤 Nombre completo",
            value=st.session_state.get('nombre_display', ''),
            key="nombre_widget"
        )

        cedula = st.text_input(
            "🆔 Cédula",
            value=st.session_state.get('cedula_display', ''),
            key="cedula_widget",
            on_change=limpiar_cedula_widget
        )

    with col2:
        email = st.text_input(
            "📧 Correo",
            value=st.session_state.get('email_display', ''),
            key="email_widget"
        )

        # ---------- EMPRESA Y NIT ----------
        lista_empresas = []
        df_empresas = pd.DataFrame()

        try:
            df_empresas = conn.read(
                worksheet="Empresas",
                ttl=0
            ).dropna(how="all")

            if "Nombre_Empresa" not in df_empresas.columns:
                raise ValueError("La hoja Empresas debe tener la columna Nombre_Empresa.")

            lista_empresas = (
                df_empresas["Nombre_Empresa"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )
            lista_empresas = [
                nombre for nombre in lista_empresas
                if nombre and nombre.casefold() != "otra"
            ]

        except Exception as e:
            st.error(f"Error cargando empresas: {e}")

        empresa_seleccionada = st.selectbox(
            "🏢 Empresa",
            [""] + lista_empresas + ["Otra"],
            key="empresa_widget"
        )

        nit_auto = ""
        doc_id_auto = ""
        empresa_valor = empresa_seleccionada

        if empresa_seleccionada == "Otra":
            empresa_valor = st.text_input(
                "Nombre de la empresa",
                placeholder="Escribe el nombre de tu empresa",
                key="empresa_manual_widget"
            ).strip()
            nit_auto = st.text_input(
                "NIT de la empresa",
                placeholder="Escribe el NIT de tu empresa",
                key="nit_manual_widget"
            ).strip()

            # Si existe una fila llamada 'Otra' en la hoja Empresas,
            # se utiliza su Doc_ID como plantilla general para empresas no listadas.
            if not df_empresas.empty and "Doc_ID" in df_empresas.columns:
                filas_otra = df_empresas[
                    df_empresas["Nombre_Empresa"].astype(str).str.strip().str.casefold() == "otra"
                ]
                if not filas_otra.empty:
                    valor_doc = filas_otra["Doc_ID"].iloc[0]
                    doc_id_auto = "" if pd.isna(valor_doc) else str(valor_doc).strip()

        elif empresa_seleccionada and not df_empresas.empty:
            empresa_valor = empresa_seleccionada
            filtro_empresa = (
                df_empresas["Nombre_Empresa"]
                .astype(str)
                .str.strip()
                == empresa_seleccionada.strip()
            )

            if filtro_empresa.any():
                fila_empresa = df_empresas.loc[filtro_empresa].iloc[0]

                if "Doc_ID" in df_empresas.columns:
                    valor_doc = fila_empresa.get("Doc_ID", "")
                    doc_id_auto = "" if pd.isna(valor_doc) else str(valor_doc).strip()

                if "NIT" in df_empresas.columns:
                    valor_nit = fila_empresa.get("NIT", "")
                    nit_auto = "" if pd.isna(valor_nit) else str(valor_nit).strip()

            if nit_auto:
                st.caption(f"NIT: {nit_auto}")

        # Buscar y validar la plantilla de forma silenciosa. No mostrar
        # mensajes de 'plantilla encontrada' ni IDs al usuario.
        if doc_id_auto:
            try:
                info_plantilla = obtener_info_plantilla(doc_id_auto)
                st.session_state.doc_id_plantilla = info_plantilla["id"]
                st.session_state.nombre_plantilla = info_plantilla.get("name", "Documento sin nombre")
                st.session_state.plantilla_url = info_plantilla.get("webViewLink", "")
            except Exception:
                st.session_state.doc_id_plantilla = ""
                st.session_state.nombre_plantilla = ""
                st.session_state.plantilla_url = ""
        else:
            st.session_state.doc_id_plantilla = ""
            st.session_state.nombre_plantilla = ""
            st.session_state.plantilla_url = ""

    st.markdown("### 📍 Lugar de firma de la carta")
    departamentos_colombia = [
        "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá, D.C.",
        "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca",
        "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía",
        "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta",
        "Nariño", "Norte de Santander", "Putumayo", "Quindío",
        "Risaralda", "San Andrés y Providencia", "Santander", "Sucre",
        "Tolima", "Valle del Cauca", "Vaupés", "Vichada"
    ]
    departamento_valor = st.selectbox(
        "Departamento",
        [""] + departamentos_colombia,
        key="departamento_widget",
        index=0
    )
    ciudad_valor = st.text_input(
        "Ciudad",
        placeholder="Escribe el nombre de tu ciudad",
        key="ciudad_widget"
    )

    # ---------- BOTONES ----------
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("↩️ Atrás", use_container_width=True):
            st.session_state.step = 'verificar_saldo'
            st.rerun()

    with col_btn2:
        if st.button("Siguiente →", use_container_width=True):

            monto_raw_val = st.session_state.monto_raw_widget
            telefono_val = st.session_state.telefono_widget
            nombre_val = st.session_state.nombre_widget
            cedula_val = st.session_state.cedula_widget
            email_val = st.session_state.email_widget

            if not monto_raw_val or not all([
                telefono_val,
                nombre_val,
                cedula_val,
                email_val,
                empresa_seleccionada,
                empresa_valor,
                nit_auto,
                ciudad_valor,
                departamento_valor
            ]):
                st.error(
                    "Completa tus datos, selecciona la empresa y escribe la ciudad y el departamento de firma."
                )
                st.stop()

            if not st.session_state.doc_id_plantilla:
                st.error(
                    "No se puede continuar porque no hay una plantilla asignada. "
                    "Para empresas no listadas, agrega en la hoja Empresas una fila "
                    "llamada 'Otra' con el Doc_ID de la plantilla general."
                )
                st.stop()

            telefono_val = re.sub(r"\D", "", str(telefono_val))
            cedula_val = re.sub(r"\D", "", str(cedula_val))
            email_val = str(email_val).strip()

            if len(telefono_val) != 10:
                st.error("El WhatsApp debe tener exactamente 10 dígitos.")
                st.stop()

            if not cedula_val:
                st.error("La cédula debe contener únicamente números.")
                st.stop()

            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email_val):
                st.error("Ingresa un correo válido, con @ y un punto después del @.")
                st.stop()

            limpio = re.sub(r'[^0-9]', '', monto_raw_val)

            if not limpio:
                st.error("Ingresa un monto válido.")
                st.stop()

            if (
                st.session_state.saldo_limpio
                and int(limpio) > int(st.session_state.saldo_limpio)
            ):
                st.error("El monto supera el saldo ingresado.")
                st.stop()

            st.session_state.monto = (
                f"{int(limpio):,}".replace(',', '.')
            )

            st.session_state.monto_limpio = limpio
            st.session_state.telefono = telefono_val
            st.session_state.nombre = nombre_val
            st.session_state.cedula = cedula_val
            st.session_state.email = email_val
            st.session_state.empresa = empresa_valor
            st.session_state.nit = nit_auto
            st.session_state.ciudad = ciudad_valor.strip()
            st.session_state.departamento = departamento_valor.strip()

            st.session_state.step = 'resultados'
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_resultados():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container">
        <h3 style="color:#102868;font-weight:700;">
            ✅ ¡Listo! Resumen
        </h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"**🎯 Motivo:** {st.session_state.proposito}"
        )
        st.markdown(
            f"**🏦 Fondo:** {st.session_state.fondo}"
        )
        st.markdown(
            f"**💰 Monto a retirar:** {st.session_state.monto}"
        )

    with col2:
        st.markdown(
            f"**👤 Nombre:** {st.session_state.nombre}"
        )
        st.markdown(
            f"**🏢 Empresa:** {st.session_state.empresa}"
        )
        st.markdown(
            f"**📋 NIT:** {st.session_state.nit}"
        )

    if st.button(
        "📄 Continuar con pago →",
        use_container_width=True
    ):
        st.session_state.step = 'generando'
        st.rerun()

    if st.button("↩️ Atrás", use_container_width=True):
        st.session_state.step = 'monto_exacto'
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_generando():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container" style="text-align:center;">
        <h3 style="color:#102868;font-weight:700;">
            🔄 Procesando...
        </h3>
        <p style="color:#64748B;">
            Guardando tu solicitud y copiando la plantilla.
        </p>
    """, unsafe_allow_html=True)

    # ---------- GUARDAR SOLICITUD ----------
    if not st.session_state.solicitud_guardada:

        solicitud_id = (
            f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        st.session_state.solicitud_id = solicitud_id

        fecha_actual = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        try:
            existing_data = conn.read(
                worksheet="Solicitudes",
                ttl=0
            ).dropna(how="all")

            nuevo_dato = pd.DataFrame([{
                "solicitud_id": solicitud_id,
                "fecha": fecha_actual,
                "nombre": st.session_state.nombre,
                "cedula": st.session_state.cedula,
                "telefono": st.session_state.telefono,
                "email": st.session_state.email,
                "nit": st.session_state.nit,
                "empresa": st.session_state.empresa,
                "fondo": st.session_state.fondo,
                "motivo": st.session_state.proposito,
                # Guardar solo los dígitos como texto para evitar que la
                # configuración regional/formato de Sheets cambie 900000 a 900.
                "monto": str(st.session_state.monto_limpio),
                "ciudad": st.session_state.ciudad,
                "departamento": st.session_state.departamento,
                "estado": "Pendiente"
            }])

            updated_df = pd.concat(
                [existing_data, nuevo_dato],
                ignore_index=True
            )

            conn.update(
                worksheet="Solicitudes",
                data=updated_df
            )

            st.session_state.solicitud_guardada = True

        except Exception as e:
            st.error(
                f"Error guardando en Google Sheets: {e}"
            )

            if st.button("Reintentar"):
                st.rerun()

            st.stop()

    # ---------- COPIAR PLANTILLA ----------
    if not st.session_state.doc_id_copia:

        try:
            copia = copiar_plantilla(
                st.session_state.doc_id_plantilla,
                st.session_state.solicitud_id,
                st.session_state.nombre
            )

            st.session_state.doc_id_copia = copia["id"]

            st.session_state.url_copia = (
                copia.get("webViewLink", "")
            )

        except Exception as e:
            st.error(
                "La solicitud quedó guardada en Google Sheets, "
                "pero no se pudo copiar la plantilla. "
                f"Detalle de Google Drive: {e}"
            )

            st.info(
                "Verifica que el administrador haya conectado la cuenta Gmail "
                "propietaria de la plantilla mediante OAuth, que esa cuenta "
                "tenga acceso de Editor y que refresh_token esté guardado "
                "en Streamlit Secrets."
            )

            if st.button("Reintentar copia de plantilla"):
                st.rerun()

            st.stop()

    # ---------- RELLENAR LA COPIA (NO LA PLANTILLA ORIGINAL) ----------
    if not st.session_state.documento_rellenado:
        try:
            motivo = str(st.session_state.proposito or "").strip()
            motivo = re.sub(r"^[^\wÁÉÍÓÚáéíóúÑñ]+", "", motivo).strip()
            fecha_documento = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y")

            valores = {
                # Los datos de texto se insertan en MAYÚSCULAS en la copia,
                # sin modificar nunca la plantilla original.
                "{{FONDO_CESANTIAS}}": str(st.session_state.fondo).upper(),
                "{{NOMBRE_TRABAJADOR}}": str(st.session_state.nombre).upper(),
                "{{CEDULA}}": str(st.session_state.cedula),
                "{{MONTO_RETIRO}}": str(st.session_state.monto).upper(),
                "{{MONTO DE RETIRO}}": str(st.session_state.monto).upper(),
                "{{MOTIVO_RETIRO}}": motivo.upper(),
                "{{CIUDAD}}": str(st.session_state.ciudad).upper(),
                "{{DEPARTAMENTO}}": str(st.session_state.departamento).upper(),
                "{{FECHA}}": fecha_documento
            }
            rellenar_plantilla_google_docs(
                st.session_state.doc_id_copia,
                valores
            )
            st.session_state.documento_rellenado = True
        except Exception as e:
            st.error(
                "La copia se creó en Drive, pero no se pudieron reemplazar "
                f"los marcadores del documento. Detalle: {e}"
            )
            st.info(
                "La plantilla original no fue modificada. Puedes corregir el "
                "problema y pulsar Reintentar para rellenar la copia existente."
            )
            if st.button("Reintentar rellenado del documento"):
                st.rerun()
            st.stop()

    # ---------- EXPORTAR PDF EN LA MISMA CARPETA ----------
    if not st.session_state.pdf_generado:
        try:
            archivo_pdf = exportar_google_doc_a_pdf(
                st.session_state.doc_id_copia,
                st.session_state.solicitud_id,
                st.session_state.nombre
            )
            st.session_state.pdf_id = archivo_pdf["id"]
            st.session_state.pdf_url = archivo_pdf.get(
                "webViewLink",
                f"https://drive.google.com/file/d/{archivo_pdf['id']}/view"
            )
            st.session_state.pdf_generado = True
        except Exception as e:
            st.error(
                "El documento Google Docs quedó creado y rellenado, pero no se pudo "
                f"generar o guardar el PDF. Detalle: {e}"
            )
            st.info(
                "El documento editable permanece en Solicitudes_Cesantias. "
                "Puedes reintentar la generación del PDF sin crear otra copia del documento."
            )
            if st.button("Reintentar generación del PDF"):
                st.rerun()
            st.stop()

    # ---------- CONFIRMACIÓN ----------
    st.success(
        f"✅ Solicitud {st.session_state.solicitud_id} "
        f"guardada. Se generaron el documento editable y su PDF."
    )

    if st.session_state.url_copia:
        st.markdown(
            f"[Abrir documento Google Docs]"
            f"({st.session_state.url_copia})"
        )

    if st.session_state.pdf_url:
        st.markdown(
            f"[📄 Abrir o descargar PDF]"
            f"({st.session_state.pdf_url})"
        )

    st.markdown(f"""
    <div style="background:#E8F5E9;padding:1rem;
    border-radius:16px;border-left:4px solid #25D366;
    margin-top:1rem;">
        <strong>📱 Mensaje simulado de WhatsApp:</strong><br>
        "Hola {st.session_state.nombre}, hemos recibido tu solicitud.
        En un máximo de 24 horas hábiles te estaremos enviando
        tu carta. Estamos aquí para cualquier duda."
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "Avanzar 24 Horas (Simulación) →",
        use_container_width=True
    ):
        st.session_state.step = 'whatsapp_entrega'
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_whatsapp_entrega():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container" style="text-align:center;">
        <h3 style="color:#102868;font-weight:700;">
            📱 24 Horas Después...
        </h3>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#E8F5E9;padding:1rem;
    border-radius:16px;border-left:4px solid #25D366;
    margin:1rem 0;">
        <strong>📱 Vista previa de mensaje (simulación):</strong><br>
        "Hola {st.session_state.nombre}. La copia de tu plantilla
        quedó creada para la solicitud
        {st.session_state.solicitud_id}."
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.url_copia:
        st.link_button(
            "📄 Abrir copia de la plantilla",
            st.session_state.url_copia,
            use_container_width=True
        )
    else:
        st.info(
            "La copia se creó, pero Google Drive no devolvió "
            "un enlace para abrirla."
        )

    if st.button(
        "Continuar al Pago →",
        use_container_width=True
    ):
        st.session_state.step = 'pago'
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_pago():
    render_brand_header(width=185)
    st.markdown("""
    <div class="glass-container">
        <h3 style="color:#102868;font-weight:700;">
            💳 Pago con Nequi
        </h3>
        <p style="color:#64748B;">
            Realiza el pago de <strong>$20.000 COP</strong> al número:
        </p>
        <div class="phone-number"
        style="background:linear-gradient(135deg,#7B2FBE,#9B4DCA);">
            📱 312 679 3911
        </div>
    """, unsafe_allow_html=True)

    if st.button(
        "✅ Ya pagué, finalizar",
        use_container_width=True
    ):
        st.session_state.step = 'landing'
        st.success("¡Gracias! Proceso finalizado.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- MAIN ----------
def main():

    # Google vuelve a la URL principal con code/state después de autorizar.
    if st.query_params.get("code") or st.query_params.get("error"):
        procesar_callback_oauth()

    # El refresh token se muestra en una pantalla separada y protegida.
    if st.session_state.get("oauth_pending_refresh_token"):
        render_token_oauth()
        return

    # La configuración administrativa solo aparece al abrir ?configurar_drive=1.
    if st.query_params.get("configurar_drive") == "1":
        render_configuracion_drive()
        return

    if st.session_state.step == 'landing':
        render_landing()

    elif st.session_state.step == 'pregunta1':
        render_pregunta1()

    elif st.session_state.step == 'pregunta2':
        render_pregunta2()

    elif st.session_state.step == 'verificar_saldo':
        render_verificar_saldo()

    elif st.session_state.step == 'monto_exacto':
        render_monto_exacto()

    elif st.session_state.step == 'resultados':
        render_resultados()

    elif st.session_state.step == 'generando':
        render_generando()

    elif st.session_state.step == 'whatsapp_entrega':
        render_whatsapp_entrega()

    elif st.session_state.step == 'pago':
        render_pago()

    else:
        render_landing()


if __name__ == "__main__":
    main()
