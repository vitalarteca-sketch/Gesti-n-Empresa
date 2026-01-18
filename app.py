import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión Empresarial Integral", layout="wide", page_icon="🏢")

# --- URL DE TU EXCEL CONFIGURADA ---
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1btqRzww3PoTd8J6OdmXqR27ZI4Q5lalE/edit"

# Estilo visual profesional
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #004b95; color: white; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #e1e4e8; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y FUNCIONES TÉCNICAS
conn = st.connection("gsheets", type=GSheetsConnection)

def registrar_dato(tabla, nuevo_df):
    """Inserta datos en el Excel usando la URL directa para evitar errores de 'Spreadsheet not specified'"""
    try:
        # Leemos los datos existentes
        df_existente = conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
        # Concatenamos el nuevo registro
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        # Actualizamos el Excel
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error técnico de conexión: {e}")
        return False

def guardar_registro_modulo(nombre_modulo, datos_dict):
    """Prepara los datos de los 11 módulos para ser guardados"""
    datos_dict['Fecha'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    datos_dict['Usuario'] = st.session_state.nombre_usuario
    datos_dict['Modulo'] = nombre_modulo
    
    nuevo_df = pd.DataFrame([datos_dict])
    return registrar_dato("Registros_Globales", nuevo_df)

# 3. LÓGICA DE NAVEGACIÓN Y SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE ACCESO (LOGIN Y REGISTRO) ---
if not st.session_state.autenticado:
    st.title("🏢 Sistema de Gestión Operativa")
    tab_login, tab_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro de Personal"])

    with tab_login:
        c_login = st.text_input("Cédula de Identidad", key="login_cedula").strip()
        p_login = st.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.button("ENTRAR AL SISTEMA"):
            if c_login and p_login:
                df_u = conn.read(spreadsheet=URL_EXCEL, worksheet="Usuarios", ttl=0)
                # Normalizamos datos para la comparación
                df_u['Cédula'] = df_u['Cédula'].astype(str).str.strip()
                df_u['Password'] = df_u['Password'].astype(str).str.strip()
                
                match = df_u[(df_u['Cédula'] == c_login) & (df_u['Password'] == p_login)]
                
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                    st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                    st.success("Acceso concedido...")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña no encontrados.")
            else:
                st.warning("Por favor rellene ambos campos.")

    with tab_reg:
        with st.form("registro_nuevo"):
            st.subheader("Crear Cuenta de Trabajador")
            r_ced = st.text_input("Número de Cédula")
            r_nom = st.text_input("Nombre y Apellido")
            r_car = st.selectbox("Cargo / Área", ["Operativo", "Administrativo", "Supervisor", "Gerente"])
            r_pas = st.text_input("Asigne una Contraseña", type="password")
            
            if st.form_submit_button("REGISTRARSE E INGRESAR"):
                if r_ced and r_nom and r_pas:
                    # Crear fila para la pestaña Usuarios
                    nuevo_user = pd.DataFrame([[r_ced.strip(), r_pas.strip(), r_nom.strip(), r_car]], 
                                            columns=["Cédula", "Password", "Nombre", "Cargo"])
                    
                    if registrar_dato("Usuarios", nuevo_user):
                        # Login automático
                        st.session_state.autenticado = True
                        st.session_state.nombre_usuario = r_nom
                        st.session_state.cargo_usuario = r_car
                        st.success("¡Registro exitoso!")
                        st.rerun()
                else:
                    st.error("Todos los campos son obligatorios.")

# --- PANEL DE CONTROL (11 MÓDULOS) ---
else:
    # Barra lateral de usuario
    st.sidebar.title("Menú")
    st.sidebar.write(f"👤 **Usuario:** {st.session_state.nombre_usuario}")
    st.sidebar.write(f"💼 **Cargo:** {st.session_state.cargo_usuario}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("🚀 Panel Operativo Integral")
    
    modulos = [
        "📋 Tareas", "🎓 Formación", "👥 RRHH", "🏢 Organización", 
        "📂 Documentos", "🔧 Equipamiento", "⚠️ Incidencias", 
        "🌿 Ambiental", "🤝 Proveedores", "🔎 Coordinación", "📊 Evaluación"
    ]
    
    tabs = st.tabs(modulos)

    for i, nombre in enumerate(modulos):
        with tabs[i]:
            st.header(nombre)
            with st.form(key=f"form_modulo_{i}"):
                st.write(f"Registro de actividad para: {nombre}")
                descripcion = st.text_area("Describa la actividad o novedad aquí:", key=f"text_{i}")
                
                # Ejemplo de campo dinámico para Incidencias
                extra = ""
                if nombre == "⚠️ Incidencias":
                    extra = st.selectbox("Nivel de Gravedad", ["Bajo", "Medio", "Alto", "Crítico"])
                
                if st.form_submit_button(f"Enviar a {nombre}"):
                    if descripcion:
                        texto_final = f"{descripcion} | Ref: {extra}" if extra else descripcion
                        if guardar_registro_modulo(nombre, {"Detalle": texto_final}):
                            st.success("Información guardada correctamente en el Excel.")
                    else:
                        st.warning("Por favor escriba un detalle antes de guardar.")
     cant = st.text_input("Cantidad/Peso")
            if st.form_submit_button("Registrar Acción Ambiental"):
                guardar_registro("Ambiental", {"Detalle": f"Residuo: {residuo} | Cant: {cant}"})

    with tabs[8]: # PROVEEDORES
        st.header("🤝 Gestión de Proveedores")
        with st.form("f8"):
            prov = st.text_input("Nombre del Proveedor")
            serv = st.text_input("Servicio/Producto recibido")
            if st.form_submit_button("Registrar Recepción"):
                guardar_registro("Proveedores", {"Detalle": f"Proveedor: {prov} | Servicio: {serv}"})

    with tabs[9]: # COORDINACIÓN
        st.header("🔎 Coordinación y Enlace")
        with st.form("f9"):
            minuta = st.text_area("Puntos tratados en reunión/coordinación")
            acuerdo = st.text_input("Acuerdo principal")
            if st.form_submit_button("Guardar Minuta"):
                guardar_registro("Coordinación", {"Detalle": f"Puntos: {minuta} | Acuerdo: {acuerdo}"})

    with tabs[10]: # EVALUACIÓN
        st.header("📊 Evaluación y Desempeño")
        with st.form("f10"):
            meta = st.text_input("Meta/KPI alcanzado")
            porcentaje = st.slider("Porcentaje de cumplimiento", 0, 100, 50)
            if st.form_submit_button("Enviar Evaluación"):
                guardar_registro("Evaluación", {"Detalle": f"Meta: {meta} | Cumplimiento: {porcentaje}%"})
