import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN VISUAL CORPORATIVA
st.set_page_config(page_title="Sistema de Gestión Empresarial", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #002e5d;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# CONEXIÓN A BASE DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_en_excel(tabla, dataframe_nuevo):
    try:
        df_actual = conn.read(worksheet=tabla, ttl=0)
        df_final = pd.concat([df_actual, dataframe_nuevo], ignore_index=True)
        conn.update(worksheet=tabla, data=df_final)
        return True
    except:
        return False

# CONTROL DE SESIÓN
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# PANTALLA DE ACCESO
if st.session_state.usuario is None:
    st.title("🏢 Bienvenido al Sistema de Gestión")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔑 Inicio de Sesión")
        u_id = st.text_input("Cédula")
        u_pw = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            db_users = conn.read(worksheet="Usuarios", ttl=0)
            user = db_users[(db_users['Cédula'].astype(str) == u_id) & (db_users['Password'].astype(str) == u_pw)]
            if not user.empty:
                st.session_state.usuario = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Datos incorrectos")

    with col2:
        st.subheader("📝 Registro de Trabajador")
        with st.form("reg_form"):
            new_nom = st.text_input("Nombre y Apellidos")
            new_ced = st.text_input("Cédula")
            new_pas = st.text_input("Crear Contraseña", type="password")
            new_cel = st.text_input("Celular")
            new_dir = st.text_input("Dirección")
            new_car = st.text_input("Cargo")
            new_fam = st.number_input("Carga Familiar", min_value=0)
            if st.form_submit_button("Registrarme"):
                nuevo_u = pd.DataFrame([[new_ced, new_pas, new_nom, new_cel, new_dir, new_car, new_fam]], 
                                      columns=["Cédula", "Password", "Nombre", "Celular", "Dirección", "Cargo", "Carga Familiar"])
                registrar_en_excel("Usuarios", nuevo_u)
                st.success("¡Registro guardado! Ya puedes entrar.")

# PANEL PRIVADO
else:
    u = st.session_state.usuario
    st.sidebar.title(f"Hola, {u['Nombre']}")
    st.sidebar.write(f"**Cargo:** {u['Cargo']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()

    st.title("🚀 Panel de Control")
    
    # LOS 11 MÓDULOS
    modulos = [
        "Tareas pendientes", "Formación", "RRHH", "Organización", 
        "Documentación", "Equipamiento", "Incidencias", 
        "Evaluación Ambiental", "Proveedores", "Revisión Coordinación", "Evaluaciones"
    ]
    
    tabs = st.tabs(modulos)

    for i, m_nombre in enumerate(modulos):
        with tabs[i]:
            st.header(m_nombre)
            with st.form(f"form_{i}"):
                detalle = st.text_area("Ingresar información nueva:")
                if st.form_submit_button("Guardar en Base de Datos"):
                    nuevo_reg = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), u['Nombre'], m_nombre, detalle]], 
                                             columns=["Fecha", "Usuario", "Modulo", "Detalle"])
                    registrar_en_excel("Registros_Globales", nuevo_reg)
                    st.success("Información enviada correctamente.")
            
            # Ver historial del módulo
            st.write("---")
            st.subheader("Historial del módulo")
            historial = conn.read(worksheet="Registros_Globales", ttl=0)
            if not historial.empty:
                st.dataframe(historial[historial['Modulo'] == m_nombre], use_container_width=True)
