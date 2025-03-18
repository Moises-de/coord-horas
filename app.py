import streamlit as st
import pandas as pd



# Configurar la interfaz
st.set_page_config(page_title="Gestión de Horas", layout="wide")

# Inicializar el estado de la sección seleccionada y los filtros
if "pagina_seleccionada" not in st.session_state:
    st.session_state.pagina_seleccionada = "Horas trabajadas"
    st.session_state.df_mostrar = None
    st.session_state.servicio_seleccionado = None
    st.session_state.filtro_empleado_servicio = "Todos"

# Sidebar con navegación
st.sidebar.title("📌 Menú")
pagina_seleccionada = st.sidebar.radio("Selecciona una opción:", ["Horas trabajadas", "Horas por servicio"])

# Si el usuario cambia de sección, resetear los valores
if pagina_seleccionada != st.session_state.pagina_seleccionada:
    st.session_state.pagina_seleccionada = pagina_seleccionada
    st.session_state.df_mostrar = None
    st.session_state.servicio_seleccionado = None
    st.session_state.filtro_empleado_servicio = "Todos"

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

            # 🔹 Filtros exclusivos de "Horas trabajadas"
            empleados = df_resultado["Empleado"].unique().tolist()
            estados = df_resultado["Estado"].unique().tolist()

            filtro_empleado = st.selectbox("🔎 Filtrar por Empleado", ["Todos"] + empleados, key="filtro_empleado")
            filtro_estado = st.selectbox("🔎 Filtrar por Estado", ["Todos"] + estados, key="filtro_estado")

            # Aplicar filtros manualmente
            if filtro_empleado != "Todos":
                df_resultado = df_resultado[df_resultado["Empleado"] == filtro_empleado]
            if filtro_estado != "Todos":
                df_resultado = df_resultado[df_resultado["Estado"] == filtro_estado]

            st.dataframe(df_resultado)

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

            # 🔹 Organizar los botones en una cuadrícula (3 por fila)
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

        # 🔹 Filtro exclusivo de "Horas por servicio"
        empleados = df_mostrar["Empleado"].unique().tolist()

        # Inicializar el filtro si no existe
        if "filtro_empleado_servicio" not in st.session_state:
            st.session_state.filtro_empleado_servicio = "Todos"

        filtro_empleado = st.selectbox("🔎 **Filtrar por Empleado**", ["Todos"] + empleados, key="filtro_empleado_servicio")

        # Aplicar filtro sin borrar la tabla
        if filtro_empleado != "Todos":
            df_mostrar = df_mostrar[df_mostrar["Empleado"] == filtro_empleado]

        st.dataframe(df_mostrar)

# Llamar solo a la función correspondiente
if pagina_seleccionada == "Horas trabajadas":
    mostrar_horas_trabajadas()
elif pagina_seleccionada == "Horas por servicio":
    mostrar_horas_por_servicio()
