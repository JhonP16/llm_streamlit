"""
================================================================================
 ANÁLISIS ECONÓMICO MUNDIAL - Simulación interactiva con Streamlit
================================================================================
Simula series de tiempo (2015-2024) de indicadores macroeconómicos para las
20 economías más relevantes del mundo y ofrece análisis cuantitativo,
cualitativo y gráfico con interacción dinámica.

Ejecutar con:
    streamlit run app.py

Los datos son SIMULADOS con fines académicos: se parte de valores de
referencia aproximados (PIB, crecimiento, inflación, desempleo, deuda, IDH)
y se generan series aleatorias reproducibles (semilla configurable) alrededor
de esos valores. No deben usarse como fuente estadística oficial.
================================================================================
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Análisis Económico Mundial",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

ANIO_INICIAL, ANIO_FINAL = 2015, 2024
ANIOS = list(range(ANIO_INICIAL, ANIO_FINAL + 1))

# ------------------------------------------------------------------------------
# 1. PARÁMETROS BASE DE LAS 20 ECONOMÍAS (valores de referencia aproximados)
# ------------------------------------------------------------------------------
PAISES_BASE = {
    "Estados Unidos":  {"iso3": "USA", "region": "Norteamérica",  "gdp_base": 27000, "gdp_growth_mean": 2.3, "inflation_mean": 3.2,  "unemployment_mean": 3.9,  "population": 335,  "hdi_base": 0.927, "debt_gdp_base": 122},
    "China":           {"iso3": "CHN", "region": "Asia",          "gdp_base": 18500, "gdp_growth_mean": 4.8, "inflation_mean": 1.0,  "unemployment_mean": 5.1,  "population": 1410, "hdi_base": 0.788, "debt_gdp_base": 88},
    "Japón":           {"iso3": "JPN", "region": "Asia",          "gdp_base": 4200,  "gdp_growth_mean": 0.9, "inflation_mean": 2.5,  "unemployment_mean": 2.6,  "population": 124,  "hdi_base": 0.920, "debt_gdp_base": 255},
    "Alemania":        {"iso3": "DEU", "region": "Europa",        "gdp_base": 4500,  "gdp_growth_mean": 0.4, "inflation_mean": 2.9,  "unemployment_mean": 3.2,  "population": 84,   "hdi_base": 0.942, "debt_gdp_base": 64},
    "India":           {"iso3": "IND", "region": "Asia",          "gdp_base": 3900,  "gdp_growth_mean": 6.8, "inflation_mean": 5.4,  "unemployment_mean": 7.8,  "population": 1428, "hdi_base": 0.644, "debt_gdp_base": 82},
    "Reino Unido":     {"iso3": "GBR", "region": "Europa",        "gdp_base": 3400,  "gdp_growth_mean": 1.1, "inflation_mean": 3.4,  "unemployment_mean": 4.2,  "population": 68,   "hdi_base": 0.940, "debt_gdp_base": 100},
    "Francia":         {"iso3": "FRA", "region": "Europa",        "gdp_base": 3100,  "gdp_growth_mean": 0.9, "inflation_mean": 2.6,  "unemployment_mean": 7.3,  "population": 68,   "hdi_base": 0.910, "debt_gdp_base": 110},
    "Italia":          {"iso3": "ITA", "region": "Europa",        "gdp_base": 2300,  "gdp_growth_mean": 0.6, "inflation_mean": 2.3,  "unemployment_mean": 7.6,  "population": 59,   "hdi_base": 0.906, "debt_gdp_base": 137},
    "Brasil":          {"iso3": "BRA", "region": "Sudamérica",    "gdp_base": 2200,  "gdp_growth_mean": 2.5, "inflation_mean": 4.5,  "unemployment_mean": 8.0,  "population": 216,  "hdi_base": 0.760, "debt_gdp_base": 85},
    "Canadá":          {"iso3": "CAN", "region": "Norteamérica",  "gdp_base": 2100,  "gdp_growth_mean": 1.5, "inflation_mean": 2.9,  "unemployment_mean": 5.8,  "population": 39,   "hdi_base": 0.935, "debt_gdp_base": 106},
    "Rusia":           {"iso3": "RUS", "region": "Eurasia",       "gdp_base": 2100,  "gdp_growth_mean": 1.5, "inflation_mean": 6.8,  "unemployment_mean": 3.0,  "population": 144,  "hdi_base": 0.821, "debt_gdp_base": 20},
    "Corea del Sur":   {"iso3": "KOR", "region": "Asia",          "gdp_base": 1900,  "gdp_growth_mean": 2.2, "inflation_mean": 2.5,  "unemployment_mean": 2.9,  "population": 52,   "hdi_base": 0.925, "debt_gdp_base": 55},
    "Australia":       {"iso3": "AUS", "region": "Oceanía",       "gdp_base": 1800,  "gdp_growth_mean": 2.0, "inflation_mean": 3.5,  "unemployment_mean": 4.0,  "population": 26,   "hdi_base": 0.951, "debt_gdp_base": 45},
    "México":          {"iso3": "MEX", "region": "Norteamérica",  "gdp_base": 1800,  "gdp_growth_mean": 2.1, "inflation_mean": 4.7,  "unemployment_mean": 2.8,  "population": 128,  "hdi_base": 0.781, "debt_gdp_base": 52},
    "España":          {"iso3": "ESP", "region": "Europa",        "gdp_base": 1600,  "gdp_growth_mean": 2.4, "inflation_mean": 2.9,  "unemployment_mean": 11.8, "population": 48,   "hdi_base": 0.905, "debt_gdp_base": 106},
    "Indonesia":       {"iso3": "IDN", "region": "Asia",          "gdp_base": 1400,  "gdp_growth_mean": 5.0, "inflation_mean": 3.0,  "unemployment_mean": 5.3,  "population": 279,  "hdi_base": 0.713, "debt_gdp_base": 39},
    "Países Bajos":    {"iso3": "NLD", "region": "Europa",        "gdp_base": 1100,  "gdp_growth_mean": 0.6, "inflation_mean": 3.2,  "unemployment_mean": 3.6,  "population": 18,   "hdi_base": 0.946, "debt_gdp_base": 46},
    "Arabia Saudita":  {"iso3": "SAU", "region": "Medio Oriente", "gdp_base": 1100,  "gdp_growth_mean": 3.5, "inflation_mean": 2.0,  "unemployment_mean": 4.8,  "population": 36,   "hdi_base": 0.875, "debt_gdp_base": 26},
    "Suiza":           {"iso3": "CHE", "region": "Europa",        "gdp_base": 900,   "gdp_growth_mean": 1.3, "inflation_mean": 1.5,  "unemployment_mean": 2.3,  "population": 9,    "hdi_base": 0.967, "debt_gdp_base": 40},
    "Turquía":         {"iso3": "TUR", "region": "Eurasia",       "gdp_base": 1100,  "gdp_growth_mean": 3.5, "inflation_mean": 30.0, "unemployment_mean": 9.0,  "population": 87,   "hdi_base": 0.855, "debt_gdp_base": 32},
}

INDICADORES_NUMERICOS = [
    "PIB (Miles de Millones USD)",
    "Crecimiento PIB (%)",
    "Inflación (%)",
    "Desempleo (%)",
    "Deuda/PIB (%)",
    "IDH",
    "Población (Millones)",
    "PIB per cápita (USD)",
]


# ------------------------------------------------------------------------------
# 2. MOTOR DE SIMULACIÓN
# ------------------------------------------------------------------------------
def _generar_serie_pais(nombre: str, params: dict, rng: np.random.Generator) -> pd.DataFrame:
    """Genera la serie 2015-2024 de un país a partir de sus parámetros base."""
    n = len(ANIOS)

    # Crecimiento del PIB: ruido normal alrededor de la media histórica
    crecimientos = rng.normal(params["gdp_growth_mean"], 1.2, n)

    # PIB inicial estimado retrocediendo desde el valor "actual" (gdp_base)
    pib_inicial = params["gdp_base"] / ((1 + params["gdp_growth_mean"] / 100) ** (n - 1))
    pibs = [pib_inicial]
    for g in crecimientos[1:]:
        pibs.append(pibs[-1] * (1 + g / 100))

    inflaciones = np.clip(
        rng.normal(params["inflation_mean"], max(params["inflation_mean"] * 0.18, 0.4), n), -2, None
    )
    desempleos = np.clip(rng.normal(params["unemployment_mean"], 0.6, n), 1, None)
    deudas = np.clip(rng.normal(params["debt_gdp_base"], params["debt_gdp_base"] * 0.05, n), 5, None)
    idh = np.clip(rng.normal(params["hdi_base"], 0.004, n), 0, 1)
    poblaciones = params["population"] * np.cumprod(1 + rng.normal(0.006, 0.002, n))

    df = pd.DataFrame(
        {
            "País": nombre,
            "Región": params["region"],
            "ISO3": params["iso3"],
            "Año": ANIOS,
            "PIB (Miles de Millones USD)": pibs,
            "Crecimiento PIB (%)": crecimientos,
            "Inflación (%)": inflaciones,
            "Desempleo (%)": desempleos,
            "Deuda/PIB (%)": deudas,
            "IDH": idh,
            "Población (Millones)": poblaciones,
        }
    )
    return df


@st.cache_data(show_spinner=False)
def simular_datos(semilla: int) -> pd.DataFrame:
    """Simula la serie completa (todos los países, 2015-2024) para una semilla dada."""
    rng = np.random.default_rng(semilla)
    partes = [_generar_serie_pais(nombre, params, rng) for nombre, params in PAISES_BASE.items()]
    df = pd.concat(partes, ignore_index=True)
    df["PIB per cápita (USD)"] = (
        df["PIB (Miles de Millones USD)"] / df["Población (Millones)"] * 1000
    )
    return df


def clasificar_economia(row: pd.Series) -> str:
    """Clasificación cualitativa basada en reglas simples sobre los indicadores."""
    if row["Crecimiento PIB (%)"] > 4 and row["Inflación (%)"] < 6:
        return "🚀 Emergente en expansión"
    if row["Inflación (%)"] > 8:
        return "⚠️ Riesgo inflacionario"
    if row["Desempleo (%)"] > 8:
        return "🔻 Alto desempleo"
    if row["IDH"] > 0.9 and row["Crecimiento PIB (%)"] < 2:
        return "🏛️ Desarrollada estable"
    if row["Deuda/PIB (%)"] > 100:
        return "💰 Alto endeudamiento"
    return "➖ Desempeño moderado"


# ------------------------------------------------------------------------------
# 3. BARRA LATERAL: CONTROLES DE INTERACCIÓN
# ------------------------------------------------------------------------------
st.sidebar.title("⚙️ Controles de simulación")

if "semilla" not in st.session_state:
    st.session_state.semilla = 42

if st.sidebar.button("🔄 Regenerar simulación", use_container_width=True):
    st.session_state.semilla = int(np.random.randint(0, 1_000_000))

st.sidebar.caption(f"Semilla actual: `{st.session_state.semilla}`")

todos_paises = list(PAISES_BASE.keys())
default_paises = ["Estados Unidos", "China", "India", "Alemania", "Brasil", "Japón", "México", "Rusia"]

paises_sel = st.sidebar.multiselect(
    "Países a comparar", options=todos_paises, default=default_paises
)

regiones_disp = sorted({p["region"] for p in PAISES_BASE.values()})
regiones_sel = st.sidebar.multiselect("Filtrar por región (opcional)", options=regiones_disp, default=[])

rango_anios = st.sidebar.slider(
    "Rango de años", min_value=ANIO_INICIAL, max_value=ANIO_FINAL, value=(ANIO_INICIAL, ANIO_FINAL)
)

indicador_foco = st.sidebar.selectbox(
    "Indicador principal para gráficos", options=INDICADORES_NUMERICOS, index=0
)

top_n = st.sidebar.slider("Top N países (rankings)", min_value=3, max_value=20, value=10)

mostrar_datos_crudos = st.sidebar.checkbox("Mostrar tabla de datos crudos", value=False)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Datos simulados con fines académicos a partir de valores de referencia "
    "aproximados. No constituyen una fuente estadística oficial."
)

# ------------------------------------------------------------------------------
# 4. GENERACIÓN Y FILTRADO DE DATOS
# ------------------------------------------------------------------------------
df_full = simular_datos(st.session_state.semilla)

df_filtrado = df_full[(df_full["Año"] >= rango_anios[0]) & (df_full["Año"] <= rango_anios[1])].copy()
if regiones_sel:
    df_filtrado = df_filtrado[df_filtrado["Región"].isin(regiones_sel)]
if paises_sel:
    df_vista = df_filtrado[df_filtrado["País"].isin(paises_sel)].copy()
else:
    df_vista = df_filtrado.copy()

if df_vista.empty:
    st.warning("No hay países seleccionados o el filtro actual no arroja resultados. Ajusta los controles del panel lateral.")
    st.stop()

anio_max = int(df_vista["Año"].max())
df_ultimo_anio = df_filtrado[df_filtrado["Año"] == anio_max].copy()
df_ultimo_anio["Clasificación"] = df_ultimo_anio.apply(clasificar_economia, axis=1)

# ------------------------------------------------------------------------------
# 5. ENCABEZADO Y KPIs DINÁMICOS
# ------------------------------------------------------------------------------
st.title("🌍 Análisis Económico Mundial — Simulación Interactiva")
st.caption(
    f"Economías simuladas: {len(PAISES_BASE)}  ·  Periodo: {ANIO_INICIAL}-{ANIO_FINAL}  ·  "
    f"Vista actual: {df_vista['País'].nunique()} país(es), {rango_anios[0]}-{rango_anios[1]}"
)

vista_ultimo_anio_sel = df_vista[df_vista["Año"] == df_vista["Año"].max()]

col1, col2, col3, col4 = st.columns(4)
with col1:
    lider_pib = vista_ultimo_anio_sel.loc[vista_ultimo_anio_sel["PIB (Miles de Millones USD)"].idxmax()]
    st.metric("Mayor PIB (selección)", lider_pib["País"], f"{lider_pib['PIB (Miles de Millones USD)']:,.0f} MM USD")
with col2:
    lider_crec = vista_ultimo_anio_sel.loc[vista_ultimo_anio_sel["Crecimiento PIB (%)"].idxmax()]
    st.metric("Mayor crecimiento", lider_crec["País"], f"{lider_crec['Crecimiento PIB (%)']:.1f}%")
with col3:
    lider_inf = vista_ultimo_anio_sel.loc[vista_ultimo_anio_sel["Inflación (%)"].idxmin()]
    st.metric("Menor inflación", lider_inf["País"], f"{lider_inf['Inflación (%)']:.1f}%")
with col4:
    lider_idh = vista_ultimo_anio_sel.loc[vista_ultimo_anio_sel["IDH"].idxmax()]
    st.metric("Mayor IDH", lider_idh["País"], f"{lider_idh['IDH']:.3f}")

st.markdown("---")

# ------------------------------------------------------------------------------
# 6. PESTAÑAS DE ANÁLISIS
# ------------------------------------------------------------------------------
tab_cuant, tab_cual, tab_graf, tab_datos = st.tabs(
    ["📊 Análisis cuantitativo", "🧭 Análisis cualitativo", "📈 Análisis gráfico", "🗂️ Datos"]
)

# --- 6.1 CUANTITATIVO -----------------------------------------------------
with tab_cuant:
    st.subheader("Estadística descriptiva")
    st.caption(f"Calculada sobre la selección actual ({df_vista['País'].nunique()} país(es), {rango_anios[0]}-{rango_anios[1]})")
    desc = df_vista[INDICADORES_NUMERICOS].describe().T
    desc = desc.rename(
        columns={"count": "n", "mean": "Media", "std": "Desv. Est.", "min": "Mín", "max": "Máx",
                 "25%": "P25", "50%": "Mediana", "75%": "P75"}
    )
    st.dataframe(desc.style.format("{:.2f}"), use_container_width=True)

    st.subheader(f"Ranking Top {top_n} · {indicador_foco} ({anio_max})")
    ranking = (
        df_ultimo_anio.sort_values(indicador_foco, ascending=False)
        .head(top_n)[["País", "Región", indicador_foco]]
        .reset_index(drop=True)
    )
    ranking.index = ranking.index + 1
    st.dataframe(ranking.style.format({indicador_foco: "{:.2f}"}), use_container_width=True)

    st.subheader("Matriz de correlación entre indicadores")
    corr = df_vista[INDICADORES_NUMERICOS].corr()
    fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto"
    )
    fig_corr.update_layout(height=500, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_corr, use_container_width=True)

    with st.expander("¿Cómo interpretar la matriz de correlación?"):
        st.write(
            "Valores cercanos a **1** indican relación positiva fuerte (ambos indicadores suben juntos); "
            "valores cercanos a **-1** indican relación inversa fuerte; valores cercanos a **0** indican "
            "poca o ninguna relación lineal entre los indicadores."
        )

# --- 6.2 CUALITATIVO --------------------------------------------------------
with tab_cual:
    st.subheader(f"Clasificación económica por país ({anio_max})")
    st.caption("Categorías derivadas por reglas a partir del crecimiento, inflación, desempleo, deuda e IDH.")

    tabla_cual = df_ultimo_anio[df_ultimo_anio["País"].isin(df_vista["País"].unique())][
        ["País", "Región", "Clasificación"]
    ].reset_index(drop=True)
    st.dataframe(tabla_cual, use_container_width=True)

    conteo_cat = df_ultimo_anio["Clasificación"].value_counts().reset_index()
    conteo_cat.columns = ["Clasificación", "Cantidad de países"]
    fig_cat = px.bar(
        conteo_cat, x="Clasificación", y="Cantidad de países", color="Clasificación",
        title=f"Distribución de categorías económicas — todas las economías ({anio_max})",
    )
    fig_cat.update_layout(showlegend=False, height=420)
    st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("Lectura narrativa automática")
    top_pib = vista_ultimo_anio_sel.loc[vista_ultimo_anio_sel["PIB (Miles de Millones USD)"].idxmax(), "País"]
    top_crec = vista_ultimo_anio_sel.loc[vista_ultimo_anio_sel["Crecimiento PIB (%)"].idxmax(), "País"]
    top_riesgo = vista_ultimo_anio_sel.loc[vista_ultimo_anio_sel["Inflación (%)"].idxmax(), "País"]
    corr_pib_idh = df_vista["PIB per cápita (USD)"].corr(df_vista["IDH"])

    texto = f"""
