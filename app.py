import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Integral", layout="wide", page_icon="🏢")

# URL DE TU EXCEL
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1btqRzww3PoTd8J6OdmXqR27ZI4Q5lalE/edit"

# 2. CONEXIÓN Y MOTOR DE AUTO-CONFIGURACIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def inicializar_estructura():
    """Crea las pestañas con sus encabezados si el Excel está vacío"""
    try:
        # Verificar o crear pestaña Usuarios
        try:
            conn.read(spreadsheet=URL_EXCEL, worksheet="Usuarios", ttl=0)
        except:
            df_u = pd.DataFrame(columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
            conn.update(spreadsheet=URL_EXCEL, worksheet="Usuarios", data=df_u)
        
        # Verificar o crear pestaña Registros_Globales
        try:
            conn.read(spreadsheet=URL_EXCEL, worksheet="Registros_Globales", ttl=0)
        except:
            df_r = pd.DataFrame(columns=["Fecha", "Usuario", "Modulo", "Detalle"])
            conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_r)
    except:
        pass # Si ya existen, no hace nada

# Ejecutamos la configuración inicial
inicializar_estructura()

def obtener_datos(tabla):
    return conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)

def guardar_en_excel(tabla, nuevo_df):
    try:
        df_existente = obtener_datos(tabla)
        nuevo_df.columns = nuevo_df.columns.str.strip()
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error de guardado: {e}")
        return False

# 3. LÓGICA DE SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- INTERFAZ DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🏢 Sistema Corporativo")
    t_login, t_reg = st.tabs(["🔐 Login", "📝 Registro"])

    with t_login:
        c_login = st.text_input("Cédula", key="l_c").strip()
        p_login = st.text_input("Contraseña", type="password", key="l_p").strip()
        if st.button("INGRESAR"):
            df_u = obtener_datos("Usuarios")
            df_u.columns = df_u.columns.str.strip()
            match = df_u[(df_u['Cédula'].astype(str) == c_login) & (df_u['Password'].astype(str) == p_login)]
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                st.rerun()
            else:
                st.error("Datos incorrectos")

    with t_reg:
        with st.form("registro"):
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_dir = st.text_input("Dirección")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Password", type="password")
            if st.form_submit_button("REGISTRAR"):
                df_u = obtener_datos("Usuarios")
                if r_ced.strip() in df_u['Cédula'].astype(str).values:
                    st.warning("Usuario ya existe")
                else:
                    nuevo_u = pd.DataFrame([[r_ced, r_pas, r_nom, r_dir, r_car]], 
                                         columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
                    if guardar_en_excel("Usuarios", nuevo_u):
                        st.success("¡Registrado!")
                        st.session_state.autenticado = True
                        st.session_state.nombre_usuario = r_nom
                        st.session_state.cargo_usuario = r_car
                        st.rerun()

# --- PANEL DE MÓDULOS ---
else:
    st.sidebar.title("Menú")
    st.sidebar.info(f"👤 {st.session_state.nombre_usuario}\n💼 {st.session_state.cargo_usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    titulos = ["📋 Tareas", "🎓 Formación", "👥 RRHH", "🏢 Org.", "📂 Docs", "🔧 Equipos", "⚠️ Riesgos", "🌿 Ambiente", "🤝 Prov.", "🔎 Coord.", "📊 Eval."]
    if st.session_state.cargo_usuario == "Gerencia":
        titulos.append("📈 REPORTE")

    tabs = st.tabs(titulos)
    
    # Lógica simplificada para los 11 módulos
    for i in range(11):
        with tabs[i]:
            st.header(titulos[i])
            with st.form(key=f"f_{i}"):
                dato = st.text_area("Detalle de la actividad:")
                if st.form_submit_button("Guardar"):
                    nuevo_reg = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), 
                                               "Usuario": st.session_state.nombre_usuario, 
                                               "Modulo": titulos[i], "Detalle": dato}])
                    if guardar_en_excel("Registros_Globales", nuevo_reg):
                        st.success("Guardado")

    if st.session_state.cargo_usuario == "Gerencia":
        with tabs[-1]:
            st.subheader("Reporte General")
            st.dataframe(obtener_datos("Registros_Globales"))
d", "Destino Final"]),
        ("🤝 Proveedores", ["Nombre Proveedor", "Servicio/Insumo", "N° de Factura/Guía"]),
        ("🔎 Coordinación", ["Puntos Tratados", "Responsables Designados", "Próxima Revisión"]),
        ("📊 Evaluación", ["Indicador de Gestión", "Valor Alcanzado", "Observaciones"])
    ]

    # Renderizar módulos de entrada de datos
    for i, (nombre, campos) in enumerate(modulos_config):
        with tabs[i]:
            st.subheader(f"Formulario: {nombre}")
            with st.form(key=f"mod_form_{i}"):
                respuestas = {campo: st.text_input(campo) for campo in campos}
                if st.form_submit_button("Guardar Reporte"):
                    if any(respuestas.values()):
                        detalle_unido = " | ".join([f"{k}: {v}" for k, v in respuestas.items()])
                        datos = pd.DataFrame([{
                            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Usuario": st.session_state.nombre_usuario,
                            "Modulo": nombre,
                            "Detalle": detalle_unido
                        }])
                        if guardar_en_excel("Registros_Globales", datos):
                            st.success(f"Información de {nombre} enviada con éxito.")
                    else:
                        st.warning("Por favor, rellene al menos un campo.")

    # Módulo exclusivo para GERENCIA (última pestaña si existe)
    if es_gerente:
        with tabs[-1]:
            st.header("📈 Auditoría y Reportes Globales")
            st.info("Solo el personal de Gerencia tiene acceso a esta visualización.")
            if st.button("🔄 Cargar Datos Actualizados"):
                df_global = obtener_datos("Registros_Globales")
                st.dataframe(df_global, use_container_width=True)
                
                # Botón de descarga
                csv = df_global.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar Reporte en CSV", csv, "reporte_integral.csv", "text/csv")
