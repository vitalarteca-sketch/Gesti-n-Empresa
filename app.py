import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Integral", layout="wide", page_icon="🏢")

# NUEVA URL ACTUALIZADA
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1K_iPI_cte1dv82rObC_IEfMIh75KViClc6eayZjiHAE/edit"

# 2. CONEXIÓN Y MOTOR DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    try:
        # ttl=0 para lectura en tiempo real
        return conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
    except Exception:
        # Si la tabla no existe o hay error, devolvemos estructura base
        if tabla == "Usuarios":
            return pd.DataFrame(columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
        else:
            return pd.DataFrame(columns=["Fecha", "Usuario", "Modulo", "Detalle"])

def guardar_en_excel(tabla, nuevo_df):
    try:
        df_existente = obtener_datos(tabla)
        # Limpiar posibles espacios en blanco en encabezados
        nuevo_df.columns = nuevo_df.columns.str.strip()
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 3. CONTROL DE SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- INTERFAZ DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🏢 Acceso Corporativo")
    t_login, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])

    with t_login:
        c_login = st.text_input("Cédula", key="l_c").strip()
        p_login = st.text_input("Contraseña", type="password", key="l_p").strip()
        if st.button("INGRESAR"):
            df_u = obtener_datos("Usuarios")
            df_u.columns = df_u.columns.str.strip()
            # Validación de credenciales
            match = df_u[(df_u['Cédula'].astype(str) == c_login) & (df_u['Password'].astype(str) == p_login)]
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                st.rerun()
            else:
                st.error("Cédula o contraseña incorrectas.")

    with t_reg:
        with st.form("registro_form"):
            st.subheader("Formulario de Registro")
            r_ced = st.text_input("Cédula (ID de acceso)")
            r_nom = st.text_input("Nombre Completo")
            r_dir = st.text_input("Dirección")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("REGISTRARSE"):
                if r_ced and r_nom and r_pas:
                    df_u = obtener_datos("Usuarios")
                    # Verificar si ya existe
                    if r_ced.strip() in df_u['Cédula'].astype(str).values:
                        st.warning("Esta cédula ya está registrada en el sistema.")
                    else:
                        nuevo_u = pd.DataFrame([[r_ced.strip(), r_pas.strip(), r_nom.strip(), r_dir.strip(), r_car]], 
                                             columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
                        if guardar_en_excel("Usuarios", nuevo_u):
                            st.success("¡Usuario creado con éxito!")
                            st.session_state.autenticado = True
                            st.session_state.nombre_usuario = r_nom
                            st.session_state.cargo_usuario = r_car
                            st.rerun()
                else:
                    st.error("Por favor, rellene los campos obligatorios.")

# --- PANEL DE MÓDULOS ---
else:
    st.sidebar.title("Menú")
    st.sidebar.success(f"👤 {st.session_state.nombre_usuario}\n💼 {st.session_state.cargo_usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # Módulos y campos
    config_m = [
        ("📋 Tareas", ["Actividad", "Estado"]),
        ("🎓 Formación", ["Curso", "Nota"]),
        ("👥 RRHH", ["Novedad", "Motivo"]),
        ("🏢 Org.", ["Área", "Mejora"]),
        ("📂 Docs", ["Nombre", "Ubicación"]),
        ("🔧 Equipos", ["Equipo", "Falla"]),
        ("⚠️ Riesgos", ["Riesgo", "Acción"]),
        ("🌿 Ambiente", ["Residuo", "Cantidad"]),
        ("🤝 Prov.", ["Empresa", "Factura"]),
        ("🔎 Coord.", ["Acuerdos", "Fecha"]),
        ("📊 Eval.", ["KPI", "Resultado"])
    ]

    titulos = [m[0] for m in config_m]
    if st.session_state.cargo_usuario == "Gerencia":
        titulos.append("📈 REPORTE MAESTRO")

    tabs = st.tabs(titulos)

    for i, (nombre, campos) in enumerate(config_m):
        with tabs[i]:
            st.header(nombre)
            with st.form(key=f"f_{i}"):
                res = {c: st.text_input(c)
    
