import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide")
st.title("FIBRA ANALYTICS | Reporte de Dividendos")

# -------------------------
# CARGA DE CSV
# -------------------------
try:
    dividendos_all = pd.read_csv("data/dividendos.csv")
    precios_all = pd.read_csv("data/precios.csv")
except Exception as e:
    st.error(f"Error cargando CSV: {e}")
    st.stop()

# -------------------------
# LIMPIEZA DE FECHAS
# -------------------------
try:
    dividendos_all["Fecha"] = pd.to_datetime(dividendos_all["Fecha"])
    precios_all["Fecha"] = pd.to_datetime(precios_all["Fecha"])
except Exception as e:
    st.error(f"Error en fechas: {e}")
    st.stop()

# -------------------------
# FIBRAS
# -------------------------
fibras = {
    "Fibra Monterrey": "FMTY14.MX",
    "Fibra Uno": "FUNO11.MX",
    "Fibra Macquarie": "FIBRAMQ12.MX",
    "Fibra CFE": "FCFE18.MX",
    "Fibra Danhos": "DANHOS13.MX",
    "Fibra Shop": "FSHOP13.MX",
    "Prologis Fibra": "FIBRAPL14.MX",
    "Fibra Nova": "FNOVA17.MX"
}

# -------------------------
# FILTROS
# -------------------------
col1, col2 = st.columns(2)

with col1:
    fibra_seleccionada = st.selectbox(
        "Selecciona una FIBRA",
        list(fibras.keys())
    )

with col2:
    rango_fechas = st.date_input("Rango de fechas", [])

ticker = fibras[fibra_seleccionada]

# -------------------------
# FILTRADO
# -------------------------
dividendos = dividendos_all[dividendos_all["ticker"] == ticker].copy()
precios = precios_all[precios_all["ticker"] == ticker].copy()

if dividendos.empty or precios.empty:
    st.warning("No hay datos para esta FIBRA")
    st.stop()

# -------------------------
# MERGE
# -------------------------
df = pd.merge(dividendos, precios, on="Fecha", how="left")
df = df.sort_values("Fecha", ascending=False)

if df.empty:
    st.warning("No hay datos disponibles")
    st.stop()

# -------------------------
# MÉTRICAS
# -------------------------
precio_actual = precios.sort_values("Fecha")["Precio"].iloc[-1]

ultimo_pago = df.iloc[0]["Fecha"]
monto_ultimo_pago = df.iloc[0]["Dividendo"]

# -------------------------
# YIELD TRAILING 365 DÍAS EXACTO
# -------------------------

# asegurar tipo fecha
dividendos["Fecha"] = pd.to_datetime(dividendos["Fecha"])
precios["Fecha"] = pd.to_datetime(precios["Fecha"])

# fecha de referencia (último dato disponible)
end_date = precios["Fecha"].max()
start_date = end_date - pd.Timedelta(days=365)

# filtrar dividendos dentro de ventana exacta
dividendos_ttm = dividendos[
    (dividendos["Fecha"] > start_date) &
    (dividendos["Fecha"] <= end_date)
]

# suma real TTM
ttm_dividends = dividendos_ttm["Dividendo"].sum()

# precio más reciente
precio_actual = precios.sort_values("Fecha")["Precio"].iloc[-1]

# yield final
yield_anual = (
    (ttm_dividends / precio_actual) * 100
    if precio_actual > 0 else 0
)

# -------------------------
# SCORECARDS
# -------------------------
st.subheader("Resumen de Dividendos")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Precio Actual", f"${precio_actual:.2f}")
c2.metric("Último Pago", ultimo_pago.strftime("%Y-%m-%d"))
c3.metric("Monto Último Pago", f"${monto_ultimo_pago:.4f}")
c4.metric("Yield Anualizado", f"{yield_anual:.2f}%")

# -------------------------
# FILTRO DE FECHAS
# -------------------------
df_filtrado = df.copy()

if len(rango_fechas) == 2:
    inicio = pd.to_datetime(rango_fechas[0])
    fin = pd.to_datetime(rango_fechas[1])

    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= inicio) &
        (df_filtrado["Fecha"] <= fin)
    ]

df_filtrado = df_filtrado.sort_values("Fecha")

# -------------------------
# GRÁFICA
# -------------------------
st.subheader("Histórico de Dividendos")

fig = px.line(
    df_filtrado,
    x="Fecha",
    y="Dividendo",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TABLA LIMPIA
# -------------------------
st.subheader("Tabla de Dividendos")

tabla = df_filtrado.copy()

# -------------------------
# ORDENAR (más reciente primero)s
# -------------------------
tabla = tabla.sort_values("Fecha", ascending=False)

# -------------------------
# eliminar columnas ticker si existen
# -------------------------
tabla = tabla.loc[:, ~tabla.columns.str.contains("ticker")]

# -------------------------
# formato
# -------------------------
tabla["Fecha"] = tabla["Fecha"].dt.strftime("%Y-%m-%d")

if "Dividendo" in tabla.columns:
    tabla["Dividendo"] = tabla["Dividendo"].round(4)

if "Precio" in tabla.columns:
    tabla["Precio"] = tabla["Precio"].round(2)

st.dataframe(tabla, use_container_width=True)