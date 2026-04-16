import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide")

st.title("FIBRA ANALYTICS | Reporte de Dividendos | Fuente Yahoo Finance")

# -------------------------
# FIBRAS DISPONIBLES
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
# CARGA DE CSV
# -------------------------
dividendos_all = pd.read_csv("data/dividendos.csv")
precios_all = pd.read_csv("data/precios.csv")

# convertir fechas
dividendos_all["Fecha"] = pd.to_datetime(dividendos_all["Fecha"])
precios_all["Fecha"] = pd.to_datetime(precios_all["Fecha"])

# -------------------------
# FILTROS
# -------------------------
st.subheader("Filtros")

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
# FILTRAR DATA
# -------------------------
dividendos = dividendos_all[dividendos_all["ticker"] == ticker].copy()
precios = precios_all[precios_all["ticker"] == ticker].copy()

# -------------------------
# MERGE
# -------------------------
df = pd.merge(dividendos, precios, on="Fecha", how="left")

# 🔥 ELIMINAR DUPLICADOS DE TICKER
df = df.drop(columns=["ticker_y"])
df = df.rename(columns={"ticker_x": "ticker"})

df = df.sort_values("Fecha", ascending=False)

if df.empty:
    st.warning("No hay dividendos disponibles para esta FIBRA")
    st.stop()

# -------------------------
# SCORECARDS
# -------------------------
precio_hist = precios.sort_values("Fecha").tail(5).set_index("Fecha")

if precio_hist.empty:
    st.warning("No se pudo obtener el precio actual")
    st.stop()

precio_actual = precio_hist["Precio"].iloc[-1]
price_date = precio_hist.index[-1]

# ultimo pago
ultimo_pago = df.iloc[0]["Fecha"]
monto_ultimo_pago = df.iloc[0]["Dividendo"]

# dividendos últimos 12 meses
last_year = price_date - timedelta(days=365)

dividendos_12m = dividendos[
    dividendos["Fecha"] >= last_year
]["Dividendo"].sum()

yield_anual = (dividendos_12m / precio_actual) * 100 if precio_actual != 0 else 0

# -------------------------
# METRICAS
# -------------------------
st.subheader("Resumen de Dividendos")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Precio Actual", f"${precio_actual:.2f}")
c2.metric("Fecha Último Pago", ultimo_pago.strftime("%Y-%m-%d"))
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

if not df_filtrado.empty:
    ultima_fecha = df_filtrado["Fecha"].max()

    ultimo_valor = df_filtrado[
        df_filtrado["Fecha"] == ultima_fecha
    ]["Dividendo"].values[0]

    fig.add_annotation(
        x=ultima_fecha,
        y=ultimo_valor,
        text=f"${ultimo_valor:.4f}",
        showarrow=True
    )

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TABLA
# -------------------------
st.subheader("Tabla de Dividendos")

tabla = df_filtrado.sort_values("Fecha", ascending=False).copy()

if not tabla.empty:
    tabla["Fecha"] = tabla["Fecha"].dt.strftime("%Y-%m-%d")
    tabla["Dividendo"] = tabla["Dividendo"].round(4)
    tabla["Precio"] = tabla["Precio"].round(2)

    # 🔥 OPCIONAL: ocultar ticker si no lo quieres ver
    tabla = tabla.drop(columns=["ticker"])

    st.dataframe(tabla, use_container_width=True)
else:
    st.warning("No hay datos en el rango seleccionado")