import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# CONFIGURACIÓN
# =========================

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

YEARS_HISTORY = 3

# =========================
# PROCESO
# =========================

resultados = []

for ticker in FIBRAS:

    fib = yf.Ticker(ticker)

    dividends = fib.dividends
    prices = fib.history(period="4y")["Close"]

    if dividends.empty or prices.empty:
        continue

    # -------------------------
    # DIVIDENDOS
    # -------------------------

    df_div = dividends.reset_index()
    df_div.columns = ["fecha", "dividendo"]
    df_div["fecha"] = pd.to_datetime(df_div["fecha"])

    df_div["quarter"] = df_div["fecha"].dt.to_period("QE")

    dividends_q = df_div.groupby("quarter")["dividendo"].sum()

    # -------------------------
    # PRECIOS
    # -------------------------

    prices_q = prices.resample("QE").mean()

    # -------------------------
    # DATAFRAME FINAL
    # -------------------------

    df = pd.DataFrame({
        "dividendo": dividends_q,
        "precio_prom": prices_q
    }).dropna()

    if len(df) < 6:
        continue

    # trimestre actual
    actual = df.iloc[-1]

    # promedio histórico últimos 3 años (~12 trimestres)
    promedio_hist = df.iloc[-(YEARS_HISTORY*4):-1]["dividendo"].mean()

    yield_trimestre = actual["dividendo"] / actual["precio_prom"]

    resultados.append({
        "fibra": ticker.replace(".MX",""),
        "dividendo": actual["dividendo"],
        "yield": yield_trimestre,
        "precio": actual["precio_prom"],
        "promedio_hist": promedio_hist
    })

# =========================
# DATAFRAME
# =========================

df_rank = pd.DataFrame(resultados)

df_rank = df_rank.sort_values(
    "dividendo",
    ascending=False
)

# =========================
# GRÁFICA
# =========================

plt.figure(figsize=(11,6))

bars = plt.bar(
    df_rank["fibra"],
    df_rank["dividendo"]
)

# aumentar eje Y para etiquetas
plt.ylim(0, df_rank["dividendo"].max()*1.35)

# =========================
# ETIQUETAS
# =========================

for i,row in df_rank.iterrows():

    etiqueta = (
        f"${row['dividendo']:.2f} | "
        f"{row['yield']:.2%} yield | "
        f"Prom 3y: ${row['promedio_hist']:.2f}"
    )

    plt.text(
        df_rank.index.get_loc(i),
        row["dividendo"]*1.05,
        etiqueta,
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

# =========================
# FORMATO
# =========================

plt.title(
    "Ranking FIBRAs — Dividendos del trimestre actual\n"
    "Comparación contra promedio trimestral de últimos 3 años",
    pad=15
)

plt.ylabel("Dividendo por certificado (MXN)")
plt.xlabel("FIBRA")

plt.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.show()