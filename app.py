import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import re
from streamlit_gsheets import GSheetsConnection

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
    .phone-number .copy-btn { background: rgba(255,255,255,0.15); border: none; color: white; padding: 0.3rem 0.8rem; border-radius: 30px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; }
    .phone-number .copy-btn:hover { background: rgba(255,255,255,0.25); }
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
for key in ['proposito', 'monto', 'monto_limpio', 'fondo', 'nombre', 'cedula', 'telefono', 'email', 'empresa', 'nit', 'saldo_verificado', 'saldo_limpio']:
    if key not in st.session_state: st.session_state[key] = ""

conn = st.connection("gsheets", type=GSheetsConnection)

# ---------- PANTALLAS ----------
def render_landing():
    st.markdown("""
    <div class="glass-container">
        <div class="hero-icon">📄</div>
        <div class="main-title">Tus <span>Cesantías</span><br>al Instante</div>
        <div class="sub-title">Retira tu dinero en 4 pasos, sin abogados</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="benefit-grid">
        <div class="benefit-card"><span class="icon">🎯</span><h4>1. Propósito</h4><p>Elige el motivo</p></div>
        <div class="benefit-card"><span class="icon">🏦</span><h4>2. Fondo</h4><p>Selecciona tu fondo</p></div>
        <div class="benefit-card"><span class="icon">📞</span><h4>3. Verifica</h4><p>Tu saldo disponible</p></div>
        <div class="benefit-card"><span class="icon">💰</span><h4>4. Retira</h4><p>Monto exacto</p></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Comenzar ahora →", use_container_width=True):
        st.session_state.step = 'pregunta1'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_pregunta1():
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 1 de 4</div>
        <div class="progress-container"><div class="progress-bar" style="width:25%;"></div></div>
        <h3 style="color:#0A2540;font-weight:700;margin-bottom:1rem;">🎯 ¿Para qué quieres retirar?</h3>
    """, unsafe_allow_html=True)
    st.session_state.proposito = st.radio("", ["🏠 Mejora de Vivienda", "📚 Educación", "💼 Desempleo", "❓ Otro"], key="p1")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ Atrás", use_container_width=True): st.session_state.step = 'landing'; st.rerun()
    with col2:
        if st.button("Siguiente →", use_container_width=True): st.session_state.step = 'pregunta2'; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_pregunta2():
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 2 de 4</div>
        <div class="progress-container"><div class="progress-bar" style="width:50%;"></div></div>
        <h3 style="color:#0A2540;font-weight:700;margin-bottom:1rem;">🏦 ¿En qué fondo estás?</h3>
    """, unsafe_allow_html=True)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "assets")
    def get_logo_path(filename):
        path = os.path.join(assets_dir, filename)
        return path if os.path.exists(path) else None

    fondos = [
        {"key": "porv", "nombre": "Porvenir", "logo": "Porvenir_logo.png", "emoji": "🏦"},
        {"key": "colf", "nombre": "Colfondos", "logo": "Colfondos_logo.png", "emoji": "🏢"},
        {"key": "prot", "nombre": "Protección", "logo": "Proteccion_logo.png", "emoji": "🛡️"},
        {"key": "fna", "nombre": "FNA", "logo": "FNA_logo.png", "emoji": "🏛️"},
        {"key": "otro", "nombre": "Otro", "logo": None, "emoji": "❓"},
    ]
    columns = st.columns(5)
    for idx, fondo in enumerate(fondos):
        with columns[idx]:
            logo_path = get_logo_path(fondo["logo"]) if fondo["logo"] else None
            if logo_path:
                with open(logo_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; height: 120px;"><img src="data:image/png;base64,{img_data}" style="max-width: 100px; max-height: 100px; object-fit: contain;"></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="font-size:4rem;text-align:center;">{fondo["emoji"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; font-weight: 600; color: #0A2540; margin: 8px 0; font-size: 0.9rem;">{fondo["nombre"]}</div>', unsafe_allow_html=True)
            if st.button("Seleccionar", key=fondo["key"], use_container_width=True):
                st.session_state.fondo = fondo["nombre"]
                st.session_state.step = 'verificar_saldo'
                st.rerun()

    if st.button("↩️ Atrás", use_container_width=True): st.session_state.step = 'pregunta1'; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_verificar_saldo():
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 3 de 4</div>
        <div class="progress-container"><div class="progress-bar" style="width:75%;"></div></div>
        <h3 style="color:#0A2540;font-weight:700;margin-bottom:0.5rem;">📞 Verifica tu saldo</h3>
    """, unsafe_allow_html=True)
    numeros = {"Porvenir": "01 8000 111 222", "Colfondos": "01 8000 123 456", "Protección": "01 8000 789 012", "FNA": "01 8000 456 789", "Otro": "01 8000 000 000"}
    numero = numeros.get(st.session_state.fondo, "01 8000 000 000")
    st.markdown(f'<div class="phone-number"><span>📱 {numero}</span></div>', unsafe_allow_html=True)
    st.info("Marca, presiona 1, digita tu cédula y escucha tu saldo.")
    
    saldo_raw = st.text_input("💰 Saldo exacto", placeholder="Ej: 10000000")
    if saldo_raw:
        limpio = re.sub(r'[^0-9]', '', saldo_raw)
        if limpio: st.success(f"✅ Saldo: **{f'{int(limpio):,}'.replace(',', '.')}**")
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ Atrás", use_container_width=True): st.session_state.step = 'pregunta2'; st.rerun()
    with col2:
        if st.button("Siguiente →", use_container_width=True):
            if saldo_raw:
                st.session_state.saldo_limpio = re.sub(r'[^0-9]', '', saldo_raw)
                st.session_state.saldo_verificado = f"${f'{int(st.session_state.saldo_limpio):,}'.replace(',', '.')}"
                st.session_state.step = 'monto_exacto'; st.rerun()
            else: st.error("Ingresa el saldo.")
    st.markdown("</div>", unsafe_allow_html=True)

