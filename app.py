import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
st.set_page_config(page_title="Gestión Empresarial Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        height: 3em;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #dee2e6;
        border-radius: 5px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_dato(tabla, nuevo_df):
    try:
        df_existente = conn.read(worksheet=tabla, ttl=0)
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        conn.update(worksheet=tabla, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 3. MANEJO DE SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_datos = None

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🏢 Sistema Integral de Gestión")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔑 Acceso al Personal")
        cedula_login = st.text_input("Cédula de Identidad")
        pass_login = st.text_input("Contraseña", type="password")
        
        if st.button("ENTRAR AL SISTEMA"):
            db_usuarios = conn.read(worksheet="Usuarios", ttl=0)
            # Validar credenciales
            usuario_match = db_usuarios[
                (db_usuarios['Cédula'].astype(str) == cedula_login) & 
                (db_usuarios['Password'].astype(str) == pass_login)
            ]
            
            if not usuario_match.empty:
                st.session_state.autenticado = True
                st.session_state.usuario_datos = usuario_match.iloc[0].to_dict()
                st.success("Acceso concedido. Cargando módulos...")
                st.rerun()
            else:
                st.error("Cédula o contraseña incorrecta.")

    with col2:
        st.subheader("📝 Registro de Nuevo Ingreso")
        with st.form("registro_trabajador"):
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_pas = st.text_input("Contraseña Nueva", type="password")
            r_car = st.text_input("Cargo")
            r_cel = st.text_input("Celular")
            
            if st.form_submit_button("REGISTRARME"):
                nuevo_user = pd.DataFrame([[r_ced, r_pas, r_nom, r_car, r_cel]], 
                    columns=["Cédula", "Password", "Nombre", "Cargo", "Celular"])
                if registrar_dato("Usuarios", nuevo_user):
                    st.success("Registro exitoso. Ya puedes iniciar sesión.")

# --- PANEL PRINCIPAL (MÓDULOS) ---
else:
    u = st.session_state.usuario_datos
    st.sidebar.title(f"👤 {u['Nombre']}")
    st.sidebar.info(f"Cargo: {u['Cargo']}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("🚀 Panel de Control Operativo")
    
    # Lista de los 11 módulos
    titulos_modulos = [
        "📋 Tareas", "🎓 Formación", "👥 RRHH", "🏢 Organización", 
        "📂 Documentos", "🔧 Equipamiento", "⚠️ Incidencias", 
        "🌿 Ambiental", "🤝 Proveedores", "🔎 Coordinación", "📊 Evaluación"
    ]
    
    pestanas = st.tabs(titulos_modulos)

    for i, titulo in enumerate(titulos_modulos):
        with pestanas[i]:
            st.header(titulo)
            
            # Subir información
            with st.expander("➕ Reportar nueva actividad"):
                with st.form(f"form_{i}"):
                    descripcion = st.text_area("Detalles del reporte:")
                    if st.form_submit_button("Enviar a Base de Datos"):
                        nuevo_registro = pd.DataFrame([[
                            datetime.now().strftime("%d/%m/%Y %H:%M"),
                            u['Nombre'],
                            titulo,
                            descripcion
                        ]], columns=["Fecha", "Usuario", "Modulo", "Detalle"])
                        
                        if registrar_dato("Registros_Globales", nuevo_registro):
                            st.success("Información guardada en Excel.")
            
            # Visualizar historial específico de este módulo
            st.write("---")
            st.subheader("Historial Reciente")
            df_historial = conn.read(worksheet="Registros_Globales", ttl=0)
            if not df_historial.empty:
                # Filtrar solo los datos de este módulo
                filtro = df_historial[df_historial['Modulo'] == titulo]
                st.dataframe(filtro, use_container_width=True)
