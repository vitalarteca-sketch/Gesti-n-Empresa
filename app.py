import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Sistema de Gestión Integral", layout="wide")

# URL DE TU EXCEL (Actualizada)
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1g7W5lAB6DZXBW84eFHTUUzAEj9LytjLnjLP7Lrn1IhI/edit"

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    try:
        # ttl=0 para que siempre lea lo más nuevo
        df = conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
        return df.fillna("")
    except:
        # Si la tabla no existe o está vacía, creamos la estructura base
        if tabla == "Usuarios":
            return pd.DataFrame(columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
        else:
            return pd.DataFrame(columns=["Fecha", "Usuario", "Modulo", "Detalle"])

def guardar_datos(tabla, nuevo_df):
    try:
        df_actual = obtener_datos(tabla)
        # Unimos el registro nuevo al final
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        # Limpieza de columnas para evitar el error de "esquema"
        df_final.columns = [str(c).strip() for c in df_final.columns]
        # Guardar en Google Sheets
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error técnico de escritura: {e}")
        return False

# 3. SESIÓN
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- INTERFAZ ---
if not st.session_state.auth:
    st.title("🏢 Acceso al Sistema Corporativo")
    t_login, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro Nuevo"])

    with t_login:
        c_in = st.text_input("Cédula", key="c_login").strip()
        p_in = st.text_input("Contraseña", type="password", key="p_login").strip()
        if st.button("INGRESAR"):
            df = obtener_datos("Usuarios")
            if not df.empty:
                # Comprobación de credenciales
                match = df[(df['Cédula'].astype(str) == c_in) & (df['Password'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth = True
                    st.session_state.user = match.iloc[0]['Nombre']
                    st.session_state.cargo = match.iloc[0]['Cargo']
                    st.rerun()
                else:
                    st.error("❌ Cédula o contraseña incorrectas")

    with t_reg:
        with st.form("form_registro"):
            r_ced = st.text_input("Cédula (con tilde)")
            r_nom = st.text_input("Nombre Completo")
            r_dir = st.text_input("Dirección (con tilde)")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("REGISTRAR Y ENTRAR"):
                if r_ced and r_nom and r_pas:
                    # Crear el DataFrame con los nombres exactos que pide tu Excel
                    nuevo_u = pd.DataFrame([[r_ced, r_pas, r_nom, r_dir, r_car]], 
                                          columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
                    if guardar_datos("Usuarios", nuevo_u):
                        st.success("✅ ¡Cuenta creada exitosamente!")
                        st.session_state.auth = True
                        st.session_state.user = r_nom
                        st.session_state.cargo = r_car
                        st.rerun()
                else:
                    st.warning("⚠️ Todos los campos son obligatorios")

else:
    # PANEL DE CONTROL
    st.sidebar.success(f"Bienvenido: {st.session_state.user}")
    st.sidebar.info(f"Cargo: {st.session_state.cargo}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    st.header(f"Gestión de Módulos - {st.session_state.cargo}")
    
    modulos = ["Tareas", "Formación", "RRHH", "Organización", "Documentos", "Equipos", "Riesgos", "Ambiente", "Proveedores", "Coordinación", "Evaluación"]
    sel_mod = st.selectbox("Seleccione Módulo", modulos)
    
    with st.form("form_reporte"):
        detalle = st.text_area("Detalle del reporte:")
        if st.form_submit_button("Guardar Reporte"):
            if detalle:
                nuevo_rep = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state.user, sel_mod, detalle]], 
                                        columns=["Fecha", "Usuario", "Modulo", "Detalle"])
                if guardar_datos("Registros_Globales", nuevo_rep):
                    st.success("✅ Reporte guardado en el historial")
            else:
                st.warning("⚠️ El detalle no puede estar vacío")

    if st.session_state.cargo == "Gerencia":
        st.divider()
        st.subheader("📊 Historial General (Solo Gerencia)")
        st.dataframe(obtener_datos("Registros_Globales"), use_container_width=True)
            
