import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# Configuración
# -----------------------------
st.set_page_config(
    page_title="Análisis de los Mejores Países",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Simulador de los Mejores Países del Mundo")

st.write("""
Este sistema simula información de distintos países y permite realizar:

- Análisis cuantitativo
- Análisis cualitativo
- Visualizaciones gráficas
- Interacción dinámica
""")

# -----------------------------
# Generación de datos simulados
# -----------------------------

np.random.seed(42)

paises = [
    "Suiza",
    "Canadá",
    "Suecia",
    "Noruega",
    "Finlandia",
    "Dinamarca",
    "Alemania",
    "Australia",
    "Japón",
    "Nueva Zelanda",
    "Países Bajos",
    "Singapur",
    "Islandia",
    "Reino Unido",
    "Corea del Sur"
]

df = pd.DataFrame({
    "País": paises,
    "PIB per cápita": np.random.randint(25000, 95000, len(paises)),
    "Esperanza de vida": np.random.randint(72, 86, len(paises)),
    "Educación": np.random.randint(60, 100, len(paises)),
    "Seguridad": np.random.randint(60, 100, len(paises)),
    "Calidad de vida": np.random.randint(60, 100, len(paises))
})

# -----------------------------
# Índice General
# -----------------------------

df["Índice"] = (
    df["Educación"] +
    df["Seguridad"] +
    df["Calidad de vida"]
) / 3

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("Filtros")

pais = st.sidebar.selectbox(
    "Seleccione un país",
    df["País"]
)

metrica = st.sidebar.selectbox(
    "Seleccione una métrica",
    [
        "PIB per cápita",
        "Esperanza de vida",
        "Educación",
        "Seguridad",
        "Calidad de vida",
        "Índice"
    ]
)

# -----------------------------
# Mostrar datos
# -----------------------------

st.subheader("Datos simulados")

st.dataframe(df)

# -----------------------------
# Cuantitativo
# -----------------------------

st.header("📊 Análisis Cuantitativo")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Promedio",
    round(df[metrica].mean(),2)
)

col2.metric(
    "Máximo",
    round(df[metrica].max(),2)
)

col3.metric(
    "Mínimo",
    round(df[metrica].min(),2)
)

# -----------------------------
# Cualitativo
# -----------------------------

st.header("📝 Análisis Cualitativo")

fila = df[df["País"] == pais].iloc[0]

descripcion = ""

if fila["Índice"] >= 85:
    descripcion = "Excelente calidad de vida y desarrollo."
elif fila["Índice"] >= 75:
    descripcion = "Muy buen nivel de desarrollo."
elif fila["Índice"] >= 65:
    descripcion = "Buen desempeño general."
else:
    descripcion = "Presenta oportunidades de mejora."

st.success(f"""
### {pais}

- Índice General: **{fila['Índice']:.2f}**
- PIB per cápita: **${fila['PIB per cápita']:,}**
- Esperanza de vida: **{fila['Esperanza de vida']} años**

**Conclusión:**

{descripcion}
""")

# -----------------------------
# Gráfico de barras
# -----------------------------

st.header("📈 Comparación")

fig = px.bar(
    df.sort_values(metrica),
    x=metrica,
    y="País",
    orientation="h",
    color=metrica,
    title=f"Comparación de {metrica}"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Scatter
# -----------------------------

st.header("Relación PIB vs Calidad de Vida")

fig2 = px.scatter(
    df,
    x="PIB per cápita",
    y="Calidad de vida",
    size="Índice",
    hover_name="País",
    color="Índice"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Ranking
# -----------------------------

st.header("🏆 Ranking Mundial")

ranking = df.sort_values("Índice", ascending=False)

st.dataframe(
    ranking.reset_index(drop=True)
)

# -----------------------------
# Interacción
# -----------------------------

st.header("🎯 Simulador Interactivo")

educacion = st.slider(
    "Educación",
    0,
    100,
    80
)

seguridad = st.slider(
    "Seguridad",
    0,
    100,
    80
)

calidad = st.slider(
    "Calidad de vida",
    0,
    100,
    80
)

indice = (educacion + seguridad + calidad) / 3

st.metric(
    "Índice Calculado",
    round(indice,2)
)

if indice >= 85:
    st.balloons()
    st.success("Este país estaría entre los mejores del mundo.")
elif indice >= 70:
    st.info("Sería un país con muy buen desempeño.")
else:
    st.warning("Necesita mejorar sus indicadores.")
