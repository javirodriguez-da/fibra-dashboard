import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIGURACIÓN
# =============================
FIBRAS = [
   ##"FUNO11.MX",
    ##"FMTY14.MX",
    ##"FNOVA17.MX",
    ##"DANHOS13.MX",
    ##"FIBRAMQ12.MX",
    "FSHOP13.MX",
    ##"NEXT25.MX",
    ##"FINN13.MX"
]

START_YEAR = 2022
END_YEAR = 2025

# =============================
# PROCESO
# =============================
plt.figure(figsize=(12, 6))

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

    # Dividendo trimestral (mensual se suma automáticamente)
    quarterly = df.groupby("quarter")["dividendo"].sum()

    # Rolling 4Q (últimos 4 trimestres)
    rolling_4q = quarterly.rolling(window=4).sum()

    plt.plot(
        rolling_4q.index.astype(str),
        rolling_4q.values,
        marker="o",
        label=ticker.replace(".MX", "")
    )

# =============================
# FORMATO
# =============================
plt.title(
    "Dividendos acumulados últimos 4 trimestres (Rolling 4Q)\n"
    "Ingreso real sin anualizar",
    pad=15
)

plt.xlabel("Trimestre")
plt.ylabel("Dividendo acumulado (MXN)")
plt.grid(alpha=0.3)
plt.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
