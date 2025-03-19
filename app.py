import streamlit as st
import pandas as pd
import numpy as np
 
# Configurar la interfaz
st.set_page_config(page_title="Gestión de Horas", layout="wide")
 
# CSS personalizado para mejorar el sidebar y tabla de totales
st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .css-hxt7ib {
        padding-top: 2rem;
    }
    .total-row {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .highlight-total {
        background-color: #e6f3ff;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .total-box {
        background-color: #e6f3ff;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #b8daff;
        text-align: center;
    }
    .total-value {
        font-size: 24px;
        font-weight: bold;
        color: #0366d6;
    }
</style>
""", unsafe_allow_html=True)
 
# Inicializar el estado de la sección seleccionada y los filtros
if "pagina_seleccionada" not in st.session_state:
    st.session_state.pagina_seleccionada = "Horas trabajadas"
    st.session_state.df_mostrar = None
    st.session_state.servicio_seleccionado = None
    st.session_state.filtro_empleados_servicio = []
    st.session_state.filtro_empleados_trabajadas = []
    st.session_state.filtro_estados = []
 
# Sidebar con navegación mejorada
with st.sidebar:
    st.title("📌 Menú")
   
    # Añadir línea divisoria
    st.markdown("<hr style='margin-top: 0; margin-bottom: 1rem; border: 0; border-top: 1px solid rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
   
    # Iconos para las opciones del menú
    opciones_con_iconos = {
        "Horas trabajadas": "👨‍💼 Horas trabajadas",
        "Horas por servicio": "🛠️ Horas por servicio"
    }
   
    pagina_seleccionada = st.selectbox(
        "Selecciona una opción:",
        list(opciones_con_iconos.keys()),
        format_func=lambda x: opciones_con_iconos[x]
    )
   
    # Información adicional en el sidebar
    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 1rem; border: 0; border-top: 1px solid rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color: #e9ecef; padding: 1rem; border-radius: 0.3rem; margin-top: 1rem;'>
        <p style='margin: 0; font-size: 0.9rem;'><strong>Contacto</strong></p>
        <p style='margin: 0; font-size: 0.8rem; color: #6c757d;'>no_responder@horbath.com</p>
    </div>
    """, unsafe_allow_html=True)
 
# Si el usuario cambia de sección, resetear los valores
if pagina_seleccionada != st.session_state.pagina_seleccionada:
    st.session_state.pagina_seleccionada = pagina_seleccionada
    st.session_state.df_mostrar = None
    st.session_state.servicio_seleccionado = None
    st.session_state.filtro_empleados_servicio = []
    st.session_state.filtro_empleados_trabajadas = []
    st.session_state.filtro_estados = []
 
# Función para mostrar la sección "Horas trabajadas"
def mostrar_horas_trabajadas():
    st.title("👨‍💼 Control de Horas Trabajadas")
    uploaded_file = st.file_uploader("📂 Sube el archivo Excel con las horas trabajadas", type=["xlsx"], key="horas_trabajadas")
    col1, col2 = st.columns(2)
    mes_seleccionado = col1.selectbox("📅 Selecciona el mes", list(range(1, 13)), index=0, key="mes_trabajadas")
    año_seleccionado = col2.selectbox("📆 Selecciona el año", list(range(2020, 2031)), index=5, key="año_trabajadas")
   
    if uploaded_file:
        xls = pd.ExcelFile(uploaded_file)
        resultados = []
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df["Empleado"] = sheet_name
            df_filtrado = df[(df["mes"] == mes_seleccionado) & (df["año"] == año_seleccionado)]
            resumen = df_filtrado.groupby(["Empleado", "dia", "mes", "año"]).agg({"horas": "sum"}).reset_index()
            for _, row in resumen.iterrows():
                total_horas = row["horas"]
                estado = "✅ Cumple jornada" if total_horas == 8 else "⚠️ No cumple jornada" if total_horas < 8 else "⚠️ Excede jornada"
                resultados.append({"Empleado": row["Empleado"], "Fecha": f"{row['dia']}-{row['mes']}-{row['año']}", "Horas": total_horas, "Estado": estado})
       
        df_resultado = pd.DataFrame(resultados)
        if not df_resultado.empty:
            st.success("✅ Datos procesados correctamente")
           
            # Filtros multiselect para "Horas trabajadas"
            empleados = df_resultado["Empleado"].unique().tolist()
            estados = df_resultado["Estado"].unique().tolist()
           
            col1, col2 = st.columns(2)
            with col1:
                filtro_empleados = st.multiselect(
                    "🔎 Filtrar por Empleado(s)",
                    options=empleados,
                    default=[],
                    key="filtro_empleados_trabajadas"
                )
           
            with col2:
                filtro_estados = st.multiselect(
                    "🔎 Filtrar por Estado(s)",
                    options=estados,
                    default=[],
                    key="filtro_estados"
                )
           
            # Aplicar filtros multiselect
            df_filtrado = df_resultado.copy()
           
            if filtro_empleados:
                df_filtrado = df_filtrado[df_filtrado["Empleado"].isin(filtro_empleados)]
           
            if filtro_estados:
                df_filtrado = df_filtrado[df_filtrado["Estado"].isin(filtro_estados)]
           
            # Mostrar número de registros y dataframe filtrado
            st.write(f"Mostrando {len(df_filtrado)} de {len(df_resultado)} registros")
           
            # Mostrar tabla
            st.dataframe(df_filtrado, hide_index=True)
           
            # Calcular el total de horas
            total_horas_filtrado = df_filtrado["Horas"].sum()
           
            # Mostrar total de horas en un cuadro destacado debajo de la tabla
            st.markdown(f"""
            <div class="total-box">
                <h3>Total de Horas</h3>
                <div class="total-value">{total_horas_filtrado}</div>
            </div>
            """, unsafe_allow_html=True)
           
        else:
            st.warning("⚠️ No se encontraron datos para el período y año especificados.")
 
