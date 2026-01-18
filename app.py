import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Pro", layout="wide", page_icon="🏢")

# Estilos visuales
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div.stButton > button:first-child {
        background-color: #0066cc;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_dato(tabla, nuevo_df):
    try:
        df_existente = conn.read(worksheet=tabla, ttl=0)
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        conn.update(worksheet=tabla, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# 3. LÓGICA DE NAVEGACIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE ACCESO (LOGIN / REGISTRO) ---
if not st.session_state.autenticado:
    st.title("🏢 Acceso al Sistema")
    
    tab_login, tab_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registrar Nuevo Usuario"])

    with tab_login:
        with st.container():
            cedula = st.text_input("Cédula de Identidad", key="l_cedula")
            clave = st.text_input("Contraseña", type="password", key="l_clave")
            
            if st.button("ENTRAR AL SISTEMA"):
                df_users = conn.read(worksheet="Usuarios", ttl=0)
                # Validar si existe el usuario
                user_match = df_users[(df_users['Cédula'].astype(str) == cedula) & 
                                     (df_users['Password'].astype(str) == clave)]
                
                if not user_match.empty:
                    st.session_state.autenticado = True
                    st.session_state.nombre_usuario = user_match.iloc[0]['Nombre']
                    st.session_state.cargo_usuario = user_match.iloc[0]['Cargo']
                    st.success(f"Bienvenido, {st.session_state.nombre_usuario}")
                    st.rerun() # Salta de inmediato a los módulos
                else:
                    st.error("Datos incorrectos. Intente de nuevo.")

    with tab_reg:
        with st.form("registro"):
            st.subheader("Datos del Trabajador")
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_car = st.selectbox("Cargo", ["Operario", "Supervisor", "Gerente", "Administrativo"])
            r_pas = st.text_input("Cree una Contraseña", type="password")
            
            if st.form_submit_button("REGISTRAR Y ENTRAR"):
                if r_ced and r_nom and r_pas:
                    nuevo_u = pd.DataFrame([[r_ced, r_pas, r_nom, r_car]], 
                                         columns=["Cédula", "Password", "Nombre", "Cargo"])
                    
                    if registrar_dato("Usuarios", nuevo_u):
                        # Login automático tras registro
                        st.session_state.autenticado = True
                        st.session_state.nombre_usuario = r_nom
                        st.session_state.cargo_usuario = r_car
                        st.success("¡Registro exitoso!")
                        st.rerun()
                else:
                    st.warning("Por favor rellene todos los campos.")

# --- PANEL DE MÓDULOS (ESTO APARECE DESPUÉS DE ENTRAR) ---
else:
    # Barra lateral
    st.sidebar.title("Menú Principal")
    st.sidebar.write(f"👤 **Usuario:** {st.session_state.nombre_usuario}")
    st.sidebar.write(f"💼 **Cargo:** {st.session_state.cargo_usuario}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("🚀 Gestión de Módulos Operativos")
    
    modulos = [
        "📋 Tareas", "🎓 Formación", "👥 RRHH", "🏢 Organización", 
        "📂 Documentos", "🔧 Equipamiento", "⚠️ Incidencias", 
        "🌿 Ambiental", "🤝 Proveedores", "🔎 Coordinación", "📊 Evaluación"
    ]
    
    tabs = st.tabs(modulos)

    for i, nombre_mod in enumerate(modulos):
        with tabs[i]:
            st.header(nombre_mod)
            with st.form(f"f_{nombre_mod}"):
                detalles = st.text_area("Descripción de la actividad o reporte:")
                if st.form_submit_button(f"Guardar en {nombre_mod}"):
                    nuevo_reg = pd.DataFrame([[
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        st.session_state.nombre_usuario,
                        nombre_mod,
                        detalles
                    ]], columns=["Fecha", "Usuario", "Modulo", "Detalle"])
                    
                    if registrar_dato("Registros_Globales", nuevo_reg):
                        st.success("Reporte guardado con éxito.")
         if not df_historial.empty:
                # Filtrar solo los datos de este módulo
                filtro = df_historial[df_historial['Modulo'] == titulo]
                st.dataframe(filtro, use_container_width=True)