En la selección actual, **{top_pib}** concentra el mayor PIB nominal, mientras que
**{top_crec}** presenta el mayor ritmo de crecimiento económico en {anio_max}.
**{top_riesgo}** es la economía con mayor presión inflacionaria dentro del grupo analizado.

La correlación entre **PIB per cápita** e **IDH** en la selección es de **{corr_pib_idh:.2f}**,
lo que sugiere una relación {"fuerte y positiva" if corr_pib_idh > 0.6 else "moderada" if corr_pib_idh > 0.3 else "débil"}
entre el nivel de ingreso y el desarrollo humano en este conjunto de países.
"""
    st.markdown(texto)

# --- 6.3 GRÁFICO ------------------------------------------------------------
with tab_graf:
    st.subheader(f"Evolución de {indicador_foco} ({rango_anios[0]}-{rango_anios[1]})")
    fig_linea = px.line(
        df_vista, x="Año", y=indicador_foco, color="País", markers=True,
        hover_data=["Región"],
    )
    fig_linea.update_layout(height=460, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_linea, use_container_width=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.subheader(f"Ranking {indicador_foco} ({anio_max})")
        fig_barras = px.bar(
            vista_ultimo_anio_sel.sort_values(indicador_foco, ascending=True),
            x=indicador_foco, y="País", orientation="h", color="Región",
        )
        fig_barras.update_layout(height=460, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_der:
        st.subheader(f"PIB per cápita vs. Crecimiento ({anio_max})")
        fig_disp = px.scatter(
            vista_ultimo_anio_sel, x="PIB per cápita (USD)", y="Crecimiento PIB (%)",
            size="Población (Millones)", color="Región", hover_name="País",
            size_max=45,
        )
        fig_disp.update_layout(height=460, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_disp, use_container_width=True)

    st.subheader(f"Mapa mundial · {indicador_foco} ({anio_max})")
    fig_mapa = px.choropleth(
        df_ultimo_anio, locations="ISO3", color=indicador_foco, hover_name="País",
        color_continuous_scale="Viridis",
    )
    fig_mapa.update_layout(height=480, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_mapa, use_container_width=True)

    st.subheader("Comparación multidimensional (radar)")
    paises_radar = st.multiselect(
        "Países en el radar (máx. 6)", options=list(df_vista["País"].unique()),
        default=list(df_vista["País"].unique())[:4], max_selections=6, key="radar_sel",
    )
    if paises_radar:
        indicadores_radar = ["PIB (Miles de Millones USD)", "Crecimiento PIB (%)", "IDH",
                              "PIB per cápita (USD)", "Deuda/PIB (%)"]
        base_radar = df_ultimo_anio.set_index("País")[indicadores_radar]
        # Normalización min-max para hacer comparables las escalas
        norm_radar = (base_radar - base_radar.min()) / (base_radar.max() - base_radar.min() + 1e-9)

        fig_radar = go.Figure()
        for pais in paises_radar:
            valores = norm_radar.loc[pais].tolist()
            fig_radar.add_trace(go.Scatterpolar(
                r=valores + [valores[0]],
                theta=indicadores_radar + [indicadores_radar[0]],
                fill="toself", name=pais,
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=500, showlegend=True,
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption("Valores normalizados (0-1) respecto al conjunto completo de economías simuladas en el último año.")
    else:
        st.info("Selecciona al menos un país para construir el radar.")

# --- 6.4 DATOS ---------------------------------------------------------------
with tab_datos:
    st.subheader("Datos simulados (según filtros activos)")
    st.dataframe(df_vista.sort_values(["País", "Año"]).reset_index(drop=True), use_container_width=True)
    st.download_button(
        "⬇️ Descargar CSV de la selección actual",
        data=df_vista.to_csv(index=False).encode("utf-8"),
        file_name="datos_economicos_simulados.csv",
        mime="text/csv",
    )
    if mostrar_datos_crudos:
        st.subheader("Dataset completo simulado (todas las economías, todos los años)")
        st.dataframe(df_full, use_container_width=True)