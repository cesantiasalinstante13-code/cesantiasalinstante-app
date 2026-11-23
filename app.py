import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import base64
import mimetypes
import html
import re
import unicodedata
import hmac
import hashlib
import secrets
import time
import json
import requests
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from threading import Lock
from io import BytesIO
from streamlit_gsheets import GSheetsConnection
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# Identificador de compilación para comprobar qué archivo ejecuta Streamlit.
APP_BUILD_ID = "CESANTIAS_FORMATO_PLANTILLA_6.2_2026-11-22"

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
    'pdf_id', 'pdf_url', 'pdf_generado', 'whatsapp_autorizado',
    'whatsapp_confirmacion_estado', 'whatsapp_documento_estado',
    'busqueda_otra_completada', 'logo_empresa_insertado', 'logo_marcador_procesado', 'estado_logo_empresa', 'estado_empresa_web', 'diagnostico_logo_empresa', 'logo_empresa_en_template'
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



def obtener_config_whatsapp():
    """Lee la configuración privada de WhatsApp desde Streamlit Secrets."""
    try:
        return dict(st.secrets["whatsapp"])
    except Exception as exc:
        raise RuntimeError(
            "Falta el bloque [whatsapp] en Streamlit Secrets. "
            "Agrega allí access_token, phone_number_id, api_version y test_recipient."
        ) from exc


def enviar_mensaje_prueba_meta():
    """Envía el template oficial hello_world solo al destinatario de prueba autorizado."""
    datos = obtener_config_whatsapp()
    token = str(datos.get("access_token", "")).strip()
    phone_number_id = str(datos.get("phone_number_id", "")).strip()
    destinatario = re.sub(r"\D", "", str(datos.get("test_recipient", "")))
    version = str(datos.get("api_version", "v27.0")).strip()
    if not version.startswith("v"):
        version = f"v{version}"

    faltantes = []
    if not token:
        faltantes.append("access_token")
    if not phone_number_id:
        faltantes.append("phone_number_id")
    if not destinatario:
        faltantes.append("test_recipient")
    if faltantes:
        raise RuntimeError(
            "Faltan estos valores en [whatsapp] de Streamlit Secrets: "
            + ", ".join(faltantes)
        )

    url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {"code": "en_US"}
        }
    }

    try:
        respuesta = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"No se pudo conectar con Meta para enviar la prueba: {exc}"
        ) from exc

    try:
        resultado = respuesta.json()
    except ValueError:
        resultado = {}

    if not respuesta.ok:
        error = resultado.get("error", {}) if isinstance(resultado, dict) else {}
        codigo = error.get("code", "")
        mensaje = error.get("message", "Meta no aceptó el mensaje.")
        detalle = f"HTTP {respuesta.status_code}"
        if codigo:
            detalle += f" · código Meta {codigo}"
        raise RuntimeError(f"{detalle}: {mensaje}")

    mensajes = resultado.get("messages", []) if isinstance(resultado, dict) else []
    if not mensajes or not mensajes[0].get("id"):
        raise RuntimeError(
            "Meta respondió sin un identificador de mensaje. Revisa la respuesta desde el panel de Meta."
        )

    return {
        "message_id": mensajes[0]["id"],
        "recipient": destinatario,
        "status": mensajes[0].get("message_status", "accepted")
    }


def _whatsapp_api_base(datos):
    version = str(datos.get("api_version", "v27.0")).strip()
    if not version.startswith("v"):
        version = f"v{version}"
    phone_number_id = str(datos.get("phone_number_id", "")).strip()
    token = str(datos.get("access_token", "")).strip()
    if not token or not phone_number_id:
        raise RuntimeError("Falta access_token o phone_number_id en [whatsapp] de Streamlit Secrets.")
    return f"https://graph.facebook.com/{version}/{phone_number_id}", {
        "Authorization": f"Bearer {token}"
    }


def enviar_template_whatsapp(destinatario, nombre_template, parametros_cuerpo, documento_media_id=None):
    """Envía una plantilla aprobada. Para la plantilla PDF, el encabezado debe ser Documento."""
    datos = obtener_config_whatsapp()
    base, headers = _whatsapp_api_base(datos)
    codigo_pais = re.sub(r"\D", "", str(datos.get("country_code", "57"))) or "57"
    numero = re.sub(r"\D", "", str(destinatario))
    if len(numero) == 10:
        numero = codigo_pais + numero
    componentes = []
    if documento_media_id:
        componentes.append({
            "type": "header",
            "parameters": [{
                "type": "document",
                "document": {"id": documento_media_id, "filename": "Documento_cesantias.pdf"}
            }]
        })
    if parametros_cuerpo:
        componentes.append({
            "type": "body",
            "parameters": [{"type": "text", "text": str(valor)} for valor in parametros_cuerpo]
        })
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": nombre_template,
            "language": {"code": str(datos.get("template_language", "es_CO"))},
            **({"components": componentes} if componentes else {})
        }
    }
    respuesta = requests.post(
        f"{base}/messages", headers={**headers, "Content-Type": "application/json"},
        json=payload, timeout=40
    )
    try:
        resultado = respuesta.json()
    except ValueError:
        resultado = {}
    if not respuesta.ok:
        error = resultado.get("error", {}) if isinstance(resultado, dict) else {}
        raise RuntimeError(f"Meta HTTP {respuesta.status_code}: {error.get('message', 'No se pudo enviar la plantilla.')} (código {error.get('code', 'sin código')})")
    mensajes = resultado.get("messages", []) if isinstance(resultado, dict) else []
    if not mensajes:
        raise RuntimeError("Meta no devolvió identificador del mensaje.")
    return mensajes[0].get("id", "")


def subir_pdf_a_meta(pdf_file_id):
    """Descarga el PDF privado desde Drive y lo carga en el endpoint de medios de WhatsApp."""
    datos = obtener_config_whatsapp()
    base, headers = _whatsapp_api_base(datos)
    servicio = obtener_servicio_drive()
    solicitud = servicio.files().get_media(fileId=pdf_file_id)
    buffer = BytesIO()
    descargador = MediaIoBaseDownload(buffer, solicitud)
    terminado = False
    while not terminado:
        _, terminado = descargador.next_chunk()
    buffer.seek(0)
    respuesta = requests.post(
        f"{base}/media",
        headers=headers,
        files={"file": ("Documento_cesantias.pdf", buffer, "application/pdf")},
        data={"messaging_product": "whatsapp", "type": "application/pdf"},
        timeout=90
    )
    try:
        resultado = respuesta.json()
    except ValueError:
        resultado = {}
    if not respuesta.ok or not resultado.get("id"):
        error = resultado.get("error", {}) if isinstance(resultado, dict) else {}
        raise RuntimeError(f"Meta no pudo cargar el PDF (HTTP {respuesta.status_code}): {error.get('message', 'Error al cargar el archivo.')}")
    return resultado["id"]


def enviar_whatsapp_solicitud_y_pdf():
    """Envía solo con autorización expresa y con activación administrativa explícita."""
    if not st.session_state.get("whatsapp_autorizado", False):
        return
    datos = obtener_config_whatsapp()
    if str(datos.get("enabled", "false")).lower() not in ("1", "true", "yes", "si"):
        return
    telefono = st.session_state.get("telefono", "")
    nombre = st.session_state.get("nombre", "")
    radicado = st.session_state.get("solicitud_id", "")
    errores = []

    if not st.session_state.get("whatsapp_confirmacion_estado") == "Enviado":
        try:
            template_confirmacion = str(datos.get("template_confirmation", "confirmacion_solicitud_cesantias"))
            enviar_template_whatsapp(telefono, template_confirmacion, [nombre, radicado])
            st.session_state.whatsapp_confirmacion_estado = "Enviado"
        except Exception as exc:
            st.session_state.whatsapp_confirmacion_estado = "Error"
            errores.append(f"Confirmación: {exc}")

    # La segunda plantilla debe estar aprobada con encabezado multimedia de tipo Documento.
    documento_listo = str(datos.get("document_template_ready", "false")).lower() in ("1", "true", "yes", "si")
    if documento_listo and not st.session_state.get("whatsapp_documento_estado") == "Enviado":
        try:
            media_id = subir_pdf_a_meta(st.session_state.pdf_id)
            template_documento = str(datos.get("template_document", "documento_cesantias_listo"))
            enviar_template_whatsapp(telefono, template_documento, [nombre, radicado], documento_media_id=media_id)
            st.session_state.whatsapp_documento_estado = "Enviado"
        except Exception as exc:
            st.session_state.whatsapp_documento_estado = "Error"
            errores.append(f"Documento PDF: {exc}")
    elif not documento_listo:
        st.session_state.whatsapp_documento_estado = "Pendiente de plantilla con encabezado Documento"

    if errores:
        st.session_state.whatsapp_errores = errores


def render_configuracion_whatsapp():
    """Prueba administrativa protegida; no interviene en el recorrido del cliente."""
    st.title("Prueba privada de WhatsApp · Meta")
    st.caption(
        "Esta pantalla es solo para administración. Envía el template hello_world "
        "al número de prueba autorizado que figura en Streamlit Secrets."
    )

    try:
        clave_correcta = str(obtener_config_oauth().get("admin_key", ""))
        if not clave_correcta:
            st.error(
                "Falta admin_key dentro de [google_oauth] en Streamlit Secrets. "
                "No se puede proteger esta pantalla sin esa clave."
            )
            st.stop()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    with st.form("form_admin_whatsapp"):
        clave_ingresada = st.text_input("Clave administrativa", type="password")
        continuar = st.form_submit_button("Continuar")

    if continuar:
        st.session_state["admin_whatsapp_autorizado"] = hmac.compare_digest(
            clave_ingresada, clave_correcta
        )
        if not st.session_state["admin_whatsapp_autorizado"]:
            st.error("La clave administrativa no coincide.")

    if not st.session_state.get("admin_whatsapp_autorizado", False):
        st.info("Introduce la misma clave administrativa que utilizas para la configuración de Google Drive.")
        st.stop()

    try:
        datos = obtener_config_whatsapp()
        phone_number_id = str(datos.get("phone_number_id", "")).strip()
        version = str(datos.get("api_version", "v27.0")).strip()
        if not version.startswith("v"):
            version = f"v{version}"
        destinatario = re.sub(r"\D", "", str(datos.get("test_recipient", "")))
        token = str(datos.get("access_token", "")).strip()

        st.success("Se encontró el bloque [whatsapp] en Streamlit Secrets.")
        st.write(f"**Versión Graph API:** {version}")
        st.write(f"**Phone Number ID:** {phone_number_id or 'Falta configurar'}")
        st.write(
            "**Destinatario de prueba:** "
            + (f"••••{destinatario[-4:]}" if destinatario else "Falta configurar")
        )
        st.write(f"**Token:** {'Configurado' if token else 'Falta configurar'}")
        st.warning(
            "Este botón envía un mensaje real de prueba al destinatario autorizado. "
            "No envía nada a clientes ni modifica el flujo de solicitudes."
        )
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    if st.button("Enviar mensaje de prueba hello_world", type="primary", use_container_width=True):
        try:
            with st.spinner("Enviando mensaje de prueba a través de Meta..."):
                resultado = enviar_mensaje_prueba_meta()
            st.success("Meta aceptó el mensaje de prueba.")
            st.write(f"**Estado:** {resultado['status']}")
            st.code(resultado["message_id"], language=None)
            st.caption("Comprueba ahora el WhatsApp del teléfono destinatario.")
        except Exception as exc:
            st.error(f"No se pudo enviar el mensaje de prueba: {exc}")


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


