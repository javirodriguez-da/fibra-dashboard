import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("FIBRA Analytics México | Fuente: Yahoo Finance")

# -----------------------------
# FUNCION LIMPIAR FECHAS
# -----------------------------

def clean_dates(series):
    if not series.empty:
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
# DATA RANKING (PRECIO ACTUAL)
# -----------------------------

summary_data = []
price_date = datetime.today().date()

for name in fibras:

    ticker = fibras[name]
    stock = yf.Ticker(ticker)

    try:

        hist = stock.history(period="5d")

        if hist.empty:
            continue

        price = hist["Close"].iloc[-1]
        price_date = hist.index[-1].date()

        dividends = clean_dates(stock.dividends)

        last_year = pd.Timestamp(price_date) - timedelta(days=365)
        dividends_12m = dividends[dividends.index >= last_year].sum()

        yield_pct = (dividends_12m / price) * 100 if price > 0 else 0

        summary_data.append({
            "Fibra": name,
            "Precio": round(price,2),
            "Dividendos 12M": round(dividends_12m,2),
            "Dividend Yield %": round(yield_pct,2)
        })

    except:
        continue

summary_df = pd.DataFrame(summary_data)

# -----------------------------
# RANKING
# -----------------------------

if not summary_df.empty:

    summary_df = summary_df.sort_values(
        "Dividend Yield %",
        ascending=False
    ).reset_index(drop=True)

    summary_df.index = summary_df.index + 1
    summary_df.index.name = "Rank"

    summary_df = summary_df[
        ["Fibra", "Precio", "Dividendos 12M", "Dividend Yield %"]
    ]

    st.subheader(
        f"Ranking Dividend Yield - Últimos 12 meses (Precio al {price_date})"
    )

    st.dataframe(summary_df, use_container_width=True)

    fig_rank = px.bar(
        summary_df.reset_index(),
        x="Fibra",
        y="Dividend Yield %",
        text="Dividend Yield %",
        title="Ranking Dividend Yield (%)"
    )

    fig_rank.update_traces(
        texttemplate='%{text:.2f}%',
        textposition="outside"
    )

    st.plotly_chart(fig_rank, use_container_width=True)

else:
    st.warning("No hay datos disponibles")


# -----------------------------
# PRECIO HISTORICO
# -----------------------------

st.subheader("Precio histórico")

col1, col2, col3 = st.columns(3)

with col1:
    selected_fibras_price = st.multiselect(
        "Selecciona FIBRAs",
        list(fibras.keys()),
        default=list(fibras.keys())
    )

with col2:
    start_date = st.date_input(
        "Fecha inicio",
        datetime(2020,1,1)
    )

with col3:
    end_date = st.date_input(
        "Fecha fin",
        datetime.today()
    )

price_history = []

for name in selected_fibras_price:

    ticker = fibras[name]
    stock = yf.Ticker(ticker)

    try:

        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            continue

        hist["Fibra"] = name
        price_history.append(hist.reset_index())

    except:
        continue

if price_history:

    price_df = pd.concat(price_history)

    fig_price = px.line(
        price_df,
        x="Date",
        y="Close",
        color="Fibra",
        title=f"Precio histórico ({start_date} → {end_date})"
    )

    st.plotly_chart(fig_price, use_container_width=True)

else:
    st.warning("No hay datos de precios en el rango seleccionado")


# -----------------------------
# PANEL DIVIDENDOS
# -----------------------------

st.subheader("Histórico de Dividendos por FIBRA")

col1, col2, col3 = st.columns(3)

with col1:
    div_fibra = st.selectbox(
        "Selecciona una FIBRA",
        list(fibras.keys())
    )

with col2:
    div_start = st.date_input(
        "Fecha inicio dividendos",
        datetime(2018,1,1)
    )

with col3:
    div_end = st.date_input(
        "Fecha fin dividendos",
        datetime.today()
    )

ticker = fibras[div_fibra]
stock = yf.Ticker(ticker)

try:

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

except:
    st.warning("No se pudieron cargar los dividendos")