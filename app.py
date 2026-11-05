import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import re
import io
from streamlit_gsheets import GSheetsConnection
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ---------- CONFIG ----------
st.set_page_config(page_title="Cesantías al Instante", layout="centered")

# ---------- CSS PREMIUM ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: linear-gradient(145deg, #F8FAFC 0%, #EDF2F7 100%); padding: 0 !important; }
    .glass-container {
        background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border-radius: 32px; padding: 2rem 1.5rem; margin: 1rem auto; max-width: 480px;
        box-shadow: 0 20px 60px rgba(10, 37, 64, 0.08); border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #0A2540; text-align: center; line-height: 1.1; margin-bottom: 0.2rem; }
    .main-title span { background: linear-gradient(135deg, #0066FF, #00C853); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sub-title { font-size: 1.1rem; color: #64748B; text-align: center; margin-bottom: 1.5rem; font-weight: 400; }
    .hero-icon { text-align: center; font-size: 4.5rem; margin-bottom: 0.5rem; animation: float 3s ease-in-out infinite; }
    @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
    .benefit-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0.8rem; margin: 1.5rem 0; }
    .benefit-card { background: white; padding: 1.2rem 0.5rem; border-radius: 16px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border: 1px solid #E2E8F0; transition: all 0.3s; }
    .benefit-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
    .benefit-card .icon { font-size: 2.2rem; display: block; margin-bottom: 0.3rem; }
    .benefit-card h4 { margin: 0; font-size: 0.85rem; font-weight: 700; color: #0A2540; }
    .benefit-card p { margin: 0.2rem 0 0 0; font-size: 0.7rem; color: #94A3B8; }
    .stButton > button { background: linear-gradient(135deg, #0066FF, #00C853) !important; color: white !important; font-weight: 700 !important; border-radius: 60px !important; width: 100% !important; padding: 0.9rem !important; font-size: 1.1rem !important; border: none !important; transition: all 0.3s ease !important; box-shadow: 0 8px 25px rgba(0, 102, 255, 0.25) !important; letter-spacing: 0.3px; }
    .stButton > button:hover { transform: scale(1.02) !important; box-shadow: 0 12px 35px rgba(0, 102, 255, 0.35) !important; }
    .stButton > button:active { transform: scale(0.97) !important; }
    .stRadio > div { display: flex; flex-wrap: wrap; gap: 0.8rem; justify-content: center; }
    .stRadio > div > label { background: white; border: 2px solid #E2E8F0; border-radius: 16px; padding: 0.9rem 1.2rem; cursor: pointer; transition: all 0.2s ease; flex: 1; min-width: 120px; text-align: center; font-weight: 600; color: #0A2540; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
    .stRadio > div > label:hover { border-color: #0066FF; background: #F0F7FF; transform: translateY(-2px); }
    .stRadio > div > label > div { display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
    .stRadio > div > label[data-checked="true"] { border-color: #0066FF; background: #F0F7FF; box-shadow: 0 4px 12px rgba(0, 102, 255, 0.15); }
    .stTextInput > div > div > input { border-radius: 16px !important; border: 2px solid #E2E8F0 !important; padding: 0.9rem 1.2rem !important; font-size: 1rem !important; transition: all 0.3s !important; background: white; }
    .stTextInput > div > div > input:focus { border-color: #0066FF !important; box-shadow: 0 0 0 4px rgba(0, 102, 255, 0.1) !important; }
    .progress-container { background: #E2E8F0; border-radius: 40px; height: 6px; margin: 1.5rem 0 1rem 0; overflow: hidden; }
    .progress-bar { height: 100%; border-radius: 40px; background: linear-gradient(90deg, #0066FF, #00C853); transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1); }
    .step-text { text-align: center; color: #64748B; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 0.3rem; }
    .result-card { background: white; padding: 1.5rem; border-radius: 20px; border-left: 6px solid #00C853; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin: 1rem 0; }
    .price-tag { background: linear-gradient(135deg, #0066FF, #00C853); color: white; padding: 0.6rem 2rem; border-radius: 60px; display: inline-block; font-weight: 800; font-size: 2rem; margin: 0.5rem 0; box-shadow: 0 8px 20px rgba(0, 102, 255, 0.2); }
    .phone-number { background: #0A2540; color: white; padding: 1rem; border-radius: 20px; text-align: center; font-size: 2rem; font-weight: 800; letter-spacing: 1px; margin: 0.5rem 0; box-shadow: 0 8px 24px rgba(10, 37, 64, 0.15); display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
    .verified-badge { background: #00C853; color: white; padding: 0.2rem 0.8rem; border-radius: 30px; font-size: 0.75rem; font-weight: 700; display: inline-block; }
    @media (max-width: 480px) {
        .glass-container { padding: 1.5rem 1rem; border-radius: 24px; margin: 0.5rem 0.5rem; }
        .main-title { font-size: 2.2rem; }
        .phone-number { font-size: 1.5rem; padding: 0.8rem; }
        .benefit-grid { grid-template-columns: 1fr 1fr; }
    }
</style>
""", unsafe_allow_html=True)

# ---------- ESTADO ----------
if 'step' not in st.session_state: st.session_state.step = 'landing'
for key in ['proposito', 'monto', 'monto_limpio', 'fondo', 'nombre', 'cedula', 'telefono', 'email', 'empresa', 'nit', 'saldo_verificado', 'saldo_limpio', 'solicitud_guardada', 'pdf_bytes']:
    if key not in st.session_state: st.session_state[key] = ""

conn = st.connection("gsheets", type=GSheetsConnection)

# ---------- CONEXIÓN A GOOGLE DRIVE/DOCS ----------
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
try:
    CREDS = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    DRIVE_SERVICE = build('drive', 'v3', credentials=CREDS)
    DOCS_SERVICE = build('docs', 'v1', credentials=CREDS)
except Exception as e:
    st.error(f"Error cargando credentials.json: {e}")

def generar_pdf(doc_id, datos):
    """Copia la plantilla, rellena los datos y exporta a PDF."""
    # 1. Copiar la plantilla
    copy_title = f"Carta_{datos['nombre']}_{datos['cedula']}"
    body = {'name': copy_title}
    copia = DRIVE_SERVICE.files().copy(fileId=doc_id, body=body).execute()
    copia_id = copia.get('id')

    # 2. Reemplazar el texto
    requests = [
        {'replaceAllText': {'containsText': {'text': '{{NOMBRE}}', 'matchCase': True}, 'replaceText': datos['nombre']}},
        {'replaceAllText': {'containsText': {'text': '{{CEDULA}}', 'matchCase': True}, 'replaceText': datos['cedula']}},
        {'replaceAllText': {'containsText': {'text': '{{MONTO}}', 'matchCase': True}, 'replaceText': datos['monto']}},
        {'replaceAllText': {'containsText': {'text': '{{FONDO}}', 'matchCase': True}, 'replaceText': datos['fondo']}},
        {'replaceAllText': {'containsText': {'text': '{{MOTIVO}}', 'matchCase': True}, 'replaceText': datos['motivo']}}
    ]
    DOCS_SERVICE.documents().batchUpdate(documentId=copia_id, body={'requests': requests}).execute()

    # 3. Exportar a PDF
    request_pdf = DRIVE_SERVICE.files().export_media(fileId=copia_id, mimeType='application/pdf')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_pdf)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    # 4. Borrar la copia temporal
    DRIVE_SERVICE.files().delete(fileId=copia_id).execute()

    return fh.getvalue()

# ---------- PANTALLAS ----------
# (Las pantallas landing, pregunta1, pregunta2, verificar_saldo, monto_exacto y resultados se mantienen igual)
# ... [Aquí van las funciones render_landing, render_pregunta1, render_pregunta2, render_verificar_saldo, render_monto_exacto y render_resultados tal cual las tienes] ...

def render_generando():
    st.markdown("""
    <div class="glass-container" style="text-align:center;">
        <h3 style="color:#0A2540;font-weight:700;">🔄 Procesando...</h3>
        <p style="color:#64748B;">Buscando tu plantilla y generando tu carta.</p>
    """, unsafe_allow_html=True)

    # 1. Guardar en Google Sheets (solo una vez)
    if not st.session_state.solicitud_guardada:
        solicitud_id = f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            existing_data = conn.read(worksheet="Solicitudes", ttl=0).dropna(how="all")
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
                "monto": st.session_state.monto,
                "estado": "Pendiente"
            }])
            updated_df = pd.concat([existing_data, nuevo_dato], ignore_index=True)
            conn.update(worksheet="Solicitudes", data=updated_df)
            st.session_state.solicitud_guardada = True
        except Exception as e:
            st.error(f"Error guardando en Google Sheets: {e}")
            if st.button("Reintentar"):
                st.rerun()
            st.stop()

    # 2. Generar PDF si no existe
    if not st.session_state.pdf_bytes:
        try:
            # Obtener el Doc_ID de la hoja Empresas
            df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
            fila = df_empresas[df_empresas["Nombre_Empresa"] == st.session_state.empresa].iloc[0]
            doc_id = str(fila["Doc_ID"]).strip()

            datos = {
                "nombre": st.session_state.nombre,
                "cedula": st.session_state.cedula,
                "monto": st.session_state.monto,
                "fondo": st.session_state.fondo,
                "motivo": st.session_state.proposito
            }
            pdf = generar_pdf(doc_id, datos)
            st.session_state.pdf_bytes = pdf
        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")
            if st.button("Reintentar"):
                st.rerun()
            st.stop()

    # 3. Mostrar éxito y botón de descarga
    st.success("✅ ¡Tu carta está lista!")
    st.download_button(
        label="⬇️ Descargar Carta en PDF",
        data=st.session_state.pdf_bytes,
        file_name=f"Carta_{st.session_state.nombre}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.markdown(f"""
    <div style="background:#E8F5E9; padding:1rem; border-radius:16px; border-left:4px solid #25D366; margin-top: 1rem;">
        <strong>📱 Mensaje simulado de WhatsApp:</strong><br>
        "Hola {st.session_state.nombre}, hemos recibido tu solicitud. En un máximo de 24 horas hábiles te estaremos enviando tu carta. Estamos aquí para cualquier duda."
    </div>
    """, unsafe_allow_html=True)

    if st.button("Avanzar 24 Horas (Simulación) →", use_container_width=True):
        st.session_state.step = 'whatsapp_entrega'
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# (La función render_whatsapp_entrega se mantiene igual, pero el enlace de descarga puede apuntar al PDF generado si lo deseas)

# ---------- MAIN ----------
def main():
    if st.session_state.step == 'landing': render_landing()
    elif st.session_state.step == 'pregunta1': render_pregunta1()
    elif st.session_state.step == 'pregunta2': render_pregunta2()
    elif st.session_state.step == 'verificar_saldo': render_verificar_saldo()
    elif st.session_state.step == 'monto_exacto': render_monto_exacto()
    elif st.session_state.step == 'resultados': render_resultados()
    elif st.session_state.step == 'generando': render_generando()
    elif st.session_state.step == 'whatsapp_entrega': render_whatsapp_entrega()
    elif st.session_state.step == 'pago': render_pago()
    else: render_landing()

if __name__ == "__main__":
    main()
