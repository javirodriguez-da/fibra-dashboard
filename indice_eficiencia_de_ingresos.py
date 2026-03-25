import yfinance as yf
import pandas as pd
import numpy as np

# =============================
# CONFIGURACIÓN
# =============================
FIBRAS = [
    "FUNO11.MX",
    "FMTY14.MX",
    "FNOVA17.MX"
]

START_YEAR = 2022
END_YEAR = 2025

rows = []

# =============================
# PROCESO
# =============================
for ticker in FIBRAS:
    fib = yf.Ticker(ticker)

    dividends = fib.dividends
    prices = fib.history(
        start=f"{START_YEAR}-01-01",
        end=f"{END_YEAR}-12-31"
    )["Close"]

    if dividends.empty or prices.empty:
        continue

    # -------------------------
    # DIVIDENDOS TRIMESTRALES
    # -------------------------
    df_div = dividends.reset_index()
    df_div.columns = ["fecha", "dividendo"]
    df_div["fecha"] = pd.to_datetime(df_div["fecha"])
    df_div["quarter"] = df_div["fecha"].dt.to_period("Q")

    quarterly_div = df_div.groupby("quarter")["dividendo"].sum()

    # -------------------------
    # PRECIOS PROMEDIO TRIMESTRALES
    # -------------------------
    prices_q = prices.resample("QE").mean()
    prices_q.index = prices_q.index.to_period("Q")

    common = quarterly_div.index.intersection(prices_q.index)
    quarterly_div = quarterly_div.loc[common]
    prices_q = prices_q.loc[common]

    # -------------------------
    # ROLLING 4Q
    # -------------------------
    rolling_div_4q = quarterly_div.rolling(4).sum()
    rolling_price_4q = prices_q.rolling(4).mean()

    rolling_yield_4q = (rolling_div_4q / rolling_price_4q) * 100
    rolling_yield_4q = rolling_yield_4q.dropna()
    rolling_price_4q = rolling_price_4q.loc[rolling_yield_4q.index]

    if rolling_yield_4q.empty:
        continue

    # -------------------------
    # MÉTRICAS FINALES
    # -------------------------
    yield_4q = rolling_yield_4q.iloc[-1]
    price_4q = rolling_price_4q.iloc[-1]

    consistency = quarterly_div.std() / quarterly_div.mean()
    consistency_factor = 1 / (1 + consistency)

    efficiency_index = (yield_4q / price_4q) * consistency_factor

    rows.append({
        "Fibra": ticker.replace(".MX", ""),
        "Yield_4Q_%": yield_4q,
        "Precio_4Q": price_4q,
        "Consistencia": consistency,
        "Indice_Eficiencia": efficiency_index
    })

# =============================
# RESULTADO
# =============================
df = pd.DataFrame(rows).set_index("Fibra")

# Normalizar índice a base 100 para comunicación
df["Indice_Eficiencia_100"] = (
    df["Indice_Eficiencia"] / df["Indice_Eficiencia"].max()
) * 100

df = df.sort_values("Indice_Eficiencia_100", ascending=False)

print(df.round(3))
