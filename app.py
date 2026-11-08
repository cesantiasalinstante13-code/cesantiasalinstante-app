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
    """Marca y progreso del recorrido definitivo de seis pantallas."""
    logo_uri = imagen_data_uri(obtener_logo_app_path())
    logo_html = f'<img src="{logo_uri}" alt="Cesantías al Instante">' if logo_uri else '<strong>Cesantías al Instante</strong>'
    st.markdown(
        '<div class="brand-header"><div class="brand-logo-wrap">' + logo_html + '</div>'
        '<div class="brand-trust"><span>✓</span> Trámite fácil y seguro</div></div>',
        unsafe_allow_html=True
    )
    etiquetas = ["Inicio", "Fondo", "Datos", "Resumen", "Misión", "Empresa"]
    pasos = []
    for n, etiqueta in enumerate(etiquetas, 1):
        clase = "active" if n == etapa else ("done" if n < etapa else "")
        simbolo = "✓" if n < etapa else str(n)
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
        "solicitud_id", "documento_rellenado", "pdf_id", "pdf_url", "pdf_generado",
    ]
    for key in llaves:
        st.session_state[key] = ""
    widgets = [
        "ciudad_widget", "departamento_widget", "empresa_manual_widget", "nit_manual_widget",
        "empresa_widget", "saldo_widget", "monto_raw_widget", "telefono_widget",
        "nombre_widget", "cedula_widget", "email_widget",
    ]
    for key in widgets:
        st.session_state[key] = ""


