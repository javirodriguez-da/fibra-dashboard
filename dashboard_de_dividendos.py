import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

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
    rango_fechas = st.date_input(
        "Rango de fechas",
        []
    )

ticker = fibras[fibra_seleccionada]
data = yf.Ticker(ticker)

# -------------------------
# DATOS
# -------------------------
dividendos = data.dividends.reset_index()
dividendos.columns = ["Fecha", "Dividendo"]

precios = data.history(period="max")[["Close"]].reset_index()
precios.columns = ["Fecha", "Precio"]

df = pd.merge(dividendos, precios, on="Fecha", how="left")

df = df.sort_values("Fecha", ascending=False)

# -------------------------
# SCORECARDS (SIN FILTRO)
# -------------------------
precio_actual = data.history(period="1d")["Close"].iloc[-1]
ultimo_pago = df.iloc[0]["Fecha"]
monto_ultimo_pago = df.iloc[0]["Dividendo"]

dividendos_12m = dividendos[
    dividendos["Fecha"] > dividendos["Fecha"].max() - pd.DateOffset(months=12)
]["Dividendo"].sum()

yield_anual = (dividendos_12m / precio_actual) * 100

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
# TRENDLINE DIVIDENDOS
# -------------------------
st.subheader("Histórico de Dividendos")

fig = px.line(
    df_filtrado,
    x="Fecha",
    y="Dividendo",
    markers=True
)

# etiqueta solo ultimo punto
ultima_fecha = df_filtrado["Fecha"].max()
ultimo_valor = df_filtrado[df_filtrado["Fecha"] == ultima_fecha]["Dividendo"].values[0]

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

tabla = df_filtrado.sort_values("Fecha", ascending=False)

tabla["Fecha"] = tabla["Fecha"].dt.strftime("%Y-%m-%d")
tabla["Dividendo"] = tabla["Dividendo"].round(4)
tabla["Precio"] = tabla["Precio"].round(2)

st.dataframe(tabla, use_container_width=True)