def obtener_id_carpeta_plantillas_empresas():
    """Obtiene o crea la carpeta de Drive donde se guardan las plantillas por empresa."""
    servicio = _crear_servicio_drive_nuevo()
    nombre_carpeta = "Plantillas_Empresas_Cesantias"
    nombre_q = nombre_carpeta.replace("\\", "\\\\").replace("'", "\\'")
    consulta = (
        f"name = '{nombre_q}' and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )
    existentes = servicio.files().list(
        q=consulta,
        pageSize=20,
        orderBy="createdTime",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        fields="files(id,name,mimeType,parents)"
    ).execute(num_retries=2).get("files", [])
    if existentes:
        return existentes[0]["id"]

    creada = servicio.files().create(
        body={"name": nombre_carpeta, "mimeType": "application/vnd.google-apps.folder"},
        fields="id,name,mimeType"
    ).execute(num_retries=2)
    return creada["id"]


def _clave_template_empresa(nombre, nit):
    identidad = _clave_nit(nit) or _normalizar_nombre_empresa(nombre)
    resumen = hashlib.sha256(identidad.encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", str(nombre or "Empresa")).strip("_")[:55]
    # El sufijo permite renovar plantillas antiguas creadas por buscadores de
    # logos menos estrictos. La fila existente en Sheets se actualiza al nuevo
    # Doc_ID; no se crea una segunda empresa.
    return f"Plantilla_Empresa_{slug}_{resumen}_v62"


def copiar_template_empresa(doc_id_base, nombre, nit):
    """Crea una plantilla específica de empresa desde la plantilla universal, sin duplicarla."""
    doc_id_base = str(doc_id_base or "").strip()
    if not doc_id_base:
        raise ValueError("No existe el Doc_ID de la plantilla universal en la fila 'Otra' de Empresas.")

    servicio = _crear_servicio_drive_nuevo()
    folder_id = obtener_id_carpeta_plantillas_empresas()
    _log_busqueda_empresa(
        f"PLANTILLA COPIA: origen=plantilla universal Doc_ID={doc_id_base}; "
        f"destino={_clave_template_empresa(nombre, nit)}; revisión=v62."
    )
    # Busca primero por la identidad actual (NIT si existe) y después por nombre.
    # Esto permite recuperar una copia previa si Drive la creó pero Sheets falló,
    # o si el NIT se completó en una solicitud posterior.
    nombres_archivo = list(dict.fromkeys([
        _clave_template_empresa(nombre, nit),
        _clave_template_empresa(nombre, "")
    ]))
    nombre_archivo_nuevo = nombres_archivo[0]
    for nombre_archivo in nombres_archivo:
        nombre_q = nombre_archivo.replace("\\", "\\\\").replace("'", "\\'")
        consulta = (
            f"name = '{nombre_q}' and '{folder_id}' in parents and trashed = false"
        )
        encontrados = servicio.files().list(
            q=consulta,
            pageSize=10,
            orderBy="createdTime desc",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields="files(id,name,mimeType,webViewLink,parents)"
        ).execute(num_retries=2).get("files", [])
        if encontrados:
            return encontrados[0], folder_id, True

    copia = servicio.files().copy(
        fileId=doc_id_base,
        body={"name": nombre_archivo_nuevo, "parents": [folder_id]},
        supportsAllDrives=True,
        fields="id,name,mimeType,webViewLink,parents"
    ).execute(num_retries=2)
    return copia, folder_id, False


def rellenar_plantilla_google_docs(document_id, valores):
    """Sustituye marcadores sin aplicar fuentes globales: conserva los estilos de la plantilla."""
    _log_busqueda_empresa(
        "FORMATO DOCS: se reemplazan únicamente los textos de los marcadores; "
        "no se aplica Calibri ni se modifica globalmente fuente, tamaño o negrita. "
        "El formato se hereda de la plantilla universal copiada."
    )
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


def _texto_plano_documento_google_docs(documento):
    """Extrae texto de body, tablas, encabezados y pies de un documento Docs."""
    partes = []

    def recorrer_bloque(contenido):
        for elemento in contenido or []:
            if not isinstance(elemento, dict):
                continue
            parrafo = elemento.get("paragraph")
            if isinstance(parrafo, dict):
                for parte in parrafo.get("elements", []) or []:
                    text_run = parte.get("textRun") if isinstance(parte, dict) else None
                    if isinstance(text_run, dict):
                        partes.append(text_run.get("content", ""))
            tabla = elemento.get("table")
            if isinstance(tabla, dict):
                for fila in tabla.get("tableRows", []) or []:
                    for celda in fila.get("tableCells", []) or []:
                        recorrer_bloque(celda.get("content", []))

    recorrer_bloque((documento.get("body") or {}).get("content", []))
    for encabezado in (documento.get("headers") or {}).values():
        recorrer_bloque(encabezado.get("content", []))
    for pie in (documento.get("footers") or {}).values():
        recorrer_bloque(pie.get("content", []))
    return "".join(partes)


def rellenar_identidad_en_plantilla_empresa(document_id, nombre_empresa, nit_empresa):
    """Fija nombre y NIT en la plantilla específica y verifica el resultado."""
    docs = obtener_servicio_docs()
    documento = docs.documents().get(documentId=document_id).execute()
    texto_antes = _texto_plano_documento_google_docs(documento)
    habia_marcador_logo = _documento_contiene_marcador(documento, "{{LOGO_EMPRESA}}")
    if habia_marcador_logo:
        _log_busqueda_empresa(
            "PLANTILLA EMPRESA: {{LOGO_EMPRESA}} detectado; se conservará intacto "
            "para insertar una imagen real. Nunca se sustituye por el nombre de la empresa."
        )

    posibles = {
        "{{NOMBRE EMPRESA}}": nombre_empresa,
        "{{NOMBRE_EMPRESA}}": nombre_empresa,
        "{{NOMBRE_DE_LA_EMPRESA}}": nombre_empresa,
        "{{EMPRESA_NOMBRE}}": nombre_empresa,
        "{{RAZON_SOCIAL}}": nombre_empresa,
        "{{RAZON SOCIAL}}": nombre_empresa,
        "{{RAZON_SOCIAL_EMPRESA}}": nombre_empresa,
        "{{NOMBRE_RAZON_SOCIAL}}": nombre_empresa,
        "{{EMPRESA}}": nombre_empresa,
        "{{NIT}}": nit_empresa,
        "{{NUMERO_NIT}}": nit_empresa,
        "{{NIT_EMPRESA}}": nit_empresa,
        "{{NIT EMPRESA}}": nit_empresa,
        "{{NIT_DE_LA_EMPRESA}}": nit_empresa,
        "{{NIT_EMPLEADOR}}": nit_empresa,
        "{{IDENTIFICACION_TRIBUTARIA}}": nit_empresa,
        "{{NUMERO_IDENTIFICACION_TRIBUTARIA}}": nit_empresa,
    }

    marcadores_detectados = []
    for match_marcador in re.finditer(r"\{\{\s*([^{}]+?)\s*\}\}", texto_antes):
        marcador = match_marcador.group(0)
        interior = match_marcador.group(1)
        marcadores_detectados.append(marcador)
        tokens = set(_normalizar_nombre_empresa(interior).split())
        if not tokens:
            continue
        # IMPORTANTE: {{LOGO_EMPRESA}} contiene la palabra "empresa", pero NO
        # es un marcador de razón social. La versión 5.6 lo clasificaba por error
        # como campo de nombre y lo reemplazaba por texto, dejando sin destino
        # a la inserción de la imagen. Todo marcador de logo debe permanecer intacto.
        if tokens.intersection({"logo", "logotipo", "logotype"}):
            _log_busqueda_empresa(
                f"PLANTILLA EMPRESA: marcador {marcador} excluido de sustitución de identidad; "
                "se reserva para insertar el archivo de imagen."
            )
            continue
        if "nit" in tokens or {"identificacion", "tributaria"}.issubset(tokens):
            posibles[marcador] = nit_empresa
        elif (
            "razon" in tokens or "empresa" in tokens or "compania" in tokens
            or "sociedad" in tokens or "empleador" in tokens
        ):
            posibles[marcador] = nombre_empresa

    reemplazos = {
        marcador: valor for marcador, valor in posibles.items()
        if marcador in texto_antes and str(valor or "").strip()
    }
    hay_nombre = any(str(valor or "") == str(nombre_empresa or "") for valor in reemplazos.values())
    hay_nit = any(str(valor or "") == str(nit_empresa or "") for valor in reemplazos.values())

    texto_normalizado_antes = _normalizar_nombre_empresa(texto_antes)
    nombre_ya_guardado = bool(
        _normalizar_nombre_empresa(nombre_empresa)
        and _normalizar_nombre_empresa(nombre_empresa) in texto_normalizado_antes
    )
    nit_base_ya_guardado = _normalizar_nit(nit_empresa)
    nit_ya_guardado = bool(nit_base_ya_guardado and nit_base_ya_guardado in _normalizar_nit(texto_antes))

    # Si la plantilla de esta misma empresa ya tiene los valores literales,
    # no se necesitan marcadores: se considera una identidad ya persistida.
    if not hay_nombre and nombre_ya_guardado:
        hay_nombre = True
    if not hay_nit and nit_ya_guardado:
        hay_nit = True
    if not reemplazos and hay_nombre and hay_nit:
        _log_busqueda_empresa(
            "PLANTILLA EMPRESA: la plantilla ya contiene el nombre legal y el NIT; "
            "no se necesitan sustituciones adicionales."
        )
        return True

    if not hay_nombre or not hay_nit:
        faltan = []
        if not hay_nombre:
            faltan.append("marcador de nombre/razón social o valor legal ya guardado")
        if not hay_nit:
            faltan.append("marcador de NIT o valor ya guardado")
        mensaje = (
            "La plantilla específica no tiene los marcadores necesarios para guardar la identidad "
            "de la empresa: " + ", ".join(faltan) + ". Marcadores encontrados: "
            + (", ".join(marcadores_detectados[:30]) if marcadores_detectados else "ninguno")
        )
        _log_busqueda_empresa("PLANTILLA EMPRESA: " + mensaje)
        raise RuntimeError(mensaje)

    _log_busqueda_empresa(
        f"PLANTILLA EMPRESA: fijando identidad en Doc_ID={document_id}; "
        f"marcadores={', '.join(reemplazos.keys())}."
    )
    rellenar_plantilla_google_docs(document_id, reemplazos)

    documento_despues = docs.documents().get(documentId=document_id).execute()
    texto_despues = _texto_plano_documento_google_docs(documento_despues)
    pendientes = [marcador for marcador in reemplazos if marcador in texto_despues]
    if habia_marcador_logo and not _documento_contiene_marcador(documento_despues, "{{LOGO_EMPRESA}}"):
        mensaje_logo = (
            "El marcador {{LOGO_EMPRESA}} desapareció durante el rellenado del nombre/NIT. "
            "Se detiene el proceso para no sustituir el logo por texto ni guardar una plantilla dañada."
        )
        _log_busqueda_empresa("PLANTILLA EMPRESA: " + mensaje_logo)
        raise RuntimeError(mensaje_logo)
    nombre_normalizado = _normalizar_nombre_empresa(nombre_empresa)
    texto_normalizado = _normalizar_nombre_empresa(texto_despues)
    nit_normalizado = _normalizar_nit(nit_empresa)
    texto_numeros = _normalizar_nit(texto_despues)
    nombre_presente = bool(nombre_normalizado and nombre_normalizado in texto_normalizado)
    nit_presente = bool(nit_normalizado and nit_normalizado in texto_numeros)
    if pendientes or not nombre_presente or not nit_presente:
        detalles = []
        if pendientes:
            detalles.append("marcadores sin sustituir: " + ", ".join(pendientes))
        if not nombre_presente:
            detalles.append("el nombre legal no aparece al volver a leer la plantilla")
        if not nit_presente:
            detalles.append("el NIT no aparece al volver a leer la plantilla")
        mensaje = "Google Docs no confirmó la identidad completa en la plantilla: " + "; ".join(detalles)
        _log_busqueda_empresa("PLANTILLA EMPRESA: " + mensaje)
        raise RuntimeError(mensaje)

    _log_busqueda_empresa(
        "PLANTILLA EMPRESA: verificación posterior correcta; nombre legal y NIT "
        "están guardados en la plantilla reutilizable."
    )
    return True


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


def _normalizar_nit(valor):
    """Deja únicamente dígitos para comparar NIT con o sin puntos/guion."""
    return re.sub(r"\D", "", str(valor or ""))


def _clave_nit(valor):
    """Devuelve el NIT base: acepta el identificador con o sin dígito de verificación."""
    digitos = _normalizar_nit(valor)
    return digitos[:-1] if len(digitos) == 10 else digitos


def _calcular_dv_nit_colombiano(nit_base):
    """Calcula el dígito de verificación colombiano para un NIT numérico."""
    digitos = _normalizar_nit(nit_base)
    if not digitos or len(digitos) > 15:
        return ""
    pesos = (71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3)
    suma = sum(int(digito) * peso for digito, peso in zip(digitos, pesos[-len(digitos):]))
    residuo = suma % 11
    return str(residuo if residuo in (0, 1) else 11 - residuo)


# ---------- DIAGNÓSTICO DE BÚSQUEDA EMPRESARIAL ----------
def _log_busqueda_empresa(mensaje):
    """Guarda trazas técnicas por sesión; nunca registra secretos de Google."""
    try:
        if "log_busqueda_empresa" not in st.session_state:
            st.session_state.log_busqueda_empresa = []
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.log_busqueda_empresa.append(f"[{marca}] {mensaje}")
    except Exception:
        pass


def _iniciar_log_busqueda_empresa(nombre, nit):
    try:
        st.session_state.log_busqueda_empresa = []
    except Exception:
        pass
    _log_busqueda_empresa("INICIO DE VALIDACIÓN")
    _log_busqueda_empresa(f"APP_BUILD_ID={APP_BUILD_ID}")
    _log_busqueda_empresa("RUES_TIMEOUT_CONFIG=connect:8s/read:35s")
    _log_busqueda_empresa(f"Datos recibidos: nombre={_celda_texto(nombre) or '(vacío)'} | NIT={_celda_texto(nit) or '(vacío)'}")


def _texto_log_busqueda_empresa():
    try:
        return "\n".join(st.session_state.get("log_busqueda_empresa", [])) or "No hay eventos registrados."
    except Exception:
        return "No hay eventos registrados."


# ---------- IDENTIDAD EMPRESARIAL: FUENTE OFICIAL RUES / CONFECÁMARAS ----------
# Conjunto nacional de datos básicos del Registro Mercantil, sincronizado con
# RUES y publicado por Confecámaras en el Portal Nacional de Datos Abiertos.
# No contiene excepciones ni NIT de empresas escritos manualmente en el código.
RUES_DATOS_ABIERTOS_API = "https://www.datos.gov.co/resource/c82u-588k.json"
RUES_DATOS_ABIERTOS_URL = (
    "https://www.datos.gov.co/Comercio-Industria-y-Turismo/"
    "Personas-Naturales-Personas-Jur-dicas-y-Entidades-/c82u-588k"
)
RUES_PORTAL_URL = "https://ruesfront.rues.org.co/"

# Conjunto oficial de entidades vigiladas, publicado por la propia
# Superintendencia Financiera en Datos Abiertos Colombia.
SFC_ENTIDADES_VIGILADAS_API = "https://www.datos.gov.co/resource/sr9n-792w.json"
SFC_ENTIDADES_VIGILADAS_URL = (
    "https://www.datos.gov.co/en/en/Public-Finance/"
    "Entidades-vigiladas-por-la-Superfinanciera/sr9n-792w"
)


def _clave_nit(valor):
    """Devuelve el NIT base sin separadores ni dígito de verificación."""
    digitos = _normalizar_nit(valor)
    return digitos[:-1] if len(digitos) == 10 else digitos


def _soql_escape(valor):
    """Escapa comillas simples en valores de consultas SoQL."""
    return str(valor or "").replace("'", "''")


def _consultar_dataset_rues(where, limite=30):
    """Consulta el conjunto oficial RUES/Confecámaras en datos.gov.co."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "CesantiasAlInstante/4.1 (consulta empresarial RUES)",
    }
    # El token de Socrata es opcional. Sin él, la consulta pública puede
    # realizarse sujeta a los límites de uso del portal.
    try:
        app_token = st.secrets.get("datos_gov_app_token", "")
    except Exception:
        app_token = ""
    if app_token:
        headers["X-App-Token"] = str(app_token).strip()

    _log_busqueda_empresa(
        f"RUES: enviando consulta al conjunto oficial; límite={limite}; "
        f"timeout_connect=8s; timeout_read=35s; filtro={where}"
    )
    respuesta = requests.get(
        RUES_DATOS_ABIERTOS_API,
        params={"$where": where, "$limit": str(limite)},
        headers=headers,
        timeout=(8, 35),
    )
    _log_busqueda_empresa(f"RUES: HTTP {respuesta.status_code}; content-type={respuesta.headers.get('Content-Type', '')}")
    respuesta.raise_for_status()
    datos = respuesta.json()
    if isinstance(datos, dict):
        mensaje = datos.get("message") or datos.get("error") or "Respuesta no válida del conjunto RUES."
        raise RuntimeError(str(mensaje)[:300])
    if not isinstance(datos, list):
        raise RuntimeError("El conjunto RUES devolvió un formato de respuesta no reconocido.")
    _log_busqueda_empresa(f"RUES: respuesta válida con {len(datos)} filas sin normalizar.")
    return datos


def _separar_nombre_principal_y_aliases(nombre_fuente):
    """Separa la razón social principal de cláusulas legales de denominaciones alternativas."""
    texto = re.sub(r"\s+", " ", _celda_texto(nombre_fuente)).strip(" ,;\n\t")
    if not texto:
        return "", [], []

    # RUES puede incluir en el campo razon_social una transcripción de una
    # cláusula estatutaria completa. La razón social principal termina antes
    # de expresiones como "podrá girar..." o "pudiendo identificar...".
    patrones_corte = (
        r"\b(?:(?:ADEM[AÁ]S|TAMBI[EÉ]N)\s+)?PODR[AÁ]\s+GIRAR\b",
        r"\bPUDIENDO\s+IDENTIFICAR\b",
    )
    posiciones = [m.start() for patron in patrones_corte
                  for m in re.finditer(patron, texto, flags=re.IGNORECASE)]
    nombre_principal = texto[:min(posiciones)] if posiciones else texto
    nombre_principal = re.sub(r"[\s,;:–—-]+$", "", nombre_principal).strip()
    if not nombre_principal:
        nombre_principal = texto
    # Normaliza la puntuación habitual de la forma societaria cuando el
    # conjunto omite el punto final, sin cambiar el contenido del nombre.
    nombre_principal = re.sub(r"\bS\.?\s*A\.?$", "S.A.", nombre_principal, flags=re.IGNORECASE)
    nombre_principal = re.sub(r"\bS\.?\s*A\.?\s*S\.?$", "S.A.S.", nombre_principal, flags=re.IGNORECASE)

    denominaciones = []
    comerciales = []
    patrones_alias = (
        (r"\bdenominaci[oó]n(?:\s+social)?\s+(?P<valor>.+?)(?=\s*,|\s+pudiendo\b|$)", denominaciones),
        (r"\bnombre\s+(?!comercial\b)(?:de\s+)?(?P<valor>.+?)(?=\s*,|\s+pudiendo\b|$)", denominaciones),
        (r"\bnombre\s+comercial(?:\s+de)?\s+(?P<valor>.+?)(?=\s*,|\s+pudiendo\b|$)", comerciales),
    )
    for patron, destino in patrones_alias:
        for match in re.finditer(patron, texto, flags=re.IGNORECASE):
            valor = re.sub(r"\s+", " ", match.group("valor")).strip(" .;,:\t")
            if valor and _normalizar_nombre_empresa(valor) != _normalizar_nombre_empresa(nombre_principal):
                if valor not in destino:
                    destino.append(valor)

    return nombre_principal, denominaciones, comerciales


def _registro_coincide_con_nombre(registro, nombre_consultado):
    """Comprueba nombre legal, alias, nombre comercial y otras denominaciones del mismo NIT."""
    nombres = [registro.get("nombre", "")]
    for campo in (
        "denominaciones_alternativas",
        "nombres_comerciales",
        "otras_denominaciones_mismo_nit",
    ):
        nombres.extend(registro.get(campo, []) or [])
    return any(_nombres_legales_coinciden(nombre_consultado, candidato)
               for candidato in nombres if _celda_texto(candidato))


def _registro_rues_tiene_matricula_activa(registro):
    """Reconoce estados activos explícitos sin confundirlos con 'INACTIVA'."""
    estado = _normalizar_nombre_empresa(registro.get("estado_matricula", ""))
    return estado in {"activa", "activo", "matricula activa", "matricula activo"}


def _seleccionar_nombre_vigente_rues(registros):
    """Selecciona una única razón social respaldada por matrícula RUES activa.

    Si el mismo NIT tiene nombres distintos y exactamente uno de ellos aparece
    en una matrícula ACTIVA, ese nombre se usa como principal. Los demás nombres
    se conservan como otras denominaciones para búsqueda y auditoría; no se descartan.
    Si hay cero o más de un nombre activo, no decide y devuelve None.
    """
    activos = [r for r in registros if _registro_rues_tiene_matricula_activa(r)]
    por_nombre_activo = {}
    for registro in activos:
        clave = _clave_nombre_empresa(registro.get("nombre", ""))
        if clave:
            por_nombre_activo.setdefault(clave, []).append(registro)

    if len(por_nombre_activo) != 1:
        _log_busqueda_empresa(
            "RUES: no hay una única razón social asociada a matrícula ACTIVA; "
            f"nombres activos distintos={len(por_nombre_activo)}. Se requiere otra fuente oficial."
        )
        return None

    clave_vigente, candidatos_activos = next(iter(por_nombre_activo.items()))
    # Si hay varias filas activas de la misma razón social, preferir la matrícula
    # con año de renovación más reciente, conservando el resto como auditoría.
    def puntaje(registro):
        try:
            anio = int(registro.get("ultimo_ano_renovado") or 0)
        except (TypeError, ValueError):
            anio = 0
        return (anio, bool(_celda_texto(registro.get("matricula"))))

    seleccionado = dict(max(candidatos_activos, key=puntaje))
    otras_denominaciones = []
    for registro in registros:
        nombre = _celda_texto(registro.get("nombre", ""))
        clave = _clave_nombre_empresa(nombre)
        if nombre and clave != clave_vigente and nombre not in otras_denominaciones:
            otras_denominaciones.append(nombre)
        for anterior in registro.get("otras_denominaciones_mismo_nit", []) or []:
            anterior = _celda_texto(anterior)
            if anterior and _clave_nombre_empresa(anterior) != clave_vigente and anterior not in otras_denominaciones:
                otras_denominaciones.append(anterior)

    seleccionado["otras_denominaciones_mismo_nit"] = otras_denominaciones
    seleccionado["fuente_identidad"] = (
        "RUES / Confecámaras - única razón social con matrícula ACTIVA; "
        "otras denominaciones del mismo NIT conservadas como denominaciones adicionales"
    )
    seleccionado["url_fuente_identidad"] = RUES_DATOS_ABIERTOS_URL
    _log_busqueda_empresa(
        "RUES: identidad resuelta por estado registral: "
        f"nombre principal={seleccionado.get('nombre')} | "
        f"estado={seleccionado.get('estado_matricula')} | "
        f"matrícula={seleccionado.get('matricula')} | "
        f"otras denominaciones del mismo NIT={otras_denominaciones}"
    )
    return seleccionado


def _registro_rues_normalizado(fila):
    """Normaliza una fila oficial RUES y conserva el texto fuente y las denominaciones alternativas."""
    nombre_fuente = _celda_texto(fila.get("razon_social", ""))
    if not nombre_fuente:
        partes = [
            _celda_texto(fila.get("primer_nombre", "")),
            _celda_texto(fila.get("segundo_nombre", "")),
            _celda_texto(fila.get("primer_apellido", "")),
            _celda_texto(fila.get("segundo_apellido", "")),
        ]
        nombre_fuente = " ".join(p for p in partes if p)
    nombre, denominaciones, comerciales = _separar_nombre_principal_y_aliases(nombre_fuente)
    nit_base = _clave_nit(fila.get("nit", "") or fila.get("numero_identificacion", ""))
    dv = re.sub(r"\D", "", _celda_texto(fila.get("digito_verificacion", "")))[:1]
    nit_completo = f"{nit_base}-{dv}" if nit_base and dv else nit_base
    return {
        "nombre": nombre,
        "nombre_fuente": nombre_fuente,
        "denominaciones_alternativas": denominaciones,
        "nombres_comerciales": comerciales,
        "nit_base": nit_base,
        "digito_verificacion": dv,
        "nit": nit_completo,
        "estado_matricula": _celda_texto(fila.get("estado_matricula", "")),
        "camara_comercio": _celda_texto(fila.get("camara_comercio", "")),
        "codigo_camara": _celda_texto(fila.get("codigo_camara", "")),
        "matricula": _celda_texto(fila.get("matricula", "")),
        "ultimo_ano_renovado": _celda_texto(fila.get("ultimo_ano_renovado", "")),
        "fuente_identidad": "RUES / Confecámaras - Datos Abiertos Colombia",
        "url_fuente_identidad": RUES_DATOS_ABIERTOS_URL,
    }


def _deduplicar_registros_rues(filas):
    """Deduplica registros de una misma razón social/NIT en varias matrículas."""
    unicos = {}
    for fila in filas:
        registro = _registro_rues_normalizado(fila)
        if not registro["nombre"] or not registro["nit_base"]:
            continue
        clave = (registro["nit_base"], _clave_nombre_empresa(registro["nombre"]))
        anterior = unicos.get(clave)
        if anterior is None:
            unicos[clave] = registro
            continue
        try:
            anio_nuevo = int(registro.get("ultimo_ano_renovado") or 0)
        except Exception:
            anio_nuevo = 0
        try:
            anio_anterior = int(anterior.get("ultimo_ano_renovado") or 0)
        except Exception:
            anio_anterior = 0
        estado_nuevo = _normalizar_nombre_empresa(registro.get("estado_matricula", ""))
        estado_anterior = _normalizar_nombre_empresa(anterior.get("estado_matricula", ""))
        puntuacion_nueva = (1 if "activa" in estado_nuevo else 0, anio_nuevo)
        puntuacion_anterior = (1 if "activa" in estado_anterior else 0, anio_anterior)

        # Las distintas matrículas del mismo NIT pueden aportar alias o textos
        # estatutarios complementarios. Se conservan todos, aunque se elija
        # como registro principal la matrícula activa más útil.
        seleccionado = registro if puntuacion_nueva > puntuacion_anterior else anterior
        otro = anterior if seleccionado is registro else registro
        for campo in ("denominaciones_alternativas", "nombres_comerciales"):
            combinados = list(seleccionado.get(campo, []) or [])
            for valor in otro.get(campo, []) or []:
                if valor not in combinados:
                    combinados.append(valor)
            seleccionado[campo] = combinados
        fuentes = []
        for valor in (seleccionado.get("nombres_fuente", []) or [seleccionado.get("nombre_fuente", "")]):
            if valor and valor not in fuentes:
                fuentes.append(valor)
        for valor in (otro.get("nombres_fuente", []) or [otro.get("nombre_fuente", "")]):
            if valor and valor not in fuentes:
                fuentes.append(valor)
        seleccionado["nombres_fuente"] = fuentes
        unicos[clave] = seleccionado
    return list(unicos.values())


def _consultar_rues_por_nit(nit):
    """Busca NIT exacto en RUES; evita una batería de consultas parciales vacías."""
    nit_digitos = _normalizar_nit(nit)
    nit_base = _clave_nit(nit)
    if len(nit_base) < 7:
        return []

    variantes = []
    for valor in (nit_base, nit_digitos):
        if valor and valor not in variantes:
            variantes.append(valor)
    condiciones = []
    for campo in ("nit", "numero_identificacion"):
        for valor in variantes:
            condiciones.append(f"{campo} = '{_soql_escape(valor)}'")
    where = "(" + " OR ".join(condiciones) + ")"

    filas = []
    error_consulta = None
    try:
        filas = _consultar_dataset_rues(where, limite=100)
    except Exception as exc:
        error_consulta = exc
        _log_busqueda_empresa(
            f"RUES: falló la consulta exacta: {type(exc).__name__}: {str(exc)[:220]}. "
            "Se hará una sola consulta de recuperación."
        )
        try:
            where_reintento = " OR ".join(
                f"nit = '{_soql_escape(valor)}'" for valor in variantes
            )
            filas = _consultar_dataset_rues("(" + where_reintento + ")", limite=100)
            _log_busqueda_empresa("RUES: consulta de recuperación completada.")
        except Exception as exc_reintento:
            _log_busqueda_empresa(
                f"RUES: también falló la recuperación: {type(exc_reintento).__name__}: "
                f"{str(exc_reintento)[:220]}"
            )
            filas = []

    registros = _deduplicar_registros_rues(filas)
    exactos = [r for r in registros if r.get("nit_base") == nit_base]
    _log_busqueda_empresa(
        f"RUES: {len(filas)} filas recibidas; {len(registros)} registros únicos; "
        f"{len(exactos)} coincidencias exactas para el NIT base."
    )
    for reg in exactos[:20]:
        _log_busqueda_empresa(
            f"RUES candidato: nombre principal={reg.get('nombre')} | "
            f"nombre original={reg.get('nombre_fuente', reg.get('nombre'))} | "
            f"denominaciones alternativas={reg.get('denominaciones_alternativas', [])} | "
            f"NIT={reg.get('nit')} | cámara={reg.get('camara_comercio')} | "
            f"matrícula={reg.get('matricula')} | estado={reg.get('estado_matricula')}"
        )
    if exactos:
        return exactos
    if error_consulta:
        _log_busqueda_empresa("RUES: sin resultado por incidencia de conexión; se continuará con fuentes oficiales alternativas.")
    else:
        _log_busqueda_empresa("RUES: la consulta exacta respondió correctamente, pero este NIT no figura en el conjunto consultado.")
    return []

def _consultar_rues_por_nombre(nombre):
    """Busca por razón social en RUES sin escoger coincidencias ambiguas."""
    clave = _clave_nombre_empresa(nombre)
    tokens = [t for t in clave.split() if len(t) >= 3]
    if not tokens:
        return []
    # Conserva la grafía original (con tildes) y también una variante sin
    # diacríticos: en el conjunto RUES conviven nombres con y sin acentos.
    tokens_originales = [
        t for t in re.findall(r"[^\W_]+", str(nombre or ""), flags=re.UNICODE)
        if len(_clave_nombre_empresa(t)) >= 3
    ]
    tokens_consulta = tokens[:2]
    originales = tokens_originales[:2]
    condiciones = []
    for indice, token in enumerate(tokens_consulta):
        variantes = {token.upper()}
        if indice < len(originales):
            variantes.add(originales[indice].upper())
        condiciones_token = [
            f"upper(razon_social) like '%{_soql_escape(v)}%'"
            for v in sorted(variantes)
        ]
        condiciones.append("(" + " OR ".join(condiciones_token) + ")")
    filas = _consultar_dataset_rues(" AND ".join(condiciones), limite=100)
    return _deduplicar_registros_rues(filas)


def _nombres_legales_coinciden(nombre_entrada, nombre_oficial):
    """Compara nombres ignorando tildes, conectores y sufijos jurídicos."""
    a = set(_clave_nombre_empresa(nombre_entrada).split())
    b = set(_clave_nombre_empresa(nombre_oficial).split())
    if not a or not b:
        return False
    if a == b:
        return True
    interseccion = len(a & b)
    return interseccion >= min(len(a), len(b)) and interseccion >= 1


def _consultar_entidad_vigilada_superfinanciera_por_nit(nit):
    """Consulta directamente el conjunto oficial de entidades vigiladas por la SFC."""
    nit_digitos = _normalizar_nit(nit)
    nit_base = _clave_nit(nit)
    if len(nit_base) < 7:
        return None

    # El conjunto almacena NUMEROIDENTIFICACION como campo numérico y suele
    # incluir el dígito de verificación. Si el usuario solo escribió el NIT
    # base, también se consulta el DV calculado.
    valores = []
    for valor in (nit_digitos, nit_base):
        if valor and valor.isdigit() and valor not in valores:
            valores.append(valor)
    if len(nit_digitos) == 9:
        dv = _calcular_dv_nit_colombiano(nit_base)
        if dv and (nit_base + dv) not in valores:
            valores.append(nit_base + dv)
    condiciones = [f"numeroidentificacion = {int(v)}" for v in valores]
    where = "(" + " OR ".join(condiciones) + ")"
    _log_busqueda_empresa(
        "Superfinanciera: consultando directamente el conjunto oficial "
        f"sr9n-792w; filtro={where}"
    )
    try:
        respuesta = requests.get(
            SFC_ENTIDADES_VIGILADAS_API,
            params={"$where": where, "$limit": "10"},
            headers={
                "Accept": "application/json",
                "User-Agent": "CesantiasAlInstante/4.7 (validacion de entidad vigilada)",
            },
            timeout=(5, 15),
        )
        _log_busqueda_empresa(
            f"Superfinanciera: HTTP {respuesta.status_code}; "
            f"content-type={respuesta.headers.get('Content-Type', '')}"
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not isinstance(datos, list):
            _log_busqueda_empresa("Superfinanciera: respuesta JSON no contiene una lista de registros.")
            return None
    except Exception as exc:
        _log_busqueda_empresa(
            f"Superfinanciera: consulta directa falló: {type(exc).__name__}: {str(exc)[:220]}"
        )
        return None

    coincidencias = []
    for fila in datos:
        nit_fila = _normalizar_nit(fila.get("numeroidentificacion", ""))
        if _clave_nit(nit_fila) != nit_base:
            continue
        nombre = _celda_texto(fila.get("razon_social", ""))
        if not nombre:
            continue
        coincidencias.append({"nombre": nombre, "nit": nit_fila, "fila": fila})

    unicos = {}
    for item in coincidencias:
        unicos.setdefault(_clave_nombre_empresa(item["nombre"]), item)
    _log_busqueda_empresa(
        f"Superfinanciera: {len(datos)} filas recibidas; "
        f"{len(coincidencias)} coincidencias exactas; "
        f"{len(unicos)} denominaciones únicas para el NIT."
    )
    for item in coincidencias[:10]:
        _log_busqueda_empresa(
            f"Superfinanciera candidato: {item['nombre']} | NIT={item['nit']}"
        )

    if len(unicos) != 1:
        if not unicos:
            _log_busqueda_empresa("Superfinanciera: el NIT no aparece en el conjunto de entidades vigiladas.")
        else:
            _log_busqueda_empresa("Superfinanciera: hay más de una denominación para el NIT; no se selecciona ninguna.")
        return None

    candidato = next(iter(unicos.values()))
    nit_completo = candidato["nit"]
    dv = nit_completo[-1] if len(nit_completo) == 10 else ""
    _log_busqueda_empresa(
        f"Superfinanciera: identidad confirmada por fuente oficial: {candidato['nombre']} | "
        f"URL={SFC_ENTIDADES_VIGILADAS_URL}"
    )
    return {
        "nombre": candidato["nombre"],
        "nit_base": nit_base,
        "digito_verificacion": dv,
        "nit": f"{nit_base}-{dv}" if dv else nit_base,
        "estado_matricula": "",
        "camara_comercio": "",
        "codigo_camara": "",
        "matricula": "",
        "ultimo_ano_renovado": "",
        "fuente_identidad": "Superintendencia Financiera de Colombia - Datos Abiertos",
        "url_fuente_identidad": SFC_ENTIDADES_VIGILADAS_URL,
    }


def _consultar_secop_ii_por_nit(nit):
    """Consulta el dataset oficial SECOP II por NIT de la entidad contratante.

    Es una fuente estructurada adicional para entidades públicas que pueden no
    aparecer en el conjunto mercantil RUES (por ejemplo, empresas industriales
    y comerciales del Estado). No depende de Bing/Google.
    """
    nit_base = _clave_nit(nit)
    nit_digitos = _normalizar_nit(nit)
    if len(nit_base) < 7:
        return None

    api = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
    variantes = []
    for valor in (nit_base, nit_digitos):
        if valor and valor not in variantes:
            variantes.append(valor)
    literales = ", ".join("'" + _soql_escape(v) + "'" for v in variantes)
    where = f"nit_entidad in ({literales})"
    _log_busqueda_empresa(
        f"SECOP II: consulta directa del conjunto oficial p6dx-8zbt por NIT; filtro={where}"
    )
    try:
        respuesta = requests.get(
            api,
            params={
                "$select": "nit_entidad,entidad,count(*) as frecuencia",
                "$where": where,
                "$group": "nit_entidad,entidad",
                "$order": "frecuencia DESC",
                "$limit": "20",
            },
            headers={
                "Accept": "application/json",
                "User-Agent": "CesantiasAlInstante/5.1 (consulta de datos abiertos SECOP II)",
            },
            timeout=(8, 25),
        )
        _log_busqueda_empresa(
            f"SECOP II: HTTP {respuesta.status_code}; "
            f"content-type={respuesta.headers.get('Content-Type', '')}"
        )
        respuesta.raise_for_status()
        filas = respuesta.json()
        if not isinstance(filas, list):
            _log_busqueda_empresa("SECOP II: la respuesta no es una lista JSON; se omite esta fuente.")
            return None
    except Exception as exc:
        _log_busqueda_empresa(
            f"SECOP II: consulta directa falló: {type(exc).__name__}: {str(exc)[:220]}"
        )
        return None

    candidatos = {}
    for fila in filas:
        nit_fila = _normalizar_nit(fila.get("nit_entidad", ""))
        if _clave_nit(nit_fila) != nit_base:
            continue
        nombre = _celda_texto(fila.get("entidad", ""))
        if not nombre:
            continue
        try:
            frecuencia = int(float(fila.get("frecuencia", 0) or 0))
        except Exception:
            frecuencia = 0
        clave = _clave_nombre_empresa(nombre)
        if not clave:
            continue
        actual = candidatos.get(clave)
        if actual is None or frecuencia > actual["frecuencia"]:
            candidatos[clave] = {
                "nombre": nombre,
                "nit": nit_fila,
                "frecuencia": frecuencia,
            }

    _log_busqueda_empresa(
        f"SECOP II: {len(filas)} filas agregadas; "
        f"{len(candidatos)} nombres distintos para el NIT."
    )
    for item in sorted(candidatos.values(), key=lambda x: x["frecuencia"], reverse=True)[:10]:
        _log_busqueda_empresa(
            f"SECOP II candidato: {item['nombre']} | NIT={item['nit']} | "
            f"procesos={item['frecuencia']}"
        )
    if not candidatos:
        _log_busqueda_empresa("SECOP II: no se encontró coincidencia exacta para el NIT.")
        return None

    ordenados = sorted(candidatos.values(), key=lambda x: x["frecuencia"], reverse=True)
    principal = ordenados[0]
    # La fuente es el NIT exacto de la entidad que publicó procesos. Si el
    # dataset conserva nombres históricos, se guardan como denominaciones
    # adicionales y se usa el nombre de mayor recurrencia.
    digitos = _normalizar_nit(nit)
    dv = digitos[-1] if len(digitos) == 10 else _calcular_dv_nit_colombiano(nit_base)
    nit_formateado = f"{nit_base}-{dv}" if dv else nit_base
    alternativas = [x["nombre"] for x in ordenados[1:] if x["nombre"] != principal["nombre"]]
    _log_busqueda_empresa(
        f"SECOP II: identidad candidata por NIT exacto: {principal['nombre']} | "
        f"alternativas conservadas={alternativas[:5]}"
    )
    return {
        "nombre": principal["nombre"],
        "nombre_fuente": principal["nombre"],
        "nombres_fuente": [principal["nombre"]] + alternativas,
        "denominaciones_alternativas": alternativas,
        "nombres_comerciales": [],
        "otras_denominaciones_mismo_nit": alternativas,
        "nit_base": nit_base,
        "digito_verificacion": dv or "",
        "nit": nit_formateado,
        "estado_matricula": "",
        "camara_comercio": "",
        "codigo_camara": "",
        "matricula": "",
        "ultimo_ano_renovado": "",
        "fuente_identidad": "Agencia Nacional de Contratación Pública - SECOP II / Datos Abiertos",
        "url_fuente_identidad": "https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt",
    }


def _consultar_identidad_nit_en_fuentes_oficiales(nit):
    """Respalda RUES con documentos públicos oficiales que identifican el mismo NIT."""
    nit_digitos = _normalizar_nit(nit)
    nit_base = _clave_nit(nit)
    if not nit_base:
        return None

    # Primero se consultan fuentes oficiales estructuradas, por NIT exacto.
    registro_sfc = _consultar_entidad_vigilada_superfinanciera_por_nit(nit)
    if registro_sfc:
        return registro_sfc

    # Segunda fuente estructurada: SECOP II contiene el NIT y nombre de la
    # entidad que publica procesos. Es útil para entidades públicas que no
    # necesariamente figuran en RUES. Se consulta por API, no por buscadores.
    registro_secop = _consultar_secop_ii_por_nit(nit)
    if registro_secop:
        return registro_secop

    variantes = [nit_digitos] if nit_digitos else []
    if nit_base not in variantes:
        variantes.append(nit_base)
    # Máximo cuatro búsquedas dirigidas (sin repetir cada consulta por el NIT con y sin DV).
    consultas = [
        f'site:superservicios.gov.co "{nit_base}" "Nombre o razón social" RUPS',
        f'site:wa-reportsui.azurewebsites.net "{nit_base}" OR "{nit_digitos}"',
        f'site:superfinanciera.gov.co "{nit_base}" OR "{nit_digitos}" NIT',
        f'site:supersociedades.gov.co "{nit_base}" OR "{nit_digitos}" NIT',
    ]

    dominios_oficiales = (
        "datos.gov.co", "gov.co", "rues.org.co", "ccc.org.co", "ccb.org.co",
        "camaramedellin.com.co", "camaracali.com.co", "camarapereira.org.co",
        "camarabogota.org.co", "confecamaras.org.co", "supersociedades.gov.co",
        "superfinanciera.gov.co", "superservicios.gov.co", "sui.superservicios.gov.co",
        "wa-reportsui.azurewebsites.net", "sic.gov.co", "mincit.gov.co", "invima.gov.co", "dian.gov.co",
    )
    candidatos = {}
    _log_busqueda_empresa(
        f"Respaldo documental: búsqueda dirigida por NIT {nit_base}; "
        f"{len(consultas)} consultas en fuentes oficiales mediante Bing RSS. "
        "La identidad solo se acepta si el documento o página consultada contiene el NIT exacto."
    )
    for indice_consulta, consulta in enumerate(consultas, 1):
        _log_busqueda_empresa(f"Búsqueda documental: consulta {indice_consulta}/{len(consultas)}: {consulta}")
        try:
            resultados = _buscar_resultados_empresa(consulta, max_resultados=12)
            _log_busqueda_empresa(f"Búsqueda documental: consulta {indice_consulta} devolvió {len(resultados)} resultados RSS.")
        except Exception as exc:
            _log_busqueda_empresa(f"Búsqueda documental: error en consulta {indice_consulta}: {type(exc).__name__}: {str(exc)[:250]}")
            continue

        for item in resultados:
            _log_busqueda_empresa(f"Resultado web: título={_celda_texto(item.get('titulo', ''))[:180]} | URL={_celda_texto(item.get('url', ''))[:300]} | resumen={_celda_texto(item.get('snippet', ''))[:350]}")
            url = item.get("url", "")
            titulo = _celda_texto(item.get("titulo", ""))
            snippet = _celda_texto(item.get("snippet", ""))
            host = urlparse(url).netloc.lower().split(":")[0].removeprefix("www.")
            texto_resumen = f"{titulo} {snippet}"
            if not url.startswith(("http://", "https://")):
                continue

            # No se descarta solo porque el buscador no muestre el NIT en el
            # resumen. Se consulta la página oficial y se exige el NIT exacto
            # en su contenido antes de aceptar cualquier razón social.
            # Las fuentes admitidas son portales oficiales, cámaras, RUES o
            # certificados mercantiles alojados en el propio dominio empresarial.
            dominio_oficial = any(host == d or host.endswith("." + d) for d in dominios_oficiales)
            menciona_certificado = bool(re.search(
                r"certificado\s+de\s+(?:existencia|representaci[oó]n)|c[aá]mara\s+de\s+comercio|registro\s+mercantil|RUPS|identificador\s+del\s+prestador",
                texto_resumen, re.I
            ))
            dominio_sui = any(host == d or host.endswith("." + d) for d in (
                "superservicios.gov.co", "sui.superservicios.gov.co", "wa-reportsui.azurewebsites.net"
            ))
            dominio_empresarial_candidato = not any(
                host == d or host.endswith("." + d) for d in (
                    "bing.com", "google.com", "duckduckgo.com", "wikipedia.org",
                    "facebook.com", "instagram.com", "linkedin.com", "youtube.com",
                    "x.com", "twitter.com", "tiktok.com"
                )
            )
            if not (dominio_oficial or menciona_certificado or dominio_empresarial_candidato):
                continue

            candidato = _nombre_candidato_desde_resultado(titulo, snippet, nit)
            texto_verificacion = texto_resumen
            # Cuando el resumen no contiene una razón social (con forma jurídica),
            # intentar leer la página pública; en certificados oficiales el nombre
            # suele estar en el cuerpo y no en el título del resultado.
            tiene_forma_legal = bool(candidato and re.search(
                r"(?:S\.?\s*A\.?\s*S\.?|S\.?\s*A\.?\s*E\.?\s*S\.?\s*P\.?|S\.?\s*A\.?|E\.?\s*S\.?\s*P\.?|E\.?\s*I\.?\s*C\.?\s*E\.?|LTDA\.?|LIMITADA|E\.?\s*U\.?|S\.?\s*EN\s*C\.?)$",
                candidato, re.I
            ))
            if not candidato or len(_normalizar_nombre_empresa(candidato).split()) < 2 or not tiene_forma_legal:
                try:
                    pagina = requests.get(
                        url,
                        headers={"User-Agent": "Mozilla/5.0 (compatible; CesantiasAlInstante/4.1)"},
                        timeout=(5, 12),
                        allow_redirects=True,
                    )
                    if pagina.ok:
                        content_type = pagina.headers.get("Content-Type", "").lower()
                        texto_pagina = ""
                        if "text/html" in content_type or "application/xhtml" in content_type:
                            texto_pagina = _texto_html_limpio(pagina.text[:2_500_000])
                        elif "pdf" in content_type or (pagina.content[:5] == b"%PDF-"):
                            try:
                                from pypdf import PdfReader
                                import io
                                lector_pdf = PdfReader(io.BytesIO(pagina.content))
                                texto_pagina = " ".join((p.extract_text() or "") for p in lector_pdf.pages[:20])
                            except Exception as exc_pdf:
                                _log_busqueda_empresa(f"Respaldo oficial: no se pudo extraer PDF {url}: {type(exc_pdf).__name__}: {str(exc_pdf)[:140]}")
                        if texto_pagina:
                            texto_verificacion += " " + texto_pagina
                            candidato = (
                                _nombre_candidato_cercano_al_nit(texto_pagina, nit)
                                or _nombre_candidato_desde_resultado(titulo, texto_pagina, nit)
                                or candidato
                            )
                except Exception:
                    pass

            if not candidato or len(_normalizar_nombre_empresa(candidato).split()) < 2:
                continue
            # Se requiere que el resultado oficial muestre el NIT consultado y
            # que el nombre encontrado tenga forma de razón social.
            if not _nit_coincide_con_texto(nit, texto_verificacion):
                continue
            if not re.search(
                r"\b(?:S\.?\s*A\.?\s*S\.?|S\.?\s*A\.?\s*E\.?\s*S\.?\s*P\.?|S\.?\s*A\.?|E\.?\s*S\.?\s*P\.?|E\.?\s*I\.?\s*C\.?\s*E\.?|LTDA\.?|LIMITADA|E\.?\s*U\.?|S\.?\s*EN\s*C\.?)\b",
                candidato, re.I
            ):
                continue
            clave = _clave_nombre_empresa(candidato)
            candidatos.setdefault(clave, {"nombre": candidato, "url": url, "titulo": titulo})

    _log_busqueda_empresa(f"Respaldo oficial: {len(candidatos)} razones sociales candidatas únicas: " + "; ".join(v.get("nombre", "") for v in candidatos.values()))
    if len(candidatos) != 1:
        _log_busqueda_empresa("Respaldo oficial: no se pudo confirmar una única razón social; se rechaza por seguridad.")
        return None

    candidato = next(iter(candidatos.values()))
    _log_busqueda_empresa(f"Respaldo oficial: identidad candidata confirmada: {candidato.get('nombre')} | URL={candidato.get('url')}")
    digitos = _normalizar_nit(nit)
    dv = digitos[-1] if len(digitos) == 10 else ""
    return {
        "nombre": candidato["nombre"],
        "nit_base": nit_base,
        "digito_verificacion": dv,
        "nit": f"{nit_base}-{dv}" if dv else nit_base,
        "estado_matricula": "",
        "camara_comercio": "",
        "codigo_camara": "",
        "matricula": "",
        "ultimo_ano_renovado": "",
        "fuente_identidad": "Documento público oficial localizado por NIT",
        "url_fuente_identidad": candidato["url"],
    }


def _resolver_identidad_rues(nombre_empresa="", nit_empresa=""):
    """Resuelve nombre/NIT desde RUES; usa documentos oficiales como respaldo público."""
    nombre_entrada = _celda_texto(nombre_empresa)
    nit_entrada = _celda_texto(nit_empresa)
    if not nombre_entrada and not nit_entrada:
        raise ValueError("Escribe el nombre de la empresa, el NIT o ambos.")
    _iniciar_log_busqueda_empresa(nombre_entrada, nit_entrada)

    if nit_entrada:
        digitos_usuario = _normalizar_nit(nit_entrada)
        if len(digitos_usuario) == 10:
            dv_calculado = _calcular_dv_nit_colombiano(digitos_usuario[:-1])
            if dv_calculado and digitos_usuario[-1] != dv_calculado:
                raise ValueError(
                    f"El dígito de verificación del NIT no es correcto. Para el número {digitos_usuario[:-1]}, "
                    f"el dígito calculado es {dv_calculado}. Revisa el dato antes de continuar."
                )
        errores_rues = []
        try:
            registros = _consultar_rues_por_nit(nit_entrada)
        except Exception as exc:
            registros = []
            errores_rues.append(str(exc)[:180])

        _log_busqueda_empresa(f"RUES: resultado final de búsqueda por NIT: {len(registros)} registros.")
        if not registros:
            # El conjunto público se sincroniza periódicamente y algunas
            # matrículas pueden no aparecer en la consulta por campo exacto.
            # Se intenta localizar un documento público oficial con el mismo NIT.
            registro_oficial = _consultar_identidad_nit_en_fuentes_oficiales(nit_entrada)
            if registro_oficial:
                registros = [registro_oficial]

        if not registros:
            detalle = (" Detalle técnico RUES: " + errores_rues[0]) if errores_rues else ""
            raise ValueError(
                "No encontramos ese NIT en RUES ni en las fuentes estructuradas y documentos oficiales consultados. "
                "La búsqueda no pudo confirmar la empresa; no se creó plantilla ni se modificó la base."
                + detalle
            )
        if len(registros) > 1:
            # RUES puede devolver varias matrículas antiguas o variantes de
            # denominación para un mismo NIT. No se elige la primera fila a ciegas:
            # se contrasta contra una fuente pública oficial de mayor autoridad
            # (superintendencia, entidad de vigilancia, DIAN o cámara de comercio).
            nombres = {_clave_nombre_empresa(r.get("nombre", "")) for r in registros if r.get("nombre")}
            nombres.discard("")
            if len(nombres) > 1:
                nombres_detectados = sorted({
                    _celda_texto(r.get("nombre", "")) for r in registros if r.get("nombre")
                })
                _log_busqueda_empresa(
                    "VALIDACIÓN: RUES devolvió varias denominaciones para el mismo NIT: "
                    + "; ".join(nombres_detectados)
                )

                # Primera regla general: si entre las matrículas del mismo NIT
                # existe exactamente una razón social distinta con estado ACTIVA,
                # usarla como nombre vigente y conservar los demás nombres como
                # denominaciones adicionales. Esto resuelve cambios de razón social y matrículas
                # antiguas sin hardcodear empresas ni NIT concretos.
                registro_vigente = _seleccionar_nombre_vigente_rues(registros)
                if registro_vigente:
                    registros = [registro_vigente]
                else:
                    _log_busqueda_empresa(
                        "VALIDACIÓN: se inicia contraste con fuentes oficiales adicionales; "
                        "no se utilizarán buscadores generales como prueba de identidad."
                    )
                    registro_oficial = _consultar_identidad_nit_en_fuentes_oficiales(nit_entrada)
                    if registro_oficial:
                        registros = [registro_oficial]
                    else:
                        _log_busqueda_empresa(
                            "VALIDACIÓN: ninguna fuente oficial resolvió el conflicto. "
                            "Se detiene el proceso sin modificar Drive ni Sheets."
                        )
                        detalle_nombres = "; ".join(nombres_detectados[:5])
                        raise ValueError(
                            "RUES encontró varias denominaciones para el mismo NIT y no hay "
                            "una única razón social con matrícula ACTIVA ni una confirmación "
                            "suficiente en otra fuente oficial. No se creó plantilla ni se "
                            "modificó la base para evitar asociar datos incorrectos. "
                            "Denominaciones encontradas: " + detalle_nombres
                        )
        registro = registros[0]
        digitos_entrada = _normalizar_nit(nit_entrada)
        if len(digitos_entrada) == 10 and registro.get("digito_verificacion"):
            if digitos_entrada[-1] != registro["digito_verificacion"]:
                raise ValueError(
                    "El dígito de verificación no coincide con el registro oficial. Revisa el NIT antes de continuar."
                )
        if nombre_entrada and _registro_coincide_con_nombre(registro, nombre_entrada):
            if any(
                _nombres_legales_coinciden(nombre_entrada, otra_denominacion)
                for otra_denominacion in (registro.get("otras_denominaciones_mismo_nit", []) or [])
            ):
                _log_busqueda_empresa(
                    f"VALIDACIÓN: el nombre ingresado coincide con otra denominación registrada para el mismo NIT; "
                    f"se conservará como nombre principal vigente {registro.get('nombre')}."
                )
        if nombre_entrada and not _registro_coincide_con_nombre(registro, nombre_entrada):
            raise ValueError(
                f"El NIT pertenece a «{registro['nombre']}», pero el nombre ingresado no coincide "
                "con la razón social ni con las denominaciones alternativas registradas. "
                "No se asociaron los datos para evitar mezclar empresas."
            )
        _log_busqueda_empresa(f"VALIDACIÓN: identidad aceptada: {registro.get('nombre')} | fuente={registro.get('fuente_identidad')} | URL={registro.get('url_fuente_identidad')}")
        return registro

    _log_busqueda_empresa("Búsqueda RUES por nombre (no se proporcionó NIT).")
    registros = _consultar_rues_por_nombre(nombre_entrada)
    if not registros:
        raise ValueError(
            "RUES/Confecámaras no encontró esa razón social. Comprueba el nombre legal o agrega el NIT."
        )
    clave_entrada = _clave_nombre_empresa(nombre_entrada)
    exactos = [r for r in registros if _clave_nombre_empresa(r["nombre"]) == clave_entrada]
    candidatos = exactos or [r for r in registros if _registro_coincide_con_nombre(r, nombre_entrada)]
    por_identidad = {}
    for registro in candidatos:
        por_identidad[(registro["nit_base"], _clave_nombre_empresa(registro["nombre"]))] = registro
    candidatos = list(por_identidad.values())
    if len(candidatos) != 1:
        raise ValueError(
            "La consulta oficial encontró varias empresas posibles con ese nombre. "
            "Escribe también el NIT para identificar la sociedad correcta."
        )
    return candidatos[0]

def _normalizar_nombre_empresa(valor):
    """Normaliza tildes, siglas jurídicas y signos para comparar nombres."""
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"[^a-z0-9]+", " ", texto.lower()).strip()


def _clave_nombre_empresa(valor):
    """Clave estable de razón social; omite conectores y sufijos jurídicos frecuentes."""
    ignorar = {
        "sas", "sa", "s", "a", "bic", "ltda", "limitada", "eu", "e.u",
        "cia", "compania", "sociedad", "anonima", "anónima", "empresa",
        "de", "del", "la", "el", "los", "las", "y", "e"
    }
    palabras = [
        palabra for palabra in _normalizar_nombre_empresa(valor).split()
        if palabra not in ignorar and len(palabra) > 1
    ]
    return " ".join(palabras)


def _texto_html_limpio(valor):
    valor = re.sub(r"<[^>]+>", " ", str(valor or ""))
    return re.sub(r"\s+", " ", html.unescape(valor)).strip()


def _nit_coincide_con_texto(nit, texto):
    """Compara NIT completo o base de 9 dígitos cuando la fuente omite el DV."""
    clave = _clave_nit(nit)
    digitos_texto = _normalizar_nit(texto)
    return bool(clave and clave in digitos_texto)


def _texto_coincide_empresa(nombre, texto):
    """Comprueba coincidencia razonable del nombre, ignorando sufijos societarios."""
    palabras_ignorar = {
        "sas", "sa", "s", "a", "bic", "empresa", "colombia", "sociedad",
        "compania", "cia", "limitada", "ltda", "the", "de", "del", "la", "el",
        "y", "e", "en", "por", "para"
    }
    palabras = [
        palabra for palabra in _normalizar_nombre_empresa(nombre).split()
        if len(palabra) >= 3 and palabra not in palabras_ignorar
    ]
    texto_normalizado = _normalizar_nombre_empresa(texto)
    if not palabras:
        return False
    encontradas = sum(1 for palabra in set(palabras) if palabra in texto_normalizado)
    minimo = 1 if len(set(palabras)) == 1 else min(2, len(set(palabras)))
    return encontradas >= minimo


def _extraer_nit_de_pagina(texto):
    """Extrae un NIT mencionado cerca de las etiquetas habituales en Colombia."""
    texto_limpio = _texto_html_limpio(texto)
    patrones = (
        r"(?:NIT|N\.\s*I\.\s*T\.?|NIT\s+No\.?|identificaci[oó]n tributaria)\s*[:#-]?\s*([0-9][0-9.\-\s]{7,18}[0-9])",
        r"(?:tax\s*id|tax\s*number)\s*[:#-]?\s*([0-9][0-9.\-\s]{7,18}[0-9])",
    )
    for patron in patrones:
        coincidencia = re.search(patron, texto_limpio, re.I)
        if coincidencia:
            valor = re.sub(r"\s+", "", coincidencia.group(1)).strip(".-")
            digitos = _normalizar_nit(valor)
            if 9 <= len(digitos) <= 10:
                return valor
    return ""


def _extraer_nombre_de_pagina(html_pagina, titulo_busqueda="", url=""):
    """Intenta obtener la razón social desde metadatos y contenido de la página."""
    contenido = str(html_pagina or "")[:2_000_000]
    candidatos = []

    for etiqueta in re.findall(r"<meta\b[^>]*>", contenido, re.I):
        attrs = {}
        for clave, comilla, valor in re.findall(r"([\w:-]+)\s*=\s*([\"'])(.*?)\2", etiqueta, re.I | re.S):
            attrs[clave.lower()] = html.unescape(valor)
        key = (attrs.get("property") or attrs.get("name") or "").lower()
        if key in ("og:site_name", "application-name") and attrs.get("content"):
            candidatos.append(attrs["content"])

    for bloque in re.findall(
        r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        contenido, re.I | re.S
    ):
        try:
            datos = json.loads(bloque.strip())
        except Exception:
            continue
        pendientes = datos if isinstance(datos, list) else [datos]
        while pendientes:
            elemento = pendientes.pop(0)
            if isinstance(elemento, dict):
                tipo = elemento.get("@type", "")
                tipos = tipo if isinstance(tipo, list) else [tipo]
                if any(any(t in str(tipo_item) for t in ("Organization", "Corporation", "LocalBusiness")) for tipo_item in tipos):
                    nombre = elemento.get("name")
                    if isinstance(nombre, str) and nombre.strip():
                        candidatos.append(nombre.strip())
                pendientes.extend(v for v in elemento.values() if isinstance(v, (dict, list)))
            elif isinstance(elemento, list):
                pendientes.extend(elemento)

    for patron in (r"<h1\b[^>]*>(.*?)</h1>", r"<title\b[^>]*>(.*?)</title>"):
        hallazgo = re.search(patron, contenido, re.I | re.S)
        if hallazgo:
            candidatos.append(_texto_html_limpio(hallazgo.group(1)))

    if titulo_busqueda:
        candidatos.append(_texto_html_limpio(titulo_busqueda))

    for candidato in candidatos:
        candidato = re.split(r"\s+[|–—-]\s+", candidato, maxsplit=1)[0].strip(" -|–—")
        candidato = re.sub(r"^(inicio|home|p[aá]gina principal)\s*[:|–—-]*\s*", "", candidato, flags=re.I)
        if len(candidato) >= 3 and not re.fullmatch(r"(?i)(inicio|home|contacto|login|facebook|instagram|linkedin)", candidato):
            return candidato[:180]

    host = urlparse(url).netloc.lower().removeprefix("www.")
    if host:
        return host.split(".")[0].replace("-", " ").title()
    return ""


def _dominio_es_red_social(url):
    dominio = urlparse(url or "").netloc.lower().split(":")[0]
    return any(
        dominio == red or dominio.endswith("." + red)
        for red in (
            "facebook.com", "instagram.com", "linkedin.com",
            "youtube.com", "x.com", "twitter.com", "tiktok.com"
        )
    )


def _desenvolver_url_bing(href):
    """Convierte enlaces de seguimiento Bing (/ck/a) en su URL de destino real."""
    href = html.unescape(str(href or "")).strip()
    if not href:
        return ""
    parsed = urlparse(href)
    host = parsed.netloc.lower().split(":")[0].removeprefix("www.")
    if host not in ("bing.com", "cn.bing.com", "global.bing.com"):
        return href

    parametros = parse_qs(parsed.query)
    destino = (parametros.get("u") or parametros.get("url") or [""])[0].strip()
    if destino.startswith("a1"):
        codificado = destino[2:]
        try:
            relleno = "=" * ((4 - len(codificado) % 4) % 4)
            destino = base64.urlsafe_b64decode(codificado + relleno).decode("utf-8", errors="replace")
        except Exception:
            return ""
    destino = html.unescape(destino).strip()
    if not destino.startswith(("http://", "https://")):
        return ""
    host_destino = urlparse(destino).netloc.lower().split(":")[0].removeprefix("www.")
    if not host_destino or host_destino.endswith("bing.com"):
        return ""
    return destino


def _desenvolver_url_google(href, url_base="https://www.google.com/"):
    """Recupera el destino real de enlaces de redirección de Google Search."""
    href = html.unescape(str(href or "")).strip()
    if not href:
        return ""
    url_absoluta = urljoin(url_base, href)
    parsed = urlparse(url_absoluta)
    host = parsed.netloc.lower().split(":", 1)[0].removeprefix("www.")
    if not (host == "google.com" or host.endswith(".google.com") or host.startswith("google.")):
        return url_absoluta
    if parsed.path not in ("/url", "/imgres"):
        return ""
    parametros = parse_qs(parsed.query)
    destino = ""
    for clave in ("q", "url", "imgurl"):
        valores = parametros.get(clave) or []
        if valores and valores[0].startswith(("http://", "https://")):
            destino = html.unescape(valores[0]).strip()
            break
    if not destino:
        return ""
    host_destino = urlparse(destino).netloc.lower().split(":", 1)[0]
    if not host_destino or "google." in host_destino:
        return ""
    return destino


def _extraer_enlaces_con_titulo_html(html_pagina, url_base):
    """Extrae enlaces con encabezado/título visible, sin depender de una clase CSS."""
    class _ParserEnlaces(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.enlaces = []
            self.actual = None
            self.profundidad_h = 0

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag.lower() == "a" and attrs.get("href"):
                if self.actual:
                    # Cierra defensivamente un anchor mal formado antes de abrir otro.
                    self._cerrar_actual()
                self.actual = {"href": attrs.get("href", ""), "texto": [], "titulo": [], "en_h": False}
            elif self.actual and tag.lower() in ("h1", "h2", "h3", "h4"):
                self.actual["en_h"] = True

        def handle_data(self, data):
            if self.actual:
                self.actual["texto"].append(data)
                if self.actual["en_h"]:
                    self.actual["titulo"].append(data)

        def handle_endtag(self, tag):
            if not self.actual:
                return
            if tag.lower() in ("h1", "h2", "h3", "h4"):
                self.actual["en_h"] = False
            elif tag.lower() == "a":
                self._cerrar_actual()

        def _cerrar_actual(self):
            if not self.actual:
                return
            href = html.unescape(self.actual.get("href", "")).strip()
            titulo = re.sub(r"\s+", " ", " ".join(self.actual.get("titulo") or [])).strip()
            texto = re.sub(r"\s+", " ", " ".join(self.actual.get("texto") or [])).strip()
            if href:
                url_candidata = urljoin(url_base, href)
                host_candidato = urlparse(url_candidata).netloc.lower().split(":", 1)[0].removeprefix("www.")
                if host_candidato == "google.com" or host_candidato.endswith(".google.com") or host_candidato.startswith("google."):
                    url_candidata = _desenvolver_url_google(url_candidata, url_base=url_base)
                if url_candidata:
                    self.enlaces.append({"url": url_candidata, "titulo": titulo or texto[:180], "snippet": texto[:350]})
            self.actual = None

    parser = _ParserEnlaces()
    try:
        parser.feed(str(html_pagina or ""))
    except Exception:
        pass
    resultados = []
    vistos = set()
    for item in parser.enlaces:
        url = item.get("url", "")
        host = urlparse(url).netloc.lower().removeprefix("www.")
        if not url.startswith(("http://", "https://")) or not host:
            continue
        if any(x in host for x in ("google.com", "bing.com", "microsoft.com")):
            continue
        clave = url.split("?", 1)[0].rstrip("/").lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        resultados.append(item)
    return resultados


def _buscar_resultados_google(query, max_resultados=12):
    """Respaldo de búsqueda Google: extrae anchors con h1-h4 y exige dominio/título relacionado."""
    max_resultados = max(1, min(int(max_resultados), 30))
    try:
        respuesta = requests.get(
            "https://www.google.com/search",
            params={"q": query, "num": max(10, max_resultados), "hl": "es", "gl": "co"},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=(8, 18), allow_redirects=True,
        )
        _log_busqueda_empresa(
            f"Google HTML fallback: HTTP {respuesta.status_code}; content-type={respuesta.headers.get('Content-Type','')}; bytes={len(respuesta.content)}."
        )
        respuesta.raise_for_status()
        pagina_html = respuesta.text[:5_000_000]
        resultados = _extraer_enlaces_con_titulo_html(pagina_html, respuesta.url)
        comillas = re.findall(r'[\"“]([^\"”]{2,100})[\"”]', query)
        empresa_esperada = next((q.strip() for q in comillas if not re.fullmatch(r"[\d.\- ]+", q.strip())), "")
        sitio_restringido = re.search(r"\bsite:([a-z0-9.-]+)", query, re.I)
        filtrados = []
        for item in resultados:
            host = urlparse(item["url"]).netloc.lower().removeprefix("www.")
            if sitio_restringido:
                dominio_objetivo = sitio_restringido.group(1).lower().removeprefix("www.")
                if host != dominio_objetivo and not host.endswith("." + dominio_objetivo):
                    continue
            if empresa_esperada and not (
                _texto_coincide_empresa(empresa_esperada, item.get("titulo", ""))
                or _texto_coincide_empresa(empresa_esperada, item.get("snippet", ""))
                or _dominio_coincide_empresa(host, empresa_esperada)
            ):
                continue
            filtrados.append(item)
            if len(filtrados) >= max_resultados:
                break
        _log_busqueda_empresa(
            f"Google HTML fallback: enlaces={len(resultados)}; resultados relevantes={len(filtrados)}; "
            f"empresa_filtro={empresa_esperada or '(sin frase exacta)'}."
        )
        return filtrados
    except Exception as exc:
        _log_busqueda_empresa(f"Google HTML fallback: error {type(exc).__name__}: {str(exc)[:240]}")
        return []


def _buscar_resultados_empresa(query, max_resultados=12):
    """Busca páginas candidatas por RSS y, si RSS viene vacío, usa resultados HTML estructurados.

    Bing RSS está respondiendo HTTP 200 con feeds de ~1 KB y ningún <item>.
    En ese caso se activa el HTML normal y se aceptan solo resultados cuyo título,
    resumen o dominio guarden relación con la empresa buscada.
    """
    import xml.etree.ElementTree as ET

    max_resultados = max(1, min(int(max_resultados), 50))
    resultados = []
    vistos = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, text/html;q=0.8, */*;q=0.7",
    }

    # Primera opción: RSS.
    try:
        respuesta = requests.get(
            "https://www.bing.com/search",
            params={"format": "rss", "q": query, "cc": "CO", "setlang": "es", "count": max(10, max_resultados)},
            headers=headers,
            timeout=(8, 20),
        )
        _log_busqueda_empresa(
            f"Bing RSS: HTTP {respuesta.status_code}; content-type={respuesta.headers.get('Content-Type', '')}; "
            f"respuesta={len(respuesta.content)} bytes."
        )
        respuesta.raise_for_status()
        try:
            root = ET.fromstring(respuesta.content)
            channel_title = root.findtext(".//channel/title", default="")
            channel_desc = root.findtext(".//channel/description", default="")
            for item in root.findall(".//item"):
                titulo = _celda_texto(item.findtext("title", default=""))
                url = html.unescape(_celda_texto(item.findtext("link", default=""))).strip()
                snippet = _celda_texto(item.findtext("description", default=""))
                if not titulo or not url.startswith(("http://", "https://")):
                    continue
                host = urlparse(url).netloc.lower().split(":")[0].removeprefix("www.")
                if not host or host.endswith("bing.com"):
                    continue
                clave_url = url.split("?")[0].rstrip("/").lower()
                if clave_url in vistos:
                    continue
                vistos.add(clave_url)
                resultados.append({"url": url, "titulo": titulo, "snippet": snippet})
                if len(resultados) >= max_resultados:
                    break
            _log_busqueda_empresa(
                f"Bing RSS: raíz={root.tag}; canal={channel_title[:120]}; "
                f"descripción={channel_desc[:160]}; elementos item={len(root.findall('.//item'))}."
            )
        except Exception as exc_xml:
            _log_busqueda_empresa(
                f"Bing RSS: XML no interpretable ({type(exc_xml).__name__}: {str(exc_xml)[:180]})."
            )
    except Exception as exc:
        _log_busqueda_empresa(
            f"Bing RSS: no se pudo obtener el feed: {type(exc).__name__}: {str(exc)[:220]}"
        )

    # Segunda opción: HTML de Bing. Se usa cuando RSS no trae resultados.
    if not resultados:
        try:
            respuesta_html = requests.get(
                "https://www.bing.com/search",
                params={"q": query, "cc": "CO", "setlang": "es", "count": max(10, max_resultados)},
                headers={**headers, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"},
                timeout=(8, 20),
            )
            _log_busqueda_empresa(
                f"Bing HTML fallback: HTTP {respuesta_html.status_code}; "
                f"content-type={respuesta_html.headers.get('Content-Type', '')}; bytes={len(respuesta_html.content)}."
            )
            respuesta_html.raise_for_status()
            pagina_html = respuesta_html.text
            comillas = re.findall(r'[\"“]([^\"”]{2,100})[\"”]', query)
            empresa_esperada = next(
                (q.strip() for q in comillas if not re.fullmatch(r"[\d.\- ]+", q.strip())), ""
            )
            sitio_restringido = re.search(r"\bsite:([a-z0-9.-]+)", query, re.I)

            # Los resultados web de Bing normalmente están en <li class="b_algo">.
            bloques = []
            for match_li in re.finditer(r"<li\b([^>]*)>(.*?)</li>", pagina_html, re.I | re.S):
                attrs_li = _obtener_atributos_html("<li " + match_li.group(1) + ">")
                clases = attrs_li.get("class", "").lower().split()
                if "b_algo" in clases:
                    bloques.append(match_li.group(2))

            # Fallback secundario si Bing cambia la envoltura <li> pero conserva h2>a.
            if not bloques:
                bloques = [m.group(0) for m in re.finditer(
                    r"<h2\b[^>]*>\s*<a\b[^>]*>.*?</a>\s*</h2>.*?(?=<h2\b|$)",
                    pagina_html, re.I | re.S
                )]

            for bloque in bloques:
                match_a = re.search(r"<h2\b[^>]*>\s*<a\b([^>]*)>(.*?)</a>", bloque, re.I | re.S)
                if not match_a:
                    continue
                attrs_a = _obtener_atributos_html("<a " + match_a.group(1) + ">")
                url = _desenvolver_url_bing(attrs_a.get("href", ""))
                titulo = _texto_html_limpio(match_a.group(2))
                match_p = re.search(r"<p\b[^>]*>(.*?)</p>", bloque, re.I | re.S)
                snippet = _texto_html_limpio(match_p.group(1)) if match_p else ""
                if not url or not titulo:
                    continue
                host = urlparse(url).netloc.lower().removeprefix("www.")
                if not host or host.endswith(("bing.com", "microsoft.com")):
                    continue
                if sitio_restringido:
                    dominio_objetivo = sitio_restringido.group(1).lower().removeprefix("www.")
                    if host != dominio_objetivo and not host.endswith("." + dominio_objetivo):
                        continue
                # Evita repetir el problema de resultados irrelevantes: el resultado
                # debe mencionar la empresa o usar un dominio cuyo nombre la identifique.
                if empresa_esperada and not (
                    _texto_coincide_empresa(empresa_esperada, f"{titulo} {snippet}")
                    or _dominio_coincide_empresa(host, empresa_esperada)
                ):
                    continue
                clave_url = url.split("?")[0].rstrip("/").lower()
                if clave_url in vistos:
                    continue
                vistos.add(clave_url)
                resultados.append({"url": url, "titulo": titulo, "snippet": snippet})
                if len(resultados) >= max_resultados:
                    break
            _log_busqueda_empresa(
                f"Bing HTML fallback: bloques={len(bloques)}; resultados relevantes={len(resultados)}; "
                f"empresa_filtro={empresa_esperada or '(sin frase exacta)'}."
            )
        except Exception as exc:
            _log_busqueda_empresa(
                f"Bing HTML fallback: error {type(exc).__name__}: {str(exc)[:240]}"
            )

    # Tercer proveedor: Google HTML. Se usa solo si Bing RSS/HTML no entregó
    # candidatos; el resultado debe coincidir con la empresa y respetar site:.
    if not resultados:
        resultados_google = _buscar_resultados_google(query, max_resultados=max_resultados)
        for item in resultados_google:
            clave_url = item.get("url", "").split("?", 1)[0].rstrip("/").lower()
            if clave_url and clave_url not in vistos:
                vistos.add(clave_url)
                resultados.append(item)
                if len(resultados) >= max_resultados:
                    break

    _log_busqueda_empresa(f"Búsqueda web: {len(resultados)} resultados válidos para la consulta.")
    for item in resultados[:5]:
        _log_busqueda_empresa(
            f"Resultado búsqueda: título={item['titulo'][:150]} | URL={item['url'][:250]} | "
            f"resumen={item['snippet'][:220]}"
        )
    return resultados

def _nombre_candidato_cercano_al_nit(texto, nit):
    """Extrae una razón social adyacente al NIT de un snippet o fila de resultados."""
    texto = _texto_html_limpio(texto)
    base = _clave_nit(nit)
    if not texto or not base:
        return ""
    patron_nit = r"(?<!\d)" + r"[\s.\-]*".join(map(re.escape, base)) + r"(?:[\s.\-]*\d)?(?!\d)"
    sufijo_legal = r"(?:S\.?\s*A\.?\s*S\.?|S\.?\s*A\.?\s*E\.?\s*S\.?\s*P\.?|S\.?\s*A\.?|E\.?\s*S\.?\s*P\.?|E\.?\s*I\.?\s*C\.?\s*E\.?|LTDA\.?|LIMITADA|E\.?\s*U\.?|S\.?\s*EN\s*C\.?|S\.?\s*C\.?\s*A\.?)"
    # En informes SUI/Superservicios la razón social suele aparecer bajo una etiqueta explícita.
    etiqueta_nombre = re.search(
        r"(?:nombre\s+o\s+raz[oó]n\s+social|raz[oó]n\s+social|nombre\s+del\s+prestador)\s*[:：-]?\s*"
        r"(.{3,180}?)\s*(?=(?:\d+(?:\.\d+)*\s*)?(?:NIT|N\.\s*I\.\s*T\.?|identificador\s+del\s+prestador))",
        texto, re.I | re.S
    )
    if etiqueta_nombre and _nit_coincide_con_texto(nit, texto):
        candidato = re.sub(r"\s+", " ", etiqueta_nombre.group(1)).strip(" ,:;-–—")
        candidato = re.sub(r"^(?:\d+(?:\.\d+)*\s*)", "", candidato)
        candidato = re.sub(r"\s+\d+(?:\.\d+)*\.?$", "", candidato).strip(" ,:;-–—")
        if len(_normalizar_nombre_empresa(candidato).split()) >= 2 and re.search(sufijo_legal + r"$", candidato, re.I):
            return candidato[:180]
    ruido = {
        "consulta", "consultas", "empresa", "empresas", "resultado", "resultados",
        "registro", "registros", "ministerio", "mintrabajo", "trabajo", "gobierno", "calificacion",
        "calificacion", "estandares", "minimos", "nit", "rut", "numero", "identificacion",
        "colombia", "informacion", "comercio", "principal", "aceptable", "activo",
        "activa", "inactivo", "inactiva", "razon", "social", "camara", "camaras",
        "de", "del", "la", "el", "los", "las", "y", "en", "por", "para", "con"
    }
    for match_nit in re.finditer(patron_nit, texto, re.I):
        antes = texto[max(0, match_nit.start() - 180):match_nit.start()]
        despues = texto[match_nit.end():match_nit.end() + 180]
        for contexto in (antes, despues):
            # Las fichas suelen mostrar NIT | RAZÓN SOCIAL o RAZÓN SOCIAL | NIT.
            segmentos = re.split(r"[|;\n•]+", contexto)
            segmentos = [s.strip(" .,:;-–—") for s in segmentos if s.strip(" .,:;-–—")]
            for segmento in reversed(segmentos) if contexto is antes else segmentos:
                # Prioriza la razón social que termina en una forma jurídica.
                for m in re.finditer(r"([A-ZÁÉÍÓÚÑ0-9][A-ZÁÉÍÓÚÑ0-9&'’.,()\- ]{1,120}?\b" + sufijo_legal + r")", segmento, re.I):
                    candidato = m.group(1).strip(" ,:;–—")
                    # Recorta prefijos del título del portal (p. ej. "Consulta
                    # MinTrabajo - ") y conserva la puntuación de S.A./S.A.S.
                    candidato = re.split(r"[|;•]", candidato)[-1].strip(" ,:;–—")
                    candidato = re.split(r"\s+-\s+", candidato)[-1].strip(" ,:;–—")
                    sufijo = re.search(sufijo_legal + r"$", candidato, re.I)
                    if sufijo:
                        tokens = list(re.finditer(r"\S+", candidato[:sufijo.start()]))
                        tokens = tokens[-7:]
                        while tokens and _normalizar_nombre_empresa(tokens[0].group()) in ruido:
                            tokens.pop(0)
                        if tokens:
                            candidato = candidato[tokens[0].start():].strip(" ,:;–—")
                    if len(_normalizar_nombre_empresa(candidato).split()) >= 2:
                        return candidato[:180]
                # Respaldo: etiqueta explícita dentro del mismo bloque.
                m = re.search(
                    r"(?:raz[oó]n\s+social|empresa|nombre\s+legal)\s*[:：-]?\s*([^,;|]{3,120})",
                    segmento, re.I
                )
                if m:
                    candidato = m.group(1).strip(" .,:;-–—")
                    candidato = re.sub(patron_nit, " ", candidato, flags=re.I).strip(" .,:;-–—")
                    if len(_normalizar_nombre_empresa(candidato).split()) >= 2:
                        return candidato[:180]
    return ""


def _nombre_candidato_desde_resultado(titulo="", snippet="", nit=""):
    """Extrae una razón social probable del título o resumen de un resultado web."""
    textos = [_texto_html_limpio(titulo), _texto_html_limpio(snippet)]
    if nit:
        # Los motores pueden devolver el NIT y la razón social dentro del resumen,
        # pero no necesariamente con la etiqueta literal "Razón Social".
        for texto_resultado in (textos[1], textos[0]):
            candidato_nit = _nombre_candidato_cercano_al_nit(texto_resultado, nit)
            if candidato_nit:
                return candidato_nit
    patrones_explicitos = (
        r"(?:raz[oó]n\s+social|nombre\s+(?:legal\s+)?de\s+la\s+empresa)\s*[:：-]?\s*([^|;\n]{3,150})",
        r"(?:raz[oó]n\s+social)\s+(?:es|:)?\s*([^|;\n]{3,150})",
    )
    for texto in textos:
        if not texto:
            continue
        for patron in patrones_explicitos:
            match = re.search(patron, texto, re.I)
            if match:
                candidato = match.group(1).strip(" .,:;-–—")
                candidato = re.split(
                    r"\s+(?:NIT|N\.\s*I\.\s*T\.?|identificaci[oó]n tributaria|domicilio|actividad|tel[eé]fono)\b",
                    candidato, maxsplit=1, flags=re.I
                )[0].strip(" .,:;-–—")
                if len(candidato) >= 3:
                    return candidato[:180]

    if textos[0]:
        candidato = textos[0]
        # Quitar los sufijos habituales de los resultados de directorios y buscadores.
        candidato = re.split(
            r"\s+(?:[-|–—]\s*)?(?:datos?\s+de\s+contacto|datos?\s+generales|informaci[oó]n\s+comercial|directorio\s+de\s+empresas|ranking\s+de\s+empresas|consulta\s+de\s+RUT)\b",
            candidato, maxsplit=1, flags=re.I
        )[0]
        candidato = re.split(r"\s+[|–—]\s+", candidato, maxsplit=1)[0]
        candidato = re.sub(r"^\s*(?:NIT|RUT)\s*[:#-]?\s*[0-9.\-]+\s*[-:|]?\s*", "", candidato, flags=re.I)
        candidato = re.sub(r"^\s*[0-9]{9,10}\s*[-:|]?\s*", "", candidato)
        candidato = re.sub(r"^\s*empresa\s*[:#-]?\s*", "", candidato, flags=re.I)
        candidato = re.sub(r"\s+NIT\s+[0-9.\-]+.*$", "", candidato, flags=re.I).strip(" .,:;-–—")
        palabras_ruido = {
            "inicio", "home", "contacto", "noticias", "ministerio", "gobierno",
            "consulta", "resultado", "resultados", "registro", "documento", "pdf"
        }
        tokens = _normalizar_nombre_empresa(candidato).split()
        if len(candidato) >= 3 and tokens and tokens[0] not in palabras_ruido:
            return candidato[:180]
    return ""


def _descargar_candidato_logo(candidato, referer=""):
    """Descarga un candidato y registra por qué se acepta o descarta."""
    if not candidato or urlparse(candidato).scheme not in ("http", "https"):
        _log_busqueda_empresa(f"LOGO DESCARGA: candidato omitido por URL no válida: {str(candidato)[:220]}")
        return None
    url_limpia = candidato.lower().split("?")[0]
    if any(palabra in url_limpia for palabra in ("loader", "loading", "spinner", "placeholder", "tracking-pixel")):
        _log_busqueda_empresa(f"LOGO DESCARGA: candidato omitido por ser placeholder: {candidato[:220]}")
        return None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }
        if referer:
            headers["Referer"] = referer
        imagen = requests.get(
            candidato, headers=headers, timeout=(8, 18),
            allow_redirects=True, stream=True
        )
        tipo = imagen.headers.get("Content-Type", "").lower().split(";")[0].strip()
        if not imagen.ok:
            _log_busqueda_empresa(
                f"LOGO DESCARGA: HTTP {imagen.status_code}; URL={candidato[:220]}; content-type={tipo}."
            )
            imagen.close()
            return None
        contenido = bytearray()
        for bloque in imagen.iter_content(65536):
            if not bloque:
                continue
            contenido.extend(bloque)
            if len(contenido) > 5_000_000:
                imagen.close()
                _log_busqueda_empresa(f"LOGO DESCARGA: imagen excede 5 MB y se descarta: {candidato[:220]}")
                return None
        url_final = imagen.url
        imagen.close()
        if len(contenido) < 100:
            _log_busqueda_empresa(
                f"LOGO DESCARGA: respuesta demasiado pequeña ({len(contenido)} bytes): {url_final[:220]}"
            )
            return None

        datos_imagen = bytes(contenido)
        if datos_imagen.startswith(b"\x89PNG\r\n\x1a\n"):
            tipo = "image/png"
        elif datos_imagen.startswith(b"\xff\xd8\xff"):
            tipo = "image/jpeg"
        elif datos_imagen.startswith((b"GIF87a", b"GIF89a")):
            tipo = "image/gif"
        elif b"<svg" in datos_imagen[:1000].lower() or tipo in ("image/svg+xml", "text/xml", "application/xml"):
            tipo = "image/svg+xml"
        elif tipo == "image/webp" or datos_imagen[8:12] == b"WEBP":
            tipo = "image/webp"

        if tipo == "image/svg+xml":
            try:
                import cairosvg
                datos_imagen = cairosvg.svg2png(bytestring=datos_imagen, output_width=1200)
                tipo = "image/png"
            except Exception as exc:
                _log_busqueda_empresa(
                    f"LOGO DESCARGA: SVG recibido pero no convertido; {type(exc).__name__}: {str(exc)[:220]}"
                )
                return None
        elif tipo == "image/webp":
            try:
                from PIL import Image
                origen = Image.open(BytesIO(datos_imagen)).convert("RGBA")
                salida = BytesIO()
                origen.save(salida, format="PNG")
                datos_imagen = salida.getvalue()
                tipo = "image/png"
            except Exception as exc:
                _log_busqueda_empresa(
                    f"LOGO DESCARGA: WEBP recibido pero no convertido; {type(exc).__name__}: {str(exc)[:220]}"
                )
                return None

        if tipo not in ("image/png", "image/jpeg", "image/gif"):
            _log_busqueda_empresa(
                f"LOGO DESCARGA: formato no admitido ({tipo or 'desconocido'}); URL={url_final[:220]}"
            )
            return None
        _log_busqueda_empresa(
            f"LOGO DESCARGA: imagen válida descargada; mime={tipo}; bytes={len(datos_imagen)}; URL={url_final[:260]}"
        )
        return {"url": url_final, "bytes": datos_imagen, "mime": tipo}
    except Exception as exc:
        _log_busqueda_empresa(
            f"LOGO DESCARGA: error descargando {candidato[:220]}: {type(exc).__name__}: {str(exc)[:260]}"
        )
        return None


def _extraer_logo_oficial_desde_sitio(url_sitio, permitir_og_social=False, nombre_empresa=""):
    """Extrae el logo corporativo y descarta imágenes etiquetadas con otra marca."""
    respuesta = requests.get(
        url_sitio,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        timeout=(5, 15), allow_redirects=True
    )
    respuesta.raise_for_status()
    if "text/html" not in respuesta.headers.get("Content-Type", "text/html").lower():
        return None

    contenido = respuesta.text[:4_000_000]
    candidatos = []
    vistos = set()

    def agregar(valor, prioridad=0, origen_logo_confiable=False):
        if not valor:
            return
        valor = html.unescape(str(valor)).strip().strip("\"'()")
        if not valor or valor.startswith(("data:", "javascript:", "blob:")):
            return
        # srcset puede contener descriptor de tamaño; se conserva solo la URL.
        if "," in valor and not valor.lower().startswith(("http://", "https://")):
            valor = valor.split(",", 1)[0].strip().split(" ", 1)[0]
        url = urljoin(respuesta.url, valor)
        partes = urlparse(url)
        if partes.scheme not in ("http", "https"):
            return
        # Evita que un logo de producto (por ejemplo, AMAZON dentro del catálogo
        # de Colombina) sea aceptado como identidad visual de la empresa solicitada.
        if nombre_empresa and not origen_logo_confiable:
            nombre_archivo = partes.path.rsplit("/", 1)[-1]
            nombre_archivo = re.sub(r"([a-z])([A-Z])", r"\1 \2", nombre_archivo)
            tokens_archivo = set(_normalizar_nombre_empresa(nombre_archivo).split())
            tokens_empresa_archivo = {t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5}
            ruido_archivo = {
                "logo", "logos", "logotipo", "brand", "marca", "image", "imagen", "img",
                "png", "jpg", "jpeg", "svg", "webp", "gif", "company", "corporate",
                "col", "ingles", "english", "02", "default", "max", "files", "sites",
                "public", "styles", "desktop", "mobile", "header", "footer", "main",
            }
            distintivos_archivo = tokens_archivo - tokens_empresa_archivo - ruido_archivo
            if distintivos_archivo:
                _log_busqueda_empresa(
                    "LOGO WEB: candidato descartado porque el nombre del archivo identifica otra marca: "
                    + ", ".join(sorted(distintivos_archivo)[:5])
                )
                return
        ruta = (partes.path + " " + partes.query).lower()
        if any(p in ruta for p in ("loader", "loading", "spinner", "placeholder", "tracking-pixel", "banner", "hero", "campaign", "avatar-placeholder")):
            return
        clave = url.split("#", 1)[0]
        if clave not in vistos:
            vistos.add(clave)
            candidatos.append((prioridad, url))

    def atributos(etiqueta):
        salida = {}
        patron = r"([\w:-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))"
        for clave, doble, simple, sin_comillas in re.findall(patron, etiqueta, re.I | re.S):
            salida[clave.lower()] = html.unescape(doble or simple or sin_comillas or "")
        return salida

    # 1) JSON-LD: el atributo logo de Organization/Corporation es la señal más fuerte.
    for bloque in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        contenido, re.I | re.S
    ):
        try:
            datos = json.loads(bloque.strip())
        except Exception:
            continue
        pendientes = datos if isinstance(datos, list) else [datos]
        while pendientes:
            elemento = pendientes.pop(0)
            if isinstance(elemento, dict):
                logo = elemento.get("logo")
                tipo = elemento.get("@type", "")
                tipos = tipo if isinstance(tipo, list) else [tipo]
                if logo and (not tipos or any(any(x in str(t) for x in ("Organization", "Corporation", "BankOrCreditUnion")) for t in tipos)):
                    if isinstance(logo, dict):
                        logo = logo.get("url") or logo.get("contentUrl")
                    if isinstance(logo, list):
                        logo = next((x.get("url") if isinstance(x, dict) else x for x in logo if x), None)
                    if isinstance(logo, str):
                        agregar(logo, 120, origen_logo_confiable=True)
                pendientes.extend(v for v in elemento.values() if isinstance(v, (dict, list)))
            elif isinstance(elemento, list):
                pendientes.extend(elemento)

    # 2) Rel/iconos y metadatos de logo. OG:image solo se permite en perfiles sociales.
    es_social = permitir_og_social and _dominio_es_red_social(respuesta.url)
    for etiqueta in re.findall(r'<(?:meta|link)\b[^>]*>', contenido, re.I):
        attrs = atributos(etiqueta)
        clave = (attrs.get("itemprop") or attrs.get("property") or attrs.get("name") or "").lower()
        rel = attrs.get("rel", "").lower()
        if clave in ("logo", "og:logo", "organization:logo", "twitter:image:src"):
            agregar(attrs.get("content") or attrs.get("href"), 110, origen_logo_confiable=True)
        elif "logo" in rel.split():
            agregar(attrs.get("href"), 108, origen_logo_confiable=True)
        elif "apple-touch-icon" in rel or "mask-icon" in rel:
            agregar(attrs.get("href"), 90)
        elif es_social and clave in ("og:image", "twitter:image"):
            agregar(attrs.get("content"), 85)

    # 3) Recorre todo el HTML, no solo <header>/<nav>: muchos sitios modernos
    # ponen el logotipo en un div, picture, source o componente fuera de esas etiquetas.
    etiquetas_imagen = list(re.finditer(r"<(?:img|source|input|image|object)\b[^>]*>", contenido, re.I))
    for match_tag in etiquetas_imagen:
        etiqueta = match_tag.group(0)
        attrs = atributos(etiqueta)
        src = (attrs.get("data-src") or attrs.get("data-lazy-src") or attrs.get("data-original")
               or attrs.get("data-lazyload") or attrs.get("data-image") or attrs.get("src")
               or attrs.get("href") or attrs.get("data"))
        srcset = attrs.get("srcset") or attrs.get("data-srcset")
        nombre_archivo_imagen = urlparse(src or "").path.rsplit("/", 1)[-1]
        señales = " ".join((attrs.get("alt", ""), attrs.get("title", ""), attrs.get("class", ""),
                            attrs.get("id", ""), attrs.get("aria-label", ""), nombre_archivo_imagen)).lower()
        contexto_tag = contenido[max(0, match_tag.start() - 1800):match_tag.end() + 1000].lower()
        marca_logo_explicita = bool(re.search(
            r"\b(?:logo|logotipo|brand-logo|site-logo|header-brand|navbar-brand|masthead-brand|wordmark|isotipo)\b",
            señales, re.I
        ))
        contexto_cabecera = bool(re.search(
            r"<header\b|site-header|header-brand|navbar-brand|masthead|branding|brand-logo|site-logo",
            contexto_tag, re.I
        ))
        texto_alt_titulo = " ".join((attrs.get("alt", ""), attrs.get("title", ""), attrs.get("aria-label", "")))
        marca_coincide_en_alt = bool(nombre_empresa and texto_alt_titulo and _texto_coincide_empresa(nombre_empresa, texto_alt_titulo))
        contexto_producto = bool(re.search(r"product[-_ ]?(?:card|item|image)|productos?[-_ ]?(?:card|item)|catalogue|catalogo", contexto_tag, re.I))
        # La marca en el ALT o el contexto de cabecera permite aceptar nombres de archivo
        # técnicos/hasheados (por ejemplo, logo-es-<hash>.png) que no repiten la razón social.
        logo_corporativo_explicito = bool(
            marca_logo_explicita and not contexto_producto and
            (contexto_cabecera or marca_coincide_en_alt or
             re.search(r"site[-_ ]?logo|header[-_ ]?logo|corporate[-_ ]?logo|company[-_ ]?logo", señales, re.I))
        )
        if nombre_empresa:
            tokens_empresa = {t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5}
            tokens_senal = set(_normalizar_nombre_empresa(señales).split())
            ruido_senal = {
                "logo", "logotipo", "brand", "marca", "image", "imagen", "img", "header",
                "navbar", "site", "corporate", "identity", "wordmark", "isotipo", "png",
                "jpg", "jpeg", "svg", "webp", "desktop", "mobile", "white", "black",
                "color", "main", "primary", "footer", "menu", "icon", "col", "ingles",
                "english", "02", "es", "en", "logoempresa", "logocol",
            }
            tokens_distintivos = tokens_senal - tokens_empresa - ruido_senal
            # Si ALT/título/archivo identifica otra marca (p. ej. AMAZON),
            # no se usa como logo corporativo de la empresa solicitada.
            if tokens_distintivos and not (tokens_senal & tokens_empresa):
                continue
        if src and logo_corporativo_explicito:
            agregar(src, 132, origen_logo_confiable=True)
        elif src and any(p in señales for p in ("logo", "brand", "marca", "identity", "corporate", "wordmark", "isotipo", "logotipo")):
            agregar(src, 100, origen_logo_confiable=logo_corporativo_explicito)
        elif src and any(p in señales for p in ("site-header", "header-brand", "navbar-brand", "masthead-brand")):
            agregar(src, 82, origen_logo_confiable=True)
        elif src:
            contexto = contenido[max(0, match_tag.start() - 1600):match_tag.end() + 700].lower()
            if re.search(r"<header\b|<nav\b|site-header|navbar|masthead|branding|brand-logo", contexto):
                agregar(src, 72)
        if srcset and any(p in señales for p in ("logo", "brand", "marca", "identity", "corporate", "wordmark", "logotipo")):
            for opcion in srcset.split(","):
                agregar(opcion.strip().split(" ", 1)[0], 98, origen_logo_confiable=logo_corporativo_explicito)

    # 4) SVG inline: busca image href o use href asociados al logotipo.
    for bloque_svg in re.findall(r"<svg\b.*?</svg>", contenido, re.I | re.S):
        if re.search(r"logo|brand|marca|identity|corporate", bloque_svg, re.I):
            for href in re.findall(r"(?:href|xlink:href)\s*=\s*[\"']([^\"']+)[\"']", bloque_svg, re.I):
                if re.search(r"\.(?:svg|png|jpe?g|webp)(?:[?#]|$)", href, re.I):
                    agregar(href, 96)

    # 5) CSS inline de todo el documento, priorizando selectores que mencionen logo/brand.
    for bloque_css in re.findall(r"<style\b[^>]*>(.*?)</style>", contenido, re.I | re.S):
        for selector, urls in re.findall(r"([^{}]+)\{([^{}]*background(?:-image)?\s*:[^{}]+)\}", bloque_css, re.I | re.S):
            selector_marca = bool(re.search(r"logo|brand|marca|identity", selector, re.I))
            prioridad = 112 if selector_marca and re.search(r"header|navbar|masthead|site-brand", selector, re.I) else (92 if selector_marca else 35)
            logo_css_confiable = bool(selector_marca and re.search(r"header|navbar|masthead|site-brand", selector, re.I))
            for imagen_css in re.findall(r"url\((.*?)\)", urls, re.I | re.S):
                agregar(imagen_css.strip(" \t\r\n\"'"), prioridad, origen_logo_confiable=logo_css_confiable)

    # 6) Enlaces directos a archivos de logo y kits de prensa descargables.
    # Muchas empresas publican los logos como enlaces de descarga, no como <img>.
    kit_urls = []
    for match_anchor in re.finditer(r"<a\b[^>]*>.*?</a>", contenido, re.I | re.S):
        anchor = match_anchor.group(0)
        inicio = re.search(r"<a\b[^>]*>", anchor, re.I | re.S)
        if not inicio:
            continue
        attrs = atributos(inicio.group(0))
        href = attrs.get("href", "")
        texto_anchor = _texto_html_limpio(anchor)
        contexto_anchor = contenido[max(0, match_anchor.start() - 900):match_anchor.end() + 300]
        señales = f"{texto_anchor} {href} {attrs.get('title', '')} {contexto_anchor}".lower()
        texto_directo = f"{texto_anchor} {href} {attrs.get('title', '')}".lower()
        hay_logo = any(p in texto_directo for p in ("logo", "logotipo", "brand", "marca", "recursos de marca"))
        hay_kit = (any(p in señales for p in ("kit de prensa", "press kit"))
                   and any(p in texto_directo for p in ("descargar", "download", "kit")))
        if not href or not (hay_logo or hay_kit):
            continue
        href = urljoin(respuesta.url, href)
        ruta = urlparse(href).path.lower()
        if re.search(r"\.(?:png|jpe?g|gif|webp|svg)$", ruta):
            agregar(href, 118)
        elif (re.search(r"\.(?:zip|pptx|pdf)$", ruta) or hay_kit or "recursos de marca" in señales):
            kit_urls.append(href)

    # 7) Kits ZIP: extrae únicamente imágenes cuyo nombre/ruta identifica claramente
    # un logo. Nunca usa fotos genéricas del kit como sustituto del logotipo.
    for kit_url in dict.fromkeys(kit_urls[:5]):
        try:
            kit_r = requests.get(
                kit_url,
                headers={"User-Agent": "Mozilla/5.0", "Referer": respuesta.url},
                timeout=(5, 15), allow_redirects=True
            )
            if not kit_r.ok or len(kit_r.content) > 20_000_000:
                continue
            import zipfile
            buffer_zip = BytesIO(kit_r.content)
            if not zipfile.is_zipfile(buffer_zip):
                # Algunos kits enlazan directamente un archivo de imagen.
                imagen_directa = _descargar_candidato_logo(kit_url, referer=respuesta.url)
                if imagen_directa:
                    return imagen_directa
                continue
            buffer_zip.seek(0)
            with zipfile.ZipFile(buffer_zip) as archivo_zip:
                miembros = [
                    m for m in archivo_zip.namelist()
                    if not m.endswith("/")
                    and re.search(r"\.(?:png|jpe?g|gif|webp|svg)$", m, re.I)
                    and re.search(r"logo|logotipo|brand|marca", m, re.I)
                ]
                for miembro in miembros[:12]:
                    datos_img = archivo_zip.read(miembro)
                    mime_img = ""
                    if datos_img.startswith(b"\x89PNG\r\n\x1a\n"):
                        mime_img = "image/png"
                    elif datos_img.startswith(b"\xff\xd8\xff"):
                        mime_img = "image/jpeg"
                    elif datos_img.startswith((b"GIF87a", b"GIF89a")):
                        mime_img = "image/gif"
                    elif b"<svg" in datos_img[:1500].lower():
                        try:
                            import cairosvg
                            datos_img = cairosvg.svg2png(bytestring=datos_img, output_width=1200)
                            mime_img = "image/png"
                        except Exception:
                            continue
                    elif datos_img[8:12] == b"WEBP":
                        try:
                            from PIL import Image
                            origen = Image.open(BytesIO(datos_img)).convert("RGBA")
                            salida = BytesIO()
                            origen.save(salida, format="PNG")
                            datos_img = salida.getvalue()
                            mime_img = "image/png"
                        except Exception:
                            continue
                    if mime_img and len(datos_img) >= 100:
                        return {"url": kit_url + "#" + miembro, "bytes": datos_img, "mime": mime_img}
        except Exception:
            continue

    # 8) CSS externo enlazado: solo las hojas enlazadas por la propia web.
    css_urls = []
    for etiqueta in re.findall(r"<link\b[^>]*>", contenido, re.I):
        attrs = atributos(etiqueta)
        if "stylesheet" in attrs.get("rel", "").lower() and attrs.get("href"):
            css_urls.append(urljoin(respuesta.url, attrs["href"]))
    for css_url in css_urls[:8]:
        try:
            css_r = requests.get(css_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=(3, 6))
            if not css_r.ok:
                continue
            for selector, urls in re.findall(r"([^{}]+)\{([^{}]*background(?:-image)?\s*:[^{}]+)\}", css_r.text[:1_000_000], re.I | re.S):
                prioridad = 94 if re.search(r"logo|brand|marca|identity", selector, re.I) else 25
                for imagen_css in re.findall(r"url\((.*?)\)", urls, re.I | re.S):
                    agregar(imagen_css.strip(" \t\r\n\"'"), prioridad)
        except Exception:
            continue

    for _, candidato in sorted(candidatos, key=lambda x: -x[0]):
        imagen = _descargar_candidato_logo(candidato, referer=respuesta.url)
        if imagen:
            return imagen
    return None

def _extraer_nombre_de_fila_con_nit(html_pagina, nit):
    """Lee una fila HTML que contiene el NIT y devuelve su celda de razón social."""
    if not html_pagina or not nit:
        return ""
    sufijo_legal = re.compile(
        r"\b(?:S\.?\s*A\.?\s*S\.?|S\.?\s*A\.?\s*E\.?\s*S\.?\s*P\.?|S\.?\s*A\.?|E\.?\s*S\.?\s*P\.?|E\.?\s*I\.?\s*C\.?\s*E\.?|LTDA\.?|LIMITADA|E\.?\s*U\.?|S\.?\s*EN\s*C\.?|S\.?\s*C\.?\s*A\.?)(?=$|[^A-Za-z0-9])",
        re.I
    )
    for fila_html in re.findall(r"<tr\b[^>]*>(.*?)</tr>", str(html_pagina), re.I | re.S):
        texto_fila = _texto_html_limpio(fila_html)
        if not _nit_coincide_con_texto(nit, texto_fila):
            continue
        celdas = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", fila_html, re.I | re.S)
        candidatos = [_texto_html_limpio(celda) for celda in celdas]
        candidatos = [
            c for c in candidatos
            if c and not _nit_coincide_con_texto(nit, c)
            and re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", c)
            and len(_normalizar_nombre_empresa(c).split()) >= 2
        ]
        for candidato in candidatos:
            candidato = re.sub(r"^(?:raz[oó]n\s+social|empresa)\s*[:：-]?\s*", "", candidato, flags=re.I)
            if sufijo_legal.search(candidato):
                return candidato[:180]
        if candidatos:
            # Si la tabla no muestra sufijo legal, la celda de nombre suele ser
            # la segunda después del NIT; se evita escoger estados o categorías.
            for candidato in candidatos:
                if not re.search(r"\b(activa|activo|inactiva|inactivo|cancelada|principal|jur[ií]dica)\b", candidato, re.I):
                    return candidato[:180]
    return ""


def _host_dominio_base(host):
    """Obtiene el dominio registrable aproximado, incluyendo sufijos .com.co y similares."""
    host = str(host or "").lower().split(":", 1)[0].removeprefix("www.").strip(".")
    partes = [p for p in host.split(".") if p]
    if len(partes) >= 3 and ".".join(partes[-2:]) in {"com.co", "org.co", "net.co", "gov.co", "edu.co", "com.mx", "com.ar", "com.br"}:
        return ".".join(partes[-3:])
    return ".".join(partes[-2:]) if len(partes) >= 2 else host


def _dominio_coincide_empresa(url_o_host, nombre_empresa):
    """Comprueba si el dominio registrable contiene una palabra distintiva de la empresa."""
    host = urlparse(url_o_host).netloc if "://" in str(url_o_host) else str(url_o_host)
    base = _host_dominio_base(host)
    etiqueta = base.split(".", 1)[0]
    etiqueta = re.sub(r"[^a-z0-9]", "", etiqueta)
    tokens = [t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5]
    # Solo admite dominio exactamente asociado a la marca o prefijos corporativos
    # habituales (p. ej. grupo+marca); no acepta sufijos engañosos como -secure/login.
    for token in tokens:
        if etiqueta in {token, "grupo" + token, token + "grupo"}:
            return True
        if etiqueta.startswith(token) and len(etiqueta) - len(token) <= 3:
            return True
    return False


def _pertenece_a_dominio_verificado(url_o_host, dominios):
    host = urlparse(url_o_host).netloc if "://" in str(url_o_host) else str(url_o_host)
    host = host.lower().removeprefix("www.")
    for dominio in dominios or []:
        d = _host_dominio_base(dominio)
        if host == d or host.endswith("." + d) or _host_dominio_base(host) == d:
            return True
    return False


def _obtener_atributos_html(tag):
    attrs = {}
    for clave, doble, simple, sin_comillas in re.findall(
        r"([\w:-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", tag, re.I | re.S
    ):
        attrs[clave.lower()] = html.unescape(doble or simple or sin_comillas or "")
    return attrs


def _buscar_logo_en_bing_images(nombre_empresa, dominios_corporativos):
    """Busca logos en Bing Images y solo descarga resultados originados en dominios corporativos identificados."""
    dominios = {_host_dominio_base(d) for d in (dominios_corporativos or []) if d}
    if not dominios:
        return None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    consultas = [f'"{nombre_empresa}" logo Colombia', f'"{nombre_empresa}" logotipo oficial']
    for dominio in sorted(dominios):
        consultas.append(f'"{nombre_empresa}" logo site:{dominio}')
    vistos = set()
    for consulta in consultas:
        try:
            respuesta = requests.get(
                "https://www.bing.com/images/search",
                params={"q": consulta, "form": "HDRSC3", "first": "1"},
                headers=headers, timeout=(5, 14)
            )
            respuesta.raise_for_status()
        except Exception:
            continue

        etiquetas = re.findall(r"<a\b[^>]*class=[\"'][^\"']*\biusc\b[^\"']*[\"'][^>]*>", respuesta.text, re.I | re.S)
        for etiqueta in etiquetas:
            attrs = _obtener_atributos_html(etiqueta)
            meta = attrs.get("m", "")
            if not meta:
                continue
            try:
                datos = json.loads(html.unescape(meta))
            except Exception:
                continue
            pagina_origen = datos.get("purl", "") or datos.get("purl2", "")
            imagen_url = datos.get("murl", "")
            titulo = _celda_texto(datos.get("t", ""))
            if not pagina_origen or not imagen_url or not _pertenece_a_dominio_verificado(pagina_origen, dominios):
                continue
            tokens_empresa = [t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5]
            texto_archivo = _normalizar_nombre_empresa(
                urlparse(imagen_url).path.replace("/", " ").replace("-", " ").replace("_", " ")
            )
            coincide_titulo = bool(titulo and _texto_coincide_empresa(nombre_empresa, titulo))
            coincide_archivo = bool(tokens_empresa and any(t in texto_archivo.split() for t in tokens_empresa))
            # El dominio de origen no basta: impide aceptar marcas de producto
            # como si fueran el logotipo institucional de la empresa.
            if not (coincide_titulo or coincide_archivo):
                continue
            if re.search(r"\.pdf(?:$|[?#])", pagina_origen, re.I):
                continue
            clave = (imagen_url, pagina_origen)
            if clave in vistos:
                continue
            vistos.add(clave)
            imagen = _descargar_candidato_logo(imagen_url, referer=pagina_origen)
            if imagen:
                return imagen, pagina_origen

    # Respaldo: API JSON de DuckDuckGo Images. Su estructura no depende del HTML de Bing.
    for consulta in consultas:
        try:
            pagina = requests.get(
                "https://duckduckgo.com/",
                params={"q": consulta, "iax": "images", "ia": "images"},
                headers=headers, timeout=(5, 12)
            )
            pagina.raise_for_status()
            vqd_match = (re.search(r"vqd=([\"'])(.*?)\1", pagina.text, re.I)
                         or re.search(r"\bvqd\s*[:=]\s*[\"']([^\"']+)", pagina.text, re.I))
            if not vqd_match:
                continue
            vqd = vqd_match.group(2) if vqd_match.lastindex == 2 else vqd_match.group(1)
            datos_r = requests.get(
                "https://duckduckgo.com/i.js",
                params={"l": "us-en", "o": "json", "q": consulta, "vqd": vqd, "f": ",,,,"},
                headers={**headers, "Referer": pagina.url}, timeout=(5, 14)
            )
            datos_r.raise_for_status()
            resultados = datos_r.json().get("results", [])
        except Exception:
            continue
        for item in resultados[:60]:
            pagina_origen = item.get("url", "") or item.get("source", "")
            imagen_url = item.get("image", "")
            titulo = _celda_texto(item.get("title", ""))
            if not pagina_origen or not imagen_url or not _pertenece_a_dominio_verificado(pagina_origen, dominios):
                continue
            tokens_empresa = [t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5]
            texto_archivo = _normalizar_nombre_empresa(
                urlparse(imagen_url).path.replace("/", " ").replace("-", " ").replace("_", " ")
            )
            coincide_titulo = bool(titulo and _texto_coincide_empresa(nombre_empresa, titulo))
            coincide_archivo = bool(tokens_empresa and any(t in texto_archivo.split() for t in tokens_empresa))
            if not (coincide_titulo or coincide_archivo):
                continue
            if re.search(r"\.pdf(?:$|[?#])", pagina_origen, re.I):
                continue
            imagen = _descargar_candidato_logo(imagen_url, referer=pagina_origen)
            if imagen:
                return imagen, pagina_origen
    return None



def _tokens_distintivos_empresa_logo(nombre_empresa):
    # Tokens de marca, sin sufijos legales ni términos genéricos.
    ignorar = {
        "grupo", "empresa", "empresas", "compania", "nacional", "sociedad",
        "anonima", "sas", "sa", "s", "a", "bic", "ltda", "limitada",
        "esp", "e", "u", "eu", "de", "del", "la", "el", "los", "las",
        "y", "and", "the", "colombia", "colombiana",
    }
    return [t for t in _normalizar_nombre_empresa(nombre_empresa).split()
            if len(t) >= 4 and t not in ignorar]


def _procolombia_url_coincide_nombre(url, nombre_empresa):
    parsed = urlparse(str(url or ""))
    host = parsed.netloc.lower().removeprefix("www.")
    if host not in {"b2bmarketplace.procolombia.co", "b2bmarketplaceplus.procolombia.co"}:
        return False
    path = unquote(parsed.path or "")
    if not re.search(r"\.aspx$", path, re.I):
        return False
    if re.search(r"/(search|user|login|node)(/|$)", path, re.I):
        return False
    tokens_empresa = set(_tokens_distintivos_empresa_logo(nombre_empresa))
    tokens_ruta = set(_normalizar_nombre_empresa(path).split())
    coincidencias = tokens_empresa & tokens_ruta
    if not coincidencias:
        return False
    minimo = 1 if len(tokens_empresa) <= 2 else 2
    return len(coincidencias) >= minimo


def _extraer_perfiles_procolombia_robusto(html_busqueda, url_base, nombre_empresa):
    # Lee href/data-href y URLs dentro de JSON/JavaScript, además del HTMLParser existente.
    texto = html.unescape(str(html_busqueda or ""))
    texto = (texto.replace(r"\/", "/").replace(r"\u002F", "/")
                  .replace(r"\u003A", ":").replace(r"\u0026", "&"))
    candidatos = set()
    patron_atributos = re.compile(r"(?:href|data-href|data-url|data-link)\s*=\s*[\"']([^\"']+)[\"']", re.I | re.S)
    for m in patron_atributos.finditer(texto):
        candidatos.add(html.unescape(m.group(1).strip()))
    patron_absoluto = re.compile(r"(?:https?:)?//b2bmarketplace(?:plus)?\.procolombia\.co/(?:es|en)/[^\s\"'<>\\]+?\.aspx(?:\?[^\s\"'<>\\]*)?", re.I)
    for m in patron_absoluto.finditer(texto):
        candidatos.add(m.group(0))
    patron_relativo = re.compile(r"/(?:es|en)/[^\s\"'<>\\]+?\.aspx(?:\?[^\s\"'<>\\]*)?", re.I)
    for m in patron_relativo.finditer(texto):
        candidatos.add(m.group(0))

    resultados, vistos = [], set()
    for candidato in candidatos:
        candidato = candidato.strip().rstrip("),;]")
        url = urljoin(url_base, candidato)
        if not _procolombia_url_coincide_nombre(url, nombre_empresa):
            continue
        clave = url.split("?", 1)[0].rstrip("/").lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        slug = unquote(urlparse(url).path.rsplit("/", 1)[-1]).replace(".aspx", "")
        resultados.append({"url": url, "titulo": slug.replace("-", " ").title(),
                           "snippet": "Perfil extraído del HTML/JSON del directorio ProColombia"})
    return resultados


def _buscar_perfiles_procolombia_en_sitemap(nombre_empresa):
    # Índice de perfiles independiente de los buscadores web.
    sitemap_base = "https://b2bmarketplace.procolombia.co/sitemap.xml"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CesantiasAlInstante/6.0)",
               "Accept": "application/xml,text/xml,*/*;q=0.8"}
    try:
        resp = requests.get(sitemap_base, headers=headers, timeout=(6, 12), allow_redirects=True)
        _log_busqueda_empresa(f"LOGO ProColombia sitemap: HTTP {resp.status_code}; bytes={len(resp.content)}.")
        if not resp.ok or "xml" not in resp.headers.get("Content-Type", "").lower():
            return []
        locs = re.findall(r"<loc[^>]*>\s*(.*?)\s*</loc>", resp.text, re.I | re.S)
    except Exception as exc:
        _log_busqueda_empresa(f"LOGO ProColombia sitemap: error {type(exc).__name__}: {str(exc)[:180]}")
        return []

    urls, hijos = [], []
    for raw in locs:
        u = html.unescape(raw.strip())
        if u.lower().endswith(".xml") or "sitemap" in urlparse(u).path.lower():
            hijos.append(u)
        else:
            urls.append(u)
    for hijo_url in hijos[:12]:
        try:
            hijo = requests.get(hijo_url, headers=headers, timeout=(6, 12), allow_redirects=True)
            if hijo.ok and "xml" in hijo.headers.get("Content-Type", "").lower():
                urls.extend(html.unescape(x.strip()) for x in re.findall(r"<loc[^>]*>\s*(.*?)\s*</loc>", hijo.text, re.I | re.S))
        except Exception as exc:
            _log_busqueda_empresa(f"LOGO ProColombia sitemap hijo: {type(exc).__name__}: {str(exc)[:140]}")

    resultados, vistos = [], set()
    for u in urls:
        if not _procolombia_url_coincide_nombre(u, nombre_empresa):
            continue
        clave = u.split("?", 1)[0].rstrip("/").lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        slug = unquote(urlparse(u).path.rsplit("/", 1)[-1]).replace(".aspx", "")
        resultados.append({"url": u, "titulo": slug.replace("-", " ").title(),
                           "snippet": "Perfil localizado en sitemap oficial ProColombia"})
    _log_busqueda_empresa(f"LOGO ProColombia sitemap: {len(resultados)} perfiles que coinciden con {nombre_empresa}.")
    return resultados


def _prioridad_imagen_procolombia(url_imagen, senales, nombre_empresa, nit_empresa):
    # Si el NIT exacto aparece en la ruta de la imagen, es la señal más fuerte.
    nit_base = _clave_nit(nit_empresa)
    if nit_base and nit_base in _normalizar_nit(url_imagen):
        return 260
    tokens_empresa = {t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5}
    tokens_senales = set(_normalizar_nombre_empresa(senales).split())
    ruido = {"logo", "logos", "logotipo", "brand", "marca", "image", "imagen", "img",
             "company", "corporate", "col", "ingles", "english", "public", "companies",
             "sites", "files", "styles", "png", "jpg", "jpeg", "svg", "webp", "02",
             "max", "325x325", "default", "es", "en", "empresaid"}
    distintivos = tokens_senales - tokens_empresa - ruido
    if distintivos and not (tokens_senales & tokens_empresa):
        return 0
    texto = " ".join((str(senales or ""), str(url_imagen or ""))).lower()
    if any(x in texto for x in ("logo", "logotipo", "brand")):
        return 150 if (tokens_senales & tokens_empresa) else 130
    return 0


def _logoapi_resultado_coincide(nombre_empresa, dominio_oficial, item):
    # No acepta fuzzy, dominios aproximados ni nombres de otra marca.
    if not isinstance(item, dict) or item.get("fuzzy") is True:
        return False
    esperado = _host_dominio_base(dominio_oficial)
    dominio = _host_dominio_base(item.get("domain", ""))
    if not esperado or dominio != esperado:
        return False
    tokens_empresa = set(_tokens_distintivos_empresa_logo(nombre_empresa))
    tokens_api = set(_tokens_distintivos_empresa_logo(str(item.get("name", ""))))
    if not tokens_empresa or not (tokens_empresa & tokens_api):
        return False
    host_fuente = _host_dominio_base(urlparse(str(item.get("source", ""))).netloc)
    return host_fuente == esperado


def _validar_png_logoapi(respuesta):
    # fallback=404 y X-Logo-Fallback impiden que un favicon o mosaico pase como logo.
    try:
        if not getattr(respuesta, "ok", False):
            return None
        headers = getattr(respuesta, "headers", {}) or {}
        if headers.get("X-Logo-Fallback"):
            return None
        tipo = headers.get("Content-Type", "").lower().split(";", 1)[0].strip()
        datos = bytes(getattr(respuesta, "content", b""))
        if tipo != "image/png" or not datos.startswith(b"\x89PNG\r\n\x1a\n") or len(datos) < 500 or len(datos) > 5_000_000:
            return None
        import struct
        if len(datos) < 24:
            return None
        ancho, alto = struct.unpack(">II", datos[16:24])
        if ancho < 64 or alto < 32 or ancho > 5000 or alto > 5000:
            return None
        return {"url": getattr(respuesta, "url", ""), "bytes": datos, "mime": "image/png"}
    except Exception:
        return None


def _buscar_logo_logoapi(nombre_empresa, dominios_verificados):
    # Catálogo auxiliar: coincidencia de nombre + dominio y PNG sin fallback.
    for dominio_bruto in dominios_verificados or []:
        dominio = _host_dominio_base(dominio_bruto)
        if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", dominio or ""):
            continue
        try:
            busqueda = requests.get("https://logoapi.sh/search", params={"q": dominio},
                headers={"User-Agent": "CesantiasAlInstante/6.0", "Accept": "application/json"},
                timeout=(5, 10), allow_redirects=True)
            _log_busqueda_empresa(f"LOGO API: búsqueda de dominio {dominio}; HTTP {busqueda.status_code}.")
            if not busqueda.ok:
                continue
            payload = busqueda.json()
            items = payload.get("results", []) if isinstance(payload, dict) else []
            coincidencias = [x for x in items if _logoapi_resultado_coincide(nombre_empresa, dominio, x)]
            if not coincidencias:
                _log_busqueda_empresa(f"LOGO API: sin coincidencia exacta de marca y dominio para {dominio}.")
                continue
            item = sorted(coincidencias, key=lambda x: (bool(x.get("wordmark")), int(x.get("score", 0))), reverse=True)[0]
            url_png = f"https://logoapi.sh/{dominio}.png?size=512&bg=white&fallback=404"
            imagen = requests.get(url_png, headers={"User-Agent": "CesantiasAlInstante/6.0", "Accept": "image/png"},
                                  timeout=(5, 15), allow_redirects=True)
            validada = _validar_png_logoapi(imagen)
            if validada:
                _log_busqueda_empresa(f"LOGO API: PNG corporativo validado para {nombre_empresa} ({dominio}); bytes={len(validada['bytes'])}.")
                return validada, f"https://logoapi.sh/brand/{dominio}"
            _log_busqueda_empresa(f"LOGO API: PNG rechazado para {dominio}; HTTP={imagen.status_code}; fallback={imagen.headers.get('X-Logo-Fallback', '')}.")
        except Exception as exc:
            _log_busqueda_empresa(f"LOGO API: error con {dominio}: {type(exc).__name__}: {str(exc)[:180]}")
    return None


def _buscar_logo_en_directorio_procolombia(nombre_empresa, nit_empresa):
    """Busca el perfil B2B de ProColombia y obtiene su imagen de empresa.

    El sitio actual no siempre publica el NIT en el HTML visible. En ese caso,
    exige coincidencia del nombre legal y un enlace a la web corporativa. La
    identidad/NIT ya debe venir validada por la fuente registral anterior.
    """
    nit_base = _clave_nit(nit_empresa)
    if not nombre_empresa:
        _log_busqueda_empresa("LOGO ProColombia: omitido; falta nombre legal.")
        return None

    dominios_procolombia = {
        "b2bmarketplace.procolombia.co",
        "b2bmarketplaceplus.procolombia.co",
    }
    consultas = [
        f'site:b2bmarketplace.procolombia.co "{nombre_empresa}"',
        f'site:b2bmarketplace.procolombia.co "{nombre_empresa}" "logo"',
        f'site:b2bmarketplace.procolombia.co "{nombre_empresa}" "Company"',
    ]
    if nit_base:
        consultas.extend([
            f'site:b2bmarketplaceplus.procolombia.co "{nombre_empresa}" "{nit_base}"',
            f'site:b2bmarketplaceplus.procolombia.co "{nit_base}"',
        ])
    paginas_vistas = set()
    # Primera vía: buscador propio del B2B Marketplace de ProColombia.
    # Su formulario público utiliza /es/search o /en/search y el parámetro query=.
    for ruta_busqueda in (
        "https://b2bmarketplace.procolombia.co/es/search",
        "https://b2bmarketplace.procolombia.co/en/search",
    ):
        try:
            respuesta_busqueda = requests.get(
                ruta_busqueda,
                params={"query": nombre_empresa, "tariff": ""},
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                },
                timeout=(8, 18), allow_redirects=True,
            )
            _log_busqueda_empresa(
                f"LOGO ProColombia directo: {ruta_busqueda.rsplit('/',1)[-1]} HTTP {respuesta_busqueda.status_code}; "
                f"bytes={len(respuesta_busqueda.content)}; URL={respuesta_busqueda.url[:280]}."
            )
            if respuesta_busqueda.ok and "text/html" in respuesta_busqueda.headers.get("Content-Type", "text/html").lower():
                html_busqueda = respuesta_busqueda.text[:5_000_000]
                items_directos = _extraer_enlaces_con_titulo_html(html_busqueda, respuesta_busqueda.url)
                # El parser original no siempre reconoce tarjetas Drupal/JS.
                items_robustos = _extraer_perfiles_procolombia_robusto(html_busqueda, respuesta_busqueda.url, nombre_empresa)
                for item_robusto in items_robustos:
                    if item_robusto.get("url") not in {x.get("url") for x in items_directos}:
                        items_directos.append(item_robusto)
                # Si el buscador interno no devuelve tarjetas, usar el sitemap oficial.
                if not any(_procolombia_url_coincide_nombre(x.get("url", ""), nombre_empresa) for x in items_directos):
                    for item_sitemap in _buscar_perfiles_procolombia_en_sitemap(nombre_empresa):
                        if item_sitemap.get("url") not in {x.get("url") for x in items_directos}:
                            items_directos.append(item_sitemap)
                # El perfil empresarial puede tener rutas anidadas, por ejemplo:
                # /es/agroindustria/agroindustrial/colombina-sa.aspx.
                # No se debe asumir que el nombre está en el segundo segmento ni
                # que la ruta termina en un ID numérico.
                tokens_nombre = [t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 4]
                enlaces_directos_vistos = {
                    (item.get("url", "") or "").split("?", 1)[0].rstrip("/").lower()
                    for item in items_directos
                }
                for item_enlace in list(items_directos):
                    url_raw = item_enlace.get("url", "")
                    host_raw = urlparse(url_raw).netloc.lower().removeprefix("www.")
                    if host_raw not in dominios_procolombia:
                        continue
                    partes_raw = [unquote(p) for p in urlparse(url_raw).path.split("/") if p]
                    if not partes_raw or partes_raw[0].lower() not in ("es", "en"):
                        continue
                    ruta_normalizada = _normalizar_nombre_empresa(" ".join(partes_raw[1:]))
                    titulo_raw = item_enlace.get("titulo", "") or item_enlace.get("snippet", "")
                    nombre_en_ruta = any(t in set(ruta_normalizada.split()) for t in tokens_nombre)
                    nombre_en_titulo = _texto_coincide_empresa(nombre_empresa, titulo_raw)
                    # Acepta rutas de ficha con cualquier profundidad siempre que
                    # el nombre distintivo aparezca en el slug o en el título.
                    parece_ficha = (
                        nombre_en_ruta
                        or (nombre_en_titulo and len(partes_raw) >= 3)
                        or bool(re.search(r"-\d+$", partes_raw[-1]))
                    )
                    if parece_ficha:
                        clave_url = url_raw.split("?", 1)[0].rstrip("/").lower()
                        if clave_url not in enlaces_directos_vistos:
                            enlaces_directos_vistos.add(clave_url)
                            items_directos.append({
                                "url": url_raw,
                                "titulo": titulo_raw or " ".join(partes_raw[-2:]),
                                "snippet": item_enlace.get("snippet", ""),
                            })
                # Segunda pasada explícita con HTMLParser: recoge enlaces aunque
                # el título esté en un elemento hermano del anchor o el HTML tenga
                # atributos en distinto orden. El helper ya resuelve entidades HTML.
                for item_enlace in _extraer_enlaces_con_titulo_html(html_busqueda, respuesta_busqueda.url):
                    url_raw = item_enlace.get("url", "")
                    host_raw = urlparse(url_raw).netloc.lower().removeprefix("www.")
                    if host_raw not in dominios_procolombia:
                        continue
                    partes_raw = [unquote(p) for p in urlparse(url_raw).path.split("/") if p]
                    if not partes_raw or partes_raw[0].lower() not in ("es", "en"):
                        continue
                    ruta_normalizada = _normalizar_nombre_empresa(" ".join(partes_raw[1:]))
                    texto_candidato = " ".join((item_enlace.get("titulo", ""), item_enlace.get("snippet", ""), ruta_normalizada))
                    if not any(t in set(ruta_normalizada.split()) for t in tokens_nombre) and not _texto_coincide_empresa(nombre_empresa, texto_candidato):
                        continue
                    clave_url = url_raw.split("?", 1)[0].rstrip("/").lower()
                    if clave_url not in enlaces_directos_vistos:
                        enlaces_directos_vistos.add(clave_url)
                        items_directos.append(item_enlace)
                for item_directo in items_directos:
                    host_directo = urlparse(item_directo.get("url", "")).netloc.lower().removeprefix("www.")
                    titulo_directo = item_directo.get("titulo", "")
                    if host_directo not in dominios_procolombia:
                        continue
                    url_directa = item_directo.get("url", "")
                    ruta_directa = _normalizar_nombre_empresa(unquote(urlparse(url_directa).path))
                    texto_identidad_candidato = " ".join((titulo_directo, item_directo.get("snippet", ""), ruta_directa))
                    if not _texto_coincide_empresa(nombre_empresa, texto_identidad_candidato) and not _procolombia_url_coincide_nombre(url_directa, nombre_empresa):
                        continue
                    clave_directa = url_directa.split("?", 1)[0].rstrip("/").lower()
                    if clave_directa not in paginas_vistas:
                        paginas_vistas.add(clave_directa)
                        _log_busqueda_empresa(
                            f"LOGO ProColombia directo: candidato de ficha encontrado: "
                            f"{titulo_directo[:150]} | {url_directa[:280]}"
                        )
                        consultas_directas = [{"url": url_directa, "titulo": titulo_directo, "snippet": item_directo.get("snippet", "")}]
                        # Inyecta la página encontrada en el mismo procesamiento de fichas.
                        for item in consultas_directas:
                            url_pagina = item.get("url", "")
                            try:
                                pagina = requests.get(
                                    url_pagina,
                                    headers={"User-Agent": "Mozilla/5.0 (compatible; CesantiasAlInstante/5.4)",
                                             "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
                                    timeout=(8, 18), allow_redirects=True,
                                )
                                if not pagina.ok or "text/html" not in pagina.headers.get("Content-Type", "text/html").lower():
                                    continue
                                html_pagina = pagina.text[:5_000_000]
                                texto_pagina = _texto_html_limpio(html_pagina)
                                if not _texto_coincide_empresa(nombre_empresa, texto_pagina):
                                    continue
                                nit_coincide = bool(nit_base and _nit_coincide_con_texto(nit_empresa, texto_pagina))
                                enlaces_externos = []
                                for enlace in _extraer_enlaces_con_titulo_html(html_pagina, pagina.url):
                                    host_enlace = urlparse(enlace.get("url", "")).netloc.lower().removeprefix("www.")
                                    if host_enlace and host_enlace not in dominios_procolombia and not any(
                                        red in host_enlace for red in ("facebook.com", "instagram.com", "linkedin.com", "youtube.com", "x.com")
                                    ):
                                        enlaces_externos.append(enlace["url"])
                                web_coincide = any(_dominio_coincide_empresa(enlace, nombre_empresa) for enlace in enlaces_externos)
                                if not nit_coincide and not web_coincide:
                                    continue
                                candidatos = []
                                # Primero conserva las imágenes declaradas por etiquetas <img>.
                                for match_img in re.finditer(r"<img\b[^>]*>", html_pagina, re.I | re.S):
                                    attrs_img = _obtener_atributos_html(match_img.group(0))
                                    src_img = (attrs_img.get("data-src") or attrs_img.get("data-original") or attrs_img.get("data-lazy-src") or attrs_img.get("src") or "").strip()
                                    if not src_img:
                                        continue
                                    url_img = urljoin(pagina.url, src_img)
                                    filename = urlparse(url_img).path.rsplit("/", 1)[-1]
                                    senales_img = " ".join((attrs_img.get("alt", ""), attrs_img.get("title", ""), attrs_img.get("class", ""), attrs_img.get("id", ""), filename))
                                    prioridad_img = _prioridad_imagen_procolombia(url_img, senales_img, nombre_empresa, nit_empresa)
                                    if prioridad_img:
                                        candidatos.append((prioridad_img, url_img))
                                    else:
                                        _log_busqueda_empresa("LOGO ProColombia directo: imagen descartada; no coincide el NIT ni la marca: " + url_img[:240])
                                # Algunas fichas publican el logo como enlace de imagen
                                # y el parser de <img> no recibe el href original.
                                for enlace_img in _extraer_enlaces_con_titulo_html(html_pagina, pagina.url):
                                    url_img = enlace_img.get("url", "")
                                    path_img = urlparse(url_img).path.lower()
                                    if not re.search(r"\.(?:png|jpe?g|gif|webp|svg)(?:[?#].*)?$", path_img):
                                        continue
                                    nombre_img = path_img.rsplit("/", 1)[-1]
                                    prioridad_href = _prioridad_imagen_procolombia(url_img, nombre_img, nombre_empresa, nit_empresa)
                                    if prioridad_href:
                                        candidatos.append((prioridad_href, url_img))
                                candidatos.sort(key=lambda x: x[0], reverse=True)
                                for prioridad, url_img in candidatos:
                                    imagen = _descargar_candidato_logo(url_img, referer=pagina.url)
                                    if imagen:
                                        _log_busqueda_empresa(
                                            f"LOGO ProColombia directo: logo descargado; prioridad={prioridad}; "
                                            f"URL={url_img[:280]}; bytes={len(imagen['bytes'])}."
                                        )
                                        return imagen, pagina.url
                            except Exception as exc:
                                _log_busqueda_empresa(f"LOGO ProColombia directo: error leyendo ficha: {type(exc).__name__}: {str(exc)[:220]}")
        except Exception as exc:
            _log_busqueda_empresa(f"LOGO ProColombia directo: error consultando {ruta_busqueda}: {type(exc).__name__}: {str(exc)[:220]}")

    # Segunda vía: buscadores externos por si el índice interno no devuelve la ficha.
    for consulta in consultas:
        try:
            resultados = _buscar_resultados_empresa(consulta, max_resultados=10)
        except Exception as exc:
            _log_busqueda_empresa(
                f"LOGO ProColombia: error buscando ficha: {type(exc).__name__}: {str(exc)[:220]}"
            )
            continue
        _log_busqueda_empresa(
            f"LOGO ProColombia: consulta devolvió {len(resultados)} resultados candidatos "
            "después de resolver redirecciones de Google/Bing."
        )
        for item in resultados:
            url_pagina = item.get("url", "")
            host = urlparse(url_pagina).netloc.lower().removeprefix("www.")
            if host not in dominios_procolombia:
                continue
            clave = url_pagina.split("?")[0].rstrip("/").lower()
            if clave in paginas_vistas:
                continue
            paginas_vistas.add(clave)
            try:
                pagina = requests.get(
                    url_pagina,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; CesantiasAlInstante/5.2)",
                        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                    },
                    timeout=(8, 18), allow_redirects=True,
                )
                _log_busqueda_empresa(
                    f"LOGO ProColombia: ficha HTTP {pagina.status_code}; URL={pagina.url[:260]}; "
                    f"content-type={pagina.headers.get('Content-Type', '')}; bytes={len(pagina.content)}."
                )
                if not pagina.ok or "text/html" not in pagina.headers.get("Content-Type", "text/html").lower():
                    continue
                html_pagina = pagina.text[:5_000_000]
                texto_pagina = _texto_html_limpio(html_pagina)
                if not _texto_coincide_empresa(nombre_empresa, texto_pagina):
                    _log_busqueda_empresa("LOGO ProColombia: ficha descartada; no coincide el nombre empresarial.")
                    continue

                coincide_nit = bool(nit_base and _nit_coincide_con_texto(nit_empresa, texto_pagina))
                enlaces_externos = []
                for match_a in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>", html_pagina, re.I | re.S):
                    href = urljoin(pagina.url, html.unescape(match_a.group(1)))
                    host_href = urlparse(href).netloc.lower().removeprefix("www.")
                    if not host_href or host_href in dominios_procolombia:
                        continue
                    if any(x in host_href for x in ("facebook.com", "instagram.com", "linkedin.com", "youtube.com", "x.com")):
                        continue
                    enlaces_externos.append(href)
                web_coincidente = any(
                    _dominio_coincide_empresa(href, nombre_empresa)
                    for href in enlaces_externos
                )
                if not coincide_nit and not web_coincidente:
                    _log_busqueda_empresa(
                        "LOGO ProColombia: ficha descartada; no contiene el NIT y tampoco enlaza "
                        "una web corporativa coherente con el nombre legal."
                    )
                    continue
                _log_busqueda_empresa(
                    "LOGO ProColombia: identidad de ficha confirmada por "
                    + ("NIT + nombre legal." if coincide_nit else "nombre legal + web corporativa enlazada (ficha actual sin NIT visible).")
                )

                candidatos = []
                for match in re.finditer(r"<img\b[^>]*>", html_pagina, re.I | re.S):
                    attrs = _obtener_atributos_html(match.group(0))
                    src = (attrs.get("data-src") or attrs.get("data-original") or
                           attrs.get("data-lazy-src") or attrs.get("src") or "").strip()
                    if not src:
                        continue
                    url_imagen = urljoin(pagina.url, src)
                    path_digitos = _normalizar_nit(url_imagen)
                    nombre_archivo_imagen = urlparse(src).path.rsplit("/", 1)[-1]
                    señales = " ".join((attrs.get("alt", ""), attrs.get("title", ""),
                                        attrs.get("class", ""), attrs.get("id", ""), nombre_archivo_imagen)).lower()
                    tokens_empresa = {t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5}
                    tokens_senal = set(_normalizar_nombre_empresa(señales).split())
                    ruido_senal = {
                        "logo", "logotipo", "brand", "marca", "image", "imagen", "img", "company",
                        "corporate", "col", "ingles", "english", "public", "companies", "sites",
                        "files", "styles", "png", "jpg", "jpeg", "svg", "webp", "02", "max",
                        "325x325", "default", "col", "ingles", "english",
                    }
                    nit_en_url_imagen = bool(nit_base and nit_base in _normalizar_nit(url_imagen))
                    distintivos = tokens_senal - tokens_empresa - ruido_senal
                    if distintivos and not (tokens_senal & tokens_empresa) and not nit_en_url_imagen:
                        _log_busqueda_empresa(
                            "LOGO ProColombia: imagen descartada por identificar otra marca "
                            f"({', '.join(sorted(distintivos)[:5])})."
                        )
                        continue
                    contexto = html_pagina[max(0, match.start()-2200):match.end()+2200]
                    contexto_txt = _texto_html_limpio(contexto)
                    score = 0
                    if nit_en_url_imagen:
                        score = 260
                    elif "empresaid" in src.lower() and nit_base in path_digitos:
                        score = 140
                    elif nit_base in path_digitos:
                        score = 125
                    elif any(x in señales for x in ("logo", "logotipo", "brand-logo", "company-logo")):
                        score = 125
                    elif any(x in señales for x in ("logo", "logotipo", "brand")):
                        score = 110
                    if score:
                        candidatos.append((score, url_imagen))

                # También revisa enlaces directos a imágenes si la etiqueta img
                # está envuelta en un anchor.
                for match in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>", html_pagina, re.I | re.S):
                    href = urljoin(pagina.url, html.unescape(match.group(1)))
                    if re.search(r"\.(?:png|jpe?g|gif|webp|svg)(?:[?#]|$)", href, re.I):
                        digitos = _normalizar_nit(href)
                        archivo_href = urlparse(href).path.rsplit("/", 1)[-1]
                        tokens_href = set(_normalizar_nombre_empresa(archivo_href).split())
                        tokens_empresa_href = {t for t in _clave_nombre_empresa(nombre_empresa).split() if len(t) >= 5}
                        ruido_href = {"logo", "logos", "logotipo", "brand", "png", "jpg", "jpeg", "svg", "webp", "col", "ingles", "english", "02", "default", "max", "325x325", "styles", "sites", "files", "public"}
                        nit_en_href = bool(nit_base and nit_base in _normalizar_nit(href))
                        distintivos_href = tokens_href - tokens_empresa_href - ruido_href
                        marca_ajena = bool(distintivos_href and not (tokens_href & tokens_empresa_href))
                        if nit_en_href:
                            candidatos.append((260, href))
                        elif marca_ajena:
                            _log_busqueda_empresa(
                                "LOGO ProColombia: enlace de imagen descartado por marca ajena: "
                                + ", ".join(sorted(distintivos_href)[:5])
                            )
                        elif "logo" in urlparse(href).path.lower():
                            candidatos.append((125, href))

                candidatos.sort(key=lambda x: x[0], reverse=True)
                _log_busqueda_empresa(
                    f"LOGO ProColombia: ficha confirmada para {nombre_empresa}; "
                    f"{len(candidatos)} imágenes candidatas."
                )
                vistos_img = set()
                for prioridad, url_imagen in candidatos[:20]:
                    if url_imagen in vistos_img:
                        continue
                    vistos_img.add(url_imagen)
                    _log_busqueda_empresa(
                        f"LOGO ProColombia: probando imagen prioridad={prioridad}: {url_imagen[:300]}"
                    )
                    imagen = _descargar_candidato_logo(url_imagen, referer=pagina.url)
                    if imagen:
                        _log_busqueda_empresa(
                            f"LOGO ProColombia: imagen descargada correctamente ({imagen['mime']}, "
                            f"{len(imagen['bytes'])} bytes)."
                        )
                        return imagen, pagina.url
                _log_busqueda_empresa("LOGO ProColombia: la ficha coincide, pero sus imágenes no pudieron descargarse como imagen válida.")
            except Exception as exc:
                _log_busqueda_empresa(
                    f"LOGO ProColombia: error leyendo ficha: {type(exc).__name__}: {str(exc)[:240]}"
                )
    _log_busqueda_empresa("LOGO ProColombia: no se encontró una ficha con NIT y nombre coincidentes.")
    return None


def _buscar_icono_dominio_corporativo(dominios):
    """Último respaldo: favicon de alta resolución del dominio oficial ya identificado."""
    for dominio in sorted({_host_dominio_base(d) for d in (dominios or []) if d}):
        urls = [
            f"https://www.google.com/s2/favicons?domain_url=https://{dominio}&sz=256",
            f"https://{dominio}/favicon.ico",
        ]
        for url in urls:
            imagen = _descargar_candidato_logo(url, referer=f"https://{dominio}/")
            if not imagen:
                continue
            try:
                from PIL import Image
                imagen_pil = Image.open(BytesIO(imagen["bytes"]))
                ancho, alto = imagen_pil.size
                if min(ancho, alto) < 64:
                    continue
                if imagen_pil.format not in ("PNG", "JPEG", "GIF"):
                    continue
            except Exception:
                # No se usa un icono que no podamos verificar como imagen utilizable.
                continue
            return imagen
    return None

def _dominios_probables_por_nombre(nombre_empresa, max_dominios=10):
    """Genera dominios candidatos desde la razón social, sin nombres/NIT codificados.

    Solo propone dominios; jamás los considera oficiales hasta que el sitio responde
    y su contenido confirma el nombre de la empresa.
    """
    palabras = _normalizar_nombre_empresa(nombre_empresa).split()
    legales = {
        "sa", "sas", "s", "a", "esp", "e", "sp", "p", "bic", "ltda", "limitada",
        "eu", "cia", "compania", "sociedad", "anonima", "anónima", "sc", "sca",
    }
    conectores = {"de", "del", "la", "el", "los", "las", "y", "e", "en"}
    genericas = {
        "grupo", "grupos", "empresa", "empresas", "publica", "publicas", "publico", "publicos",
        "servicios", "servicio", "industria", "industrial", "comercial", "nacional", "nacionales",
        "colombia", "colombiana", "colombiano", "energia", "electricas", "electrica", "municipal",
        "municipales", "medellin", "bogota", "cali", "productos", "alimenticios", "sociedad", "compania", "empresarial",
    }
    significativas = [w for w in palabras if w not in legales and w not in conectores]
    marcas = [w for w in significativas if w not in genericas and len(w) >= 4]
    semillas = []

    # Nombres de grupo: "Grupo Nutresa" -> gruponutresa.com y nutresa.com.
    if "grupo" in significativas:
        siguientes = [w for w in significativas if w != "grupo" and w not in genericas]
        if siguientes:
            semillas.append("grupo" + siguientes[0])

    # Para una marca distintiva (Colombina, Alpina, Postobón), prueba primero
    # el nombre de marca antes de construir acrónimos a partir de palabras largas.
    semillas.extend(marcas[:4])

    # Acrónimo para razones sociales sin palabra de marca distintiva, como EPM.
    if not marcas and 3 <= len(significativas) <= 6:
        acronimo = "".join(w[0] for w in significativas if w)
        if 2 <= len(acronimo) <= 6:
            semillas.append(acronimo)
    # Para nombres compuestos comerciales, intenta la unión de las dos palabras de marca.
    if len(marcas) >= 2:
        semillas.append("".join(marcas[:2]))

    extensiones = ("com.co", "com", "co") if len(significativas) >= 3 else ("com", "com.co", "co")
    dominios = []
    for semilla in semillas:
        if not re.fullmatch(r"[a-z0-9]{3,30}", semilla):
            continue
        for extension in extensiones:
            dominio = f"{semilla}.{extension}"
            if dominio not in dominios:
                dominios.append(dominio)
            if len(dominios) >= max_dominios:
                return dominios
    return dominios[:max_dominios]


def _acronimo_nombre_empresa(nombre_empresa):
    palabras = _normalizar_nombre_empresa(nombre_empresa).split()
    ignorar = {
        "sa", "sas", "s", "a", "esp", "e", "sp", "p", "bic", "ltda", "limitada", "eu",
        "de", "del", "la", "el", "los", "las", "y", "e", "en", "cia", "compania",
        "sociedad", "anonima", "grupo", "grupos",
    }
    palabras = [w for w in palabras if w not in ignorar]
    if 2 <= len(palabras) <= 6:
        return "".join(w[0] for w in palabras if w)
    return ""


def _buscar_logo_en_dominio_derivado(nombre_empresa):
    """Prueba dominios candidatos construidos desde el nombre y exige validar el contenido.

    Esta ruta no depende de Bing RSS, que puede devolver HTTP 200 sin ningún resultado.
    """
    dominios = _dominios_probables_por_nombre(nombre_empresa)
    _log_busqueda_empresa(
        "LOGO WEB DIRECTA: dominios candidatos generados desde la razón social: "
        + (", ".join(dominios) if dominios else "ninguno")
    )
    dominios_verificados = []
    for dominio in dominios:
        url = f"https://{dominio}/"
        try:
            pagina = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
                },
                timeout=(5, 12), allow_redirects=True,
            )
            tipo = pagina.headers.get("Content-Type", "").lower()
            _log_busqueda_empresa(
                f"LOGO WEB DIRECTA: candidato={dominio}; HTTP={pagina.status_code}; "
                f"tipo={tipo}; bytes={len(pagina.content)}; destino={pagina.url[:220]}"
            )
            if not pagina.ok or "text/html" not in tipo:
                continue
            contenido = pagina.text[:2_000_000]
            texto_pagina = _texto_html_limpio(contenido)
            titulo = re.search(r"<title[^>]*>(.*?)</title>", contenido, re.I | re.S)
            title_text = _texto_html_limpio(titulo.group(1)) if titulo else ""
            coincide = _texto_coincide_empresa(nombre_empresa, f"{title_text} {texto_pagina}")
            acronimo = _acronimo_nombre_empresa(nombre_empresa)
            normalizado = _normalizar_nombre_empresa(f"{title_text} {texto_pagina}")
            coincide_acronimo = bool(
                acronimo and re.search(r"(?<![a-z0-9])" + re.escape(acronimo) + r"(?![a-z0-9])", normalizado)
            )
            if not (coincide or coincide_acronimo):
                _log_busqueda_empresa(
                    f"LOGO WEB DIRECTA: {dominio} descartado; contenido no confirma la empresa "
                    f"(título={title_text[:100]})."
                )
                continue

            dominio_final = _host_dominio_base(urlparse(pagina.url).netloc)
            if dominio_final and dominio_final not in dominios_verificados:
                dominios_verificados.append(dominio_final)
            _log_busqueda_empresa(
                f"LOGO WEB DIRECTA: sitio aceptado por coincidencia de nombre; sitio={pagina.url[:250]}"
            )
            try:
                logo = _extraer_logo_oficial_desde_sitio(
                    pagina.url, permitir_og_social=False, nombre_empresa=nombre_empresa
                )
            except Exception as exc:
                _log_busqueda_empresa(
                    f"LOGO WEB DIRECTA: extracción de HTML falló en {dominio_final}: "
                    f"{type(exc).__name__}: {str(exc)[:220]}"
                )
                logo = None
            if logo:
                _log_busqueda_empresa(
                    f"LOGO WEB DIRECTA: logo descargado desde {pagina.url}; "
                    f"mime={logo.get('mime')}; bytes={len(logo.get('bytes', b''))}."
                )
                return logo, pagina.url, dominios_verificados
            _log_busqueda_empresa(
                f"LOGO WEB DIRECTA: el sitio {dominio_final} coincide, pero no publicó un archivo de logo reconocible en su HTML."
            )
        except Exception as exc:
            _log_busqueda_empresa(
                f"LOGO WEB DIRECTA: error consultando {dominio}: {type(exc).__name__}: {str(exc)[:220]}"
            )
    return None, "", dominios_verificados


def buscar_empresa_y_logo_python(nombre_empresa="", nit_empresa=""):
    """Verifica identidad en RUES y busca el logotipo en sitios corporativos oficiales."""
    registro = _resolver_identidad_rues(nombre_empresa, nit_empresa)
    nombre_oficial = registro["nombre"]
    nit_oficial = registro["nit"]
    resultado = {
        "nombre": nombre_oficial,
        "nombre_fuente": registro.get("nombre_fuente", nombre_oficial),
        "nombres_fuente": registro.get("nombres_fuente", [registro.get("nombre_fuente", nombre_oficial)]),
        "denominaciones_alternativas": registro.get("denominaciones_alternativas", []),
        "nombres_comerciales": registro.get("nombres_comerciales", []),
        "nit": nit_oficial,
        "logo": None,
        "sitio": registro.get("url_fuente_identidad", RUES_PORTAL_URL),
        "empresa_verificada": True,
        "fuente_identidad": registro["fuente_identidad"],
        "url_fuente_identidad": registro["url_fuente_identidad"],
        "estado_matricula": registro.get("estado_matricula", ""),
        "fuente_logo": "",
        "diagnostico": "Identidad confirmada en RUES o en un documento público oficial.",
    }

    consultas = [
        f'"{nombre_oficial}" Colombia sitio oficial empresa',
        f'"{nombre_oficial}" logo sitio oficial Colombia',
        f'"{nombre_oficial}" kit de prensa logo',
        f'"{nombre_oficial}" logotipo descargar',
    ]
    resultados = []
    vistos = set()
    errores = []
    dominios_verificados = []
    urls_priorizadas = []
    _log_busqueda_empresa(f"LOGO: inicia búsqueda para nombre={nombre_oficial} | NIT={nit_oficial}.")
    _log_busqueda_empresa("LOGO_POLICY=v6.1: ProColombia prioriza coincidencia exacta NIT↔archivo; LogoAPI exige dominio+marca y PNG sin fallback.")

    # Primero consulta el directorio B2B de ProColombia. Su ficha actual publica
    # un logo corporativo explícito y un enlace a la web de la empresa. Se prioriza
    # antes de buscadores de imágenes que pueden devolver logos de productos.
    hallazgo_procolombia = _buscar_logo_en_directorio_procolombia(nombre_oficial, nit_oficial)
    if hallazgo_procolombia:
        resultado["logo"], pagina_logo = hallazgo_procolombia
        resultado["sitio"] = pagina_logo
        resultado["fuente_logo"] = "logo explícito en ficha empresarial de ProColombia"
        resultado["diagnostico"] = "Logo recuperado de ficha empresarial de ProColombia con nombre legal y web corporativa coincidentes."

    # Primero prueba el dominio que puede derivarse del nombre legal. Esta ruta
    # evita depender exclusivamente de Bing RSS, que en el diagnóstico 5.2
    # respondió HTTP 200 pero no entregó ningún resultado.
    if not resultado.get("logo"):
        logo_directo, sitio_directo, dominios_directos = _buscar_logo_en_dominio_derivado(nombre_oficial)
        for dominio_directo in dominios_directos:
            if dominio_directo not in dominios_verificados:
                dominios_verificados.append(dominio_directo)
        if logo_directo:
            resultado["logo"] = logo_directo
            resultado["sitio"] = sitio_directo
            resultado["fuente_logo"] = "página corporativa localizada por dominio derivado y validada por el nombre de la empresa"
            resultado["diagnostico"] = "Logo descargado directamente del sitio corporativo tras validar que su contenido corresponde a la razón social."

    # Catálogo estructurado auxiliar: dominio exacto + nombre coincidente + PNG sin fallback.
    if not resultado.get("logo") and dominios_verificados:
        hallazgo_logoapi = _buscar_logo_logoapi(nombre_oficial, dominios_verificados)
        if hallazgo_logoapi:
            resultado["logo"], pagina_logoapi = hallazgo_logoapi
            resultado["sitio"] = pagina_logoapi
            resultado["fuente_logo"] = "LogoAPI: dominio y nombre de marca coincidentes; PNG sin fallback"
            resultado["diagnostico"] = "Logo recuperado mediante catálogo de logos tras validar nombre y dominio corporativo."

    # Si el dominio derivado no funcionó, recurre al buscador web (RSS + HTML).
    if not resultado.get("logo"):
        for numero_consulta, consulta in enumerate(consultas, 1):
            try:
                items_consulta = _buscar_resultados_empresa(consulta, max_resultados=20)
                _log_busqueda_empresa(f"LOGO: consulta general {numero_consulta}/{len(consultas)} devolvió {len(items_consulta)} resultados.")
                for item in items_consulta:
                    url = item.get("url", "")
                    clave = url.split("?")[0].rstrip("/").lower()
                    if url and clave not in vistos:
                        vistos.add(clave)
                        resultados.append(item)
            except Exception as exc:
                errores.append(str(exc)[:180])

    dominios_no_corporativos = (
        "datos.gov.co", "rues.org.co", "dian.gov.co", "funcionpublica.gov.co",
        "supersociedades.gov.co", "mincit.gov.co", "gov.co", "wikipedia.org",
        "registronit.com", "einforma.com.co", "empresite.com", "dateas.com",
        "directorio-empresas", "lasempresas.com.co", "informa.co", "youtube.com",
        "facebook.com", "instagram.com", "linkedin.com", "x.com", "twitter.com",
        "tiktok.com", "bing.com", "google.com", "duckduckgo.com",
    )
    _log_busqueda_empresa(
        f"LOGO: {len(resultados)} URLs únicas para revisar; "
        + ("primeras URLs: " + " | ".join(x.get("url", "")[:180] for x in resultados[:6]) if resultados else "sin resultados RSS")
    )

    # Primera pasada: lee páginas recuperables, pero también conserva un dominio
    # corporativo cuyo nombre coincide con la razón social aunque bloquee robots.
    for item in resultados[:100]:
        url = item.get("url", "")
        dominio = urlparse(url).netloc.lower().removeprefix("www.")
        es_social = _dominio_es_red_social(url)
        if not dominio or (not es_social and any(d in dominio for d in dominios_no_corporativos)):
            continue
        titulo = item.get("titulo", "")
        snippet = item.get("snippet", "")
        texto_resultado = f"{titulo} {snippet}"
        coincide_resumen = _texto_coincide_empresa(nombre_oficial, texto_resultado)
        dominio_marca = _dominio_coincide_empresa(dominio, nombre_oficial)

        # Un dominio que contiene una palabra distintiva de la razón social y
        # aparece en el resultado de la búsqueda de esa empresa se conserva
        # como candidato oficial aun si el sitio bloquea el scraping automático.
        if dominio_marca and (coincide_resumen or not snippet):
            base = _host_dominio_base(dominio)
            if base not in dominios_verificados:
                dominios_verificados.append(base)
            urls_priorizadas.append((url, es_social, titulo, snippet))
        elif es_social and coincide_resumen:
            # Los perfiles sociales solo se usan para extraer la imagen de su
            # propia página; nunca se considera todo el dominio social oficial.
            urls_priorizadas.append((url, True, titulo, snippet))

        try:
            pagina = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 Chrome/120 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
                timeout=(5, 12), allow_redirects=True,
            )
            if not pagina.ok or "text/html" not in pagina.headers.get("Content-Type", "text/html").lower():
                continue
            texto_pagina = _texto_html_limpio(pagina.text[:2_000_000])
            if not _texto_coincide_empresa(nombre_oficial, f"{titulo} {snippet} {texto_pagina}"):
                continue

            host_final = urlparse(pagina.url or url).netloc.lower().removeprefix("www.")
            if not es_social and host_final:
                base = _host_dominio_base(host_final)
                if base not in dominios_verificados:
                    dominios_verificados.append(base)
            logo = _extraer_logo_oficial_desde_sitio(
                pagina.url or url, permitir_og_social=es_social, nombre_empresa=nombre_oficial
            )
            if logo:
                resultado["logo"] = logo
                resultado["sitio"] = pagina.url or url
                resultado["fuente_logo"] = "perfil público de la empresa" if es_social else "página corporativa oficial"
                resultado["diagnostico"] = "Identidad confirmada en fuente oficial; logo descargado desde la propia página."
                break
        except Exception as exc:
            errores.append(str(exc)[:180])
            continue

    # Segunda pasada: consulta las secciones de marca/kit de prensa de cada dominio
    # identificado. Es importante para empresas cuyo logo no está en la portada.
    if not resultado.get("logo") and dominios_verificados:
        for dominio in list(dominios_verificados)[:8]:
            for consulta in (
                f'"{nombre_oficial}" logo site:{dominio}',
                f'"{nombre_oficial}" "kit de prensa" site:{dominio}',
                f'site:{dominio} logotipo OR logo',
            ):
                try:
                    extras = _buscar_resultados_empresa(consulta, max_resultados=12)
                    for extra in extras:
                        extra_url = extra.get("url", "")
                        if not _pertenece_a_dominio_verificado(extra_url, dominios_verificados):
                            continue
                        urls_priorizadas.append((extra_url, False, extra.get("titulo", ""), extra.get("snippet", "")))
                        try:
                            pagina = requests.get(
                                extra_url,
                                headers={"User-Agent": "Mozilla/5.0 (compatible; CesantiasAlInstante/4.2)"},
                                timeout=(4, 9), allow_redirects=True,
                            )
                            if pagina.ok and "text/html" in pagina.headers.get("Content-Type", "text/html").lower():
                                logo = _extraer_logo_oficial_desde_sitio(
                                    pagina.url, permitir_og_social=False, nombre_empresa=nombre_oficial
                                )
                                if logo:
                                    resultado["logo"] = logo
                                    resultado["sitio"] = pagina.url
                                    resultado["fuente_logo"] = "sección de prensa o recursos de marca del sitio corporativo"
                                    resultado["diagnostico"] = "Logo descargado de una sección de prensa o recursos de marca del dominio corporativo verificado."
                                    break
                        except Exception as exc:
                            errores.append(str(exc)[:180])
                    if resultado.get("logo"):
                        break
                except Exception as exc:
                    errores.append(str(exc)[:180])
            if resultado.get("logo"):
                break

    # Si el dominio se identificó solo después de la búsqueda general, reintenta LogoAPI.
    if not resultado.get("logo") and dominios_verificados:
        hallazgo_logoapi = _buscar_logo_logoapi(nombre_oficial, dominios_verificados)
        if hallazgo_logoapi:
            resultado["logo"], pagina_logoapi = hallazgo_logoapi
            resultado["sitio"] = pagina_logoapi
            resultado["fuente_logo"] = "LogoAPI: dominio y nombre de marca coincidentes; PNG sin fallback"
            resultado["diagnostico"] = "Logo recuperado mediante catálogo de logos tras validar nombre y dominio corporativo."

    # Tercera pasada: buscadores de imágenes. Se aceptan imágenes alojadas en
    # CDNs externos siempre que su página de origen sea un dominio corporativo
    # ya identificado; así funcionan los kits de prensa servidos desde CDN.
    if not resultado.get("logo") and dominios_verificados:
        try:
            hallazgo_imagen = _buscar_logo_en_bing_images(nombre_oficial, dominios_verificados)
            if hallazgo_imagen:
                resultado["logo"], pagina_logo = hallazgo_imagen
                resultado["sitio"] = pagina_logo
                resultado["fuente_logo"] = "imagen pública enlazada desde el sitio corporativo verificado"
                resultado["diagnostico"] = "Identidad confirmada en RUES; logo recuperado de una imagen vinculada a la web corporativa."
        except Exception as exc:
            errores.append(str(exc)[:180])

    # No se acepta un favicon genérico como logotipo corporativo: puede ser un
    # icono mínimo o una imagen del proveedor de búsqueda, y acabar impreso en la carta.
    if not resultado.get("logo") and dominios_verificados:
        _log_busqueda_empresa(
            "LOGO: no se usa favicon como sustituto. Se deja el logo pendiente antes que insertar una imagen incorrecta."
        )

    if resultado.get("logo"):
        _log_busqueda_empresa(
            f"LOGO: imagen encontrada; fuente={resultado.get('fuente_logo', '')}; "
            f"URL={resultado.get('logo', {}).get('url', '')[:300]}; "
            f"mime={resultado.get('logo', {}).get('mime', '')}; bytes={len(resultado.get('logo', {}).get('bytes', b''))}."
        )
    else:
        _log_busqueda_empresa(
            "LOGO: no se descargó ninguna imagen válida después de probar ProColombia (perfil/sitemap), "
            "sitio corporativo, LogoAPI sin fallback y fuentes de imágenes."
        )
    if not resultado.get("logo"):
        resultado["diagnostico"] = (
            "La razón social y el NIT sí fueron identificados en la fuente oficial, "
            "pero los sitios corporativos identificados no ofrecieron una imagen descargable. "
            "La plantilla puede crearse y el logo quedará pendiente de revisión manual."
        )
        if errores:
            resultado["diagnostico"] += " Detalle técnico: " + errores[0]
    return resultado

def _longitud_indice_google_docs(texto):
    """Google Docs mide los índices en unidades UTF-16, no en caracteres Python."""
    return len(str(texto).encode("utf-16-le")) // 2


def _buscar_marcador_en_bloque(contenido, marcador, segment_id=None):
    """Busca un marcador en párrafos y tablas, incluso si está partido en varios TextRun."""
    for elemento in contenido or []:
        if not isinstance(elemento, dict):
            continue

        # Los marcadores suelen estar en párrafos de encabezado, cuerpo o pie.
        parrafo = elemento.get("paragraph")
        if isinstance(parrafo, dict):
            grupos = []
            grupo_actual = []
            cursor = elemento.get("startIndex", 1)
            for parte in parrafo.get("elements", []) or []:
                if not isinstance(parte, dict):
                    continue
                text_run = parte.get("textRun")
                if isinstance(text_run, dict):
                    texto = text_run.get("content", "") or ""
                    inicio = parte.get("startIndex", cursor)
                    if texto:
                        grupo_actual.append((int(inicio), texto))
                    cursor = parte.get("endIndex", int(inicio) + _longitud_indice_google_docs(texto))
                else:
                    if grupo_actual:
                        grupos.append(grupo_actual)
                        grupo_actual = []
                    cursor = parte.get("endIndex", cursor)
            if grupo_actual:
                grupos.append(grupo_actual)

            for grupo in grupos:
                texto_combinado = "".join(texto for _, texto in grupo)
                posicion = texto_combinado.find(marcador)
                if posicion < 0:
                    continue
                desplazamiento = posicion
                for inicio_run, texto_run in grupo:
                    if desplazamiento < len(texto_run):
                        indice = inicio_run + _longitud_indice_google_docs(texto_run[:desplazamiento])
                        return {"index": indice, "segmentId": segment_id}
                    desplazamiento -= len(texto_run)

        # Google Docs puede ubicar el marcador dentro de una tabla (p. ej. la
        # celda del membrete). Cada celda contiene su propio arreglo content.
        tabla = elemento.get("table")
        if isinstance(tabla, dict):
            for fila in tabla.get("tableRows", []) or []:
                for celda in fila.get("tableCells", []) or []:
                    encontrado = _buscar_marcador_en_bloque(
                        celda.get("content", []), marcador, segment_id
                    )
                    if encontrado:
                        return encontrado
    return None


def _buscar_marcador_en_documento(documento, marcador="{{LOGO_EMPRESA}}"):
    """Busca el marcador en cuerpo, encabezados y pies del Google Doc."""
    if not isinstance(documento, dict):
        return None
    encontrado = _buscar_marcador_en_bloque(
        documento.get("body", {}).get("content", []), marcador, None
    )
    if encontrado:
        return encontrado
    for segmento_id, encabezado in (documento.get("headers") or {}).items():
        encontrado = _buscar_marcador_en_bloque(
            encabezado.get("content", []), marcador, segmento_id
        )
        if encontrado:
            return encontrado
    for segmento_id, pie in (documento.get("footers") or {}).items():
        encontrado = _buscar_marcador_en_bloque(
            pie.get("content", []), marcador, segmento_id
        )
        if encontrado:
            return encontrado
    return None


def _documento_contiene_marcador(documento, marcador="{{LOGO_EMPRESA}}"):
    return _buscar_marcador_en_documento(documento, marcador) is not None


def _crear_png_marca_agua(datos_logo, relacion_aspecto=1.0, opacidad=0.13):
    """Crea una versión PNG grande, centrada y translúcida del logo corporativo."""
    try:
        from PIL import Image
        imagen = Image.open(BytesIO(datos_logo)).convert("RGBA")
    except Exception as exc:
        raise RuntimeError(f"No se pudo abrir el logo para crear la marca de agua: {exc}") from exc

    # Quita únicamente blancos casi puros del fondo, frecuentes en JPG de logos.
    pixeles = []
    for r, g, b, a in imagen.getdata():
        if r >= 247 and g >= 247 and b >= 247 and max(r, g, b) - min(r, g, b) <= 10:
            a = 0
        else:
            a = int(round(a * float(opacidad)))
        pixeles.append((r, g, b, max(0, min(255, a))))
    imagen.putdata(pixeles)

    caja = imagen.getbbox()
    if not caja:
        raise RuntimeError("El logo no contiene píxeles visibles para crear la marca de agua.")
    imagen = imagen.crop(caja)

    # La caja PNG conserva la relación del objeto de marca de agua que ya existe
    # en la plantilla. Así replaceImage mantiene la ubicación, tamaño y capa detrás del texto.
    try:
        relacion_aspecto = float(relacion_aspecto)
    except Exception:
        relacion_aspecto = 1.0
    if not (0.35 <= relacion_aspecto <= 4.0):
        relacion_aspecto = 1.0

    ancho_canvas = 1600
    alto_canvas = int(round(ancho_canvas / relacion_aspecto))
    alto_canvas = max(500, min(2400, alto_canvas))
    # El logo ocupa más superficie dentro del marco de marca de agua ya configurado en Google Docs.
    max_ancho = int(ancho_canvas * 0.96)
    max_alto = int(alto_canvas * 0.90)
    # thumbnail() no amplía imágenes pequeñas; se calcula una escala que también puede ampliar,
    # respetando siempre los límites y la proporción del logo.
    escala = min(max_ancho / imagen.width, max_alto / imagen.height)
    nuevo_tamano = (
        max(1, int(round(imagen.width * escala))),
        max(1, int(round(imagen.height * escala))),
    )
    imagen = imagen.resize(nuevo_tamano, Image.Resampling.LANCZOS)

    lienzo = Image.new("RGBA", (ancho_canvas, alto_canvas), (255, 255, 255, 0))
    x = (ancho_canvas - imagen.width) // 2
    y = (alto_canvas - imagen.height) // 2
    lienzo.alpha_composite(imagen, (x, y))

    salida = BytesIO()
    lienzo.save(salida, format="PNG", optimize=True)
    datos = salida.getvalue()
    if not datos.startswith(b"\x89PNG\r\n\x1a\n") or len(datos) < 500:
        raise RuntimeError("La marca de agua PNG generada no superó la validación de imagen.")
    return datos, ancho_canvas, alto_canvas


def _obtener_objetos_marca_agua(documento):
    """Devuelve imágenes posicionadas detrás del texto; no toca imágenes inline del encabezado."""
    candidatos = []
    for object_id, objeto in (documento.get("positionedObjects") or {}).items():
        propiedades = (objeto or {}).get("positionedObjectProperties") or {}
        posicion = propiedades.get("positioning") or {}
        incrustado = propiedades.get("embeddedObject") or {}
        imagen = incrustado.get("imageProperties") or {}
        if posicion.get("layout") != "BEHIND_TEXT" or not imagen:
            continue
        tamano = incrustado.get("size") or {}
        ancho = (tamano.get("width") or {}).get("magnitude")
        alto = (tamano.get("height") or {}).get("magnitude")
        try:
            area = float(ancho or 0) * float(alto or 0)
            ratio = float(ancho) / float(alto) if ancho and alto else 1.0
        except Exception:
            area, ratio = 0.0, 1.0
        candidatos.append({
            "object_id": object_id,
            "area": area,
            "ratio": ratio,
            "width": ancho,
            "height": alto,
            "positioning": posicion,
            "embedded": incrustado,
        })
    # En esta plantilla el elemento detrás del texto es la marca de agua central.
    # Se prioriza el de mayor superficie para no reemplazar elementos decorativos pequeños.
    return sorted(candidatos, key=lambda x: x["area"], reverse=True)


def insertar_marca_agua_desde_logo(document_id, logo, solicitud_id, carpeta_destino_id=None):
    """Reemplaza la imagen existente BEHIND_TEXT por una versión translúcida del logo empresarial.

    Google Docs API no ofrece una petición para crear un objeto flotante nuevo detrás del texto.
    Por eso se reutiliza el objeto de marca de agua ya posicionado en la plantilla universal y
    se reemplaza su imagen, conservando su posición y tamaño.
    """
    if not logo or not logo.get("bytes"):
        _log_busqueda_empresa("MARCA DE AGUA: omitida; no hay bytes de logo corporativo.")
        return False

    docs = obtener_servicio_docs()
    documento = docs.documents().get(documentId=document_id).execute()
    candidatos = _obtener_objetos_marca_agua(documento)
    if not candidatos:
        mensaje = (
            "La plantilla no contiene una imagen posicionada BEHIND_TEXT para usar como marca de agua. "
            "No se insertará una imagen inline que desplace el contenido."
        )
        st.session_state["error_marca_agua_empresa"] = mensaje
        _log_busqueda_empresa("MARCA DE AGUA: " + mensaje)
        return False

    objetivo = candidatos[0]
    marca_png, ancho_png, alto_png = _crear_png_marca_agua(
        logo["bytes"], relacion_aspecto=objetivo.get("ratio", 1.0), opacidad=0.13
    )

    servicio_drive = _crear_servicio_drive_nuevo()
    folder_id = str(carpeta_destino_id or obtener_id_carpeta_solicitudes()).strip()
    nombre_archivo = f"MarcaAgua_{solicitud_id}.png"
    media = MediaIoBaseUpload(BytesIO(marca_png), mimetype="image/png", resumable=False)
    archivo = servicio_drive.files().create(
        body={"name": nombre_archivo, "parents": [folder_id]},
        media_body=media,
        fields="id,webContentLink,webViewLink",
    ).execute(num_retries=2)
    marca_id = archivo["id"]
    servicio_drive.permissions().create(
        fileId=marca_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute(num_retries=2)
    uri = archivo.get("webContentLink") or f"https://drive.google.com/uc?export=download&id={marca_id}"
    if len(uri) > 2000:
        raise RuntimeError("La URL pública de la marca de agua supera el límite de Google Docs.")

    _log_busqueda_empresa(
        f"MARCA DE AGUA: reemplazando objeto detrás del texto; object_id={objetivo['object_id']}; "
        f"layout=BEHIND_TEXT; tamaño_original={objetivo.get('width')}x{objetivo.get('height')}; "
        f"opacidad=13%; PNG={ancho_png}x{alto_png}; bytes={len(marca_png)}."
    )
    solicitud = {
        "replaceImage": {
            "imageObjectId": objetivo["object_id"],
            "uri": uri,
            "imageReplaceMethod": "CENTER_CROP",
        }
    }
    docs.documents().batchUpdate(
        documentId=document_id,
        body={"requests": [solicitud]},
    ).execute(num_retries=2)

    verificacion = docs.documents().get(documentId=document_id).execute()
    actualizado = (verificacion.get("positionedObjects") or {}).get(objetivo["object_id"])
    props_actualizadas = (actualizado or {}).get("positionedObjectProperties") or {}
    posicion_actualizada = props_actualizadas.get("positioning") or {}
    imagen_actualizada = (props_actualizadas.get("embeddedObject") or {}).get("imageProperties") or {}
    if not actualizado or posicion_actualizada.get("layout") != "BEHIND_TEXT" or not imagen_actualizada:
        raise RuntimeError(
            "Google Docs no confirmó que la marca de agua siga detrás del texto después del reemplazo."
        )

    st.session_state["marca_agua_empresa_insertada"] = True
    st.session_state["error_marca_agua_empresa"] = ""
    _log_busqueda_empresa(
        f"MARCA DE AGUA: inserción verificada; object_id={objetivo['object_id']}; "
        "la imagen permanece BEHIND_TEXT y conserva el objeto posicionado original."
    )
    return True


def insertar_logo_en_plantilla(document_id, logo, solicitud_id, carpeta_destino_id=None, limpiar_marcador_si_falla=False):
    """Inserta imagen en Google Docs y verifica que el documento recibió un InlineObject."""
    st.session_state["marca_agua_empresa_insertada"] = False
    marcador = "{{LOGO_EMPRESA}}"
    docs = obtener_servicio_docs()
    documento = docs.documents().get(documentId=document_id).execute()
    ubicacion = _buscar_marcador_en_documento(documento, marcador)
    if not ubicacion:
        mensaje = "No se encontró {{LOGO_EMPRESA}} en cuerpo, encabezados, pies ni tablas del documento."
        st.session_state["error_insercion_logo_empresa"] = mensaje
        _log_busqueda_empresa("LOGO INSERCIÓN: " + mensaje)
        return False

    indice = int(ubicacion["index"])
    segment_id = ubicacion.get("segmentId")

    def rango_actual(documento_actual=None):
        doc = documento_actual or docs.documents().get(documentId=document_id).execute()
        ubicacion_actual = _buscar_marcador_en_documento(doc, marcador)
        if not ubicacion_actual:
            return None
        rango = {
            "startIndex": int(ubicacion_actual["index"]),
            "endIndex": int(ubicacion_actual["index"]) + _longitud_indice_google_docs(marcador),
        }
        if ubicacion_actual.get("segmentId"):
            rango["segmentId"] = ubicacion_actual["segmentId"]
        return rango

    def limpiar_marcador_final():
        if not limpiar_marcador_si_falla:
            return
        try:
            actual = docs.documents().get(documentId=document_id).execute()
            rango = rango_actual(actual)
            if rango:
                docs.documents().batchUpdate(
                    documentId=document_id,
                    body={"requests": [{"deleteContentRange": {"range": rango}}]},
                ).execute()
                _log_busqueda_empresa("LOGO INSERCIÓN: marcador eliminado solo de la copia final; la plantilla conserva su marcador.")
        except Exception as exc:
            _log_busqueda_empresa(
                f"LOGO INSERCIÓN: no se pudo limpiar el marcador de la copia final: {type(exc).__name__}: {str(exc)[:300]}"
            )

    if not logo or not logo.get("bytes"):
        mensaje = "La búsqueda de la empresa no entregó bytes de una imagen de logo utilizable."
        st.session_state["error_insercion_logo_empresa"] = mensaje
        _log_busqueda_empresa("LOGO INSERCIÓN: " + mensaje)
        limpiar_marcador_final()
        return False

    # Carga una copia en Drive para conservar el recurso, además de probar la URL
    # original como respaldo si Google Docs no puede descargar el enlace de Drive.
    uris_candidatas = []
    logo_id = None
    try:
        servicio_drive = _crear_servicio_drive_nuevo()
        folder_id = str(carpeta_destino_id or obtener_id_carpeta_solicitudes()).strip()
        nombre = f"Logo_empresa_{solicitud_id}"
        media = MediaIoBaseUpload(BytesIO(logo["bytes"]), mimetype=logo["mime"], resumable=False)
        archivo = servicio_drive.files().create(
            body={"name": nombre, "parents": [folder_id]},
            media_body=media,
            fields="id,webContentLink,webViewLink",
        ).execute()
        logo_id = archivo["id"]
        _log_busqueda_empresa(
            f"LOGO DRIVE: imagen cargada; file_id={logo_id}; mime={logo['mime']}; "
            f"bytes={len(logo['bytes'])}; carpeta={folder_id}."
        )
        servicio_drive.permissions().create(
            fileId=logo_id,
            body={"type": "anyone", "role": "reader"},
            fields="id",
        ).execute()
        _log_busqueda_empresa("LOGO DRIVE: permiso de lectura pública confirmado.")
        uris_candidatas.append((
            archivo.get("webContentLink") or f"https://drive.google.com/uc?export=download&id={logo_id}",
            "archivo público de Google Drive",
        ))
    except Exception as exc:
        detalle_drive = f"{type(exc).__name__}: {str(exc)[:500]}"
        _log_busqueda_empresa("LOGO DRIVE: no se pudo guardar/compartir la imagen: " + detalle_drive)

    url_origen = str(logo.get("url") or "").strip()
    if url_origen.startswith(("https://", "http://")):
        uris_candidatas.append((url_origen, "URL original de la imagen"))

    # Evita intentar dos veces la misma URL.
    uris_unicas = []
    vistos_uri = set()
    for uri, etiqueta in uris_candidatas:
        if uri and uri not in vistos_uri:
            vistos_uri.add(uri)
            uris_unicas.append((uri, etiqueta))

    error_final = "No se obtuvo una URL pública para insertar la imagen."
    for uri, etiqueta in uris_unicas:
        try:
            documento_actual = docs.documents().get(documentId=document_id).execute()
            ubi = _buscar_marcador_en_documento(documento_actual, marcador)
            if not ubi:
                # En caso de que una tentativa anterior insertara la imagen
                # correctamente, valida el objeto antes de marcar fallo.
                inline_antes = set((documento.get("inlineObjects") or {}).keys())
                inline_ahora = set((documento_actual.get("inlineObjects") or {}).keys())
                if inline_ahora - inline_antes:
                    st.session_state["error_insercion_logo_empresa"] = ""
                    _log_busqueda_empresa("LOGO DOCS: el documento ya contiene el objeto de imagen insertado.")
                    return True
                error_final = "El marcador ya no está disponible en el documento para insertar el logo."
                break

            loc = {"index": int(ubi["index"])}
            if ubi.get("segmentId"):
                loc["segmentId"] = ubi["segmentId"]
            rango = {
                "startIndex": int(ubi["index"]),
                "endIndex": int(ubi["index"]) + _longitud_indice_google_docs(marcador),
            }
            if ubi.get("segmentId"):
                rango["segmentId"] = ubi["segmentId"]

            inline_antes = set((documento_actual.get("inlineObjects") or {}).keys())
            _log_busqueda_empresa(
                f"LOGO DOCS: intentando insertar desde {etiqueta}; documento={document_id}; "
                f"segmento={'encabezado/pie' if ubi.get('segmentId') else 'cuerpo'}; índice={ubi['index']}."
            )
            respuesta = docs.documents().batchUpdate(
                documentId=document_id,
                body={"requests": [
                    {"deleteContentRange": {"range": rango}},
                    {"insertInlineImage": {
                        "location": loc,
                        "uri": uri,
                        "objectSize": {
                            # Logo 31% más grande, manteniendo prácticamente la proporción original.
                            "width": {"magnitude": 125, "unit": "PT"},
                            "height": {"magnitude": 59, "unit": "PT"},
                        },
                    }},
                ]},
            ).execute()

            documento_verificacion = docs.documents().get(documentId=document_id).execute()
            inline_despues = set((documento_verificacion.get("inlineObjects") or {}).keys())
            nuevos_objetos = inline_despues - inline_antes
            replies = respuesta.get("replies", []) if isinstance(respuesta, dict) else []
            reply_objeto = bool(
                len(replies) > 1 and
                isinstance(replies[1], dict) and
                replies[1].get("insertInlineImage", {}).get("objectId")
            )
            if nuevos_objetos or reply_objeto:
                st.session_state["error_insercion_logo_empresa"] = ""
                _log_busqueda_empresa(
                    f"LOGO DOCS: inserción confirmada; fuente={etiqueta}; "
                    f"objetos_nuevos={len(nuevos_objetos)}; file_id_drive={logo_id or 'no guardado'}."
                )
                # Reutiliza la imagen ya posicionada detrás del texto en la plantilla
                # universal. La reemplaza por el logo de esta empresa con 13% de opacidad.
                try:
                    insertar_marca_agua_desde_logo(
                        document_id, logo, solicitud_id,
                        carpeta_destino_id=carpeta_destino_id
                    )
                except Exception as exc_marca:
                    st.session_state["marca_agua_empresa_insertada"] = False
                    st.session_state["error_marca_agua_empresa"] = f"{type(exc_marca).__name__}: {str(exc_marca)[:500]}"
                    _log_busqueda_empresa(
                        "MARCA DE AGUA: no se pudo reemplazar; el logo pequeño de cabecera sí quedó insertado. "
                        + st.session_state["error_marca_agua_empresa"]
                    )
                return True
            error_final = "Google Docs respondió, pero no aparece un InlineObject nuevo al volver a leer el documento."
            _log_busqueda_empresa("LOGO DOCS: " + error_final)
        except Exception as exc:
            error_final = f"{type(exc).__name__}: {str(exc)[:600]}"
            _log_busqueda_empresa(f"LOGO DOCS: falló intento con {etiqueta}: {error_final}")

    st.session_state["error_insercion_logo_empresa"] = error_final
    _log_busqueda_empresa("LOGO INSERCIÓN: resultado final fallido: " + error_final)
    limpiar_marcador_final()
    return False


def _forzar_columnas_texto(df, nombres):
    """Evita que columnas vacías de Sheets queden como float64 en pandas."""
    for nombre_columna in nombres:
        if nombre_columna not in df.columns:
            df[nombre_columna] = pd.Series(index=df.index, dtype="object")
        else:
            # object acepta tanto cadenas vacías como texto en columnas que
            # pandas pudo inferir como float64 porque todas sus celdas estaban vacías.
            df[nombre_columna] = df[nombre_columna].astype("object")
    return df


def actualizar_estado_empresa_en_sheets(solicitud_id, resultado):
    """Actualiza únicamente la fila de la solicitud con el resultado de la búsqueda."""
    try:
        df = conn.read(worksheet="Solicitudes", ttl=0).dropna(how="all")
        if "solicitud_id" not in df.columns:
            return

        # En Sheets, una columna sin valores puede llegar desde pandas como
        # float64. Convertimos los campos textuales antes de escribir cadenas.
        df = _forzar_columnas_texto(
            df, ("empresa", "nit", "estado_logo", "logo_url", "estado_empresa")
        )

        fila = df.index[df["solicitud_id"].astype(str) == str(solicitud_id)]
        if len(fila):
            i = fila[0]
            if resultado.get("nombre"):
                df.at[i, "empresa"] = str(resultado["nombre"]).upper()
            if resultado.get("nit"):
                df.at[i, "nit"] = str(resultado["nit"])
            df.at[i, "estado_logo"] = (
                "Pendiente de inserción" if resultado.get("logo")
                else "falta-logo-revision manual"
            )
            logo = resultado.get("logo") or {}
            df.at[i, "logo_url"] = str(logo.get("url") or "")
            df.at[i, "estado_empresa"] = (
                "Verificada en RUES/Confecámaras" if resultado.get("empresa_verificada")
                else "revision manual"
            )
            conn.update(worksheet="Solicitudes", data=df)
    except Exception as exc:
        # Un problema de actualización de metadatos no debe detener la carta.
        st.warning(f"La carta continuará; no se pudo actualizar el estado de búsqueda en Sheets: {exc}")


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
                doc_id_auto = _celda_texto(valor_doc)
    elif empresa_seleccionada:
        filtro_empresa = (
            df_empresas["Nombre_Empresa"].astype(str).str.strip()
            == empresa_seleccionada.strip()
        )
        if filtro_empresa.any():
            fila_empresa = df_empresas.loc[filtro_empresa].iloc[0]
            if "Doc_ID" in df_empresas.columns:
                valor_doc = fila_empresa.get("Doc_ID", "")
                doc_id_auto = _celda_texto(valor_doc)
            if "NIT" in df_empresas.columns:
                valor_nit = fila_empresa.get("NIT", "")
                nit_auto = _celda_texto(valor_nit)

    st.session_state.empresa = empresa_valor
    st.session_state.nit = nit_auto
    st.session_state.empresa_seleccionada = empresa_seleccionada
    st.session_state.logo_empresa_en_template = False
    st.session_state.estado_logo_empresa = "falta-logo-revision manual"
    st.session_state.logo_empresa_pendiente = None
    st.session_state.busqueda_otra_completada = False

    if doc_id_auto:
        info_plantilla = obtener_info_plantilla(doc_id_auto)
        st.session_state.doc_id_plantilla = info_plantilla["id"]
        st.session_state.nombre_plantilla = info_plantilla.get("name", "Documento sin nombre")
        st.session_state.plantilla_url = info_plantilla.get("webViewLink", "")
        if empresa_seleccionada != "Otra":
            fila_empresa = df_empresas.loc[filtro_empresa].iloc[0] if "filtro_empresa" in locals() and filtro_empresa.any() else None
            if fila_empresa is not None:
                estado_logo = _celda_texto(fila_empresa.get("Estado_Logo", ""))
                st.session_state.estado_logo_empresa = estado_logo or "falta-logo-revision manual"
                st.session_state.logo_empresa_en_template = estado_logo.lower().startswith("logo-insertado")
                st.session_state.marca_agua_empresa_pendiente = "marca-agua-pendiente" in estado_logo.lower()
                st.session_state.busqueda_otra_completada = bool(
                    st.session_state.logo_empresa_en_template and not st.session_state.marca_agua_empresa_pendiente
                )
    else:
        st.session_state.doc_id_plantilla = ""
        st.session_state.nombre_plantilla = ""
        st.session_state.plantilla_url = ""
    return df_empresas, empresa_valor, nit_auto, doc_id_auto


def _celda_texto(valor):
    """Convierte celdas de Sheets a texto sin propagar NaN ni valores nulos."""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass
    texto = str(valor).strip()
    return "" if texto.casefold() in ("nan", "none", "<na>") else texto


def _leer_hoja_empresas():
    """Lee Empresas y garantiza columnas textuales usadas por el flujo."""
    df = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
    columnas = ("Nombre_Empresa", "NIT", "Doc_ID", "Logo_URL", "Estado_Logo", "Fuente_Verificacion")
    for columna in columnas:
        if columna not in df.columns:
            df[columna] = ""
    df = _forzar_columnas_texto(df, columnas)
    for columna in columnas:
        df[columna] = df[columna].where(pd.notna(df[columna]), "")
    return df


def _coincidencias_empresa_en_df(df, nombre="", nit=""):
    """Devuelve coincidencias separadas por nombre y NIT, sin escoger a ciegas."""
    clave_nit = _clave_nit(nit)
    clave_nombre = _clave_nombre_empresa(nombre)
    indices_nombre = []
    indices_nit = []

    for indice, fila in df.iterrows():
        nombre_fila = _celda_texto(fila.get("Nombre_Empresa", ""))
        if not nombre_fila or nombre_fila.casefold() == "otra":
            continue
        nit_fila = _celda_texto(fila.get("NIT", ""))
        if clave_nombre and _clave_nombre_empresa(nombre_fila) == clave_nombre:
            indices_nombre.append(indice)
        if clave_nit and _clave_nit(nit_fila) == clave_nit:
            indices_nit.append(indice)

    if len(indices_nombre) > 1:
        raise ValueError(
            "Hay más de un registro con ese nombre normalizado en la hoja Empresas. "
            "Debes revisar y unificar esos duplicados antes de continuar."
        )
    if len(indices_nit) > 1:
        raise ValueError(
            "Hay más de un registro con ese NIT en la hoja Empresas. "
            "Debes revisar y unificar esos duplicados antes de continuar."
        )

    indice_nombre = indices_nombre[0] if indices_nombre else None
    indice_nit = indices_nit[0] if indices_nit else None

    if indice_nombre is not None and indice_nit is not None and indice_nombre != indice_nit:
        raise ValueError(
            "El nombre y el NIT que escribiste pertenecen a dos registros diferentes "
            "de la base de Empresas. No se modificó ningún registro. Revisa ambos datos."
        )

    indice = indice_nit if indice_nit is not None else indice_nombre
    if indice is None:
        return None

    fila = df.loc[indice]
    nombre_guardado = _celda_texto(fila.get("Nombre_Empresa", ""))
    nit_guardado = _celda_texto(fila.get("NIT", ""))

    # Si solo una de las dos claves encuentra registro, la otra entrada no puede
    # contradecir los datos ya guardados en ese registro.
    if nombre and nombre_guardado and _clave_nombre_empresa(nombre) != _clave_nombre_empresa(nombre_guardado):
        raise ValueError(
            f"El NIT coincide con «{nombre_guardado}», pero el nombre escrito no coincide. "
            "No se asociaron los datos para evitar mezclar empresas."
        )
    if nit and nit_guardado and _clave_nit(nit) != _clave_nit(nit_guardado):
        raise ValueError(
            f"El nombre coincide con «{nombre_guardado}», pero el NIT escrito es diferente "
            "del que ya está registrado. No se modificó la base de empresas."
        )
    return indice


def _buscar_fila_empresa_en_df(df, nombre="", nit=""):
    """Busca una empresa validando conjuntamente el nombre y el NIT cuando se entregan."""
    return _coincidencias_empresa_en_df(df, nombre, nit)


def guardar_empresa_en_sheets(nombre, nit, doc_id, logo_url="", estado_logo="falta-logo-revision manual", fuente_verificacion=""):
    """Inserta o actualiza la empresa y su Doc_ID de plantilla en Google Sheets."""
    nombre = str(nombre or "").strip()
    nit = str(nit or "").strip()
    doc_id = str(doc_id or "").strip()
    if not nombre or not doc_id:
        raise ValueError("Para guardar una empresa se requiere nombre y Doc_ID de plantilla.")

    df = _leer_hoja_empresas()
    indice = _buscar_fila_empresa_en_df(df, nombre, nit)
    if indice is None:
        fila_nueva = {columna: "" for columna in df.columns}
        fila_nueva.update({
            "Nombre_Empresa": nombre,
            "NIT": nit,
            "Doc_ID": doc_id,
            "Logo_URL": str(logo_url or ""),
            "Estado_Logo": str(estado_logo or "falta-logo-revision manual"),
            "Fuente_Verificacion": str(fuente_verificacion or "")
        })
        df = pd.concat([df, pd.DataFrame([fila_nueva], columns=df.columns)], ignore_index=True)
        df = _forzar_columnas_texto(df, ("Nombre_Empresa", "NIT", "Doc_ID", "Logo_URL", "Estado_Logo", "Fuente_Verificacion"))
    else:
        df = _forzar_columnas_texto(df, ("Nombre_Empresa", "NIT", "Doc_ID", "Logo_URL", "Estado_Logo", "Fuente_Verificacion"))
        df.at[indice, "Nombre_Empresa"] = nombre
        if nit:
            df.at[indice, "NIT"] = nit
        df.at[indice, "Doc_ID"] = doc_id
        df.at[indice, "Logo_URL"] = str(logo_url or "")
        df.at[indice, "Estado_Logo"] = str(estado_logo or "falta-logo-revision manual")
        if fuente_verificacion:
            df.at[indice, "Fuente_Verificacion"] = str(fuente_verificacion)

    conn.update(worksheet="Empresas", data=df)
    return doc_id


def preparar_empresa_nueva_y_template(nombre_ingresado="", nit_ingresado=""):
    """Verifica nombre/NIT en RUES oficial, reutiliza registros existentes o crea una sola plantilla propia."""
    nombre_original = _celda_texto(nombre_ingresado)
    nit_original = _celda_texto(nit_ingresado)
    if not nombre_original and not nit_original:
        raise ValueError("Escribe el nombre de la empresa, el NIT o ambos.")

    df = _leer_hoja_empresas()
    fila_existente = _buscar_fila_empresa_en_df(df, nombre_original, nit_original)

    nombre_guardado = ""
    nit_guardado = ""
    doc_guardado = ""
    estado_guardado = ""
    logo_url_guardado = ""
    plantilla_guardada_actual = False
    if fila_existente is not None:
        fila = df.loc[fila_existente]
        nombre_guardado = _celda_texto(fila.get("Nombre_Empresa", ""))
        nit_guardado = _celda_texto(fila.get("NIT", ""))
        doc_guardado = _celda_texto(fila.get("Doc_ID", ""))
        estado_guardado = _celda_texto(fila.get("Estado_Logo", ""))
        logo_url_guardado = _celda_texto(fila.get("Logo_URL", ""))

    # La fila «Otra» siempre conserva el ID de la plantilla universal.
    filas_base = df[df["Nombre_Empresa"].astype(str).str.strip().str.casefold() == "otra"]
    doc_id_base = _celda_texto(filas_base.iloc[0].get("Doc_ID", "")) if not filas_base.empty else ""

    _log_busqueda_empresa(
        f"PLANTILLA REVISION 6.2: plantilla universal Doc_ID={doc_id_base or 'NO_CONFIGURADA'}; "
        "las plantillas de empresa anteriores se renovarán para heredar el formato actualizado."
    )

    # Si el registro existente ya tiene nombre y NIT, esa pareja de la base es
    # la fuente de verdad. La búsqueda web posterior se usa solo para recuperar logo.
    pareja_confirmada_en_base = bool(nombre_guardado and nit_guardado)
    nombre_busqueda = nombre_guardado or nombre_original
    nit_busqueda = nit_guardado or nit_original

    # Solo reutiliza plantillas creadas con la revisión actual. Las anteriores se
    # renuevan una vez para incorporar la marca de agua corporativa y retirar
    # el nombre/NIT. La misma fila de Empresas se actualiza con el nuevo Doc_ID.
    if doc_guardado and doc_guardado != doc_id_base:
        info_guardada = obtener_info_plantilla(doc_guardado)
        nombre_esperado = _clave_template_empresa(
            nombre_guardado or nombre_original, nit_guardado or nit_original
        )
        plantilla_guardada_actual = _celda_texto(info_guardada.get("name", "")) == nombre_esperado
        if not plantilla_guardada_actual:
            _log_busqueda_empresa(
                "PLANTILLA EMPRESA: se detectó una plantilla anterior a v6.2; "
                "se creará una copia nueva desde la plantilla universal actual para heredar sus fuentes, tamaños y negritas."
            )

        if plantilla_guardada_actual and estado_guardado.lower().startswith("logo-insertado"):
            rellenar_identidad_en_plantilla_empresa(
                doc_guardado, nombre_guardado or nombre_original, nit_guardado or nit_original
            )
            st.session_state.empresa = nombre_guardado or nombre_original
            st.session_state.nit = nit_guardado or nit_original
            st.session_state.doc_id_plantilla = info_guardada["id"]
            st.session_state.nombre_plantilla = info_guardada.get("name", "Plantilla de empresa")
            st.session_state.plantilla_url = info_guardada.get("webViewLink", "")
            st.session_state.logo_empresa_en_template = True
            st.session_state.marca_agua_empresa_insertada = True
            st.session_state.marca_agua_empresa_pendiente = False
            st.session_state.logo_empresa_pendiente = None
            st.session_state.estado_logo_empresa = "logo-insertado"
            st.session_state.busqueda_otra_completada = True
            st.session_state.empresa_seleccionada = "Otra"
            return st.session_state.empresa, st.session_state.nit, doc_guardado

    # Si ya hay una pareja completa en Sheets, buscar el logo por nombre usando
    # la razón social guardada. Si falta uno de los datos, validar ambos en una
    # misma fuente antes de asociarlos.
    if pareja_confirmada_en_base:
        # Revalidamos nombre y NIT juntos contra la fuente oficial RUES incluso
        # cuando ya estaban guardados: la hoja no sustituye la verificación oficial.
        resultado = buscar_empresa_y_logo_python(nombre_busqueda, nit_busqueda)
    else:
        resultado = buscar_empresa_y_logo_python(nombre_busqueda, nit_busqueda)
        if nombre_busqueda and nit_busqueda and not resultado.get("empresa_verificada"):
            raise ValueError(
                "No pudimos confirmar que el nombre y el NIT correspondan a la misma empresa. "
                "No se creó una plantilla ni se actualizó la base. Verifica los datos o intenta "
                "con el nombre legal exacto y el NIT correcto."
            )

    # Al renovar una plantilla solo para heredar el nuevo formato del documento
    # universal, no debemos perder un logo que ya había sido verificado y guardado.
    # Primero se intenta la búsqueda actual; si falla, se descarga la URL aprobada
    # que ya estaba registrada en la fila de la empresa.
    if not resultado.get("logo") and logo_url_guardado:
        _log_busqueda_empresa(
            "LOGO: búsqueda nueva sin imagen; se intentará recuperar el logo previamente verificado "
            "desde la columna Logo_URL de Empresas."
        )
        logo_previo = _descargar_candidato_logo(
            logo_url_guardado, referer=resultado.get("sitio", "")
        )
        if logo_previo:
            resultado["logo"] = logo_previo
            resultado["fuente_logo"] = "URL previamente verificada y guardada en Empresas"
            resultado["diagnostico"] = (
                "Se reutilizó el logo previamente verificado para renovar la plantilla desde el formato universal actual."
            )
            _log_busqueda_empresa("LOGO: se recuperó correctamente el logo previamente verificado.")
        else:
            _log_busqueda_empresa(
                "LOGO: no se pudo descargar la URL previamente guardada; no se renovará la plantilla "
                "para evitar perder el logo que ya estaba insertado."
            )

    # Protección: si la plantilla anterior ya tenía logo y ahora no hay bytes
    # para volver a insertarlo, detener antes de crear/reemplazar la plantilla.
    # Así una actualización tipográfica nunca degrada una plantilla que ya servía.
    if estado_guardado.lower().startswith("logo-insertado") and not resultado.get("logo"):
        raise RuntimeError(
            "La plantilla anterior ya tenía un logo insertado, pero no se pudo recuperar "
            "la imagen para renovar el formato desde la plantilla universal. No se reemplazó "
            "la plantilla ni se modificó el Doc_ID existente."
        )

    nombre_final = nombre_guardado or _celda_texto(resultado.get("nombre")) or nombre_original
    nit_final = nit_guardado or _celda_texto(resultado.get("nit")) or nit_original
    if not nombre_final:
        detalle = _celda_texto(resultado.get("diagnostico", ""))
        mensaje = (
            "No se pudo identificar la razón social a partir del NIT. "
            "La búsqueda automática no encontró una fuente pública legible con el nombre."
        )
        if detalle:
            mensaje += " Detalle: " + detalle
        mensaje += " Puedes intentar de nuevo más tarde o escribir también el nombre legal."
        raise ValueError(mensaje)

    # Si el registro ya existe y tiene una plantilla, se actualiza esa misma.
    # Si existe pero no tiene Doc_ID, se crea una copia desde la plantilla universal.
    if doc_guardado and doc_guardado != doc_id_base and plantilla_guardada_actual:
        doc_id_empresa = doc_guardado
        carpeta_templates_id = obtener_id_carpeta_plantillas_empresas()
    else:
        if not doc_id_base:
            raise ValueError("No se encontró la fila 'Otra' con el Doc_ID de la plantilla universal en la hoja Empresas.")
        docs = obtener_servicio_docs()
        documento_base = docs.documents().get(documentId=doc_id_base).execute()
        if not _documento_contiene_marcador(documento_base):
            raise ValueError("La plantilla universal no contiene el marcador {{LOGO_EMPRESA}}. Agrégalo en el lugar del logo y vuelve a probar.")
        copia, carpeta_templates_id, _ = copiar_template_empresa(doc_id_base, nombre_final, nit_final)
        doc_id_empresa = copia["id"]

    # La plantilla específica de empresa conserva su propio nombre y NIT.
    # La plantilla universal «Otra» nunca se modifica.
    _log_busqueda_empresa(
        f"PLANTILLA EMPRESA: se guardará identidad en Doc_ID={doc_id_empresa}; "
        f"empresa={nombre_final}; NIT={nit_final}."
    )
    identidad_plantilla_ok = rellenar_identidad_en_plantilla_empresa(
        doc_id_empresa, nombre_final, nit_final
    )
    if not identidad_plantilla_ok:
        raise RuntimeError(
            "No se pudo confirmar el nombre y NIT dentro de la plantilla reutilizable. "
            "No se actualizará la fila Empresas con una plantilla incompleta."
        )

    docs = obtener_servicio_docs()
    documento_copia = docs.documents().get(documentId=doc_id_empresa).execute()
    texto_copia = json.dumps(documento_copia, ensure_ascii=False)
    tiene_marcador = _documento_contiene_marcador(documento_copia)
    tiene_imagen = "inlineObjectElement" in texto_copia
    logo_insertado = bool(tiene_imagen and not tiene_marcador)

    marca_agua_insertada = False
    if resultado.get("logo") and tiene_marcador:
        logo_insertado = insertar_logo_en_plantilla(
            doc_id_empresa,
            resultado["logo"],
            _clave_template_empresa(nombre_final, nit_final),
            carpeta_destino_id=carpeta_templates_id
        )
        marca_agua_insertada = bool(st.session_state.get("marca_agua_empresa_insertada", False))
    elif resultado.get("logo") and logo_insertado:
        # El logo superior ya existe en esta plantilla; reintenta solo la marca de agua.
        try:
            marca_agua_insertada = insertar_marca_agua_desde_logo(
                doc_id_empresa, resultado["logo"],
                _clave_template_empresa(nombre_final, nit_final),
                carpeta_destino_id=carpeta_templates_id
            )
        except Exception as exc_marca:
            st.session_state["error_marca_agua_empresa"] = f"{type(exc_marca).__name__}: {str(exc_marca)[:500]}"
            _log_busqueda_empresa("MARCA DE AGUA: reintento pendiente falló: " + st.session_state["error_marca_agua_empresa"])

    if logo_insertado and marca_agua_insertada:
        estado_logo = "logo-insertado"
    elif logo_insertado:
        estado_logo = "logo-insertado; marca-agua-pendiente"
    else:
        estado_logo = "falta-logo-revision manual"
    logo_url = _celda_texto((resultado.get("logo") or {}).get("url", ""))
    # Este guardado actualiza el registro encontrado; solo agrega una fila si
    # nombre y NIT no existen. La función vuelve a validar ambas claves.
    guardar_empresa_en_sheets(
        nombre_final, nit_final, doc_id_empresa, logo_url, estado_logo,
        _celda_texto(resultado.get("fuente_identidad", ""))
    )

    info = obtener_info_plantilla(doc_id_empresa)
    st.session_state.empresa = nombre_final
    st.session_state.nit = nit_final
    st.session_state.doc_id_plantilla = info["id"]
    st.session_state.nombre_plantilla = info.get("name", "Plantilla de empresa")
    st.session_state.plantilla_url = info.get("webViewLink", "")
    st.session_state.logo_empresa_en_template = bool(logo_insertado)
    st.session_state.marca_agua_empresa_insertada = bool(marca_agua_insertada)
    st.session_state.marca_agua_empresa_pendiente = bool(logo_insertado and not marca_agua_insertada)
    st.session_state.logo_empresa_pendiente = None if logo_insertado else resultado.get("logo")
    st.session_state.estado_logo_empresa = estado_logo
    st.session_state.estado_empresa_web = "Verificada" if resultado.get("empresa_verificada") else "revision manual"
    st.session_state.diagnostico_logo_empresa = resultado.get("diagnostico", "")
    st.session_state.busqueda_otra_completada = True
    st.session_state.logo_marcador_procesado = False
    st.session_state.empresa_seleccionada = "Otra"
    return nombre_final, nit_final, doc_id_empresa


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
        "whatsapp_autorizado", "whatsapp_confirmacion_estado", "whatsapp_documento_estado", "whatsapp_errores",
        "whatsapp_test_message_id", "whatsapp_test_recipient",
        "busqueda_otra_completada", "logo_empresa_pendiente", "logo_empresa_insertado",
        "logo_marcador_procesado", "estado_logo_empresa", "estado_empresa_web", "logo_empresa_en_template", "diagnostico_logo_empresa",
        "error_insercion_logo_empresa",
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
    """Conserva hasta 15 dígitos para admitir números internacionales E.164."""
    valor = str(st.session_state.get("telefono_widget", ""))
    st.session_state.telefono_widget = re.sub(r"\D", "", valor)[:15]


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
            telefono = st.text_input("Teléfono / WhatsApp", label_visibility="collapsed", placeholder="Ej. +1 5141234567 o +57 3001234567", key="telefono_widget", on_change=limpiar_telefono_widget)
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

        st.session_state.whatsapp_autorizado = st.checkbox(
            "Autorizo a Cesantías al Instante a enviarme por WhatsApp la confirmación de mi solicitud y las novedades del documento. (Obligatorio)",
            value=bool(st.session_state.get("whatsapp_autorizado", False)),
            key="whatsapp_consentimiento_widget"
        )
        st.caption("Debes marcar esta autorización para continuar con la solicitud y recibir las comunicaciones por WhatsApp.")

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
                    if not st.session_state.get("whatsapp_autorizado", False):
                        st.error("Para continuar, debes autorizar las comunicaciones por WhatsApp marcando la casilla correspondiente.")
                        st.stop()
                    if not all([saldo_limpio, monto_limpio, nombre.strip(), cedula_limpia, telefono_limpio, email_limpio, departamento, ciudad.strip()]):
                        st.error("Completa el saldo, el monto y los seis datos personales antes de continuar.")
                        st.stop()
                    if not st.session_state.get("fondo"):
                        st.error("Selecciona primero tu fondo de cesantías.")
                        st.stop()
                    if not (10 <= len(telefono_limpio) <= 15):
                        st.error("Escribe un teléfono válido con código de país: entre 10 y 15 dígitos en total. Ejemplo Canadá: +1 seguido de los 10 dígitos del número.")
                        st.stop()
                    # Los números colombianos de 10 dígitos reciben automáticamente el prefijo 57.
                    # Los números internacionales que ya incluyen código de país se conservan.
                    telefono_whatsapp = telefono_limpio
                    if len(telefono_whatsapp) == 10:
                        telefono_whatsapp = "57" + telefono_whatsapp
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
                    st.session_state.telefono = telefono_whatsapp
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
            "Si eliges «Otra», puedes escribir el nombre, el NIT o ambos. Verificaremos los datos después de registrar la solicitud."
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
            '<p>Selecciona «Otra» al inicio del listado para escribir el nombre, el NIT o ambos.</p></div></div>',
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
                            if not empresa_manual.strip() and not nit_manual.strip():
                                st.error("Escribe al menos uno de estos datos: nombre de la empresa o NIT.")
                                st.stop()
                            _iniciar_log_busqueda_empresa(empresa_manual, nit_manual)
                            with st.spinner("Verificando la empresa, creando su plantilla y guardando el Doc_ID en la base de empresas..."):
                                preparar_empresa_nueva_y_template(empresa_manual, nit_manual)
                        else:
                            resolver_empresa_y_plantilla(empresa_seleccionada)
                            st.session_state.empresa = empresa_seleccionada
                        if not st.session_state.get("nit"):
                            st.warning("No encontramos el NIT en las fuentes disponibles. La empresa y su plantilla quedarán registradas para revisión manual.")
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
                        _log_busqueda_empresa(f"ERROR FINAL: {type(exc).__name__}: {str(exc)}")
                        _log_busqueda_empresa("FIN: proceso detenido. No continuar con creación/actualización si la identidad no quedó validada.")
                        st.error(f"No se pudo validar la empresa o localizar su plantilla: {exc}")
                        st.download_button(
                            "Descargar registro técnico de esta búsqueda (.txt)",
                            data=_texto_log_busqueda_empresa(),
                            file_name=f"diagnostico_busqueda_empresa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key="descargar_log_busqueda_empresa"
                        )
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
                "departamento": st.session_state.departamento, "estado": "Pendiente",
                "whatsapp_autorizado": bool(st.session_state.get("whatsapp_autorizado", False)),
                "whatsapp_confirmacion_estado": "Pendiente" if st.session_state.get("whatsapp_autorizado", False) else "No autorizado",
                "whatsapp_documento_estado": "Pendiente" if st.session_state.get("whatsapp_autorizado", False) else "No autorizado",
                "estado_logo": "Pendiente de búsqueda" if (st.session_state.get("empresa") or st.session_state.get("nit")) else "No aplica",
                "logo_url": "",
                "estado_empresa": "Pendiente de verificación" if st.session_state.get("empresa_seleccionada") == "Otra" else "Registrada"
            }])
            updated_df = pd.concat([existing_data, nuevo_dato], ignore_index=True)
            conn.update(worksheet="Solicitudes", data=updated_df)
            st.session_state.solicitud_guardada = True
        except Exception as e:
            st.error(f"Error guardando en Google Sheets: {e}")
            if st.button("Reintentar", key="retry_sheets"):
                st.rerun()
            st.stop()

    # ---------- BÚSQUEDA DE EMPRESA/LOGO PARA «OTRA» (PYTHON, SIN N8N) ----------
    # La búsqueda debe ejecutarse también cuando el usuario solo proporciona el NIT.
    # Se ejecuta una sola vez después de registrar la solicitud. La búsqueda tiene
    # tiempos de espera cortos y nunca bloquea la generación de la carta si falla.
    if (st.session_state.get("empresa") or st.session_state.get("nit")) and not st.session_state.get("busqueda_otra_completada", False):
        with st.spinner("Estamos verificando los datos de la empresa. Si no encontramos el logo, prepararemos la carta sin él..."):
            resultado_busqueda = buscar_empresa_y_logo_python(
                st.session_state.get("empresa", ""),
                st.session_state.get("nit", "")
            )
            if resultado_busqueda.get("nombre"):
                st.session_state.empresa = resultado_busqueda["nombre"].upper()
            if resultado_busqueda.get("nit"):
                st.session_state.nit = resultado_busqueda["nit"]
            logo_insertado = False
            st.session_state.logo_empresa_pendiente = resultado_busqueda.get("logo")
            st.session_state.estado_logo_empresa = "Pendiente de inserción" if resultado_busqueda.get("logo") else "falta-logo-revision manual"
            st.session_state.estado_empresa_web = "Verificada" if resultado_busqueda.get("empresa_verificada") else "revision manual"
            st.session_state.diagnostico_logo_empresa = resultado_busqueda.get("diagnostico", "")

            # Si esta es una plantilla propia de empresa (no la plantilla maestra),
            # guardar el logo dentro de ella para que las siguientes solicitudes lo hereden.
            if resultado_busqueda.get("logo") and st.session_state.get("doc_id_plantilla"):
                try:
                    df_empresas_actual = _leer_hoja_empresas()
                    filas_maestra = df_empresas_actual[
                        df_empresas_actual["Nombre_Empresa"].astype(str).str.strip().str.casefold() == "otra"
                    ]
                    doc_id_maestro = _celda_texto(filas_maestra.iloc[0].get("Doc_ID", "")) if not filas_maestra.empty else ""
                    if st.session_state.doc_id_plantilla != doc_id_maestro:
                        carpeta_templates = obtener_id_carpeta_plantillas_empresas()
                        if st.session_state.get("logo_empresa_en_template", False) and st.session_state.get("marca_agua_empresa_pendiente", False):
                            # El logo pequeño ya está en la plantilla; reintenta solo la marca de agua central.
                            marca_ok = insertar_marca_agua_desde_logo(
                                st.session_state.doc_id_plantilla,
                                resultado_busqueda["logo"],
                                _clave_template_empresa(st.session_state.get("empresa", ""), st.session_state.get("nit", "")),
                                carpeta_destino_id=carpeta_templates
                            )
                            logo_insertado = True
                            marca_agua_insertada = bool(marca_ok)
                        else:
                            logo_insertado = insertar_logo_en_plantilla(
                                st.session_state.doc_id_plantilla,
                                resultado_busqueda["logo"],
                                _clave_template_empresa(st.session_state.get("empresa", ""), st.session_state.get("nit", "")),
                                carpeta_destino_id=carpeta_templates
                            )
                            marca_agua_insertada = bool(st.session_state.get("marca_agua_empresa_insertada", False))
                        if logo_insertado:
                            st.session_state.logo_empresa_en_template = True
                            st.session_state.marca_agua_empresa_insertada = marca_agua_insertada
                            st.session_state.marca_agua_empresa_pendiente = not marca_agua_insertada
                            st.session_state.logo_empresa_pendiente = None
                            estado_logo_final = "logo-insertado" if marca_agua_insertada else "logo-insertado; marca-agua-pendiente"
                            st.session_state.estado_logo_empresa = estado_logo_final
                            guardar_empresa_en_sheets(
                                st.session_state.get("empresa", ""),
                                st.session_state.get("nit", ""),
                                st.session_state.doc_id_plantilla,
                                resultado_busqueda["logo"].get("url", ""),
                                estado_logo_final
                            )
                except Exception:
                    # Conserva la imagen descargada para intentar insertarla en la copia de esta solicitud.
                    st.session_state.logo_empresa_en_template = False

            st.session_state.busqueda_otra_completada = True
            actualizar_estado_empresa_en_sheets(st.session_state.solicitud_id, resultado_busqueda)

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

    # ---------- RESOLVER SIEMPRE EL MARCADOR DEL LOGO ----------
    # Aunque la búsqueda no encuentre imagen, se elimina {{LOGO_EMPRESA}}
    # de la copia para que nunca aparezca como texto en la carta final.
    if not st.session_state.get("logo_marcador_procesado", False):
        try:
            if st.session_state.get("logo_empresa_en_template", False):
                # La copia de la solicitud ya hereda el logo insertado en la plantilla de empresa.
                logo_insertado = True
            else:
                logo_insertado = insertar_logo_en_plantilla(
                    st.session_state.doc_id_copia,
                    st.session_state.get("logo_empresa_pendiente"),
                    st.session_state.solicitud_id,
                    limpiar_marcador_si_falla=True
                )
            st.session_state.logo_empresa_insertado = bool(logo_insertado)
            st.session_state.logo_marcador_procesado = True
            error_logo = str(st.session_state.get("error_insercion_logo_empresa", "") or "").strip()
            if error_logo:
                _log_busqueda_empresa("LOGO: último error de inserción: " + error_logo[:700])
            if logo_insertado:
                st.session_state.estado_logo_empresa = (
                    "logo-insertado; marca-agua-pendiente"
                    if st.session_state.get("marca_agua_empresa_pendiente", False)
                    else "logo-insertado"
                )
            else:
                st.session_state.estado_logo_empresa = "falta-logo-revision manual"
        except Exception:
            st.session_state.logo_empresa_insertado = False
            st.session_state.estado_logo_empresa = "falta-logo-revision manual"
            # No bloqueamos la carta si la operación del logo falla.
            st.session_state.logo_marcador_procesado = True
        if not st.session_state.get("logo_empresa_insertado", False):
            detalle_logo = str(st.session_state.get("error_insercion_logo_empresa", "") or "").strip()
            if detalle_logo:
                st.warning("La empresa se identificó, pero el logo no pudo insertarse. Detalle técnico: " + detalle_logo[:500])
            elif not st.session_state.get("logo_empresa_pendiente"):
                st.warning("La empresa se identificó, pero no se pudo recuperar una imagen de logo utilizable. Abre el diagnóstico técnico al finalizar la solicitud para ver qué etapa falló.")
    if st.session_state.get("empresa") or st.session_state.get("nit"):
        # Conserva el estado final exacto solicitado para revisión administrativa.
        if not str(st.session_state.get("estado_logo_empresa", "")).lower().startswith("logo-insertado"):
            st.session_state.estado_logo_empresa = "falta-logo-revision manual"
        try:
            df_estado = conn.read(worksheet="Solicitudes", ttl=0).dropna(how="all")
            if "solicitud_id" in df_estado.columns:
                df_estado = _forzar_columnas_texto(df_estado, ("estado_logo",))
                filas_estado = df_estado.index[df_estado["solicitud_id"].astype(str) == str(st.session_state.solicitud_id)]
                if len(filas_estado):
                    df_estado.at[filas_estado[0], "estado_logo"] = st.session_state.estado_logo_empresa
                    conn.update(worksheet="Solicitudes", data=df_estado)
        except Exception:
            pass

    # ---------- RELLENAR LA COPIA (NUNCA LA PLANTILLA ORIGINAL) ----------
    if not st.session_state.documento_rellenado:
        try:
            motivo = str(st.session_state.proposito or "").strip()
            motivo = re.sub(r"^[^\wÁÉÍÓÚáéíóúÑñ]+", "", motivo).strip()
            fecha_documento = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y")
            valores = {
                "{{NOMBRE EMPRESA}}": str(st.session_state.empresa).upper(),
                "{{NOMBRE_EMPRESA}}": str(st.session_state.empresa).upper(),
                "{{NOMBRE_DE_LA_EMPRESA}}": str(st.session_state.empresa).upper(),
                "{{EMPRESA_NOMBRE}}": str(st.session_state.empresa).upper(),
                "{{RAZON_SOCIAL}}": str(st.session_state.empresa).upper(),
                "{{RAZON SOCIAL}}": str(st.session_state.empresa).upper(),
                "{{NIT}}": str(st.session_state.nit).upper(),
                "{{NUMERO_NIT}}": str(st.session_state.nit).upper(),
                "{{NIT_EMPRESA}}": str(st.session_state.nit).upper(),
                "{{NIT EMPRESA}}": str(st.session_state.nit).upper(),
                "{{NIT_DE_LA_EMPRESA}}": str(st.session_state.nit).upper(),
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

    # PRUEBA AUTOMATICA: al terminar la solicitud, envía hello_world
    # al destinatario autorizado configurado en [whatsapp].
    # Meta solo permite usar este destinatario de prueba durante esta etapa.
    if st.session_state.get("whatsapp_autorizado", False) and st.session_state.get("whatsapp_confirmacion_estado") != "Enviado":
        try:
            resultado_whatsapp = enviar_mensaje_prueba_meta()
            st.session_state.whatsapp_confirmacion_estado = "Enviado"
            st.session_state.whatsapp_test_message_id = resultado_whatsapp.get("message_id", "")
            st.session_state.whatsapp_test_recipient = resultado_whatsapp.get("recipient", "")
            st.session_state.whatsapp_errores = []
        except Exception as exc:
            st.session_state.whatsapp_confirmacion_estado = "Error"
            st.session_state.whatsapp_errores = [str(exc)]

    # La generación terminó correctamente. La confirmación se presenta en
    # una pantalla independiente para que el recorrido tenga un FINAL real.
    st.session_state.step = "final"
    st.rerun()


def render_final():
    """Confirmación final con número de solicitud."""
    render_brand_header(7)  # Los seis pasos aparecen completados.
    if st.session_state.get("whatsapp_confirmacion_estado") == "Enviado":
        st.success("WhatsApp: Meta aceptó el mensaje de prueba hello_world y lo envió al destinatario de prueba configurado.")
    elif st.session_state.get("whatsapp_confirmacion_estado") == "Error":
        st.warning("La solicitud se completó, pero no se pudo enviar el mensaje de WhatsApp de prueba: " + "; ".join(st.session_state.get("whatsapp_errores", [])))
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
        if st.session_state.get("log_busqueda_empresa"):
            with st.expander("Diagnóstico técnico de empresa y logo"):
                st.caption("Este registro permite distinguir si falló la búsqueda de la imagen, su descarga, la carga a Drive o la inserción en Google Docs.")
                st.download_button(
                    "Descargar diagnóstico de empresa y logo (.txt)",
                    data=_texto_log_busqueda_empresa(),
                    file_name=f"diagnostico_logo_{st.session_state.get('nit', 'empresa')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="descargar_diagnostico_logo_final",
                    use_container_width=True,
                )
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

    # Prueba privada de WhatsApp Meta; no altera las pantallas de los clientes.
    if st.query_params.get("configurar_whatsapp") == "1":
        render_configuracion_whatsapp()
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