# Función para mostrar la sección "Horas por servicio"
def mostrar_horas_por_servicio():
    st.markdown("## 🛠️ Horas por Servicio")
    uploaded_file_servicio = st.file_uploader("📂 **Sube el archivo Excel con las horas por servicio**", type=["xlsx"], key="horas_servicio")
    col1, col2 = st.columns(2)
    mes_seleccionado_servicio = col1.selectbox("📅 **Selecciona el mes**", list(range(1, 13)), index=0, key="mes_servicio")
    año_seleccionado_servicio = col2.selectbox("📆 **Selecciona el año**", list(range(2020, 2031)), index=5, key="año_servicio")
   
    if uploaded_file_servicio:
        xls = pd.ExcelFile(uploaded_file_servicio)
        df_total = pd.concat([pd.read_excel(xls, sheet_name=sheet).assign(Empleado=sheet) for sheet in xls.sheet_names], ignore_index=True)
        df_filtrado = df_total[(df_total["mes"] == mes_seleccionado_servicio) & (df_total["año"] == año_seleccionado_servicio)]
        servicios = df_filtrado.groupby("servicio")["horas"].sum().reset_index()
       
        if not servicios.empty:
            st.markdown("## 📌 **Selecciona un servicio para ver detalles**")
            # Organizar los botones en una cuadrícula (3 por fila)
            cols = st.columns(3)
            for i, row in enumerate(servicios.itertuples()):
                servicio = row.servicio
                horas_totales = row.horas
                if cols[i % 3].button(f"🔧 {servicio} - {horas_totales} horas", use_container_width=True):
                    st.session_state.servicio_seleccionado = servicio
                    df_servicio = df_filtrado[df_filtrado["servicio"] == servicio].copy()
                    df_servicio["Fecha"] = df_servicio.apply(lambda row: f"{row['dia']}-{row['mes']}-{row['año']}", axis=1)
                    df_mostrar = df_servicio[["Empleado", "Fecha", "actividad", "servicio", "horas"]]
                    st.session_state.df_mostrar = df_mostrar
   
    # Mostrar la tabla si ya hay datos guardados
    if st.session_state.df_mostrar is not None:
        df_mostrar = st.session_state.df_mostrar
       
        # Filtro multiselect para "Horas por servicio"
        empleados = df_mostrar["Empleado"].unique().tolist()
       
        # Filtro multiselect de empleados
        filtro_empleados = st.multiselect(
            "🔎 **Filtrar por Empleado(s)**",
            options=empleados,
            default=[],
            key="filtro_empleados_servicio"
        )
       
        # Aplicar filtro sin borrar la tabla
        df_filtrado = df_mostrar.copy()
        if filtro_empleados:
            df_filtrado = df_filtrado[df_filtrado["Empleado"].isin(filtro_empleados)]
       
        # Mostrar número de registros y dataframe filtrado
        st.write(f"Mostrando {len(df_filtrado)} de {len(df_mostrar)} registros")
       
        # Mostrar dataframe
        st.dataframe(df_filtrado, hide_index=True)
       
        # Calcular el total filtrado
        total_horas_filtrado = df_filtrado["horas"].sum()
       
        # Mostrar total de horas en un cuadro destacado debajo de la tabla
        st.markdown(f"""
        <div class="total-box">
            <h3>Total de Horas</h3>
            <div class="total-value">{total_horas_filtrado}</div>
        </div>
        """, unsafe_allow_html=True)
 
# Llamar solo a la función correspondiente
if pagina_seleccionada == "Horas trabajadas":
    mostrar_horas_trabajadas()
elif pagina_seleccionada == "Horas por servicio":
    mostrar_horas_por_servicio()
