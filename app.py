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
    layout="wide",
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


# ---------- SISTEMA VISUAL: MAQUETA DE SEIS PANTALLAS ----------
st.markdown(r"""
<style>
:root{
 --cia-navy:#062d70;--cia-blue:#0874d8;--cia-cyan:#12bfe9;--cia-gold:#ffb51b;
 --cia-ink:#102f60;--cia-muted:#506783;--cia-line:#d6e4f3;--cia-pale:#eef7ff;
}
html,body,[class*="css"],.stApp{font-family:Inter,Arial,sans-serif!important}
.stApp{background:linear-gradient(135deg,#05275f 0%,#06498f 48%,#08a4d8 100%)!important;color:var(--cia-ink)!important}
.main .block-container{max-width:1120px!important;padding:1rem clamp(.55rem,2vw,1.4rem) 2.4rem!important}
#MainMenu,footer,header{visibility:hidden}
.brand-header{max-width:1050px;margin:.12rem auto .65rem;padding:.48rem 1.05rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;background:#fff;border:1px solid #dce9f7;border-radius:19px 19px 8px 8px;box-shadow:0 8px 25px rgba(0,20,65,.15)}
.brand-logo-wrap{display:flex;align-items:center;min-width:0;max-width:56%}
.brand-logo-wrap img{display:block;max-height:65px;width:auto;max-width:100%;object-fit:contain}
.brand-trust{display:flex;align-items:center;gap:.45rem;color:var(--cia-navy);font-size:.82rem;font-weight:800;white-space:nowrap}
.brand-trust span{display:inline-flex;width:29px;height:29px;border-radius:50%;align-items:center;justify-content:center;color:#fff;background:linear-gradient(135deg,var(--cia-blue),var(--cia-cyan));font-size:1rem}
.journey-wrap{position:relative;max-width:1050px;margin:0 auto .8rem;padding:.7rem 1rem .58rem;background:rgba(255,255,255,.97);border:1px solid var(--cia-line);border-radius:12px;box-shadow:0 8px 24px rgba(0,20,65,.12)}
.journey{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:.25rem;position:relative}
.journey-step{position:relative;display:flex;flex-direction:column;align-items:center;gap:.28rem;text-align:center;color:#7588a0;font-size:.72rem;font-weight:650;z-index:1}
.journey-step:before{content:"";position:absolute;height:2px;background:#ccd9e8;left:-50%;right:50%;top:14px;z-index:-1}
.journey-step:first-child:before{display:none}
.journey-dot{width:29px;height:29px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#e2eaf3;color:#18345b;font-size:.78rem;font-weight:900;border:2px solid #fff;box-shadow:0 0 0 1px #d3deeb}
.journey-step.active{color:var(--cia-navy);font-weight:900}
.journey-step.active .journey-dot{color:#fff;background:linear-gradient(135deg,var(--cia-blue),#0752b8);box-shadow:0 0 0 2px #d2e9ff,0 4px 12px #0874d844}
.journey-step.done{color:#0a6ebd}
.journey-step.done .journey-dot{color:#fff;background:#11b9df;box-shadow:0 0 0 1px #b9eefa}
.glass-container{position:relative;overflow:hidden;max-width:1050px;margin:.6rem auto 1rem;padding:clamp(1rem,2.7vw,2rem);border-radius:23px;background:linear-gradient(180deg,#fff 0%,#f8fbff 88%,#e9f7ff 100%);border:1px solid #d2e3f4;box-shadow:0 17px 48px rgba(0,19,65,.19)}
.glass-container:after{content:"";position:absolute;pointer-events:none;width:260px;height:65px;right:-65px;bottom:-39px;transform:rotate(-13deg);border-radius:60% 0 0 0;background:linear-gradient(90deg,#0cc6f3,#0872d4,#06357f);opacity:.9}
.glass-container>*{position:relative;z-index:1}
.screen-heading{display:flex;align-items:center;gap:.8rem;margin:.2rem 0 1.15rem}
.screen-heading .screen-icon{width:54px;height:54px;flex:0 0 54px;border-radius:15px;display:flex;align-items:center;justify-content:center;color:#fff;background:linear-gradient(145deg,#0879df,#05bce8);font-size:1.7rem;box-shadow:0 7px 18px #0874d833}
.screen-heading h2{margin:0;color:var(--cia-navy);font-size:clamp(1.25rem,2.7vw,1.72rem);font-weight:900;letter-spacing:-.025em}
.screen-heading p{margin:.12rem 0 0;color:#405b7b;font-size:.95rem}
/* Landing, con la mujer de la maqueta */
.hero-shell{position:relative;isolation:isolate;display:grid;grid-template-columns:1.05fr .95fr;min-height:490px;max-width:1050px;margin:0 auto 1rem;overflow:hidden;border-radius:24px;background:linear-gradient(135deg,#062a6b 0%,#073e91 58%,#087ed0 100%);box-shadow:0 20px 55px rgba(0,17,59,.28);border:1px solid #1688dc}
.hero-shell:before{content:"";position:absolute;z-index:-1;left:-8%;top:-19%;width:66%;height:45%;border-radius:0 0 70% 12%;background:linear-gradient(145deg,#fff 0%,#f4fbff 72%,#b8eaff 100%);transform:rotate(-5deg)}
.hero-shell:after{content:"";position:absolute;z-index:2;bottom:-42px;right:-4%;width:64%;height:85px;transform:rotate(-8deg);border-radius:80% 0 0 0;border-top:16px solid #0ac6f0;pointer-events:none}
.hero-copy{position:relative;z-index:3;padding:1.25rem 1.5rem 1.45rem;display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-start}
.hero-logo{width:min(100%,410px);height:122px;display:flex;align-items:center;margin:-.5rem 0 1.2rem}
.hero-logo img{max-width:100%;max-height:112px;object-fit:contain;object-position:left center;border-radius:8px}
.hero-title{margin:.2rem 0 .7rem;color:#fff;font-size:clamp(2rem,4.2vw,3.15rem);font-weight:950;letter-spacing:-.045em;line-height:1.03}
.hero-title span{display:block;color:#12d2f4}
.hero-description{max-width:440px;color:#fff;font-size:clamp(1rem,1.8vw,1.22rem);line-height:1.45;margin:0 0 1.15rem}
.hero-benefits{display:grid;gap:.55rem;margin:.15rem 0 .75rem;color:#fff;font-size:1.12rem;font-weight:750}
.hero-benefit{display:flex;align-items:center;gap:.65rem}
.hero-benefit i{font-style:normal;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#13c7e8;color:#003d8d;font-size:1.05rem;font-weight:900}
.hero-person{position:relative;min-height:490px;align-self:stretch;overflow:hidden;border-radius:0 0 0 100px}
.hero-person img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center top}
.hero-person:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#07357e 0%,transparent 30%),linear-gradient(0deg,rgba(0,69,160,.2),transparent 40%);pointer-events:none}
/* Streamlit button shapes and inputs */
.stButton>button,[data-testid="stDownloadButton"] button,[data-testid="stLinkButton"] a{min-height:45px;border:1px solid #0874d8!important;border-radius:13px!important;padding:.62rem 1rem!important;color:#fff!important;background:linear-gradient(110deg,#073d91,#0874d8 68%,#0aa6db)!important;font-weight:850!important;font-size:.96rem!important;box-shadow:0 7px 17px rgba(8,74,151,.17)!important;transition:transform .16s,box-shadow .16s!important}
.stButton>button:hover,[data-testid="stDownloadButton"] button:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(8,74,151,.24)!important}
div.st-key-landing_start{max-width:255px;margin-top:-5.35rem;margin-left:1.4rem;margin-bottom:3.5rem;position:relative;z-index:4}
div.st-key-landing_start button{color:#072d66!important;background:linear-gradient(110deg,#ffcf39,#ffab00)!important;border:0!important;border-radius:40px!important;font-size:1.04rem!important;box-shadow:0 9px 23px #ffb51b55!important}
.st-key-motivo_vivienda button,.st-key-motivo_educacion button,.st-key-motivo_salud button,.st-key-motivo_vacaciones button,.st-key-motivo_vehiculo button,.st-key-motivo_otro button{height:112px;white-space:pre-line!important;line-height:1.34!important;background:linear-gradient(180deg,#fff,#f1f8ff)!important;color:var(--cia-navy)!important;border:1px solid #d5e5f5!important;border-radius:15px!important;box-shadow:0 4px 12px #062d7010!important;font-size:.9rem!important}
.st-key-motivo_vivienda button:hover,.st-key-motivo_educacion button:hover,.st-key-motivo_salud button:hover,.st-key-motivo_vacaciones button:hover,.st-key-motivo_vehiculo button:hover,.st-key-motivo_otro button:hover{border-color:#0874d8!important;background:#edf8ff!important}
.st-key-fondo_porv button,.st-key-fondo_colf button,.st-key-fondo_prot button,.st-key-fondo_fna button,.st-key-fondo_otro button{height:72px;background:#fff!important;color:var(--cia-navy)!important;border:1px solid #d5e5f5!important;box-shadow:none!important}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid var(--cia-line)!important;border-radius:16px!important;background:linear-gradient(180deg,#fff,#f6fbff)!important;box-shadow:0 5px 16px #082b6610!important}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label,[data-testid="stWidgetLabel"] span,[data-testid="stTextInput"] label,[data-testid="stSelectbox"] label,[data-testid="stRadio"] label{color:var(--cia-navy)!important;font-weight:800!important;opacity:1!important}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] [data-baseweb="select"]>div{min-height:45px;border:1.4px solid #c6d9ed!important;border-radius:12px!important;background:#fff!important;color:#152f55!important}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:#0874d8!important;box-shadow:0 0 0 3px #0874d81c!important}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{color:#8093a9!important;opacity:1!important}
[data-testid="stCaptionContainer"] p,.stCaption{color:#526780!important;opacity:1!important}
[data-testid="stAlert"]{border-radius:13px!important;border:1px solid #cfe4f5!important}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],[data-testid="stAlert"] p,[data-testid="stAlert"] span{color:#52657b!important;opacity:1!important}
.fund-logo-box{height:72px;display:flex;align-items:center;justify-content:center;padding:5px;background:#fff;border-radius:10px;margin-bottom:4px}
.fund-logo-box img{max-width:100%;max-height:64px;object-fit:contain}
.fund-emoji{height:72px;display:flex;align-items:center;justify-content:center;font-size:2.1rem}
.fund-name{color:var(--cia-navy)!important;font-weight:850;text-align:center;font-size:.9rem;min-height:1.5rem}
.summary-panel{background:linear-gradient(135deg,#fff,#eff7ff);border:1px solid #d0e2f3;border-radius:17px;padding:1.15rem;box-shadow:0 6px 19px #082b6610}
.summary-check{width:92px;height:92px;margin:.2rem auto .9rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#20c83d,#12a52d);color:#fff;font-size:3.6rem;font-weight:900;box-shadow:0 10px 25px #18b83733}
.success-shell{max-width:1050px;margin:.5rem auto;padding:clamp(1.3rem,4vw,3rem);border-radius:24px;background:radial-gradient(circle at 50% 22%,#e5f4ff,#fff 60%,#eef8ff);border:1px solid #d2e3f4;box-shadow:0 17px 48px #00194133;text-align:center;position:relative;overflow:hidden}
.success-shell:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 16% 18%,#12bfe955 0 3px,transparent 4px),radial-gradient(circle at 27% 10%,#ffb51b88 0 4px,transparent 5px),radial-gradient(circle at 76% 16%,#0874d855 0 4px,transparent 5px),radial-gradient(circle at 88% 28%,#ffb51b88 0 3px,transparent 4px),radial-gradient(circle at 9% 60%,#12bfe955 0 3px,transparent 4px);pointer-events:none}
.success-check{width:92px;height:92px;margin:.2rem auto .9rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#10bdf0,#0756c4);color:#fff;font-size:3.6rem;font-weight:900;box-shadow:0 10px 25px #0874d833;position:relative;z-index:1}
.success-shell h1{color:var(--cia-navy);font-size:clamp(2rem,4vw,3rem);font-weight:950;letter-spacing:-.04em;margin:.2rem 0 .5rem}
.success-shell p{color:#173d76;font-size:1.05rem;line-height:1.45}
.success-email{max-width:680px;margin:1.25rem auto;padding:.9rem 1.2rem;border-radius:16px;background:#d8edff;color:#063574;font-weight:650;text-align:left}
.footer-brand{text-align:center;color:#063574;font-weight:850;font-style:italic;margin-top:1.3rem}
/* Six-step flow is kept legible on narrow phones. */
@media(max-width:760px){
 .main .block-container{padding:.55rem .45rem 1.5rem!important}
 .brand-header{padding:.45rem .65rem;border-radius:14px;margin-bottom:.5rem}
 .brand-logo-wrap{max-width:68%}.brand-logo-wrap img{max-height:52px}
 .brand-trust{font-size:.66rem;gap:.25rem}.brand-trust span{width:23px;height:23px}
 .journey-wrap{padding:.55rem .2rem;border-radius:12px}
 .journey{gap:0}.journey-step{font-size:.57rem;gap:.22rem}.journey-dot{width:25px;height:25px;font-size:.68rem}
 .journey-step:before{top:12px}
 .glass-container{padding:1rem .75rem;margin:.4rem 0;border-radius:17px}
 .screen-heading{gap:.6rem;margin-bottom:.9rem}.screen-heading .screen-icon{width:44px;height:44px;flex-basis:44px;font-size:1.4rem}
 .screen-heading h2{font-size:1.24rem}.screen-heading p{font-size:.83rem}
 .hero-shell{grid-template-columns:1fr;min-height:0;border-radius:18px}
 .hero-shell:before{width:90%;height:24%;top:-10%}
 .hero-copy{padding:.8rem 1rem 1.1rem}
 .hero-logo{height:85px;width:min(100%,310px);margin:-.15rem 0 .55rem}.hero-logo img{max-height:78px}
 .hero-title{font-size:2.25rem;margin:.15rem 0 .5rem}.hero-description{font-size:1rem;margin-bottom:.7rem}
 .hero-benefits{display:flex;flex-wrap:wrap;gap:.5rem;font-size:.82rem}.hero-benefit{gap:.35rem}.hero-benefit i{width:27px;height:27px;font-size:.85rem}
 .hero-person{min-height:300px;max-height:365px;border-radius:0 0 0 60px}
 .hero-person img{object-position:center 25%}
 div.st-key-landing_start{margin:-1rem auto 1.1rem;max-width:calc(100% - 2rem)}
 div.st-key-landing_start button{min-height:50px}
 .st-key-motivo_vivienda button,.st-key-motivo_educacion button,.st-key-motivo_salud button,.st-key-motivo_vacaciones button,.st-key-motivo_vehiculo button,.st-key-motivo_otro button{height:105px;font-size:.8rem!important;padding:.45rem!important}
 .st-key-fondo_porv button,.st-key-fondo_colf button,.st-key-fondo_prot button,.st-key-fondo_fna button,.st-key-fondo_otro button{min-height:62px;font-size:.82rem!important}
 .success-shell{padding:1.3rem .9rem;border-radius:18px}
}
@media(max-width:390px){.brand-trust{font-size:.6rem}.journey-step{font-size:.49rem}.journey-dot{width:22px;height:22px}.journey-step:before{top:10px}.hero-title{font-size:2rem}}
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


def obtener_imagen_hero_path():
    """Imagen de bienvenida; se mantiene separada de las plantillas de Google Docs."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for carpeta in (os.path.join(base_dir, "assets"), base_dir):
        ruta = os.path.join(carpeta, "hero_mujer.png")
        if os.path.isfile(ruta):
            return ruta
    return None


def imagen_data_uri(ruta):
    if not ruta or not os.path.isfile(ruta):
        return ""
    mime = mimetypes.guess_type(ruta)[0] or "image/png"
    with open(ruta, "rb") as archivo:
        contenido = base64.b64encode(archivo.read()).decode("ascii")
    return f"data:{mime};base64,{contenido}"


def resolver_empresa_y_plantilla(empresa_seleccionada, empresa_manual="", nit_manual=""):
    """Lee la hoja Empresas y conserva la relación empresa → NIT → plantilla."""
    df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
    if "Nombre_Empresa" not in df_empresas.columns:
        raise ValueError("La hoja Empresas debe tener la columna Nombre_Empresa.")

    empresa_valor = empresa_seleccionada
    nit_auto = ""
    doc_id_auto = ""

    if empresa_seleccionada == "Otra":
        empresa_valor = str(empresa_manual or "").strip()
        nit_auto = str(nit_manual or "").strip()
        if "Doc_ID" in df_empresas.columns:
            filas_otra = df_empresas[
                df_empresas["Nombre_Empresa"].astype(str).str.strip().str.casefold() == "otra"
            ]
            if not filas_otra.empty:
                valor_doc = filas_otra["Doc_ID"].iloc[0]
                doc_id_auto = "" if pd.isna(valor_doc) else str(valor_doc).strip()
    elif empresa_seleccionada:
        filtro_empresa = (
            df_empresas["Nombre_Empresa"].astype(str).str.strip()
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

    st.session_state.empresa = empresa_valor
    st.session_state.nit = nit_auto
    st.session_state.empresa_seleccionada = empresa_seleccionada

    if doc_id_auto:
        info_plantilla = obtener_info_plantilla(doc_id_auto)
        st.session_state.doc_id_plantilla = info_plantilla["id"]
        st.session_state.nombre_plantilla = info_plantilla.get("name", "Documento sin nombre")
        st.session_state.plantilla_url = info_plantilla.get("webViewLink", "")
    else:
        st.session_state.doc_id_plantilla = ""
        st.session_state.nombre_plantilla = ""
        st.session_state.plantilla_url = ""
    return df_empresas, empresa_valor, nit_auto, doc_id_auto


def render_brand_header(width=190):
    """Encabezado común con marca y el stepper de seis etapas."""
    logo_app = obtener_logo_app_path()
    logo_uri = imagen_data_uri(logo_app)
    etapa_por_pantalla = {
        "pregunta1": 1, "pregunta2": 2, "verificar_saldo": 3,
        "monto_exacto": 3, "resultados": 4,
        "generando": 6, "whatsapp_entrega": 6, "pago": 6
    }
    etiquetas = ["Motivo", "Empresa", "Solicitud", "Resumen", "Confirmar", "Finalizar"]
    activa = etapa_por_pantalla.get(st.session_state.get("step", ""), 1)
    logo_html = f'<img src="{logo_uri}" alt="Cesantías al Instante">' if logo_uri else '<strong>Cesantías al Instante</strong>'
    st.markdown(
        '<div class="brand-header"><div class="brand-logo-wrap">' + logo_html + '</div>'
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
    st.markdown('<div class="journey-wrap"><div class="journey">' + ''.join(pasos_html) + '</div></div>', unsafe_allow_html=True)

def render_landing():
    """Pantalla de bienvenida con composición visual equivalente a la maqueta."""
    logo_uri = imagen_data_uri(obtener_logo_app_path())
    hero_uri = imagen_data_uri(obtener_imagen_hero_path())
    logo_html = f'<img src="{logo_uri}" alt="Cesantías al Instante">' if logo_uri else '<strong>Cesantías al Instante</strong>'
    hero_html = f'<img src="{hero_uri}" alt="Asesora de Cesantías al Instante">' if hero_uri else '<div class="hero-fallback">👩🏻‍💼</div>'
    st.markdown(f"""
    <section class="hero-shell">
      <div class="hero-copy">
        <div class="hero-logo">{logo_html}</div>
        <h1 class="hero-title">Tus cesantías,<span>más cerca de ti</span></h1>
        <p class="hero-description">Gestiona tu solicitud de retiro de cesantías de manera fácil, rápida y segura.</p>
        <div class="hero-benefits">
          <div class="hero-benefit"><i>ϟ</i> Rápido</div>
          <div class="hero-benefit"><i>✓</i> Seguro</div>
          <div class="hero-benefit"><i>✓</i> Fácil</div>
        </div>
      </div>
      <div class="hero-person">{hero_html}</div>
    </section>
    """, unsafe_allow_html=True)

    if st.button("Comenzar ahora  ➜", use_container_width=True, key="landing_start"):
        for key in [
            'proposito', 'monto', 'monto_limpio', 'fondo', 'nombre', 'cedula',
            'telefono', 'email', 'empresa', 'nit', 'ciudad', 'departamento',
            'empresa_manual', 'nit_manual', 'empresa_seleccionada',
            'saldo_verificado', 'saldo_limpio', 'solicitud_guardada',
            'doc_id_plantilla', 'nombre_plantilla', 'plantilla_url',
            'doc_id_copia', 'url_copia', 'solicitud_id', 'documento_rellenado',
            'pdf_id', 'pdf_url', 'pdf_generado'
        ]:
            st.session_state[key] = ""
        for key in ["ciudad_widget", "departamento_widget", "empresa_manual_widget", "nit_manual_widget",
                    "empresa_widget", "saldo_widget", "monto_raw_widget", "telefono_widget",
                    "nombre_widget", "cedula_widget", "email_widget"]:
            st.session_state[key] = ""
        st.session_state.step = 'pregunta1'
        st.rerun()

def render_pregunta1():
    render_brand_header()
    st.markdown('''
    <div class="glass-container">
      <div class="screen-heading"><div class="screen-icon">▣</div><div><h2>¿Cuál es el motivo de tu retiro?</h2><p>Selecciona la opción que mejor se ajuste a tu caso.</p></div></div>
    ''', unsafe_allow_html=True)

    motivos = [
        ("motivo_vivienda", "🏠  Vivienda\nCompra o mejora de vivienda", "Compra o mejora de vivienda"),
        ("motivo_educacion", "🎓  Educación\nEstudios propios o de tus hijos", "Estudios propios o de tus hijos"),
        ("motivo_salud", "✚  Salud\nTratamientos médicos", "Tratamientos médicos"),
        ("motivo_vacaciones", "🌴  Vacaciones\nDescanso y bienestar", "Descanso y bienestar"),
        ("motivo_vehiculo", "🚘  Vehículo\nCompra de vehículo", "Compra de vehículo"),
        ("motivo_otro", "•••  Otro motivo\nOtra razón válida", "Otro motivo")
    ]
    for inicio in range(0, len(motivos), 3):
        cols = st.columns(3, gap="small")
        for col, (key, label, value) in zip(cols, motivos[inicio:inicio + 3]):
            with col:
                texto = "✓ " + label if st.session_state.get("proposito") == value else label
                if st.button(texto, key=key, use_container_width=True):
                    st.session_state.proposito = value
                    st.rerun()

    if st.session_state.get("proposito"):
        st.success(f"Motivo seleccionado: {st.session_state.proposito}")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        if st.button("← Atrás", use_container_width=True):
            st.session_state.step = 'landing'
            st.rerun()
    with col2:
        if st.button("Siguiente  ➜", use_container_width=True, disabled=not bool(st.session_state.get("proposito"))):
            st.session_state.step = 'pregunta2'
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_pregunta2():
    """Etapa Empresa: conserva consulta de Empresas, NIT y Doc_ID, y selección de fondo."""
    render_brand_header()
    st.markdown('''
    <div class="glass-container">
      <div class="screen-heading"><div class="screen-icon">▦</div><div><h2>Empresa donde trabajas</h2><p>Selecciona tu empresa de la lista.</p></div></div>
    ''', unsafe_allow_html=True)

    lista_empresas = []
    df_empresas = pd.DataFrame()
    error_empresas = ""
    try:
        df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
        if "Nombre_Empresa" not in df_empresas.columns:
            raise ValueError("La hoja Empresas debe tener la columna Nombre_Empresa.")
        lista_empresas = df_empresas["Nombre_Empresa"].dropna().astype(str).str.strip().tolist()
        lista_empresas = [x for x in lista_empresas if x and x.casefold() != "otra"]
    except Exception as exc:
        error_empresas = str(exc)
        st.error(f"No fue posible cargar la lista de empresas: {exc}")

    empresa_seleccionada = st.selectbox(
        "Empresa", [""] + lista_empresas + ["Otra"], key="empresa_widget",
        placeholder="Selecciona tu empresa"
    )
    empresa_manual = ""
    nit_manual = ""
    if empresa_seleccionada == "Otra":
        st.info('Selecciona “Otra” para ingresar los datos manualmente.')
        manual_cols = st.columns(2)
        with manual_cols[0]:
            empresa_manual = st.text_input("Nombre de la empresa", placeholder="Nombre de la empresa", key="empresa_manual_widget")
        with manual_cols[1]:
            nit_manual = st.text_input("NIT de la empresa", placeholder="NIT de la empresa", key="nit_manual_widget")

    # El fondo de cesantías se conserva en esta etapa para que no se pierda la selección actual.
    st.markdown("### Fondo de cesantías")
    fondos = [
        {"key":"fondo_porv","nombre":"Porvenir","logo":"Porvenir_logo.png","emoji":"🏦"},
        {"key":"fondo_colf","nombre":"Colfondos","logo":"Colfondos_logo.png","emoji":"🏢"},
        {"key":"fondo_prot","nombre":"Protección","logo":"Proteccion_logo.png","emoji":"🛡️"},
        {"key":"fondo_fna","nombre":"FNA","logo":"FNA_logo.png","emoji":"🏛️"},
        {"key":"fondo_otro","nombre":"Otro","logo":None,"emoji":"❓"}
    ]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    for inicio in range(0, len(fondos), 3):
        cols = st.columns(3, gap="small")
        for col, fondo in zip(cols, fondos[inicio:inicio + 3]):
            with col:
                logo_path = None
                if fondo["logo"]:
                    base = os.path.splitext(fondo["logo"])[0].lower()
                    for carpeta in (assets_dir, os.path.join(assets_dir, "logos")):
                        if os.path.isdir(carpeta):
                            for archivo in os.listdir(carpeta):
                                b, ext = os.path.splitext(archivo)
                                if b.lower() in {base, base.replace("_logo", "")} and ext.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                                    logo_path = os.path.join(carpeta, archivo)
                                    break
                        if logo_path:
                            break
                if logo_path:
                    with open(logo_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("ascii")
                    mime = mimetypes.guess_type(logo_path)[0] or "image/png"
                    st.markdown(f'<div class="fund-logo-box"><img src="data:{mime};base64,{b64}" alt="{fondo["nombre"]}"></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="fund-emoji">{fondo["emoji"]}</div>', unsafe_allow_html=True)
                marcado = "✓ " if st.session_state.get("fondo") == fondo["nombre"] else ""
                if st.button(marcado + fondo["nombre"], key=fondo["key"], use_container_width=True):
                    st.session_state.fondo = fondo["nombre"]
                    st.rerun()

    nit_actual = ""
    if empresa_seleccionada:
        try:
            _, empresa_valor, nit_actual, _ = resolver_empresa_y_plantilla(
                empresa_seleccionada, empresa_manual, nit_manual
            )
            if nit_actual:
                st.caption(f"NIT: {nit_actual}")
        except Exception as exc:
            st.session_state.doc_id_plantilla = ""
            st.error(f"No se pudo validar la empresa o su plantilla: {exc}")

    col1, col2 = st.columns([1, 1.5])
    with col1:
        if st.button("← Atrás", use_container_width=True):
            st.session_state.step = 'pregunta1'
            st.rerun()
    with col2:
        siguiente_habilitado = bool(empresa_seleccionada and st.session_state.get("fondo"))
        if st.button("Siguiente  ➜", use_container_width=True, disabled=not siguiente_habilitado):
            if empresa_seleccionada == "Otra":
                if not empresa_manual.strip() or not nit_manual.strip():
                    st.error("Escribe el nombre y el NIT de tu empresa.")
                    st.stop()
                try:
                    resolver_empresa_y_plantilla(empresa_seleccionada, empresa_manual, nit_manual)
                except Exception as exc:
                    st.error(f"No se pudo validar la plantilla general: {exc}")
                    st.stop()
            elif empresa_seleccionada:
                resolver_empresa_y_plantilla(empresa_seleccionada)
            if not st.session_state.get("doc_id_plantilla"):
                st.error("Esta empresa no tiene una plantilla asignada. Verifica la columna Doc_ID en la hoja Empresas.")
                st.stop()
            st.session_state.empresa = empresa_manual.strip() if empresa_seleccionada == "Otra" else empresa_seleccionada
            st.session_state.nit = nit_manual.strip() if empresa_seleccionada == "Otra" else st.session_state.get("nit", "")
            st.session_state.step = 'monto_exacto'
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
    """Etapa Solicitud: reúne saldo, monto y datos personales en la misma pantalla."""
    render_brand_header()
    st.markdown('''
    <div class="glass-container">
      <div class="screen-heading"><div class="screen-icon">▤</div><div><h2>Datos de tu solicitud</h2><p>Completa tus datos para preparar la carta de retiro.</p></div></div>
    ''', unsafe_allow_html=True)

    numeros = {"Porvenir":"01 8000 111 222", "Colfondos":"01 8000 123 456", "Protección":"01 8000 789 012", "FNA":"01 8000 456 789", "Otro":"01 8000 000 000"}
    numero = numeros.get(st.session_state.get("fondo", "Otro"), "01 8000 000 000")
    st.markdown(f'<div class="phone-number">📞 {numero}</div>', unsafe_allow_html=True)
    st.info("Marca, presiona 1, digita tu cédula y escucha tu saldo. Luego escribe el saldo disponible para validar el monto.")
    saldo_raw = st.text_input("Saldo exacto disponible", placeholder="Ej: 10000000", key="saldo_widget")
    if saldo_raw:
        saldo_limpio_vista = re.sub(r"[^0-9]", "", saldo_raw)
        if saldo_limpio_vista:
            st.caption(f"Saldo ingresado: ${f'{int(saldo_limpio_vista):,}'.replace(',', '.')}")

    monto_raw = st.text_input(
        "Monto exacto a retirar", placeholder="Ej: 900000", key="monto_raw_widget",
        value=st.session_state.get("monto_raw_display", "")
    )
    if monto_raw:
        limpio_vista = re.sub(r"[^0-9]", "", monto_raw)
        if limpio_vista:
            st.caption(f"Monto a retirar: ${f'{int(limpio_vista):,}'.replace(',', '.')}")

    st.markdown("### Datos personales")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        cedula = st.text_input("Cédula", placeholder="Solo números", key="cedula_widget", on_change=limpiar_cedula_widget)
        telefono = st.text_input("Celular (WhatsApp)", placeholder="3001234567", key="telefono_widget", on_change=limpiar_telefono_widget)
        nombre = st.text_input("Nombre completo", placeholder="Como aparece en tu documento", key="nombre_widget")
    with col2:
        email = st.text_input("Correo electrónico", placeholder="tu@email.com", key="email_widget")
        departamentos_colombia = [
            "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá, D.C.", "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo", "Quindío", "Risaralda", "San Andrés y Providencia", "Santander", "Sucre", "Tolima", "Valle del Cauca", "Vaupés", "Vichada"
        ]
        departamento_valor = st.selectbox("Departamento", [""] + departamentos_colombia, key="departamento_widget", index=0)
        ciudad_valor = st.text_input("Ciudad", placeholder="Escribe tu ciudad", key="ciudad_widget")

    # Datos de empresa y plantilla fueron seleccionados en la pantalla anterior.
    empresa_seleccionada = st.session_state.get("empresa_seleccionada", "")
    empresa_valor = st.session_state.get("empresa", "")
    nit_auto = st.session_state.get("nit", "")

    col1, col2 = st.columns([1, 1.5])
    with col1:
        if st.button("← Atrás", use_container_width=True):
            st.session_state.step = 'pregunta2'
            st.rerun()
    with col2:
        if st.button("Siguiente  ➜", use_container_width=True):
            monto_raw_val = st.session_state.get("monto_raw_widget", "")
            saldo_raw_val = st.session_state.get("saldo_widget", "")
            telefono_val = st.session_state.get("telefono_widget", "")
            nombre_val = st.session_state.get("nombre_widget", "")
            cedula_val = st.session_state.get("cedula_widget", "")
            email_val = st.session_state.get("email_widget", "")

            if not monto_raw_val or not saldo_raw_val or not all([
                telefono_val, nombre_val, cedula_val, email_val, empresa_seleccionada,
                empresa_valor, nit_auto, ciudad_valor, departamento_valor
            ]):
                st.error("Completa el saldo, el monto, tus datos personales y el lugar de firma.")
                st.stop()
            if not st.session_state.get("doc_id_plantilla"):
                st.error("No se puede continuar porque la empresa no tiene una plantilla asignada en la hoja Empresas.")
                st.stop()

            telefono_val = re.sub(r"\D", "", str(telefono_val))
            cedula_val = re.sub(r"\D", "", str(cedula_val))
            email_val = str(email_val).strip()
            saldo_limpio = re.sub(r"[^0-9]", "", str(saldo_raw_val))
            monto_limpio = re.sub(r"[^0-9]", "", str(monto_raw_val))

            if len(telefono_val) != 10:
                st.error("El WhatsApp debe tener exactamente 10 dígitos.")
                st.stop()
            if not cedula_val:
                st.error("La cédula debe contener únicamente números.")
                st.stop()
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email_val):
                st.error("Ingresa un correo válido, con @ y un punto después del @.")
                st.stop()
            if not saldo_limpio or not monto_limpio:
                st.error("Ingresa valores numéricos válidos para saldo y monto.")
                st.stop()
            if int(monto_limpio) > int(saldo_limpio):
                st.error("El monto supera el saldo ingresado.")
                st.stop()

            st.session_state.saldo_limpio = saldo_limpio
            st.session_state.saldo_verificado = f"${f'{int(saldo_limpio):,}'.replace(',', '.')}"
            st.session_state.monto = f"{int(monto_limpio):,}".replace(",", ".")
            st.session_state.monto_limpio = monto_limpio
            st.session_state.telefono = telefono_val
            st.session_state.nombre = nombre_val.strip()
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
    render_brand_header()
    st.markdown('''
    <div class="glass-container">
      <div class="screen-heading"><div class="screen-icon">▤</div><div><h2>Resumen de tu solicitud</h2><p>Verifica que toda la información sea correcta.</p></div></div>
      <div class="summary-panel">
    ''', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.45, 1, 1], gap="medium")
    with col1:
        st.markdown('<div class="summary-check">✓</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"**Motivo:** {st.session_state.proposito}")
        st.markdown(f"**Empresa:** {st.session_state.empresa}")
        st.markdown(f"**NIT:** {st.session_state.nit}")
        st.markdown(f"**Fondo:** {st.session_state.fondo}")
        st.markdown(f"**Cédula:** {st.session_state.cedula}")
    with col3:
        st.markdown(f"**Celular:** {st.session_state.telefono}")
        st.markdown(f"**Correo:** {st.session_state.email}")
        st.markdown(f"**Ciudad:** {st.session_state.ciudad}, {st.session_state.departamento}")
        st.markdown(f"**Saldo disponible:** {st.session_state.saldo_verificado}")
        st.markdown(f"**Monto a retirar:** ${st.session_state.monto}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.info('Al hacer clic en “Confirmar solicitud”, registraremos tu solicitud y prepararemos la carta usando la plantilla asociada a tu empresa.')
    col1, col2 = st.columns([1, 1.6])
    with col1:
        if st.button("← Atrás", use_container_width=True):
            st.session_state.step = 'monto_exacto'
            st.rerun()
    with col2:
        if st.button("Confirmar solicitud  ✓", use_container_width=True):
            st.session_state.step = 'generando'
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_generando():
    """Crea registro, copia la plantilla, la rellena y exporta el PDF; luego muestra la confirmación."""
    render_brand_header()
    st.markdown('<div class="glass-container"><div class="screen-heading"><div class="screen-icon">✦</div><div><h2>Estamos preparando tu solicitud</h2><p>Estamos creando tu carta de retiro de cesantías.</p></div></div>', unsafe_allow_html=True)

    # ---------- GUARDAR SOLICITUD EN GOOGLE SHEETS ----------
    if not st.session_state.solicitud_guardada:
        solicitud_id = f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        st.session_state.solicitud_id = solicitud_id
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            existing_data = conn.read(worksheet="Solicitudes", ttl=0).dropna(how="all")
            nuevo_dato = pd.DataFrame([{
                "solicitud_id": solicitud_id, "fecha": fecha_actual,
                "nombre": st.session_state.nombre, "cedula": st.session_state.cedula,
                "telefono": st.session_state.telefono, "email": st.session_state.email,
                "nit": st.session_state.nit, "empresa": st.session_state.empresa,
                "fondo": st.session_state.fondo, "motivo": st.session_state.proposito,
                "monto": str(st.session_state.monto_limpio), "ciudad": st.session_state.ciudad,
                "departamento": st.session_state.departamento, "estado": "Pendiente"
            }])
            updated_df = pd.concat([existing_data, nuevo_dato], ignore_index=True)
            conn.update(worksheet="Solicitudes", data=updated_df)
            st.session_state.solicitud_guardada = True
        except Exception as e:
            st.error(f"Error guardando en Google Sheets: {e}")
            if st.button("Reintentar", key="retry_sheets"):
                st.rerun()
            st.stop()

    # ---------- COPIAR PLANTILLA EN GOOGLE DRIVE ----------
    if not st.session_state.doc_id_copia:
        try:
            copia = copiar_plantilla(st.session_state.doc_id_plantilla, st.session_state.solicitud_id, st.session_state.nombre)
            st.session_state.doc_id_copia = copia["id"]
            st.session_state.url_copia = copia.get("webViewLink", "")
        except Exception as e:
            st.error("La solicitud quedó guardada en Google Sheets, pero no se pudo copiar la plantilla. " + f"Detalle de Google Drive: {e}")
            st.info("Verifica que el administrador haya conectado la cuenta Gmail propietaria de la plantilla mediante OAuth, que esa cuenta tenga acceso de Editor y que refresh_token esté guardado en Streamlit Secrets.")
            if st.button("Reintentar copia de plantilla", key="retry_copy"):
                st.rerun()
            st.stop()

    # ---------- RELLENAR LA COPIA (NUNCA LA PLANTILLA ORIGINAL) ----------
    if not st.session_state.documento_rellenado:
        try:
            motivo = str(st.session_state.proposito or "").strip()
            motivo = re.sub(r"^[^\wÁÉÍÓÚáéíóúÑñ]+", "", motivo).strip()
            fecha_documento = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y")
            valores = {
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
            rellenar_plantilla_google_docs(st.session_state.doc_id_copia, valores)
            st.session_state.documento_rellenado = True
        except Exception as e:
            st.error("La copia se creó en Drive, pero no se pudieron reemplazar los marcadores del documento. " + f"Detalle: {e}")
            st.info("La plantilla original no fue modificada. Puedes corregir el problema y pulsar Reintentar para rellenar la copia existente.")
            if st.button("Reintentar rellenado del documento", key="retry_fill"):
                st.rerun()
            st.stop()

    # ---------- EXPORTAR PDF EN Solicitudes_Cesantias ----------
    if not st.session_state.pdf_generado:
        try:
            archivo_pdf = exportar_google_doc_a_pdf(st.session_state.doc_id_copia, st.session_state.solicitud_id, st.session_state.nombre)
            st.session_state.pdf_id = archivo_pdf["id"]
            st.session_state.pdf_url = archivo_pdf.get("webViewLink", f"https://drive.google.com/file/d/{archivo_pdf['id']}/view")
            st.session_state.pdf_generado = True
        except Exception as e:
            st.error("El documento Google Docs quedó creado y rellenado, pero no se pudo generar o guardar el PDF. " + f"Detalle: {e}")
            st.info("El documento editable permanece en Solicitudes_Cesantias. Puedes reintentar la generación del PDF sin crear otra copia del documento.")
            if st.button("Reintentar generación del PDF", key="retry_pdf"):
                st.rerun()
            st.stop()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <section class="success-shell">
      <div class="success-check">✓</div>
      <h1>¡Solicitud Enviada!</h1>
      <p>Tu solicitud de retiro de cesantías ha sido<br>procesada correctamente.</p>
      <div class="success-email">✉️ &nbsp; Recibirás la carta en tu correo electrónico en pocos minutos.</div>
      <p><strong>Número de solicitud:</strong> {st.session_state.solicitud_id}</p>
      <div class="footer-brand">Cesantías al Instante... siempre contigo</div>
    </section>
    """, unsafe_allow_html=True)
    if st.session_state.pdf_url:
        st.link_button("📄 Abrir o descargar mi carta (PDF)", st.session_state.pdf_url, use_container_width=True)
    if st.session_state.url_copia:
        st.link_button("Abrir documento editable", st.session_state.url_copia, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Volver al inicio", use_container_width=True):
            st.session_state.step = 'landing'
            st.rerun()
    with c2:
        if st.button("Ver entrega y pago", use_container_width=True):
            st.session_state.step = 'whatsapp_entrega'
            st.rerun()

def render_whatsapp_entrega():
    render_brand_header()
    st.markdown('<div class="glass-container" style="text-align:center"><div class="screen-heading" style="justify-content:center"><div class="screen-icon">✉</div><div><h2>Tu carta está lista</h2><p>Vista previa de la entrega de tu solicitud.</p></div></div>', unsafe_allow_html=True)
    st.info(f"Hola {st.session_state.nombre}. La copia de tu plantilla quedó creada para la solicitud {st.session_state.solicitud_id}.")
    if st.session_state.pdf_url:
        st.link_button("📄 Abrir o descargar PDF", st.session_state.pdf_url, use_container_width=True)
    if st.session_state.url_copia:
        st.link_button("Abrir copia de la plantilla", st.session_state.url_copia, use_container_width=True)
    if st.button("Continuar al pago", use_container_width=True):
        st.session_state.step = 'pago'
        st.rerun()
    if st.button("Volver a la confirmación", use_container_width=True):
        st.session_state.step = 'generando'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_pago():
    render_brand_header()
    st.markdown('<div class="glass-container" style="text-align:center"><div class="screen-heading" style="justify-content:center"><div class="screen-icon">$</div><div><h2>Pago con Nequi</h2><p>Realiza el pago de $20.000 COP al número:</p></div></div><div class="phone-number" style="background:linear-gradient(135deg,#7B2FBE,#9B4DCA)">📱 312 679 3911</div>', unsafe_allow_html=True)
    if st.button("Ya pagué, finalizar", use_container_width=True):
        st.session_state.step = 'landing'
        st.success("¡Gracias! Proceso finalizado.")
        st.rerun()
    if st.button("Volver a la solicitud", use_container_width=True):
        st.session_state.step = 'generando'
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
