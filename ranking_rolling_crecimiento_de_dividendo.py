import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIGURACIÓN
# =============================
FIBRAS = [
    "FUNO11.MX",
    "FMTY14.MX",
    "FIBRAPL14.MX",
    "FIBRAMQ12.MX",
    "FIHO12.MX"
]

START_YEAR = 2023
END_YEAR = 2025

results = []

# =============================
# CÁLCULO
# =============================
for ticker in FIBRAS:
    fib = yf.Ticker(ticker)
    dividends = fib.dividends

    if dividends.empty:
        continue

    df = dividends.reset_index()
    df.columns = ["fecha", "dividendo"]
    df["fecha"] = pd.to_datetime(df["fecha"])

    df = df[
        (df["fecha"].dt.year >= START_YEAR) &
        (df["fecha"].dt.year <= END_YEAR)
    ]

    # Trimestre
    df["quarter"] = df["fecha"].dt.to_period("Q")
    quarterly = df.groupby("quarter")["dividendo"].sum()

    # Rolling 4Q
    rolling_4q = quarterly.rolling(window=4).sum().dropna()

    if len(rolling_4q) < 2:
        continue

    first_val = rolling_4q.iloc[0]
    last_val = rolling_4q.iloc[-1]

    growth_pct = (last_val / first_val - 1) * 100

    results.append({
        "FIBRA": ticker.replace(".MX", ""),
        "Crecimiento Rolling 4Q (%)": growth_pct
    })

# =============================
# DATAFRAME Y ORDEN
# =============================
ranking_df = (
    pd.DataFrame(results)
    .sort_values("Crecimiento Rolling 4Q (%)")
)

# =============================
# GRÁFICO
# =============================
plt.figure(figsize=(10, 6))

plt.barh(
    ranking_df["FIBRA"],
    ranking_df["Crecimiento Rolling 4Q (%)"]
)

plt.axvline(0, linestyle="--", linewidth=1)

plt.xlabel("Crecimiento del ingreso acumulado últimos 4 trimestres (%)")
plt.title(
    "Ranking de crecimiento del ingreso (Rolling 4Q)\n"
    "Comparación de dividendos reales pagados",
    pad=15
)

plt.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.show()
