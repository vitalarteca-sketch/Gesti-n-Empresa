import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión Empresarial Integral", layout="wide", page_icon="📊")

# Estilo personalizado para mejorar la visualización en celulares
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #004b95; color: white; }
    .stExpander { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def guardar_registro(nombre_modulo, datos_dict):
    try:
        # Añadir metadatos comunes
        datos_dict['Fecha'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        datos_dict['Usuario'] = st.session_state.nombre_usuario
        datos_dict['Modulo'] = nombre_modulo
        
        nuevo_df = pd.DataFrame([datos_dict])
        df_existente = conn.read(worksheet="Registros_Globales", ttl=0)
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        conn.update(worksheet="Registros_Globales", data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 3. LÓGICA DE SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🏢 Portal de Trabajo")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔐 Ingresar")
        c = st.text_input("Cédula")
        p = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR"):
            df_u = conn.read(worksheet="Usuarios", ttl=0)
            match = df_u[(df_u['Cédula'].astype(str) == c) & (df_u['Password'].astype(str) == p)]
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                st.rerun()
            else:
                st.error("Datos incorrectos")

    with col2:
        st.subheader("📝 Nuevo Registro")
        with st.form("reg_u"):
            nc = st.text_input("Cédula")
            nn = st.text_input("Nombre")
            nca = st.selectbox("Cargo", ["Operativo", "Administrativo", "Gerencia"])
            np = st.text_input("Contraseña", type="password")
            if st.form_submit_button("REGISTRAR Y ENTRAR"):
                if registrar_dato("Usuarios", pd.DataFrame([[nc, np, nn, nca]], columns=["Cédula", "Password", "Nombre", "Cargo"])):
                    st.session_state.autenticado = True
                    st.session_state.nombre_usuario = nn
                    st.session_state.cargo_usuario = nca
                    st.rerun()

# --- PANEL DE MÓDULOS ---
else:
    st.sidebar.title(f"Bienvenido/a")
    st.sidebar.success(f"👤 {st.session_state.nombre_usuario}\n\n💼 {st.session_state.cargo_usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("🚀 Sistema Operativo")
    
    tabs = st.tabs([
        "📋 Tareas", "🎓 Formación", "👥 RRHH", "🏢 Org.", "📂 Docs", 
        "🔧 Equipos", "⚠️ Incidencias", "🌿 Amb.", "🤝 Prov.", "🔎 Coord.", "📊 Eval."
    ])

    # --- DEFINICIÓN DE FORMULARIOS POR MÓDULO ---
    with tabs[0]: # TAREAS
        st.header("📋 Gestión de Tareas")
        with st.form("f0"):
            t = st.text_input("Tarea realizada")
            e = st.selectbox("Estado", ["Completada", "En proceso", "Pendiente"])
            if st.form_submit_button("Guardar"):
                guardar_registro("Tareas", {"Detalle": f"Tarea: {t} | Estado: {e}"})

    with tabs[1]: # FORMACIÓN
        st.header("🎓 Capacitación y Formación")
        with st.form("f1"):
            cur = st.text_input("Nombre del Curso/Charla")
            dur = st.number_input("Horas", min_value=1)
            if st.form_submit_button("Registrar Formación"):
                guardar_registro("Formación", {"Detalle": f"Curso: {cur} | Duración: {dur}h"})

    with tabs[2]: # RRHH
        st.header("👥 Recursos Humanos")
        with st.form("f2"):
            tipo = st.selectbox("Tipo de novedad", ["Permiso", "Vacaciones", "Licencia Médica", "Otro"])
            obs = st.text_area("Observaciones")
            if st.form_submit_button("Enviar Solicitud"):
                guardar_registro("RRHH", {"Detalle": f"Tipo: {tipo} | Obs: {obs}"})

    with tabs[3]: # ORGANIZACIÓN
        st.header("🏢 Estructura Organizativa")
        with st.form("f3"):
            dep = st.text_input("Departamento/Área")
            cambio = st.text_area("Propuesta de mejora u organización")
            if st.form_submit_button("Enviar Propuesta"):
                guardar_registro("Organización", {"Detalle": f"Área: {dep} | Propuesta: {cambio}"})

    with tabs[4]: # DOCUMENTOS
        st.header("📂 Control Documental")
        with st.form("f4"):
            doc = st.text_input("Código o Nombre del Documento")
            ver = st.text_input("Versión/Fecha de Revisión")
            if st.form_submit_button("Registrar Documento"):
                guardar_registro("Documentos", {"Detalle": f"Doc: {doc} | Versión: {ver}"})

    with tabs[5]: # EQUIPAMIENTO
        st.header("🔧 Mantenimiento de Equipos")
        with st.form("f5"):
            eq = st.text_input("Equipo/Máquina")
            mante = st.selectbox("Tipo", ["Preventivo", "Correctivo", "Limpieza"])
            if st.form_submit_button("Reportar Mantenimiento"):
                guardar_registro("Equipamiento", {"Detalle": f"Equipo: {eq} | Tipo: {mante}"})

    with tabs[6]: # INCIDENCIAS
        st.header("⚠️ Reporte de Incidencias / Riesgos")
        with st.form("f6"):
            riesgo = st.selectbox("Nivel de Riesgo", ["Bajo", "Medio", "Alto", "Crítico"])
            desc = st.text_area("Descripción de lo ocurrido")
            if st.form_submit_button("🚨 REPORTAR INCIDENCIA"):
                guardar_registro("Incidencias", {"Detalle": f"RIESGO: {riesgo} | EVENTO: {desc}"})

    with tabs[7]: # AMBIENTAL
        st.header("🌿 Gestión Ambiental")
        with st.form("f7"):
            residuo = st.text_input("Tipo de Residuo/Desecho gestionado")
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
