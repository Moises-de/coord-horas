import streamlit as st
import pandas as pd

# Configurar la interfaz
st.set_page_config(page_title="Gestión de Horas", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
        .menu-container {
            display: flex;
            flex-direction: column;
        }
        .menu-button {
            padding: 12px;
            margin: 5px 0;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            border: 2px solid transparent;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            background-color: #ffffff;
            color: #333;
        }
        .menu-button:hover {
            background-color: #e6e6e6;
        }
        .menu-button-selected {
            border: 2px solid #ff4b4b;
            background-color: #ffecec;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar con navegación
st.sidebar.title("📌 Menú")
paginas = ["Horas trabajadas", "Horas por servicio"]
pagina_seleccionada = st.session_state.get("pagina_seleccionada", paginas[0])

st.sidebar.markdown('<div class="menu-container">', unsafe_allow_html=True)
for pagina in paginas:
    clase = "menu-button-selected" if pagina == pagina_seleccionada else "menu-button"
    if st.sidebar.button(f"🔹 {pagina}", key=pagina):
        st.session_state.pagina_seleccionada = pagina
        pagina_seleccionada = pagina
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Sección "Horas trabajadas"
if pagina_seleccionada == "Horas trabajadas":
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
            st.dataframe(df_resultado)
        else:
            st.warning("⚠️ No se encontraron datos para el período y año especificados.")

# Sección "Horas por servicio"
elif pagina_seleccionada == "Horas por servicio":
    st.title("🛠️ Horas por Servicio")

    uploaded_file_servicio = st.file_uploader("📂 Sube el archivo Excel con las horas por servicio", type=["xlsx"], key="horas_servicio")

    col1, col2 = st.columns(2)
    mes_seleccionado_servicio = col1.selectbox("📅 Selecciona el mes", list(range(1, 13)), index=0, key="mes_servicio")
    año_seleccionado_servicio = col2.selectbox("📆 Selecciona el año", list(range(2020, 2031)), index=5, key="año_servicio")

    if uploaded_file_servicio:
        xls = pd.ExcelFile(uploaded_file_servicio)
        df_total = pd.concat([pd.read_excel(xls, sheet_name=sheet).assign(Empleado=sheet) for sheet in xls.sheet_names], ignore_index=True)

        df_filtrado = df_total[(df_total["mes"] == mes_seleccionado_servicio) & (df_total["año"] == año_seleccionado_servicio)]

        servicios = df_filtrado.groupby("servicio")["horas"].sum().reset_index()

        if not servicios.empty:
            st.subheader("📌 Selecciona un servicio para ver detalles")

            for _, row in servicios.iterrows():
                servicio = row["servicio"]
                horas_totales = row["horas"]

                if st.button(f"🛠 {servicio} - {horas_totales} horas"):
                    df_servicio = df_filtrado[df_filtrado["servicio"] == servicio].copy()
                    df_servicio["Fecha"] = df_servicio.apply(lambda row: f"{row['dia']}-{row['mes']}-{row['año']}", axis=1)
                    df_mostrar = df_servicio[["Empleado", "Fecha", "actividad", "servicio", "horas"]]

                    st.write(f"🔍 Detalles del servicio **{servicio}**")
                    st.dataframe(df_mostrar)
        else:
            st.warning("⚠️ No se encontraron datos para el período y año especificados.")
