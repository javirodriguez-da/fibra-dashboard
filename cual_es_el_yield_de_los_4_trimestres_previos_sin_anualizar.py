import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIGURACIÓN
# =============================
FIBRAS = [
    "FUNO11.MX",
    "FMTY14.MX",
    "FNOVA17.MX"
]

START_YEAR = 2023
END_YEAR = 2025

# =============================
# PROCESO
# =============================
for ticker in FIBRAS:
    fib = yf.Ticker(ticker)

    # -------------------------
    # DIVIDENDOS
    # -------------------------
    dividends = fib.dividends
    prices = fib.history(
        start=f"{START_YEAR}-01-01",
        end=f"{END_YEAR}-12-31"
    )["Close"]

    if dividends.empty or prices.empty:
        continue

    df_div = dividends.reset_index()
    df_div.columns = ["fecha", "dividendo"]
    df_div["fecha"] = pd.to_datetime(df_div["fecha"])

    df_div = df_div[
        (df_div["fecha"].dt.year >= START_YEAR) &
        (df_div["fecha"].dt.year <= END_YEAR)
    ]

    # Trimestre
    df_div["quarter"] = df_div["fecha"].dt.to_period("Q")

    # Dividendo trimestral
    quarterly_div = df_div.groupby("quarter")["dividendo"].sum()

    # -------------------------
    # PRECIOS PROMEDIO TRIMESTRALES
    # -------------------------
    prices_q = prices.resample("QE").mean()
    prices_q.index = prices_q.index.to_period("Q")

    # -------------------------
    # ALINEAR PERIODOS
    # -------------------------
    common = quarterly_div.index.intersection(prices_q.index)

    quarterly_div = quarterly_div.loc[common]
    prices_q = prices_q.loc[common]

    # -------------------------
    # ROLLING 4Q
    # -------------------------
    rolling_div_4q = quarterly_div.rolling(4).sum()
    rolling_price_4q = prices_q.rolling(4).mean()

    rolling_yield_4q = (rolling_div_4q / rolling_price_4q) * 100

    # Eliminar NaN iniciales
    rolling_yield_4q = rolling_yield_4q.dropna()

    # =============================
    # GRÁFICO INDIVIDUAL
    # =============================
    plt.figure(figsize=(10, 5))

    plt.plot(
        rolling_yield_4q.index.astype(str),
        rolling_yield_4q.values,
        marker="o",
        linewidth=2
    )

    # -------------------------
    # ETIQUETAS EN CADA PUNTO
    # -------------------------
    for x, y in zip(
        rolling_yield_4q.index.astype(str),
        rolling_yield_4q.values
    ):
        plt.text(
            x,
            y,
            f"{y:.2f}%",
            fontsize=9,
            ha="center",
            va="bottom"
        )

    # -------------------------
    # FORMATO
    # -------------------------
    plt.title(
        f"{ticker.replace('.MX', '')} | Yield rolling últimos 4 trimestres\n"
        "Dividendos acumulados / precio promedio (sin anualizar)",
        pad=15
    )

    plt.xlabel("Trimestre")
    plt.ylabel("Yield rolling 4Q (%)")
    plt.grid(alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
