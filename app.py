import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Integral", layout="wide", page_icon="🏢")

# URL DE TU EXCEL
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1btqRzww3PoTd8J6OdmXqR27ZI4Q5lalE/edit"

# 2. CONEXIÓN Y MOTOR DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    try:
        return conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
    except Exception:
        if tabla == "Usuarios":
            return pd.DataFrame(columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
        else:
            return pd.DataFrame(columns=["Fecha", "Usuario", "Modulo", "Detalle"])

def guardar_en_excel(tabla, nuevo_df):
    try:
        df_existente = obtener_datos(tabla)
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
            match = df_u[(df_u['Cédula'].astype(str) == c_login) & (df_u['Password'].astype(str) == p_login)]
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                st.rerun()
            else:
                st.error("Datos incorrectos.")

    with t_reg:
        with st.form("registro_form"):
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_dir = st.text_input("Dirección")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña", type="password")
            if st.form_submit_button("REGISTRARSE"):
                if r_ced and r_nom and r_pas:
                    df_u = obtener_datos("Usuarios")
                    if r_ced.strip() in df_u['Cédula'].astype(str).values:
                        st.warning("Esta cédula ya existe.")
                    else:
                        nuevo_u = pd.DataFrame([[r_ced.strip(), r_pas.strip(), r_nom.strip(), r_dir.strip(), r_car]], 
                                             columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
                        if guardar_en_excel("Usuarios", nuevo_u):
                            st.session_state.autenticado = True
                            st.session_state.nombre_usuario = r_nom
                            st.session_state.cargo_usuario = r_car
                            st.rerun()
                else:
                    st.error("Rellene todos los campos.")

# --- PANEL DE MÓDULOS ---
else:
    st.sidebar.title("Menú")
    st.sidebar.success(f"👤 {st.session_state.nombre_usuario}\n💼 {st.session_state.cargo_usuario}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    config_m = [
        ("📋 Tareas", ["Actividad", "Prioridad"]),
        ("🎓 Formación", ["Curso", "Nota"]),
        ("👥 RRHH", ["Novedad", "Motivo"]),
        ("🏢 Org.", ["Área", "Mejora"]),
        ("📂 Docs", ["Nombre", "Lugar"]),
        ("🔧 Equipos", ["Equipo", "Acción"]),
        ("⚠️ Riesgos", ["Riesgo", "Acción"]),
        ("🌿 Ambiente", ["Residuo", "Destino"]),
        ("🤝 Prov.", ["Empresa", "Factura"]),
        ("🔎 Coord.", ["Puntos", "Acuerdos"]),
        ("📊 Eval.", ["KPI", "Observación"])
    ]

    titulos = [m[0] for m in config_m]
    if st.session_state.cargo_usuario == "Gerencia":
        titulos.append("📈 REPORTE")

    tabs = st.tabs(titulos)

    for i, (nombre, campos) in enumerate(config_m):
        with tabs[i]:
            st.header(nombre)
            with st.form(key=f"f_{i}"):
                res = {c: st.text_input(c) for c in campos}
                if st.form_submit_button(f"Guardar {nombre}"):
                    if any(res.values()):
                        detalle = " | ".join([f"{k}: {v}" for k, v in res.items()])
                        # Lógica de guardado corregida (Mismo nivel de espacios)
                        nuevo_reg = pd.DataFrame([{
                            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Usuario": st.session_state.nombre_usuario,
                            "Modulo": nombre,
                            "Detalle": detalle
                        }])
                        if guardar_en_excel("Registros_Globales", nuevo_reg):
                            st.success("Guardado.")
                    else:
                        st.warning("Escriba algo.")

    if st.session_state.cargo_usuario == "Gerencia":
        with tabs[-1]:
            st.header("Auditoría")
            if st.button("Actualizar"):
                st.dataframe(obtener_datos("Registros_Globales"))
 "Usuario": st.session_state.nombre_usuario,
                            "Modulo": nombre,
                            "Detalle": detalle
                        }])
                        if guardar_en_excel("Registros_Globales", nuevo_reg):
                            st.success("Información guardada.")
                    else:
                        st.warning("Escriba algo antes de guardar.")

    # Módulo exclusivo para Gerencia
    if st.session_state.cargo_usuario == "Gerencia":
        with tabs[-1]:
            st.header("Auditoría General")
            if st.button("🔄 Actualizar Datos"):
                st.dataframe(obtener_datos("Registros_Globales"), use_container_width=True)
e.nombre_usuario,
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
