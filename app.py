import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import base64
import mimetypes
import html
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

# ---------- SISTEMA VISUAL PREMIUM: CESANTÍAS AL INSTANTE ----------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root{
 --cia-navy:#062b68;--cia-blue:#086fd0;--cia-cyan:#10bce8;--cia-gold:#ffb51b;
 --cia-ink:#18345b;--cia-muted:#60748d;--cia-line:#d8e6f4;--cia-pale:#eff7ff;
}
html,body,[class*="css"],.stApp{font-family:Inter,Arial,sans-serif!important}

/* IMPORTANTE: cada st.markdown(<style>) crea un wrapper vacío en el flujo vertical
   de Streamlit. Los 15 bloques CSS acumulaban separaciones y generaban la franja azul.
   Se oculta únicamente el wrapper que contiene una hoja de estilos; las reglas CSS
   permanecen activas y los componentes visibles de la aplicación no se modifican. */
div[data-testid="stElementContainer"]:has(style) {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}
#MainMenu,footer,header{visibility:hidden}
.stApp{background:linear-gradient(118deg,#06295f 0%,#07539a 53%,#079dcc 100%)!important;color:var(--cia-ink)!important}
.main .block-container{max-width:1160px!important;padding:1.1rem clamp(.65rem,2.2vw,1.6rem) 2.6rem!important}
[data-testid="stToolbar"], [data-testid="stDecoration"]{display:none!important}
/* Encabezado y navegación */
.brand-header{max-width:1080px;margin:0 auto .7rem;padding:.62rem 1.05rem;display:flex;align-items:center;justify-content:space-between;gap:1rem;background:#fff;border:1px solid #deebf7;border-radius:18px;box-shadow:0 8px 26px #001b4930}
.brand-logo-wrap{display:flex;align-items:center;min-width:0}
.brand-logo-wrap img{display:block;max-height:58px;width:auto;max-width:min(62vw,330px);object-fit:contain}
.brand-trust{display:flex;align-items:center;gap:.5rem;color:var(--cia-navy);font-size:.82rem;font-weight:800;white-space:nowrap}
.brand-trust span{display:inline-flex;width:29px;height:29px;border-radius:50%;align-items:center;justify-content:center;color:#fff;background:linear-gradient(140deg,var(--cia-blue),var(--cia-cyan));font-size:1rem}
.journey-wrap{max-width:1080px;margin:0 auto .85rem;padding:.72rem .85rem .6rem;background:#ffffffed;border:1px solid #d9e7f4;border-radius:16px;box-shadow:0 8px 24px #001b4920}
.journey{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:.25rem}
.journey-step{position:relative;display:flex;flex-direction:column;align-items:center;gap:.32rem;text-align:center;color:#60758c;font-size:.71rem;font-weight:800}
.journey-step:not(:first-child):before{content:"";position:absolute;height:2px;background:#d5e0ec;left:-50%;right:50%;top:14px;z-index:0}
.journey-dot{position:relative;z-index:1;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#e5edf5;color:#546a82;font-size:.78rem;font-weight:900;border:2px solid #fff;box-shadow:0 0 0 1px #d2deeb}
.journey-step.active{color:var(--cia-navy);font-weight:900}
.journey-step.active .journey-dot{color:white;background:linear-gradient(135deg,var(--cia-blue),var(--cia-cyan));box-shadow:0 0 0 2px #d7efff,0 4px 12px #0874d844}
.journey-step.done{color:#087bb8}
.journey-step.done .journey-dot{color:#fff;background:#11b9dc}
/* Contenedores de contenido */
.st-key-screen_fund,.st-key-screen_data,.st-key-screen_summary,.st-key-screen_mission,.st-key-screen_company,.st-key-screen_processing,.st-key-screen_success{
 background:linear-gradient(180deg,#fff 0%,#fafdff 75%,#f0f8ff 100%)!important;
 border:1px solid #d9e8f5!important;border-radius:26px!important;
 padding:clamp(1.05rem,2.8vw,2.2rem)!important;
 box-shadow:0 18px 55px #001b4933!important;
}
.st-key-summary_panel{padding:1.05rem!important;border:1px solid #d2e3f2!important;border-radius:20px!important;background:linear-gradient(135deg,#fff,#f0f7ff)!important;box-shadow:0 8px 22px #082b6610!important}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid #d7e6f4!important;border-radius:20px!important;background:linear-gradient(180deg,#fff,#f5faff)!important;box-shadow:0 7px 20px #062b6810!important}
.st-key-screen_fund [data-testid="stVerticalBlock"],.st-key-screen_data [data-testid="stVerticalBlock"],.st-key-screen_summary [data-testid="stVerticalBlock"],.st-key-screen_mission [data-testid="stVerticalBlock"],.st-key-screen_company [data-testid="stVerticalBlock"]{gap:.8rem!important}
.page-shell{position:relative;isolation:isolate;overflow:hidden;max-width:1080px;margin:.65rem auto 1rem;padding:clamp(1.1rem,2.8vw,2.2rem);border-radius:26px;background:linear-gradient(180deg,#fff 0%,#fafdff 75%,#f0f8ff 100%);border:1px solid #d9e8f5;box-shadow:0 18px 55px #001b4933}
.page-shell:after{content:"";position:absolute;z-index:-1;pointer-events:none;width:250px;height:58px;right:-60px;bottom:-32px;transform:rotate(-9deg);border-radius:80% 0 0 0;background:linear-gradient(90deg,var(--cia-cyan),var(--cia-blue),var(--cia-navy))}
.screen-heading{display:flex;align-items:center;gap:.9rem;margin:.1rem 0 1.35rem}
.screen-icon{width:54px;height:54px;flex:0 0 54px;display:flex;align-items:center;justify-content:center;border-radius:16px;color:#fff;background:linear-gradient(145deg,#0879df,#05bce8);box-shadow:0 8px 20px #0874d833}
.screen-icon svg{width:27px;height:27px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.screen-heading h2{margin:0;color:var(--cia-navy);font-size:clamp(1.35rem,2.8vw,1.9rem);font-weight:900;letter-spacing:-.035em;line-height:1.15}
.screen-heading p{margin:.28rem 0 0;color:#526984;font-size:.96rem;line-height:1.45}
.eyebrow{display:inline-flex;align-items:center;gap:.4rem;padding:.4rem .72rem;border-radius:100px;color:#076db7;background:#e7f6ff;font-size:.72rem;font-weight:850;letter-spacing:.05em;text-transform:uppercase}
/* Portada integrada: CTA dentro del mismo panel */
.hero-shell{position:relative;isolation:isolate;display:grid;grid-template-columns:1.04fr .96fr;max-width:1080px;min-height:545px;margin:.3rem auto 1rem;overflow:hidden;border-radius:27px;background:linear-gradient(135deg,#062c6c 0%,#073c8b 60%,#086fbd 100%);border:1px solid #1595df;box-shadow:0 22px 60px #00183e55}
.hero-shell:before{content:"";position:absolute;z-index:0;left:-7%;top:-20%;width:67%;height:44%;border-radius:0 0 75% 10%;background:linear-gradient(135deg,#fff 0%,#f2fbff 72%,#c1ebff 100%);transform:rotate(-5deg)}
.hero-shell:after{content:"";position:absolute;z-index:3;right:-4%;bottom:-45px;width:64%;height:92px;transform:rotate(-8deg);border-radius:80% 0 0 0;border-top:16px solid #08c6ee;pointer-events:none}
.hero-copy{position:relative;z-index:2;display:flex;flex-direction:column;align-items:flex-start;padding:1.15rem clamp(1.25rem,3vw,2rem) 1.55rem}
.hero-logo{display:flex;align-items:center;justify-content:flex-start;width:min(100%,390px);height:112px;margin:-.2rem 0 1.15rem}
.hero-logo img{display:block;max-width:100%;max-height:108px;object-fit:contain;object-position:left center;border-radius:7px}
.hero-title{margin:.15rem 0 .85rem;color:#fff;font-size:clamp(2.1rem,4vw,3.4rem);font-weight:950;letter-spacing:-.055em;line-height:1.03}
.hero-title span{display:block;color:#13d0f2}
.hero-description{max-width:470px;margin:0 0 1.1rem;color:#e9f5ff;font-size:clamp(1rem,1.6vw,1.18rem);line-height:1.5}
.hero-benefits{display:grid;gap:.65rem;margin:.25rem 0 1.35rem;color:white;font-size:1.08rem;font-weight:800}
.hero-benefit{display:flex;align-items:center;gap:.7rem}
.hero-benefit i{font-style:normal;width:35px;height:35px;flex:0 0 35px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#12c7e8;color:#043c86;font-size:1.05rem;font-weight:950}
.hero-cta{display:inline-flex;align-items:center;justify-content:center;gap:.55rem;min-height:52px;max-width:100%;padding:.8rem 1.9rem;border-radius:100px;color:#082c68!important;background:linear-gradient(110deg,#ffda55,#ffad00);font-size:1.02rem;font-weight:900;text-decoration:none!important;box-shadow:0 10px 26px #ffb51b55;transition:transform .18s,box-shadow .18s}
.hero-cta:hover{transform:translateY(-3px);box-shadow:0 14px 30px #ffb51b77}
.hero-person{position:relative;min-height:545px;align-self:stretch;overflow:hidden;border-radius:0 0 0 105px}
.hero-person picture{position:absolute;inset:0;display:block;width:100%;height:100%}
.hero-person img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 20%}
.hero-person:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#07377f 0%,transparent 27%),linear-gradient(0deg,#00499a22,transparent 48%);pointer-events:none}
/* Tarjetas e inputs */
.fund-card{min-height:195px;padding:1rem .95rem .85rem;border:1px solid #d7e6f4;border-radius:20px;background:linear-gradient(180deg,#fff,#f4faff);box-shadow:0 7px 20px #062b6810;text-align:center}
.fund-logo-box{height:92px;display:flex;align-items:center;justify-content:center;margin:0 auto .55rem;padding:.35rem;background:#fff;border-radius:13px}
.fund-logo-box img{display:block;max-width:100%;max-height:82px;object-fit:contain}
.fund-fallback{height:92px;display:flex;align-items:center;justify-content:center;color:#0875d2}
.fund-fallback svg{width:55px;height:55px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.fund-name{margin:.15rem 0 .6rem;color:var(--cia-navy);font-size:1.02rem;font-weight:900}
.personal-tip{display:flex;gap:.9rem;align-items:center;padding:.95rem 1.1rem;margin:0 0 1.1rem;border:1px solid #bfe5fa;border-radius:17px;background:linear-gradient(110deg,#eaf7ff,#d9f4ff)}
.personal-tip-icon{width:48px;height:48px;flex:0 0 48px;display:flex;align-items:center;justify-content:center;border-radius:14px;color:#fff;background:linear-gradient(145deg,#0874d8,#10bde8);font-size:1.25rem;font-weight:900}
.personal-tip strong{display:block;color:#073575;font-size:1.05rem;font-weight:900}
.personal-tip p{margin:.15rem 0 0;color:#47627d;font-size:.86rem;line-height:1.45}
.section-label{display:flex;align-items:center;gap:.55rem;margin:.85rem 0 .6rem;color:var(--cia-navy);font-size:1.03rem;font-weight:900}
.section-label svg{width:21px;height:21px;stroke:#0878d2;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.field-label{display:flex;align-items:center;gap:.48rem;margin:.52rem 0 .22rem;color:#10376f;font-size:.88rem;font-weight:850}
.field-label svg{width:18px;height:18px;stroke:#0878d2;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:0 0 18px}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label,[data-testid="stWidgetLabel"] span,[data-testid="stTextInput"] label,[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label{color:var(--cia-navy)!important;font-weight:800!important;opacity:1!important}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] [data-baseweb="select"]>div{min-height:48px;border:1.5px solid #c9dced!important;border-radius:13px!important;background:#fff!important;color:#17345c!important;box-shadow:0 2px 6px #082b6608}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:#0876d3!important;box-shadow:0 0 0 3px #0876d322!important}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{color:#8093a9!important;opacity:1!important}
[data-testid="stSelectbox"] [data-baseweb="select"] *{color:#18345b!important}
[data-testid="stCaptionContainer"] p,.stCaption{color:#58708b!important;opacity:1!important}
.stButton>button,[data-testid="stDownloadButton"] button,[data-testid="stLinkButton"] a{min-height:48px;border:1px solid #0874d8!important;border-radius:14px!important;padding:.7rem 1.1rem!important;color:#fff!important;background:linear-gradient(110deg,#073b8a,#0874d4 70%,#0aa6dc)!important;font-weight:850!important;font-size:.96rem!important;box-shadow:0 8px 19px #084a9728!important;transition:transform .16s,box-shadow .16s!important}
.stButton>button:hover,[data-testid="stDownloadButton"] button:hover{transform:translateY(-2px);box-shadow:0 12px 25px #084a9738!important}
.stButton>button:disabled{opacity:.48!important;transform:none!important}
/* Botones principales y secundarios por clave de widget */
.st-key-fund_back button,.st-key-data_back button,.st-key-summary_back button,.st-key-mission_back button,.st-key-company_back button{background:#fff!important;color:#0752a0!important;border:1.5px solid #8fc6f0!important;box-shadow:none!important}
.st-key-company_submit button,.st-key-summary_continue button,.st-key-mission_continue button,.st-key-data_continue button{background:linear-gradient(110deg,#073b8a,#0874d4 70%,#0aa6dc)!important}
/* Tarjetas informativas / resumen / misión / confirmación */
.summary-panel{padding:1.2rem;border:1px solid #d2e3f2;border-radius:20px;background:linear-gradient(135deg,#fff,#f0f7ff);box-shadow:0 8px 22px #082b6610}
.summary-check{width:72px;height:72px;margin:.2rem auto .8rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#22c83d,#0fa52f);color:#fff;font-size:2.8rem;font-weight:950;box-shadow:0 10px 24px #18b83733}
.summary-item{padding:.7rem .8rem;margin:.3rem 0;border:1px solid #e0ebf5;border-radius:12px;background:#fff}
.summary-item small{display:block;color:#526981;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em}
.summary-item strong{display:block;color:#102f60;font-size:.97rem;font-weight:850;overflow-wrap:anywhere}
.mission-hero{padding:1.25rem 1.35rem;margin:.2rem 0 1rem;border-radius:20px;background:linear-gradient(120deg,#062e70,#0879cf);color:#fff}
.mission-hero h3{margin:0 0 .5rem;color:#fff;font-size:1.45rem;font-weight:900}
.mission-hero p{margin:0;color:#e9f6ff;line-height:1.6}
.mission-card{height:100%;padding:1rem;border-radius:17px;border:1px solid #d8e7f4;background:#fff;box-shadow:0 6px 18px #082b660d}
.mission-card .mission-symbol{width:43px;height:43px;margin-bottom:.65rem;display:flex;align-items:center;justify-content:center;border-radius:13px;color:#fff;background:linear-gradient(145deg,#0878d8,#12bce8);font-size:1.2rem;font-weight:900}
.mission-card .mission-symbol svg{width:23px;height:23px;stroke:white;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.mission-card strong{display:block;color:var(--cia-navy);font-size:.98rem;font-weight:900}
.mission-card p{margin:.35rem 0 0;color:#5b7189;font-size:.85rem;line-height:1.5}
.success-shell{max-width:1080px;margin:.55rem auto 1rem;padding:clamp(1.35rem,4vw,3rem);border-radius:26px;background:radial-gradient(circle at 50% 12%,#e2f4ff,#fff 58%,#eef8ff);border:1px solid #d3e5f4;box-shadow:0 18px 50px #00194135;text-align:center;position:relative;overflow:hidden}
.success-check{width:92px;height:92px;margin:.2rem auto .9rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#12bce9,#0756c4);color:#fff;font-size:3.5rem;font-weight:950;box-shadow:0 10px 25px #0874d833}
.success-shell h1{color:var(--cia-navy);font-size:clamp(2rem,4vw,3rem);font-weight:950;letter-spacing:-.04em;margin:.2rem 0 .5rem}
.success-shell p{color:#173d76;font-size:1.04rem;line-height:1.55}
.success-delivery{max-width:740px;margin:1.1rem auto;padding:1rem 1.15rem;border-radius:16px;background:#dff1ff;color:#083a7b;font-weight:750;text-align:left;line-height:1.55}
.footer-brand{text-align:center;color:#063574;font-weight:850;font-style:italic;margin-top:1.25rem}
[data-testid="stAlert"]{border-radius:14px!important;border:1px solid #cfe4f5!important}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],[data-testid="stAlert"] p,[data-testid="stAlert"] span{color:#52657b!important;opacity:1!important}
/* Ajustes tablet y teléfono */
@media(max-width:760px){
 .main .block-container{padding:.55rem .45rem 1.5rem!important}
 .brand-header{padding:.45rem .65rem;border-radius:14px;margin-bottom:.5rem}
 .brand-logo-wrap img{max-height:47px;max-width:62vw}
 .brand-trust{font-size:.66rem;gap:.25rem}.brand-trust span{width:23px;height:23px}
 .journey-wrap{padding:.55rem .18rem;border-radius:12px}
 .journey{gap:0}.journey-step{font-size:.56rem;gap:.22rem}.journey-dot{width:25px;height:25px;font-size:.68rem}
 .journey-step:not(:first-child):before{top:12px}
 .page-shell{padding:1.05rem .8rem;margin:.4rem 0;border-radius:19px}
 .st-key-screen_fund,.st-key-screen_data,.st-key-screen_summary,.st-key-screen_mission,.st-key-screen_company,.st-key-screen_processing,.st-key-screen_success{padding:1.05rem .8rem!important;border-radius:19px!important}
 .st-key-summary_panel{padding:.75rem!important}
 .screen-heading{gap:.65rem;margin-bottom:1rem}.screen-icon{width:46px;height:46px;flex-basis:46px;border-radius:13px}.screen-icon svg{width:23px;height:23px}
 .screen-heading h2{font-size:1.28rem}.screen-heading p{font-size:.84rem}
 .hero-shell{grid-template-columns:1fr;min-height:0;margin:.15rem auto;border-radius:19px}
 .hero-person{grid-row:1;min-height:290px;max-height:330px;border-radius:0 0 55px 0}
 .hero-person img{object-position:center 24%}
 .hero-copy{grid-row:2;padding:.85rem 1rem 1.25rem}
 .hero-shell:before{top:285px;left:-8%;width:90%;height:27%;border-radius:60%}
 .hero-logo{height:77px;width:min(100%,280px);margin:-.25rem 0 .45rem}.hero-logo img{max-height:74px}
 .hero-title{font-size:2.18rem;margin:.1rem 0 .55rem}.hero-description{font-size:.96rem;margin-bottom:.65rem}
 .hero-benefits{display:flex;flex-wrap:wrap;gap:.55rem;font-size:.82rem;margin:.4rem 0 1rem}.hero-benefit{gap:.35rem}.hero-benefit i{width:28px;height:28px;flex-basis:28px;font-size:.86rem}
 .hero-cta{min-height:48px;padding:.72rem 1.45rem;font-size:.94rem;align-self:flex-start;width:auto}
 .fund-card{min-height:170px;padding:.75rem .55rem}.fund-logo-box,.fund-fallback{height:76px}.fund-logo-box img{max-height:69px}
 .personal-tip{align-items:flex-start;padding:.75rem}.personal-tip-icon{width:40px;height:40px;flex-basis:40px}
 .summary-panel{padding:.8rem}
 .mission-card{margin-bottom:.55rem}
 .success-shell{padding:1.25rem .8rem;border-radius:19px}
 [data-testid="stTextInput"] input,[data-testid="stSelectbox"] [data-baseweb="select"]{font-size:16px!important}
 .stButton>button{min-height:47px;font-size:.9rem!important}
}
@media(max-width:390px){.brand-trust{display:none}.journey-step{font-size:.49rem}.journey-dot{width:22px;height:22px}.journey-step:not(:first-child):before{top:10px}.hero-person{min-height:250px;max-height:280px}.hero-title{font-size:1.95rem}}

/* ---------- CORRECCIÓN DEFINITIVA DE CONTRASTE Y PANELES ---------- */
.main .block-container,
div[data-testid="stMainBlockContainer"] {
  width:calc(100% - 2rem)!important; max-width:1160px!important;
  margin-left:auto!important; margin-right:auto!important;
  padding-left:clamp(.55rem,2vw,1.25rem)!important;
  padding-right:clamp(.55rem,2vw,1.25rem)!important;
}
.st-key-screen_fund,
.st-key-screen_data,
.st-key-screen_summary,
.st-key-screen_mission,
.st-key-screen_company,
.st-key-screen_processing,
.st-key-screen_success {
  display:block!important; width:100%!important; max-width:1080px!important;
  margin:.65rem auto 1rem!important; box-sizing:border-box!important;
  color:#17345b!important;
  background:linear-gradient(180deg,#ffffff 0%,#fbfdff 72%,#f1f8ff 100%)!important;
  border:1px solid #cbdff0!important; border-radius:25px!important;
  padding:clamp(1.05rem,2.6vw,2rem)!important;
  box-shadow:0 18px 48px rgba(0,24,68,.22)!important;
}
.st-key-summary_panel {
  display:block!important; box-sizing:border-box!important; width:100%!important;
  color:#17345b!important; background:linear-gradient(135deg,#fff,#f4f9ff)!important;
  border:1px solid #d2e3f2!important; border-radius:18px!important;
  padding:clamp(.8rem,2vw,1.2rem)!important;
}
.st-key-screen_fund [data-testid="stMarkdownContainer"] p,
.st-key-screen_data [data-testid="stMarkdownContainer"] p,
.st-key-screen_summary [data-testid="stMarkdownContainer"] p,
.st-key-screen_mission [data-testid="stMarkdownContainer"] p,
.st-key-screen_company [data-testid="stMarkdownContainer"] p,
.st-key-screen_processing [data-testid="stMarkdownContainer"] p {
  color:#40566f!important; opacity:1!important; line-height:1.55!important;
}
.st-key-screen_fund .screen-heading h2,
.st-key-screen_data .screen-heading h2,
.st-key-screen_summary .screen-heading h2,
.st-key-screen_mission .screen-heading h2,
.st-key-screen_company .screen-heading h2,
.st-key-screen_processing .screen-heading h2 {
  color:#082e6b!important; opacity:1!important; font-weight:900!important;
}
.st-key-screen_fund .screen-heading p,
.st-key-screen_data .screen-heading p,
.st-key-screen_summary .screen-heading p,
.st-key-screen_mission .screen-heading p,
.st-key-screen_company .screen-heading p,
.st-key-screen_processing .screen-heading p { color:#405873!important; opacity:1!important; }
.st-key-screen_fund .section-label,
.st-key-screen_data .section-label,
.st-key-screen_company .section-label,
.st-key-screen_fund .field-label,
.st-key-screen_data .field-label,
.st-key-screen_company .field-label {
  color:#12396e!important; opacity:1!important; font-weight:850!important;
}
.st-key-screen_fund [data-testid="stWidgetLabel"],
.st-key-screen_data [data-testid="stWidgetLabel"],
.st-key-screen_company [data-testid="stWidgetLabel"],
.st-key-screen_fund [data-testid="stWidgetLabel"] *,
.st-key-screen_data [data-testid="stWidgetLabel"] *,
.st-key-screen_company [data-testid="stWidgetLabel"] * {
  color:#16375f!important; opacity:1!important; font-weight:800!important;
}
.st-key-screen_fund [data-testid="stTextInput"] input,
.st-key-screen_data [data-testid="stTextInput"] input,
.st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.st-key-screen_company [data-testid="stTextInput"] input,
.st-key-screen_company [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  color:#172f4f!important; background:#fff!important; border:1.5px solid #b9cee2!important;
  min-height:48px!important; opacity:1!important; border-radius:12px!important;
}
.st-key-screen_data [data-testid="stTextInput"] input::placeholder,
.st-key-screen_company [data-testid="stTextInput"] input::placeholder {
  color:#71849a!important; opacity:1!important;
}
.st-key-screen_fund [data-testid="stCaptionContainer"] p,
.st-key-screen_data [data-testid="stCaptionContainer"] p,
.st-key-screen_summary [data-testid="stCaptionContainer"] p,
.st-key-screen_mission [data-testid="stCaptionContainer"] p,
.st-key-screen_company [data-testid="stCaptionContainer"] p {
  color:#52677f!important; opacity:1!important;
}
.st-key-screen_summary [data-testid="stAlert"] p,
.st-key-screen_company [data-testid="stAlert"] p {
  color:#234565!important; opacity:1!important;
}
/* CTA real de Streamlit, anclado dentro de la tarjeta de bienvenida. */
.st-key-landing_wrap {position:relative!important;max-width:1080px!important;width:100%!important;margin:.3rem auto 1rem!important;overflow:visible!important}
.st-key-landing_wrap .hero-shell {width:100%!important;max-width:1080px!important;margin:0 auto!important}
.st-key-landing_start {
  position:absolute!important; z-index:12!important; left:clamp(1.25rem,3vw,2rem)!important;
  bottom:1.45rem!important; max-width:230px!important; margin:0!important;
}
.st-key-landing_start button {
  display:inline-flex!important; width:auto!important; min-width:205px!important;
  min-height:52px!important; justify-content:center!important; align-items:center!important;
  padding:.8rem 1.7rem!important; border:0!important; border-radius:999px!important;
  color:#082c68!important; background:linear-gradient(110deg,#ffda55,#ffad00)!important;
  font-size:1.02rem!important; font-weight:900!important;
  box-shadow:0 10px 26px rgba(255,181,27,.36)!important;
}
.st-key-landing_start button:hover { transform:translateY(-2px)!important; }
/* Quitar bordes grises genéricos de los contenedores principales; las tarjetas internas sí conservan su diseño. */
.st-key-screen_fund > div,
.st-key-screen_data > div,
.st-key-screen_summary > div,
.st-key-screen_mission > div,
.st-key-screen_company > div,
.st-key-screen_processing > div { background:transparent!important; }
@media(max-width:760px){
 .st-key-screen_fund,.st-key-screen_data,.st-key-screen_summary,
 .st-key-screen_mission,.st-key-screen_company,.st-key-screen_processing,
 .st-key-screen_success {width:100%!important;max-width:100%!important;margin:.4rem auto!important;padding:1rem .8rem!important;border-radius:19px!important}
 .st-key-landing_wrap {margin:.15rem auto .8rem!important}
 .st-key-landing_start {left:1rem!important;bottom:1.1rem!important;max-width:220px!important}
 .st-key-landing_start button {min-width:195px!important;min-height:49px!important;font-size:.95rem!important}
}


/* ---------- PORTADA V1: AJUSTE ESPECÍFICO DE LA PANTALLA 1 ---------- */
.hero-shell{
  grid-template-columns:minmax(0,1.04fr) minmax(0,.96fr)!important;
  min-height:600px!important;
  align-items:stretch!important;
}
.hero-copy{
  min-width:0!important;
  padding:1rem clamp(1.15rem,2.7vw,1.85rem) 5.1rem!important;
  justify-content:flex-start!important;
}
.hero-logo{
  height:98px!important;
  width:min(100%,370px)!important;
  margin:-.12rem 0 .62rem!important;
}
.hero-logo img{max-height:94px!important;max-width:100%!important}
.hero-title{
  font-size:clamp(2.25rem,3.55vw,3.1rem)!important;
  line-height:1.02!important;
  margin:.05rem 0 .62rem!important;
}
.hero-description{
  max-width:440px!important;
  font-size:clamp(.98rem,1.35vw,1.08rem)!important;
  line-height:1.42!important;
  margin:0 0 .72rem!important;
}
.hero-benefits{
  display:grid!important;
  gap:.48rem!important;
  margin:.12rem 0 .25rem!important;
  font-size:1rem!important;
}
.hero-benefit{gap:.62rem!important}
.hero-benefit i{width:32px!important;height:32px!important;flex-basis:32px!important}
.hero-person{min-height:600px!important;height:100%!important}
.st-key-landing_start{bottom:1.15rem!important}

@media(max-width:760px){
  /* En teléfono la foto permanece al lado derecho: nunca se apila encima del texto. */
  .st-key-landing_wrap{max-width:100%!important;width:100%!important;margin:.1rem auto .75rem!important}
  .st-key-landing_wrap .hero-shell{
    display:grid!important;
    grid-template-columns:minmax(0,1.12fr) minmax(0,.88fr)!important;
    grid-template-rows:minmax(600px,auto)!important;
    min-height:600px!important;
    height:auto!important;
    border-radius:18px!important;
  }
  .st-key-landing_wrap .hero-copy{
    grid-column:1!important;grid-row:1!important;
    display:flex!important;flex-direction:column!important;
    align-items:flex-start!important;justify-content:flex-start!important;
    min-width:0!important;
    padding:.72rem .55rem 4.55rem!important;
  }
  .st-key-landing_wrap .hero-person{
    grid-column:2!important;grid-row:1!important;
    display:block!important;
    min-width:0!important;min-height:600px!important;height:100%!important;max-height:none!important;
    border-radius:0 0 0 48px!important;
  }
  .st-key-landing_wrap .hero-person img{
    position:absolute!important;inset:0!important;width:100%!important;height:100%!important;
    object-fit:cover!important;object-position:50% 18%!important;
  }
  .st-key-landing_wrap .hero-person:after{
    background:linear-gradient(90deg,rgba(5,48,112,.12),transparent 32%),linear-gradient(0deg,rgba(0,49,122,.12),transparent 42%)!important;
  }
  .st-key-landing_wrap .hero-shell:before{
    top:-15%!important;left:-17%!important;width:118%!important;height:34%!important;
    border-radius:0 0 65% 10%!important;
  }
  .st-key-landing_wrap .hero-shell:after{
    right:-13%!important;bottom:-34px!important;width:93%!important;height:66px!important;
    border-top-width:11px!important;
  }
  .st-key-landing_wrap .hero-logo{
    height:72px!important;width:100%!important;max-width:none!important;
    margin:-.08rem 0 .48rem!important;
  }
  .st-key-landing_wrap .hero-logo img{
    max-height:68px!important;max-width:100%!important;object-position:left center!important;
  }
  .st-key-landing_wrap .hero-title{
    font-size:clamp(1.48rem,6vw,1.9rem)!important;
    line-height:1.02!important;letter-spacing:-.045em!important;
    margin:.02rem 0 .52rem!important;
    overflow-wrap:normal!important;
  }
  .st-key-landing_wrap .hero-title span{display:block!important}
  .st-key-landing_wrap .hero-description{
    max-width:none!important;font-size:clamp(.76rem,3.1vw,.88rem)!important;
    line-height:1.34!important;margin:0 0 .62rem!important;
    color:#f5faff!important;overflow-wrap:break-word!important;
  }
  .st-key-landing_wrap .hero-benefits{
    display:grid!important;grid-template-columns:1fr!important;
    gap:.42rem!important;margin:.1rem 0 .2rem!important;
    font-size:clamp(.72rem,2.9vw,.82rem)!important;line-height:1.1!important;
  }
  .st-key-landing_wrap .hero-benefit{display:flex!important;align-items:center!important;gap:.38rem!important;white-space:nowrap!important}
  .st-key-landing_wrap .hero-benefit i{
    width:25px!important;height:25px!important;flex:0 0 25px!important;font-size:.78rem!important;
  }
  .st-key-landing_start{
    left:.58rem!important;bottom:.62rem!important;
    width:calc(56% - .95rem)!important;max-width:190px!important;
    margin:0!important;z-index:15!important;
  }
  .st-key-landing_start button{
    width:100%!important;min-width:0!important;min-height:46px!important;
    padding:.55rem .4rem!important;font-size:clamp(.76rem,3vw,.88rem)!important;
    white-space:nowrap!important;border-radius:999px!important;
  }
}
@media(max-width:390px){
  .st-key-landing_wrap .hero-shell{grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr)!important;grid-template-rows:minmax(590px,auto)!important;min-height:590px!important}
  .st-key-landing_wrap .hero-copy{padding:.62rem .46rem 4.35rem!important}
  .st-key-landing_wrap .hero-person{min-height:590px!important}
  .st-key-landing_wrap .hero-logo{height:66px!important;margin-bottom:.4rem!important}
  .st-key-landing_wrap .hero-logo img{max-height:62px!important}
  .st-key-landing_wrap .hero-title{font-size:clamp(1.38rem,5.9vw,1.62rem)!important}
  .st-key-landing_wrap .hero-description{font-size:.74rem!important}
  .st-key-landing_wrap .hero-benefits{font-size:.7rem!important;gap:.36rem!important}
  .st-key-landing_start{bottom:.55rem!important;left:.48rem!important;width:calc(55% - .8rem)!important}
  .st-key-landing_start button{min-height:43px!important;font-size:.73rem!important}
}


/* Ajuste fino tras previsualizar la portada en tres anchos */
.hero-shell{min-height:560px!important}
.hero-person{min-height:560px!important}
.hero-shell:before{top:-30%!important;height:44%!important;transform:rotate(-3deg)!important}
.st-key-landing_start{top:440px!important;bottom:auto!important}
@media(max-width:760px){
 .st-key-landing_wrap .hero-shell{grid-template-rows:minmax(510px,auto)!important;min-height:510px!important}
 .st-key-landing_wrap .hero-person{min-height:510px!important}
 .st-key-landing_wrap .hero-shell:before{top:-28%!important;height:38%!important;transform:rotate(-3deg)!important}
 .st-key-landing_start{top:390px!important;bottom:auto!important}
}
@media(max-width:390px){
 .st-key-landing_wrap .hero-shell{grid-template-rows:minmax(510px,auto)!important;min-height:510px!important}
 .st-key-landing_wrap .hero-person{min-height:510px!important}
 .st-key-landing_start{top:390px!important;bottom:auto!important}
}


/* PORTADA V3: mujer a escala natural y logo visible también en PC */
.st-key-landing_wrap .hero-shell{
  grid-template-columns:minmax(0,1.12fr) minmax(300px,.88fr)!important;
  min-height:520px!important;height:520px!important;
  max-width:1080px!important;align-items:stretch!important;
}
.st-key-landing_wrap .hero-copy{
  padding:1.05rem 1.65rem 5rem!important;
  min-width:0!important;justify-content:flex-start!important;
}
.st-key-landing_wrap .hero-logo{
  position:relative!important;z-index:5!important;
  display:flex!important;visibility:visible!important;opacity:1!important;
  width:300px!important;max-width:100%!important;height:82px!important;
  margin:0 0 .65rem!important;padding:.22rem .55rem!important;
  border-radius:12px!important;background:rgba(255,255,255,.94)!important;
  box-shadow:0 5px 18px rgba(0,25,75,.12)!important;
}
.st-key-landing_wrap .hero-logo img{
  display:block!important;visibility:visible!important;opacity:1!important;
  width:auto!important;max-width:100%!important;height:auto!important;max-height:76px!important;
  object-fit:contain!important;object-position:left center!important;
}
.st-key-landing_wrap .hero-title{font-size:clamp(2.15rem,3.2vw,2.8rem)!important;line-height:1.03!important;margin:.12rem 0 .65rem!important}
.st-key-landing_wrap .hero-description{max-width:390px!important;font-size:1rem!important;line-height:1.42!important;margin-bottom:.75rem!important}
.st-key-landing_wrap .hero-benefits{gap:.42rem!important;margin:.12rem 0 .2rem!important;font-size:.98rem!important}
.st-key-landing_wrap .hero-benefit i{width:31px!important;height:31px!important;flex-basis:31px!important}
.st-key-landing_wrap .hero-person{
  position:relative!important;display:flex!important;align-items:flex-end!important;justify-content:center!important;
  min-width:0!important;min-height:520px!important;height:520px!important;overflow:hidden!important;
  border-radius:0 0 0 82px!important;
  background:linear-gradient(90deg,rgba(5,48,112,.16),rgba(5,48,112,0) 28%),linear-gradient(180deg,#0b4b91 0%,#0b367a 100%)!important;
}
.st-key-landing_wrap .hero-person img{
  position:absolute!important;inset:0!important;width:100%!important;height:100%!important;
  object-fit:contain!important;object-position:center bottom!important;
  opacity:.96!important;transform:scale(.94)!important;transform-origin:center bottom!important;
}
.st-key-landing_wrap .hero-person:after{
  background:linear-gradient(90deg,rgba(5,48,112,.28),rgba(5,48,112,0) 36%),linear-gradient(0deg,rgba(0,49,122,.18),transparent 38%)!important;
}
.st-key-landing_start{top:auto!important;bottom:1.15rem!important;left:1.65rem!important}
@media(max-width:760px){
 .st-key-landing_wrap .hero-shell{grid-template-columns:minmax(0,1.12fr) minmax(0,.88fr)!important;grid-template-rows:minmax(510px,auto)!important;min-height:510px!important;height:510px!important}
 .st-key-landing_wrap .hero-copy{padding:.72rem .55rem 4.3rem!important}
 .st-key-landing_wrap .hero-logo{width:100%!important;height:68px!important;padding:.16rem .28rem!important;margin:0 0 .48rem!important}
 .st-key-landing_wrap .hero-logo img{max-height:62px!important}
 .st-key-landing_wrap .hero-person{min-height:510px!important;height:510px!important;max-height:none!important}
 .st-key-landing_wrap .hero-person img{object-fit:cover!important;object-position:50% 18%!important;transform:none!important;opacity:.88!important}
 .st-key-landing_start{top:auto!important;bottom:.62rem!important;left:.58rem!important;width:calc(56% - .95rem)!important}
}
@media(max-width:390px){
 .st-key-landing_wrap .hero-shell{grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr)!important;min-height:510px!important;height:510px!important;grid-template-rows:510px!important}
 .st-key-landing_wrap .hero-person{min-height:510px!important;height:510px!important}
 .st-key-landing_start{top:auto!important;bottom:.55rem!important}
}


/* Pantalla Empresa: dos búsquedas independientes y sincronizadas con Google Sheets. */
.st-key-screen_company .st-key-company_selectors {
  width:100%!important; margin:.9rem 0 .9rem!important; padding:0!important;
}
.st-key-screen_company .st-key-company_selectors .field-label {
  min-height:26px!important; margin:.15rem 0 .48rem!important;
  color:#12396e!important; font-size:.9rem!important; font-weight:850!important;
}
.st-key-screen_company .st-key-company_selectors [data-testid="stSelectbox"] [data-baseweb="select"]>div {
  min-height:48px!important; border-radius:12px!important; border:1.4px solid #b8d2ea!important;
  background:#fff!important;
}
.st-key-screen_company .st-key-company_selectors [data-testid="stSelectbox"] input {
  color:#18345b!important;
}
@media(max-width:760px){
  .st-key-screen_company .st-key-company_selectors {margin:.65rem 0 .8rem!important;}
  .st-key-screen_company .st-key-company_selectors .field-label {font-size:.84rem!important;}
}
</style>
""", unsafe_allow_html=True)



# ---------- PORTADA V5: LOGO TRANSPARENTE Y FOTO SIN RECORTE ----------
st.markdown(r"""
<style>
.st-key-landing_wrap{position:relative!important;width:100%!important;max-width:1080px!important;margin:.25rem auto 1rem!important}
.st-key-landing_wrap .hero-shell{
 display:grid!important;grid-template-columns:minmax(0,1.08fr) minmax(270px,.92fr)!important;
 position:relative!important;isolation:isolate!important;overflow:hidden!important;
 width:100%!important;max-width:1080px!important;height:540px!important;min-height:540px!important;
 margin:0 auto!important;border:1px solid #159ce6!important;border-radius:25px!important;
 background:linear-gradient(135deg,#062b6c 0%,#073e8a 66%,#0877bd 100%)!important;
 box-shadow:0 20px 55px rgba(0,18,58,.28)!important;
}
.st-key-landing_wrap .hero-shell:before{
 content:""!important;display:block!important;position:absolute!important;z-index:0!important;
 left:-7%!important;top:-24%!important;width:70%!important;height:44%!important;
 border-radius:0 0 72% 12%!important;transform:rotate(-4deg)!important;
 background:linear-gradient(135deg,#fff 0%,#f4fbff 72%,#c9ecff 100%)!important;
}
.st-key-landing_wrap .hero-shell:after{
 content:""!important;display:block!important;position:absolute!important;z-index:4!important;
 right:-4%!important;bottom:-45px!important;width:64%!important;height:88px!important;
 transform:rotate(-8deg)!important;border-radius:80% 0 0 0!important;
 border-top:15px solid #08c6ee!important;pointer-events:none!important;
}
.st-key-landing_wrap .hero-copy{
 position:relative!important;z-index:3!important;display:flex!important;flex-direction:column!important;
 align-items:flex-start!important;justify-content:flex-start!important;min-width:0!important;
 padding:1.05rem 1.6rem 5.2rem!important;
}
/* El logo no tiene panel propio: el fondo blanco es solo la curva superior de la tarjeta. */
.st-key-landing_wrap .hero-logo{
 position:relative!important;z-index:5!important;display:flex!important;align-items:center!important;
 justify-content:flex-start!important;width:min(100%,340px)!important;height:106px!important;
 max-width:100%!important;margin:0 0 .78rem!important;padding:0!important;
 border:0!important;border-radius:0!important;background:transparent!important;
 box-shadow:none!important;overflow:visible!important;
}
.st-key-landing_wrap .hero-logo img{
 display:block!important;visibility:visible!important;opacity:1!important;
 width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important;
 object-fit:contain!important;object-position:left center!important;border:0!important;
 border-radius:0!important;background:transparent!important;box-shadow:none!important;
}
.st-key-landing_wrap .hero-title{
 position:relative!important;z-index:2!important;margin:.28rem 0 .65rem!important;
 color:#fff!important;font-size:clamp(2.12rem,3.7vw,3.02rem)!important;
 font-weight:950!important;line-height:1.02!important;letter-spacing:-.048em!important;
}
.st-key-landing_wrap .hero-title span{display:block!important;color:#12d2f4!important}
.st-key-landing_wrap .hero-description{
 position:relative!important;z-index:2!important;max-width:440px!important;
 margin:0 0 .82rem!important;color:#f4f9ff!important;
 font-size:clamp(.98rem,1.45vw,1.12rem)!important;line-height:1.42!important;font-weight:500!important;
}
.st-key-landing_wrap .hero-benefits{
 position:relative!important;z-index:2!important;display:grid!important;grid-template-columns:1fr!important;
 gap:.48rem!important;margin:.1rem 0 .15rem!important;color:#fff!important;
 font-size:1rem!important;line-height:1.15!important;font-weight:850!important;
}
.st-key-landing_wrap .hero-benefit{display:flex!important;align-items:center!important;gap:.62rem!important;white-space:nowrap!important}
.st-key-landing_wrap .hero-benefit i{
 display:flex!important;align-items:center!important;justify-content:center!important;flex:0 0 32px!important;
 width:32px!important;height:32px!important;border-radius:50%!important;
 background:#12c7e8!important;color:#063675!important;font-style:normal!important;font-weight:950!important;
}
/* Sin placa, borde ni velo de color: se usa la fotografía completa y se conserva el dedo. */
.st-key-landing_wrap .hero-person{
 position:relative!important;z-index:1!important;display:block!important;min-width:0!important;
 width:100%!important;height:540px!important;min-height:540px!important;overflow:hidden!important;
 border-radius:0 0 0 88px!important;background:transparent!important;
}
.st-key-landing_wrap .hero-person img{
 position:absolute!important;inset:0!important;display:block!important;
 width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important;
 object-fit:contain!important;object-position:65% center!important;
 opacity:1!important;transform:none!important;border:0!important;border-radius:0!important;
}
.st-key-landing_wrap .hero-person:after,.st-key-landing_wrap .hero-person:before{content:none!important;display:none!important;background:none!important}
.st-key-landing_start{
 position:absolute!important;z-index:12!important;left:1.6rem!important;bottom:1.05rem!important;
 top:auto!important;width:auto!important;max-width:235px!important;margin:0!important;
}
.st-key-landing_start button{
 display:inline-flex!important;align-items:center!important;justify-content:center!important;
 width:auto!important;min-width:205px!important;min-height:51px!important;
 padding:.75rem 1.65rem!important;border:0!important;border-radius:999px!important;
 color:#082c68!important;background:linear-gradient(110deg,#ffda55,#ffad00)!important;
 font-size:1rem!important;font-weight:900!important;white-space:nowrap!important;
 box-shadow:0 9px 24px rgba(255,181,27,.35)!important;
}
@media(max-width:760px){
 .st-key-landing_wrap{width:100%!important;max-width:100%!important;margin:.15rem auto .7rem!important}
 .st-key-landing_wrap .hero-shell{
  grid-template-columns:minmax(0,1.08fr) minmax(0,.92fr)!important;
  height:520px!important;min-height:520px!important;grid-template-rows:520px!important;
  border-radius:19px!important;
 }
 .st-key-landing_wrap .hero-shell:before{left:-13%!important;top:-18%!important;width:83%!important;height:30%!important}
 .st-key-landing_wrap .hero-shell:after{right:-12%!important;bottom:-35px!important;width:90%!important;height:65px!important;border-top-width:11px!important}
 .st-key-landing_wrap .hero-copy{grid-column:1!important;grid-row:1!important;padding:.72rem .55rem 4.25rem!important}
 .st-key-landing_wrap .hero-logo{width:100%!important;height:62px!important;margin:0 0 .62rem!important}
 .st-key-landing_wrap .hero-logo img{width:100%!important;height:100%!important;max-height:62px!important}
 .st-key-landing_wrap .hero-title{font-size:clamp(1.42rem,5.7vw,1.82rem)!important;line-height:1.03!important;margin:.24rem 0 .45rem!important;letter-spacing:-.045em!important}
 .st-key-landing_wrap .hero-description{font-size:clamp(.72rem,2.95vw,.84rem)!important;line-height:1.32!important;margin:0 0 .55rem!important}
 .st-key-landing_wrap .hero-benefits{gap:.38rem!important;font-size:clamp(.70rem,2.8vw,.79rem)!important;margin:.08rem 0 .1rem!important}
 .st-key-landing_wrap .hero-benefit{gap:.35rem!important}
 .st-key-landing_wrap .hero-benefit i{width:24px!important;height:24px!important;flex-basis:24px!important;font-size:.75rem!important}
 .st-key-landing_wrap .hero-person{grid-column:2!important;grid-row:1!important;height:520px!important;min-height:520px!important;border-radius:0 0 0 44px!important;background:transparent!important}
 .st-key-landing_wrap .hero-person img{object-fit:contain!important;object-position:right center!important;width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important}
 .st-key-landing_start{left:.52rem!important;bottom:.55rem!important;top:auto!important;width:calc(56% - .65rem)!important;max-width:190px!important}
 .st-key-landing_start button{width:100%!important;min-width:0!important;min-height:44px!important;padding:.5rem .35rem!important;font-size:clamp(.72rem,2.8vw,.84rem)!important}
}
@media(max-width:390px){
 .st-key-landing_wrap .hero-shell{grid-template-columns:minmax(0,1.07fr) minmax(0,.93fr)!important;height:510px!important;min-height:510px!important;grid-template-rows:510px!important}
 .st-key-landing_wrap .hero-copy{padding:.62rem .46rem 4.05rem!important}
 .st-key-landing_wrap .hero-logo{height:58px!important;margin-bottom:.56rem!important}
 .st-key-landing_wrap .hero-logo img{max-height:58px!important}
 .st-key-landing_wrap .hero-title{font-size:clamp(1.32rem,5.5vw,1.58rem)!important;margin-top:.2rem!important}
 .st-key-landing_wrap .hero-description{font-size:.70rem!important;line-height:1.28!important}
 .st-key-landing_wrap .hero-benefits{font-size:.68rem!important;gap:.34rem!important}
 .st-key-landing_wrap .hero-person{height:510px!important;min-height:510px!important}
 .st-key-landing_start{left:.45rem!important;bottom:.48rem!important;width:calc(55% - .6rem)!important}
 .st-key-landing_start button{min-height:42px!important;font-size:.70rem!important}
}
</style>
""", unsafe_allow_html=True)

# ---------- AJUSTE FINAL: CTA DE PORTADA EN PC SIN SOLAPAR BENEFICIOS ----------
st.markdown(r"""
<style>
@media (min-width:761px) {
  /* Compacta un poco el contenido para reservar una franja independiente al CTA. */
  .st-key-landing_wrap .hero-shell {
    height:540px!important;
    min-height:540px!important;
  }
  .st-key-landing_wrap .hero-copy {
    padding:.82rem 1.55rem 4.65rem!important;
  }
  .st-key-landing_wrap .hero-logo {
    height:84px!important;
    width:min(100%,310px)!important;
    margin:0 0 .42rem!important;
  }
  .st-key-landing_wrap .hero-logo img {
    max-height:84px!important;
  }
  .st-key-landing_wrap .hero-title {
    font-size:clamp(2.05rem,3.05vw,2.62rem)!important;
    line-height:1.01!important;
    margin:.08rem 0 .48rem!important;
  }
  .st-key-landing_wrap .hero-description {
    max-width:405px!important;
    font-size:.97rem!important;
    line-height:1.34!important;
    margin:0 0 .58rem!important;
  }
  .st-key-landing_wrap .hero-benefits {
    gap:.34rem!important;
    margin:.04rem 0 0!important;
    font-size:.94rem!important;
    line-height:1.12!important;
  }
  .st-key-landing_wrap .hero-benefit i {
    width:29px!important;
    height:29px!important;
    flex-basis:29px!important;
  }
  /* El botón queda en el flujo de la página y sube al espacio reservado inferior.
     Así su posición no depende de la altura accidental del contenedor de Streamlit. */
  .st-key-landing_start {
    position:relative!important;
    left:1.6rem!important;
    top:auto!important;
    bottom:auto!important;
    width:max-content!important;
    max-width:235px!important;
    margin-top:-72px!important;
    margin-bottom:19px!important;
    z-index:20!important;
  }
  .st-key-landing_start button {
    min-width:205px!important;
    min-height:49px!important;
  }
}
</style>
""", unsafe_allow_html=True)

# ---------- PANTALLA 2: TARJETAS DE FONDOS CLICABLES ----------
st.markdown(r"""
<style>
/* Dos tarjetas equilibradas por fila; la quinta opción queda centrada. */
.st-key-screen_fund [class*="st-key-fund_card_"] {
  position:relative!important;
  min-height:218px!important;
  height:100%!important;
  box-sizing:border-box!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:flex-start!important;
  align-items:stretch!important;
  gap:.3rem!important;
  padding:1.05rem .9rem .8rem!important;
  border:1.5px solid #d5e6f6!important;
  border-radius:20px!important;
  background:linear-gradient(180deg,#ffffff 0%,#f5faff 100%)!important;
  box-shadow:0 7px 20px rgba(6,43,104,.08)!important;
  overflow:hidden!important;
  transition:border-color .18s ease,box-shadow .18s ease,transform .18s ease!important;
}
.st-key-screen_fund [class*="st-key-fund_card_"]:hover {
  border-color:#36a8ed!important;
  box-shadow:0 12px 26px rgba(8,111,208,.15)!important;
  transform:translateY(-2px)!important;
}
.st-key-screen_fund .fund-card-title {
  width:100%;
  min-height:1.8rem;
  margin:0 0 .2rem;
  color:#082e6b!important;
  text-align:center;
  font-size:clamp(1.18rem,2vw,1.42rem);
  line-height:1.2;
  font-weight:900;
  letter-spacing:-.025em;
}
.st-key-screen_fund .fund-card-logo {
  width:100%;
  height:96px;
  min-width:0;
  flex:1 1 auto;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:.12rem .25rem;
  margin:0;
  overflow:hidden;
  box-sizing:border-box;
  background:transparent!important;
  border:0!important;
  border-radius:0!important;
}
.st-key-screen_fund .fund-card-logo img {
  display:block;
  width:auto;
  max-width:86%;
  height:auto;
  max-height:82px;
  object-fit:contain;
}
.st-key-screen_fund .fund-card-logo svg {
  display:block;
  width:46px;
  height:46px;
  max-width:100%;
  max-height:100%;
  flex:0 1 auto;
  color:#0878d8;
  stroke:currentColor;
  fill:none;
  stroke-width:1.8;
  stroke-linecap:round;
  stroke-linejoin:round;
}
/* El botón real cubre todo el contenedor: tanto nombre como logo responden al clic.
   Su etiqueta sigue disponible para lectores de pantalla, pero no aparece visualmente. */
.st-key-screen_fund [class*="st-key-fund_card_"] [class*="st-key-fund_pick_"] {
  position:absolute!important;
  inset:0!important;
  z-index:20!important;
  width:100%!important;
  height:100%!important;
  margin:0!important;
  padding:0!important;
}
.st-key-screen_fund [class*="st-key-fund_card_"] [class*="st-key-fund_pick_"] button {
  position:absolute!important;
  inset:0!important;
  display:block!important;
  width:100%!important;
  height:100%!important;
  min-height:100%!important;
  margin:0!important;
  padding:0!important;
  opacity:0!important;
  color:transparent!important;
  background:transparent!important;
  border:0!important;
  border-radius:20px!important;
  box-shadow:none!important;
  cursor:pointer!important;
}
.st-key-screen_fund [class*="st-key-fund_card_"] [class*="st-key-fund_pick_"] button:hover {
  transform:none!important;
  box-shadow:none!important;
}
.st-key-screen_fund [class*="st-key-fund_card_"]:focus-within {
  outline:3px solid rgba(16,188,232,.55)!important;
  outline-offset:3px!important;
}

</style>
""", unsafe_allow_html=True)


# ---------- PANTALLA 2: CSS MÓVIL CONSOLIDADO ----------
st.markdown(r"""
<style>
@media (max-width: 600px) {
  /* Mantener el panel y sus columnas dentro del ancho real del teléfono. */
  .st-key-screen_fund {
    width:100% !important;
    max-width:100% !important;
    min-width:0 !important;
    box-sizing:border-box !important;
    padding:.82rem .58rem 1rem !important;
    overflow:hidden !important;
  }
  .st-key-screen_fund [data-testid="stHorizontalBlock"]:not(:has(.st-key-fund_card_otro_fondo)) {
    display:grid !important;
    grid-template-columns:repeat(2,minmax(0,1fr)) !important;
    align-items:stretch !important;
    gap:.58rem !important;
    width:100% !important;
    max-width:100% !important;
    min-width:0 !important;
    box-sizing:border-box !important;
  }
  .st-key-screen_fund [data-testid="stHorizontalBlock"]:not(:has(.st-key-fund_card_otro_fondo)) > [data-testid="column"] {
    display:block !important;
    width:100% !important;
    max-width:100% !important;
    min-width:0 !important;
    flex:initial !important;
    padding:0 !important;
    box-sizing:border-box !important;
  }

  /* Cada tarjeta es un cuadrado real. La primera pieza (HTML de nombre+logo)
     ocupa todo el cuadrado; el botón transparente cubre la superficie aparte. */
  .st-key-screen_fund [class*="st-key-fund_card_"] {
    position:relative !important;
    display:grid !important;
    grid-template-columns:minmax(0,1fr) !important;
    grid-template-rows:minmax(0,1fr) !important;
    align-items:stretch !important;
    justify-items:stretch !important;
    width:100% !important;
    min-width:0 !important;
    min-height:0 !important;
    height:auto !important;
    max-height:none !important;
    aspect-ratio:1 / 1 !important;
    padding:.52rem .34rem .38rem !important;
    margin:0 !important;
    gap:0 !important;
    box-sizing:border-box !important;
    border-radius:15px !important;
    overflow:hidden !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_"] > [data-testid="stElementContainer"]:first-child {
    grid-column:1 !important;
    grid-row:1 !important;
    display:flex !important;
    align-self:stretch !important;
    width:100% !important;
    height:100% !important;
    min-width:0 !important;
    min-height:0 !important;
    margin:0 !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_"] > [data-testid="stElementContainer"]:first-child [data-testid="stMarkdown"],
  .st-key-screen_fund [class*="st-key-fund_card_"] > [data-testid="stElementContainer"]:first-child [data-testid="stMarkdownContainer"] {
    display:flex !important;
    flex:1 1 auto !important;
    align-items:stretch !important;
    width:100% !important;
    height:100% !important;
    min-width:0 !important;
    min-height:0 !important;
    margin:0 !important;
  }
  .st-key-screen_fund .fund-card-content {
    display:grid !important;
    grid-template-rows: minmax(1.7rem,auto) minmax(0,1fr) !important;
    align-items:stretch !important;
    justify-items:stretch !important;
    gap:.42rem !important;
    width:100% !important;
    height:100% !important;
    min-width:0 !important;
    min-height:0 !important;
    margin:0 !important;
    box-sizing:border-box !important;
    overflow:hidden !important;
  }
  .st-key-screen_fund .fund-card-title {
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    width:100% !important;
    min-width:0 !important;
    min-height:1.7rem !important;
    height:auto !important;
    margin:0 !important;
    padding:0 .08rem !important;
    color:#082e6b !important;
    font-size:clamp(1rem,4.3vw,1.08rem) !important;
    font-weight:900 !important;
    line-height:1.12 !important;
    text-align:center !important;
    white-space:nowrap !important;
    overflow:hidden !important;
    text-overflow:ellipsis !important;
    box-sizing:border-box !important;
  }
  .st-key-screen_fund .fund-card-logo {
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    width:100% !important;
    height:100% !important;
    min-width:0 !important;
    min-height:0 !important;
    margin:0 !important;
    padding:.18rem .12rem .06rem !important;
    overflow:hidden !important;
    box-sizing:border-box !important;
  }
  .st-key-screen_fund .fund-card-logo img {
    display:block !important;
    width:auto !important;
    height:auto !important;
    max-width:78% !important;
    max-height:clamp(42px,15vw,64px) !important;
    object-fit:contain !important;
    object-position:center center !important;
    margin:0 auto !important;
  }
  .st-key-screen_fund .fund-card-logo svg {
    display:block !important;
    width:clamp(25px,8vw,32px) !important;
    height:clamp(25px,8vw,32px) !important;
    min-width:0 !important;
    max-width:32px !important;
    max-height:32px !important;
    margin:0 auto !important;
  }

  /* El botón invisible sigue haciendo clicable toda la tarjeta. */
  .st-key-screen_fund [class*="st-key-fund_card_"] [class*="st-key-fund_pick_"] {
    position:absolute !important;
    inset:0 !important;
    z-index:20 !important;
    width:100% !important;
    height:100% !important;
    min-height:0 !important;
    margin:0 !important;
    padding:0 !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_"] [class*="st-key-fund_pick_"] button {
    position:absolute !important;
    inset:0 !important;
    display:block !important;
    width:100% !important;
    height:100% !important;
    min-height:100% !important;
    max-height:100% !important;
    margin:0 !important;
    padding:0 !important;
    opacity:0 !important;
    color:transparent !important;
    background:transparent !important;
    border:0 !important;
    box-shadow:none !important;
    border-radius:15px !important;
    cursor:pointer !important;
    touch-action:manipulation !important;
  }

  /* "Otro Fondo": fila flex centrada y tamaño fijo compacto.
     No depende de los anchos responsivos que Streamlit asigna a st.columns. */
  .st-key-screen_fund [data-testid="stHorizontalBlock"]:has(.st-key-fund_card_otro_fondo) {
    display:flex !important;
    flex-direction:row !important;
    flex-wrap:nowrap !important;
    align-items:flex-start !important;
    justify-content:center !important;
    width:100% !important;
    max-width:100% !important;
    min-width:0 !important;
    gap:0 !important;
    box-sizing:border-box !important;
  }
  .st-key-screen_fund [data-testid="stHorizontalBlock"]:has(.st-key-fund_card_otro_fondo) > [data-testid="column"]:not(:has(.st-key-fund_card_otro_fondo)) {
    display:none !important;
    width:0 !important;
    max-width:0 !important;
    min-width:0 !important;
    flex:0 0 0 !important;
    padding:0 !important;
    margin:0 !important;
  }
  .st-key-screen_fund [data-testid="stHorizontalBlock"]:has(.st-key-fund_card_otro_fondo) > [data-testid="column"]:has(.st-key-fund_card_otro_fondo) {
    display:block !important;
    flex:0 0 120px !important;
    width:120px !important;
    min-width:120px !important;
    max-width:120px !important;
    margin:0 auto !important;
    padding:0 !important;
    box-sizing:border-box !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_otro_fondo"] {
    display:flex !important;
    width:120px !important;
    min-width:120px !important;
    max-width:120px !important;
    aspect-ratio:1 / 1 !important;
    height:120px !important;
    min-height:120px !important;
    max-height:120px !important;
    margin:0 auto !important;
    padding:.42rem .22rem !important;
    box-sizing:border-box !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_otro_fondo"] .fund-card-content {
    grid-template-rows:minmax(1.3rem,auto) minmax(0,1fr) !important;
    gap:.3rem !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_otro_fondo"] .fund-card-title {
    font-size:.86rem !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_otro_fondo"] .fund-card-logo svg {
    width:26px !important;
    height:26px !important;
  }
}

@media (max-width:380px) {
  .st-key-screen_fund {
    padding:.72rem .42rem .9rem !important;
  }
  .st-key-screen_fund [data-testid="stHorizontalBlock"]:not(:has(.st-key-fund_card_otro_fondo)) {
    gap:.42rem !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_"] {
    padding:.42rem .22rem .32rem !important;
    border-radius:13px !important;
  }
  .st-key-screen_fund .fund-card-content {
    grid-template-rows:minmax(1.65rem,auto) minmax(0,1fr) !important;
    gap:.32rem !important;
  }
  .st-key-screen_fund .fund-card-title {
    font-size:.9rem !important;
  }
  .st-key-screen_fund .fund-card-logo img {
    max-width:74% !important;
    max-height:48px !important;
  }
  .st-key-screen_fund .fund-card-logo svg {
    width:27px !important;
    height:27px !important;
  }
  .st-key-screen_fund [data-testid="stHorizontalBlock"]:has(.st-key-fund_card_otro_fondo) > [data-testid="column"]:has(.st-key-fund_card_otro_fondo) {
    flex:0 0 110px !important;
    width:110px !important;
    min-width:110px !important;
    max-width:110px !important;
  }
  .st-key-screen_fund [class*="st-key-fund_card_otro_fondo"] {
    width:110px !important;
    min-width:110px !important;
    max-width:110px !important;
    height:110px !important;
    min-height:110px !important;
    max-height:110px !important;
  }
}
</style>
""", unsafe_allow_html=True)



# ---------- DISEÑO DE MAQUETA PARA DATOS, EMPRESA, RESUMEN Y FINAL ----------
st.markdown(r"""
<style>
:root{--mock-navy:#062b68;--mock-blue:#086fd0;--mock-cyan:#10bce8;--mock-line:#c9dced;--mock-ink:#18345b;--mock-muted:#526984}
.st-key-screen_data,.st-key-screen_company,.st-key-screen_summary,.st-key-screen_mission,.st-key-screen_processing,.st-key-screen_success{
 width:100%!important;max-width:1080px!important;margin:.6rem auto 1rem!important;padding:clamp(1rem,2.5vw,1.85rem)!important;
 box-sizing:border-box!important;border:1px solid #c9dff2!important;border-radius:24px!important;
 background:linear-gradient(180deg,#fff 0%,#fbfdff 72%,#eff7ff 100%)!important;
 box-shadow:0 16px 44px rgba(0,25,70,.22)!important;color:var(--mock-ink)!important
}
.st-key-screen_data [data-testid="stVerticalBlock"],.st-key-screen_company [data-testid="stVerticalBlock"],.st-key-screen_summary [data-testid="stVerticalBlock"],.st-key-screen_mission [data-testid="stVerticalBlock"]{gap:.66rem!important}
.st-key-screen_data .screen-heading,.st-key-screen_company .screen-heading,.st-key-screen_summary .screen-heading,.st-key-screen_mission .screen-heading{margin:.05rem 0 1rem!important;gap:.8rem!important}
.st-key-screen_data .screen-heading h2,.st-key-screen_company .screen-heading h2,.st-key-screen_summary .screen-heading h2,.st-key-screen_mission .screen-heading h2{color:#082e6b!important;font-weight:900!important;letter-spacing:-.035em!important}
.st-key-screen_data .screen-heading p,.st-key-screen_company .screen-heading p,.st-key-screen_summary .screen-heading p,.st-key-screen_mission .screen-heading p{color:#405873!important;opacity:1!important}
.st-key-screen_data .section-label,.st-key-screen_data .field-label,.st-key-screen_company .field-label{color:#12396e!important;font-weight:850!important}
.st-key-screen_data .field-label,.st-key-screen_company .field-label{margin:.35rem 0 .24rem!important;font-size:.88rem!important}
.st-key-screen_data [data-testid="stTextInput"] input,.st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"]>div,.st-key-screen_company [data-testid="stTextInput"] input,.st-key-screen_company [data-testid="stSelectbox"] [data-baseweb="select"]>div{
 min-height:47px!important;border:1.5px solid #c3d8eb!important;border-radius:12px!important;background:#fff!important;color:#18345b!important;opacity:1!important
}
.st-key-screen_data input::placeholder,.st-key-screen_company input::placeholder{color:#758aa2!important;opacity:1!important}
.st-key-screen_data [data-testid="stWidgetLabel"],.st-key-screen_company [data-testid="stWidgetLabel"]{color:#16375f!important;opacity:1!important}
.st-key-screen_data [data-testid="stCaptionContainer"] p{color:#58708b!important}
.st-key-screen_data .personal-tip{padding:.82rem 1rem!important;margin:.15rem 0 .8rem!important;border-radius:15px!important;background:linear-gradient(110deg,#e9f6ff,#d8f1ff)!important;border:1px solid #b9e3f7!important}
.st-key-screen_data .personal-tip strong{color:#073575!important;font-size:1.08rem!important}
.st-key-screen_data .personal-tip p{color:#405d7c!important;font-size:.87rem!important}
.st-key-screen_data .section-label{margin:.65rem 0 .28rem!important;font-size:1rem!important}
.st-key-screen_company .company-intro{display:flex;align-items:center;gap:.8rem;padding:.85rem 1rem;margin:.1rem 0 .8rem;border-radius:15px;border:1px solid #c5e5f7;background:linear-gradient(110deg,#eef8ff,#e1f4ff)}
.st-key-screen_company .company-intro-icon{width:48px;height:48px;flex:0 0 48px;display:flex;align-items:center;justify-content:center;border-radius:14px;background:linear-gradient(145deg,#0874d8,#10bce8);color:#fff}
.st-key-screen_company .company-intro-icon svg{width:26px;height:26px;stroke:#fff;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.st-key-screen_company .company-intro strong{display:block;color:#073575;font-size:1rem;font-weight:900}
.st-key-screen_company .company-intro p{margin:.16rem 0 0;color:#48627e;font-size:.85rem;line-height:1.45}
.st-key-screen_company .company-selected-card{display:flex;align-items:center;gap:.8rem;margin:.55rem 0 .85rem;padding:.72rem .9rem;border:1.5px solid #bcd9f2;border-radius:15px;background:linear-gradient(110deg,#fff,#f2f8ff);box-shadow:0 4px 13px rgba(8,65,135,.06)}
.st-key-screen_company .company-selected-icon{width:44px;height:44px;flex:0 0 44px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:#e8f4ff;color:#0874d8}
.st-key-screen_company .company-selected-icon svg{width:27px;height:27px;stroke:currentColor;fill:none;stroke-width:2}
.st-key-screen_company .company-selected-text{display:flex;flex-direction:column;gap:.12rem;min-width:0;flex:1}
.st-key-screen_company .company-selected-text strong{color:#082e6b;font-size:1.02rem;font-weight:900;overflow-wrap:anywhere}
.st-key-screen_company .company-selected-text span{color:#49637e;font-size:.84rem;font-weight:650}
.st-key-screen_company .company-selected-check{width:28px;height:28px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#dff7e7;color:#128a3c;font-weight:950}
.st-key-screen_company .company-other-heading{display:flex;align-items:center;justify-content:center;gap:.7rem;margin:1rem 0 .25rem;padding:.72rem .9rem;border-radius:14px;background:#eaf5ff;border:1px solid #c1def5;text-align:left}
.st-key-screen_company .company-plus{width:34px;height:34px;flex:0 0 34px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:linear-gradient(135deg,#0874d8,#10bce8);color:#fff;font-size:1.45rem;font-weight:800}
.st-key-screen_company .company-other-heading strong{color:#082e6b;font-weight:900}
.st-key-screen_company .company-other-heading p{margin:.08rem 0 0;color:#405873;font-size:.84rem}
.st-key-screen_company .summary-item{margin:.2rem 0!important}
.st-key-summary_panel{width:100%!important;box-sizing:border-box!important;padding:1rem!important;border:1px solid #c6dcef!important;border-radius:18px!important;background:linear-gradient(135deg,#fff,#f2f8ff)!important;box-shadow:0 7px 20px rgba(7,48,103,.08)!important}
.st-key-screen_summary .summary-layout{display:grid;grid-template-columns:minmax(130px,.27fr) minmax(0,.73fr);gap:1.15rem;align-items:center;width:100%}
.st-key-screen_summary .summary-check-column{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:.35rem;padding:.55rem}
.st-key-screen_summary .summary-check{width:96px;height:96px;margin:0;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#22ce44,#0da52d);color:#fff;font-size:3.6rem;font-weight:950;box-shadow:0 10px 25px rgba(24,184,55,.27)}
.st-key-screen_summary .summary-check-column strong{color:#0a7430;font-size:.9rem;font-weight:900}
.st-key-screen_summary .summary-check-column span{color:#5d7187;font-size:.76rem;line-height:1.35}
.st-key-screen_summary .summary-details{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.42rem .55rem;min-width:0}
.st-key-screen_summary .summary-item{min-width:0;padding:.48rem .62rem;margin:0;border:1px solid #e0ebf5;border-radius:10px;background:#fff;overflow:hidden}
.st-key-screen_summary .summary-item small{display:block;color:#58708b;font-size:.66rem;font-weight:850;text-transform:uppercase;letter-spacing:.035em}
.st-key-screen_summary .summary-item strong{display:block;color:#0d2e5b;font-size:.88rem;font-weight:850;overflow-wrap:anywhere;line-height:1.3}
.st-key-screen_summary .summary-note{display:flex;align-items:center;gap:.7rem;margin:.8rem 0 .45rem;padding:.75rem .9rem;border-radius:14px;background:#e3f1ff;border:1px solid #c8e0f6;color:#194a7d;font-size:.87rem;line-height:1.45}
.st-key-screen_summary .summary-note-icon{width:28px;height:28px;flex:0 0 28px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#0b82dc;color:white;font-weight:950;font-size:1.05rem}
.st-key-screen_mission .mission-hero{margin:.1rem 0 .8rem!important;padding:1.15rem 1.25rem!important;border-radius:17px!important}
.st-key-screen_mission .mission-card{min-height:150px!important}
.st-key-screen_mission .mission-footnote{margin:.8rem 0 .35rem;color:#526b85;font-size:.82rem;line-height:1.5}
.st-key-screen_success .success-shell{max-width:850px;margin:.2rem auto 1rem;padding:clamp(1.3rem,3.5vw,2.5rem);border-radius:23px;background:radial-gradient(circle at 50% 12%,#e2f4ff,#fff 58%,#eef8ff);border:1px solid #d3e5f4;box-shadow:0 12px 34px rgba(0,25,65,.10);text-align:center;position:relative;overflow:hidden}
.st-key-screen_success .success-check{width:104px;height:104px;margin:.2rem auto .8rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#0ebcf0,#0756c4);color:#fff;font-size:4rem;font-weight:950;box-shadow:0 10px 25px #0874d833}
.st-key-screen_success .success-shell h1{color:#082e6b;font-size:clamp(2rem,4vw,2.8rem);font-weight:950;letter-spacing:-.04em;margin:.2rem 0 .45rem}
.st-key-screen_success .success-shell p{color:#173d76;font-size:1rem;line-height:1.5}
.st-key-screen_success .success-delivery{max-width:700px;margin:1rem auto;padding:.85rem 1rem;border-radius:15px;background:#dceeff;color:#083a7b;font-weight:750;text-align:left;line-height:1.5;display:flex;align-items:center;gap:.7rem}
.st-key-screen_success .success-mail-icon{width:42px;height:42px;flex:0 0 42px;border-radius:11px;background:linear-gradient(135deg,#0754a6,#0a94dc);color:#fff;display:flex;align-items:center;justify-content:center;font-size:1.35rem}
.st-key-screen_success .success-number{display:inline-flex;flex-direction:column;gap:.22rem;margin:.35rem auto .4rem;padding:.65rem 1.2rem;border:1px solid #d5e6f4;border-radius:13px;background:#fff}
.st-key-screen_success .success-number small{color:#62778f;font-size:.68rem;font-weight:850;letter-spacing:.06em}
.st-key-screen_success .success-number strong{color:#0b3471;font-size:1.05rem;font-weight:950;letter-spacing:.04em}
.st-key-screen_success .footer-brand{color:#063574;font-weight:850;font-style:italic;margin-top:1.05rem}
.st-key-screen_data [data-testid="stButton"] button,.st-key-screen_company [data-testid="stButton"] button,.st-key-screen_summary [data-testid="stButton"] button,.st-key-screen_mission [data-testid="stButton"] button,.st-key-screen_success [data-testid="stButton"] button{min-height:48px;border-radius:13px!important}
.st-key-screen_data .st-key-data_back button,.st-key-screen_company .st-key-company_back button,.st-key-screen_summary .st-key-summary_back button,.st-key-screen_mission .st-key-mission_back button{background:#fff!important;color:#0752a0!important;border:1.5px solid #8fc6f0!important;box-shadow:none!important}
.st-key-screen_data .st-key-data_continue button,.st-key-screen_company .st-key-company_submit button,.st-key-screen_summary .st-key-summary_continue button,.st-key-screen_mission .st-key-mission_continue button{background:linear-gradient(110deg,#073b8a,#0874d4 70%,#0aa6dc)!important;color:#fff!important}
@media(max-width:760px){
 .st-key-screen_data,.st-key-screen_company,.st-key-screen_summary,.st-key-screen_mission,.st-key-screen_processing,.st-key-screen_success{width:100%!important;max-width:100%!important;margin:.4rem auto!important;padding:1rem .78rem!important;border-radius:18px!important}
 .st-key-screen_data [data-testid="stHorizontalBlock"],.st-key-screen_company [data-testid="stHorizontalBlock"],.st-key-screen_summary [data-testid="stHorizontalBlock"],.st-key-screen_mission [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.42rem!important}
 .st-key-screen_data [data-testid="stHorizontalBlock"]>[data-testid="column"],.st-key-screen_company [data-testid="stHorizontalBlock"]>[data-testid="column"],.st-key-screen_mission [data-testid="stHorizontalBlock"]>[data-testid="column"]{flex:1 1 100%!important;min-width:100%!important;width:100%!important}
 .st-key-screen_data .screen-heading,.st-key-screen_company .screen-heading,.st-key-screen_summary .screen-heading,.st-key-screen_mission .screen-heading{gap:.58rem!important;margin-bottom:.8rem!important}
 .st-key-screen_data .screen-heading h2,.st-key-screen_company .screen-heading h2,.st-key-screen_summary .screen-heading h2,.st-key-screen_mission .screen-heading h2{font-size:1.25rem!important}
 .st-key-screen_data .screen-heading p,.st-key-screen_company .screen-heading p,.st-key-screen_summary .screen-heading p,.st-key-screen_mission .screen-heading p{font-size:.83rem!important}
 .st-key-screen_data .personal-tip{align-items:flex-start!important;padding:.7rem!important;gap:.62rem!important}
 .st-key-screen_data .personal-tip-icon{width:39px!important;height:39px!important;flex-basis:39px!important}
 .st-key-screen_company .company-selected-card{padding:.65rem!important;gap:.55rem!important}
 .st-key-screen_summary .summary-layout{grid-template-columns:1fr!important;gap:.7rem!important}
 .st-key-screen_summary .summary-check{width:76px!important;height:76px!important;font-size:2.8rem!important}
 .st-key-screen_summary .summary-details{grid-template-columns:1fr!important;gap:.35rem!important}
 .st-key-screen_summary .summary-item{padding:.52rem .62rem!important}
 .st-key-screen_summary .summary-note{align-items:flex-start!important;font-size:.82rem!important}
 .st-key-screen_mission .mission-card{min-height:0!important;margin-bottom:.45rem!important}
 .st-key-screen_success .success-shell{padding:1.25rem .78rem!important;border-radius:18px!important}
 .st-key-screen_success .success-check{width:82px!important;height:82px!important;font-size:3rem!important}
 .st-key-screen_success .success-delivery{align-items:flex-start!important;padding:.7rem!important;font-size:.82rem!important}
}
</style>
""", unsafe_allow_html=True)



# ---------- AJUSTES RESPONSIVOS FINALES: PANTALLAS 3 A 6 ----------
st.markdown(r"""
<style>
/* Estructura de encabezados: evita que títulos y subtítulos se monten. */
.st-key-screen_data .screen-heading > div:last-child,
.st-key-screen_company .screen-heading > div:last-child,
.st-key-screen_summary .screen-heading > div:last-child,
.st-key-screen_mission .screen-heading > div:last-child {
  flex:1 1 0!important;
  min-width:0!important;
}
.st-key-screen_company .screen-heading h2,
.st-key-screen_company .screen-heading p {
  max-width:100%!important;
  overflow-wrap:anywhere!important;
  word-break:normal!important;
}

/* Pantalla 3: el recuadro de saldo/monto y los seis campos usan una caja azul
   de alto contraste. PC conserva su estilo de dos columnas ya aprobado. */
.st-key-screen_data .personal-tip {
  background:linear-gradient(112deg,#0750a0 0%,#087fca 100%)!important;
  border:1px solid #0b83ca!important;
  box-shadow:0 7px 18px rgba(5,67,137,.16)!important;
}
.st-key-screen_data .personal-tip strong,
.st-key-screen_data .personal-tip p {
  color:#ffffff!important;
  opacity:1!important;
}
.st-key-screen_data .personal-tip p {line-height:1.48!important}

/* Pantalla 4: texto de empresa con espacios reales, sin solapamiento ni recorte. */
.st-key-screen_company {
  height:auto!important;
  min-height:0!important;
  max-height:none!important;
  overflow:visible!important;
}
.st-key-screen_company .company-intro {
  align-items:center!important;
  min-width:0!important;
  height:auto!important;
  min-height:76px!important;
  box-sizing:border-box!important;
  overflow:visible!important;
}
.st-key-screen_company .company-intro-copy {
  flex:1 1 0!important;
  min-width:0!important;
}
.st-key-screen_company .company-intro strong,
.st-key-screen_company .company-intro p,
.st-key-screen_company .company-other-heading strong,
.st-key-screen_company .company-other-heading p {
  display:block!important;
  position:static!important;
  height:auto!important;
  max-height:none!important;
  white-space:normal!important;
  overflow:visible!important;
  overflow-wrap:anywhere!important;
  line-height:1.42!important;
}
.st-key-screen_company .company-other-heading {
  align-items:center!important;
  justify-content:flex-start!important;
  background:linear-gradient(110deg,#0750a0,#0876bf)!important;
  border:1px solid #0a83cb!important;
  min-width:0!important;
  box-sizing:border-box!important;
}
.st-key-screen_company .company-other-heading strong,
.st-key-screen_company .company-other-heading p {
  color:#ffffff!important;
  opacity:1!important;
}
.st-key-screen_company .company-plus {
  background:linear-gradient(135deg,#16b9e8,#0874d8)!important;
  flex:0 0 34px!important;
}
.st-key-screen_company .company-selected-card {
  min-width:0!important;
  height:auto!important;
  min-height:66px!important;
  overflow:visible!important;
}
.st-key-screen_company .company-selected-text {
  min-width:0!important;
  overflow-wrap:anywhere!important;
}
.st-key-screen_company [data-testid="stSelectbox"],
.st-key-screen_company [data-testid="stTextInput"] {
  min-width:0!important;
  width:100%!important;
}

/* Pantalla 5: los datos del resumen se presentan en dos columnas también en móvil. */
.st-key-screen_summary .summary-details {
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  min-width:0!important;
}
.st-key-screen_summary .summary-item {
  min-width:0!important;
  overflow-wrap:anywhere!important;
}
.st-key-screen_summary .summary-item small,
.st-key-screen_summary .summary-item strong {
  white-space:normal!important;
  overflow-wrap:anywhere!important;
  word-break:break-word!important;
}

/* Pantalla 6: texto de la misión siempre blanco y legible sobre azul. */
.st-key-screen_mission .mission-explanation {
  background:linear-gradient(120deg,#062b68 0%,#07549c 56%,#087bc5 100%)!important;
  border:1px solid #148bd2!important;
  box-shadow:0 10px 26px rgba(4,42,100,.18)!important;
  color:#ffffff!important;
}
.st-key-screen_mission .mission-explanation h3,
.st-key-screen_mission .mission-explanation p,
.st-key-screen_mission .mission-explanation .mission-explanation-kicker {
  color:#ffffff!important;
  opacity:1!important;
}
.st-key-screen_mission .mission-explanation h3 {
  font-size:clamp(1.25rem,2.2vw,1.65rem)!important;
  line-height:1.25!important;
  margin:.25rem 0 .8rem!important;
}
.st-key-screen_mission .mission-explanation-paragraph {
  margin:.72rem 0!important;
  font-size:1rem!important;
  line-height:1.65!important;
  overflow-wrap:anywhere!important;
}
.st-key-screen_mission .mission-explanation-paragraph + .mission-explanation-paragraph {
  padding-top:.68rem!important;
  border-top:1px solid rgba(255,255,255,.2)!important;
}
.st-key-screen_mission .mission-explanation-kicker {
  font-size:.72rem!important;
  font-weight:900!important;
  letter-spacing:.09em!important;
  opacity:.9!important;
}

@media (max-width:760px) {
  /* Pantalla 3: conservar dos columnas reales en el ancho interior del teléfono. */
  .st-key-screen_data [data-testid="stHorizontalBlock"] {
    display:flex!important;
    flex-direction:row!important;
    flex-wrap:nowrap!important;
    align-items:flex-end!important;
    gap:.48rem!important;
    width:100%!important;
    max-width:100%!important;
    min-width:0!important;
  }
  .st-key-screen_data [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex:1 1 0!important;
    width:50%!important;
    min-width:0!important;
    max-width:50%!important;
    padding:0!important;
    box-sizing:border-box!important;
  }
  .st-key-screen_data .field-label {
    display:flex!important;
    align-items:flex-start!important;
    gap:.28rem!important;
    margin:.3rem 0 .22rem!important;
    min-width:0!important;
    font-size:.73rem!important;
    line-height:1.22!important;
    overflow-wrap:anywhere!important;
  }
  .st-key-screen_data .field-label svg {
    width:15px!important;
    height:15px!important;
    flex:0 0 15px!important;
    margin-top:1px!important;
  }
  .st-key-screen_data [data-testid="stTextInput"] input,
  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    width:100%!important;
    min-width:0!important;
    min-height:44px!important;
    padding-left:.48rem!important;
    padding-right:.35rem!important;
    font-size:16px!important;
  }
  .st-key-screen_data [data-testid="stTextInput"] input::placeholder {
    font-size:.78rem!important;
    opacity:1!important;
  }
  .st-key-screen_data .section-label {
    font-size:.94rem!important;
    line-height:1.25!important;
  }
  .st-key-screen_data .personal-tip {
    padding:.72rem .75rem!important;
    gap:.58rem!important;
    align-items:center!important;
  }
  .st-key-screen_data .personal-tip strong {font-size:.98rem!important}
  .st-key-screen_data .personal-tip p {font-size:.79rem!important;line-height:1.42!important}

  /* Pantalla 4: título, tarjetas y opción Otra sin texto montado ni contenido cortado. */
  .st-key-screen_company {
    padding:1rem .78rem 1.15rem!important;
    overflow:visible!important;
  }
  .st-key-screen_company .screen-heading {
    align-items:flex-start!important;
    gap:.58rem!important;
  }
  .st-key-screen_company .screen-heading h2 {
    font-size:1.2rem!important;
    line-height:1.22!important;
  }
  .st-key-screen_company .screen-heading p {
    font-size:.82rem!important;
    line-height:1.4!important;
  }
  .st-key-screen_company .company-intro {
    display:flex!important;
    align-items:flex-start!important;
    gap:.58rem!important;
    padding:.75rem!important;
    margin:.15rem 0 .7rem!important;
  }
  .st-key-screen_company .company-intro-icon {
    width:39px!important;
    height:39px!important;
    flex:0 0 39px!important;
  }
  .st-key-screen_company .company-intro-copy {flex:1 1 0!important;min-width:0!important}
  .st-key-screen_company .company-intro strong {font-size:.88rem!important;line-height:1.3!important}
  .st-key-screen_company .company-intro p {font-size:.78rem!important;line-height:1.4!important}
  .st-key-screen_company .company-other-heading {
    align-items:flex-start!important;
    gap:.55rem!important;
    margin:.7rem 0 .5rem!important;
    padding:.68rem!important;
  }
  .st-key-screen_company .company-other-heading > div {flex:1 1 0!important;min-width:0!important}
  .st-key-screen_company .company-other-heading strong {font-size:.88rem!important}
  .st-key-screen_company .company-other-heading p {font-size:.77rem!important}
  .st-key-screen_company .company-selected-card {padding:.62rem!important}
  .st-key-screen_company [data-testid="stHorizontalBlock"] {
    align-items:flex-end!important;
    min-width:0!important;
  }
  .st-key-screen_company .st-key-company_back,
  .st-key-screen_company .st-key-company_submit {min-width:0!important}

  /* Pantalla 5: resumen en dos columnas incluso en teléfonos estrechos. */
  .st-key-screen_summary .summary-layout {grid-template-columns:1fr!important;gap:.55rem!important}
  .st-key-screen_summary .summary-check-column {
    flex-direction:row!important;
    flex-wrap:wrap!important;
    justify-content:center!important;
    gap:.55rem!important;
    padding:.1rem!important;
  }
  .st-key-screen_summary .summary-check {width:58px!important;height:58px!important;font-size:2.15rem!important}
  .st-key-screen_summary .summary-details {
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:.38rem!important;
  }
  .st-key-screen_summary .summary-item {padding:.48rem .52rem!important}
  .st-key-screen_summary .summary-item small {font-size:.61rem!important;line-height:1.2!important}
  .st-key-screen_summary .summary-item strong {font-size:.78rem!important;line-height:1.28!important}
  .st-key-screen_summary .summary-note {font-size:.8rem!important;line-height:1.4!important}

  /* Pantalla 6: párrafos blancos, separados y fáciles de leer. */
  .st-key-screen_mission .mission-explanation {
    padding:.95rem .88rem!important;
    margin:.1rem 0 .8rem!important;
    border-radius:17px!important;
  }
  .st-key-screen_mission .mission-explanation h3 {font-size:1.18rem!important}
  .st-key-screen_mission .mission-explanation-paragraph {
    font-size:.88rem!important;
    line-height:1.55!important;
    margin:.62rem 0!important;
  }
}

@media (max-width:380px) {
  .st-key-screen_data [data-testid="stHorizontalBlock"] {gap:.36rem!important}
  .st-key-screen_data .field-label {font-size:.68rem!important}
  .st-key-screen_data [data-testid="stTextInput"] input,
  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] > div {font-size:16px!important}
  .st-key-screen_summary .summary-item small {font-size:.57rem!important}
  .st-key-screen_summary .summary-item strong {font-size:.73rem!important}
}
</style>
""", unsafe_allow_html=True)



# ---------- AJUSTE FINAL DE CONTRASTE Y ESPACIADO: DATOS / EMPRESA ----------
st.markdown(r"""
<style>
/* Pantalla 3: el texto del botón siguiente debe ser blanco, incluso dentro del Markdown interno de Streamlit. */
.st-key-screen_data .st-key-data_continue button,
.st-key-screen_data .st-key-data_continue button *,
.st-key-screen_data .st-key-data_continue button [data-testid="stMarkdownContainer"] p {
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
  opacity:1!important;
  font-weight:900!important;
}

/* Pantalla 4: títulos y etiquetas del selector con altura y separación reales. */
.st-key-screen_company .field-label {
  display:flex!important;
  position:relative!important;
  z-index:1!important;
  width:100%!important;
  min-height:25px!important;
  height:auto!important;
  margin:1rem 0 .38rem!important;
  padding:0!important;
  line-height:1.4!important;
  overflow:visible!important;
  white-space:normal!important;
  color:#103a73!important;
  font-size:.92rem!important;
  font-weight:900!important;
}
.st-key-screen_company [data-testid="stSelectbox"] {
  display:block!important;
  position:relative!important;
  z-index:1!important;
  width:100%!important;
  min-width:0!important;
  margin:.08rem 0 .45rem!important;
  overflow:visible!important;
}
.st-key-screen_company [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  min-height:52px!important;
  background:#ffffff!important;
  border:2px solid #8bbce9!important;
  border-radius:13px!important;
  color:#12396e!important;
  box-shadow:0 3px 10px rgba(8,74,145,.08)!important;
}
.st-key-screen_company [data-testid="stSelectbox"] [data-baseweb="select"] * {
  color:#12396e!important;
  opacity:1!important;
}
.st-key-screen_company .company-other-heading {
  display:flex!important;
  position:relative!important;
  z-index:0!important;
  width:100%!important;
  min-height:74px!important;
  height:auto!important;
  box-sizing:border-box!important;
  align-items:center!important;
  margin:1rem 0 1.35rem!important;
  padding:.85rem 1rem!important;
  overflow:visible!important;
  border-radius:15px!important;
  background:linear-gradient(110deg,#0750a0,#0876bf)!important;
  border:1px solid #0a83cb!important;
}
.st-key-screen_company .company-other-heading > div {
  flex:1 1 0!important;
  min-width:0!important;
}
.st-key-screen_company .company-other-heading strong,
.st-key-screen_company .company-other-heading p {
  display:block!important;
  position:static!important;
  height:auto!important;
  max-height:none!important;
  overflow:visible!important;
  white-space:normal!important;
  overflow-wrap:anywhere!important;
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
  opacity:1!important;
}
.st-key-screen_company .company-other-heading strong {
  font-size:1rem!important;
  line-height:1.35!important;
  font-weight:900!important;
}
.st-key-screen_company .company-other-heading p {
  margin:.2rem 0 0!important;
  font-size:.86rem!important;
  line-height:1.45!important;
}
.st-key-screen_company .company-plus {
  width:38px!important;
  height:38px!important;
  flex:0 0 38px!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  margin-right:.2rem!important;
  color:#ffffff!important;
  background:linear-gradient(135deg,#16b9e8,#0874d8)!important;
}
/* La fila de navegación queda debajo del aviso de Otra, nunca encima. */
.st-key-screen_company .st-key-company_nav {
  display:block!important;
  position:relative!important;
  z-index:2!important;
  width:100%!important;
  min-height:52px!important;
  height:auto!important;
  margin:1rem 0 .1rem!important;
  padding-top:.15rem!important;
  clear:both!important;
}
.st-key-screen_company .st-key-company_nav [data-testid="stHorizontalBlock"] {
  position:relative!important;
  z-index:2!important;
  width:100%!important;
  margin:0!important;
  align-items:stretch!important;
}

/* Texto blanco inequívoco en los botones principales de las pantallas 3 a 6. */
.st-key-screen_company .st-key-company_submit button,
.st-key-screen_company .st-key-company_submit button *,
.st-key-screen_summary .st-key-summary_continue button,
.st-key-screen_summary .st-key-summary_continue button *,
.st-key-screen_mission .st-key-mission_continue button,
.st-key-screen_mission .st-key-mission_continue button * {
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
  opacity:1!important;
  font-weight:900!important;
}
.st-key-screen_data .st-key-data_continue button,
.st-key-screen_company .st-key-company_submit button,
.st-key-screen_summary .st-key-summary_continue button,
.st-key-screen_mission .st-key-mission_continue button {
  background:linear-gradient(110deg,#073b8a 0%,#0874d4 70%,#0aa6dc 100%)!important;
  border:1px solid #0a85d6!important;
  text-shadow:0 1px 1px rgba(0,0,0,.12)!important;
}

@media(max-width:760px) {
  .st-key-screen_company .field-label {
    min-height:24px!important;
    margin:.8rem 0 .32rem!important;
    font-size:.84rem!important;
    line-height:1.35!important;
  }
  .st-key-screen_company [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height:49px!important;
  }
  .st-key-screen_company .company-other-heading {
    min-height:78px!important;
    margin:.85rem 0 1.25rem!important;
    padding:.76rem .78rem!important;
    align-items:center!important;
  }
  .st-key-screen_company .company-other-heading strong {font-size:.9rem!important;line-height:1.35!important}
  .st-key-screen_company .company-other-heading p {font-size:.78rem!important;line-height:1.45!important}
  .st-key-screen_company .st-key-company_nav {
    margin:1rem 0 .2rem!important;
    padding-top:.1rem!important;
  }
  .st-key-screen_company .st-key-company_nav [data-testid="stHorizontalBlock"] {
    gap:.5rem!important;
  }
  .st-key-screen_company .st-key-company_nav [data-testid="column"] {
    min-width:0!important;
    flex:1 1 0!important;
  }
  .st-key-screen_data .st-key-data_continue button,
  .st-key-screen_company .st-key-company_submit button {
    color:#ffffff!important;
    -webkit-text-fill-color:#ffffff!important;
  }
}
</style>
""", unsafe_allow_html=True)

# ---------- AJUSTE FINAL DE ORDEN Y ESPACIADO: PANTALLA EMPRESA ----------
st.markdown(r"""
<style>
.st-key-screen_company .company-dropdown-spacer {height:14px!important;min-height:14px!important;width:100%!important}
.st-key-screen_company .company-intro {margin-bottom:1rem!important}
.st-key-screen_company .company-meta-grid {
  display:grid!important;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr)!important;
  gap:.75rem!important;width:100%!important;margin:.8rem 0 1rem!important;align-items:stretch!important
}
.st-key-screen_company .company-meta-card {
  display:flex!important;flex-direction:column!important;justify-content:center!important;gap:.35rem!important;
  min-width:0!important;min-height:78px!important;padding:.8rem 1rem!important;box-sizing:border-box!important;
  border:1.5px solid #c6dcef!important;border-radius:14px!important;
  background:linear-gradient(135deg,#fff 0%,#f1f8ff 100%)!important;
  box-shadow:0 4px 12px rgba(8,65,135,.05)!important
}
.st-key-screen_company .company-meta-card small {
  display:block!important;color:#526b86!important;font-size:.7rem!important;font-weight:900!important;
  letter-spacing:.045em!important;line-height:1.25!important
}
.st-key-screen_company .company-meta-card strong {
  display:block!important;color:#082e6b!important;font-size:.98rem!important;font-weight:900!important;
  line-height:1.35!important;overflow-wrap:anywhere!important;word-break:break-word!important
}
.st-key-screen_company .company-meta-empty strong {color:#8394a8!important;font-size:.84rem!important;font-weight:650!important}
.st-key-screen_company .company-other-heading {
  margin:1rem 0 .25rem!important;min-height:0!important;height:auto!important;padding:.85rem 1rem!important;
  box-sizing:border-box!important;position:relative!important;z-index:0!important
}
.st-key-screen_company .st-key-company_nav {
  margin:1.3rem 0 .15rem!important;padding-top:.8rem!important;border-top:1px solid #dce8f3!important;
  display:block!important;position:relative!important;z-index:2!important;height:auto!important;min-height:52px!important
}
.st-key-screen_company .st-key-company_nav [data-testid="stHorizontalBlock"] {
  margin:0!important;align-items:stretch!important;position:relative!important;z-index:2!important
}
.st-key-screen_company .st-key-company_nav button {min-height:48px!important}
@media(max-width:760px) {
  .st-key-screen_company .company-dropdown-spacer {height:12px!important;min-height:12px!important}
  .st-key-screen_company .st-key-company_manual_fields [data-testid="stHorizontalBlock"] {
    display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;gap:.45rem!important;
    width:100%!important;min-width:0!important
  }
  .st-key-screen_company .st-key-company_manual_fields [data-testid="column"] {
    flex:1 1 0!important;width:50%!important;min-width:0!important;max-width:50%!important;
    padding:0!important;box-sizing:border-box!important
  }
  .st-key-screen_company .company-meta-grid {grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr)!important;gap:.5rem!important;margin:.65rem 0 .8rem!important}
  .st-key-screen_company .company-meta-card {min-height:76px!important;padding:.65rem .7rem!important}
  .st-key-screen_company .company-meta-card small {font-size:.61rem!important;line-height:1.2!important}
  .st-key-screen_company .company-meta-card strong {font-size:.8rem!important;line-height:1.3!important}
  .st-key-screen_company .company-meta-empty strong {font-size:.72rem!important}
  .st-key-screen_company .company-other-heading {margin:.85rem 0 .25rem!important;padding:.75rem .78rem!important}
  .st-key-screen_company .st-key-company_nav {margin:1.1rem 0 .1rem!important;padding-top:.7rem!important}
}
</style>
""", unsafe_allow_html=True)

# ---------- AJUSTE FINAL: SEPARACIÓN DEL DESPLEGABLE DE EMPRESA ----------
st.markdown(r"""
<style>
/* Separa claramente la etiqueta del selector. El contenido posterior baja
   con el flujo natural del documento, sin posiciones absolutas. */
.st-key-screen_company .company-dropdown-spacer {
    display:block!important;
    height:32px!important;
    min-height:32px!important;
    width:100%!important;
    margin:0!important;
    padding:0!important;
}
.st-key-screen_company [data-testid="stSelectbox"] {
    display:block!important;
    margin-top:.35rem!important;
    position:relative!important;
    top:auto!important;
}
@media (max-width:760px) {
    .st-key-screen_company .company-dropdown-spacer {
        height:27px!important;
        min-height:27px!important;
    }
    .st-key-screen_company [data-testid="stSelectbox"] {
        margin-top:.25rem!important;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------- AJUSTE EXCLUSIVO DE ESPACIOS VERTICALES: PANTALLAS 1 Y 2 ----------
# Pantalla 1: reduce únicamente el espacio azul superior/inferior en móvil.
# Pantalla 2: reduce el espacio vertical en PC y móvil; no altera márgenes laterales.
st.markdown(r"""
<style>
/* PORTADA: solo móvil. PC y márgenes laterales permanecen tal como están. */
@media (max-width:760px) {
  .main .block-container:has(.st-key-landing_wrap) {
    padding-top:.16rem!important;
    padding-bottom:.22rem!important;
  }
  .st-key-landing_wrap {
    margin-top:0!important;
    margin-bottom:.16rem!important;
  }
}

/* SELECCIÓN DE FONDO: menos espacio azul arriba y abajo en todos los tamaños. */
.main .block-container:has(.st-key-screen_fund) {
  padding-top:.32rem!important;
  padding-bottom:.42rem!important;
}
.main .block-container:has(.st-key-screen_fund) .brand-header {
  margin-top:0!important;
  margin-bottom:.34rem!important;
}
.main .block-container:has(.st-key-screen_fund) .journey-wrap {
  margin-top:0!important;
  margin-bottom:.34rem!important;
}
.main .block-container:has(.st-key-screen_fund) .st-key-screen_fund {
  margin-top:.18rem!important;
  margin-bottom:.22rem!important;
  padding-top:1.22rem!important;
  padding-bottom:1.22rem!important;
}

/* En móvil reducimos un poco más el espacio vertical, sin tocar los lados. */
@media (max-width:760px) {
  .main .block-container:has(.st-key-screen_fund) {
    padding-top:.24rem!important;
    padding-bottom:.30rem!important;
  }
  .main .block-container:has(.st-key-screen_fund) .brand-header {
    margin-bottom:.26rem!important;
  }
  .main .block-container:has(.st-key-screen_fund) .journey-wrap {
    margin-bottom:.26rem!important;
  }
  .main .block-container:has(.st-key-screen_fund) .st-key-screen_fund {
    margin-top:.14rem!important;
    margin-bottom:.18rem!important;
    padding-top:.88rem!important;
    padding-bottom:.88rem!important;
  }
}
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


def _crear_servicio_drive_nuevo():
    """Crea un cliente Drive nuevo para no reutilizar conexiones/sockets dañados."""
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
    return build("drive", "v3", credentials=credenciales, cache_discovery=False)


def _es_error_transitorio_drive(exc):
    """Identifica fallos de red/SSL y respuestas temporales de Google."""
    nombre = type(exc).__name__.lower()
    mensaje = str(exc).lower()
    if isinstance(exc, (BrokenPipeError, ConnectionError, TimeoutError, OSError)):
        return True
    if "ssl" in nombre or "ssl" in mensaje or "record layer failure" in mensaje:
        return True
    estado = getattr(getattr(exc, "resp", None), "status", None)
    return estado in (429, 500, 502, 503, 504)


def copiar_plantilla(doc_id, solicitud_id, nombre_persona):
    """Copia la plantilla en Drive con conexión nueva, reintentos e idempotencia."""
    nombre_seguro = re.sub(
        r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ_-]+",
        "_",
        str(nombre_persona)
    ).strip("_")
    nombre_archivo = f"Solicitud_{solicitud_id}_{nombre_seguro}"[:180]
    ultimo_error = None

    for intento in range(3):
        try:
            # Un cliente nuevo por intento evita conservar un socket SSL defectuoso.
            servicio = _crear_servicio_drive_nuevo()
            folder_id = str(obtener_config_oauth().get("solicitudes_folder_id", "")).strip()
            if not folder_id:
                raise RuntimeError("Falta solicitudes_folder_id en [google_oauth] de Streamlit Secrets.")

            # Si la petición anterior sí creó el archivo pero se perdió la respuesta,
            # recuperamos esa copia por nombre y carpeta para no duplicarla.
            consulta = (
                "name = '" + nombre_archivo.replace("\\", "\\\\").replace("'", "\\'") + "' "
                "and '" + folder_id + "' in parents and trashed = false"
            )
            encontrados = servicio.files().list(
                q=consulta,
                pageSize=10,
                orderBy="createdTime desc",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields="files(id,name,webViewLink,parents)"
            ).execute(num_retries=2).get("files", [])
            if encontrados:
                return encontrados[0]

            return servicio.files().copy(
                fileId=str(doc_id).strip(),
                body={"name": nombre_archivo, "parents": [folder_id]},
                supportsAllDrives=True,
                fields="id,name,webViewLink,parents"
            ).execute(num_retries=2)

        except Exception as exc:
            ultimo_error = exc
            if not _es_error_transitorio_drive(exc):
                raise RuntimeError(f"Google Drive rechazó la copia de la plantilla: {exc}") from exc
            if intento < 2:
                time.sleep(1.5 * (intento + 1))
                continue

    raise RuntimeError(
        "Google Drive presentó un fallo temporal de conexión/SSL al copiar la plantilla "
        f"después de 3 intentos. Detalle técnico: {ultimo_error}"
    ) from ultimo_error


def rellenar_plantilla_google_docs(document_id, valores):
    """Sustituye marcadores en la copia; reintenta fallos transitorios de conexión."""
    solicitudes = [
        {"replaceAllText": {
            "containsText": {"text": marcador, "matchCase": True},
            "replaceText": str(valor or "").upper()
        }}
        for marcador, valor in valores.items()
    ]
    ultimo_error = None
    for intento in range(3):
        try:
            # Crear un cliente nuevo en cada intento evita reutilizar un socket roto.
            datos = obtener_config_oauth()
            refresh_token = str(datos.get("refresh_token", "")).strip()
            credenciales = UserCredentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=datos["client_id"],
                client_secret=datos["client_secret"],
                scopes=[GOOGLE_DRIVE_SCOPE]
            )
            servicio = build("docs", "v1", credentials=credenciales, cache_discovery=False)
            return servicio.documents().batchUpdate(
                documentId=document_id,
                body={"requests": solicitudes}
            ).execute(num_retries=2)
        except (BrokenPipeError, ConnectionError, TimeoutError, OSError) as exc:
            ultimo_error = exc
            if intento < 2:
                time.sleep(1.5 * (intento + 1))
                continue
            raise RuntimeError(f"Falló la conexión temporal con Google Docs después de 3 intentos: {exc}") from exc
        except Exception:
            raise
    raise RuntimeError(f"No se pudo actualizar la copia de Google Docs: {ultimo_error}")


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


# ---------- RECORRIDO DEFINITIVO ----------
# 1 landing -> 2 seleccionar_fondo -> 3 datos_personales -> 4 resumen
# -> 5 mision -> 6 empresa -> final (generación + confirmación/PDF).
# No se muestra la antigua pantalla de motivo de retiro.

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
        "logo_persona_corriendo",
        "logo_cesantias_al_instante",
        "cesantias_al_instante",
        "logo_cesantias",
        "logo_app_cesantias",
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


def obtener_imagen_hero_path(es_pc=False):
    """Localiza la foto específica para PC o móvil, con alternativa automática.

    Nombres esperados dentro de assets:
      - hero_mujer_PC.png  -> escritorio (ancho desde 761 px)
      - hero_mujer.png     -> teléfono (hasta 760 px)
    Si falta una de las dos, utiliza la otra como respaldo.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nombre_preferido = "hero_mujer_PC.png" if es_pc else "hero_mujer.png"
    nombre_respaldo = "hero_mujer.png" if es_pc else "hero_mujer_PC.png"
    for carpeta in (os.path.join(base_dir, "assets"), base_dir):
        for nombre in (nombre_preferido, nombre_respaldo):
            ruta = os.path.join(carpeta, nombre)
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


def icon_svg(nombre):
    """Iconos SVG lineales para mantener un lenguaje visual coherente."""
    paths = {
        "fund": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5M9 21v-7h6v7"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
        "file": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
        "check": '<path d="m5 12 4 4L19 6"/>',
        "mission": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "building": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M9 7h1m4 0h1M9 11h1m4 0h1M9 15h1m4 0h1M10 21v-3h4v3"/>',
        "shield": '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-4"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
        "phone": '<path d="M6.5 3.5 9 3l2 5-2 1.5a14 14 0 0 0 5.5 5.5L16 13l5 2-.5 2.5A3 3 0 0 1 17.5 20C9 19 5 15 4 6.5a3 3 0 0 1 2.5-3Z"/>',
        "pin": '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
        "wallet": '<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 8h18M16 14h2"/>',
    }
    return '<svg viewBox="0 0 24 24" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">' + paths.get(nombre, paths["file"]) + '</svg>'


def render_screen_heading(icono, titulo, subtitulo):
    st.markdown(
        f'<div class="screen-heading"><div class="screen-icon">{icon_svg(icono)}</div>'
        f'<div><h2>{html.escape(titulo)}</h2><p>{html.escape(subtitulo)}</p></div></div>',
        unsafe_allow_html=True
    )

def render_field_label(icono, texto):
    st.markdown(
        f'<div class="field-label">{icon_svg(icono)}<span>{html.escape(texto)}</span></div>',
        unsafe_allow_html=True
    )


def render_brand_header(etapa=2):
    """Encabezado de marca y progreso del flujo nuevo de seis etapas."""
    logo_uri = imagen_data_uri(obtener_logo_app_path())
    logo_html = f'<img src="{logo_uri}" alt="Cesantías al Instante">' if logo_uri else '<strong>Cesantías al Instante</strong>'
    st.markdown(
        '<div class="brand-header"><div class="brand-logo-wrap">' + logo_html + '</div>'
        '<div class="brand-trust"><span>✓</span> Trámite fácil y seguro</div></div>',
        unsafe_allow_html=True
    )
    # Orden definitivo: fondo, datos, empresa, resumen y misión.
    etiquetas = ["Inicio", "Fondo", "Datos", "Empresa", "Resumen", "Misión"]
    pasos = []
    for n, etiqueta in enumerate(etiquetas, 1):
        clase = "active" if n == etapa else ("done" if n < etapa or etapa > 6 else "")
        simbolo = "✓" if n < etapa or etapa > 6 else str(n)
        pasos.append(
            f'<div class="journey-step {clase}"><div class="journey-dot">{simbolo}</div>'
            f'<span>{etiqueta}</span></div>'
        )
    st.markdown('<div class="journey-wrap"><div class="journey">' + ''.join(pasos) + '</div></div>', unsafe_allow_html=True)

def reiniciar_solicitud():
    """Limpia únicamente los datos del trámite; la autorización y servicios permanecen intactos."""
    llaves = [
        "proposito", "monto", "monto_limpio", "fondo", "nombre", "cedula", "telefono", "email",
        "empresa", "nit", "ciudad", "departamento", "empresa_manual", "nit_manual",
        "empresa_seleccionada", "saldo_verificado", "saldo_limpio", "solicitud_guardada",
        "doc_id_plantilla", "nombre_plantilla", "plantilla_url", "doc_id_copia", "url_copia",
        "solicitud_id", "documento_rellenado", "pdf_id", "pdf_url", "pdf_generado", "tipo_empresa",
    ]
    for key in llaves:
        st.session_state[key] = ""
    widgets = [
        "ciudad_widget", "departamento_widget", "empresa_manual_widget", "nit_manual_widget",
        "empresa_widget", "nit_busqueda_widget", "saldo_widget", "monto_raw_widget", "telefono_widget",
        "nombre_widget", "cedula_widget", "email_widget",
    ]
    for key in widgets:
        st.session_state[key] = ""


def render_landing():
    """Bienvenida con CTA Streamlit dentro del mismo contenedor visual."""
    logo_uri = imagen_data_uri(obtener_logo_app_path())
    # La etiqueta <picture> selecciona PC o móvil según el ancho real del navegador.
    hero_pc_uri = imagen_data_uri(obtener_imagen_hero_path(es_pc=True))
    hero_mobile_uri = imagen_data_uri(obtener_imagen_hero_path(es_pc=False))
    logo_html = f'<img src="{logo_uri}" alt="Logo Cesantías al Instante">' if logo_uri else '<strong>Cesantías al Instante</strong>'
    if hero_pc_uri or hero_mobile_uri:
        imagen_respaldo = hero_mobile_uri or hero_pc_uri
        fuente_pc = (
            f'<source media="(min-width: 761px)" srcset="{hero_pc_uri}">'
            if hero_pc_uri else ""
        )
        hero_html = (
            f'<picture class="hero-picture">{fuente_pc}'
            f'<img src="{imagen_respaldo}" alt="Asesora de Cesantías al Instante">'
            f'</picture>'
        )
    else:
        hero_html = ''
    with st.container(key="landing_wrap"):
        st.markdown(f"""
        <section class="hero-shell">
          <div class="hero-copy">
            <div class="hero-logo">{logo_html}</div>
            <h1 class="hero-title">Tus cesantías,<span>más cerca de ti</span></h1>
            <p class="hero-description">El retiro de cesantías está integrado principalmente en el Decreto 1072 de 2015 (Decreto Único Reglamentario del Sector Trabajo), el cual fue adicionado y actualizado de forma integral por el Decreto 1562 de 2019 para consolidar los plazos y trámites de retiro.</p>
            <div class="hero-benefits">
              <div class="hero-benefit"><i>ϟ</i> Rápido</div>
              <div class="hero-benefit"><i>✓</i> Seguro</div>
              <div class="hero-benefit"><i>✓</i> Fácil</div>
            </div>
          </div>
          <div class="hero-person">{hero_html}</div>
        </section>
        """, unsafe_allow_html=True)
        # Botón interno: conserva la URL y la sesión actual de Streamlit.
        if st.button("Comenzar ahora  ➜", key="landing_start", use_container_width=False):
            reiniciar_solicitud()
            st.session_state.step = "seleccionar_fondo"
            st.rerun()


def buscar_logo_fondo(nombre_archivo):
    """Localiza los logos oficiales ya existentes en assets o assets/logos."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nombre_base = os.path.splitext(nombre_archivo or "")[0].lower()
    aliases = {
        "porvenir_logo": {"porvenir_logo", "porvenir"},
        "colfondos_logo": {"colfondos_logo", "colfondos"},
        "proteccion_logo": {"proteccion_logo", "protección_logo", "proteccion"},
        "fna_logo": {"fna_logo", "fna", "fondo_nacional_del_ahorro"},
    }
    validos = aliases.get(nombre_base, {nombre_base})
    for carpeta in (os.path.join(base_dir, "assets"), os.path.join(base_dir, "assets", "logos")):
        if not os.path.isdir(carpeta):
            continue
        for archivo in os.listdir(carpeta):
            base, extension = os.path.splitext(archivo)
            if base.lower() in validos and extension.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                return os.path.join(carpeta, archivo)
    return None


def render_seleccionar_fondo():
    """Selección visual de fondo: tarjetas completas clicables, dos por fila."""
    render_brand_header(2)
    with st.container(key="screen_fund"):
        render_screen_heading(
            "fund",
            "Selecciona tu fondo de cesantías",
            "Toca el nombre o el logo del fondo donde tienes tus cesantías."
        )

        fondos = [
            {"slug": "porvenir", "nombre": "Porvenir", "valor": "Porvenir", "logo": "Porvenir_logo.png", "icono": "fund"},
            {"slug": "colfondos", "nombre": "Colfondos", "valor": "Colfondos", "logo": "Colfondos_logo.png", "icono": "building"},
            {"slug": "proteccion", "nombre": "Protección", "valor": "Protección", "logo": "Proteccion_logo.png", "icono": "shield"},
            {"slug": "fna", "nombre": "FNA", "valor": "FNA", "logo": "FNA_logo.png", "icono": "building"},
            # Se conserva "Otro" como valor interno porque el backend y las plantillas lo esperan.
            {"slug": "otro_fondo", "nombre": "Otro Fondo", "valor": "Otro", "logo": None, "icono": "wallet"},
        ]

        def mostrar_tarjeta_fondo(fondo):
            slug = fondo["slug"]
            with st.container(key=f"fund_card_{slug}"):
                # Nombre y logo dentro de un único bloque HTML para controlar
                # con precisión la separación vertical en teléfonos.
                logo_path = buscar_logo_fondo(fondo["logo"]) if fondo["logo"] else None
                if logo_path:
                    with open(logo_path, "rb") as archivo_logo:
                        logo_b64 = base64.b64encode(archivo_logo.read()).decode("ascii")
                    mime = mimetypes.guess_type(logo_path)[0] or "image/png"
                    logo_html = (
                        f'<img src="data:{mime};base64,{logo_b64}" '
                        f'alt="Logo de {html.escape(fondo['nombre'])}">'
                    )
                else:
                    logo_html = icon_svg(fondo["icono"])

                st.markdown(
                    '<div class="fund-card-content">'
                    f'<div class="fund-card-title">{html.escape(fondo["nombre"])}</div>'
                    f'<div class="fund-card-logo">{logo_html}</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                # Botón transparente superpuesto a la tarjeta completa:
                # tocar el nombre, el logo o cualquier espacio de la tarjeta selecciona el fondo.
                if st.button(
                    f"Seleccionar {fondo['nombre']}",
                    key=f"fund_pick_{slug}",
                    use_container_width=True,
                    help=f"Seleccionar {fondo['nombre']}"
                ):
                    st.session_state.fondo = fondo["valor"]
                    st.session_state.step = "datos_personales"
                    st.rerun()

        # Dos fondos por fila: Porvenir/Colfondos y Protección/FNA.
        for inicio in range(0, 4, 2):
            cols = st.columns(2, gap="large")
            for col, fondo in zip(cols, fondos[inicio:inicio + 2]):
                with col:
                    mostrar_tarjeta_fondo(fondo)

        # La única opción adicional va sola y centrada al final.
        left, center, right = st.columns([1, 2, 1], gap="medium")
        with center:
            mostrar_tarjeta_fondo(fondos[4])

        if st.button("← Volver al inicio", key="fund_back", use_container_width=True):
            st.session_state.step = "landing"
            st.rerun()


def limpiar_telefono_widget():
    """Mantiene el WhatsApp compuesto únicamente por dígitos."""
    valor = str(st.session_state.get("telefono_widget", ""))
    st.session_state.telefono_widget = re.sub(r"\D", "", valor)[:10]


def limpiar_cedula_widget():
    """Mantiene la cédula compuesta únicamente por dígitos."""
    valor = str(st.session_state.get("cedula_widget", ""))
    st.session_state.cedula_widget = re.sub(r"\D", "", valor)


def render_datos_personales():
    """Pantalla 3: datos personales y valores del retiro, en una tarjeta limpia."""
    render_brand_header(3)
    with st.container(key="screen_data"):
        render_screen_heading(
            "user", "Datos de tu solicitud",
            "Completa tus datos para preparar correctamente la carta de retiro."
        )

        numeros = {
            "Porvenir": "01 8000 111 222", "Colfondos": "01 8000 123 456",
            "Protección": "01 8000 789 012", "FNA": "01 8000 456 789", "Otro": "01 8000 000 000"
        }
        numero = numeros.get(st.session_state.get("fondo", "Otro"), "01 8000 000 000")
        st.markdown(
            f'<div class="personal-tip"><div class="personal-tip-icon">{icon_svg("phone")}</div>'
            f'<div><strong>{html.escape(numero)}</strong><p>Consulta tu saldo en los canales oficiales de tu fondo. Sigue las indicaciones y escribe abajo el saldo que te informen.</p></div></div>',
            unsafe_allow_html=True
        )

        st.markdown(f'<div class="section-label">{icon_svg("wallet")} Información del retiro</div>', unsafe_allow_html=True)
        c_saldo, c_monto = st.columns(2, gap="medium")
        with c_saldo:
            render_field_label("wallet", "Saldo disponible (COP)")
            saldo_raw = st.text_input("Saldo disponible (COP)", label_visibility="collapsed", placeholder="Ej. 10000000", key="saldo_widget")
        with c_monto:
            render_field_label("wallet", "Monto que deseas retirar (COP)")
            monto_raw = st.text_input("Monto que deseas retirar (COP)", label_visibility="collapsed", placeholder="Ej. 900000", key="monto_raw_widget")
        c_saldo_caption, c_monto_caption = st.columns(2, gap="medium")
        with c_saldo_caption:
            limpio = re.sub(r"\D", "", str(saldo_raw))
            if limpio:
                st.caption("Saldo: $" + f"{int(limpio):,}".replace(",", "."))
        with c_monto_caption:
            limpio = re.sub(r"\D", "", str(monto_raw))
            if limpio:
                st.caption("Monto: $" + f"{int(limpio):,}".replace(",", "."))

        st.markdown(f'<div class="section-label">{icon_svg("user")} Tus datos personales</div>', unsafe_allow_html=True)
        departamentos = [
            "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá, D.C.", "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo", "Quindío", "Risaralda", "San Andrés y Providencia", "Santander", "Sucre", "Tolima", "Valle del Cauca", "Vaupés", "Vichada"
        ]

        # Tres filas de dos campos. Streamlit las apila en móvil conservando el orden.
        col_nombre, col_cedula = st.columns(2, gap="large")
        with col_nombre:
            render_field_label("user", "Nombre completo")
            nombre = st.text_input("Nombre completo", label_visibility="collapsed", placeholder="Como aparece en tu cédula", key="nombre_widget")
        with col_cedula:
            render_field_label("file", "Cédula")
            cedula = st.text_input("Cédula", label_visibility="collapsed", placeholder="Escribe solo números", key="cedula_widget", on_change=limpiar_cedula_widget)

        col_telefono, col_email = st.columns(2, gap="large")
        with col_telefono:
            render_field_label("phone", "Teléfono / WhatsApp")
            telefono = st.text_input("Teléfono / WhatsApp", label_visibility="collapsed", placeholder="Ej. 3001234567", key="telefono_widget", on_change=limpiar_telefono_widget)
        with col_email:
            render_field_label("mail", "Correo electrónico")
            email_val = st.text_input("Correo electrónico", label_visibility="collapsed", placeholder="nombre@correo.com", key="email_widget")

        col_departamento, col_ciudad = st.columns(2, gap="large")
        with col_departamento:
            render_field_label("pin", "Departamento")
            departamento = st.selectbox("Departamento", [""] + departamentos, label_visibility="collapsed", key="departamento_widget", placeholder="Selecciona tu departamento")
        with col_ciudad:
            render_field_label("pin", "Ciudad")
            ciudad = st.text_input("Ciudad", label_visibility="collapsed", placeholder="Escribe tu ciudad", key="ciudad_widget")

        with st.container(key="data_navigation"):
            nav_back, nav_next = st.columns([1, 1.65], gap="medium")
            with nav_back:
                if st.button("← Atrás", key="data_back", use_container_width=True):
                    st.session_state.step = "seleccionar_fondo"
                    st.rerun()
            with nav_next:
                if st.button("Siguiente: empresa  →", key="data_continue", use_container_width=True):
                    saldo_limpio = re.sub(r"\D", "", str(saldo_raw))
                    monto_limpio = re.sub(r"\D", "", str(monto_raw))
                    telefono_limpio = re.sub(r"\D", "", str(telefono))
                    cedula_limpia = re.sub(r"\D", "", str(cedula))
                    email_limpio = str(email_val).strip()
                    if not all([saldo_limpio, monto_limpio, nombre.strip(), cedula_limpia, telefono_limpio, email_limpio, departamento, ciudad.strip()]):
                        st.error("Completa el saldo, el monto y los seis datos personales antes de continuar.")
                        st.stop()
                    if not st.session_state.get("fondo"):
                        st.error("Selecciona primero tu fondo de cesantías.")
                        st.stop()
                    if len(telefono_limpio) != 10:
                        st.error("El teléfono / WhatsApp debe tener exactamente 10 dígitos.")
                        st.stop()
                    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email_limpio):
                        st.error("Escribe un correo electrónico válido.")
                        st.stop()
                    if int(monto_limpio) > int(saldo_limpio):
                        st.error("El monto a retirar no puede superar el saldo disponible.")
                        st.stop()

                    # Valor general interno para el marcador heredado; no se muestra un motivo.
                    st.session_state.proposito = "Retiro de cesantías"
                    st.session_state.saldo_limpio = saldo_limpio
                    st.session_state.saldo_verificado = f"${int(saldo_limpio):,}".replace(",", ".")
                    st.session_state.monto = f"{int(monto_limpio):,}".replace(",", ".")
                    st.session_state.monto_limpio = monto_limpio
                    st.session_state.nombre = nombre.strip()
                    st.session_state.cedula = cedula_limpia
                    st.session_state.telefono = telefono_limpio
                    st.session_state.email = email_limpio
                    st.session_state.departamento = departamento
                    st.session_state.ciudad = ciudad.strip()
                    st.session_state.step = "empresa"
                    st.rerun()

def render_resumen():
    """Pantalla 5: resumen con verificación, empresa y NIT antes de confirmar."""
    render_brand_header(5)
    with st.container(key="screen_summary"):
        render_screen_heading("file", "Resumen de tu solicitud", "Verifica que toda la información esté correcta antes de continuar.")

        filas = [
            ("Fondo de cesantías", st.session_state.get("fondo", "")),
            ("Empresa", st.session_state.get("empresa", "")),
            ("NIT", st.session_state.get("nit", "")),
            ("Nombre completo", st.session_state.get("nombre", "")),
            ("Cédula", st.session_state.get("cedula", "")),
            ("Celular / WhatsApp", st.session_state.get("telefono", "")),
            ("Correo electrónico", st.session_state.get("email", "")),
            ("Departamento", st.session_state.get("departamento", "")),
            ("Ciudad", st.session_state.get("ciudad", "")),
            ("Saldo disponible", st.session_state.get("saldo_verificado", "")),
            ("Monto solicitado", "$" + str(st.session_state.get("monto", ""))),
        ]
        items_html = "".join(
            '<div class="summary-item"><small>' + html.escape(etiqueta) + '</small><strong>' + html.escape(str(valor)) + '</strong></div>'
            for etiqueta, valor in filas
        )
        with st.container(key="summary_panel"):
            st.markdown(
                '<div class="summary-layout"><div class="summary-check-column">'
                '<div class="summary-check">✓</div><strong>Información verificada</strong>'
                '<span>Revisa tus datos antes de avanzar.</span></div>'
                '<div class="summary-details">' + items_html + '</div></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="summary-note"><span class="summary-note-icon">i</span>'
            '<span>En la siguiente pantalla te contaremos cómo acompañamos tu solicitud. Podrás regresar si necesitas corregir algún dato.</span></div>',
            unsafe_allow_html=True
        )
        nav_back, nav_next = st.columns([1, 1.65], gap="medium")
        with nav_back:
            if st.button("← Corregir empresa", key="summary_back", use_container_width=True):
                st.session_state.step = "empresa"
                st.rerun()
        with nav_next:
            if st.button("Continuar  →", key="summary_continue", use_container_width=True):
                st.session_state.step = "mision"
                st.rerun()

def render_mision():
    """Pantalla 6: explicación del proceso y acompañamiento de Cesantías al Instante."""
    render_brand_header(6)
    with st.container(key="screen_mission"):
        render_screen_heading(
            "mission", "Nuestra misión",
            "Conoce cómo te acompañamos durante el proceso de retiro de tus cesantías."
        )
        parrafos = [
            "Te explico en qué consiste: manejamos personal interno que se encarga de hacer todo el proceso.",
            "Se sube directamente el permiso a la plataforma de Porvenir y se te genera un certificado bajo el concepto de mejora de vivienda, con el cual vas a poder realizar el retiro de tus cesantías.",
            "Ese certificado lo vas a imprimir a color y te diriges directamente a un banco AV Villas con tu cédula. El dinero únicamente se entrega a ti.",
            "Generamos el permiso directamente con el fondo sin mediar con tu empresa. Es un trámite 100% seguro y rápido."
        ]
        parrafos_html = "".join(
            '<p class="mission-explanation-paragraph">' + html.escape(p) + '</p>'
            for p in parrafos
        )
        st.markdown(
            '<section class="mission-hero mission-explanation">'
            '<div class="mission-explanation-kicker">ASÍ FUNCIONA EL PROCESO</div>'
            '<h3>Te acompañamos de principio a fin</h3>'
            + parrafos_html +
            '</section>',
            unsafe_allow_html=True
        )

        nav_back, nav_next = st.columns([1, 1.65], gap="medium")
        with nav_back:
            if st.button("← Atrás", key="mission_back", use_container_width=True):
                st.session_state.step = "resumen"
                st.rerun()
        with nav_next:
            if st.button("Preparar mi carta  →", key="mission_continue", use_container_width=True):
                st.session_state.step = "generando"
                st.rerun()

def render_empresa():
    """Selecciona la empresa por nombre o NIT usando la misma hoja de Google Sheets."""
    render_brand_header(4)
    with st.container(key="screen_company"):
        render_screen_heading(
            "building", "Nombre de la empresa",
            "Selecciona tu empresa para asociar su NIT."
        )

        # La misma hoja alimenta los dos selectores: por nombre y por NIT.
        try:
            df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
            if "Nombre_Empresa" not in df_empresas.columns:
                raise ValueError("La hoja Empresas debe tener la columna Nombre_Empresa.")
            if "NIT" not in df_empresas.columns:
                raise ValueError("La hoja Empresas debe tener la columna NIT para habilitar la búsqueda por NIT.")

            def valor_texto(valor):
                if pd.isna(valor):
                    return ""
                texto = str(valor).strip()
                # Google Sheets puede devolver NIT numéricos como 900123456.0.
                if re.fullmatch(r"\d+\.0", texto):
                    texto = texto[:-2]
                return texto

            filas_validas = []
            for _, fila in df_empresas.iterrows():
                nombre_fila = valor_texto(fila.get("Nombre_Empresa", ""))
                nit_fila = valor_texto(fila.get("NIT", ""))
                if nombre_fila and nombre_fila.casefold() != "otra":
                    filas_validas.append((nombre_fila, nit_fila))

            lista_empresas = list(dict.fromkeys(nombre for nombre, _ in filas_validas))
            nit_por_empresa = {}
            empresa_por_nit = {}
            lista_nit = []
            for nombre_fila, nit_fila in filas_validas:
                if nit_fila:
                    nit_por_empresa.setdefault(nombre_fila, nit_fila)
                    if nit_fila not in empresa_por_nit:
                        empresa_por_nit[nit_fila] = nombre_fila
                        lista_nit.append(nit_fila)
        except Exception as exc:
            st.error(f"No fue posible cargar las empresas y sus NIT desde Google Sheets: {exc}")
            st.stop()

        opciones_empresa = [""] + ["Otra"] + lista_empresas
        opciones_nit = [""] + lista_nit

        # Evita que valores guardados de una sesión anterior queden fuera de las opciones.
        if st.session_state.get("empresa_widget", "") not in opciones_empresa:
            st.session_state["empresa_widget"] = ""
        if st.session_state.get("nit_busqueda_widget", "") not in opciones_nit:
            st.session_state["nit_busqueda_widget"] = ""

        # Mantiene sincronizados ambos desplegables sin modificar las claves después
        # de que Streamlit haya creado los widgets.
        empresa_actual = st.session_state.get("empresa_widget", "")
        if empresa_actual == "Otra":
            st.session_state["nit_busqueda_widget"] = ""
        elif empresa_actual and nit_por_empresa.get(empresa_actual):
            st.session_state["nit_busqueda_widget"] = nit_por_empresa[empresa_actual]
        elif not empresa_actual and st.session_state.get("nit_busqueda_widget"):
            empresa_desde_nit = empresa_por_nit.get(st.session_state["nit_busqueda_widget"], "")
            if empresa_desde_nit:
                st.session_state["empresa_widget"] = empresa_desde_nit

        def sincronizar_nit_desde_empresa():
            seleccion = st.session_state.get("empresa_widget", "")
            st.session_state["nit_busqueda_widget"] = nit_por_empresa.get(seleccion, "")
            if seleccion == "Otra":
                st.session_state["empresa_manual_widget"] = ""
                st.session_state["nit_manual_widget"] = ""

        def sincronizar_empresa_desde_nit():
            nit_elegido = st.session_state.get("nit_busqueda_widget", "")
            empresa_encontrada = empresa_por_nit.get(nit_elegido, "")
            if empresa_encontrada:
                st.session_state["empresa_widget"] = empresa_encontrada

        with st.container(key="company_selectors"):
            col_empresa, col_nit = st.columns([1.12, .88], gap="medium")
            with col_empresa:
                render_field_label("building", "Busca o selecciona tu empresa")
                empresa_seleccionada = st.selectbox(
                    "Busca o selecciona tu empresa", opciones_empresa,
                    label_visibility="collapsed", key="empresa_widget",
                    placeholder="Escribe para buscar tu empresa",
                    help="Selecciona «Otra» si tu empresa no aparece en Google Sheets.",
                    on_change=sincronizar_nit_desde_empresa
                )
            with col_nit:
                render_field_label("file", "Buscar tu empresa por NIT")
                nit_busqueda = st.selectbox(
                    "Buscar tu empresa por NIT", opciones_nit,
                    label_visibility="collapsed", key="nit_busqueda_widget",
                    placeholder="Busca o selecciona el NIT",
                    help="Este listado se consulta desde la columna NIT de la hoja Empresas.",
                    disabled=not bool(lista_nit),
                    on_change=sincronizar_empresa_desde_nit
                )

        empresa_manual = ""
        nit_manual = ""
        nit_visible = ""

        # Para empresas registradas, se muestran nombre y NIT completos.
        # Al elegir «Otra», las tarjetas informativas desaparecen y los campos manuales
        # aparecen debajo del aviso, como solicitó el usuario.
        if empresa_seleccionada and empresa_seleccionada != "Otra":
            nit_visible = nit_por_empresa.get(empresa_seleccionada, "")
            empresa_segura = html.escape(empresa_seleccionada)
            nit_seguro = html.escape(nit_visible or "No registrado en Google Sheets")
            st.markdown(
                '<div class="company-meta-grid">'
                '<div class="company-meta-card"><small>NOMBRE DE LA EMPRESA</small>'
                f'<strong>{empresa_segura}</strong></div>'
                '<div class="company-meta-card"><small>NIT</small>'
                f'<strong>{nit_seguro}</strong></div>'
                '</div>',
                unsafe_allow_html=True
            )
        elif not empresa_seleccionada:
            st.markdown(
                '<div class="company-meta-grid">'
                '<div class="company-meta-card company-meta-empty"><small>NOMBRE DE LA EMPRESA</small>'
                '<strong>Se mostrará al seleccionar</strong></div>'
                '<div class="company-meta-card company-meta-empty"><small>NIT</small>'
                '<strong>Se mostrará al seleccionar</strong></div>'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="company-other-heading"><span class="company-plus">+</span>'
            '<div><strong>¿No encuentras tu empresa?</strong>'
            '<p>Selecciona «Otra» al inicio del listado para escribir el nombre y el NIT manualmente.</p></div></div>',
            unsafe_allow_html=True
        )

        if empresa_seleccionada == "Otra":
            with st.container(key="company_manual_fields"):
                mc1, mc2 = st.columns([1.12, .88], gap="medium")
                with mc1:
                    render_field_label("building", "Nombre de la empresa")
                    empresa_manual = st.text_input(
                        "Nombre de la empresa", label_visibility="collapsed",
                        placeholder="Escribe la razón social", key="empresa_manual_widget"
                    )
                with mc2:
                    render_field_label("file", "NIT de la empresa")
                    nit_manual = st.text_input(
                        "NIT de la empresa", label_visibility="collapsed",
                        placeholder="Escribe el NIT", key="nit_manual_widget"
                    )

        with st.container(key="company_nav"):
            nav_back, nav_next = st.columns([1, 1.65], gap="medium")
            with nav_back:
                if st.button("← Atrás", key="company_back", use_container_width=True):
                    st.session_state.step = "datos_personales"
                    st.rerun()
            with nav_next:
                if st.button("Siguiente: resumen  →", key="company_submit", use_container_width=True):
                    if not empresa_seleccionada:
                        st.error("Selecciona tu empresa por nombre o por NIT, o elige «Otra».")
                        st.stop()
                    try:
                        if empresa_seleccionada == "Otra":
                            if not empresa_manual.strip() or not nit_manual.strip():
                                st.error("Escribe el nombre y el NIT de tu empresa.")
                                st.stop()
                            resolver_empresa_y_plantilla(empresa_seleccionada, empresa_manual, nit_manual)
                            st.session_state.empresa = empresa_manual.strip()
                            st.session_state.nit = nit_manual.strip()
                        else:
                            resolver_empresa_y_plantilla(empresa_seleccionada)
                            st.session_state.empresa = empresa_seleccionada
                        if not st.session_state.get("nit"):
                            st.error("No encontramos un NIT asociado a esta empresa. Revisa la columna NIT de la hoja Empresas.")
                            st.stop()
                        if not st.session_state.get("doc_id_plantilla"):
                            if empresa_seleccionada == "Otra":
                                st.error("No encontramos la plantilla universal. En la fila «Otra» de la hoja Empresas, coloca el ID del Google Docs universal en la columna Doc_ID.")
                            else:
                                st.error("Esta empresa no tiene un Google Docs asignado. Verifica que la columna Doc_ID de su fila en la hoja Empresas contenga el ID de su plantilla.")
                            st.stop()
                        st.session_state.empresa_seleccionada = empresa_seleccionada
                        st.session_state.tipo_empresa = "Nueva" if empresa_seleccionada == "Otra" else "Registrada"
                        st.session_state.step = "resumen"
                        st.rerun()
                    except Exception as exc:
                        st.error(f"No se pudo validar la empresa o localizar su plantilla: {exc}")
                        st.stop()

def render_generando():
    """Crea registro, copia la plantilla, la rellena y exporta el PDF; luego muestra la confirmación."""
    render_brand_header(6)
    with st.container(key="screen_processing"):
        st.markdown('<div class="processing-only-message">Estamos registrando tu solicitud</div>', unsafe_allow_html=True)

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
                "fondo": st.session_state.fondo,
                "Tipo_Empresa": st.session_state.get("tipo_empresa") or ("Nueva" if st.session_state.get("empresa_seleccionada") == "Otra" else "Registrada"),
                "motivo": st.session_state.proposito,
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
            st.error("La solicitud quedó guardada en Google Sheets, pero Google Drive no pudo copiar la plantilla. " + f"Detalle: {e}")
            st.info("La aplicación ya reintentó la conexión. Si el error continúa, revisaremos la conexión SSL de Streamlit y los permisos de la cuenta administradora en Google Drive. No cambies ni compartas tus credenciales.")
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
                "{{NOMBRE EMPRESA}}": str(st.session_state.empresa).upper(),
                "{{NIT_EMPRESA}}": str(st.session_state.nit).upper(),
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

    # La generación terminó correctamente. La confirmación se presenta en
    # una pantalla independiente para que el recorrido tenga un FINAL real.
    st.session_state.step = "final"
    st.rerun()


def render_final():
    """Confirmación final con número de solicitud."""
    render_brand_header(7)  # Los seis pasos aparecen completados.
    with st.container(key="screen_success"):
        numero_solicitud_html = html.escape(str(st.session_state.solicitud_id))
        st.markdown(f"""
        <section class="success-shell">
          <div class="success-confetti" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
          <div class="success-check">✓</div>
          <h1>¡Solicitud enviada!</h1>
          <p>Tu solicitud de retiro de cesantías quedó registrada correctamente.</p>
          <div class="success-delivery"><span class="success-mail-icon">✉</span><span>Recibirás la carta por correo electrónico y <span class="whatsapp-inline"><span class="whatsapp-icon" aria-hidden="true">☎</span> <strong>WhatsApp</strong></span> dentro de las próximas <strong>4 horas.</strong></span></div>
          <div class="success-number"><small>NÚMERO DE SOLICITUD</small><strong>{numero_solicitud_html}</strong></div>
          <div class="footer-brand">Cesantías al Instante... siempre contigo</div>
        </section>
        """, unsafe_allow_html=True)
        if st.button("⌂  Volver al inicio", key="finish_home", use_container_width=True):
            reiniciar_solicitud()
            st.session_state.step = "landing"
            st.rerun()

def render_whatsapp_entrega():
    render_brand_header()
    st.markdown('<div class="glass-container" style="text-align:center"><div class="screen-heading" style="justify-content:center"><div class="screen-icon">✉</div><div><h2>Tu carta está lista</h2><p>Vista previa de la entrega de tu solicitud.</p></div></div>', unsafe_allow_html=True)
    st.info(f"Hola {st.session_state.nombre}. La copia de tu plantilla quedó creada para la solicitud {st.session_state.solicitud_id}.")
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



# ---------- AJUSTE CONSOLIDADO: ESPACIADO Y CAMPOS DE PANTALLA 3 ----------
st.markdown(r"""
<style>
/* Reducir el azul vertical solo cuando está visible la pantalla 3.
   Los paddings izquierdo y derecho no se modifican. */
.main .block-container:has(.st-key-screen_data),
div[data-testid="stMainBlockContainer"]:has(.st-key-screen_data) {
  padding-top:.42rem!important;
  padding-bottom:.62rem!important;
}
.main .block-container:has(.st-key-screen_data) .brand-header {
  margin-top:0!important;
  margin-bottom:.38rem!important;
}
.main .block-container:has(.st-key-screen_data) .journey-wrap {
  margin-bottom:.38rem!important;
}
.st-key-screen_data {
  margin:.32rem auto .42rem!important;
  padding-top:1.05rem!important;
  padding-bottom:1.08rem!important;
  box-sizing:border-box!important;
}

/* Separación específica entre Departamento/Ciudad y los botones inferiores. */
.st-key-screen_data .st-key-data_navigation {
  display:block!important;
  width:100%!important;
  box-sizing:border-box!important;
  margin-top:1.08rem!important;
  padding-top:.52rem!important;
  border-top:1px solid #dce8f3!important;
}
.st-key-screen_data .st-key-data_navigation [data-testid="stHorizontalBlock"] {
  margin-top:.12rem!important;
}

@media(max-width:760px) {
  /* Menos espacio azul arriba y abajo; se preservan los márgenes laterales. */
  .main .block-container:has(.st-key-screen_data),
  div[data-testid="stMainBlockContainer"]:has(.st-key-screen_data) {
    padding-top:.28rem!important;
    padding-bottom:.42rem!important;
  }
  .main .block-container:has(.st-key-screen_data) .brand-header {
    margin-bottom:.28rem!important;
  }
  .main .block-container:has(.st-key-screen_data) .journey-wrap {
    margin-bottom:.28rem!important;
  }
  .st-key-screen_data {
    margin:.24rem auto .32rem!important;
    padding-top:.78rem!important;
    padding-bottom:.82rem!important;
  }

  /* Dos columnas reales: cada campo ocupa exactamente media fila disponible. */
  .st-key-screen_data [data-testid="stHorizontalBlock"] {
    display:flex!important;
    flex-direction:row!important;
    flex-wrap:nowrap!important;
    align-items:flex-end!important;
    gap:.36rem!important;
    width:100%!important;
    max-width:100%!important;
    min-width:0!important;
  }
  .st-key-screen_data [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex:1 1 calc((100% - .36rem)/2)!important;
    width:calc((100% - .36rem)/2)!important;
    min-width:0!important;
    max-width:calc((100% - .36rem)/2)!important;
    padding:0!important;
    box-sizing:border-box!important;
  }

  /* Campos compactos en alto y relleno, sin reducir la fuente de entrada por debajo de 16px. */
  .st-key-screen_data .field-label {
    display:flex!important;
    align-items:flex-start!important;
    gap:.22rem!important;
    margin:.22rem 0 .16rem!important;
    min-width:0!important;
    font-size:.69rem!important;
    line-height:1.18!important;
    overflow-wrap:anywhere!important;
  }
  .st-key-screen_data .field-label svg {
    width:14px!important;
    height:14px!important;
    flex:0 0 14px!important;
    margin-top:1px!important;
  }
  .st-key-screen_data [data-testid="stTextInput"] input {
    width:100%!important;
    min-width:0!important;
    height:39px!important;
    min-height:39px!important;
    padding:.32rem .38rem!important;
    font-size:16px!important;
    line-height:1.2!important;
    box-sizing:border-box!important;
  }
  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    width:100%!important;
    min-width:0!important;
    min-height:39px!important;
    height:39px!important;
    padding-left:.34rem!important;
    padding-right:.28rem!important;
    font-size:16px!important;
    box-sizing:border-box!important;
  }
  .st-key-screen_data [data-testid="stTextInput"] input::placeholder {
    font-size:.70rem!important;
    opacity:1!important;
  }
  .st-key-screen_data .section-label {
    margin:.52rem 0 .22rem!important;
    font-size:.9rem!important;
    line-height:1.2!important;
  }
  .st-key-screen_data .personal-tip {
    padding:.62rem .68rem!important;
    gap:.5rem!important;
    margin:.05rem 0 .62rem!important;
  }
  .st-key-screen_data .personal-tip-icon {
    width:36px!important;height:36px!important;flex-basis:36px!important;
  }
  .st-key-screen_data .personal-tip strong {font-size:.92rem!important}
  .st-key-screen_data .personal-tip p {font-size:.75rem!important;line-height:1.36!important}

  /* Separación visible entre la última fila de campos y Atrás/Siguiente. */
  .st-key-screen_data .st-key-data_navigation {
    margin-top:1.22rem!important;
    padding-top:.62rem!important;
  }
  .st-key-screen_data .st-key-data_navigation [data-testid="stHorizontalBlock"] {
    gap:.42rem!important;
    align-items:stretch!important;
  }
  .st-key-screen_data .st-key-data_navigation [data-testid="column"] {
    min-width:0!important;
    flex:1 1 0!important;
    width:auto!important;
    max-width:none!important;
  }
  .st-key-screen_data .st-key-data_navigation button {
    min-height:43px!important;
    padding:.52rem .38rem!important;
    font-size:.78rem!important;
    white-space:normal!important;
    line-height:1.2!important;
  }
}
@media(max-width:380px) {
  .st-key-screen_data [data-testid="stHorizontalBlock"] {gap:.30rem!important}
  .st-key-screen_data [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex-basis:calc((100% - .30rem)/2)!important;
    width:calc((100% - .30rem)/2)!important;
    max-width:calc((100% - .30rem)/2)!important;
  }
  .st-key-screen_data .field-label {font-size:.66rem!important}
  .st-key-screen_data .st-key-data_navigation button {font-size:.74rem!important}
}
</style>
""", unsafe_allow_html=True)




# ---------- CORRECCION REAL PARA TELEFONO: ESPACIO SUPERIOR Y ANCHO DE PANTALLA 3 ----------
# Este bloque va al final de los estilos existentes para que prevalezca sobre reglas antiguas.
st.markdown(r"""
<style>
@media (max-width: 760px) {
  /* Streamlit conserva una franja para el header aunque se oculte con visibility:hidden.
     En móvil se retira del flujo y se elimina el padding superior del contenedor real. */
  header,
  [data-testid="stHeader"],
  [data-testid="stAppHeader"],
  [data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
  }

  html, body, #root, .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  section.main {
    margin-top: 0 !important;
    padding-top: 0 !important;
  }

  .main .block-container,
  div[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
  }

  /* El espacio azul no debe quedar reservado por los wrappers del primer bloque. */
  .main .block-container:has(.st-key-landing_wrap),
  div[data-testid="stMainBlockContainer"]:has(.st-key-landing_wrap),
  .main .block-container:has(.st-key-screen_fund),
  div[data-testid="stMainBlockContainer"]:has(.st-key-screen_fund),
  .main .block-container:has(.st-key-screen_data),
  div[data-testid="stMainBlockContainer"]:has(.st-key-screen_data) {
    padding-top: 0 !important;
    margin-top: 0 !important;
  }

  .st-key-landing_wrap,
  .st-key-screen_fund,
  .st-key-screen_data {
    margin-top: 0 !important;
  }

  /* Pantalla 3: el panel y todos sus descendientes quedan dentro del ancho del móvil. */
  .st-key-screen_data {
    display: block !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    overflow-x: clip !important;
    padding-left: .58rem !important;
    padding-right: .58rem !important;
  }

  .st-key-screen_data *,
  .st-key-screen_data *::before,
  .st-key-screen_data *::after {
    box-sizing: border-box !important;
    min-width: 0 !important;
  }

  .st-key-screen_data [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    gap: .32rem !important;
    overflow: visible !important;
  }

  .st-key-screen_data [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex: 0 0 calc((100% - .32rem) / 2) !important;
    width: calc((100% - .32rem) / 2) !important;
    max-width: calc((100% - .32rem) / 2) !important;
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .st-key-screen_data [data-testid="stTextInput"],
  .st-key-screen_data [data-testid="stSelectbox"],
  .st-key-screen_data [data-testid="stTextInput"] > div,
  .st-key-screen_data [data-testid="stSelectbox"] > div,
  .st-key-screen_data [data-baseweb="select"],
  .st-key-screen_data [data-testid="stTextInput"] input,
  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    display: block !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
  }

  .st-key-screen_data [data-testid="stTextInput"] input {
    height: 38px !important;
    min-height: 38px !important;
    padding: .28rem .32rem !important;
    font-size: 16px !important;
  }

  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height: 38px !important;
    height: 38px !important;
    padding-left: .28rem !important;
    padding-right: .22rem !important;
    font-size: 16px !important;
  }

  .st-key-screen_data .field-label {
    font-size: .65rem !important;
    line-height: 1.15 !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
  }

  .st-key-screen_data .field-label svg {
    width: 12px !important;
    height: 12px !important;
    flex: 0 0 12px !important;
  }
}

@media (max-width: 390px) {
  .st-key-screen_data {
    padding-left: .48rem !important;
    padding-right: .48rem !important;
  }
  .st-key-screen_data [data-testid="stHorizontalBlock"] {
    gap: .24rem !important;
  }
  .st-key-screen_data [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex-basis: calc((100% - .24rem) / 2) !important;
    width: calc((100% - .24rem) / 2) !important;
    max-width: calc((100% - .24rem) / 2) !important;
  }
}
</style>
""", unsafe_allow_html=True)


# ---------- AJUSTE MOVIL: ELIMINAR FRANJA SUPERIOR Y MEJORAR CAMPOS ----------
st.markdown(r"""
<style>
@media (max-width: 760px) {
  /* Colapsar la zona superior que Streamlit reserva para sus barras. */
  :root {
    --header-height: 0px !important;
    --top-bar-height: 0px !important;
  }
  [data-testid="stHeader"],
  [data-testid="stAppHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  header {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
  }
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  section.main,
  section.main > div,
  .main .block-container,
  div[data-testid="stMainBlockContainer"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
  }
  .main .block-container:has(.st-key-landing_wrap),
  div[data-testid="stMainBlockContainer"]:has(.st-key-landing_wrap),
  .main .block-container:has(.st-key-screen_fund),
  div[data-testid="stMainBlockContainer"]:has(.st-key-screen_fund),
  .main .block-container:has(.st-key-screen_data),
  div[data-testid="stMainBlockContainer"]:has(.st-key-screen_data) {
    padding-top: 0 !important;
    margin-top: 0 !important;
  }
  .st-key-landing_wrap,
  .st-key-screen_fund,
  .st-key-screen_data {
    margin-top: 0 !important;
  }

  /* Pantalla 3: conservar las dimensiones ya aprobadas y aclarar los controles. */
  .st-key-screen_data [data-testid="stTextInput"] input,
  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #17345b !important;
    -webkit-text-fill-color: #17345b !important;
    border: 1.3px solid #b9d1e8 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 4px rgba(13, 54, 99, .07) !important;
    opacity: 1 !important;
  }
  .st-key-screen_data [data-testid="stTextInput"] input::placeholder {
    color: #7b8fa6 !important;
    -webkit-text-fill-color: #7b8fa6 !important;
    opacity: 1 !important;
  }
  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] *,
  .st-key-screen_data [data-testid="stSelectbox"] [data-baseweb="select"] span {
    color: #17345b !important;
    -webkit-text-fill-color: #17345b !important;
    opacity: 1 !important;
  }
  /* Etiquetas separadas de sus cajas; filas con aire entre sí. */
  .st-key-screen_data .field-label {
    color: #173d70 !important;
    margin: .34rem 0 .34rem !important;
    line-height: 1.24 !important;
    font-weight: 800 !important;
  }
  .st-key-screen_data [data-testid="stHorizontalBlock"] {
    column-gap: .62rem !important;
    row-gap: .48rem !important;
    margin-bottom: .32rem !important;
  }
  .st-key-screen_data [data-testid="stTextInput"],
  .st-key-screen_data [data-testid="stSelectbox"] {
    margin-bottom: .22rem !important;
  }
  .st-key-screen_data .section-label {
    margin-top: .72rem !important;
    margin-bottom: .38rem !important;
    color: #12396e !important;
  }
}
</style>
""", unsafe_allow_html=True)


# ---------- POSICION SUPERIOR MOVIL: OVERRIDE UNICO ----------
# Elimina el espacio reservado por los wrappers de Streamlit sin cambiar
# las dimensiones aprobadas de los campos ni el diseño de escritorio.
st.markdown(r"""
<style>
@media screen and (max-width: 760px) {
  :root {
    --header-height: 0px !important;
    --top-bar-height: 0px !important;
    --block-container-vertical-padding: 0px !important;
  }

  /* Retirar completamente los encabezados superiores del flujo. */
  header,
  [data-testid="stHeader"],
  [data-testid="stAppHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
  }

  /* Los contenedores raíz de Streamlit deben comenzar arriba, nunca centrados. */
  html, body, #root, .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  section.main {
    margin-top: 0 !important;
    padding-top: 0 !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
  }

  [data-testid="stAppViewContainer"] {
    display: block !important;
    min-height: 100dvh !important;
    height: auto !important;
  }

  section.main,
  section.main > div,
  section.main > div > div,
  .main .block-container,
  div[data-testid="stMainBlockContainer"],
  div[data-testid="stAppViewBlockContainer"] {
    margin-block-start: 0 !important;
    padding-block-start: 0 !important;
    padding-top: 0 !important;
    align-self: flex-start !important;
    justify-self: start !important;
    transform: none !important;
  }

  .main .block-container:has(.st-key-landing_wrap),
  div[data-testid="stMainBlockContainer"]:has(.st-key-landing_wrap),
  div[data-testid="stAppViewBlockContainer"]:has(.st-key-landing_wrap),
  .main .block-container:has(.st-key-screen_fund),
  div[data-testid="stMainBlockContainer"]:has(.st-key-screen_fund),
  div[data-testid="stAppViewBlockContainer"]:has(.st-key-screen_fund),
  .main .block-container:has(.st-key-screen_data),
  div[data-testid="stMainBlockContainer"]:has(.st-key-screen_data),
  div[data-testid="stAppViewBlockContainer"]:has(.st-key-screen_data) {
    margin-block-start: 0 !important;
    padding-block-start: 0 !important;
    padding-top: 0 !important;
  }

  .main .block-container > [data-testid="stVerticalBlock"],
  div[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
  div[data-testid="stAppViewBlockContainer"] > [data-testid="stVerticalBlock"] {
    justify-content: flex-start !important;
    align-content: flex-start !important;
    align-items: stretch !important;
    margin-block-start: 0 !important;
    padding-block-start: 0 !important;
  }

  .st-key-landing_wrap,
  .st-key-screen_fund,
  .st-key-screen_data {
    margin-block-start: 0 !important;
  }

  .st-key-landing_wrap { padding-block-start: .12rem !important; }
  .st-key-screen_fund .brand-header,
  .st-key-screen_data .brand-header,
  .main .block-container:has(.st-key-screen_fund) .brand-header,
  .main .block-container:has(.st-key-screen_data) .brand-header {
    margin-block-start: 0 !important;
  }
}
</style>
""", unsafe_allow_html=True)


# ---------- AJUSTES SOLICITADOS: MENUS MOVILES Y ESPACIADO PANTALLA 3 ----------
st.markdown(r"""
<style>
/* Pantalla 3: un poco más de aire entre cada encabezado y su primer campo.
   No cambia el tamaño, color ni separación interna de las cajas aprobadas. */
.st-key-screen_data .section-label {
  margin-bottom: .82rem !important;
}

/* Pantalla 4: los menús de BaseWeb deben permanecer dentro del ancho visible
   del teléfono y por encima de las tarjetas/contenedores de la pantalla. */
@media (max-width: 760px) {
  body [data-baseweb="popover"] {
    z-index: 999999 !important;
    max-width: calc(100vw - 20px) !important;
    box-sizing: border-box !important;
  }
  body [data-baseweb="popover"] > div,
  body [data-baseweb="menu"],
  body [role="listbox"] {
    max-width: calc(100vw - 20px) !important;
    max-height: min(48vh, 340px) !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    box-sizing: border-box !important;
  }
  body [data-baseweb="popover"] [role="option"] {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
  }
  /* En teléfono, los selectores de empresa se apilan: nunca quedan uno al lado
     del otro ni fuerzan el ancho de la pantalla. En PC se conserva la fila original. */
  .st-key-screen_company .st-key-company_selectors,
  .st-key-screen_company .st-key-company_selectors [data-testid="stSelectbox"],
  .st-key-screen_company .st-key-company_manual_fields [data-testid="stTextInput"] {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
  }
  .st-key-screen_company .st-key-company_selectors [data-testid="stHorizontalBlock"],
  .st-key-screen_company .st-key-company_manual_fields [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    gap: .72rem !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
  }
  .st-key-screen_company .st-key-company_selectors [data-testid="column"],
  .st-key-screen_company .st-key-company_manual_fields [data-testid="column"] {
    flex: 1 1 100% !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
  }

  /* Menús desplegables claros en TODAS las pantallas del teléfono.
     El panel, las opciones, el buscador y el texto usan fondo blanco y tinta oscura. */
  body [data-baseweb="popover"],
  body [data-baseweb="popover"] > div,
  body [data-baseweb="menu"],
  body [data-testid="stSelectboxVirtualDropdown"],
  body ul[role="listbox"] {
    background: #ffffff !important;
    color: #26384d !important;
    border: 1px solid #d5e2ee !important;
    box-shadow: 0 10px 28px rgba(12, 37, 66, .18) !important;
  }
  body [data-baseweb="popover"] *,
  body [data-baseweb="menu"] *,
  body [data-testid="stSelectboxVirtualDropdown"] *,
  body [role="listbox"] * {
    color: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
  }
  body [role="option"],
  body [data-baseweb="menu"] li {
    background: #ffffff !important;
    color: #26384d !important;
  }
  body [role="option"]:hover,
  body [role="option"][aria-selected="true"],
  body [data-baseweb="menu"] li:hover {
    background: #eaf4ff !important;
    color: #12396e !important;
  }
  body [data-baseweb="popover"] input {
    background: #ffffff !important;
    color: #26384d !important;
    border-color: #cbd9e7 !important;
    -webkit-text-fill-color: #26384d !important;
  }

  /* Refuerzo para los nodos internos que BaseWeb pinta con el tema oscuro.
     Se aplica solo al menú emergente en móvil; no altera los selectores cerrados. */
  body [data-baseweb="popover"] [data-baseweb="menu"],
  body [data-baseweb="popover"] [data-baseweb="menu"] > div,
  body [data-baseweb="popover"] [role="listbox"],
  body [data-baseweb="popover"] [role="listbox"] > div,
  body [data-baseweb="popover"] ul,
  body [data-baseweb="popover"] li,
  body [data-baseweb="popover"] [role="option"],
  body [data-testid="stSelectboxVirtualDropdown"],
  body [data-testid="stSelectboxVirtualDropdown"] > div,
  body [data-testid="stSelectboxVirtualDropdown"] ul,
  body [data-testid="stSelectboxVirtualDropdown"] li {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
  }
  body [data-baseweb="popover"] [role="option"]:hover,
  body [data-baseweb="popover"] [role="option"][aria-selected="true"],
  body [data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
  body [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"] {
    background: #eaf4ff !important;
    background-color: #eaf4ff !important;
    color: #12396e !important;
    -webkit-text-fill-color: #12396e !important;
  }

  /* Último refuerzo: el selectbox de Departamento usa el popover de BaseWeb.
     Se fuerza el fondo de todos los niveles del menú, no solo del contenedor externo. */
  body [data-baseweb="layer"] [data-baseweb="popover"],
  body [data-baseweb="layer"] [data-baseweb="popover"] > *,
  body [data-baseweb="layer"] [data-baseweb="popover"] [role="listbox"],
  body [data-baseweb="layer"] [data-baseweb="popover"] [role="option"],
  body [data-baseweb="popover"] [data-baseweb="select"],
  body [data-baseweb="popover"] [data-baseweb="select"] > * {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
  }
  body [data-baseweb="layer"] [data-baseweb="popover"] [role="option"]:hover,
  body [data-baseweb="layer"] [data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background: #eaf4ff !important;
    background-color: #eaf4ff !important;
    color: #12396e !important;
    -webkit-text-fill-color: #12396e !important;
  }
}


/* El control cerrado también estaba heredando el tema oscuro.
   Afecta Departamento, Empresa y NIT únicamente en móvil. */
@media (max-width: 760px) {
  body [data-testid="stSelectbox"] [data-baseweb="select"] > div,
  body [data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #26384d !important;
    border-color: #cbd9e7 !important;
    -webkit-text-fill-color: #26384d !important;
  }
  body [data-testid="stSelectbox"] [data-baseweb="select"] *,
  body [data-testid="stSelectbox"] [data-baseweb="select"] svg {
    color: #26384d !important;
    fill: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
  }
  body [data-testid="stSelectbox"] [data-baseweb="select"] input {
    background: #ffffff !important;
    color: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
  }
}

/* Refuerzo final para los tres selectores móviles: Departamento, Empresa y NIT.
   Los menús de Streamlit se montan en una capa/portal separado del formulario. */
@media (max-width: 760px) {
  body [data-baseweb="layer"] [data-baseweb="menu"],
  body [data-baseweb="layer"] [data-baseweb="menu"] *,
  body [data-baseweb="layer"] [role="listbox"],
  body [data-baseweb="layer"] [role="listbox"] *,
  body [data-baseweb="layer"] [role="option"],
  body [data-baseweb="popover"] [data-baseweb="menu"],
  body [data-baseweb="popover"] [data-baseweb="menu"] *,
  body [data-baseweb="popover"] [role="listbox"],
  body [data-baseweb="popover"] [role="listbox"] *,
  body [data-baseweb="popover"] [role="option"] {
    background-color: #ffffff !important;
    color: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
  }

  body [data-baseweb="layer"] [role="option"]:hover,
  body [data-baseweb="layer"] [role="option"][aria-selected="true"],
  body [data-baseweb="popover"] [role="option"]:hover,
  body [data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background-color: #eaf4ff !important;
    color: #12396e !important;
    -webkit-text-fill-color: #12396e !important;
  }
}


/* Sobrescritura de alta especificidad para el fondo oscuro del selectbox.
   Limitada a los tres widgets en móvil; conserva medidas y disposición. */
@media screen and (max-width: 760px) {
  .st-key-screen_data [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
  .st-key-screen_data [data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
  .st-key-screen_data [data-testid="stSelectbox"] div[data-baseweb="select"] [role="combobox"],
  .st-key-screen_company [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
  .st-key-screen_company [data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
  .st-key-screen_company [data-testid="stSelectbox"] div[data-baseweb="select"] [role="combobox"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    background-image: none !important;
    color: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
    border-color: #cbd9e7 !important;
    box-shadow: none !important;
  }
  .st-key-screen_data [data-testid="stSelectbox"] div[data-baseweb="select"] *,
  .st-key-screen_company [data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: #26384d !important;
    -webkit-text-fill-color: #26384d !important;
  }
  .st-key-screen_data [data-testid="stSelectbox"] div[data-baseweb="select"] svg,
  .st-key-screen_company [data-testid="stSelectbox"] div[data-baseweb="select"] svg {
    fill: #26384d !important;
    color: #26384d !important;
  }
}

</style>
""", unsafe_allow_html=True)

# Espacio adicional entre el contenido y los botones en las pantallas 5 y 6.
st.markdown(r"""
<style>
.st-key-screen_summary [data-testid="stHorizontalBlock"]:has(.st-key-summary_back),
.st-key-screen_mission [data-testid="stHorizontalBlock"]:has(.st-key-mission_back) {
  margin-top:1.2rem!important;
  padding-top:.4rem!important;
  gap:.85rem!important;
}
.st-key-screen_processing .processing-only-message {
  text-align:center!important;color:#082e6b!important;
  font-size:clamp(1.15rem,2.5vw,1.55rem)!important;
  line-height:1.4!important;font-weight:900!important;
  padding:1.5rem .5rem!important;
}
.st-key-screen_success .whatsapp-inline {
  display:inline-flex;align-items:center;gap:.22rem;white-space:nowrap;color:#087d42!important;
}
.st-key-screen_success .whatsapp-icon {
  display:inline-flex;align-items:center;justify-content:center;
  width:1.25rem;height:1.25rem;border-radius:50%;
  background:#20c765;color:#fff;font-size:.82rem;font-weight:900;
}
@media(max-width:760px){
  .st-key-screen_summary [data-testid="stHorizontalBlock"]:has(.st-key-summary_back),
  .st-key-screen_mission [data-testid="stHorizontalBlock"]:has(.st-key-mission_back) {
    margin-top:1.4rem!important;padding-top:.5rem!important;gap:.7rem!important;
  }
}
</style>
""", unsafe_allow_html=True)


# ---------- MAIN ----------
def main():
    # Google vuelve a la URL principal con code/state después de autorizar.
    if st.query_params.get("code") or st.query_params.get("error"):
        procesar_callback_oauth()

    # El refresh token se muestra en una pantalla separada y protegida.
    if st.session_state.get("oauth_pending_refresh_token"):
        render_token_oauth()
        return

    # Configuración administrativa privada de Google Drive.
    if st.query_params.get("configurar_drive") == "1":
        render_configuracion_drive()
        return

    # Migra sesiones que hubieran quedado en los nombres del flujo anterior.
    migracion = {
        "pregunta1": "seleccionar_fondo",
        # En el flujo anterior, pregunta2 era la selección del fondo.
        # Si una sesión antigua quedó allí, la siguiente pantalla correcta es Datos.
        "pregunta2": "datos_personales",
        "verificar_saldo": "datos_personales",
        "monto_exacto": "datos_personales",
        "resultados": "resumen",
    }
    paso_actual = st.session_state.get("step", "landing")
    if paso_actual in migracion:
        st.session_state.step = migracion[paso_actual]

    rutas = {
        "landing": render_landing,
        "seleccionar_fondo": render_seleccionar_fondo,
        "datos_personales": render_datos_personales,
        "resumen": render_resumen,
        "mision": render_mision,
        "empresa": render_empresa,
        "generando": render_generando,
        "final": render_final,
    }
    rutas.get(st.session_state.get("step", "landing"), render_landing)()


if __name__ == "__main__":
    main()

st.markdown("""<style>

/* AJUSTE DEFINITIVO: reservar una franja independiente para el botón de portada. */
@media (min-width:761px) {
  .st-key-landing_wrap .hero-copy {padding-bottom:6.2rem!important;}
  .st-key-landing_start {margin-top:-72px!important;}
}
@media (max-width:760px) {
  .st-key-landing_wrap .hero-copy {padding-bottom:6.4rem!important;}
  .st-key-landing_start {bottom:.42rem!important;left:.52rem!important;top:auto!important;}
}
</style>""", unsafe_allow_html=True)


# ---------- CORRECCION PORTADA: CTA DEBAJO DEL PANEL, SIN SOLAPAMIENTOS ----------
st.markdown(r"""
<style>
/* El botón queda en el flujo normal de Streamlit, después del panel visual. */
.st-key-landing_start {
  position:relative!important;
  inset:auto!important;
  display:block!important;
  width:max-content!important;
  max-width:calc(100% - 2rem)!important;
  margin:14px 0 22px 1.6rem!important;
  z-index:20!important;
}
.st-key-landing_start button {
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:auto!important;
  min-width:205px!important;
  min-height:49px!important;
  padding:.75rem 1.65rem!important;
}
@media(max-width:760px) {
  .st-key-landing_start {
    position:relative!important;
    inset:auto!important;
    width:calc(100% - 1.04rem)!important;
    max-width:190px!important;
    margin:12px 0 20px .52rem!important;
  }
  .st-key-landing_start button {
    width:100%!important;
    min-width:0!important;
    min-height:44px!important;
    padding:.5rem .35rem!important;
    font-size:clamp(.72rem,2.8vw,.84rem)!important;
  }
}
</style>
""", unsafe_allow_html=True)