def render_monto_exacto():
    st.markdown("""
    <div class="glass-container">
        <div class="step-text">Paso 4 de 4</div>
        <div class="progress-container"><div class="progress-bar" style="width:100%;"></div></div>
        <h3 style="color:#0A2540;font-weight:700;margin-bottom:1rem;">💰 Monto y tus datos</h3>
    """, unsafe_allow_html=True)
    
    if st.session_state.saldo_verificado:
        st.info(f"💰 Saldo disponible: **{st.session_state.saldo_verificado}**")

    monto_raw = st.text_input("Monto exacto a retirar", value=st.session_state.get('monto_raw_display', ''), key="monto_raw_widget")
    if monto_raw:
        limpio = re.sub(r'[^0-9]', '', monto_raw)
        if limpio: st.success(f"✅ Monto a retirar: **{f'{int(limpio):,}'.replace(',', '.')}**")

    st.markdown("### 📋 Tus datos personales")
    col1, col2 = st.columns(2)
    with col1:
        telefono = st.text_input("📱 WhatsApp", value=st.session_state.get('telefono_display', ''), key="telefono_widget")
        nombre = st.text_input("👤 Nombre completo", value=st.session_state.get('nombre_display', ''), key="nombre_widget")
        cedula = st.text_input("🆔 Cédula", value=st.session_state.get('cedula_display', ''), key="cedula_widget")
    with col2:
        email = st.text_input("📧 Correo", value=st.session_state.get('email_display', ''), key="email_widget")
        
        # --- DROPDOWN DE EMPRESAS AQUI ---
        lista_empresas = []
        df_empresas = pd.DataFrame()
        try:
            df_empresas = conn.read(worksheet="Empresas", ttl=0).dropna(how="all")
            lista_empresas = df_empresas["Nombre_Empresa"].tolist()
        except Exception as e:
            st.error(f"Error cargando empresas: {e}")

        # Seleccionar Empresa
        empresa_seleccionada = st.selectbox("🏢 Empresa", [""] + lista_empresas, key="empresa_widget")
        
        # Autocompletar NIT
        nit_auto = ""
        if empresa_seleccionada:
            filtro = df_empresas["Nombre_Empresa"].astype(str).str.strip() == empresa_seleccionada.strip()
            if filtro.any():
                nit_auto = str(df_empresas.loc[filtro, "NIT"].iloc[0]).strip()
                
        st.text_input("📋 NIT de la empresa", value=nit_auto, disabled=True, key=f"nit_input_{empresa_seleccionada}")
        # ---------------------------------

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("↩️ Atrás", use_container_width=True): st.session_state.step = 'verificar_saldo'; st.rerun()
    with col_btn2:
        if st.button("Siguiente →", use_container_width=True):
            monto_raw_val = st.session_state.monto_raw_widget
            telefono_val = st.session_state.telefono_widget
            nombre_val = st.session_state.nombre_widget
            cedula_val = st.session_state.cedula_widget
            email_val = st.session_state.email_widget
            
            if not monto_raw_val or not all([telefono_val, nombre_val, cedula_val, email_val, empresa_seleccionada]):
                st.error("Completa todos los datos y selecciona una empresa."); st.stop()
            
            limpio = re.sub(r'[^0-9]', '', monto_raw_val)
            if st.session_state.saldo_limpio and int(limpio) > int(st.session_state.saldo_limpio):
                st.error("El monto supera el saldo."); st.stop()

            # Guardar en variables de sesión
            st.session_state.monto = f"{int(limpio):,}".replace(',', '.')
            st.session_state.monto_limpio = limpio
            st.session_state.telefono = telefono_val
            st.session_state.nombre = nombre_val
            st.session_state.cedula = cedula_val
            st.session_state.email = email_val
            st.session_state.empresa = empresa_seleccionada
            st.session_state.nit = nit_auto
            
            st.session_state.step = 'resultados'; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_resultados():
    st.markdown("""
    <div class="glass-container">
        <h3 style="color:#0A2540;font-weight:700;">✅ ¡Listo! Resumen</h3>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🎯 Motivo:** {st.session_state.proposito}")
        st.markdown(f"**🏦 Fondo:** {st.session_state.fondo}")
        st.markdown(f"**💰 Monto a retirar:** {st.session_state.monto}")
    with col2:
        st.markdown(f"**👤 Nombre:** {st.session_state.nombre}")
        st.markdown(f"**🏢 Empresa:** {st.session_state.empresa}")
        st.markdown(f"**📋 NIT:** {st.session_state.nit}")

    if st.button("📄 Continuar con pago →", use_container_width=True):
        st.session_state.step = 'generando'; st.rerun()
    if st.button("↩️ Atrás", use_container_width=True):
        st.session_state.step = 'monto_exacto'; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_generando():
    st.markdown("""
    <div class="glass-container" style="text-align:center;">
        <h3 style="color:#0A2540;font-weight:700;">🔄 Procesando...</h3>
        <p style="color:#64748B;">Guardando tu solicitud y generando tu carta.</p>
    """, unsafe_allow_html=True)

    # Lógica de guardado en Google Sheets
    if 'solicitud_guardada' not in st.session_state:
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

    # Simulación de WhatsApp
    st.success(f"✅ ¡Solicitud {st.session_state.nombre} guardada exitosamente!")
    st.markdown(f"""
    <div style="background:#E8F5E9; padding:1rem; border-radius:16px; border-left:4px solid #25D366; margin-top: 1rem;">
        <strong>📱 Mensaje simulado de WhatsApp:</strong><br>
        "Hola {st.session_state.nombre}, hemos recibido tu solicitud. En un máximo de 24 horas hábiles te estaremos enviando tu carta. Estamos aquí para cualquier duda."
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Avanzar 24 Horas (Simulación) →", use_container_width=True):
        st.session_state.step = 'whatsapp_entrega'; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_whatsapp_entrega():
    st.markdown("""
    <div class="glass-container" style="text-align:center;">
        <h3 style="color:#0A2540;font-weight:700;">📱 24 Horas Después...</h3>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#E8F5E9; padding:1rem; border-radius:16px; border-left:4px solid #25D366; margin: 1rem 0;">
        <strong>📱 Nuevo mensaje de WhatsApp:</strong><br>
        "¡Hola {st.session_state.nombre}! Tu carta está lista. Aquí tienes el link de descarga: <a href='#'>Descargar Carta PDF</a>. ¡Gracias por confiar en nosotros!"
    </div>
    """, unsafe_allow_html=True)

    if st.button("Continuar al Pago →", use_container_width=True):
        st.session_state.step = 'pago'; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_pago():
    st.markdown("""
    <div class="glass-container">
        <h3 style="color:#0A2540;font-weight:700;">💳 Pago con Nequi</h3>
        <p style="color:#64748B;">Realiza el pago de <strong>$20.000 COP</strong> al número:</p>
        <div class="phone-number" style="background:linear-gradient(135deg,#7B2FBE,#9B4DCA);">
            📱 312 679 3911
        </div>
    """, unsafe_allow_html=True)

    if st.button("✅ Ya pagué, finalizar", use_container_width=True):
        st.session_state.step = 'landing'
        st.session_state.solicitud_guardada = False
        st.success("¡Gracias por tu pago! Proceso finalizado.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

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
