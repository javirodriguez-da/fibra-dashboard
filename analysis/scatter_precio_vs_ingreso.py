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

data = []

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
    # PRECIOS TRIMESTRALES PROMEDIO
    # -------------------------
    prices_q = prices.resample("QE").mean()
    prices_q.index = prices_q.index.to_period("Q")

    # Alinear periodos
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

    # Tomamos el último dato disponible
    data.append({
        "Fibra": ticker.replace(".MX", ""),
        "Precio_4Q": rolling_price_4q.iloc[-1],
        "Yield_4Q": rolling_yield_4q.iloc[-1]
    })

# =============================
# DATAFRAME
# =============================
df = pd.DataFrame(data)

# Promedios para cuadrantes
x_mean = df["Precio_4Q"].mean()
y_mean = df["Yield_4Q"].mean()

# =============================
# SCATTER
# =============================
plt.figure(figsize=(10, 6))

plt.scatter(
    df["Precio_4Q"],
    df["Yield_4Q"],
    s=120
)

# Etiquetas
for _, row in df.iterrows():
    plt.text(
        row["Precio_4Q"],
        row["Yield_4Q"],
        row["Fibra"],
        fontsize=9,
        ha="center",
        va="bottom"
    )

# Líneas promedio (cuadrantes)
plt.axvline(x=x_mean, linestyle="--", alpha=0.5)
plt.axhline(y=y_mean, linestyle="--", alpha=0.5)

# =============================
# FORMATO
# =============================
plt.title(
    "Precio vs Ingreso real (Yield rolling 4Q)\n"
    "Cada punto representa una FIBRA",
    pad=15
)

plt.xlabel("Precio promedio rolling 4Q (MXN)")
plt.ylabel("Yield rolling 4Q (%)")

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
