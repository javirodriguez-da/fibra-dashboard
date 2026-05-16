import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------

st.set_page_config(
    page_title="FIBRA Analytics México",
    layout="wide"
)

st.title("FIBRA Analytics México | Reporte de Dividendos")
st.caption("Fuente de datos: Yahoo Finance | Datos actualizados mediante archivos CSV")


# -----------------------------
# FUNCIONES DE FORMATO
# -----------------------------

def format_money(value):
    try:
        return f"${value:,.2f}"
    except Exception:
        return value


def format_percent(value):
    try:
        return f"{value:.2f}%"
    except Exception:
        return value


def format_date(value):
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d")
    except Exception:
        return value


# -----------------------------
# CARGA DE DATOS
# -----------------------------

@st.cache_data(ttl=3600)
def load_data():
    prices = pd.read_csv(
        "datarankings/precios_fibras.csv",
        parse_dates=["Date"]
    )

    dividends = pd.read_csv(
        "datarankings/dividendos_fibras.csv",
        parse_dates=["Date"]
    )

    ranking = pd.read_csv(
        "datarankings/ranking_fibras.csv",
        parse_dates=["Fecha Precio"]
    )

    return prices, dividends, ranking


try:
    prices_df, dividends_df, ranking_df = load_data()

except FileNotFoundError:
    st.error(
        "No se encontraron los archivos CSV. "
        "Primero ejecuta en terminal: python3 update_data.py"
    )
    st.stop()

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()


# -----------------------------
# VALIDACIÓN DE DATOS
# -----------------------------

required_price_columns = {"Date", "Fibra", "Ticker", "Close"}
required_dividend_columns = {"Date", "Fibra", "Ticker", "Dividendos"}
required_ranking_columns = {
    "Fibra",
    "Ticker",
    "Precio",
    "Fecha Precio",
    "Dividendos 12M",
    "Dividend Yield %"
}

if not required_price_columns.issubset(prices_df.columns):
    st.error("El archivo precios_fibras.csv no tiene las columnas necesarias.")
    st.stop()

if not required_dividend_columns.issubset(dividends_df.columns):
    st.error("El archivo dividendos_fibras.csv no tiene las columnas necesarias.")
    st.stop()

if not required_ranking_columns.issubset(ranking_df.columns):
    st.error("El archivo ranking_fibras.csv no tiene las columnas necesarias.")
    st.stop()


# -----------------------------
# LIMPIEZA DE FECHAS
# -----------------------------

prices_df["Date"] = pd.to_datetime(prices_df["Date"]).dt.normalize()
dividends_df["Date"] = pd.to_datetime(dividends_df["Date"]).dt.normalize()
ranking_df["Fecha Precio"] = pd.to_datetime(ranking_df["Fecha Precio"]).dt.normalize()


# -----------------------------
# MÉTRICAS GENERALES
# -----------------------------

st.subheader("Resumen general")

col1, col2, col3, col4 = st.columns(4)

total_fibras = ranking_df["Fibra"].nunique()
latest_price_date = ranking_df["Fecha Precio"].max().strftime("%Y-%m-%d")
avg_yield = ranking_df["Dividend Yield %"].mean()
max_yield_row = ranking_df.sort_values("Dividend Yield %", ascending=False).iloc[0]

with col1:
    st.metric("FIBRAs analizadas", total_fibras)

with col2:
    st.metric("Fecha último precio", latest_price_date)

with col3:
    st.metric("Yield promedio", f"{avg_yield:.2f}%")

with col4:
    st.metric(
        "Mayor yield 12M",
        f"{max_yield_row['Dividend Yield %']:.2f}%",
        max_yield_row["Fibra"]
    )


# -----------------------------
# RANKING DE DIVIDEND YIELD
# -----------------------------

st.subheader("Ranking Dividend Yield - Últimos 12 meses")

ranking_display = ranking_df.copy()

ranking_display = ranking_display.sort_values(
    "Dividend Yield %",
    ascending=False
).reset_index(drop=True)

ranking_display.index = ranking_display.index + 1
ranking_display.index.name = "Rank"

ranking_display = ranking_display[
    [
        "Fibra",
        "Ticker",
        "Precio",
        "Fecha Precio",
        "Dividendos 12M",
        "Dividend Yield %"
    ]
]

ranking_display["Fecha Precio"] = ranking_display["Fecha Precio"].dt.strftime("%Y-%m-%d")

ranking_display_formatted = ranking_display.copy()
ranking_display_formatted["Precio"] = ranking_display_formatted["Precio"].apply(format_money)
ranking_display_formatted["Dividendos 12M"] = ranking_display_formatted["Dividendos 12M"].apply(format_money)
ranking_display_formatted["Dividend Yield %"] = ranking_display_formatted["Dividend Yield %"].apply(format_percent)

st.dataframe(
    ranking_display_formatted,
    width="stretch"
)

fig_rank = px.bar(
    ranking_display.reset_index(),
    x="Fibra",
    y="Dividend Yield %",
    text="Dividend Yield %",
    title="Ranking Dividend Yield (%) últimos 12 meses"
)

fig_rank.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_rank.update_layout(
    xaxis_title="FIBRA",
    yaxis_title="Dividend Yield (%)",
    uniformtext_minsize=8,
    uniformtext_mode="hide"
)

st.plotly_chart(fig_rank, width="stretch")


# -----------------------------
# PRECIO HISTÓRICO
# -----------------------------

st.subheader("Precio histórico")

fibras_disponibles = sorted(prices_df["Fibra"].dropna().unique())

col1, col2, col3 = st.columns(3)

