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

# ---------- SISTEMA VISUAL PREMIUM COMPLETAMENTE RESPONSIVO (MAQUETA EXACTA) ----------
st.markdown(r\"\"\"
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

/* Estilos de Contenedores de Encabezado */
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

/* Paneles de Contenido Unificados */
.st-key-screen_fund, .st-key-screen_data, .st-key-screen_summary, .st-key-screen_mission, .st-key-screen_company, .st-key-screen_processing, .st-key-screen_success {
 background:linear-gradient(180deg,#fff 0%,#fafdff 75%,#f0f8ff 100%)!important;
 border:1px solid #cbdff0!important;border-radius:26px!important;
 padding:clamp(1.05rem,2.8vw,2.2rem)!important;
 box-shadow:0 18px 55px #001b4933!important;
 max-width:1080px!important;
 margin:.65rem auto 1rem!important;
}

.screen-heading{display:flex;align-items:center;gap:.9rem;margin:.1rem 0 1.35rem}
.screen-icon{width:54px;height:54px;flex:0 0 54px;display:flex;align-items:center;justify-content:center;border-radius:16px;color:#fff;background:linear-gradient(145deg,#0879df,#05bce8);box-shadow:0 8px 20px #0874d833}
.screen-icon svg{width:27px;height:27px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.screen-heading h2{margin:0;color:var(--cia-navy);font-size:clamp(1.35rem,2.8vw,1.9rem);font-weight:900;letter-spacing:-.035em;line-height:1.15}
.screen-heading p{margin:.28rem 0 0;color:#526984;font-size:.96rem;line-height:1.45}

/* ESTRUCTURA FLEXBOX ESTRICTA PARA FILAS DE BOTONES (PREVIENE APILAMIENTO) */
.premium-flex-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
    margin-bottom: 20px;
}
.premium-flex-row {
    display: flex;
    flex-wrap: nowrap !important; /* Prohíbe terminantemente el colapso vertical en teléfonos */
    gap: 16px;
    width: 100%;
}
.premium-flex-col {
    flex: 1 1 50% !important;
    width: 50% !important;
    min-width: 0 !important;
}

/* Modificación de Componentes de Streamlit para Adaptación Estricta */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 16px !important;
}
[data-testid="stHorizontalBlock"] > div {
    flex: 1 1 50% !important;
    min-width: 0 !important;
}

/* Diseño de Tarjetas de Opciones Dinámicas */
.premium-card-btn {
    background: #ffffff !important;
    border: 1.5px solid #cbdff0 !important;
    border-radius: 20px !important;
    padding: 20px 15px !important;
    text-align: center !important;
    box-shadow: 0 6px 18px rgba(6,43,104,0.06) !important;
    cursor: pointer;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 160px;
}
.premium-card-btn:hover {
    transform: translateY(-3px) !important;
    border-color: #086fd0 !important;
    box-shadow: 0 12px 24px rgba(8,111,208,0.14) !important;
}
.premium-card-icon {
    font-size: 2.4rem;
    margin-bottom: 8px;
    line-height: 1;
}
.premium-card-title {
    color: #062b68;
    font-weight: 800;
    font-size: 1.15rem;
    margin-bottom: 4px;
}
.premium-card-desc {
    color: #60748d;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Controles de Inputs y Estética General */
.field-label{display:flex;align-items:center;gap:.48rem;margin:.52rem 0 .22rem;color:#10376f;font-size:.88rem;font-weight:850}
.field-label svg{width:18px;height:18px;stroke:#0878d2;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:0 0 18px}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label{color:var(--cia-navy)!important;font-weight:800!important}
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"]>div{min-height:48px;border:1.5px solid #c9dced!important;border-radius:13px!important;background:#fff!important;color:#17345c!important}

/* Botones de Navegación */
.stButton>button, [data-testid="stDownloadButton"] button, [data-testid="stLinkButton"] a{
 min-height:48px;border:1px solid #0874d8!important;border-radius:14px!important;
 padding:.7rem 1.1rem!important;color:#fff!important;
 background:linear-gradient(110deg,#073b8a,#0874d4 70%,#0aa6dc)!important;
 font-weight:850!important;font-size:.96rem!important;box-shadow:0 8px 19px #084a9728!important;
 width:100% !important;
}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 12px 25px #084a9738!important}

/* Estilos Específicos de Botón Atrás */
.st-key-fund_back button, .st-key-data_back button, .st-key-summary_back button, .st-key-mission_back button, .st-key-company_back button {
 background:#fff!important;color:#0752a0!important;border:1.5px solid #8fc6f0!important;box-shadow:none!important;
}

/* Portada Integrada Premium */
.hero-shell{position:relative;isolation:isolate;display:grid;grid-template-columns:1.04fr .96fr;max-width:1080px;min-height:545px;margin:.3rem auto 1rem;overflow:hidden;border-radius:27px;background:linear-gradient(135deg,#062c6c 0%,#073c8b 60%,#086fbd 100%);border:1px solid #1595df;box-shadow:0 22px 60px #00183e55}
.hero-shell:before{content:"";position:absolute;z-index:0;left:-7%;top:-20%;width:67%;height:44%;border-radius:0 0 75% 10%;background:linear-gradient(135deg,#fff 0%,#f2fbff 72%,#c1ebff 100%);transform:rotate(-5deg)}
.hero-copy{position:relative;z-index:2;display:flex;flex-direction:column;align-items:flex-start;padding:1.8rem clamp(1.25rem,3vw,2rem) 1.55rem}
.hero-logo{display:flex;align-items:center;justify-content:flex-start;width:min(100%,390px);height:112px;margin:-.2rem 0 1.15rem}
.hero-logo img{display:block;max-width:100%;max-height:108px;object-fit:contain;object-position:left center}
.hero-title{margin:.15rem 0 .85rem;color:#fff;font-size:clamp(2.1rem,4vw,3.4rem);font-weight:950;letter-spacing:-.055em;line-height:1.03}
.hero-title span{display:block;color:#13d0f2}
.hero-description{max-width:470px;margin:0 0 1.1rem;color:#e9f5ff;font-size:clamp(1rem,1.6vw,1.18rem);line-height:1.5}
.hero-benefits{display:grid;gap:.65rem;margin:.25rem 0 1.35rem;color:white;font-size:1.08rem;font-weight:800}
.hero-benefit{display:flex;align-items:center;gap:.7rem}
.hero-benefit i{font-style:normal;width:35px;height:35px;flex:0 0 35px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#12c7e8;color:#043c86;font-size:1.05rem;font-weight:950}
.hero-person{position:relative;min-height:545px;align-self:stretch;overflow:hidden;border-radius:0 0 0 105px}
.hero-person img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 20%}

/* Paneles de Resumen e Info Complementaria */
.summary-panel{padding:1.2rem;border:1px solid #d2e3f2;border-radius:20px;background:linear-gradient(135deg,#fff,#f0f7ff);box-shadow:0 8px 22px #082b6610}
.summary-check{width:72px;height:72px;margin:.2rem auto .8rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#22c83d,#0fa52f);color:#fff;font-size:2.8rem;font-weight:950}
.summary-item{padding:.7rem .8rem;margin:.3rem 0;border:1px solid #e0ebf5;border-radius:12px;background:#fff}
.summary-item small{display:block;color:#526981;font-size:.72rem;font-weight:800;text-transform:uppercase}
.summary-item strong{display:block;color:#102f60;font-size:.97rem;font-weight:850}

.mission-hero{padding:1.25rem 1.35rem;margin:.2rem 0 1rem;border-radius:20px;background:linear-gradient(120deg,#062e70,#0879cf);color:#fff}
.mission-hero h3{margin:0 0 .5rem;color:#fff;font-size:1.45rem;font-weight:900}
.mission-hero p{margin:0;color:#e9f6ff;line-height:1.6}
.mission-card{height:100%;padding:1rem;border-radius:17px;border:1px solid #d8e7f4;background:#fff;box-shadow:0 6px 18px #082b660d}
.mission-card .mission-symbol{width:43px;height:43px;margin-bottom:.65rem;display:flex;align-items:center;justify-content:center;border-radius:13px;color:#fff;background:linear-gradient(145deg,#0878d8,#12bce8)}
.mission-card strong{display:block;color:var(--cia-navy);font-size:.98rem;font-weight:900}
.mission-card p{margin:.35rem 0 0;color:#5b7189;font-size:.85rem;line-height:1.5}

.personal-tip{display:flex;gap:.9rem;align-items:center;padding:.95rem 1.1rem;margin:0 0 1.1rem;border:1px solid #bfe5fa;border-radius:17px;background:linear-gradient(110deg,#eaf7ff,#d9f4ff)}
.personal-tip-icon{width:48px;height:48px;flex:0 0 48px;display:flex;align-items:center;justify-content:center;border-radius:14px;color:#fff;background:linear-gradient(145deg,#0874d8,#10bde8);font-size:1.25rem}

.success-shell{max-width:1080px;margin:.55rem auto 1rem;padding:clamp(1.35rem,4vw,3rem);border-radius:26px;background:radial-gradient(circle at 50% 12%,#e2f4ff,#fff 58%,#eef8ff);border:1px solid #d3e5f4;text-align:center}
.success-check{width:92px;height:92px;margin:.2rem auto .9rem;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#12bce9,#0756c4);color:#fff;font-size:3.5rem;font-weight:950}
.success-shell h1{color:var(--cia-navy);font-size:clamp(2rem,4vw,3rem);font-weight:950}
.success-delivery{max-width:740px;margin:1.1rem auto;padding:1rem 1.15rem;border-radius:16px;background:#dff1ff;color:#083a7b;font-weight:750;text-align:left}

/* ADAPTACIÓN DE MEDIA QUERIES PARA DISPOSITIVOS MÓVILES */
@media(max-width:760px){
 .main .block-container{padding:.55rem .45rem 1.5rem!important}
 .brand-header{padding:.45rem .65rem;border-radius:14px}
 .brand-logo-wrap img{max-height:44px}
 .journey-wrap{padding:.55rem .18rem}
 .journey-step{font-size:.56rem}.journey-dot{width:24px;height:24px;font-size:.68rem}
 .hero-shell{grid-template-columns:1fr;min-height:0}
 .hero-person{min-height:240px;max-height:240px;border-radius:0 0 40px 44px}
 .hero-copy{padding:1.1rem 0.8rem}
 .hero-title{font-size:1.95rem}
 .premium-card-btn{min-height:125px;padding:12px 8px !important}
 .premium-card-icon{font-size:1.8rem;margin-bottom:4px}
 .premium-card-title{font-size:0.95rem}
 .premium-card-desc{font-size:0.75rem}
 [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
 }
}
</style>
\"\"\", unsafe_allow_html=True)

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

# ---------- BACKEND LOGIC: GOOGLE OAUTH & DRIVE ----------
def obtener_config_oauth():
    try:
        return dict(st.secrets["google_oauth"])
    except Exception as e:
        raise RuntimeError("Falta la sección [google_oauth] en Streamlit Secrets.") from e

@st.cache_resource
def obtener_almacen_pkce():
    return {"lock": Lock(), "verificadores": {}}

def guardar_verificador_pkce(state, code_verifier):
    almacen = obtener_almacen_pkce()
    ahora = time.time()
    with almacen["lock"]:
        vencidos = [clave for clave, valor in almacen["verificadores"].items() if ahora - valor["creado"] > 600]
        for clave in vencidos:
            almacen["verificadores"].pop(clave, None)
        almacen["verificadores"][state] = {"code_verifier": code_verifier, "creado": ahora}

def consumir_verificador_pkce(state):
    almacen = obtener_almacen_pkce()
    with almacen["lock"]:
        registro = almacen["verificadores"].pop(state, None)
    if not registro or time.time() - registro["creado"] > 600:
        return None
    return registro["code_verifier"]

def crear_flujo_oauth(state=None, code_verifier=None, autogenerate_code_verifier=True):
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
    flujo = Flow.from_client_config(config_cliente, scopes=[GOOGLE_DRIVE_SCOPE], state=state, code_verifier=code_verifier, autogenerate_code_verifier=autogenerate_code_verifier)
    flujo.redirect_uri = datos["redirect_uri"]
    return flujo

def crear_estado_oauth(clave_admin):
    contenido = f"{int(time.time())}:{secrets.token_urlsafe(24)}"
    firma = hmac.new(clave_admin.encode("utf-8"), contenido.encode("utf-8"), hashlib.sha256).hexdigest()
    contenido_codificado = base64.urlsafe_b64encode(contenido.encode("utf-8")).decode("ascii").rstrip("=")
    return f"{contenido_codificado}.{firma}"

def validar_estado_oauth(state, clave_admin):
    try:
        contenido_codificado, firma_recibida = state.split(".", 1)
        relleno = "=" * (-len(contenido_codificado) % 4)
        contenido = base64.urlsafe_b64decode(contenido_codificado + relleno).decode("utf-8")
        firma_esperada = hmac.new(clave_admin.encode("utf-8"), contenido.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(firma_recibida, firma_esperada): return False
        marca_tiempo = int(contenido.split(":", 1))
        return 0 <= time.time() - marca_tiempo <= 600
    except Exception:
        return False

def render_configuracion_drive():
    st.title("Configuración privada de Google Drive")
    try:
        datos = obtener_config_oauth()
        clave_correcta = str(datos.get("admin_key", ""))
        if not clave_correcta:
            st.error("Falta admin_key dentro de [google_oauth] en Streamlit Secrets.")
            st.stop()
    except Exception as e:
        st.error(str(e))
        st.stop()

    with st.form("form_admin_drive"):
        clave_ingresada = st.text_input("Clave administrativa", type="password")
        continuar = st.form_submit_button("Continuar")

    if continuar:
        if hmac.compare_digest(clave_ingresada, clave_correcta):
            st.session_state["admin_drive_autorizado"] = True
        else:
            st.error("La clave administrativa no coincide.")

    if not st.session_state.get("admin_drive_autorizado", False):
        st.stop()

    if str(datos.get("refresh_token", "")).strip():
        if st.button("Probar conexión a Google Drive", use_container_width=True):
            try:
                servicio = obtener_servicio_drive()
                perfil = servicio.about().get(fields="user(displayName,emailAddress)").execute()
                st.success(f"La conexión OAuth funciona. Cuenta: {perfil.get('user', {}).get('emailAddress')}")
            except Exception as e:
                st.error(f"Error de acceso a Drive: {e}")

    if st.button("Generar enlace de autorización de Google"):
        state = crear_estado_oauth(clave_correcta)
        flujo = crear_flujo_oauth(state=state)
        url_autorizacion, state_generado = flujo.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true")
        guardar_verificador_pkce(state_generado, flujo.code_verifier)
        st.session_state["url_autorizacion_drive"] = url_autorizacion

    url = st.session_state.get("url_autorizacion_drive")
    if url:
        st.link_button("Conectar la cuenta Gmail administradora", url, use_container_width=True)

def procesar_callback_oauth():
    parametros = st.query_params
    codigo = parametros.get("code")
    state = parametros.get("state")
    try:
        datos = obtener_config_oauth()
        clave_admin = str(datos.get("admin_key", ""))
        if not clave_admin or not validar_estado_oauth(state, clave_admin):
            raise RuntimeError("Validación expirada.")
        code_verifier = consumir_verificador_pkce(state)
        flujo = crear_flujo_oauth(state=state, code_verifier=code_verifier, autgenerate_code_verifier=False)
        flujo.fetch_token(code=codigo, code_verifier=code_verifier)
        st.session_state["oauth_pending_refresh_token"] = flujo.credentials.refresh_token
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Error en callback OAuth: {e}")

def render_token_oauth():
    st.title("Autorización de Google completada")
    with st.form("form_desbloquear_refresh_token"):
        clave_ingresada = st.text_input("Clave administrativa", type="password")
        desbloquear = st.form_submit_button("Mostrar token privado")
    if desbloquear:
        clave_correcta = str(obtener_config_oauth().get("admin_key", ""))
        if hmac.compare_digest(clave_ingresada, clave_correcta):
            st.code(st.session_state.get("oauth_pending_refresh_token", ""), language=None)

# ---------- LOGICA OPERATIVA DE CARPETAS Y ARCHIVOS ----------
@st.cache_resource
def obtener_servicio_drive():
    datos = obtener_config_oauth()
    credenciales = UserCredentials(token=None, refresh_token=str(datos.get("refresh_token", "")).strip(), token_uri="https://oauth2.googleapis.com/token", client_id=datos["client_id"], client_secret=datos["client_secret"], scopes=[GOOGLE_DRIVE_SCOPE])
    return build("drive", "v3", credentials=credenciales, cache_discovery=False)

@st.cache_data(ttl=300, show_spinner=False)
def obtener_info_plantilla(doc_id):
    servicio = obtener_servicio_drive()
    return servicio.files().get(fileId=str(doc_id).strip(), fields="id,name,mimeType,webViewLink", supportsAllDrives=True).execute()

@st.cache_resource
def obtener_servicio_docs():
    datos = obtener_config_oauth()
    credenciales = UserCredentials(token=None, refresh_token=str(datos.get("refresh_token", "")).strip(), token_uri="https://oauth2.googleapis.com/token", client_id=datos["client_id"], client_secret=datos["client_secret"], scopes=[GOOGLE_DRIVE_SCOPE])
    return build("docs", "v1", credentials=credenciales, cache_discovery=False)

def obtener_id_carpeta_solicitudes():
    datos = obtener_config_oauth()
    folder_id = str(datos.get("solicitudes_folder_id", "")).strip()
    servicio = obtener_servicio_drive()
    carpeta = servicio.files().get(fileId=folder_id, fields="id,name,mimeType,trashed").execute()
    return folder_id

def copiar_plantilla(doc_id, solicitud_id, nombre_persona):
    servicio = obtener_servicio_drive()
    folder_id = obtener_id_carpeta_solicitudes()
    nombre_seguro = re.sub(r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ_-]+", "_", str(nombre_persona)).strip("_")
    return servicio.files().copy(fileId=str(doc_id).strip(), body={"name": f"Solicitud_{solicitud_id}_{nombre_seguro}"[:180], "parents": [folder_id]}, supportsAllDrives=True, fields="id,name,webViewLink,parents").execute()

def rellenar_plantilla_google_docs(document_id, valores):
    servicio = obtener_servicio_docs()
    solicitudes = [{"replaceAllText": {"containsText": {"text": m, "matchCase": True}, "replaceText": str(v).upper()}} for m, v in valores.items()]
    return servicio.documents().batchUpdate(documentId=document_id, body={"requests": solicitudes}).execute()

def exportar_google_doc_a_pdf(document_id, solicitud_id, nombre_persona):
    servicio = obtener_servicio_drive()
    folder_id = obtener_id_carpeta_solicitudes()
    nombre_seguro = re.sub(r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ_-]+", "_", str(nombre_persona)).strip("_")
    nombre_pdf = f"Solicitud_{solicitud_id}_{nombre_seguro}.pdf"[:180]
    contenido_pdf = servicio.files().export(fileId=document_id, mimeType="application/pdf").execute()
    media = MediaIoBaseUpload(BytesIO(contenido_pdf), mimetype="application/pdf", resumable=False)
    return servicio.files().create(body={"name": nombre_pdf, "mimeType": "application/pdf", "parents": [folder_id]}, media_body=media, fields="id,name,webViewLink").execute()

# ---------- GESTIÓN VISUAL Y AUXILIARES DE RECORRIDO ----------
def obtener_logo_app_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for folder in [os.path.join(base_dir, "assets"), base_dir]:
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                if "logo" in file.lower() and os.path.isfile(os.path.join(folder, file)): return os.path.join(folder, file)
    return None

def obtener_imagen_hero_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, "assets", "hero_mujer.png")
    return ruta if os.path.isfile(ruta) else None

def imagen_data_uri(ruta):
    if not ruta or not os.path.isfile(ruta): return ""
    mime = mimetypes.guess_type(ruta) or "image/png"
    with open(ruta, "rb") as f: data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"

def icon_svg(nombre):
    paths = {
        "fund": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5M9 21v-7h6v7"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
        "file": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
        "check": '<path d="m5 12 4 4L19 6"/>',
        "mission": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "building": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M9 7h1m4 0h1M9 11h1m4 0h1M9 15h1m4 0h1M10 21v-3h4v3"/>',
        "phone": '<path d="M6.5 3.5 9 3 l2 5-2 1.5a14 14 0 0 0 5.5 5.5L16 13l5 2-.5 2.5A3 3 0 0 1 17.5 20C9 19 5 15 4 6.5a3 3 0 0 1 2.5-3Z"/>',
        "pin": '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
        "wallet": '<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 8h18M16 14h2"/>',
    }
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">{paths.get(nombre, paths["file"])}</svg>'

def render_screen_heading(icono, titulo, subtitulo):
    st.markdown(f'<div class="screen-heading"><div class="screen-icon">{icon_svg(icono)}</div><div><h2>{html.escape(titulo)}</h2><p>{html.escape(subtitulo)}</p></div></div>', unsafe_allow_html=True)

def render_field_label(icono, texto):
    st.markdown(f'<div class="field-label">{icon_svg(icono)}<span>{html.escape(texto)}</span></div>', unsafe_allow_html=True)

def render_brand_header(etapa=2):
    logo_uri = imagen_data_uri(obtener_logo_app_path())
    logo_html = f'<img src=\"{logo_uri}\" alt=\"Logo\">' if logo_uri else '<strong>Cesantías al Instante</strong>'
    st.markdown(f'<div class="brand-header"><div class="brand-logo-wrap">{logo_html}</div><div class="brand-trust"><span>✓</span> Trámite fácil y seguro</div></div>', unsafe_allow_html=True)
    etiquetas = ["Inicio", "Motivo", "Datos", "Resumen", "Misión", "Empresa"]
    pasos = [f'<div class="journey-step {\"active\" if n==etapa else (\"done\" if n<etapa else \"\")}\"><div class="journey-dot">{\"✓\" if n<etapa else n}</div><span>{et}</span></div>' for n, et in enumerate(etiquetas, 1)]
    st.markdown(f'<div class="journey-wrap"><div class="journey">{"".join(pasos)}</div></div>', unsafe_allow_html=True)

def reiniciar_solicitud():
    for k in ['proposito', 'monto', 'monto_limpio', 'fondo', 'nombre', 'cedula', 'telefono', 'email', 'empresa', 'nit', 'ciudad', 'departamento', 'empresa_manual', 'nit_manual', 'empresa_seleccionada', 'saldo_verificado', 'saldo_limpio', 'solicitud_guardada', 'doc_id_plantilla', 'doc_id_copia', 'pdf_generado']:
        st.session_state[k] = ""

# ---------- PANTALLA 1: PORTADA INTEGRADA PREMIUM ----------
def render_landing():
    logo_html = f'<img src=\"{imagen_data_uri(obtener_logo_app_path())}\" alt=\"Logo\">' if obtener_logo_app_path() else '<strong>Cesantías al Instante</strong>'
    hero_html = f'<img src=\"{imagen_data_uri(obtener_imagen_hero_path())}\" alt=\"Hero\">' if obtener_imagen_hero_path() else ''
    
    with st.container(key="landing_wrap"):
        st.markdown(f\"\"\"
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
        \"\"\", unsafe_allow_html=True)
        if st.button("Comenzar ahora  ➜", key="landing_start"):
            reiniciar_solicitud()
            st.session_state.step = "seleccionar_fondo"
            st.rerun()

# ---------- PANTALLA 2: SELECCIÓN DE MOTIVO (CUADRÍCULA MAQUETA EXACTA) ----------
def render_seleccionar_fondo():
    render_brand_header(2)
    with st.container(key="screen_fund"):
        render_screen_heading("fund", "¿Cuál es el motivo de tu retiro?", "Selecciona la opción que mejor se ajuste a tu caso.")
        
        st.markdown(\"\"\"
        <div class="premium-flex-grid">
            <div class="premium-flex-row">
                <div class="premium-flex-col"><div class="premium-card-btn"><div class="premium-card-icon">🏠</div><div class="premium-card-title">Vivienda</div><div class="premium-card-desc">Compra o mejora de vivienda</div></div></div>
                <div class="premium-flex-col"><div class="premium-card-btn"><div class="premium-card-icon">🎓</div><div class="premium-card-title">Educación</div><div class="premium-card-desc">Estudios propios o de tus hijos</div></div></div>
            </div>
            <div class="premium-flex-row">
                <div class="premium-flex-col"><div class="premium-card-btn"><div class="premium-card-icon">➕</div><div class="premium-card-title">Salud</div><div class="premium-card-desc">Tratamientos médicos</div></div></div>
                <div class="premium-flex-col"><div class="premium-card-btn"><div class="premium-card-icon">🌴</div><div class="premium-card-title">Vacaciones</div><div class="premium-card-desc">Descanso y bienestar</div></div></div>
            </div>
            <div class="premium-flex-row">
                <div class="premium-flex-col"><div class="premium-card-btn"><div class="premium-card-icon">🚘</div><div class="premium-card-title">Vehículo</div><div class="premium-card-desc">Compra de vehículo</div></div></div>
                <div class="premium-flex-col"><div class="premium-card-btn"><div class="premium-card-icon">•••</div><div class="premium-card-title">Otro motivo</div><div class="premium-card-desc">Otra razón válida</div></div></div>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            opcion = st.selectbox("Selecciona formalmente el motivo:", ["", "Vivienda", "Educación", "Salud", "Vacaciones", "Vehículo", "Otro motivo"], index=0, key="motivo_dropdown")
        
        st.markdown("<br>", unsafe_allow_html=True)
        nav_c1, nav_c2 = st.columns(2)
        with nav_c1:
            if st.button("← Atrás", key="fund_back"):
                st.session_state.step = "landing"
                st.rerun()
        with nav_c2:
            if st.button("Siguiente →", key="fund_continue"):
                if not opcion:
                    st.error("Por favor, selecciona una opción de la lista para continuar.")
                else:
                    st.session_state.fondo = opcion
                    st.session_state.step = "datos_personales"
                    st.rerun()

# ---------- PANTALLA 3: DATOS PERSONALES ----------
def render_datos_personales():
    render_brand_header(3)
    with st.container(key="screen_data"):
        render_screen_heading("user", "Datos de tu solicitud", "Ingresa la información básica para la generación de la carta.")
        
        c_saldo, c_monto = st.columns(2)
        with c_saldo:
            render_field_label("wallet", "Saldo disponible (COP)")
            saldo_raw = st.text_input("Saldo", label_visibility="collapsed", placeholder="Ej. 1234567", key="saldo_widget")
        with c_monto:
            render_field_label("wallet", "Monto que deseas retirar (COP)")
            monto_raw = st.text_input("Monto", label_visibility="collapsed", placeholder="Ej. 900000", key="monto_raw_widget")
            
        c1, c2 = st.columns(2)
        with c1:
            render_field_label("user", "Nombre completo")
            nombre = st.text_input("Nombre", label_visibility="collapsed", placeholder="Como aparece en la cédula", key="nombre_widget")
            render_field_label("file", "Cédula")
            cedula = st.text_input("Cédula", label_visibility="collapsed", placeholder="Solo números", key="cedula_widget")
        with c2:
            render_field_label("phone", "Celular (WhatsApp)")
            telefono = st.text_input("Celular", label_visibility="collapsed", placeholder="3001234567", key="telefono_widget")
            render_field_label("mail", "Correo electrónico")
            email_val = st.text_input("Correo", label_visibility="collapsed", placeholder="tu@email.com", key="email_widget")
            
        c3, c4 = st.columns(2)
        with c3:
            render_field_label("pin", "Departamento")
            deptos = ["Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá, D.C.", "Bolívar", "Boyacá", "Caldas", "Cundinamarca", "Santander", "Valle del Cauca"]
            departamento = st.selectbox("Depto", [""] + deptos, label_visibility="collapsed", key="departamento_widget")
        with c4:
            render_field_label("pin", "Ciudad")
            ciudad = st.text_input("Ciudad", label_visibility="collapsed", placeholder="Escribe tu ciudad", key="ciudad_widget")
            
        st.markdown("<br>", unsafe_allow_html=True)
        nav_c1, nav_c2 = st.columns(2)
        with nav_c1:
            if st.button("← Atrás", key="data_back"):
                st.session_state.step = "seleccionar_fondo"
                st.rerun()
        with nav_c2:
            if st.button("Siguiente →", key="data_continue"):
                saldo_limpio = re.sub(r"\D", "", str(saldo_raw))
                monto_limpio = re.sub(r"\D", "", str(monto_raw))
                if not all([saldo_limpio, monto_limpio, nombre.strip(), cedula.strip(), telefono.strip(), email_val.strip(), departamento, ciudad.strip()]):
                    st.error("Todos los campos son obligatorios.")
                else:
                    st.session_state.proposito = "Retiro de cesantías"
                    st.session_state.saldo_limpio = saldo_limpio
                    st.session_state.saldo_verificado = f"${int(saldo_limpio):,}".replace(",", ".")
                    st.session_state.monto = f"{int(monto_limpio):,}".replace(",", ".")
                    st.session_state.monto_limpio = monto_limpio
                    st.session_state.nombre = nombre.strip()
                    st.session_state.cedula = cedula
                    st.session_state.telefono = telefono
                    st.session_state.email = email_val.strip()
                    st.session_state.departamento = departamento
                    st.session_state.ciudad = ciudad.strip()
                    st.session_state.step = "resumen"
                    st.rerun()

# ---------- PANTALLA 4: RESUMEN DE LA SOLICITUD ----------
def render_resumen():
    render_brand_header(4)
    with st.container(key="screen_summary"):
        render_screen_heading("file", "Resumen de tu solicitud", "Verifica que toda la información sea correcta.")
        
        with st.container(key="summary_panel"):
            filas = [
                ("Motivo de Retiro", st.session_state.get("fondo", "")), ("Nombre completo", st.session_state.get("nombre", "")),
                ("Cédula", st.session_state.get("cedula", "")), ("Celular (WhatsApp)", st.session_state.get("telefono", "")),
                ("Correo electrónico", st.session_state.get("email", "")), ("Ciudad/Depto", f"{st.session_state.get('ciudad')}, {st.session_state.get('departamento')}"),
                ("Monto solicitado", f"${st.session_state.get('monto')}")
            ]
            cols = st.columns(2)
            for idx, (lbl, val) in enumerate(filas):
                with cols[idx % 2]:
                    st.markdown(f'<div class="summary-item"><small>{lbl}</small><strong>{val}</strong></div>', unsafe_allow_html=True)
                    
        st.markdown("<br>", unsafe_allow_html=True)
        nav_c1, nav_c2 = st.columns(2)
        with nav_c1:
            if st.button("← Atrás", key="summary_back"):
                st.session_state.step = "datos_personales"
                st.rerun()
        with nav_c2:
            if st.button("Siguiente →", key="summary_continue"):
                st.session_state.step = "mision"
                st.rerun()

# ---------- PANTALLA 5: NUESTRA MISIÓN ----------
def render_mision():
    render_brand_header(5)
    with st.container(key="screen_mission"):
        render_screen_heading("mission", "Nuestra misión", "Acompañamiento transparente en la generación de tus cartas.")
        st.markdown('<div class="mission-hero"><h3>Hacemos más sencillo tu proceso</h3><p>Compilamos tus requerimientos bajo estándares corporativos legales.</p></div>', unsafe_allow_html=True)
        
        nav_c1, nav_c2 = st.columns(2)
        with nav_c1:
            if st.button("← Atrás", key="mission_back"):
                st.session_state.step = "resumen"
                st.rerun()
        with nav_c2:
            if st.button("Siguiente →", key="mission_continue"):
                st.session_state.step = "empresa"
                st.rerun()

# ---------- PANTALLA 6: ASOCIACIÓN DE EMPRESA ----------
def resolver_empresa_y_plantilla(empresa_seleccionada, empresa_manual="", nit_manual=""):
    df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
    empresa_valor = empresa_seleccionada
    nit_auto = ""
    doc_id_auto = ""

    if empresa_seleccionada == "Otra":
        empresa_valor = str(empresa_manual or "").strip()
        nit_auto = str(nit_manual or "").strip()
        filas_otra = df_empresas[df_empresas["Nombre_Empresa"].astype(str).str.strip().str.casefold() == "otra"]
        if not filas_otra.empty: doc_id_auto = str(filas_otra["Doc_ID"].iloc).strip()
    else:
        filtro = df_empresas["Nombre_Empresa"].astype(str).str.strip() == empresa_seleccionada.strip()
        if filtro.any():
            fila = df_empresas.loc[filtro].iloc
            doc_id_auto = str(fila.get("Doc_ID", "")).strip()
            nit_auto = str(fila.get("NIT", "")).strip()

    st.session_state.empresa = empresa_valor
    st.session_state.nit = nit_auto
    st.session_state.doc_id_plantilla = doc_id_auto
    return df_empresas

def render_empresa():
    render_brand_header(6)
    with st.container(key="screen_company"):
        render_screen_heading("building", "Empresa donde trabajas", "Selecciona tu empresa para vincular el NIT corporativo.")
        
        df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
        lista_empresas = list(dict.fromkeys(df_empresas["Nombre_Empresa"].dropna().astype(str).str.strip().tolist()))
        if "Otra" in lista_empresas: lista_empresas.remove("Otra")
        
        empresa_seleccionada = st.selectbox("Selecciona tu empresa de la lista:", [""] + lista_empresas + ["Otra"], key="empresa_widget")
        
        empresa_manual = ""
        nit_manual = ""
        if empresa_seleccionada == "Otra":
            c1, c2 = st.columns(2)
            with c1: empresa_manual = st.text_input("Nombre de la empresa", placeholder="Razón social")
            with c2: nit_manual = st.text_input("NIT de la empresa", placeholder="900.123.456-7")
            
        st.markdown("<br>", unsafe_allow_html=True)
        nav_c1, nav_c2 = st.columns(2)
        with nav_c1:
            if st.button("← Atrás", key="company_back"):
                st.session_state.step = "mision"
                st.rerun()
        with nav_c2:
            if st.button("Confirmar solicitud ✓", key="company_submit"):
                if not empresa_seleccionada:
                    st.error("Selecciona una empresa.")
                else:
                    resolver_empresa_y_plantilla(empresa_seleccionada, empresa_manual, nit_manual)
                    st.session_state.step = "generando"
                    st.rerun()

# ---------- PROCESAMIENTO AUTOMATIZADO DE PDF ----------
def render_generando():
    render_brand_header(6)
    with st.container(key="screen_processing"):
        render_screen_heading("file", "Generando documento...", "Procesando los datos de forma segura.")

    if not st.session_state.solicitud_guardada:
        solicitud_id = f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        st.session_state.solicitud_id = solicitud_id
        try:
            existing_data = conn.read(worksheet="Solicitudes", ttl=0).dropna(how="all")
            nuevo_dato = pd.DataFrame([{
                "solicitud_id": solicitud_id, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre": st.session_state.nombre, "cedula": st.session_state.cedula,
                "telefono": st.session_state.telefono, "email": st.session_state.email,
                "nit": st.session_state.nit, "empresa": st.session_state.empresa,
                "fondo": st.session_state.fondo, "motivo": st.session_state.proposito,
                "monto": str(st.session_state.monto_limpio), "ciudad": st.session_state.ciudad,
                "departamento": st.session_state.departamento, "estado": "Pendiente"
            }])
            conn.update(worksheet="Solicitudes", data=pd.concat([existing_data, nuevo_dato], ignore_index=True))
            st.session_state.solicitud_guardada = True
        except Exception as e:
            st.error(f"Error Sheets: {e}"); st.stop()

    if not st.session_state.doc_id_copia:
        try:
            copia = copiar_plantilla(st.session_state.doc_id_plantilla, st.session_state.solicitud_id, st.session_state.nombre)
            st.session_state.doc_id_copia = copia["id"]
        except Exception as e:
            st.error(f"Error Drive: {e}"); st.stop()

    if not st.session_state.documento_rellenado:
        try:
            valores = {
                "{{FONDO_CESANTIAS}}": str(st.session_state.fondo).upper(),
                "{{NOMBRE_TRABAJADOR}}": str(st.session_state.nombre).upper(),
                "{{CEDULA}}": str(st.session_state.cedula),
                "{{MONTO_RETIRO}}": str(st.session_state.monto).upper(),
                "{{MOTIVO_RETIRO}}": str(st.session_state.fondo).upper(),
                "{{CIUDAD}}": str(st.session_state.ciudad).upper(),
                "{{DEPARTAMENTO}}": str(st.session_state.departamento).upper(),
                "{{FECHA}}": datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y")
            }
            rellenar_plantilla_google_docs(st.session_state.doc_id_copia, valores)
            st.session_state.documento_rellenado = True
        except Exception as e:
            st.error(f"Error Docs: {e}"); st.stop()

    if not st.session_state.pdf_generado:
        try:
            archivo_pdf = exportar_google_doc_a_pdf(st.session_state.doc_id_copia, st.session_state.solicitud_id, st.session_state.nombre)
            st.session_state.pdf_url = archivo_pdf.get("webViewLink")
            st.session_state.pdf_generado = True
        except Exception as e:
            st.error(f"Error PDF: {e}"); st.stop()

    st.markdown(f\"\"\"
    <section class="success-shell">
      <div class="success-check">✓</div>
      <h1>¡Solicitud Procesada!</h1>
      <p>Tu documentación ha sido estructurada con éxito bajo el radicado: <strong>{st.session_state.solicitud_id}</strong></p>
      <div class="success-delivery">Recibirás la confirmación formal en tu correo y WhatsApp registrados dentro de los próximos minutos.</div>
    </section>
    \"\"\", unsafe_allow_html=True)
    
    if st.session_state.pdf_url:
        st.link_button("📥 Descargar mi carta editable (PDF)", st.session_state.pdf_url)
    if st.button("Volver al inicio", key="finish_home"):
        st.session_state.step = 'landing'
        st.rerun()

# ---------- CONTROLADOR MAIN ----------
def main():
    if st.query_params.get("code") or st.query_params.get("error"):
        procesar_callback_oauth()
    if st.session_state.get("oauth_pending_refresh_token"):
        render_token_oauth(); return
    if st.query_params.get("configurar_drive") == "1":
        render_configuracion_drive(); return

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
