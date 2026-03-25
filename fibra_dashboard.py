import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

st.title("FIBRA Analytics México | Fuente: Yahoo Finance")

# -----------------------------
# FUNCION LIMPIAR FECHAS
# -----------------------------

def clean_dates(series):
    if series.index.tz is not None:
        series.index = series.index.tz_localize(None)
    return series

# -----------------------------
# FIBRAs
# -----------------------------

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

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.header("Filtros")

selected_fibras = st.sidebar.multiselect(
    "Selecciona FIBRAs",
    list(fibras.keys()),
    default=list(fibras.keys()),
    key="sidebar_fibras"
)

start_date = st.sidebar.date_input(
    "Fecha inicio",
    datetime(2020,1,1),
    key="sidebar_start"
)

end_date = st.sidebar.date_input(
    "Fecha fin",
    datetime.today(),
    key="sidebar_end"
)

# -----------------------------
# DATA
# -----------------------------

summary_data = []
price_history = []

for name in selected_fibras:

    ticker = fibras[name]
    stock = yf.Ticker(ticker)

    hist = stock.history(start=start_date, end=end_date)

    if hist.empty:
        continue

    price = hist["Close"].iloc[-1]

    dividends = clean_dates(stock.dividends)
    dividends_12m = dividends.last("365D").sum()

    yield_pct = (dividends_12m / price) * 100 if price > 0 else 0

    period_label = f"{end_date - pd.Timedelta(days=365)} → {end_date}"

    summary_data.append({
        "Fibra": name,
        "Precio": round(price,2),
        "Dividendos 12M": round(dividends_12m,2),
        "Dividend Yield %": round(yield_pct,2),
        
    })

    hist["Fibra"] = name
    price_history.append(hist.reset_index())

summary_df = pd.DataFrame(summary_data)

# -----------------------------
# RANKING
# -----------------------------

summary_df = summary_df.sort_values(
    "Dividend Yield %",
    ascending=False
).reset_index(drop=True)

summary_df.index = summary_df.index + 1
summary_df.index.name = "Rank"

summary_df = summary_df[
    ["Fibra", "Precio", "Dividendos 12M", "Dividend Yield %"]
]

st.subheader("Ranking Dividend Yield - Últimos 12 meses")

st.dataframe(summary_df, use_container_width=True)

# -----------------------------
# GRAFICO RANKING
# -----------------------------

fig_rank = px.bar(
    summary_df.reset_index(),
    x="Fibra",
    y="Dividend Yield %",
    text="Dividend Yield %",
    title="Ranking Dividend Yield (%)",
    subtitle=f"Periodo: Últimos 12 meses"
)

fig_rank.update_traces(texttemplate='%{text:.2f}%', textposition="outside")

st.plotly_chart(fig_rank, use_container_width=True)

# -----------------------------
# PRECIO HISTORICO
# -----------------------------

if price_history:

    price_df = pd.concat(price_history)

    st.subheader("Precio histórico")

    fig_price = px.line(
        price_df,
        x="Date",
        y="Close",
        color="Fibra",
        title="Precio histórico"
    )

    st.plotly_chart(fig_price, use_container_width=True)

# -----------------------------
# PANEL DIVIDENDOS (FINAL)
# -----------------------------

st.subheader("Histórico de Dividendos por FIBRA")

col1, col2, col3 = st.columns(3)

with col1:
    div_fibra = st.selectbox(
        "Selecciona una FIBRA",
        list(fibras.keys()),
        key="div_selector_unique"
    )

with col2:
    div_start = st.date_input(
        "Fecha inicio",
        datetime(2018,1,1),
        key="div_start_unique"
    )

with col3:
    div_end = st.date_input(
        "Fecha fin",
        datetime.today(),
        key="div_end_unique"
    )

# -----------------------------
# DATA DIVIDENDOS
# -----------------------------

ticker = fibras[div_fibra]
stock = yf.Ticker(ticker)

div = clean_dates(stock.dividends)

div = div[
    (div.index >= pd.Timestamp(div_start)) &
    (div.index <= pd.Timestamp(div_end))
]

if not div.empty:

    div_df = div.reset_index()
    div_df.columns = ["Date", "Dividendos"]

    fig_div = px.line(
        div_df,
        x="Date",
        y="Dividendos",
        markers=True,
        title=f"Dividendos - {div_fibra}"
    )

    st.plotly_chart(fig_div, use_container_width=True)

else:
    st.warning("No hay datos de dividendos en el rango seleccionado.")