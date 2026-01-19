import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Gestión Empresa", layout="wide")

# URL DE TU EXCEL
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1g7W5lAB6DZXBW84eFHTUUzAEj9LytjLnjLP7Lrn1IhI/edit"

# CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    try:
        df = conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
        return df.fillna("")
    except:
        return pd.DataFrame()

def guardar_datos(tabla, nuevo_df):
    try:
        df_actual = obtener_datos(tabla)
        # Combinamos datos antiguos con el nuevo registro
        df_final = pd.concat([df_actual, nuevo_df], ignore_index=True)
        # Enviamos al Excel
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# ESTADO DE SESIÓN
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.auth:
    st.title("🚀 Registro e Inicio de Sesión")
    tab_log, tab_reg = st.tabs(["Ingresar", "Registrarse"])

    with tab_log:
        c_in = st.text_input("Cédula", key="c_in")
        p_in = st.text_input("Contraseña", type="password", key="p_in")
        if st.button("ENTRAR"):
            df = obtener_datos("Usuarios")
            if not df.empty:
                # Comprobación simple
                match = df[(df['Cédula'].astype(str) == c_in) & (df['Password'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth = True
                    st.session_state.user = match.iloc[0]['Nombre']
                    st.session_state.cargo = match.iloc[0]['Cargo']
                    st.rerun()
                else:
                    st.error("Cédula o contraseña incorrecta")

    with tab_reg:
        with st.form("f_reg"):
            r_ced = st.text_input("Número de Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_dir = st.text_input("Dirección")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Crear Contraseña", type="password")
            
            if st.form_submit_button("CREAR CUENTA"):
                if r_ced and r_nom and r_pas:
                    nuevo_usuario = pd.DataFrame([[r_ced, r_pas, r_nom, r_dir, r_car]], 
                                                columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
                    if guardar_datos("Usuarios", nuevo_usuario):
                        st.success("¡Registrado correctamente!")
                        st.session_state.auth = True
                        st.session_state.user = r_nom
                        st.session_state.cargo = r_car
                        st.rerun()
                else:
                    st.warning("Por favor rellena todos los campos")

# --- PANEL PRINCIPAL ---
else:
    st.sidebar.title(f"Bienvenido {st.session_state.user}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    st.title(f"Panel de Control - {st.session_state.cargo}")
    
    # Lista de módulos (los 11 solicitados)
    modulos = ["Tareas", "Formación", "RRHH", "Organización", "Documentos", "Equipos", "Riesgos", "Ambiente", "Proveedores", "Coordinación", "Evaluación"]
    
    sel_mod = st.selectbox("Seleccione un módulo para reportar:", modulos)
    
    with st.form("f_reporte"):
        detalle = st.text_area("Describa la actividad o novedad:")
        if st.form_submit_button("Guardar Reporte"):
            if detalle:
                nuevo_rep = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state.user, sel_mod, detalle]], 
                                        columns=["Fecha", "Usuario", "Modulo", "Detalle"])
                if guardar_datos("Registros_Globales", nuevo_rep):
                    st.success("Reporte guardado en el sistema")
            else:
                st.warning("Escriba el detalle antes de guardar")

    if st.session_state.cargo == "Gerencia":
        st.divider()
        st.subheader("📈 Vista de Gerencia (Todos los registros)")
        st.dataframe(obtener_datos("Registros_Globales"), use_container_width=True)
