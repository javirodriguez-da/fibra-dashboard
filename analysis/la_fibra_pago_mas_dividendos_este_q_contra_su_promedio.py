import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

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

START_YEAR = 2022
END_YEAR = 2025
ROLLING_Q = 6  # trimestres históricos a comparar

OUTPUT_FOLDER = "graficas_dividendos"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =============================
# PROCESO
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

    if df.empty:
        continue

    # Trimestres
    df["quarter"] = df["fecha"].dt.to_period("Q")

    quarterly = df.groupby("quarter")["dividendo"].sum().sort_index()

    if len(quarterly) < ROLLING_Q + 1:
        continue

    prev = quarterly.iloc[-(ROLLING_Q + 1):-1]
    current = quarterly.iloc[-1]

    avg_prev = prev.mean()
    min_prev = prev.min()
    max_prev = prev.max()

    # =============================
    # GRÁFICA
    # =============================

    plt.figure(figsize=(6, 5))

    barras = ["Promedio histórico", "Dividendo actual"]
    valores = [avg_prev, current]

    color_actual = "green" if current >= avg_prev else "red"
    colores = ["steelblue", color_actual]

    x = np.arange(len(barras))

    plt.bar(x, valores, color=colores, width=0.5)

    # Línea de rango histórico
    plt.vlines(
        x=0,
        ymin=min_prev,
        ymax=max_prev,
        color="gray",
        linewidth=3
    )

    # Etiquetas de min y max
    plt.text(
        0,
        min_prev,
        f"Min: ${min_prev:.2f}",
        ha="center",
        va="top",
        fontsize=8
    )

    plt.text(
        0,
        max_prev,
        f"Max: ${max_prev:.2f}",
        ha="center",
        va="bottom",
        fontsize=8
    )

    # Etiquetas de barras
    for i, v in enumerate(valores):
        plt.text(
            i,
            v * 1.03,
            f"${v:.2f}",
            ha="center",
            fontsize=9,
            fontweight="bold"
        )

    plt.xticks(x, barras)

    plt.ylabel("Dividendo por CBFI (MXN)")
    plt.title(f"{ticker.replace('.MX','')}\nPromedio vs dividendo actual")

    plt.ylim(0, max(max_prev, current) * 1.35)

    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/{ticker.replace('.MX','')}_comparativa.png")
    plt.show()

print("✔ Gráficas generadas en carpeta:", OUTPUT_FOLDER)