def render_landing():
    """Bienvenida con CTA Streamlit dentro del mismo contenedor visual."""
    logo_uri = imagen_data_uri(obtener_logo_app_path())
    hero_uri = imagen_data_uri(obtener_imagen_hero_path())
    logo_html = f'<img src="{logo_uri}" alt="Logo Cesantías al Instante">' if logo_uri else '<strong>Cesantías al Instante</strong>'
    hero_html = f'<img src="{hero_uri}" alt="Asesora de Cesantías al Instante">' if hero_uri else ''
    with st.container(key="landing_wrap"):
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
    render_brand_header(2)
    with st.container(key="screen_fund"): 
        render_screen_heading("fund", "Selecciona tu fondo de cesantías", "Elige la entidad donde tienes tus cesantías para preparar tu solicitud.")
        fondos = [
            {"nombre": "Porvenir", "logo": "Porvenir_logo.png", "icono": "fund"},
            {"nombre": "Colfondos", "logo": "Colfondos_logo.png", "icono": "building"},
            {"nombre": "Protección", "logo": "Proteccion_logo.png", "icono": "shield"},
            {"nombre": "FNA", "logo": "FNA_logo.png", "icono": "building"},
            {"nombre": "Otro", "logo": None, "icono": "wallet"},
        ]
        for inicio in range(0, len(fondos), 2):
            cols = st.columns(2, gap="medium")
            for col, fondo in zip(cols, fondos[inicio:inicio + 2]):
                with col:
                    with st.container(border=True):
                        logo_path = buscar_logo_fondo(fondo["logo"]) if fondo["logo"] else None
                        if logo_path:
                            with open(logo_path, "rb") as archivo_logo:
                                logo_b64 = base64.b64encode(archivo_logo.read()).decode("ascii")
                            mime = mimetypes.guess_type(logo_path)[0] or "image/png"
                            st.markdown(f'<div class="fund-logo-box"><img src="data:{mime};base64,{logo_b64}" alt="Logo de {html.escape(fondo["nombre"])}"></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="fund-logo-box fund-fallback">{icon_svg(fondo["icono"])}</div>', unsafe_allow_html=True)
                        marcado = st.session_state.get("fondo") == fondo["nombre"]
                        st.markdown(f'<div class="fund-name">{html.escape(fondo["nombre"])}</div>', unsafe_allow_html=True)
                        if st.button("✓ Seleccionado" if marcado else "Seleccionar fondo", key=f"fund_{fondo['nombre'].lower().replace('ó','o')}", use_container_width=True):
                            st.session_state.fondo = fondo["nombre"]
                            st.session_state.step = "datos_personales"
                            st.rerun()
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
    render_brand_header(3)
    with st.container(key="screen_data"): 
        render_screen_heading("user", "Datos personales", "Completa tu información para preparar correctamente la carta de retiro.")
        numeros = {
            "Porvenir": "01 8000 111 222", "Colfondos": "01 8000 123 456",
            "Protección": "01 8000 789 012", "FNA": "01 8000 456 789", "Otro": "01 8000 000 000"
        }
        numero = numeros.get(st.session_state.get("fondo", "Otro"), "01 8000 000 000")
        st.markdown(
            f'<div class="personal-tip"><div class="personal-tip-icon">{icon_svg("phone")}</div>'
            f'<div><strong>{html.escape(numero)}</strong><p>Consulta tu saldo en los canales oficiales de tu fondo. Marca, sigue las indicaciones y escribe abajo el saldo que te informen.</p></div></div>',
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
        for valor, etiqueta in ((saldo_raw, "Saldo"), (monto_raw, "Monto")):
            limpio = re.sub(r"\D", "", str(valor))
            if limpio:
                st.caption(f"{etiqueta}: ${int(limpio):,}".replace(",", "."))

        st.markdown(f'<div class="section-label">{icon_svg("user")} Tus datos de contacto</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="large")
        with c1:
            render_field_label("user", "Nombre completo")
            nombre = st.text_input("Nombre completo", label_visibility="collapsed", placeholder="Como aparece en tu cédula", key="nombre_widget")
            render_field_label("file", "Cédula")
            cedula = st.text_input("Cédula", label_visibility="collapsed", placeholder="Escribe solo números", key="cedula_widget", on_change=limpiar_cedula_widget)
            render_field_label("phone", "Teléfono / WhatsApp")
            telefono = st.text_input("Teléfono / WhatsApp", label_visibility="collapsed", placeholder="Ej. 3001234567", key="telefono_widget", on_change=limpiar_telefono_widget)
        with c2:
            render_field_label("mail", "Correo electrónico")
            email_val = st.text_input("Correo electrónico", label_visibility="collapsed", placeholder="nombre@correo.com", key="email_widget")
            departamentos = [
                "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá, D.C.", "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo", "Quindío", "Risaralda", "San Andrés y Providencia", "Santander", "Sucre", "Tolima", "Valle del Cauca", "Vaupés", "Vichada"
            ]
            render_field_label("pin", "Departamento")
            departamento = st.selectbox("Departamento", [""] + departamentos, label_visibility="collapsed", key="departamento_widget", placeholder="Selecciona tu departamento")
            render_field_label("pin", "Ciudad")
            ciudad = st.text_input("Ciudad", label_visibility="collapsed", placeholder="Escribe tu ciudad", key="ciudad_widget")

        c1, c2 = st.columns([1, 1.8])
        with c1:
            if st.button("← Atrás", key="data_back", use_container_width=True):
                st.session_state.step = "seleccionar_fondo"
                st.rerun()
        with c2:
            if st.button("Continuar al resumen  →", key="data_continue", use_container_width=True):
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
                st.session_state.step = "resumen"
                st.rerun()


def render_resumen():
    render_brand_header(4)
    with st.container(key="screen_summary"): 
        render_screen_heading("file", "Resumen de tu solicitud", "Revisa que la información esté correcta antes de continuar.")
        with st.container(key="summary_panel"): 
            st.markdown('<div class="summary-check">✓</div>', unsafe_allow_html=True)
            filas = [
                ("Fondo de cesantías", st.session_state.get("fondo", "")),
                ("Nombre completo", st.session_state.get("nombre", "")),
                ("Cédula", st.session_state.get("cedula", "")),
                ("Teléfono / WhatsApp", st.session_state.get("telefono", "")),
                ("Correo electrónico", st.session_state.get("email", "")),
                ("Departamento", st.session_state.get("departamento", "")),
                ("Ciudad", st.session_state.get("ciudad", "")),
                ("Saldo disponible", st.session_state.get("saldo_verificado", "")),
                ("Monto solicitado", "$" + str(st.session_state.get("monto", ""))),
            ]
            cols = st.columns(2, gap="medium")
            for i, (etiqueta, valor) in enumerate(filas):
                with cols[i % 2]:
                    st.markdown(
                        f'<div class="summary-item"><small>{html.escape(etiqueta)}</small><strong>{html.escape(str(valor))}</strong></div>',
                        unsafe_allow_html=True
                    )
        st.info("En la siguiente pantalla te explicaremos quiénes somos y cómo acompañamos tu solicitud.")
        c1, c2 = st.columns([1, 1.8])
        with c1:
            if st.button("← Corregir datos", key="summary_back", use_container_width=True):
                st.session_state.step = "datos_personales"
                st.rerun()
        with c2:
            if st.button("Continuar  →", key="summary_continue", use_container_width=True):
                st.session_state.step = "mision"
                st.rerun()


def render_mision():
    render_brand_header(5)
    with st.container(key="screen_mission"): 
        render_screen_heading("mission", "Nuestra misión", "Queremos que conozcas cómo funciona nuestro acompañamiento.")
        st.markdown("""
        <section class="mission-hero">
          <h3>Hacemos más sencillo tu proceso de retiro de cesantías</h3>
          <p>En Cesantías al Instante te acompañamos en la organización de la información y en la preparación de la carta correspondiente, utilizando los datos y la plantilla asociados a tu empresa.</p>
        </section>
        """, unsafe_allow_html=True)
        cols = st.columns(3, gap="medium")
        cards = [
            (icon_svg("shield"), "Acompañamiento", "Te guiamos paso a paso para reunir la información necesaria de tu solicitud."),
            (icon_svg("file"), "Gestión organizada", "Registramos la solicitud y preparamos el documento con la plantilla correspondiente."),
            (icon_svg("check"), "Claridad y seguridad", "Puedes revisar tus datos antes de confirmar y mantener un registro de tu trámite."),
        ]
        for col, (simbolo, titulo, texto) in zip(cols, cards):
            with col:
                st.markdown(f'<div class="mission-card"><div class="mission-symbol">{simbolo}</div><strong>{titulo}</strong><p>{texto}</p></div>', unsafe_allow_html=True)
        st.markdown('<p style="color:#58708b;font-size:.84rem;margin:1rem 0 0">La preparación de la carta depende de que los datos sean correctos y de que exista una plantilla válida asociada a la empresa seleccionada.</p>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.8])
        with c1:
            if st.button("← Atrás", key="mission_back", use_container_width=True):
                st.session_state.step = "resumen"
                st.rerun()
        with c2:
            if st.button("Continuar a mi empresa  →", key="mission_continue", use_container_width=True):
                st.session_state.step = "empresa"
                st.rerun()


def render_empresa():
    render_brand_header(6)
    with st.container(key="screen_company"): 
        render_screen_heading("building", "Empresa donde trabajas", "Selecciona tu empresa para localizar el NIT y la plantilla de tu carta.")
        st.markdown('<div class="personal-tip"><div class="personal-tip-icon">' + icon_svg("building") + '</div><div><strong>Buscamos tu empresa en nuestro registro</strong><p>La selección permite asociar automáticamente los datos y la plantilla disponibles en nuestra base de empresas.</p></div></div>', unsafe_allow_html=True)
        try:
            df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
            if "Nombre_Empresa" not in df_empresas.columns:
                raise ValueError("La hoja Empresas debe tener la columna Nombre_Empresa.")
            lista_empresas = df_empresas["Nombre_Empresa"].dropna().astype(str).str.strip().tolist()
            lista_empresas = list(dict.fromkeys([x for x in lista_empresas if x and x.casefold() != "otra"]))
        except Exception as exc:
            st.error(f"No fue posible cargar la lista de empresas desde Google Sheets: {exc}")
            st.stop()

        render_field_label("building", "Empresa donde trabajas")
        empresa_seleccionada = st.selectbox(
            "Selecciona tu empresa", [""] + lista_empresas + ["Otra"], label_visibility="collapsed", key="empresa_widget",
            placeholder="Busca o selecciona tu empresa"
        )
        empresa_manual = ""
        nit_manual = ""
        if empresa_seleccionada == "Otra":
            st.markdown('<div class="section-label">' + icon_svg("building") + ' Información de tu empresa</div>', unsafe_allow_html=True)
            mc1, mc2 = st.columns(2, gap="medium")
            with mc1:
                render_field_label("building", "Nombre de la empresa")
                empresa_manual = st.text_input("Nombre de la empresa", label_visibility="collapsed", placeholder="Razón social", key="empresa_manual_widget")
            with mc2:
                render_field_label("file", "NIT de la empresa")
                nit_manual = st.text_input("NIT de la empresa", label_visibility="collapsed", placeholder="Número de NIT", key="nit_manual_widget")
            st.info("Para la opción “Otra”, la hoja Empresas debe tener una fila con Nombre_Empresa = Otra y el Doc_ID de la plantilla general.")
        elif empresa_seleccionada:
            coincidencias = df_empresas[df_empresas["Nombre_Empresa"].astype(str).str.strip() == empresa_seleccionada]
            nit_visible = ""
            if not coincidencias.empty and "NIT" in df_empresas.columns:
                valor_nit = coincidencias.iloc[0].get("NIT", "")
                nit_visible = "" if pd.isna(valor_nit) else str(valor_nit).strip()
            st.markdown(f'<div class="summary-item"><small>NIT registrado</small><strong>{html.escape(nit_visible or "No aparece un NIT en la hoja Empresas")}</strong></div>', unsafe_allow_html=True)

        c1, c2 = st.columns([1, 1.8])
        with c1:
            if st.button("← Atrás", key="company_back", use_container_width=True):
                st.session_state.step = "mision"
                st.rerun()
        with c2:
            if st.button("Enviar solicitud  ✓", key="company_submit", use_container_width=True):
                if not empresa_seleccionada:
                    st.error("Selecciona la empresa donde trabajas.")
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
                        st.error("Esta empresa no tiene una plantilla asignada. Verifica la columna Doc_ID de la hoja Empresas.")
                        st.stop()
                    st.session_state.empresa_seleccionada = empresa_seleccionada
                    st.session_state.step = "generando"
                    st.rerun()
                except Exception as exc:
                    st.error(f"No se pudo validar la empresa o localizar su plantilla: {exc}")
                    st.stop()

def render_generando():
    """Crea registro, copia la plantilla, la rellena y exporta el PDF; luego muestra la confirmación."""
    render_brand_header(6)
    with st.container(key="screen_processing"): 
        render_screen_heading("file", "Estamos preparando tu carta", "Estamos registrando la solicitud y generando tu documento.")

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

    numero_solicitud_html = html.escape(str(st.session_state.solicitud_id))
    st.markdown(f"""
    <section class="success-shell">
      <div class="success-check">✓</div>
      <h1>¡Tu solicitud fue enviada!</h1>
      <p>Registramos correctamente tu solicitud de retiro de cesantías.</p>
      <div class="success-delivery">✉ &nbsp; Nuestro equipo gestionará la entrega de tu carta al correo electrónico y al WhatsApp que registraste, dentro de las próximas 24 horas.</div>
      <p><strong>Número de solicitud:</strong> {numero_solicitud_html}</p>
      <div class="footer-brand">Cesantías al Instante... siempre contigo</div>
    </section>
    """, unsafe_allow_html=True)
    if st.session_state.pdf_url:
        st.link_button("Abrir o descargar mi carta (PDF)", st.session_state.pdf_url, use_container_width=True)
    if st.session_state.url_copia:
        st.link_button("Abrir documento editable", st.session_state.url_copia, use_container_width=True)
    if st.button("Volver al inicio", key="finish_home", use_container_width=True):
        st.session_state.step = 'landing'
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
    }
    rutas.get(st.session_state.get("step", "landing"), render_landing)()


if __name__ == "__main__":
    main()
