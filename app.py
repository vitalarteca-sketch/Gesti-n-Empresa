import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión", layout="wide")

# URL DE TU EXCEL
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1g7W5lAB6DZXBW84eFHTUUzAEj9LytjLnjLP7Lrn1IhI/edit"

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    try:
        df = conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
        return df.fillna("")
    except:
        if tabla == "Usuarios":
            return pd.DataFrame(columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
        else:
            return pd.DataFrame(columns=["Fecha", "Usuario", "Modulo", "Detalle"])

def guardar_datos(tabla, nuevo_df):
    try:
        df_actual = obtener_datos(tabla)
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        # Sincronización de columnas
        df_final.columns = [str(c).strip() for c in df_final.columns]
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        st.cache_data.clear()
        return True
    except:
        st.error("No se pudo guardar la información. Verifique que el archivo sea una Hoja de Cálculo de Google y tenga permisos de Editor.")
        return False

# 3. CONTROL DE SESIÓN
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- INTERFAZ ---
if not st.session_state.auth:
    st.title("🏢 Acceso al Sistema")
    t_login, t_reg = st.tabs(["Ingresar", "Registro"])

    with t_login:
        c_in = st.text_input("Cédula", key="c_login").strip()
        p_in = st.text_input("Contraseña", type="password", key="p_login").strip()
        if st.button("Entrar"):
            df = obtener_datos("Usuarios")
            if not df.empty:
                match = df[(df['Cédula'].astype(str) == c_in) & (df['Password'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth = True
                    st.session_state.user = match.iloc[0]['Nombre']
                    st.session_state.cargo = match.iloc[0]['Cargo']
                    st.rerun()
                else:
                    st.error("Cédula o contraseña incorrectas")

    with t_reg:
        with st.form("form_registro"):
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_dir = st.text_input("Dirección")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Crear Cuenta"):
                if r_ced and r_nom and r_pas:
                    nuevo_u = pd.DataFrame([[r_ced, r_pas, r_nom, r_dir, r_car]], 
                                          columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
                    if guardar_datos("Usuarios", nuevo_u):
                        st.success("Cuenta creada exitosamente")
                        st.session_state.auth = True
                        st.session_state.user = r_nom
                        st.session_state.cargo = r_car
                        st.rerun()
                else:
                    st.warning("Todos los campos son obligatorios")

else:
    # PANEL DE CONTROL
    st.sidebar.success(f"Usuario: {st.session_state.user}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    st.header(f"Módulos de Gestión - {st.session_state.cargo}")
    
    modulos = ["Tareas", "Formación", "RRHH", "Organización", "Documentos", "Equipos", "Riesgos", "Ambiente", "Proveedores", "Coordinación", "Evaluación"]
    sel_mod = st.selectbox("Módulo", modulos)
    
    with st.form("form_reporte"):
        detalle = st.text_area("Detalle del reporte")
        if st.form_submit_button("Guardar"):
            if detalle:
                nuevo_rep = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state.user, sel_mod, detalle]], 
                                        columns=["Fecha", "Usuario", "Modulo", "Detalle"])
                if guardar_datos("Registros_Globales", nuevo_rep):
                    st.success("Información guardada")
            else:
                st.warning("El campo de detalle está vacío")

    if st.session_state.cargo == "Gerencia":
        st.divider()
        st.subheader("Historial General")
        st.dataframe(obtener_datos("Registros_Globales"), use_container_width=True)
            