with col1:
    selected_fibras_price = st.multiselect(
        "Selecciona FIBRAs",
        fibras_disponibles,
        default=fibras_disponibles,
        key="selected_fibras_price"
    )

with col2:
    start_date_price = st.date_input(
        "Fecha inicio",
        value=datetime(2020, 1, 1),
        key="start_date_price"
    )

with col3:
    end_date_price = st.date_input(
        "Fecha fin",
        value=datetime.today(),
        key="end_date_price"
    )

price_filtered = prices_df[
    (prices_df["Fibra"].isin(selected_fibras_price)) &
    (prices_df["Date"] >= pd.Timestamp(start_date_price)) &
    (prices_df["Date"] <= pd.Timestamp(end_date_price))
].copy()

if not price_filtered.empty:

    fig_price = px.line(
        price_filtered,
        x="Date",
        y="Close",
        color="Fibra",
        title=f"Precio histórico ({start_date_price} a {end_date_price})"
    )

    fig_price.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Precio por CBFI ($)"
    )

    fig_price.update_yaxes(
        tickprefix="$",
        tickformat=",.2f"
    )

    st.plotly_chart(fig_price, width="stretch")

else:
    st.warning("No hay datos de precios para el rango seleccionado.")


# -----------------------------
# HISTÓRICO DE DIVIDENDOS
# -----------------------------

st.subheader("Histórico de dividendos por FIBRA")

fibras_dividendos = sorted(dividends_df["Fibra"].dropna().unique())

col1, col2, col3 = st.columns(3)

with col1:
    selected_div_fibra = st.selectbox(
        "Selecciona una FIBRA",
        fibras_dividendos,
        key="selected_div_fibra"
    )

with col2:
    start_date_div = st.date_input(
        "Fecha inicio dividendos",
        value=datetime(2018, 1, 1),
        key="start_date_div"
    )

with col3:
    end_date_div = st.date_input(
        "Fecha fin dividendos",
        value=datetime.today(),
        key="end_date_div"
    )

div_filtered = dividends_df[
    (dividends_df["Fibra"] == selected_div_fibra) &
    (dividends_df["Date"] >= pd.Timestamp(start_date_div)) &
    (dividends_df["Date"] <= pd.Timestamp(end_date_div))
].copy()

if not div_filtered.empty:

    div_filtered = div_filtered.sort_values("Date")

    fig_div = px.line(
        div_filtered,
        x="Date",
        y="Dividendos",
        markers=True,
        title=f"Dividendos históricos - {selected_div_fibra}"
    )

    fig_div.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Dividendo por CBFI ($)"
    )

    fig_div.update_yaxes(
        tickprefix="$",
        tickformat=",.4f"
    )

    st.plotly_chart(fig_div, width="stretch")

    div_table = div_filtered.copy()
    div_table["Date"] = div_table["Date"].dt.strftime("%Y-%m-%d")
    div_table["Dividendos"] = div_table["Dividendos"].apply(format_money)

    st.dataframe(
        div_table.sort_values("Date", ascending=False),
        width="stretch"
    )

else:
    st.warning("No hay dividendos para la FIBRA y rango seleccionado.")


# -----------------------------
# DIVIDENDOS ANUALES
# -----------------------------

st.subheader("Dividendos acumulados por año")

dividends_yearly = dividends_df.copy()
dividends_yearly["Año"] = dividends_yearly["Date"].dt.year

selected_fibras_yearly = st.multiselect(
    "Selecciona FIBRAs para comparar dividendos anuales",
    sorted(dividends_yearly["Fibra"].dropna().unique()),
    default=sorted(dividends_yearly["Fibra"].dropna().unique()),
    key="selected_fibras_yearly"
)

dividends_yearly_filtered = dividends_yearly[
    dividends_yearly["Fibra"].isin(selected_fibras_yearly)
].copy()

yearly_summary = dividends_yearly_filtered.groupby(
    ["Año", "Fibra"],
    as_index=False
)["Dividendos"].sum()

if not yearly_summary.empty:

    fig_yearly = px.bar(
        yearly_summary,
        x="Año",
        y="Dividendos",
        color="Fibra",
        barmode="group",
        title="Dividendos acumulados por año"
    )

    fig_yearly.update_layout(
        xaxis_title="Año",
        yaxis_title="Dividendos acumulados por CBFI ($)"
    )

    fig_yearly.update_yaxes(
        tickprefix="$",
        tickformat=",.2f"
    )

    st.plotly_chart(fig_yearly, width="stretch")

    yearly_table = yearly_summary.copy()
    yearly_table["Dividendos"] = yearly_table["Dividendos"].apply(format_money)

    st.dataframe(
        yearly_table.sort_values(["Año", "Dividendos"], ascending=[False, False]),
        width="stretch"
    )

else:
    st.warning("No hay información suficiente para calcular dividendos anuales.")


# -----------------------------
# TABLA DE DATOS DE PRECIOS
# -----------------------------

with st.expander("Ver tabla de precios históricos"):

    price_table = price_filtered.copy()

    if not price_table.empty:
        price_table["Date"] = price_table["Date"].dt.strftime("%Y-%m-%d")

        money_columns = ["Open", "High", "Low", "Close"]

        for col in money_columns:
            if col in price_table.columns:
                price_table[col] = price_table[col].apply(format_money)

        st.dataframe(
            price_table.sort_values("Date", ascending=False),
            width="stretch"
        )
    else:
        st.warning("No hay datos de precios para mostrar.")


# -----------------------------
# NOTA FINAL
# -----------------------------

st.caption(
    "Este dashboard es informativo y no representa una recomendación de inversión. "
    "Los datos pueden depender de la disponibilidad y calidad de Yahoo Finance."
)