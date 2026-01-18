import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Integral", layout="wide", page_icon="🏢")

# URL DE TU EXCEL
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1btqRzww3PoTd8J6OdmXqR27ZI4Q5lalE/edit"

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; background-color: #004b95; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f3f6; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y FUNCIONES LÓGICAS
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    return conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)

def guardar_en_excel(tabla, nuevo_df):
    try:
        df_existente = obtener_datos(tabla)
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return False

# 3. CONTROL DE SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🏢 Acceso al Sistema Corporativo")
    t_login, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro de Usuario"])

    with t_login:
        c_login = st.text_input("Cédula", key="l_c").strip()
        p_login = st.text_input("Contraseña", type="password", key="l_p").strip()
        if st.button("ENTRAR AL SISTEMA"):
            df_u = obtener_datos("Usuarios")
            df_u['Cédula'] = df_u['Cédula'].astype(str).str.strip()
            match = df_u[(df_u['Cédula'] == c_login) & (df_u['Password'].astype(str) == p_login)]
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                st.rerun()
            else:
                st.error("Credenciales incorrectas o usuario no registrado.")

    with t_reg:
        with st.form("form_registro"):
            st.subheader("Nuevo Registro de Personal")
            r_ced = st.text_input("Número de Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_car = st.selectbox("Cargo / Rol", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña de Acceso", type="password")
            
            if st.form_submit_button("REGISTRAR Y ENTRAR"):
                if r_ced and r_nom and r_pas:
                    df_u = obtener_datos("Usuarios")
                    # Evitar duplicados
                    if r_ced.strip() in df_u['Cédula'].astype(str).values:
                        st.warning("⚠️ Esta cédula ya existe. Por favor inicie sesión.")
                    else:
                        nuevo_u = pd.DataFrame([[r_ced.strip(), r_pas.strip(), r_nom.strip(), r_car]], 
                                             columns=["Cédula", "Password", "Nombre", "Cargo"])
                        if guardar_en_excel("Usuarios", nuevo_u):
                            st.session_state.autenticado = True
                            st.session_state.nombre_usuario = r_nom
                            st.session_state.cargo_usuario = r_car
                            st.success("¡Bienvenido al equipo!")
                            st.rerun()
                else:
                    st.error("Todos los campos son obligatorios.")

# --- PANEL DE MÓDULOS ---
else:
    st.sidebar.title("Menú")
    st.sidebar.success(f"👤 **Usuario:** {st.session_state.nombre_usuario}\n\n💼 **Cargo:** {st.session_state.cargo_usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("🚀 Gestión Operativa Integral")
    
    # Definición de pestañas
    titulos_tabs = ["📋 Tareas", "🎓 Formación", "👥 RRHH", "🏢 Org.", "📂 Docs", "🔧 Equipos", "⚠️ Riesgos", "🌿 Ambiente", "🤝 Prov.", "🔎 Coord.", "📊 Eval."]
    
    # Acceso restringido para Gerencia
    es_gerente = st.session_state.cargo_usuario == "Gerencia"
    if es_gerente:
        titulos_tabs.append("📈 REPORTE MAESTRO")

    tabs = st.tabs(titulos_tabs)

    # Configuración de los 11 módulos
    modulos_config = [
        ("📋 Tareas", ["Actividad Realizada", "Estado (Abierto/Cerrado)", "Horas Invertidas"]),
        ("🎓 Formación", ["Nombre del Curso", "Instructor", "Fecha de Culminación"]),
        ("👥 RRHH", ["Tipo de Novedad", "Fecha Inicio", "Justificación"]),
        ("🏢 Organización", ["Área Afectada", "Problema Identificado", "Sugerencia de Mejora"]),
        ("📂 Documentos", ["Nombre de Archivo", "Código/Referencia", "Ubicación Física/Digital"]),
        ("🔧 Equipamiento", ["Nombre del Equipo", "N° de Serie", "Acción Realizada"]),
        ("⚠️ Riesgos/Incidencias", ["Descripción del Evento", "Gravedad (1-10)", "Acciones de Emergencia"]),
        ("🌿 Ambiental", ["Residuo Manejado", "Peso/Cantidad", "Destino Final"]),
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
    
