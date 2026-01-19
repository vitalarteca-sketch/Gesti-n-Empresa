import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Sistema de Gestión Integral", layout="wide", page_icon="🏢")

# DIRECCIÓN DE TU EXCEL
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1g7W5lAB6DZXBW84eFHTUUzAEj9LytjLnjLP7Lrn1IhI/edit"

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos(tabla):
    try:
        df = conn.read(spreadsheet=URL_EXCEL, worksheet=tabla, ttl=0)
        # Limpieza extrema de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        if tabla == "Usuarios":
            return pd.DataFrame(columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
        else:
            return pd.DataFrame(columns=["Fecha", "Usuario", "Modulo", "Detalle"])

def guardar_en_excel(tabla, nuevo_df):
    try:
        df_existente = obtener_datos(tabla)
        
        # Sincronizar columnas para evitar el error de esquema
        for col in df_existente.columns:
            if col not in nuevo_df.columns:
                nuevo_df[col] = ""
        
        nuevo_df = nuevo_df[df_existente.columns] # Reordenar columnas igual al Excel
        
        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
        df_final = df_final.fillna("") # Eliminar valores nulos que rompen la API
        
        conn.update(spreadsheet=URL_EXCEL, worksheet=tabla, data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error detectado: {e}")
        return False

# 3. SESIÓN
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏢 Acceso al Sistema")
    t_login, t_reg = st.tabs(["🔐 Login", "📝 Registro"])

    with t_login:
        c_login = st.text_input("Cédula", key="l_c").strip()
        p_login = st.text_input("Contraseña", type="password", key="l_p").strip()
        if st.button("ENTRAR"):
            df_u = obtener_datos("Usuarios")
            if not df_u.empty:
                # Buscar ignorando mayúsculas/minúsculas en los datos
                match = df_u[(df_u['Cédula'].astype(str) == c_login) & (df_u['Password'].astype(str) == p_login)]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.nombre_usuario = match.iloc[0]['Nombre']
                    st.session_state.cargo_usuario = match.iloc[0]['Cargo']
                    st.rerun()
                else: st.error("Credenciales incorrectas")

    with t_reg:
        with st.form("reg_form"):
            r_ced = st.text_input("Cédula")
            r_nom = st.text_input("Nombre Completo")
            r_dir = st.text_input("Dirección")
            r_car = st.selectbox("Cargo", ["Operativo", "Administrativo", "Supervisor", "Gerencia"])
            r_pas = st.text_input("Contraseña", type="password")
            if st.form_submit_button("REGISTRAR"):
                if r_ced and r_nom and r_pas:
                    nuevo_u = pd.DataFrame([[r_ced.strip(), r_pas.strip(), r_nom.strip(), r_dir.strip(), r_car]], 
                                         columns=["Cédula", "Password", "Nombre", "Dirección", "Cargo"])
                    if guardar_en_excel("Usuarios", nuevo_u):
                        st.success("¡Registrado!")
                        st.session_state.autenticado = True
                        st.session_state.nombre_usuario = r_nom
                        st.session_state.cargo_usuario = r_car
                        st.rerun()
                else: st.error("Faltan datos")

else:
    # --- INTERFAZ PRINCIPAL ---
    st.sidebar.title("Menú")
    st.sidebar.info(f"👤 {st.session_state.nombre_usuario}\n💼 {st.session_state.cargo_usuario}")
    if st.sidebar.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    config_m = [
        ("📋 Tareas", ["Actividad", "Estado"]), ("🎓 Formación", ["Curso", "Nota"]),
        ("👥 RRHH", ["Novedad", "Motivo"]), ("🏢 Org.", ["Área", "Mejora"]),
        ("📂 Docs", ["Nombre", "Ref"]), ("🔧 Equipos", ["Equipo", "Falla"]),
        ("⚠️ Riesgos", ["Riesgo", "Acción"]), ("🌿 Ambiente", ["Tipo", "Cant"]),
        ("🤝 Prov.", ["Empresa", "Fact"]), ("🔎 Coord.", ["Puntos", "Fecha"]),
        ("📊 Eval.", ["KPI", "Obs"])
    ]

    titulos = [m[0] for m in config_m]
    if st.session_state.cargo_usuario == "Gerencia": titulos.append("📈 REPORTE")
    tabs = st.tabs(titulos)

    for i, (nombre, campos) in enumerate(config_m):
        with tabs[i]:
            with st.form(key=f"f_{i}"):
                res = {c: st.text_input(c) for c in campos}
                if st.form_submit_button("Guardar"):
                    detalle = " | ".join([f"{k}: {v}" for k, v in res.items()])
                    nuevo_reg = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Usuario": st.session_state.nombre_usuario,
                        "Modulo": nombre, "Detalle": detalle
                    }])
                    if guardar_en_excel("Registros_Globales", nuevo_reg):
                        st.success("Guardado")

    if st.session_state.cargo_usuario == "Gerencia":
        with tabs[-1]:
            st.dataframe(obtener_datos("Registros_Globales"), use_container_width=True)
            
