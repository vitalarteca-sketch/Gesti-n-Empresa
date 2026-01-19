import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Integral", layout="wide", page_icon="🏢")

# URL DE TU EXCEL (Asegúrate de que sea la versión "Hoja de cálculo de Google")
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1g7W5lAB6DZXBW84eFHTUUzAEj9LytjLnjLP7Lrn1IhI/edit"

# 2. CONEXIÓN Y MOTOR DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    try:
        # ttl=0 obliga a la app a leer los datos más recientes del Excel
        return conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
    except Exception:
        if tabla == "Usuarios":
            return pd.DataFrame(columns=["Cédula", "Password", "Nombre", "Cargo"])
        else:
            return pd.DataFrame(columns=["Fecha", "Usuario", "Modulo", "Detalle"])

def guardar_en_excel(tabla, nuevo_df):
    try:
        df_existente = obtener_datos(tabla)
        # Unir el nuevo registro a los existentes
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        # Limpiar datos para evitar errores de envío
        df_final = df_final.fillna("")
        # Enviar al Excel
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        # Limpiar cache para que la app reconozca al nuevo usuario al instante
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return False

# 3. CONTROL DE SESIÓN
if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- INTERFAZ DE ACCESO ---
if not st.session_state.auth:
    st.title("🏢 Acceso Corporativo")
    t_login, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro Nuevo"])

    with t_login:
        c_in = st.text_input("Cédula", key="l_c").strip()
        p_in = st.text_input("Contraseña", type="password", key="l_p").strip()
        if st.button("INGRESAR"):
            df_u = obtener_datos("Usuarios")
            if not df_u.empty:
                # Comprobar si existe el usuario
                match = df_u[(df_u['Cédula'].astype(str) == c_in) & (df_u['Password'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth = True
                    st.session_state.user = match.iloc[0]['Nombre']
                    st.session_state.cargo = match.iloc[0]['Cargo']
                    st.rerun()
                else:
                    st.error("Cédula o contraseña incorrectas")

    with t_reg:
        with st.form("registro_form"):
            st.subheader("Crear Nueva Cuenta")
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("CREAR CUENTA"):
                if r_ced and r_nom and r_pas:
                    df_u = obtener_datos("Usuarios")
                    # Verificar si la cédula ya existe
                    if r_ced.strip() in df_u['Cédula'].astype(str).values:
                        st.warning("Esta cédula ya está registrada.")
                    else:
                        # Crear el nuevo registro
                        nuevo_u = pd.DataFrame([[r_ced.strip(), r_pas.strip(), r_nom.strip(), r_car]], 
                                             columns=["Cédula", "Password", "Nombre", "Cargo"])
                        
                        # Guardar y dar acceso
                        if guardar_en_excel("Usuarios", nuevo_u):
                            st.success("¡Cuenta creada exitosamente!")
                            st.session_state.auth = True
                            st.session_state.user = r_nom
                            st.session_state.cargo = r_car
                            st.rerun()
                else:
                    st.error("Todos los campos son obligatorios")

# --- PANEL DE CONTROL ---
else:
    st.sidebar.success(f"Bienvenido: {st.session_state.user}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    st.header(f"Módulos de Gestión - {st.session_state.cargo}")
    
    modulos = ["Tareas", "Formación", "RRHH", "Organización", "Documentos", "Equipos", "Riesgos", "Ambiente", "Proveedores", "Coordinación", "Evaluación"]
    sel_mod = st.selectbox("Seleccione un Módulo", modulos)
    
    with st.form("form_reporte"):
        detalle = st.text_area("Describa la novedad o actividad:")
        if st.form_submit_button("Guardar Reporte"):
            if detalle:
                nuevo_rep = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y %H:%M"), st.session_state.user, sel_mod, detalle]], 
                                        columns=["Fecha", "Usuario", "Modulo", "Detalle"])
                if guardar_en_excel("Registros_Globales", nuevo_rep):
                    st.success("Registro guardado en el Excel.")
            else:
                st.warning("El detalle no puede estar vacío.")

    if st.session_state.cargo == "Gerencia":
        st.divider()
        st.subheader("📈 Reporte Maestro (Gerencia)")
        st.dataframe(obtener_datos("Registros_Globales"), use_container_width=True)
    
