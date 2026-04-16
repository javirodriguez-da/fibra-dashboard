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
    "DANHOS13.MX",
    "FIBRAMQ12.MX",
    "FSHOP13.MX",
    "NEXT25.MX",
    "FINN13.MX"
]

START_YEAR = 2023
END_YEAR = 2026

# =============================
# CÁLCULO
# =============================
results = []

for ticker in FIBRAS:
    print(f"Procesando {ticker}...")
    fib = yf.Ticker(ticker)

    dividends = fib.dividends
    prices = fib.history(
        start=f"{START_YEAR}-01-01",
        end=f"{END_YEAR}-12-31"
    )["Close"]

    if dividends.empty or prices.empty:
        continue

    # -------------------------
    # DIVIDENDOS
    # -------------------------
    df_div = dividends.reset_index()
    df_div.columns = ["fecha", "dividendo"]
    df_div["fecha"] = pd.to_datetime(df_div["fecha"])

    df_div = df_div[
        (df_div["fecha"].dt.year >= START_YEAR) &
        (df_div["fecha"].dt.year <= END_YEAR)
    ]

    df_div["quarter"] = df_div["fecha"].dt.to_period("Q")
    quarterly_div = df_div.groupby("quarter")["dividendo"].sum()

    # -------------------------
    # PRECIOS TRIMESTRALES
    # -------------------------
    prices_q = prices.resample("QE").mean()
    prices_q.index = prices_q.index.to_period("Q")

    # -------------------------
    # YIELD TRIMESTRAL
    # -------------------------
    common = quarterly_div.index.intersection(prices_q.index)

    yield_q = (quarterly_div.loc[common] / prices_q.loc[common]) * 100

    results.append({
        "FIBRA": ticker.replace(".MX", ""),
        "Yield Promedio (%)": yield_q.mean(), # Anualizado
        "Volatilidad Yield (%)": yield_q.std()
    })

# =============================
# DATAFRAME FINAL
# =============================
scatter_df = pd.DataFrame(results)

# =============================
# SCATTER PLOT
# =============================
plt.figure(figsize=(10, 7))

plt.scatter(
    scatter_df["Yield Promedio (%)"],
    scatter_df["Volatilidad Yield (%)"],
    s=120,
    alpha=0.85
)

# Etiquetas
for _, row in scatter_df.iterrows():
    plt.text(
        row["Yield Promedio (%)"] + 0.05,
        row["Volatilidad Yield (%)"],
        row["FIBRA"],
        fontsize=9
    )

# Líneas de referencia (medianas)
plt.axhline(
    scatter_df["Volatilidad Yield (%)"].median(),
    linestyle="--",
    linewidth=1,
    alpha=0.6
)

plt.axvline(
    scatter_df["Yield Promedio (%)"].median(),
    linestyle="--",
    linewidth=1,
    alpha=0.6
)

plt.xlabel("Yield promedio por Trimestre (%)")
plt.ylabel("Volatilidad del yield (%)")
plt.title(
    "Yield vs Consistencia\nAnálisis de Ingresos Pasivos (FIBRAS)",
    pad=15
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
