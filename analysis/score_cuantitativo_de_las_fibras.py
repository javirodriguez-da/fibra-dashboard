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

scores = []

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
    # PRECIOS TRIMESTRALES
    # -------------------------
    prices_q = prices.resample("QE").mean()
    prices_q.index = prices_q.index.to_period("Q")

    common = quarterly_div.index.intersection(prices_q.index)
    quarterly_div = quarterly_div.loc[common]
    prices_q = prices_q.loc[common]

    # -------------------------
    # ROLLING 4Q
    # -------------------------
    rolling_div = quarterly_div.rolling(4).sum()
    rolling_price = prices_q.rolling(4).mean()

    rolling_yield = (rolling_div / rolling_price) * 100
    rolling_yield = rolling_yield.dropna()

    # -------------------------
    # MÉTRICAS
    # -------------------------
    current_yield = rolling_yield.iloc[-1]

    growth = (
        (rolling_div.iloc[-1] / rolling_div.iloc[-5]) - 1
        if len(rolling_div.dropna()) >= 5
        else np.nan
    )

    consistency = quarterly_div.std() / quarterly_div.mean()

    price_vol = prices_q.pct_change().std()

    scores.append({
        "Fibra": ticker.replace(".MX", ""),
        "Yield_4Q": current_yield,
        "Growth_4Q": growth,
        "Consistency": consistency,
        "Price_Vol": price_vol
    })

# =============================
# DATAFRAME
# =============================
df = pd.DataFrame(scores).set_index("Fibra")

# -------------------------
# NORMALIZACIÓN (0–100)
# -------------------------
df_norm = pd.DataFrame(index=df.index)

df_norm["Yield"] = (df["Yield_4Q"] / df["Yield_4Q"].max()) * 100
df_norm["Growth"] = ((df["Growth_4Q"] - df["Growth_4Q"].min()) /
                      (df["Growth_4Q"].max() - df["Growth_4Q"].min())) * 100

df_norm["Consistency"] = (1 - (df["Consistency"] / df["Consistency"].max())) * 100
df_norm["Price_Stability"] = (1 - (df["Price_Vol"] / df["Price_Vol"].max())) * 100

# -------------------------
# SCORE FINAL
# -------------------------
df_norm["Score_Final"] = (
    df_norm["Yield"] * 0.35 +
    df_norm["Growth"] * 0.25 +
    df_norm["Consistency"] * 0.20 +
    df_norm["Price_Stability"] * 0.20
)

df_norm = df_norm.sort_values("Score_Final", ascending=False)

print(df_norm.round(2))
