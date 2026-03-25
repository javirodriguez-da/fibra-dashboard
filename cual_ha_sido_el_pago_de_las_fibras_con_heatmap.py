import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
END_YEAR = 2026   # puedes moverlo libremente

# =============================
# DESCARGA Y PROCESO
# =============================
heatmap_data = {}

for ticker in FIBRAS:
    print(f"Procesando {ticker}...")
    fib = yf.Ticker(ticker)
    div = fib.dividends

    if div.empty:
        continue

    df = div.reset_index()
    df.columns = ["fecha", "dividendo"]
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Filtrar años
    df = df[
        (df["fecha"].dt.year >= START_YEAR) &
        (df["fecha"].dt.year <= END_YEAR)
    ]

    # Año y trimestre
    df["year"] = df["fecha"].dt.year
    df["quarter"] = df["fecha"].dt.to_period("Q").astype(str)

    # Sumar dividendos trimestrales
    quarterly = (
        df.groupby("quarter")["dividendo"]
        .sum()
        .round(4)
    )

    heatmap_data[ticker.replace(".MX", "")] = quarterly

# =============================
# DATAFRAME FINAL
# =============================
heatmap_df = pd.DataFrame(heatmap_data).T
heatmap_df = heatmap_df.sort_index(axis=1)

# =============================
# GRAFICADO
# =============================
plt.figure(figsize=(18, 6))

sns.heatmap(
    heatmap_df,
    annot=True,
    fmt=".2f",
    cmap="YlGn",
    linewidths=0.5,
    linecolor="gray",
    cbar_kws={"label": "Dividendo trimestral ($)"}
)

plt.title(
    "Heatmap de Dividendos Trimestrales por FIBRA\n(Ingresos pasivos reales)",
    fontsize=14,
    pad=15
)

plt.xlabel("Trimestre")
plt.ylabel("FIBRA")

plt.tight_layout()
plt.show()
