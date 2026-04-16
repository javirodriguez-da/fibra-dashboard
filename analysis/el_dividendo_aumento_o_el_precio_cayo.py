import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# =============================
# CONFIGURACIÓN
# =============================

FIBRAS = [
    ##"FUNO11.MX",
    "FMTY14.MX",
    ##"FNOVA17.MX",
   ## "DANHOS13.MX",
   ##"FIBRAMQ12.MX",
   ## "FSHOP13.MX",
  ##  "NEXT25.MX",
   ## "FINN13.MX"
]

START_YEAR = 2021
END_YEAR = 2025
ROLLING_Q = 6

OUTPUT_FOLDER = "graficas_yield_vs_precio"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =============================
# PROCESO
# =============================

for ticker in FIBRAS:

    fib = yf.Ticker(ticker)

    dividends = fib.dividends
    prices = fib.history(start=f"{START_YEAR}-01-01", end=f"{END_YEAR}-12-31")["Close"]

    if dividends.empty or prices.empty:
        continue

    # =============================
    # DIVIDENDOS
    # =============================

    df_div = dividends.reset_index()
    df_div.columns = ["fecha", "dividendo"]
    df_div["fecha"] = pd.to_datetime(df_div["fecha"])
    df_div = df_div[
        (df_div["fecha"].dt.year >= START_YEAR) &
        (df_div["fecha"].dt.year <= END_YEAR)
    ]

    df_div["quarter"] = df_div["fecha"].dt.to_period("Q")
    div_q = df_div.groupby("quarter")["dividendo"].sum()

    # =============================
    # PRECIOS
    # =============================

    prices.index = pd.to_datetime(prices.index)
    prices_q = prices.resample("QE").mean()

    df_q = pd.DataFrame({
        "dividendo": div_q,
        "precio_prom": prices_q
    }).dropna()

    if len(df_q) < ROLLING_Q + 1:
        continue

    # =============================
    # YIELDS
    # =============================

    df_q["yield"] = df_q["dividendo"] / df_q["precio_prom"]

    hist = df_q.iloc[-(ROLLING_Q + 1):-1]
    actual = df_q.iloc[-1]

    yield_hist = hist["yield"].mean()
    yield_actual = actual["yield"]

    # =============================
    # GRÁFICA
    # =============================

    plt.figure(figsize=(6, 5))

    barras = ["Yield histórico", "Yield actual"]
    valores = [yield_hist, yield_actual]

    color_actual = "green" if yield_actual >= yield_hist else "red"
    colores = ["steelblue", color_actual]

    x = np.arange(len(barras))

    plt.bar(x, valores, color=colores, width=0.5)

    # Etiquetas de yield
    for i, v in enumerate(valores):
        plt.text(
            i,
            v * 1.05,
            f"{v:.2%}",
            ha="center",
            fontsize=10,
            fontweight="bold"
        )

    # Etiqueta de precio y dividendo actual
    texto_detalle = (
        f"Precio prom: ${actual['precio_prom']:.2f}\n"
        f"Dividendo: ${actual['dividendo']:.2f}"
    )

    plt.text(
        1,
        valores[1] * 0.6,
        texto_detalle,
        ha="center",
        fontsize=9
    )

    plt.xticks(x, barras)
    plt.ylabel("Yield trimestral")
    plt.title(f"{ticker.replace('.MX','')}\nYield actual vs histórico")

    plt.ylim(0, max(valores) * 1.35)

    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/{ticker.replace('.MX','')}_yield.png")
    plt.show()

print("✔ Gráficas generadas en carpeta:", OUTPUT_FOLDER)