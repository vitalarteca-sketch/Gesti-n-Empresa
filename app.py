import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión Empresarial Integral", layout="wide", page_icon="🏢")

# URL DE TU EXCEL
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1btqRzww3PoTd8J6OdmXqR27ZI4Q5lalE/edit"

# Estilo visual
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #004b95; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y FUNCIONES
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_dato(tabla, nuevo_df):
    try:
        df_existente = conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error técnico de conexión: {e}")
        return False

def guardar_registro_modulo(nombre_modulo, datos_dict):
    datos_dict['Fecha'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    datos_dict['Usuario'] = st.session_state.nombre_usuario
    datos_dict['Modulo'] = nombre_modulo
    nuevo_df = pd.DataFrame([datos_dict])
    return registrar_dato("Registros_Globales", nuevo_df)

# 3. MANEJO DE SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🏢 Acceso al Sistema")
    t_login, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro"])

    with t_login:
        c_login = st.text_input("Cédula", key="l_c").strip()
        p_login = st.text_input("Contraseña", type="password", key="l_p").strip()
        if st.button("ENTRAR AL SISTEMA"):
            df_u = conn.read(spreadsheet=URL_EXCEL, worksheet="Usuarios", ttl=0)
            df_u['Cédula'] = df_u['Cédula'].astype(str).str.strip()
            df_u['Password'] = df_u['Password'].astype(str).str.strip()
            match = df_u[(df_u['Cédula'] == c_login) & (df_u['Password'] == p_login)]
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                st.rerun()
            else:
                st.error("Datos incorrectos")

    with t_reg:
        with st.form("form_reg"):
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña", type="password")
            if st.form_submit_button("REGISTRAR Y ENTRAR"):
                if r_ced and r_nom and r_pas:
                    nuevo_u = pd.DataFrame([[r_ced.strip(), r_pas.strip(), r_nom.strip(), r_car]], 
                                         columns=["Cédula", "Password", "Nombre", "Cargo"])
                    if registrar_dato("Usuarios", nuevo_u):
                        st.session_state.autenticado = True
                        st.session_state.nombre_usuario = r_nom.strip()
                        st.session_state.cargo_usuario = r_car
                        st.success("¡Registro exitoso!")
                        st.rerun()
                else:
                    st.warning("Faltan datos")

# --- PANEL DE MÓDULOS ---
else:
    st.sidebar.write(f"👤 **{st.session_state.nombre_usuario}**")
    if st.sidebar.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    modulos = ["📋 Tareas", "🎓 Formación", "👥 RRHH", "🏢 Organización", "📂 Documentos", 
               "🔧 Equipos", "⚠️ Incidencias", "🌿 Ambiental", "🤝 Proveedores", "🔎 Coordinación", "📊 Evaluación"]
    
    tabs = st.tabs(modulos)
    for i, nombre in enumerate(modulos):
        with tabs[i]:
            st.header(nombre)
            with st.form(key=f"f_{i}"):
                det = st.text_area("Detalle de la actividad:", key=f"area_{i}")
                if st.form_submit_button(f"Guardar en {nombre}"):
                    if det:
                        if guardar_registro_modulo(nombre, {"Detalle": det}):
                            st.success("Guardado correctamente")
                    else:
                        st.warning("Escriba un detalle antes de guardar.")
