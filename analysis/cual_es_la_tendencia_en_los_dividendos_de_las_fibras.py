import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# =========================
# CONFIGURACIÓN
# =========================

fibras = [
    ##"FUNO11.MX",
    ##"FMTY14.MX",
    ##"FNOVA17.MX",
    ##"DANHOS13.MX",
    ##"FIBRAMQ12.MX",
    "FSHOP13.MX",
    ##"NEXT25.MX",
    ##"FINN13.MX"
]

years_back = 3
current_year = datetime.today().year
start_year = current_year - years_back

start_date = datetime(start_year, 1, 1)

# =========================
# PROCESO
# =========================

for fibra in fibras:
    ticker = yf.Ticker(fibra)
    dividends = ticker.dividends

    if dividends.empty:
        print(f"\n⚠️ Sin dividendos para {fibra}")
        continue

    df = dividends.reset_index()
    df.columns = ["fecha", "dividendo"]
    df["fecha"] = df["fecha"].dt.tz_localize(None)
    df = df[df["fecha"] >= start_date]

    if df.empty:
        print(f"\n⚠️ {fibra} sin dividendos en los últimos {years_back} años")
        continue

    # =========================
    # TOTAL ANUAL
    # =========================

    df["año"] = df["fecha"].dt.year
    total_anual = df.groupby("año")["dividendo"].sum()

    print(f"\n📊 Total anual – {fibra}")
    print(total_anual)

    # =========================
    # TRENDLINE
    # =========================

    X = np.arange(len(df))
    y = df["dividendo"].values

    coef = np.polyfit(X, y, 1)
    trend = np.poly1d(coef)(X)

    # =========================
    # GRÁFICA
    # =========================

    plt.figure(figsize=(10, 5))
    plt.plot(df["fecha"], y, marker="o", label="Dividendo")
    plt.plot(df["fecha"], trend, linestyle="--", label="Tendencia", color="red")

    # Etiquetas en puntos
    for _, row in df.iterrows():
       ## fecha_str = row["fecha"].strftime("%y-%m-%d")
        label = f"${row['dividendo']:.2f}"

        plt.annotate(
            label,
            (row["fecha"], row["dividendo"]),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            fontsize=8,
            ##rotation=45
        )

    plt.title(f"Dividendos históricos por título | {fibra}")
    plt.xlabel("Fecha")
    plt.ylabel("MXN por certificado")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()