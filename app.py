import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la página
st.set_page_config(page_title="Cesantías al Instante", page_icon="📄", layout="centered")

# 2. Inyección de CSS (Letras blancas para el formulario)
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .link-btn {
        display: block; width: 100%; padding: 15px; margin: 10px 0;
        text-align: center; background-color: transparent;
        border: 2px solid #D4AF37; border-radius: 30px;
        color: white !important; font-weight: bold; text-decoration: none;
        transition: all 0.3s ease; font-size: 16px; cursor: pointer;
    }
    .link-btn:hover { background-color: #D4AF37; color: black !important; transform: scale(1.02); box-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
    
    .link-btn-primary { border-color: #ff00cc; box-shadow: 0 0 10px rgba(255, 0, 204, 0.3); }
    .link-btn-primary:hover { background-color: #ff00cc; color: white !important; box-shadow: 0 0 20px rgba(255, 0, 204, 0.8); }

    .title { text-align: center; color: white; font-family: 'Helvetica Neue', sans-serif; font-size: 32px; font-weight: 900; margin-bottom: 0px; }
    .subtitle { text-align: center; color: #888; font-size: 14px; margin-bottom: 30px; }
    
    /* ESTILOS DEL FORMULARIO - LETRAS BLANCAS */
    .stTextInput > div > div > input { 
        background-color: #1a1a1a; 
        color: #ffffff !important; 
        border-radius: 10px; 
    }
    div[data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    .stButton > button { background-color: #ff00cc; color: white; border-radius: 30px; font-weight: bold; width: 100%; padding: 15px; border: none; }
    .stButton > button:hover { background-color: #D4AF37; color: black; }
    </style>
""", unsafe_allow_html=True)

# 3. Variables de estado
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

# ==========================================
# PÁGINA 1: EL INICIO (Intacta)
# ==========================================
if st.session_state.pagina == "inicio":
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.write("*(Sube tu logo.png a GitHub para verlo aquí)*") 
            
    st.markdown("<p class='title'>Tus Cesantías al Instante</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Retira tu dinero en 4 pasos, sin abogados.</p>", unsafe_allow_html=True)

    if st.button("📄 Aplica para retirar tus cesantías", use_container_width=True, type="primary"):
        st.session_state.pagina = "formulario"
        st.rerun()

    st.markdown('<a href="https://tiktok.com/@raw.voice.record" target="_blank" class="link-btn">🎵 Síguenos en TikTok</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://instagram.com/tu_instagram" target="_blank" class="link-btn">📸 Síguenos en Instagram</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://wa.me/TU_NUMERO" target="_blank" class="link-btn">💬 Habla directo con el asesor</a>', unsafe_allow_html=True)

# ==========================================
# PÁGINA 2: EL FORMULARIO CON DROP-DOWN
# ==========================================
elif st.session_state.pagina == "formulario":
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    st.markdown("<p class='title'>Solicitud 📄</p>", unsafe_allow_html=True)
    
    if st.button("← Volver al inicio"):
        st.session_state.pagina = "inicio"
        st.rerun()
        
    st.markdown("<p class='subtitle'>Déjanos tus datos. Si tu perfil encaja, te contactaremos.</p>", unsafe_allow_html=True)

    # --- LÓGICA DEL DROP-DOWN DE EMPRESAS ---
    lista_empresas = []
    df_empresas = pd.DataFrame()
    
    try:
        df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
        lista_empresas = df_empresas["Nombre_Empresa"].tolist()
    except Exception as e:
        st.error(f"Error leyendo la pestaña 'Empresas': {e}")

    with st.form("mi_formulario", clear_on_submit=True):
        nombre = st.text_input("Nombre completo")
        cedula = st.text_input("Cédula")
        telefono = st.text_input("WhatsApp")
        
        # El Drop-down
        if lista_empresas:
            empresa_seleccionada = st.selectbox("Selecciona tu Empresa", [""] + lista_empresas)
            nit_auto = ""
            if empresa_seleccionada:
                # Buscamos el NIT que corresponde a esa empresa
                fila = df_empresas[df_empresas["Nombre_Empresa"] == empresa_seleccionada].iloc[0]
                nit_auto = str(fila["NIT"])
        else:
            empresa_seleccionada = ""
            nit_auto = ""
            st.warning("No hay empresas cargadas en la base de datos.")

        # Mostramos el NIT bloqueado para que no lo cambien
        st.text_input("NIT de la empresa", value=nit_auto, disabled=True)
        
        fondo = st.selectbox("Fondo", ["Porvenir", "Colfondos", "Protección", "FNA", "Otro"])
        motivo = st.selectbox("Motivo", ["Vivienda", "Educación", "Desempleo", "Otro"])
        monto = st.text_input("Monto")
        
        submitted = st.form_submit_button("Enviar Solicitud 🚀", use_container_width=True)

    if submitted:
        if nombre and cedula and telefono and empresa_seleccionada and monto:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            solicitud_id = f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            try:
                # Leemos los datos existentes
                existing_data = conn.read(worksheet="Solicitudes", ttl=0).dropna(how="all")
                
                # Creamos la nueva fila
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
                
                # Guardamos
                updated_df = pd.concat([existing_data, nuevo_dato], ignore_index=True)
                conn.update(worksheet="Solicitudes", data=updated_df)
                
                st.success("¡Solicitud guardada exitosamente! 🎉")
                st.balloons() 
                
            except Exception as e:
                st.error(f"Error de conexión con Google Sheets: {e}")
        else:
            st.error("Por favor, llena todos los campos y selecciona una empresa.")
