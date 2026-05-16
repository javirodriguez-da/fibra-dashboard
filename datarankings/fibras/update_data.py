import time
from datetime import timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf


# -----------------------------
# CONFIGURACIÓN
# -----------------------------

DATA_DIR = Path("datarankings")
DATA_DIR.mkdir(parents=True, exist_ok=True)

FIBRAS = {
    "Fibra Monterrey": "FMTY14.MX",
    "Fibra Uno": "FUNO11.MX",
    "Fibra Macquarie": "FIBRAMQ12.MX",
    "Fibra CFE": "FCFE18.MX",
    "Fibra Danhos": "DANHOS13.MX",
    "Fibra Shop": "FSHOP13.MX",
    "Prologis Fibra": "FIBRAPL14.MX",
    "Fibra Inn": "FINN13.MX",
    "Fibra Next": "NEXT25.MX",
}


# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------

def clean_index_dates(df_or_series):
    """
    Elimina zona horaria del índice de fechas para evitar errores
    entre datetime con timezone y sin timezone.
    """
    if df_or_series.empty:
        return df_or_series

    if getattr(df_or_series.index, "tz", None) is not None:
        df_or_series.index = df_or_series.index.tz_localize(None)

    return df_or_series


def get_price_history(name, ticker):
    """
    Descarga el histórico completo de precios de una FIBRA.
    """
    stock = yf.Ticker(ticker)

    hist = stock.history(period="max", auto_adjust=False)

    if hist.empty:
        print(f"Sin precios para {name} ({ticker})")
        return pd.DataFrame()

    hist = clean_index_dates(hist)
    hist = hist.reset_index()

    hist["Fibra"] = name
    hist["Ticker"] = ticker

    columns = [
        "Date",
        "Fibra",
        "Ticker",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    available_columns = [col for col in columns if col in hist.columns]

    return hist[available_columns]


def get_dividends(name, ticker):
    """
    Descarga el histórico de dividendos de una FIBRA.
    """
    stock = yf.Ticker(ticker)

    dividends = stock.dividends

    if dividends.empty:
        print(f"Sin dividendos para {name} ({ticker})")
        return pd.DataFrame(columns=["Date", "Fibra", "Ticker", "Dividendos"])

    dividends = clean_index_dates(dividends)

    div_df = dividends.reset_index()
    div_df.columns = ["Date", "Dividendos"]

    div_df["Fibra"] = name
    div_df["Ticker"] = ticker

    return div_df[["Date", "Fibra", "Ticker", "Dividendos"]]


def create_ranking(prices_df, dividends_df):
    """
    Crea ranking de Dividend Yield usando:
    - Precio más reciente disponible
    - Dividendos pagados en los últimos 12 meses
    """
    ranking_data = []

    prices_df["Date"] = pd.to_datetime(prices_df["Date"])
    dividends_df["Date"] = pd.to_datetime(dividends_df["Date"])

    for name, ticker in FIBRAS.items():
        try:
            fibra_prices = prices_df[prices_df["Ticker"] == ticker].copy()
            fibra_dividends = dividends_df[dividends_df["Ticker"] == ticker].copy()

            if fibra_prices.empty:
                print(f"No hay precios para ranking de {name}")
                continue

            fibra_prices = fibra_prices.sort_values("Date")

            latest_row = fibra_prices.iloc[-1]
            latest_price = latest_row["Close"]
            latest_date = latest_row["Date"]

            last_year = latest_date - timedelta(days=365)

            dividends_12m = fibra_dividends[
                fibra_dividends["Date"] >= last_year
            ]["Dividendos"].sum()

            dividend_yield = (
                (dividends_12m / latest_price) * 100
                if latest_price and latest_price > 0
                else 0
            )

            ranking_data.append(
                {
                    "Fibra": name,
                    "Ticker": ticker,
                    "Precio": round(latest_price, 2),
                    "Fecha Precio": latest_date.date(),
                    "Dividendos 12M": round(dividends_12m, 4),
                    "Dividend Yield %": round(dividend_yield, 2),
                }
            )

        except Exception as e:
            print(f"Error creando ranking para {name} ({ticker}): {e}")

    ranking_df = pd.DataFrame(ranking_data)

    if not ranking_df.empty:
        ranking_df = ranking_df.sort_values(
            "Dividend Yield %",
            ascending=False
        ).reset_index(drop=True)

    return ranking_df


# -----------------------------
# PROCESO PRINCIPAL
# -----------------------------

def main():
    all_prices = []
    all_dividends = []

    print("Iniciando actualización de datos de FIBRAs...")
    print("-" * 50)

    for name, ticker in FIBRAS.items():
        print(f"Descargando {name} ({ticker})...")

        try:
            price_df = get_price_history(name, ticker)

            if not price_df.empty:
                all_prices.append(price_df)

            time.sleep(1)

            dividends_df = get_dividends(name, ticker)

            if not dividends_df.empty:
                all_dividends.append(dividends_df)

            time.sleep(1)

        except Exception as e:
            print(f"Error general con {name} ({ticker}): {e}")

    print("-" * 50)

    # -----------------------------
    # GUARDAR PRECIOS
    # -----------------------------

    if all_prices:
        prices_final = pd.concat(all_prices, ignore_index=True)

        prices_final["Date"] = pd.to_datetime(prices_final["Date"]).dt.date

        prices_path = DATA_DIR / "precios_fibras.csv"
        prices_final.to_csv(prices_path, index=False)

        print(f"Archivo creado: {prices_path}")
    else:
        prices_final = pd.DataFrame(
            columns=[
                "Date",
                "Fibra",
                "Ticker",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
        )

        prices_path = DATA_DIR / "precios_fibras.csv"
        prices_final.to_csv(prices_path, index=False)

        print(f"Archivo vacío creado: {prices_path}")

    # -----------------------------
    # GUARDAR DIVIDENDOS
    # -----------------------------

    if all_dividends:
        dividends_final = pd.concat(all_dividends, ignore_index=True)

        dividends_final["Date"] = pd.to_datetime(dividends_final["Date"]).dt.date

        dividends_path = DATA_DIR / "dividendos_fibras.csv"
        dividends_final.to_csv(dividends_path, index=False)

        print(f"Archivo creado: {dividends_path}")
    else:
        dividends_final = pd.DataFrame(
            columns=["Date", "Fibra", "Ticker", "Dividendos"]
        )

        dividends_path = DATA_DIR / "dividendos_fibras.csv"
        dividends_final.to_csv(dividends_path, index=False)

        print(f"Archivo vacío creado: {dividends_path}")

    # -----------------------------
    # GUARDAR RANKING
    # -----------------------------

    if not prices_final.empty:
        ranking_df = create_ranking(prices_final.copy(), dividends_final.copy())

        ranking_path = DATA_DIR / "ranking_fibras.csv"
        ranking_df.to_csv(ranking_path, index=False)

        print(f"Archivo creado: {ranking_path}")
    else:
        ranking_df = pd.DataFrame(
            columns=[
                "Fibra",
                "Ticker",
                "Precio",
                "Fecha Precio",
                "Dividendos 12M",
                "Dividend Yield %",
            ]
        )

        ranking_path = DATA_DIR / "ranking_fibras.csv"
        ranking_df.to_csv(ranking_path, index=False)

        print(f"Archivo vacío creado: {ranking_path}")

    print("-" * 50)
    print("Actualización finalizada correctamente.")


if __name__ == "__main__":
    main()