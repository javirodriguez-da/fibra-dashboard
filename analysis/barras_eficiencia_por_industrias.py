import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIGURACIÓN
# =============================
FIBRAS = [
    "FUNO11.MX",
    "FMTY14.MX",
    "FNOVA17.MX",
    "FIBRAMQ12.MX",
    "FSHOP13.MX",
    "DANHOS13.MX",
    "FINN13.MX",
    "NEXT25.MX",
    "FSTAY12.MX"
]

INDUSTRIAS = {
    "FUNO11.MX": "Retail",
    "FSHOP13.MX": "Retail",
    "DANHOS13.MX": "Retail",
    "FMTY14.MX": "Industria",
    "FNOVA17.MX": "Industria",
    "FIBRAMQ12.MX": "Industria",
    "FINN13.MX": "Hospitalidad",
    "NEXT25.MX": "Oficinas",
    "FSTAY12.MX": "Hospitalidad"
}

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

    # Dividendos trimestrales
    df_div = dividends.reset_index()
    df_div.columns = ["fecha", "dividendo"]
    df_div["fecha"] = pd.to_datetime(df_div["fecha"])
    df_div["quarter"] = df_div["fecha"].dt.to_period("Q")

    quarterly_div = df_div.groupby("quarter")["dividendo"].sum()

    # Precio promedio trimestral
    prices_q = prices.resample("QE").mean()
    prices_q.index = prices_q.index.to_period("Q")

    common = quarterly_div.index.intersection(prices_q.index)
    quarterly_div = quarterly_div.loc[common]
    prices_q = prices_q.loc[common]

    # Rolling 4Q
    rolling_div_4q = quarterly_div.rolling(4).sum()
    rolling_price_4q = prices_q.rolling(4).mean()

    rolling_yield_4q = (rolling_div_4q / rolling_price_4q) * 100
    rolling_yield_4q = rolling_yield_4q.dropna()

    for q, y in rolling_yield_4q.items():
        rows.append({
            "Industria": INDUSTRIAS.get(ticker, "Otro"),
            "Yield_4Q": y
        })

# =============================
# DATAFRAME FINAL
# =============================
df = pd.DataFrame(rows)

# =============================
# BOXPLOT
# =============================
plt.figure(figsize=(9, 5))

df.boxplot(
    column="Yield_4Q",
    by="Industria",
    grid=False
)

plt.title(
    "Distribución del yield rolling 4Q por industria\n"
    "Ingreso real sin anualizar",
    pad=15
)

plt.suptitle("")
plt.xlabel("Industria")
plt.ylabel("Yield rolling 4Q (%)")

plt.tight_layout()
plt.show()
