import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
from streamlit_gsheets import GSheetsConnection

# ---------- CONFIG ----------
st.set_page_config(page_title="Cesantías al Instante", layout="centered")

# ---------- CSS PREMIUM (RESTAURADO) ----------
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
    
    .stButton > button {
        background: linear-gradient(135deg, #0066FF, #00C853) !important; color: white !important; font-weight: 700 !important;
        border-radius: 60px !important; width: 100% !important; padding: 0.9rem !important; font-size: 1.1rem !important;
        border: none !important; transition: all 0.3s ease !important; box-shadow: 0 8px 25px rgba(0, 102, 255, 0.25) !important;
    }
    .stButton > button:hover { transform: scale(1.02) !important; box-shadow: 0 12px 35px rgba(0, 102, 255, 0.35) !important; }
    
    .step-text { text-align: center; color: #64748B; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem; }
    
    /* ESTILOS FORMULARIO */
    div[data-testid="stWidgetLabel"] p {
        color: #0A2540 !important;
        font-weight: 600 !important;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #0A2540 !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- ESTADO ----------
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'

# ==========================================
# PÁGINA 1: INICIO (Tu diseño original)
# ==========================================
if st.session_state.pagina == 'inicio':
    st.markdown("""
    <div class="glass-container">
        <div class="hero-icon">📄</div>
        <div class="main-title">Tus <span>Cesantías</span><br>al Instante</div>
        <div class="sub-title">Retira tu dinero en 4 pasos, sin abogados</div>
    """, unsafe_allow_html=True)

    if st.button("Comenzar ahora →", use_container_width=True):
        st.session_state.pagina = 'formulario'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PÁGINA 2: FORMULARIO (Con la lógica del Dropdown)
# ==========================================
elif st.session_state.pagina == 'formulario':
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 1 de 4</div>
        <h3 style="color:#0A2540;font-weight:700;margin-bottom:1rem;">🏢 Selecciona tu Empresa</h3>
    """, unsafe_allow_html=True)

    # 1. Lógica para leer Empresas y el Dropdown
    lista_empresas = []
    df_empresas = pd.DataFrame()
    
    try:
        df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
        lista_empresas = df_empresas["Nombre_Empresa"].tolist()
    except Exception as e:
        st.error(f"Error leyendo la pestaña 'Empresas': {e}")

    # 2. Selección de empresa
    if lista_empresas:
        empresa_seleccionada = st.selectbox("Busca tu empresa en la lista", [""] + lista_empresas)
        nit_auto = ""
        if empresa_seleccionada:
            fila = df_empresas[df_empresas["Nombre_Empresa"] == empresa_seleccionada].iloc[0]
            nit_auto = str(fila["NIT"])
    else:
        empresa_seleccionada = ""
        nit_auto = ""
        st.warning("No hay empresas cargadas en la base de datos.")

    # 3. Mostrar NIT bloqueado
    st.text_input("NIT de la empresa", value=nit_auto, disabled=True)

    # 4. Resto del formulario (para mantener tu prueba de guardado funcionando)
    st.markdown("---")
    nombre = st.text_input("Nombre completo")
    cedula = st.text_input("Cédula")
    telefono = st.text_input("WhatsApp")
    fondo = st.selectbox("Fondo", ["Porvenir", "Colfondos", "Protección", "FNA", "Otro"])
    motivo = st.selectbox("Motivo", ["Vivienda", "Educación", "Desempleo", "Otro"])
    monto = st.text_input("Monto")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ Atrás", use_container_width=True):
            st.session_state.pagina = 'inicio'
            st.rerun()
    with col2:
        if st.button("Enviar Solicitud", use_container_width=True):
            if nombre and cedula and telefono and empresa_seleccionada and monto:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                solicitud_id = f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                try:
                    existing_data = conn.read(worksheet="Solicitudes", ttl=0).dropna(how="all")
                    nuevo_dato = pd.DataFrame([{
                        "solicitud_id": solicitud_id,
                        "fecha": fecha_actual,
                        "nombre": nombre,
                        "cedula": cedula,
                        "telefono": telefono,
                        "nit": nit_auto,
                        "empresa": empresa_seleccionada,
                        "fondo": fondo,
                        "motivo": motivo,
                        "monto": monto,
                        "estado": "Pendiente"
                    }])
                    
                    updated_df = pd.concat([existing_data, nuevo_dato], ignore_index=True)
                    conn.update(worksheet="Solicitudes", data=updated_df)
                    
                    st.success("¡Solicitud guardada exitosamente! 🎉")
                    st.balloons() 
                    
                except Exception as e:
                    st.error(f"Error de conexión con Google Sheets: {e}")
            else:
                st.error("Por favor, llena todos los campos y selecciona una empresa.")
                
    st.markdown("</div>", unsafe_allow_html=True)
