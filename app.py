import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Cesantías", layout="centered")

# Patrón exacto de Raw Voice
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("Formulario de Solicitud")

with st.form("mi_formulario", clear_on_submit=True):
    nombre = st.text_input("Nombre completo")
    cedula = st.text_input("Cédula")
    telefono = st.text_input("WhatsApp")
    nit = st.text_input("NIT")
    empresa = st.text_input("Empresa")
    fondo = st.selectbox("Fondo", ["Porvenir", "Colfondos", "Protección", "FNA", "Otro"])
    motivo = st.selectbox("Motivo", ["Vivienda", "Educación", "Desempleo", "Otro"])
    monto = st.text_input("Monto")
    
    enviar = st.form_submit_button("Guardar")

if enviar:
    if nombre and cedula and telefono and nit and empresa and monto:
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
                "nit": nit,
                "empresa": empresa,
                "fondo": fondo,
                "motivo": motivo,
                "monto": monto,
                "estado": "Pendiente"
            }])
            
            updated_df = pd.concat([existing_data, nuevo_dato], ignore_index=True)
            conn.update(worksheet="Solicitudes", data=updated_df)
            
            st.success("Guardado correctamente.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Llena todos los campos.")